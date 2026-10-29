"""TC2 Step 2: generate, dedupe, validate.

Writes use_case/data/synthetic_v1.jsonl (gitignored) and the dedupe drops next to
it, so you can read what was thrown away.

    uv run python 02_Open_Weights/challenge/generate.py
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from axes import AXES, OUTCOME_LABELS, TEMPTS, is_dead  # noqa: E402
from helpers import nb, sdg  # noqa: E402
from helpers.llm import CallStats  # noqa: E402
from axes import TAXONOMY  

GOLDEN = ROOT / "use_case" / "evals" / "golden.jsonl"
DATA = ROOT / "use_case" / "data"

# Short names for the evidence axis, in the same order as its values in axes.py.
# Maps the full sentence the generator saw -> the name the label rules use
EVIDENCE: dict[str, str] = dict(
    zip(AXES["evidence"], ["complete", "partial", "conflicting", "absent"], strict=True)
)
TAXONOMY_NAMES: set[str] = {category["name"] for category in TAXONOMY["categories"]}
EXISTING_CATEGORIES = TAXONOMY_NAMES | {"not_toil"}

REQUIRED_INCIDENT_KEYS = (
    "incident_id", "status", "opened_at", "resolved_at",
    "summary", "reported_symptoms", "work_notes", "resolution", "affected_context",
)
INCIDENT_STATUSES = {"resolved", "closed"}

# --- Settings. Every one of these goes in DATASHEET.md's Generation run table.
# None means "the model's default" (qwen3.5:9b: temperature 1, top_p 0.95, top_k 20).
TEMPERATURE: float | None = None  # TODO: choose, and say why (S3 Task 3)
TOP_P: float | None = None  # TODO: choose (S3 Task 5)
TOP_K: int | None = None  # TODO: the model sets 20 by default; override or record it
DEDUPE_THRESHOLD = 0.7  # TODO: decide after reading the dropped pairs
PER_COMBO = 3
N_EXAMPLES = 5

# --- Pilot first: 2 values per axis, 16 combinations. Set PILOT = False for the full run.
PILOT = True
PILOT_PICK = {  # indexes into each axis's values in axes.py
    "evidence": [0, 3],  # complete, absent
    "surface_vs_cause": [0, 1],  # direct, misleading_ddos
    "outcome_type": [0, 10],  # hardware_failure, not_toil
    "blast_radius": [0, 2],  # absorbed, multi_site
}

def row_text(row: dict) -> str:
    """The text that stands for this row when asking "is this the same incident
    twice?". The leak check searches the same text.

    row["incident"] has: summary, reported_symptoms, work_notes (a list of
    {recorded_at, responder_id, note}), resolution, affected_context, and IDs.
    Shared boilerplate (field names, ID formats, timestamps) makes distinct
    incidents look alike, so choose what goes in.
    """
    # Runs before validate(), on raw model output, so a missing or malformed field
    # must not crash a run that has already spent hours on model calls
    incident = row.get("incident")
    if not isinstance(incident, dict):
        return str(incident or "")

    notes = [
        note.get("note", "") for note in incident.get("work_notes") or [] if isinstance(note, dict)
    ]
    resolution = incident.get("resolution")
    # Only the text values: service_restored true/false is shared by almost every row
    resolution_text = (
        [value for value in resolution.values() if isinstance(value, str)]
        if isinstance(resolution, dict)
        else [str(resolution or "")]
    )
    parts = [incident.get("summary", ""), incident.get("reported_symptoms", ""), *notes, *resolution_text]
    return " ".join(str(part) for part in parts if part)


def validate(row: dict) -> bool:
    """Is this row well-formed enough to keep? Raising counts as False in generate()."""
    incident, expected = row.get("incident"), row.get("expected")
    return (
        isinstance(incident, dict)
        and isinstance(expected, dict)
        and incident_ok(incident)
        and expected_ok(expected)
    )


def incident_ok(incident: dict) -> bool:
    if any(key not in incident for key in REQUIRED_INCIDENT_KEYS):
        return False
    # work_notes may be empty (partial evidence); every other required field needs content
    if any(incident[key] in (None, "", {}) for key in REQUIRED_INCIDENT_KEYS if key != "work_notes"):
        return False
    return (
        isinstance(incident["work_notes"], list)
        and isinstance(incident["resolution"], dict)
        and isinstance(incident["affected_context"], dict)
        and incident["status"] in INCIDENT_STATUSES
        and datetime.fromisoformat(incident["resolved_at"]) > datetime.fromisoformat(incident["opened_at"])
    )


def expected_ok(expected: dict) -> bool:
    category = expected.get("suggested_category")
    status = expected.get("category_status")
    needs_human = expected.get("needs_human")

    # One of the outcome shapes schema.py allows
    shape_ok = (
        isinstance(needs_human, bool)
        and expected.get("problem_id") is None
        and (needs_human or status == "approved")  # skipping review needs an approved category
        and (
            (status == "approved" and category in EXISTING_CATEGORIES)
            or (status == "new" and isinstance(category, str) and category.strip() != ""
                and category not in EXISTING_CATEGORIES)
            or (status == "unclassified" and category is None)
        )
    )
    if not shape_ok:
        return False

    # Confidence band: {"min"} and/or {"max"}, numbers in 0-1, inside classifier.py's bands
    band = expected.get("confidence")
    if not isinstance(band, dict) or not band or set(band) - {"min", "max"}:
        return False
    if not all(type(value) in (int, float) for value in band.values()):  # type() also rejects True/False
        return False
    low, high = band.get("min", 0.0), band.get("max", 1.0)
    return (
        0 <= low <= high <= 1
        and (needs_human or low >= 0.8)  # auto-decision: ">= 0.8"
        and (not needs_human or high < 0.8)  # review sits below the auto-decision line
        and (status != "new" or high <= 0.69)  # "no category match: 0.5-0.69"
        and (status != "unclassified" or high <= 0.3)  # "nothing identified: < 0.3"
    )

def label_matches_axes(row: dict) -> bool:
    combo = row["_axes"]
    hidden = OUTCOME_LABELS[combo["outcome_type"]]
    evidence = EVIDENCE[combo["evidence"]]
    tempting = TEMPTS.get(combo["surface_vs_cause"])
    expected = row["expected"]
    suggested_category = expected.get("suggested_category")
    category_status = expected.get("category_status")
    needs_human = expected.get("needs_human")
    
    existing = EXISTING_CATEGORIES

    # R2: a misleading row never expects the category it imitates
    if tempting and suggested_category == tempting:
        return False
    # R1: no cause, no leading hypothesis (rule 5b)
    if evidence == "absent":
        return suggested_category is None and category_status == "unclassified" and needs_human is True
    # R6: a leading hypothesis on an existing category, sent for review (rule 5a)
    if evidence == "conflicting":
        band_max = expected["confidence"].get("max", 1.0)
        return (
            suggested_category in existing
            and category_status == "approved"
            and needs_human is True
            and band_max <= 0.49  # "cause suspected / leading hypothesis: 0.31-0.49"
        )
    # complete / partial from here: the cause is established (rule 4)
    # R4 (rule 4a)
    if hidden == "not_toil":
        return suggested_category == "not_toil" and category_status == "approved" and needs_human is False
    # R5 (rule 4c)
    if hidden == "new_category":
        return (
            isinstance(suggested_category, str)
            and suggested_category.strip() != ""
            and suggested_category not in existing
            and category_status == "new"
            and needs_human is True
        )
    # R3 (rule 4b)
    return suggested_category == hidden and category_status == "approved" and needs_human is False

def preflight(seeds: list[dict]) -> None:
    """Your goldens must pass your own checks. Fails here, before any model call,
    if a function is unfinished or rejects the examples it was written from."""
    for seed in seeds:
        assert row_text(seed).strip(), f"{seed['id']}: row_text returned nothing"
        assert validate(seed) is not False, f"{seed['id']}: fails your own validate()"
    # label_matches_axes only runs after generation, so prove it is written before
    # spending any calls. The answer does not matter here, only that it runs
    label_matches_axes({**seeds[0], "_axes": sdg.combinations(AXES)[0]})


def main() -> None:
    cfg = nb.bootstrap()
    seeds = [json.loads(line) for line in GOLDEN.read_text().splitlines() if line.strip()]
    preflight(seeds)

    axes = (
        {axis: [AXES[axis][i] for i in picks] for axis, picks in PILOT_PICK.items()}
        if PILOT
        else AXES
    )
    sampling = {"temperature": TEMPERATURE, "top_p": TOP_P, "top_k": TOP_K}
    llm_kwargs = {"num_ctx": int(os.environ["LLM_NUM_CTX"])}
    llm_kwargs |= {name: value for name, value in sampling.items() if value is not None}

    to_run = sum(not is_dead(combo) for combo in sdg.combinations(axes))
    print(
        f"{'PILOT' if PILOT else 'FULL'} run: {to_run} combinations x {PER_COMBO} rows, "
        f"model {cfg.llm_model}, settings {llm_kwargs}\n"
        f"Nothing is saved until every call finishes. The first call also loads the model."
    )
    started = time.perf_counter()

    def show_progress(done: int, total: int) -> None:
        elapsed = time.perf_counter() - started
        print(f"\r{done}/{total} combinations · {elapsed / 60:.1f} min · "
              f"{elapsed / done:.0f}s per call", end="", flush=True)

    stats = CallStats()
    rows, report = sdg.generate(
        cfg,
        seeds,
        axes,
        exclude=is_dead,
        row_text=row_text,
        validate=validate,
        per_combo=PER_COMBO,
        n_examples=N_EXAMPLES,
        dedupe_threshold=DEDUPE_THRESHOLD,
        timeout=600,
        stats=stats,
        llm_kwargs=llm_kwargs,
        progress=show_progress,
    )
    print()
    print(report)
    print(stats)

    mismatched = [row for row in rows if not label_matches_axes(row)]
    print(f"{len(mismatched)} of {len(rows)} rows: expected output disagrees with the axes")

    name = "synthetic_v1.pilot" if PILOT else "synthetic_v1"
    out = DATA / f"{name}.jsonl"
    out.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
    drops = DATA / f"{name}.dropped.jsonl"
    drops.write_text("".join(
        json.dumps({"dropped": row, "matched": twin}, ensure_ascii=False) + "\n"
        for row, twin in report.dropped
    ))
    print(f"wrote {out.relative_to(ROOT)} and {drops.relative_to(ROOT)}")
    if report.leaks:
        print("possible leaks:", report.leaks)


if __name__ == "__main__":
    main()
