from typing import List, Dict, Any

DEFAULT_GUARDS = [
    {"decision": "New SME Loan Approvals", "dimension": "Capital Adequacy", "min_score": 0.5, "note": "Pause approvals if below"},
    {"decision": "Marketing Spend Increase", "dimension": "Earnings Volatility", "min_score": 0.45, "note": "Require CFO approval if below"},
]

def evaluate_guardrails(result: Dict[str, Any], guards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_name = {c["name"]: c for c in result.get("contributions", [])}
    report = []
    for g in guards:
        dim = g["dimension"]
        min_score = float(g.get("min_score", 0.0))
        actual = by_name.get(dim, {"score": None}).get("score")
        status = "OK" if (actual is not None and actual >= min_score) else "BREACH"
        report.append({"decision": g["decision"], "dimension": dim, "min_score": min_score, "actual": actual, "status": status, "note": g.get("note")})
    return report
