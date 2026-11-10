"""Run every golden through solve_single and score it against `expected`.

    uv run --env-file ../../.env python run_goldens.py            # call the model, save outputs, score
    uv run --env-file ../../.env python run_goldens.py --rescore  # score the saved outputs, no model calls

The model run is slow, so the raw outputs are saved and the scoring can be
re-run on them while you change the checks.
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone

import llm
from classifier import load_taxonomy, solve_single
from incidents import GOLDEN_PATH, USE_CASE_DIR
from schema import SingleIntRequest

RUN_PATH = USE_CASE_DIR / "evals" / "golden_run.json"


# --- The checks: yours to write ---------------------------------------------
# Each one takes the model's output (a dict) and the golden's `expected` dict.
# Return True for a pass, False for a fail, or None while it is not written yet
# (None is reported as "not scored", never counted as a pass).


def check_category(output: dict, expected: dict) -> bool | None:
    got = output["suggested_category"]
    if expected["category_status"] == "new":
        taxonomy = load_taxonomy()
        known = {c["name"] for c in taxonomy["categories"]} | {taxonomy["not_toil"]["name"]}
        return bool(got and got.strip()) and got not in known
    return got == expected["suggested_category"]


def check_status(output: dict, expected: dict) -> bool | None:
    return output["category_status"] == expected["category_status"]


def check_needs_human(output: dict, expected: dict) -> bool | None:
    return output["needs_human"] == expected["needs_human"]


def check_confidence(output: dict, expected: dict) -> bool | None:
    conf = output["confidence"]
    min_conf = expected["confidence"].get("min")
    max_conf = expected["confidence"].get("max")
    if min_conf is not None and conf < min_conf:
        return False
    if max_conf is not None and conf > max_conf:
        return False
    return True


def check_reason(output: dict, expected: dict) -> bool | None:
    reason = output["reason"].lower()
    must_mention = [m.lower() for m in expected["reason_must_mention_any"]]
    return any(m in reason for m in must_mention)


def check_must_not(output: dict, must_not: list[str]) -> bool | None:
    # Optional. The rules are written as text, e.g. "suggested_category == routing_bgp".
    return None


STRUCTURED = {
    "category": check_category,
    "status": check_status,
    "needs_human": check_needs_human,
    "confidence": check_confidence,
}


# --- Plumbing ----------------------------------------------------------------


def load_goldens() -> list[dict]:
    with GOLDEN_PATH.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def run_model(goldens: list[dict]) -> dict:
    results = []
    for golden in goldens:
        incident_id = golden["incident"]["incident_id"]
        print(f"→ {golden['id']} ({incident_id}) ...", flush=True)
        start = time.perf_counter()
        try:
            output, error = solve_single(SingleIntRequest(incident_id=incident_id)).model_dump(mode="json"), None
        except Exception as e:
            output, error = None, f"{type(e).__name__}: {e}"
        results.append({"id": golden["id"], "output": output, "error": error,
                        "seconds": round(time.perf_counter() - start, 1)})
    run = {
        "model": llm.MODEL,
        "commit": git_commit(),
        "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "results": results,
    }
    RUN_PATH.write_text(json.dumps(run, indent=2), encoding="utf-8")
    print(f"✅ saved {RUN_PATH}")
    return run


def mark(result: bool | None) -> str:
    return {True: "pass", False: "FAIL", None: "-"}[result]


def score(run: dict, goldens: list[dict]) -> None:
    by_id = {g["id"]: g for g in goldens}
    print(f"\nmodel {run['model']} · commit {run['commit']} · {run['ran_at']}\n")
    print(f"{'golden':<7} {'category':<9} {'status':<7} {'human':<6} {'conf':<5} {'reason':<7} {'must_not':<9} seconds")

    structured_pass = reason_pass = scored = 0
    for r in run["results"]:
        golden = by_id[r["id"]]
        if r["error"]:
            print(f"{r['id']:<7} ERROR {r['error']}")
            scored += 1
            continue
        out, exp = r["output"], golden["expected"]
        checks = {name: fn(out, exp) for name, fn in STRUCTURED.items()}
        reason = check_reason(out, exp)
        must_not = check_must_not(out, golden.get("must_not", []))
        print(f"{r['id']:<7} {mark(checks['category']):<9} {mark(checks['status']):<7} "
              f"{mark(checks['needs_human']):<6} {mark(checks['confidence']):<5} {mark(reason):<7} "
              f"{mark(must_not):<9} {r['seconds']}")
        if None in checks.values() or reason is None:
            continue
        scored += 1
        structured_pass += all(checks.values())
        reason_pass += all(checks.values()) and reason

    print(f"\nstructured fields: {structured_pass}/{scored}   all checks incl. reason: {reason_pass}/{scored}"
          f"   (of {len(run['results'])} goldens; unwritten checks are not counted)")


if __name__ == "__main__":
    goldens = load_goldens()
    if "--rescore" in sys.argv:
        run = json.loads(RUN_PATH.read_text(encoding="utf-8"))
    else:
        run = run_model(goldens)
    score(run, goldens)
