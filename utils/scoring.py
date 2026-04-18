"""
TNFD-aligned site scoring.

This is *not* a black-box score. Following TNFD's explicit guidance, the tool
reports a **portfolio of indicators** (the TNFD disclosure matrix) and treats
any aggregate number strictly as a navigation aid for SMEs — never as a
substitute for the underlying metrics.

Each flag is categorised into one of the four TNFD nature-related issues:
  - Dependency
  - Impact
  - Risk  (physical / transition)
  - Opportunity

The flag also records the metric that triggered it, so the PDF report can
trace any claim back to a specific satellite reading.
"""
from __future__ import annotations


def _num(v):
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


def build_risk_and_recommendations(preset: str, category: str, metrics: dict) -> dict:
    flags: list[dict] = []
    recs: list[str] = []
    score = 0

    def add(kind: str, pts: int, title: str, body: str, rec: str, metric: str):
        nonlocal score
        score += pts
        flags.append({
            "kind": kind,
            "title": title,
            "body": body,
            "rec": rec,
            "metric": metric,
            "points": pts,
        })
        recs.append(rec)

    # Dependencies (what nature gives you)
    water = _num(metrics.get("water_occ"))
    if water is not None and water < 5:
        add("Dependency", 12,
            "High dependence on off-site water",
            f"Visible surface water is only {water:.1f}%. Operations lean heavily on boreholes or storage, which raises costs and fragility in dry years.",
            "Formalise a water-reliability plan: metered use, backup storage, and a drought trigger that moves the business to water-saving mode.",
            "water_occ")

    bii = _num(metrics.get("bii"))
    if bii is not None and bii < 0.80:
        add("Dependency", 10,
            "Pollination and pest-control dependency at risk",
            f"Biodiversity intactness around the site is {bii:.2f} (1.0 = fully intact). This typically means fewer pollinators and natural pest controllers.",
            "Protect pollinator strips, wild-flower margins, and reduce pesticide intensity on 10–15% of the land.",
            "bii")

    kba_km = _num(metrics.get("kba_distance_km"))
    if kba_km is not None and kba_km < 20:
        add("Dependency", 6,
            "Operation close to a Key Biodiversity Area",
            f"The site is within ~{kba_km:.0f} km of a KBA. Lenders and regulators may require extra due diligence.",
            "Adopt a simple biodiversity-screening checklist before any expansion, and keep a photo log of on-site wildlife.",
            "kba_distance_km")

    # Impacts (what you change about nature)
    forest_loss = _num(metrics.get("forest_loss_pct"))
    if forest_loss is not None and forest_loss > 2:
        add("Impact", 8,
            "Tree cover loss signal in the landscape",
            f"About {forest_loss:.1f}% of tree cover has been lost recently. Even if not directly caused by you, it erodes the buffers that protect your site.",
            "Avoid further clearance on-site; plant shade trees and native windbreaks to rebuild habitat connectivity.",
            "forest_loss_pct")

    built = _num(metrics.get("built_pct"))
    if built is not None and built > 30:
        add("Impact", 6,
            "High built-up share",
            f"{built:.0f}% of the site is built-up. Hard surfaces reduce infiltration and raise local heat.",
            "Retrofit with permeable surfaces, small green corridors, and shade-giving trees to improve liveability and reduce cooling costs.",
            "built_pct")

    # Risks (physical and transition)
    rain = _num(metrics.get("rain_anom_pct"))
    if rain is not None and rain < -10:
        add("Risk", 15,
            "Below-average rainfall (physical)",
            f"Rainfall is about {abs(rain):.0f}% below the 30-year baseline. Expect lower yields, higher irrigation demand, and water-pricing pressure.",
            "Switch to drought-tolerant cultivars where possible, add mulching and soil cover, and shift irrigation to drip on the driest fields.",
            "rain_anom_pct")

    lst = _num(metrics.get("lst_mean"))
    if lst is not None and lst > 30:
        add("Risk", 12,
            "Heat stress (physical)",
            f"Average surface temperature is {lst:.1f}°C — crops, livestock, and workers all lose productivity at this level.",
            "Install shade for livestock and workers; ventilate greenhouses; schedule labour for cooler hours.",
            "lst_mean")

    flood = _num(metrics.get("flood_risk"))
    if flood is not None and flood > 0.3:
        add("Risk", 10,
            "Flood exposure (physical)",
            f"Modelled 1-in-100-year flood depth is {flood:.2f} m. Low-lying fields, stores, and access roads are at risk.",
            "Raise critical infrastructure above the 1-in-100-year line; keep emergency stock in a second location.",
            "flood_risk")

    aqueduct = _num(metrics.get("aqueduct_stress"))
    if aqueduct is not None and aqueduct >= 3:
        add("Risk", 8,
            "Upstream water stress (transition)",
            f"The wider basin is in Aqueduct stress category {aqueduct:.0f}/5. Expect tighter water rules and higher tariffs.",
            "Track basin-level water plans; pre-position for tariff changes by reducing waste now.",
            "aqueduct_stress")

    fire = _num(metrics.get("fire_risk"))
    if fire is not None and fire > 5:
        add("Risk", 6,
            "Recent fire signal nearby",
            f"A burn-area indicator of {fire:.1f} suggests recent fire activity within the screening area.",
            "Create or refresh firebreaks and clear dry debris near buildings and fences before the dry season peaks.",
            "fire_risk")

    ndvi = _num(metrics.get("ndvi_current"))
    if ndvi is not None and ndvi < 0.25:
        add("Risk", 8,
            "Weak vegetation cover",
            f"NDVI is {ndvi:.2f} — very low. Weak cover means drier, hotter topsoil and higher erosion.",
            "Cover-crop the driest areas and prioritise 2–3 fields for intensive management before planting next cycle.",
            "ndvi_current")

    # Opportunities
    tree_pct = _num(metrics.get("tree_pct"))
    if tree_pct is not None and tree_pct > 10:
        add("Opportunity", -4,
            "Carbon and biodiversity credit potential",
            f"With ~{tree_pct:.0f}% tree cover, the site already has a base for regenerative land-use and voluntary-market credits.",
            "Pilot a small carbon or biodiversity credit scheme on 1–2 hectares; use it to test project economics.",
            "tree_pct")

    if ndvi is not None and ndvi >= 0.45 and (rain is None or rain >= -5):
        add("Opportunity", -3,
            "Conditions support regenerative practices",
            "Healthy vegetation and adequate rainfall create a window for cover cropping, mulching, and reduced-till practices.",
            "Commit to one regenerative practice this cycle and measure yield + cost impact against a matched field.",
            "ndvi_current")

    # Sector-specific nudges
    if "Agri" in category:
        recs.append("Use the TNFD dependency matrix tab to explain nature dependencies to staff and funders.")
    elif "Food" in category:
        recs.append("Extend screening to your three largest supplier zones — most of your nature risk is upstream.")
    elif "Manufacturing" in category:
        recs.append("Run a quick water-balance on the site: compare metered use to the Aqueduct basin baseline.")

    # Tier / band
    score = max(0, min(score, 100))
    band = "Low"
    if score >= 55:
        band = "High"
    elif score >= 30:
        band = "Moderate"

    # De-dup and trim recs
    seen, unique_recs = set(), []
    for r in recs:
        if r not in seen:
            unique_recs.append(r)
            seen.add(r)

    # Legacy fields for PDF compatibility
    legacy_flags = [f["title"] for f in flags]

    return {
        "score":        score,
        "band":         band,
        "flags":        legacy_flags,
        "structured":   flags,          # new rich structure (dependency/impact/risk/opportunity)
        "recs":         unique_recs[:10],
    }
