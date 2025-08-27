# RiskMetrica – RAC Prototype (Streamlit Cloud)

This repo contains a **Streamlit** prototype of the Risk Appetite Calculator (RAC) scoped to your platform map:

- **1. Login** (stubbed)
- **2.1 Dashboard**
- **2.2 Foundation – RAC** (tabs **2.2.1 → 2.2.12**)
- **2.11 Reports**
- **2.12 Admin**
- All other sections present as placeholders for click-through.

## Deploy to Streamlit Community Cloud

1. Create a new GitHub repo (e.g., `riskmetrica-rac-streamlit`).
2. Upload all files from this repo.
3. Go to https://share.streamlit.io → **New app** → select your repo.
4. Set **Main file path** to `app.py`, Branch `main`, then **Deploy**.

### Notes
- No secrets required for this prototype.
- Assessments are saved as JSON under `data/assessments` (ephemeral in Cloud).
- Appetite bands live in `config/bands.yaml` (editable from the Admin page).
