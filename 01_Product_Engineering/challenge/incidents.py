import json
import os
from pathlib import Path

USE_CASE_DIR = Path(os.getenv("USE_CASE_DIR") or Path(__file__).resolve().parent.parent.parent / "use_case")
GOLDEN_PATH = USE_CASE_DIR / "evals" / "golden.jsonl"

def load_incidents():
    with GOLDEN_PATH.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def get_incident(incident_id):
    for incident in load_incidents():
        if incident["incident"]["incident_id"] == incident_id:
            return incident["incident"]
    raise KeyError(f"no incident {incident_id}")