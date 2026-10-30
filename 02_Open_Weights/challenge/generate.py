"""TC2 Step 2: generate, dedupe, validate.

Writes use_case/data/synthetic_v1.jsonl (gitignored) and the dedupe drops next to
it, so you can read what was thrown away.

    uv run python 02_Open_Weights/challenge/generate.py
"""

import json
import math
import os
import random
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from axes import AXES, OUTCOME_LABELS, TEMPTS, expected_from_axes, is_dead  # noqa: E402
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
# What an invented category name must look like; rejects descriptions copied from GS-04
NEW_CATEGORY_NAME = re.compile(r"[a-z][a-z0-9_]{2,59}")
SYNTHETIC_ID = re.compile(r"SYN-\d{4,}")

# Rows removed after reading, by SYN- id -> why. finish() keeps them out of every
# output file and writes them to synthetic_v1.removed.jsonl, so the record survives
REMOVED: dict[str, str] = {
    # not_toil rows whose text gives no sign the event was planned (the not_toil definition since TC2)
    "SYN-0086": "not_toil, but a power supply failed from thermal overload: a hardware failure",
    "SYN-0088": "not_toil, but a manually added static route caused a loop: a change-induced error",
    "SYN-0094": "not_toil, but a deployment script created a blocking firewall rule: a change-induced error",
    "SYN-0099": "not_toil, but an upstream provider's fibre was cut: nothing planned",
    "SYN-0100": "not_toil, but flapping during a provider's repair, with no sign it was announced",
    "SYN-0104": "not_toil, but a PSU failed from a capacitor leak: a hardware failure",
    "SYN-0105": "not_toil, but a browser vendor's auto-update bug: unplanned, and outside the network team",
    "SYN-0106": "not_toil, but a manual router reboot cut egress, with no sign it was planned",
    "SYN-0116": "not_toil, but an upstream provider's fibre was cut during an emergency repair: nothing planned",
    "SYN-0416": "not_toil (surplus), with no sign in the text that the event was planned",
    # labels that do not fit the incident as written, found in the 50-row read
    "SYN-0132": "new category, but a config file removed a health-check target: change_induced_errors",
    "SYN-0129": "new category, but a known microcode bug: software_firmware_bug",
    "SYN-0064": "conflicting, labelled dns, but the competing explanations are an ACL rule and hardware",
    "SYN-0006": "absent, but the record establishes a brute-force attempt: security",
    "SYN-0296": "link_circuit_carrier, but carrier line cards shut down from cabinet overheating",
}

# --- Prompt. Version 1 (the first full run) was sdg's GENERATION_PROMPT unchanged, and
# the model, never shown the category names, invented its own. Version 2 adds them.
# Every generated row records the version that made it, as _prompt_version
PROMPT_VERSION = 2
BASE_PROMPT = sdg.GENERATION_PROMPT
DOMAIN_RULES = (
    "In the expected output, suggested_category must be one of these names, exactly as written:\n"
    + "\n".join(f"- {category['name']}: {category['description']}" for category in TAXONOMY["categories"])
    + "\n- not_toil: a one-off or planned event with no recurring pattern\n"
    "For a new category, invent a short snake_case name for the cause, such as expiring_certificate; "
    "never copy a description from the examples. Category names belong only in the expected "
    "output, never in the incident text."
).replace("{", "{{").replace("}", "}}")  # the prompt goes through .format()

REQUIRED_INCIDENT_KEYS = (
    "incident_id", "status", "opened_at", "resolved_at",
    "summary", "reported_symptoms", "work_notes", "resolution", "affected_context",
)
INCIDENT_STATUSES = {"resolved", "closed"}

# --- Settings. Every one of these goes in DATASHEET.md's Generation run table.
# None means "the model's default" (qwen3.5:9b: temperature 1, top_p 0.95, top_k 20).
TEMPERATURE: float | None = None  # Keeping the preset default as data generated meets my requirements and thresholds
TOP_P: float | None = None  # Keeping the preset default as data generated meets my requirements and thresholds
TOP_K: int | None = None # Keeping the preset default as data generated meets my requirements and thresholds
DEDUPE_THRESHOLD = 0.7  # the helper's default, kept: no pair came near it (decisions.md, Week 2)
PER_COMBO = 3
N_EXAMPLES = 5

