
import streamlit as st
from typing import List, Dict, Any
from riskmetrica_core.rac.models import Context, Dimension, RequestPayload
from riskmetrica_core.rac.calculator import calculate
from riskmetrica_core import persistence
from riskmetrica_core.guards import DEFAULT_GUARDS, evaluate_guardrails
import json, os

st.set_page_config(page_title="RiskMetrica – RAC Prototype", page_icon="🧭", layout="wide")

# ---------------- Auth ----------------
if "authed" not in st.session_state:
    st.session_state.authed = False

def login_view():
    st.title("1. Login")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u.strip() and p.strip():
                st.session_state.authed = True
                st.session_state.user = u.strip()
                st.success("Logged in.")
            else:
                st.error("Enter a username and password.")

# ---------------- Nav ----------------
def top_nav():
    st.sidebar.title("RiskMetrica")
    choice = st.sidebar.radio("Navigate", [
        "2.1 Dashboard",
        "2.2 Foundation – RAC",
        "2.11 Reports",
        "2.12 Admin",
        "2.3 Structure (placeholder)",
        "2.4 Balance (placeholder)",
        "2.5 Intelligence (placeholder)",
        "2.6 Governance (placeholder)",
        "2.7 AI Assurance (placeholder)",
        "2.8 Culture (placeholder)",
        "2.9 Agents (placeholder)",
        "2.10 Predictive & ML (placeholder)",
    ])
    return choice

def placeholder_page(title: str):
    st.title(title)
    st.info("Placeholder in current prototype.")

# ---------------- RAC state ----------------
def init_current():
    if "current" not in st.session_state:
        st.session_state.current = {
            "context": {
                "organisation": "Example Bank",
                "strategic_objective": "Grow SME lending profitably",
                "time_horizon_months": 12,
                "risk_domain": "Credit Risk",
                "category": "Financial",
            },
            "dimensions": [
                {"name":"Capital Adequacy", "score":0.60, "weight":0.25},
                {"name":"Earnings Volatility", "score":0.40, "weight":0.20},
                {"name":"Liquidity Buffer", "score":0.70, "weight":0.20},
                {"name":"Concentration Risk", "score":0.35, "weight":0.20},
                {"name":"Regulatory Headroom", "score":0.55, "weight":0.15},
            ],
            "result": None,
            "guards": DEFAULT_GUARDS,
            "title": "SME Lending Appetite 2025"
        }

def run_calculation():
    cur = st.session_state.current
    ctx = Context(**cur["context"])
    dims = [Dimension(**d) for d in cur["dimensions"]]
    payload = RequestPayload(context=ctx, dimensions=dims)
    result = calculate(payload, config_path="config/bands.yaml")
    cur["result"] = result.model_dump()
    return cur["result"]

def export_markdown() -> str:
    cur = st.session_state.current
    res = cur.get("result") or {}
    md = f"""# Risk Appetite Statement

**Organisation:** {cur['context']['organisation']}  
**Objective:** {cur['context']['strategic_objective']}  
**Domain:** {cur['context']['risk_domain']}  
**Horizon:** {cur['context']['time_horizon_months']} months  
**Category:** {cur['context']['category']}

## Appetite
- **Band:** {res.get('band')}
- **Weighted Score:** {res.get('weighted_score')}

> {res.get('statement')}

## Contributions
"""
    for c in res.get("contributions", []):
        md += f"- {c['name']}: score {c['score']}, weight {c['weight']:.2f}, contribution {c['contribution']:.3f}\n"
    md += "\n## Audit\n"
    md += "```json\n" + json.dumps(res.get("audit", {}), indent=2) + "\n```\n"
    return md

# ---------------- Views ----------------
def dashboard_view():
    st.title("2.1 Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Open Assessments", len(persistence.list_assessments()))
    col2.metric("Avg Appetite Score", "0.57", "demo")
    col3.metric("Active Guardrails", "2", "demo")
    col4.metric("Alerts (24h)", "1", "demo")
    st.subheader("Predictive Indicators (demo)")
    st.write("• Trends and KRI forecasts (placeholders).")

