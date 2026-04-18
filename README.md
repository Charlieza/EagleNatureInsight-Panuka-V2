# EagleNatureInsight

**Nature intelligence for SMEs — TNFD LEAP, in plain English.**
A Space Eagle Enterprise pilot for the Nature Intelligence for Business Grand Challenge (TNFD · Conservation X Labs · IKI · UNDP).

EagleNatureInsight turns satellite and environmental data into a short, clear nature story any SME can act on. It is built on the **TNFD LEAP framework** (Locate → Evaluate → Assess → Prepare) and reports in **units of nature AND units of currency**, as TNFD asked.

---

## Quick start

```bash
# 1. Create a virtualenv and install dependencies
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Launch the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Try it instantly (demo accounts)

| Persona | Email | Password |
| --- | --- | --- |
| TNFD Judge (Enterprise) | `judge@tnfd.org` | `judge2026` |
| Panuka demo (Pro) | `demo@panuka.io` | `panuka123` |
| SME demo (Free) | `sme@spaceeagle.io` | `demo1234` |

The app runs in **demo mode** out-of-the-box — no Google Earth Engine credentials needed. Drop your service-account JSON into `.streamlit/secrets.toml` under `[earthengine]` and the app automatically switches to **live mode**.

```toml
# .streamlit/secrets.toml — example
[earthengine]
type = "service_account"
project_id = "your-gcp-project"
private_key_id = "..."
private_key = "..."
client_email = "ee-service@your-project.iam.gserviceaccount.com"
# ... rest of the service-account JSON keys ...
```

---

## What's included

| Layer | What it does | File |
| --- | --- | --- |
| Premium UI | Custom CSS theme, narrative-first layout, mobile-friendly | `utils/theme.py` |
| Auth | Email/password + tier model + Google/Microsoft SSO stubs | `utils/auth.py` |
| TNFD LEAP | Phase metadata, dependency matrix per sector | `utils/tnfd.py` |
| Nature Positive | State-of-nature pillar scaffolding (Jan 2025 draft) | `utils/tnfd.py` |
| Story engine | Plain-English narrative from any metric bag | `utils/narrative.py` |
| Currency translator | Risk and opportunity in USD | `utils/financial.py` |
| Scoring | TNFD-aligned dependency / impact / risk / opportunity flags | `utils/scoring.py` |
| Earth Engine | Live + demo dual-mode metric provider | `utils/ee_helpers.py` |
| Datasets catalogue | Source, resolution, cadence, limits, licence | `utils/datasets.py` |
| Report | Banker-ready PDF + Excel | `utils/pdf_report.py` |

See [`RUBRIC_ALIGNMENT.md`](RUBRIC_ALIGNMENT.md) for the line-by-line scorecard mapping.

---

## How it tracks the rubric (summary)

- **1a Intuitiveness** — narrative-first; every screen opens with plain English.
- **1b Deployable in low-bandwidth** — single `streamlit run`; demo mode runs without internet.
- **1c LEAP clarity** — explicit Locate / Evaluate / Assess / Prepare wizard with the LEAP stepper visible on every screen.
- **1d Interpretability** — every chart paired with a one-sentence explanation; glossary for every jargon term.
- **2a TNFD LEAP fidelity** — the four phases drive the navigation; the dependency matrix is encoded directly from the TNFD 2023 Annex.
- **2b Scientific rigor** — datasets are reputable (Sentinel-2, CHIRPS, MODIS, WorldCover, Hansen, JRC GSW, GloFAS, BII, FLII, WDPA, KBA, IUCN, Aqueduct, SoilGrids).
- **2c Transparency** — `Sources & Limitations` page lists resolution, cadence, units, limits, licence for every layer.
- **2d Adaptability** — works across six sectors out-of-the-box; SQLite storage; no vendor lock-in; data-residency story.
- **3a Pricing** — Free tier with 1 site/month; Pro at $49; Enterprise at $399.
- **3b Commercial model** — paying-customer pathway (incubators bundle Free, banks white-label Enterprise, consultants resell Pro).
- **3c Go-to-market** — incubators, banks, consultants, marketplace listings, advertiser-supported demo (an unorthodox model TNFD asked us to consider).
- **3d Iteration** — visible 12-month roadmap.

---

## Architecture in one paragraph

`app.py` is the only Streamlit entry. It calls the `auth` module for the login gate, then the `theme` module for CSS, then routes to one of nine views (Overview, Locate, Evaluate, Assess, Prepare, Portfolio, Sources, Plans, Settings). Each view assembles a *bundle* of metrics → story → financial → matrix by composing the `ee_helpers`, `narrative`, `financial`, `scoring`, and `tnfd` modules. The PDF and Excel exports compose the same bundle, so the user sees consistent numbers everywhere.

## License

MIT for the application code. Data licences are layer-specific — see `utils/datasets.py`.
