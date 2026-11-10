import json
import os
from pathlib import Path

USE_CASE_DIR = Path(os.getenv("USE_CASE_DIR") or Path(__file__).resolve().parent.parent.parent / "use_case")
GOLDEN_PATH = USE_CASE_DIR / "evals" / "golden.jsonl"
SYNTHETIC_PATH = USE_CASE_DIR / "data" / "synthetic_v1.jsonl"


def _read_jsonl(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_incidents():
    return _read_jsonl(GOLDEN_PATH) + _read_jsonl(SYNTHETIC_PATH)


def get_incident(incident_id):
    for row in load_incidents():
        if row["incident"]["incident_id"] == incident_id:
            return row["incident"]
    raise KeyError(f"no incident {incident_id}")
