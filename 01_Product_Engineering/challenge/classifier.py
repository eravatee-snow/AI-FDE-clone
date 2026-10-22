import json
import os
from pathlib import Path
import llm
from schema import SingleIntRequest, SingleIntResponse
from incidents import get_incident
from pydantic import ValidationError
 
USE_CASE_DIR = Path(os.getenv("USE_CASE_DIR") or Path(__file__).resolve().parent.parent.parent / "use_case")
TAXONOMY_PATH = USE_CASE_DIR / "taxonomy.json"
 
 
def load_taxonomy() -> dict:
    """Read taxonomy.json and return it as a dict."""
    with TAXONOMY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
 
 
_PROMPT_INTRO = """1. You are a classifier for incidents.
2. You will be given an incident as a JSON object and you will classify it into a category. 
The definition of a not_toil task is as follows:
"""

_PROMPT_BEFORE_CATEGORIES = """Toil tasks should be classified into a category that best fits their casusation and resolution. 
The categories are as follows:
"""

_PROMPT_RULES = """The rules you need to know to classify an incident are as follows:
3. You need to establish the cause of the incident. The cause of an incident is considered established when the record states a cause that was verified, and not merely suspected.
4. If cause is established you find the determine the best matching category for the cause. You must define a reason for your classification.
    4a. If you identify an incident to be of not_toil type, return suggested_category: not_toil, category_status: approved, needs_human: false
    4b. if find a matching category, return suggested_category: <category>, category_status: approved, needs_human: false
    4c. if you cannot find a matching category, return suggested_category: <new category>, category_status: new, needs_human: true
5. If cause is not established do one of two things:
    5a. If you have a leading hypothesis (low confidence) return suggested_category: <category>, category_status: approved, needs_human: true
    5b. If you do not have a leading hypothesis return suggested_category: null, category_status: unclassified, needs_human: true
6. Once you identify a category, you need to define a category status.The four statuses and when each applies are as follows:
    6a. -approved: an existing category, or not_toil 
    6b. -new: you created a new suggested category 
    6c. -unclassified: no leading hypothesis 
7. Once you are done with all the above steps, you need to define a confidence score for your classification.Confidence is a value between 0 and 1, where 0 is the least confident and 1 is the most confident.
7a. confidence rules:
  - cause established + clear category match: >= 0.8
  - cause established + unclear category match: 0.7-0.79
  - cause established + no category match: 0.5-0.69
  - cause suspected / leading hypothesis: 0.31-0.49
  - nothing identified: <0.3
8. You will return a JSON response object only.
Always set problem_id to null. All keys must be in double quotes.
The output must be a JSON object that conforms to this JSON schema:
"""


def build_system_prompt(taxonomy: dict) -> str:
    """The policy. Built from the taxonomy file, never typed out by hand."""
    not_toil = taxonomy["not_toil"]
    categories = "\n".join(f"{c['name']}: {c['description']}" for c in taxonomy["categories"])
    return (
        _PROMPT_INTRO
        + f"{not_toil['name']}: {not_toil['description']}\n"
        + _PROMPT_BEFORE_CATEGORIES
        + categories + "\n"
        + _PROMPT_RULES
        + json.dumps(SingleIntResponse.model_json_schema(), indent=2) + "\n"
    )
 
def build_user_message(incident: dict) -> str:
    """The evidence the model sees: the incident as JSON text."""
    return json.dumps(incident, indent=2)
 
def classify_incident(incident_id: str) -> SingleIntResponse:
    incident = get_incident(incident_id)          # raises KeyError if unknown
    messages = [
        {"role": "system", "content": build_system_prompt(load_taxonomy())},
        {"role": "user", "content": build_user_message(incident)},
    ]
    for attempt in range(2):
        raw = llm.complete_json(llm.MODEL, messages)
        try:
            return SingleIntResponse.model_validate_json(raw)
        except ValidationError as e:
            if attempt == 1:
                raise
            problems = [{"field": err["loc"], "problem": err["msg"]} for err in e.errors()]
            messages = messages + [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": f"That response was invalid: {json.dumps(problems, default=str)}. Return corrected JSON only."},
            ]


def solve_single(request: SingleIntRequest) -> SingleIntResponse:
    if not request.incident_id:
        raise ValueError("incident_id is required")
    return classify_incident(request.incident_id)


