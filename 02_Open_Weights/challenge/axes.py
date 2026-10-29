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
    f"a one-off or planned event, such as scheduled maintenance by us or a provider, with no recurring pattern. {NEVER_NAME}": "not_toil",
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
        "responders recorded two or more competing explanations that point to different kinds of cause, and the record never settles which one was right",  # conflicting
        "the investigation never established a root cause: the notes show checks that found nothing conclusive, and the resolution says the cause is unknown",  # absent -- the decline
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


def is_dead(combo: dict) -> bool:
    """A misleading value whose hidden cause is the category it tempts toward is
    not misleading at all, so the combination cannot exist."""
    return TEMPTS.get(combo["surface_vs_cause"]) == OUTCOME_LABELS[combo["outcome_type"]]


if __name__ == "__main__":
    import itertools
    from math import prod

    combos = [dict(zip(AXES, values)) for values in itertools.product(*AXES.values())]
    dead = sum(is_dead(combo) for combo in combos)
    print(f"{len(AXES)} axes -> {prod(len(v) for v in AXES.values())} combinations, "
          f"{dead} dead, {len(combos) - dead} to generate")