# --- Pilot first: 9 combinations aimed at the label paths the first pilot never
# produced. Set PILOT = False for the full run.
PILOT = False
PILOT_PICK = {  # indexes into each axis's values in axes.py
    "evidence": [2],  # complete, conflicting, absent
    "surface_vs_cause": [1],  # misleading_ddos: exercises R2 and the must_not guard
    "outcome_type": [0, 3],  # hardware_failure, not_toil, new_category
    "blast_radius": [1],  # one_site
}

# --- Full run: rows wanted per label group after every check, 400 in total.
# Looked up from published network-incident studies where they exist, assumed
# elsewhere (decisions.md, Week 2). Keys must match group_of()
QUOTA: dict[str, int] = {
    "absent": 60,  # looked up: 5-29% of incidents never get a cause
    "conflicting": 20,  # assumed: the studies count these as undetermined
    "not_toil": 40,  # assumed
    "new_category": 12,  # assumed
    "change_induced_errors": 79,  # looked up: about twice hardware
    "hardware_failure": 43,  # looked up
    "software_firmware_bug": 37,  # looked up
    "link_circuit_carrier": 32,  # looked up
    "third_party_upstream": 21,  # partly looked up
    "capacity_congestion": 19,  # looked up
    "routing_bgp": 13,  # assumed
    "power_environmental": 11,  # looked up
    "security": 8,  # partly looked up
    "dns": 5,  # assumed
}
SURVIVAL = 0.6  # share of generated rows expected to reach the dataset; sizes each group's calls
SEED = 2  # fixes which combinations are sampled, so a run can be repeated


def group_of(combo: dict) -> str:
    """The QUOTA group a combination's rows count towards."""
    evidence = EVIDENCE[combo["evidence"]]
    return evidence if evidence in ("absent", "conflicting") else OUTCOME_LABELS[combo["outcome_type"]]


def combo_key(combo: dict) -> tuple:
    return tuple(combo[axis] for axis in AXES)


def plan_rounds(quota: dict[str, int], seed: int = SEED) -> list[set]:
    """The combinations to call, in rounds. Each group in `quota` gets enough calls to
    meet it after losses, spread over its combinations at random. One sdg.generate
    pass calls a combination at most once, so a group needing more calls than it has
    combinations repeats some of them in a later round."""
    rng = random.Random(seed)
    groups: dict[str, list[dict]] = {}
    for combo in sdg.combinations(AXES):
        if not is_dead(combo):
            groups.setdefault(group_of(combo), []).append(combo)
    assert set(groups) == set(QUOTA), f"QUOTA and the axes disagree on groups: {set(groups) ^ set(QUOTA)}"

    rounds: list[set] = []
    for name, combos in groups.items():
        rng.shuffle(combos)
        for call in range(math.ceil(quota.get(name, 0) / (PER_COMBO * SURVIVAL))):
            round_number = call // len(combos)
            while len(rounds) <= round_number:
                rounds.append(set())
            rounds[round_number].add(combo_key(combos[call % len(combos)]))
    return rounds


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