def rac_view():
    st.title("2.2 Foundation – RAC")
    tabs = st.tabs([
        "2.2.1 Prior Assessments",
        "2.2.2 Context & Scope",
        "2.2.3 Performance Management",
        "2.2.4 Risk Boundaries",
        "2.2.5 Appetite Statement",
        "2.2.6 Cascade & Alignment",
        "2.2.7 Review & Approvals",
        "2.2.8 Report Building",
        "2.2.9 RAC Workbench",
        "2.2.10 Appetite & Tolerance Monitor",
        "2.2.11 Delegations & Decisions Guard Rails",
        "2.2.12 Audit & Version History",
    ])

    # 2.2.1
    with tabs[0]:
        st.subheader("2.2.1 Prior Assessments")
        cats = ["Financial","Safety & HR","Reputational","Compliance","Operational","Strategic"]
        colA, colB = st.columns(2)
        with colA:
            cat = st.selectbox("Filter by category", ["(all)"] + cats)
            items = persistence.list_assessments(None if cat=="(all)" else cat)
            st.write(items or "No saved assessments yet.")
        with colB:
            st.write("Load assessment:")
            for it in items or []:
                if st.button(f"Load: {it['title']} ({it['saved_at']})", key=f"load_{it['id']}"):
                    loaded = persistence.load_assessment(it["id"])
                    if loaded:
                        st.session_state.current = loaded
                        st.success("Assessment loaded.")

    # 2.2.2
    with tabs[1]:
        st.subheader("2.2.2 Context & Scope")
        cur = st.session_state.current
        c = cur["context"]
        colA, colB = st.columns(2)
        with colA:
            c["organisation"] = st.text_input("Organisation", c["organisation"])
            c["strategic_objective"] = st.text_area("Strategic Objective", c["strategic_objective"])
            c["risk_domain"] = st.text_input("Risk Domain", c["risk_domain"])
        with colB:
            c["time_horizon_months"] = st.number_input("Time Horizon (months)", 1, 120, int(c["time_horizon_months"]))
            c["category"] = st.selectbox("Assessment Category", ["Financial","Safety & HR","Reputational","Compliance","Operational","Strategic"], index=0)

        st.divider()
        st.subheader("Dimensions")
        new_dims = []
        for i, d in enumerate(cur["dimensions"]):
            col1, col2, col3 = st.columns([3,2,2])
            with col1:
                name = st.text_input(f"Name {i+1}", d["name"], key=f"name_{i}")
            with col2:
                score = st.slider(f"Score {i+1}", 0.0, 1.0, float(d["score"]), 0.01, key=f"score_{i}")
            with col3:
                weight = st.number_input(f"Weight {i+1}", 0.0, 1.0, float(d["weight"]), 0.01, key=f"weight_{i}")
            new_dims.append({"name":name, "score":score, "weight":weight})
        cur["dimensions"] = new_dims

    # 2.2.3
    with tabs[2]:
        st.subheader("2.2.3 Performance Management")
        st.caption("Select key measures (demo).")
        st.multiselect("Key Measures", ["ROE","RAROC","NPL Ratio","CET1","LCR","Net Interest Margin","Churn Rate","LTIFR","Regulatory Findings"], default=["CET1","NPL Ratio","ROE"])

    # 2.2.4
    with tabs[3]:
        st.subheader("2.2.4 Risk Boundaries")
        col1, col2, col3 = st.columns(3)
        ws = col1.slider("Wild Success boundary", 0.7, 1.0, 0.9, 0.01)
        base = col2.slider("Expected boundary", 0.4, 0.9, 0.6, 0.01)
        fail = col3.slider("Objective Failure boundary", 0.0, 0.5, 0.3, 0.01)
        st.write(f"Boundaries set → success≥{ws}, expected≈{base}, fail≤{fail} (demo).")

    # 2.2.5
    with tabs[4]:
        st.subheader("2.2.5 Appetite Statement")
        if st.button("Calculate Appetite"):
            res = run_calculation()
            st.success(f"Band: **{res['band']}** | Weighted Score: **{res['weighted_score']:.3f}**")
            st.write(res["statement"])
        if st.session_state.current.get("result"):
            text = st.text_area("Refine statement", st.session_state.current["result"]["statement"], height=120)
            st.session_state.current["result"]["statement"] = text

    # 2.2.6
    with tabs[5]:
        st.subheader("2.2.6 Cascade & Alignment (placeholder)")
        st.table([
            {"Unit":"Retail Banking","Band":"Balanced","Notes":"Within NPL tolerance"},
            {"Unit":"SME Lending","Band":"Guarded","Notes":"Tighten concentration limits"},
            {"Unit":"Treasury","Band":"Balanced","Notes":"Liquidity stable"},
        ])

    # 2.2.7
    with tabs[6]:
        st.subheader("2.2.7 Review & Approvals")
        cur = st.session_state.current
        status = st.selectbox("Workflow Status", ["Draft","Under Review","Approved","Rejected"])
        cur["status"] = status
        approvers = st.text_input("Approvers (comma-separated)", "CRO, CFO, Head of Credit")
        cur["approvers"] = approvers

    # 2.2.8
    with tabs[7]:
        st.subheader("2.2.8 Report Building")
        md = export_markdown()
        st.download_button("Download Board Pack (Markdown)", data=md, file_name="RAC_board_pack.md")

    # 2.2.9
    with tabs[8]:
        st.subheader("2.2.9 RAC Workbench (demo)")
        if st.button("Recalculate now"):
            res = run_calculation()
            st.json(res)

    # 2.2.10
    with tabs[9]:
        st.subheader("2.2.10 Appetite & Tolerance Monitor (placeholder)")
        st.write("• No current breaches (demo).")

    # 2.2.11
    with tabs[10]:
        st.subheader("2.2.11 Delegations & Decisions Guard Rails")
        cur = st.session_state.current
        guards = cur.get("guards", [])
        st.write("Current guardrails:")
        st.table(guards)
        if st.button("Evaluate guardrails against current result"):
            if not cur.get("result"):
                st.warning("Calculate Appetite first.")
            else:
                report = evaluate_guardrails(cur["result"], guards)
                st.subheader("Evaluation")
                st.table(report)

    # 2.2.12
    with tabs[11]:
        st.subheader("2.2.12 Audit & Version History")
        cur = st.session_state.current
        if st.button("Save Assessment"):
            doc = {
                "title": cur.get("title","RAC Assessment"),
                "context": cur["context"],
                "dimensions": cur["dimensions"],
                "result": cur.get("result"),
                "status": cur.get("status","Draft"),
                "approvers": cur.get("approvers",""),
                "guards": cur.get("guards", []),
            }
            _id = persistence.save_assessment(doc)
            st.success(f"Saved assessment with id: {_id}")
        st.write("History:")
        st.write(persistence.list_assessments())

