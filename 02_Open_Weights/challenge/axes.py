"""Variation axes for ToilMap synthetic incidents (TC2 Step 1).

Must match the Variation axes table in use_case/data/DATASHEET.md.
"""

import json
from pathlib import Path

# Read from the taxonomy so the axes cannot drift from the categories the classifier uses
TAXONOMY = json.loads(
    (Path(__file__).resolve().parents[2] / "use_case" / "taxonomy.json").read_text()
)

NEVER_NAME = "Describe only the technical events and never write a category name or label."

# The text the generator sees -> the hidden label. The generator only ever sees the
# text, so this is how a generated row's intended label is recovered for checking
OUTCOME_LABELS: dict[str, str] = {
    **{
        f"the underlying cause is: {category['description']} {NEVER_NAME}": category["name"]
        for category in TAXONOMY["categories"]
    },
    f"a planned or expected event rather than a failure: work scheduled and announced in advance, by us or by a provider, such as a maintenance window, a planned cutover or a pre-notified provider repair, whose impact matched what was announced. The record must say that the work was planned and when it was announced. Nothing failed unexpectedly: it is not a component failure, a cable cut, an attack, or planned work that caused more impact than announced, even if it happened only once. {NEVER_NAME}": "not_toil",
    f"a recurring kind of problem that none of the existing toil categories describes, for example something lapsing such as an expiring certificate or it can be any other name that is not already a part of the taxonomy list. {NEVER_NAME}": "new_category",
}

MISLEADING_DDOS = "responders first see a sudden traffic surge with degraded or dropped service, which looks like a DDoS attack; that impression is not what the record supports"
MISLEADING_DNS = "responders first see names failing to resolve, which looks like a DNS outage; that impression is not what the record supports"

# Each misleading value -> the category it tempts toward
TEMPTS: dict[str, str] = {MISLEADING_DDOS: "security", MISLEADING_DNS: "dns"}

AXES: dict[str, list[str]] = {
    # How much of what the engineers knew made it into the record, and so how
    # settled the cause is. Covers lossy notes and knowledge that never left the engineer
    "evidence": [
        "complete evidence, from start to finish, every step taken, every discussion covered, every decision documented and the final result with resolution noted on the incident",  # complete
        "the initial description and final resolution documented, but intermediate steps taken were not documented",  # partial
        "responders recorded two or more competing explanations that belong to different kinds of cause, such as a hardware fault versus a software bug or a bad change, never just one failed part versus another; the notes lean toward one of them, the real cause, with more supporting evidence than the others, but nothing confirms it and the record never settles which one was right",  # conflicting
        """If the investigation never established a root cause, ensure the work_notes on the incident record list the checks that were performed — and each came back clean; no note favours one explanation over another; the case closes with the reason recorded as "not determined". Whatever really happened may show in the details related to the incident, but nothing in the record confirms it. The expected output has the same shape as example GS-05: no category, unclassified, sent to a human, confidence at most 0.3.""",  # absent -- the decline
    ],
    # Whether the first visible symptoms point at the real cause or at a tempting wrong one.
    # Misleading does not require a cause to be found; evidence decides that
    "surface_vs_cause": [
        "the first symptoms responders saw point straight at the real cause",  # direct
        MISLEADING_DDOS,  # misleading: looks like security
        MISLEADING_DNS,  # misleading: looks like dns
    ],
    # The hidden truth the generator writes the incident from. Never named in the incident text
    # 10 taxonomy categories + not_toil + new category
    "outcome_type": list(OUTCOME_LABELS),
    # How widely the failure spreads, and whether redundancy absorbed it
    "blast_radius": [
        "a component failed but redundancy carried the traffic, with no user or service impact",  # absorbed
        "the impact is confined to one site, from a single device or link up to the whole site",  # one_site
        "several sites are affected at the same time, in one region or across regions",  # multi_site
    ],
}

# Earlier wordings of an outcome value -> its label. Added after AXES so they are never
# generated again, but rows made from them still resolve to their label
OUTCOME_LABELS[
    f"a one-off or planned event, such as scheduled maintenance by us or a provider, with no recurring pattern. {NEVER_NAME}"
] = "not_toil"


def is_dead(combo: dict) -> bool:
    """A misleading value whose hidden cause is the category it tempts toward is
    not misleading at all, so the combination cannot exist."""
    return TEMPTS.get(combo["surface_vs_cause"]) == OUTCOME_LABELS[combo["outcome_type"]]


def expected_from_axes(combo: dict) -> dict:
    """The expected block a row with these axes must have, decided by the rules
    rather than by the model.

    Leaves out what the axes cannot decide: reason_must_mention_any, and the
    invented name for a new category. Those come from the model's row afterwards.
    """
    hidden = OUTCOME_LABELS[combo["outcome_type"]]
    # Same order as the evidence values in AXES, and as EVIDENCE in generate.py
    evidence = ("complete", "partial", "conflicting", "absent")[
        AXES["evidence"].index(combo["evidence"])
    ]

    def label(category: str | None, status: str, needs_human: bool, confidence: dict) -> dict:
        return {
            "suggested_category": category,
            "category_status": status,
            "problem_id": None,
            "needs_human": needs_human,
            "confidence": confidence,  # {"min": ...} and/or {"max": ...}
        }

    # R1: no cause, no leading hypothesis (rule 5b)
    if evidence == "absent":
        return label(category=None, status="unclassified", needs_human=True, confidence={"max": 0.3})

    # R6: a leading hypothesis on an existing category, sent for review (rule 5a)
    if evidence == "conflicting":
        # No existing category fits a new cause, so there is no hypothesis to lead with:
        # labelled like R1 (decisions.md)
        if hidden == "new_category":
            return label(category=None, status="unclassified", needs_human=True, confidence={"max": 0.3})
        return label(category=hidden, status="approved", needs_human=True, confidence={"min": 0.31, "max": 0.49})

    # complete / partial from here: the cause is established (rule 4)
    # R4 (rule 4a)
    if hidden == "not_toil":
        return label(category="not_toil", status="approved", needs_human=False, confidence={"min": 0.8})

    # R5 (rule 4c): the name is a placeholder until the model's row fills it in
    if hidden == "new_category":
        return label(category="NEW_CATEGORY", status="new", needs_human=True, confidence={"min": 0.5, "max": 0.69})

    # R3 (rule 4b)
    return label(category=hidden, status="approved", needs_human=False, confidence={"min": 0.8})


if __name__ == "__main__":
    import itertools
    from math import prod

    combos = [dict(zip(AXES, values)) for values in itertools.product(*AXES.values())]
    dead = sum(is_dead(combo) for combo in combos)
    print(f"{len(AXES)} axes -> {prod(len(v) for v in AXES.values())} combinations, "
          f"{dead} dead, {len(combos) - dead} to generate")
