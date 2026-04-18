# Rubric alignment — Nature Intelligence for Business Grand Challenge

This document maps every rubric criterion to the exact change in EagleNatureInsight v2.

---

## 1. User / Customer Experience — up to 30 pts

### 1a. Intuitiveness & Ease of Use (up to 7 pts)

- **Narrative-first everywhere.** Every screen opens with a plain-English "story" block (`utils/theme.py::story`) and only then shows numbers.
- **Demo accounts** (`utils/auth.py::DEMO_ACCOUNTS`) let judges try the tool in under 10 seconds — no SaaS sign-up, no Earth Engine credentials required.
- **LEAP wizard** renders at the top of every screen (`utils/theme.py::leap_stepper`) so users always know where they are.
- **Glossary** (`utils/narrative.py::glossary`) explains every jargon term in one sentence.

### 1b. Deployable & manageable in SME environments (up to 8 pts)

- **Offline / demo mode** is the default; the app runs fully without internet via `utils/demo_data.py` snapshots.
- **Mobile-friendly CSS** (`@media (max-width: 720px)` block in `utils/theme.py`).
- **Pure-Python stack** (ReportLab + openpyxl + SQLite) — no Chrome, no Postgres, no cloud-only dependencies.
- **No vendor lock-in** — auth in SQLite, assumptions in session state, exports in PDF/Excel, Earth Engine runs in the user's own Google Cloud project.

### 1c. Clarity of TNFD LEAP workflow & data requirements (up to 8 pts)

- **Explicit LEAP navigation** (Locate → Evaluate → Assess → Prepare) in the sidebar and stepper.
- **Tooltips and explainer copy** on every input (`utils/tnfd.py::LEAP_PHASES[*]['plain']`).
- **Data inputs are optional** — pick a Panuka preset, drop a pin, or upload GeoJSON/KML. No form walls.
- **Scope is explicit** — every dataset's `covers` and `limits` is shown in the Sources page.

### 1d. Interpretability & actionability of outputs (up to 7 pts)

- **Every metric paired with plain meaning** (`utils/tnfd.py::NATURE_POSITIVE_METRICS[*]['plain']` and `utils/narrative.py::build_site_story`).
- **Financial translation** converts every nature metric into a USD risk/upside line (`utils/financial.py`).
- **"One thing to do"** callout at the bottom of the Overview gives SMEs a single next action.
- **Banker-ready PDF** with risk, matrix, dollar view, and next moves.

---

## 2. Solution Performance — up to 40 pts

### 2a. Alignment with TNFD LEAP approach & metrics (up to 10 pts)

- **LEAP phases encoded as data** (`utils/tnfd.py::LEAP_PHASES`) with the four TNFD questions per phase.
- **Dependency matrix** is drawn from the TNFD 2023 Annex sector guidance (`utils/tnfd.py::SECTOR_DEPENDENCIES`, `SECTOR_IMPACTS`).
- **Portfolio matrix, not a single score.** Per TNFD meeting feedback: in Assess we show Dependency · Impact · Risk · Opportunity columns side-by-side, with an aggregate score used only as a navigation aid, not a substitute.
- **Dependencies, impacts, risks and opportunities are all covered** in `utils/scoring.py`.

### 2b. Scientific rigor & data quality (up to 10 pts)

Datasets (all referenced in `utils/datasets.py`):

- Sentinel-2 L2A (ESA Copernicus)
- CHIRPS v2.0 (UCSB CHG)
- MODIS MOD11A2 / MOD16A2 (NASA)
- ESA WorldCover 2021
- Hansen Global Forest Change (UMD)
- JRC Global Surface Water v1.4
- JRC/CEMS GloFAS flood hazard
- MODIS MCD64A1 burned area
- SoilGrids v2.0 (ISRIC)
- **Biodiversity Intactness Index** (NHM PREDICTS)
- **Forest Landscape Integrity Index** (Grantham et al. 2020)
- **WDPA** (UNEP-WCMC)
- **KBA** (KBA Partnership)
- **IUCN Red List** threatened-species ranges
- **WRI Aqueduct 4.0** water stress
- Pollinator habitat suitability (InVEST derivative)

### 2c. Transparency of methodology & limitations (up to 10 pts)

