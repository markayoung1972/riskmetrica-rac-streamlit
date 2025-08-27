from .models import RequestPayload, Result, Contribution
import yaml, pathlib

def _load_bands(config_path: str | None = None):
    default = {"bands":[
        {"name":"Averse","max":0.33,"description":"Low appetite – prioritise capital preservation and compliance."},
        {"name":"Guarded","max":0.5,"description":"Cautious appetite – selective risk-taking under tight controls."},
        {"name":"Balanced","max":0.7,"description":"Measured appetite – risk accepted with proportionate returns."},
        {"name":"Seeking","max":1.0,"description":"Higher appetite – pursue opportunities with strong oversight."},
    ]}
    path = pathlib.Path(config_path or "config/bands.yaml")
    if path.exists():
        try:
            with open(path,"r") as f:
                cfg = yaml.safe_load(f) or default
            return cfg.get("bands", default["bands"])
        except Exception:
            return default["bands"]
    return default["bands"]

def _normalise_weights(dimensions):
    total = sum(d.weight for d in dimensions) or 1.0
    return [ (d, (d.weight / total)) for d in dimensions ]

def classify(bands, score: float) -> str:
    for b in bands:
        if score <= b["max"] + 1e-9:
            return b["name"]
    return bands[-1]["name"]

def generate_statement(org, obj, domain, horizon, band, score):
    pct = round(score * 100)
    return (f"{org} expresses a '{band}' risk appetite ({pct}%) for {domain.lower()} over the next "
            f"{horizon} months, aligned to the objective: {obj}. Risk-taking will be proportionate to returns and monitored.")

def calculate(payload: RequestPayload, config_path: str | None = None) -> Result:
    bands = _load_bands(config_path)
    dims_norm = _normalise_weights(payload.dimensions)
    weighted_score = 0.0
    contributions = []
    for d, w in dims_norm:
        contr = d.score * w
        weighted_score += contr
        contributions.append(Contribution(name=d.name, score=d.score, weight=w, contribution=contr))
    band = classify(bands, weighted_score)
    stmt = generate_statement(payload.context.organisation, payload.context.strategic_objective,
                              payload.context.risk_domain, payload.context.time_horizon_months, band, weighted_score)
    audit = {
        "bands": bands,
        "normalised_weights_sum": round(sum(c.weight for c in contributions), 6),
        "raw_weight_sum": round(sum(d.weight for d in payload.dimensions), 6),
        "inputs": payload.model_dump(),
        "calculation": [{"name":c.name,"score":c.score,"norm_weight":c.weight,"contribution":c.contribution} for c in contributions],
        "weighted_score": weighted_score,
        "band": band,
    }
    return Result(weighted_score=weighted_score, band=band, statement=stmt, contributions=contributions, audit=audit)