def validate_incident(row: dict) -> bool:
    """The check generation runs on the model's raw row. Only the incident: the
    expected block is replaced from the axes afterwards, so a wrong model label
    must not throw away a good incident. Rejects an incident that names a category,
    since that hands the classifier the answer (only snake_case names: "dns" and
    "security" are ordinary words in incident text)."""
    text = row_text(row)
    return (
        isinstance(row.get("incident"), dict)
        and incident_ok(row["incident"])
        and not any(name in text for name in EXISTING_CATEGORIES if "_" in name)
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
        # No existing category fits a new cause: labelled like R1 (decisions.md)
        if hidden == "new_category":
            return suggested_category is None and category_status == "unclassified" and needs_human is True
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


def relabel(row: dict) -> dict | None:
    """Replace the model's expected block with the one the axes decide, keeping the
    model's guess beside it as _model_expected. None if the row cannot be used."""
    guess = row["expected"] if isinstance(row.get("expected"), dict) else {}
    expected = expected_from_axes(row["_axes"])
    # The two things the axes cannot decide come from the model's row
    expected["reason_must_mention_any"] = guess.get("reason_must_mention_any") or []
    if expected["category_status"] == "new":
        name = guess.get("suggested_category")
        if not isinstance(name, str) or not NEW_CATEGORY_NAME.fullmatch(name) or name in EXISTING_CATEGORIES:
            return None
        expected["suggested_category"] = name
    return {**row, "expected": expected, "_model_expected": guess}


def model_agrees(row: dict) -> bool:
    """Does the model's own guess agree with the label from the axes? Disagreement
    suggests the incident may not fit its axes, so these are the rows to read."""
    guess, expected = row["_model_expected"], row["expected"]
    if guess.get("needs_human") != expected["needs_human"]:
        return False
    # The model rarely writes a leading hypothesis itself, so on conflicting rows the
    # signal is only whether it also judged the cause unsettled
    if EVIDENCE[row["_axes"]["evidence"]] == "conflicting":
        return True
    if expected["category_status"] == "new":  # a new category's name is the model's anyway
        return guess.get("category_status") == "new"
    category = guess.get("suggested_category")
    # Prompt version 1 never showed the model the category names, so a name it invented
    # only says it judged the cause settled. Version 2 rows are held to the real names
    if row.get("_prompt_version", 1) == 1 and category is not None and category not in EXISTING_CATEGORIES:
        return guess.get("category_status") == "approved"
    return category == expected["suggested_category"] and guess.get("category_status") == expected["category_status"]


def guard_must_not(row: dict) -> tuple[list, int, int]:
    """The model's must_not, made safe: (entries, added, removed).

    Adds what the axes decide (the tempting category, the opposite of needs_human),
    removes entries naming a category that does not exist or forbidding what the
    row's own expected requires, and keeps every other entry, free text included.
    """
    expected = row["expected"]
    # The value each field would have in a correct answer, as must_not writes it
    required = {
        "suggested_category": str(expected["suggested_category"]),
        "needs_human": str(expected["needs_human"]).lower(),
        "category_status": expected["category_status"],
    }
    model_list = row.get("must_not") if isinstance(row.get("must_not"), list) else []

    kept: list = []
    for entry in model_list:
        if not isinstance(entry, str):
            continue
        field_name, _, value = (part.strip() for part in entry.partition("=="))
        if value:  # a "field == value" entry; anything else is kept as written
            if value in ("null", "None"):
                value = "None"
            invented = field_name == "suggested_category" and value != "None" and value not in EXISTING_CATEGORIES
            if invented or required.get(field_name) == value:
                continue
        if entry not in kept:
            kept.append(entry)

    tempting = TEMPTS.get(row["_axes"]["surface_vs_cause"])
    derived = [f"needs_human == {str(not expected['needs_human']).lower()}"]
    if tempting:
        derived.append(f"suggested_category == {tempting}")
    added = [entry for entry in derived if entry not in kept]
    return kept + added, len(added), len(model_list) - len(kept)


def preflight(seeds: list[dict]) -> None:
    """Your goldens must pass your own checks. Fails here, before any model call,
    if a function is unfinished or rejects the examples it was written from."""
    for seed in seeds:
        assert row_text(seed).strip(), f"{seed['id']}: row_text returned nothing"
        assert validate(seed) is not False, f"{seed['id']}: fails your own validate()"
    # label_matches_axes only runs after generation, so prove it is written before
    # spending any calls. The answer does not matter here, only that it runs
    label_matches_axes({**seeds[0], "_axes": sdg.combinations(AXES)[0]})
    # Every label the code can produce must pass your own schema check
    for combo in sdg.combinations(AXES):
        if not is_dead(combo):
            label = expected_from_axes(combo)
            assert expected_ok(label), f"expected_from_axes gives {label}, which fails expected_ok()"


def setup() -> tuple:
    cfg = nb.bootstrap()
    seeds = [json.loads(line) for line in GOLDEN.read_text().splitlines() if line.strip()]
    preflight(seeds)
    return cfg, seeds


def sampled_passes(quota: dict[str, int], seed: int = SEED) -> list[tuple]:
    """One sdg.generate pass per round of sampled combinations."""
    return [(AXES, lambda combo, keys=keys: combo_key(combo) not in keys) for keys in plan_rounds(quota, seed)]


def main() -> None:
    cfg, seeds = setup()
    # One pass over the pilot grid, or one pass per round of sampled combinations
    if PILOT:
        pilot_axes = {axis: [AXES[axis][i] for i in picks] for axis, picks in PILOT_PICK.items()}
        passes = [(pilot_axes, is_dead)]
    else:
        passes = sampled_passes(QUOTA)
    live = sum(not is_dead(combo) for combo in sdg.combinations(AXES))
    rows, report = run_passes(
        cfg, seeds, passes,
        "PILOT run" if PILOT else f"FULL run, sampled from {live} live combinations",
    )

    name = "synthetic_v1.pilot" if PILOT else "synthetic_v1"
    finish(rows, name, trim=not PILOT)
    write_dropped(name, report.dropped, append=False)
    if report.leaks:
        print("possible leaks:", report.leaks)


def top_up() -> None:
    """Generate only for the groups short of their quota, with the current prompt,
    and add the new rows to the last full run's. Rows already in the dataset stay."""
    cfg, seeds = setup()
    files = [DATA / f"synthetic_v1{suffix}.jsonl" for suffix in ("", ".surplus", ".review")]
    kept: dict[str, int] = {}
    for line in files[0].read_text().splitlines():
        group = group_of(json.loads(line)["_axes"])
        kept[group] = kept.get(group, 0) + 1
    short = {group: quota - kept.get(group, 0) for group, quota in QUOTA.items() if kept.get(group, 0) < quota}
    if not short:
        print("Every group is at its quota; nothing to top up.")
        return

    backup = DATA / "before_topup"
    backup.mkdir(exist_ok=True)
    for path in files:
        shutil.copy(path, backup)
    print(f"backed up the current files to {backup.relative_to(ROOT)}")

    # A different seed, so the top-up does not pick the full run's combinations again
    new_rows, report = run_passes(cfg, seeds, sampled_passes(short, seed=SEED + 1), f"TOP-UP for {short}")
    # Existing rows come first, so a new row that repeats one of them is the one dropped
    pool, repeats = sdg.dedupe(load_last_run() + new_rows, threshold=DEDUPE_THRESHOLD, text=row_text)
    print(f"{len(repeats)} new rows dropped as duplicates of existing ones")
    finish(pool, "synthetic_v1", trim=True)
    write_dropped("synthetic_v1", report.dropped + repeats, append=True)
    if report.leaks:
        print("possible leaks:", report.leaks)


def run_passes(cfg, seeds: list[dict], passes: list[tuple], title: str) -> tuple[list[dict], "sdg.SDGReport"]:
    """Call the model for every pass, merge the rows and the counts, and dedupe
    across passes. Every row is tagged with the prompt version that made it."""
    pass_calls = [sum(not exclude(combo) for combo in sdg.combinations(axes)) for axes, exclude in passes]
    to_run = sum(pass_calls)

    sampling = {"temperature": TEMPERATURE, "top_p": TOP_P, "top_k": TOP_K}
    llm_kwargs = {"num_ctx": int(os.environ["LLM_NUM_CTX"]), "think": False}
    llm_kwargs |= {name: value for name, value in sampling.items() if value is not None}

    sdg.GENERATION_PROMPT = DOMAIN_RULES + "\n\n" + BASE_PROMPT
    print(
        f"{title}: {to_run} calls x {PER_COMBO} rows in {len(passes)} rounds, prompt v{PROMPT_VERSION}, "
        f"model {cfg.llm_model}, settings {llm_kwargs}\n"
        f"Nothing is saved until every call finishes. The first call also loads the model.",
        flush=True,
    )
    started = time.perf_counter()
    calls_before = 0  # calls finished in earlier passes

    def show_progress(done: int, total: int) -> None:
        elapsed = time.perf_counter() - started
        print(f"\r{calls_before + done}/{to_run} calls · {elapsed / 60:.1f} min · "
              f"{elapsed / (calls_before + done):.0f}s per call", end="", flush=True)

    stats = CallStats()
    rows, report = [], sdg.SDGReport()
    for (axes, exclude), calls in zip(passes, pass_calls, strict=True):
        pass_rows, pass_report = sdg.generate(
            cfg,
            seeds,
            axes,
            exclude=exclude,
            row_text=row_text,
            validate=validate_incident,
            per_combo=PER_COMBO,
            n_examples=N_EXAMPLES,
            dedupe_threshold=DEDUPE_THRESHOLD,
            timeout=600,
            stats=stats,
            llm_kwargs=llm_kwargs,
            progress=show_progress,
        )
        rows += [{**row, "_prompt_version": PROMPT_VERSION} for row in pass_rows]
        for count in ("generated", "unparseable", "failed_combos", "after_dedupe", "valid"):
            setattr(report, count, getattr(report, count) + getattr(pass_report, count))
        report.leaks += pass_report.leaks
        report.dropped += pass_report.dropped
        calls_before += calls
    print()
    print(report)
    print(stats)

    if len(passes) > 1:
        # Each pass only dedupes within itself; a repeated combination can repeat a row
        rows, across = sdg.dedupe(rows, threshold=DEDUPE_THRESHOLD, text=row_text)
        report.dropped += across
        print(f"{len(across)} more dropped as duplicates across rounds")
    return rows, report


def write_dropped(name: str, dropped: list[tuple], append: bool) -> None:
    path = DATA / f"{name}.dropped.jsonl"
    with path.open("a" if append else "w") as out:
        out.writelines(
            json.dumps({"dropped": row, "matched": twin}, ensure_ascii=False) + "\n" for row, twin in dropped
        )
    print(f"{'appended to' if append else 'wrote'} {path.relative_to(ROOT)}")


def load_last_run() -> list[dict]:
    """Every row the last full run kept, set aside, or held as surplus, with the
    model's own expected block restored so the checks can run on it again."""
    rows = []
    for suffix in ("", ".surplus", ".review", ".removed"):
        path = DATA / f"synthetic_v1{suffix}.jsonl"
        if not path.exists():  # .removed only exists after the first removal
            continue
        for line in path.read_text().splitlines():
            row = json.loads(line)
            row.pop("_removed_because", None)  # finish() decides again, from REMOVED
            row["expected"] = row.pop("_model_expected")  # back to what the model wrote
            row["_was_kept"] = suffix == ""  # so trimming keeps the current dataset stable
            rows.append(row)
    return rows


def reprocess() -> None:
    """Re-run every check that follows generation on the last full run's rows. No
    model calls; dedupe drops are untouched."""
    rows = load_last_run()
    print(f"REPROCESS: {len(rows)} rows from the last full run, no model calls")
    finish(rows, "synthetic_v1", trim=True)


def assign_ids(rows: list[dict]) -> int:
    """Give every row a unique id (SYN-0001) and incident_id (INC-SYN-0001). The model
    continues the goldens' numbering, so its own IDs repeat. A row keeps a SYN- ID it
    already has, so a reprocess or a top-up never renumbers it. Returns how many were new."""
    taken = [int(row["id"][4:]) for row in rows if SYNTHETIC_ID.fullmatch(str(row.get("id")))]
    next_number, assigned = max(taken, default=0) + 1, 0
    for row in rows:
        if not SYNTHETIC_ID.fullmatch(str(row.get("id"))):
            row["id"], next_number, assigned = f"SYN-{next_number:04d}", next_number + 1, assigned + 1
        row["incident"]["incident_id"] = f"INC-{row['id']}"
    assert len({row["id"] for row in rows}) == len(rows), "two rows share a SYN- ID"
    return assigned


def clear_links(rows: list[dict]) -> int:
    """Empty the incident and PRB links the model copied from the goldens: they point
    at records that do not exist. PRBs are created and assigned in a later step.
    Returns how many rows had any."""
    cleared = 0
    for row in rows:
        links = row["incident"].get("existing_links")
        if isinstance(links, dict) and (links.get("incident_ids") or links.get("problem_ids")):
            links["incident_ids"], links["problem_ids"], cleared = [], [], cleared + 1
    return cleared


def finish(rows: list[dict], name: str, trim: bool) -> None:
    """Relabel from the axes, assign IDs, guard must_not, set aside disagreements, trim to quota, write."""
    relabelled = [relabel(row) for row in rows]
    print(f"{relabelled.count(None)} rows dropped: a new category with no usable name from the model")
    rows = [row for row in relabelled if row is not None]
    assert all(validate(row) for row in rows), "a relabelled row fails validate(): check expected_from_axes"
    print(f"{assign_ids(rows)} rows given a new SYN- ID, {len(rows)} in all")
    print(f"{clear_links(rows)} rows had incident or PRB links to records that do not exist; cleared")
    taken_out = [{**row, "_removed_because": REMOVED[row["id"]]} for row in rows if row["id"] in REMOVED]
    rows = [row for row in rows if row["id"] not in REMOVED]
    print(f"{len(taken_out)} rows removed after reading (REMOVED in generate.py)")

    added = removed = 0
    for row in rows:
        row["must_not"], row_added, row_removed = guard_must_not(row)
        added, removed = added + row_added, removed + row_removed
    print(f"must_not: added {added}, removed {removed} across {len(rows)} rows")

    # Disagreeing rows are kept out of the dataset and written separately, to be read
    review = [row for row in rows if not model_agrees(row)]
    rows = [row for row in rows if model_agrees(row)]
    print(f"{len(review)} rows set aside: the model's own label disagrees with the axes")

    # Trim each group to its quota, so the dataset has the planned mix and not
    # whatever survived. Extra rows are kept apart, not thrown away
    surplus: list[dict] = []
    if trim:
        rng = random.Random(SEED)
        by_group: dict[str, list[dict]] = {}
        for row in rows:
            by_group.setdefault(group_of(row["_axes"]), []).append(row)
        rows = []
        for group, quota in QUOTA.items():
            members = by_group.get(group, [])
            rng.shuffle(members)
            members.sort(key=lambda row: not row.get("_was_kept"))  # rows already in the dataset first
            rows += members[:quota]
            surplus += members[quota:]
            if len(members) < quota:
                print(f"  SHORT: {group} has {len(members)} of {quota} rows")
        print(f"trimmed to quota: {len(rows)} of {sum(QUOTA.values())} rows, {len(surplus)} surplus")

    def write(suffix: str, these: list[dict]) -> Path:
        path = DATA / f"{name}{suffix}.jsonl"
        path.write_text("".join(
            json.dumps({key: value for key, value in row.items() if key != "_was_kept"}, ensure_ascii=False) + "\n"
            for row in these
        ))
        return path.relative_to(ROOT)

    if trim:
        print(f"wrote {write('.surplus', surplus)} ({len(surplus)} surplus) and {write('.removed', taken_out)} ({len(taken_out)} removed)")
    print(f"wrote {write('', rows)} ({len(rows)} rows) and {write('.review', review)} ({len(review)} to read)")


if __name__ == "__main__":
    if "--reprocess" in sys.argv:
        reprocess()
    elif "--top-up" in sys.argv:
        top_up()
    else:
        main()
