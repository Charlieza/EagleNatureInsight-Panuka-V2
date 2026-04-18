"""
EagleNatureInsight — TNFD LEAP nature-intelligence app for SMEs.

This is the main Streamlit entry point. It runs the LEAP workflow:

    Locate  →  Evaluate  →  Assess  →  Prepare

The design is narrative-first and explicitly low-jargon, per the TNFD
consultation feedback: every screen opens with plain-English text, then
supplies numbers, never the other way around. Technical metrics are paired
with a tooltip-sized explanation and a trace back to the source dataset.

The app runs in two modes automatically:

    * **Live** — if Google Earth Engine credentials are in st.secrets["earthengine"],
      metrics are computed live.
    * **Demo** — otherwise, the app uses pre-cached Panuka data so judges and
      SMEs can try the full workflow offline.
"""
from __future__ import annotations

from datetime import date
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# First-party modules (all local; no vendor lock-in)
from utils.auth import login_gate, current_user, logout, TIERS
from utils.theme import (
    inject_theme, story, callout, badge, kpi_card, leap_stepper, section_title,
)
from utils.tnfd import (
    LEAP_PHASES, NATURE_POSITIVE_METRICS, matrix_for_sector, leap_phase,
)
from utils.narrative import build_site_story, glossary
from utils.financial import translate_to_currency, assumptions_table, DEFAULT_ASSUMPTIONS
from utils.scoring import build_risk_and_recommendations
from utils.datasets import DATASETS
from utils.demo_data import PANUKA_SITES
from utils.ee_helpers import (
    initialize_ee_from_secrets, mode as ee_mode, get_site_metrics,
    get_trend_series, get_landcover_df, available_sites, site_meta,
)
from utils.pdf_report import build_pdf_report

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="EagleNatureInsight · Nature Intelligence for SMEs",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "EagleNatureInsight — Nature Intelligence for Business. "
            "Built on the TNFD LEAP framework and Nature Positive state-of-nature metrics. "
            "A Space Eagle Enterprise pilot for the Nature Intelligence for Business Grand Challenge."
        ),
    },
)

# ---------------------------------------------------------------------------
# Auth gate (also injects theme and seeds demo accounts)
# ---------------------------------------------------------------------------
user = login_gate()

# Initialise Earth Engine if possible; otherwise run in demo mode.
try:
    eng_mode = initialize_ee_from_secrets(st.secrets)
except Exception:
    eng_mode = "demo"

inject_theme()  # idempotent; ensures theme is applied on every rerun

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
_DEFAULTS = {
    "leap_phase":     "L",
    "site_key":       list(PANUKA_SITES.keys())[0],
    "sector":         "Agriculture / Agribusiness",
    "custom_lat":     "",
    "custom_lon":     "",
    "custom_buffer":  1000,
    "assumptions":    dict(DEFAULT_ASSUMPTIONS),
    "computed":       False,
    "tour_seen":      False,
}
for k, v in _DEFAULTS.items():
    st.session_state.setdefault(k, v)


# ---------------------------------------------------------------------------
# Sidebar — identity, navigation, tier, settings
# ---------------------------------------------------------------------------
# Programmatic navigation pattern: views set st.session_state["_goto"] and
# st.rerun(). Here, BEFORE the radio widget instantiates, we move the
# pending value into the widget-owned key so Streamlit accepts it.
if "_goto" in st.session_state:
    st.session_state["nav"] = st.session_state.pop("_goto")