def reports_view():
    st.title("2.11 Reports")
    items = persistence.list_assessments()
    if not items:
        st.info("No assessments yet.")
        return
    ids = {f"{it['title']} ({it['saved_at']})": it["id"] for it in items}
    choice = st.selectbox("Select assessment", list(ids.keys()))
    data = persistence.load_assessment(ids[choice])
    st.subheader("Summary")
    st.write({"context": data.get("context"), "result": data.get("result"), "status": data.get("status")})
    st.download_button("Download Result JSON", data=json.dumps(data.get("result",{}), indent=2), file_name="rac_result.json", mime="application/json")
    st.download_button("Download Full Assessment JSON", data=json.dumps(data, indent=2), file_name="rac_assessment.json", mime="application/json")

def admin_view():
    st.title("2.12 Admin")
    st.subheader("Bands & Thresholds")
    path = "config/bands.yaml"
    with open(path,"r") as f:
        txt = f.read()
    new_txt = st.text_area("Edit bands.yaml", txt, height=260)
    if st.button("Save bands.yaml"):
        with open(path,"w") as f:
            f.write(new_txt)
        st.success("Saved.")

    st.subheader("Users (demo)")
    st.write([{"user":"admin@riskmetrica.ai","role":"admin"},{"user":"analyst@riskmetrica.ai","role":"analyst"}])

# ---------------- Main ----------------
def main():
    if not st.session_state.authed:
        login_view()
        return
    init_current()
    page = top_nav()
    if page == "2.1 Dashboard":
        dashboard_view()
    elif page == "2.2 Foundation – RAC":
        rac_view()
    elif page == "2.11 Reports":
        reports_view()
    elif page == "2.12 Admin":
        admin_view()
    else:
        placeholder_page(page)

if __name__ == "__main__":
    main()
