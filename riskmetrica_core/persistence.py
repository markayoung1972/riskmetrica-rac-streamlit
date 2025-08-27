import os, json, uuid, datetime
from typing import List, Optional, Dict, Any

DATA_ROOT = os.path.join(os.getcwd(), "data")
ASSESS_DIR = os.path.join(DATA_ROOT, "assessments")
os.makedirs(ASSESS_DIR, exist_ok=True)

def _now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def save_assessment(doc: Dict[str, Any]) -> str:
    _id = doc.get("id") or str(uuid.uuid4())
    doc["id"] = _id
    doc["saved_at"] = _now_iso()
    path = os.path.join(ASSESS_DIR, f"{_id}.json")
    with open(path, "w") as f:
        json.dump(doc, f, indent=2)
    return _id

def list_assessments(category: Optional[str] = None) -> List[Dict[str, Any]]:
    out = []
    for fn in os.listdir(ASSESS_DIR):
        if not fn.endswith(".json"): continue
        p = os.path.join(ASSESS_DIR, fn)
        try:
            with open(p, "r") as f:
                doc = json.load(f)
            if (category is None) or (doc.get("context",{}).get("category") == category):
                out.append({
                    "id": doc.get("id"),
                    "title": doc.get("title") or doc.get("context",{}).get("strategic_objective","(no title)"),
                    "category": doc.get("context",{}).get("category"),
                    "saved_at": doc.get("saved_at")
                })
        except Exception:
            continue
    out.sort(key=lambda d: d.get("saved_at") or "", reverse=True)
    return out

def load_assessment(assessment_id: str) -> Optional[Dict[str, Any]]:
    p = os.path.join(ASSESS_DIR, f"{assessment_id}.json")
    if not os.path.exists(p):
        return None
    with open(p, "r") as f:
        return json.load(f)