with st.sidebar:
    st.markdown(
        f"""
        <div style="padding:4px 0 10px 0;">
            <div style="font-weight:800;font-size:18px;color:#0f5c3d;">🦅 EagleNatureInsight</div>
            <div style="color:#64748b;font-size:12px;">Nature Intelligence · TNFD LEAP</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"**{user.name}**  \n<span style='color:#64748b;font-size:12px;'>{user.organisation or ''}</span>", unsafe_allow_html=True)
    tier = user.tier_details
    st.markdown(
        f"<span class='en-badge en-badge--info'>Plan: {tier['label']}</span>",
        unsafe_allow_html=True,
    )
    st.caption(
        ("🛰️ Live data mode" if eng_mode == "live"
         else "📦 Demo mode — offline snapshot for rapid evaluation")
    )

    st.divider()
    nav = st.radio(
        "Navigate",
        ["🏠 Overview", "📍 Locate", "🔎 Evaluate", "⚖️ Assess", "📋 Prepare",
         "💼 Portfolio", "📚 Sources", "💳 Plans & pricing", "⚙️ Settings"],
        label_visibility="collapsed",
        key="nav",
    )

    st.divider()
    if st.button("Sign out", use_container_width=True, type="secondary"):
        logout()
        st.rerun()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _hero(title: str, sub: str, eyebrow: str = "EAGLENATUREINSIGHT · TNFD LEAP"):
    chips = [
        "Locate · Evaluate · Assess · Prepare",
        "Units of nature AND currency",
        "Nature Positive metrics",
        ("Live satellite data" if eng_mode == "live" else "Demo / offline ready"),
    ]
    chips_html = " ".join(f'<span class="en-chip">{c}</span>' for c in chips)
    st.markdown(
        f"""
        <div class="en-hero">
          <div class="en-hero__eyebrow">{eyebrow}</div>
          <div class="en-hero__title">{title}</div>
          <div class="en-hero__sub">{sub}</div>
          <div class="en-hero__meta">{chips_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _level_from_band(band: str) -> str:
    return {"Low": "good", "Moderate": "watch", "High": "risk"}.get(band, "watch")


def _compute_bundle() -> dict:
    """Compute (or reuse) the full metric + narrative bundle for the active site."""
    site = st.session_state["site_key"]
    sector = st.session_state["sector"] or site_meta(site).get("category", "Agriculture / Agribusiness")
    metrics = get_site_metrics(site_key=site)
    risk = build_risk_and_recommendations("", sector, metrics)
    financial = translate_to_currency(metrics, sector, st.session_state["assumptions"])
    story_text = build_site_story(site, sector, metrics, financial)
    matrix = matrix_for_sector(sector)
    return {
        "site": site, "sector": sector,
        "metrics": metrics, "risk": risk,
        "financial": financial, "story": story_text, "matrix": matrix,
    }


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------
def view_overview():
    _hero(
        "Your nature story, in plain English.",
        "A quick read of how your operations interact with nature — measured in units of "
        "nature AND units of currency, and structured around the TNFD LEAP workflow.",
    )

    leap_stepper(st.session_state["leap_phase"])

    bundle = _compute_bundle()
    story_data = bundle["story"]
    fin = bundle["financial"]

    # Headline
    story("Headline", story_data["headline"])
    story("The scene", story_data["opener"])

    # KPI strip
    c1, c2, c3, c4 = st.columns(4)
    m = bundle["metrics"]
    with c1:
        kpi_card("Rainfall vs baseline", f"{m.get('rain_anom_pct', 0):+.1f}%",
                 "Below average" if m.get("rain_anom_pct", 0) < 0 else "At or above average",
                 level="risk" if m.get("rain_anom_pct", 0) < -15 else ("watch" if m.get("rain_anom_pct", 0) < -5 else "good"))
    with c2:
        kpi_card("Vegetation health (NDVI)", f"{m.get('ndvi_current', 0):.2f}",
                 "0 = bare, 1 = lush",
                 level="risk" if m.get("ndvi_current", 0) < 0.25 else ("watch" if m.get("ndvi_current", 0) < 0.45 else "good"))
    with c3:
        kpi_card("Heat (surface)", f"{m.get('lst_mean', 0):.1f} °C",
                 "Stress threshold ~28 °C",
                 level="risk" if m.get("lst_mean", 0) > 32 else ("watch" if m.get("lst_mean", 0) > 28 else "good"))
    with c4:
        kpi_card("Biodiversity (BII)", f"{m.get('bii', 0):.2f}",
                 "1.0 = fully intact",
                 level="risk" if m.get("bii", 0) < 0.65 else ("watch" if m.get("bii", 0) < 0.80 else "good"))

    # Financial strip
    st.markdown("")
    section_title("The bottom line", "Translating nature signals into money", icon="💸")
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Risk exposure", f"${fin['downside_usd']:,.0f}",
                 f"{fin['downside_pct']:.1f}% of assumed revenue",
                 level="risk" if fin["downside_pct"] > 10 else "watch")
    with c2:
        kpi_card("Upside potential", f"${fin['upside_usd']:,.0f}",
                 f"{fin['upside_pct']:.1f}% of assumed revenue",
                 level="good")
    with c3:
        net = fin["net_usd"]
        kpi_card("Net position", f"${abs(net):,.0f}",
                 "Risk" if net > 0 else "Upside",
                 level="risk" if net > 0 else "good")
    story("What it means", story_data["bottom_line"])

    # Next step
    callout("👉 <b>One thing to do:</b> " + story_data["next_step"], "info")


def view_locate():
    _hero("Locate your site", "Step 1 of the TNFD LEAP workflow. Tell us where your business operates.")
    st.session_state["leap_phase"] = "L"
    leap_stepper("L")

    p = leap_phase("L")
    story(f"What this step is", p["plain"])

    tab_preset, tab_pin, tab_upload = st.tabs(["Use a preset site", "Drop a pin", "Upload a boundary"])
    with tab_preset:
        st.write("Choose one of the Panuka pilot sites or a built-in SME example.")
        sites = available_sites()
        idx = sites.index(st.session_state["site_key"]) if st.session_state["site_key"] in sites else 0
        pick = st.selectbox("Site", options=sites, index=idx, label_visibility="collapsed")
        st.session_state["site_key"] = pick
        meta = site_meta(pick)
        st.session_state["sector"] = meta.get("category", st.session_state["sector"])
        st.caption(f"Sector: **{st.session_state['sector']}** · Centre: ({meta.get('lat', 0):.4f}, {meta.get('lon', 0):.4f}) · Buffer: {meta.get('buffer_m', 0)} m")

        try:
            import folium
            from streamlit_folium import st_folium
            m = folium.Map(location=[meta["lat"], meta["lon"]], zoom_start=meta.get("zoom", 14),
                           tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                           attr="Esri Satellite")
            folium.Circle([meta["lat"], meta["lon"]], radius=meta.get("buffer_m", 1000),
                          color="#1f8f5f", weight=3, fill=True, fill_opacity=0.1).add_to(m)
            folium.Marker([meta["lat"], meta["lon"]], popup=pick).add_to(m)
            st_folium(m, height=420, use_container_width=True)
        except Exception as e:  # graceful degradation if folium isn't installed
            st.info("Map preview requires `folium` and `streamlit-folium`. Install them to see the basemap.")

    with tab_pin:
        st.write("Drop a pin by entering coordinates for any location on Earth.")
        col1, col2, col3 = st.columns(3)
        with col1:
            lat = st.text_input("Latitude", value=st.session_state["custom_lat"] or "-15.251")
        with col2:
            lon = st.text_input("Longitude", value=st.session_state["custom_lon"] or "28.145")
        with col3:
            buf = st.number_input("Buffer (m)", value=int(st.session_state["custom_buffer"] or 1000),
                                  min_value=200, max_value=5000, step=100)
        st.session_state["custom_lat"] = lat
        st.session_state["custom_lon"] = lon
        st.session_state["custom_buffer"] = buf
        callout("Custom pin mode uses the nearest demo snapshot in demo mode; in live mode it computes fresh satellite data for the buffered area.", "info")

    with tab_upload:
        st.write("Upload a farm boundary (GeoJSON or KML). Pro and Enterprise plans only.")
        if not user.can("tnfd_matrix"):
            callout("🔒 Boundary upload is available on the Pro and Enterprise plans.", "info")
        else:
            f = st.file_uploader("Boundary file", type=["geojson", "json", "kml"])
            if f:
                st.success("Boundary received — processing will begin in Evaluate.")

    section_title("Why your sector matters", "Your dependencies & impacts differ by sector.", icon="🏷️")
    sectors = list({m["category"] for m in PANUKA_SITES.values()}) + ["Manufacturing / Industrial", "Property / Built environment", "Food processing / Supply chain", "Energy / Infrastructure", "Water / Circular economy"]
    sectors = list(dict.fromkeys(sectors))  # preserve order, de-dup
    st.session_state["sector"] = st.selectbox("Business sector", sectors,
                                              index=sectors.index(st.session_state["sector"]) if st.session_state["sector"] in sectors else 0)

    st.divider()
    if st.button("Next → Evaluate", type="primary"):
        st.session_state["leap_phase"] = "E"
        st.session_state["_goto"] = "🔎 Evaluate"
        st.rerun()


def view_evaluate():
    _hero("Evaluate: dependencies & impacts",
          "Step 2 of LEAP. We translate satellite data into a plain-English story of what nature gives you, and what you change about it.")
    st.session_state["leap_phase"] = "E"
    leap_stepper("E")
    p = leap_phase("E")
    story("What this step is", p["plain"])

    b = _compute_bundle()
    m, s = b["metrics"], b["story"]

    # Dependencies side / Impacts side
    col_d, col_i = st.columns(2)
    with col_d:
        section_title("What nature gives you", "Your dependencies", icon="🌿")
        for d in s["dependencies"]:
            st.markdown(f"- {d}")
        st.markdown("")
        section_title("TNFD dependency matrix", f"Sector: {b['sector']}", icon="🧭")
        for row in b["matrix"]["dependencies"]:
            st.markdown(
                f"""
                <div class="en-matrix-cell">
                  <b>{row.service}</b> &nbsp; {badge(row.rating)}<br/>
                  <span style='color:#334155;font-size:14px;'>{row.why}</span><br/>
                  <span style='color:#64748b;font-size:12px;'>Measured in: {row.nature_unit}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with col_i:
        section_title("What you change about nature", "Your impacts", icon="🏭")
        for d in s["impacts"]:
            st.markdown(f"- {d}")
        st.markdown("")
        section_title("TNFD pressure categories", "", icon="⚙️")
        for row in b["matrix"]["impacts"]:
            st.markdown(
                f"""
                <div class="en-matrix-cell">
                  <b>{row.service}</b> &nbsp; {badge(row.rating)}<br/>
                  <span style='color:#334155;font-size:14px;'>{row.why}</span><br/>
                  <span style='color:#64748b;font-size:12px;'>Measured in: {row.nature_unit}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Trend charts
    st.markdown("---")
    section_title("Trends over time", "What has been changing at your site", icon="📈")
    c1, c2, c3 = st.columns(3)
    site_key = b["site"]
    with c1:
        df = get_trend_series(site_key, "ndvi")
        fig = px.line(df, x="year", y="value", markers=True, title="Vegetation health (NDVI) per year")
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        df = get_trend_series(site_key, "rain")
        fig = px.bar(df, x="year", y="value", title="Annual rainfall (mm)")
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    with c3:
        df = get_trend_series(site_key, "lst")
        fig = px.line(df, x="year", y="value", markers=True, title="Surface temperature (°C)")
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Land cover
    section_title("Land-cover mix", "What the area is made of today", icon="🗺️")
    lc = get_landcover_df(site_key)
    fig = px.bar(lc.sort_values("area_ha", ascending=True), x="area_ha", y="class_name", orientation="h")
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Area (ha)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("← Back to Locate"):
            st.session_state["_goto"] = "📍 Locate"
            st.rerun()
    with col_next:
        if st.button("Next → Assess", type="primary"):
            st.session_state["_goto"] = "⚖️ Assess"
            st.rerun()


def view_assess():
    _hero("Assess: risks and opportunities",
          "Step 3 of LEAP. We prioritise the issues in plain English and translate them into dollars — so banks, funders, and boards can act.")
    st.session_state["leap_phase"] = "A"
    leap_stepper("A")
    p = leap_phase("A")
    story("What this step is", p["plain"])

    b = _compute_bundle()
    risk = b["risk"]
    fin = b["financial"]

    # Portfolio matrix header (per TNFD meeting feedback: "portfolio of matrix, not a single score")
    section_title("Portfolio matrix", "Risks, impacts, dependencies and opportunities — as TNFD asks", icon="🧩")
    structured = risk.get("structured", [])
    if not structured:
        st.info("No dominant flags detected — monitor seasonally.")
    else:
        # Group by kind
        kinds = ["Dependency", "Impact", "Risk", "Opportunity"]
        cols = st.columns(len(kinds))
        for col, kind in zip(cols, kinds):
            with col:
                st.markdown(f"**{kind}**")
                items = [x for x in structured if x["kind"] == kind]
                if not items:
                    st.caption("None flagged.")
                for it in items:
                    st.markdown(
                        f"""
                        <div class="en-matrix-cell">
                          <b>{it['title']}</b><br/>
                          <span style='color:#334155;font-size:13px;'>{it['body']}</span><br/>
                          <span style='color:#64748b;font-size:12px;'>Triggered by <code>{it['metric']}</code></span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # Financial materiality
    st.markdown("---")
    section_title("Financial materiality", "Units of nature translated into units of currency", icon="💰")
    fin_df = pd.DataFrame(fin["lines"])
    if not fin_df.empty:
        fin_df["direction"] = fin_df["business_impact_usd"].apply(lambda x: "Downside" if x > 0 else "Upside")
        fig = px.bar(
            fin_df, x="business_impact_usd", y="label", color="direction",
            orientation="h",
            color_discrete_map={"Downside": "#dc2626", "Upside": "#16a34a"},
            labels={"business_impact_usd": "USD / year", "label": ""},
            title="Revenue at risk / upside — by driver",
        )
        fig.update_layout(height=360, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            fin_df[["label", "nature_unit", "nature_value", "business_impact_pct", "business_impact_usd", "rationale"]]
            .rename(columns={
                "label": "Driver", "nature_unit": "Unit of nature",
                "nature_value": "Value", "business_impact_pct": "% revenue",
                "business_impact_usd": "USD / year", "rationale": "Why",
            }),
            hide_index=True, use_container_width=True,
        )
    else:
        st.info("No financial drivers triggered for this site.")

    with st.expander("What assumptions are behind the dollar numbers?"):
        st.caption(
            "These assumptions are tunable on the Settings page. They are deliberately transparent "
            "so SMEs and banks can challenge them and replace them with their own."
        )
        st.dataframe(pd.DataFrame(assumptions_table(st.session_state["assumptions"])),
                     hide_index=True, use_container_width=True)

    st.divider()
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("← Back to Evaluate"):
            st.session_state["_goto"] = "🔎 Evaluate"
            st.rerun()
    with col_next:
        if st.button("Next → Prepare", type="primary"):
            st.session_state["_goto"] = "📋 Prepare"
            st.rerun()


def view_prepare():
    _hero("Prepare: the report you can send to a banker",
          "Step 4 of LEAP. One click produces a TNFD-aligned PDF with the full story, the dependency matrix, and the dollar view.")
    st.session_state["leap_phase"] = "P"
    leap_stepper("P")
    p = leap_phase("P")
    story("What this step is", p["plain"])

    b = _compute_bundle()

    # Next moves
    section_title("Your next moves", "", icon="🚀")
    for i, rec in enumerate(b["risk"].get("recs", []), 1):
        st.markdown(f"**{i}.** {rec}")

    # Nature Positive pillars snapshot
    section_title("Nature Positive state-of-nature snapshot", "Extent · Condition · Species · Sensitive places", icon="🌎")
    np_rows = []
    for n in NATURE_POSITIVE_METRICS:
        key = {
            "Natural habitat area (ha)": "tree_pct",
            "Biodiversity Intactness Index (BII, 0–1)": "bii",
            "Forest Landscape Integrity Index (FLII, 0–10)": "flii",
            "Threatened species count (IUCN Red List, range overlap)": "threatened_species_count",
            "Distance to nearest KBA / WDPA polygon (km)": "kba_distance_km",
        }.get(n["indicator"])
        val = b["metrics"].get(key)
        np_rows.append({
            "Pillar": n["pillar"], "Indicator": n["indicator"],
            "Value": val, "Plain meaning": n["plain"], "Source layer": n["source_layer"],
        })
    st.dataframe(pd.DataFrame(np_rows), hide_index=True, use_container_width=True)

    # Build PDF bytes
    wm = "DEMO" if eng_mode != "live" or user.can("pdf_watermark") else None  # basic watermark logic
    try:
        nat_pos_for_pdf = []
        for n, row in zip(NATURE_POSITIVE_METRICS, np_rows):
            nat_pos_for_pdf.append({**n, "key": None})  # plain pass-through
        pdf = build_pdf_report(
            site_name=b["site"], sector=b["sector"],
            story=b["story"], metrics=b["metrics"],
            financial=b["financial"], risk=b["risk"],
            tnfd_matrix=b["matrix"],
            nature_positive=nat_pos_for_pdf,
            datasets=DATASETS,
            watermark=wm,
        )
        st.download_button(
            "📄 Download TNFD-aligned PDF report",
            data=pdf,
            file_name=f"EagleNatureInsight_{b['site'].split(' — ')[0].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
    except Exception as e:
        st.error(f"Could not render PDF: {e}")
        st.info("Install reportlab (`pip install reportlab`) to enable PDF export.")

    # Excel export
    try:
        xlsx_buf = BytesIO()
        with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
            pd.DataFrame([b["metrics"]]).to_excel(writer, sheet_name="Metrics", index=False)
            pd.DataFrame(b["risk"]["structured"]).to_excel(writer, sheet_name="Risk_Matrix", index=False)
            pd.DataFrame(b["financial"]["lines"]).to_excel(writer, sheet_name="Financial", index=False)
            pd.DataFrame(DATASETS).to_excel(writer, sheet_name="Sources", index=False)
        xlsx_buf.seek(0)
        st.download_button(
            "📊 Download raw data (Excel)",
            data=xlsx_buf.getvalue(),
            file_name=f"EagleNatureInsight_{b['site'].split(' — ')[0].replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    except Exception:
        st.caption("Excel export requires `openpyxl`. It will be enabled in cloud deployment.")


def view_portfolio():
    _hero("Portfolio view",
          "See every site you track, in one place. Ideal for incubators like Panuka who support many SMEs.")

    if not user.can("tnfd_matrix"):
        callout("🔒 Portfolio view is available on the Pro and Enterprise plans. It lets you compare all SMEs across your network.", "info")
        return

    rows = []
    for site in available_sites():
        m = get_site_metrics(site_key=site)
        sector = site_meta(site).get("category", "Agriculture / Agribusiness")
        r = build_risk_and_recommendations("", sector, m)
        f = translate_to_currency(m, sector, st.session_state["assumptions"])
        rows.append({
            "Site": site, "Sector": sector,
            "NDVI": m.get("ndvi_current"),
            "Rain anomaly %": m.get("rain_anom_pct"),
            "Heat °C": m.get("lst_mean"),
            "BII": m.get("bii"),
            "Risk band": r["band"],
            "Downside %": round(f["downside_pct"], 1),
            "Upside %":   round(f["upside_pct"], 1),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, use_container_width=True)

    fig = px.scatter(
        df, x="Heat °C", y="NDVI", size="Downside %",
        color="Risk band", hover_name="Site",
        color_discrete_map={"Low": "#16a34a", "Moderate": "#eab308", "High": "#dc2626"},
        title="Portfolio: vegetation health vs heat, sized by revenue-at-risk",
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)


def view_sources():
    _hero("Sources & limitations",
          "Every number in this tool traces back here. No black boxes, no vendor lock-in.")

    st.caption(
        "Aligned with TNFD Recommendation D1 on transparency and Nature Positive "
        "Initiative principle of open, auditable methods."
    )
    df = pd.DataFrame(DATASETS)[["layer", "source", "resolution", "update_cadence",
                                 "units_of_nature", "covers", "limits", "licence"]]
    st.dataframe(df, hide_index=True, use_container_width=True,
                 column_config={
                     "layer": "Layer",
                     "source": "Source",
                     "resolution": "Resolution",
                     "update_cadence": "Updates",
                     "units_of_nature": "Unit of nature",
                     "covers": "What it covers",
                     "limits": "Known limits",
                     "licence": "Licence",
                 })

    st.markdown("---")
    section_title("Glossary", "Plain-English translation of every term we use.", icon="📖")
    for g in glossary():
        st.markdown(f"**{g['term']}** — {g['plain']}")


def view_pricing():
    _hero("Plans & pricing",
          "Built for SMEs first — a free tier that actually works, and paid tiers that unlock portfolio-level TNFD disclosure.")

    cols = st.columns(3)
    for col, key in zip(cols, ["free", "pro", "enterprise"]):
        t = TIERS[key]
        featured = " en-price--featured" if key == "pro" else ""
        with col:
            st.markdown(
                f"""
                <div class="en-price{featured}">
                  <div class="en-price__tier">{t['label']}</div>
                  <div class="en-price__amount">${t['monthly_usd']}<span style='font-size:14px;color:#64748b;'> /month</span></div>
                  """
                + "".join(f'<div class="en-price__feat">• {f}</div>' for f in t['features'])
                + "</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    section_title("Go-to-market strategy", "How we plan to reach SMEs at scale", icon="📡")
    st.markdown(
        """
- **Incubators and hubs** (e.g. Panuka AgriBiz Hub) bundle the Free tier into their SME onboarding. We share revenue when SMEs upgrade to Pro.
- **Banks and development-finance institutions** embed our report into loan applications. White-label Enterprise deployments sit alongside their credit-scoring tools.
- **Sustainability consultants and accountants** resell Pro on a seat basis to their SME clients.
- **Data-partner marketplaces** (Google Earth Engine, ESA Copernicus, Microsoft Planetary Computer) distribute the free tier as a showcase.
- **Advertiser-supported demo experience**: SME-friendly brands (seed companies, irrigation suppliers, climate insurers) can sponsor contextually relevant tips that appear in the Prepare step — an unorthodox funding model requested by the TNFD consultation and common in African SME tools.
        """
    )

    st.markdown("---")
    section_title("Product roadmap (next 12 months)", "", icon="🗺️")
    roadmap = pd.DataFrame([
        {"Quarter": "Q2 2026", "Delivery": "Pilot-feedback fixes; Swahili, French, Portuguese localisation"},
        {"Quarter": "Q2 2026", "Delivery": "Mobile-first redesign + PWA for offline field use"},
        {"Quarter": "Q3 2026", "Delivery": "Bank-ready loan annex template; WDPA/KBA live layer"},
        {"Quarter": "Q3 2026", "Delivery": "Species overlap layer live (IUCN range polygons + GBIF)"},
        {"Quarter": "Q4 2026", "Delivery": "Public API + Microsoft / Google marketplace listing"},
        {"Quarter": "Q1 2027", "Delivery": "Data-residency deployment option (Zambia + Kenya)"},
    ])
    st.dataframe(roadmap, hide_index=True, use_container_width=True)


def view_settings():
    _hero("Settings", "Tune the assumptions behind every dollar number you see.")
    st.caption("We expose these values because TNFD asked for transparency — you should be able to replace ours with yours.")

    assump = st.session_state["assumptions"]
    new_vals = {}
    cols = st.columns(2)
    for i, (k, v) in enumerate(DEFAULT_ASSUMPTIONS.items()):
        with cols[i % 2]:
            new_vals[k] = st.number_input(k, value=float(assump.get(k, v)), key=f"set_{k}")
    if st.button("Save assumptions", type="primary"):
        st.session_state["assumptions"].update(new_vals)
        st.success("Saved. Head back to Assess to see the updated currency numbers.")

    st.markdown("---")
    section_title("Data sovereignty", "Where your data lives", icon="🛡️")
    st.markdown(
        """
- Your account and assumptions are stored locally in a SQLite file (`data/eni_users.sqlite3`). No third-party SaaS.
- Earth Engine calls happen in your own Google Cloud project — you own the keys and quotas.
- Export your data at any time via the Excel button in **Prepare**.
- Enterprise deployments support on-premise installation and in-country data residency (Zambia, Kenya, South Africa).
        """
    )


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------
route = {
    "🏠 Overview":         view_overview,
    "📍 Locate":           view_locate,
    "🔎 Evaluate":         view_evaluate,
    "⚖️ Assess":           view_assess,
    "📋 Prepare":          view_prepare,
    "💼 Portfolio":        view_portfolio,
    "📚 Sources":          view_sources,
    "💳 Plans & pricing":  view_pricing,
    "⚙️ Settings":         view_settings,
}
route.get(nav, view_overview)()