- **Sources page** lists every layer with source, resolution, cadence, units, limits, licence.
- **PDF appendix** repeats the same for auditors and bankers.
- **Assumptions table** (`utils/financial.py::assumptions_table`) exposes every sensitivity constant behind the USD numbers. Users can tune and save them in Settings.
- **Scope boundaries** — we mark proxies as proxies (e.g. pollinator suitability, greenhouse pest-risk indicator).

### 2d. Adaptability & contextual flexibility (up to 10 pts)

- **Six sectors supported** out of the box (Agri, Food processing, Manufacturing, Property, Energy, Water).
- **Geography-agnostic** — any lat/lon; Panuka presets included for the pilot.
- **Regulatory flexibility** — data is stored locally (SQLite); Enterprise tier supports on-premise deployment and Zambia/Kenya/South Africa residency.
- **Portable tech stack** — Streamlit + Python; no proprietary runtime.

---

## 3. Solution Plan — up to 30 pts

### 3a. Pricing accessibility for SMEs (up to 8 pts)

| Tier | Monthly | Fit |
| --- | --- | --- |
| Free | $0 | 1 site / month, watermarked PDF. Aimed at SMEs the first time they think about nature. |
| Pro | $49 | Unlimited sites + TNFD matrix + Nature Positive + branded PDF. Aimed at established SMEs and consultants. |
| Enterprise | $399 | SSO, white-label, API, data residency. Aimed at banks, DFIs, incubators with many SMEs. |

### 3b. Commercial model sustainability (up to 10 pts)

- **Who pays** is explicit: incubators bundle Free → upgrade to Pro; banks white-label Enterprise into loan flows; consultants resell Pro per seat.
- **Advertising-supported demo** (TNFD meeting feedback on unorthodox funding): contextual tips from seed, irrigation, or insurance brands in the Prepare step.
- **Mission-aligned** — the Free tier is genuinely useful, not a crippled trial.

### 3c. Go-to-market & SME adoption strategy (up to 7 pts)

- **Incubators** — Panuka, iHub, Seedstars bundle the Free tier into SME onboarding.
- **Banks and DFIs** — AFDB, FMO, AfricInvest integrate Enterprise into credit workflows.
- **Accountants and sustainability consultants** — per-seat Pro licensing.
- **Platform partnerships** — Google Earth Engine showcase, ESA Copernicus, Microsoft Planetary Computer listings.
- **Adoption barriers addressed** — Free tier is no-cost; demo mode removes connectivity barrier; demo accounts remove onboarding friction; localisation on the roadmap.

### 3d. Iteration & roadmap (up to 5 pts)

Visible 12-month roadmap in the Plans & pricing page:

- Q2 2026 — pilot-feedback fixes; Swahili/French/Portuguese localisation
- Q2 2026 — mobile-first PWA for offline field use
- Q3 2026 — bank-ready loan annex template; WDPA/KBA live layer
- Q3 2026 — species overlap layer (IUCN range polygons + GBIF)
- Q4 2026 — public API + Microsoft / Google marketplace listings
- Q1 2027 — data-residency deployment (Zambia + Kenya)

---

## What was removed from v1 (and why)

| v1 pattern | Issue | v2 replacement |
| --- | --- | --- |
| Dashboard-first layout | Users drowned in NDVI/LST/ET numbers | Narrative-first LEAP wizard |
| Single aggregate "score" | TNFD explicitly said *not* to do this | Portfolio matrix: dependency/impact/risk/opportunity |
| Earth Engine required | Judges without credentials couldn't try the app | Demo mode + live mode |
| No login | No SME account model, no monetisation story | Auth with Free/Pro/Enterprise + SSO stubs |
| No currency translation | TNFD asked for "units of currency" | `utils/financial.py` translates every metric to USD |
| No biodiversity / KBA / species | Rubric 2a asked for comprehensive nature coverage | BII, FLII, KBA, WDPA, IUCN, Aqueduct, pollinator, soil |
| No transparency of limitations | Rubric 2c | Sources page + PDF appendix + assumptions table |
| No go-to-market clarity | Rubric 3b–3c | Plans & pricing page with partnership strategy and roadmap |
