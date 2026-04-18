"""
Financial materiality translator.

The TNFD consultation feedback was explicit: nature must be reported in
"units of nature AND units of currency." This module turns environmental
indicators into a coarse business-bottom-line view that an SME, banker, or
investor can understand at a glance.

Numbers here are deliberately conservative, transparent screening estimates.
They are NOT a replacement for a full financial model; they are an
order-of-magnitude translation that helps the user understand WHY a metric
matters before they invest in deeper analysis.

All assumptions are exposed via :func:`assumptions_table` so that judges and
SMEs can see the reasoning and tune it.
"""
from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Default assumptions (exposed in the UI; user can tune in Settings)
# ---------------------------------------------------------------------------
DEFAULT_ASSUMPTIONS = {
    # General SME baseline
    "annual_revenue_usd":      120_000,   # typical Panuka-tier SME annual turnover
    "gross_margin_pct":        35.0,
    # Sensitivities — % of revenue at risk per unit deterioration
    "yield_loss_per_neg10_rain":      6.0,    # 10% below-baseline rainfall ≈ 6% revenue loss
    "yield_loss_per_3C_above_28":     4.0,    # each +3°C above 28°C land-surface temp
    "yield_loss_per_low_ndvi":        8.0,    # if NDVI < 0.25 in growing area
    "pollination_loss_pct":           18.0,   # share of revenue from pollinator-dependent crops
    "pollination_realised_loss_per_010_bii_drop": 6.0,
    "flood_damage_per_05m":           12.0,   # event-year cost as % of revenue
    "fire_event_cost_pct":            5.0,
    "water_stress_cost_pct":          7.0,
    # Opportunities (negative = upside vs revenue)
    "regen_practice_uplift_pct":      4.0,
    "carbon_credit_per_ha_usd":       12.0,
    "shade_tree_cooling_savings_pct": 1.5,
}


@dataclass
class FinancialLine:
    label: str
    nature_unit: str           # how it's measured in nature
    nature_value: str          # value (formatted)
    business_impact_pct: float # +ve = downside, -ve = upside
    business_impact_usd: float
    rationale: str             # plain-English why


def _safe_float(v) -> float | None:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


def translate_to_currency(metrics: dict, sector: str, assumptions: dict | None = None) -> dict:
    """Translate a metrics bag into a list of financial lines + totals."""
    A = {**DEFAULT_ASSUMPTIONS, **(assumptions or {})}
    revenue = float(A["annual_revenue_usd"])
    lines: list[FinancialLine] = []

    rain = _safe_float(metrics.get("rain_anom_pct"))
    if rain is not None and rain < -5:
        loss_pct = (abs(rain) / 10.0) * A["yield_loss_per_neg10_rain"]
        loss_pct = min(loss_pct, 35)  # cap so screening output stays realistic
        lines.append(FinancialLine(
            "Rainfall shortfall",
            "Rainfall anomaly vs 30-yr baseline",
            f"{rain:.1f}%",
            loss_pct,
            revenue * loss_pct / 100.0,
            f"Each 10% below baseline rainfall reduces revenue by ~{A['yield_loss_per_neg10_rain']:.0f}% in rain-fed agriculture.",
        ))

    lst = _safe_float(metrics.get("lst_mean"))
    if lst is not None and lst > 28:
        steps = (lst - 28) / 3.0
        loss_pct = steps * A["yield_loss_per_3C_above_28"]
        loss_pct = min(loss_pct, 25)
        lines.append(FinancialLine(
            "Heat stress",
            "Mean land-surface temperature",
            f"{lst:.1f} °C",
            loss_pct,
            revenue * loss_pct / 100.0,
            "Plants and animals lose productivity above ~28 °C; greenhouses need extra cooling and ventilation.",
        ))

    ndvi = _safe_float(metrics.get("ndvi_current"))
    if ndvi is not None and ndvi < 0.25:
        loss_pct = A["yield_loss_per_low_ndvi"]
        lines.append(FinancialLine(
            "Weak vegetation cover",
            "NDVI (vegetation health index, 0–1)",
            f"{ndvi:.2f}",
            loss_pct,
            revenue * loss_pct / 100.0,
            "Low NDVI suggests stressed or sparse vegetation in the operating area, which usually translates to lower yields.",
        ))

    bii = _safe_float(metrics.get("bii"))
    if bii is not None and bii < 0.85 and "Agri" in sector:
        gap = max(0.0, 0.85 - bii)
        steps = gap / 0.10
        loss_pct = steps * A["pollination_realised_loss_per_010_bii_drop"]
        lines.append(FinancialLine(
            "Pollinator decline",
            "Biodiversity Intactness Index",
            f"{bii:.2f}",
            loss_pct,
            revenue * loss_pct / 100.0,
            f"About {A['pollination_loss_pct']:.0f}% of typical agribusiness revenue depends on pollinators. Lower local biodiversity reduces pollination services.",
        ))

    flood = _safe_float(metrics.get("flood_risk"))
    if flood is not None and flood >= 0.5:
        loss_pct = A["flood_damage_per_05m"] * (flood / 0.5)
        loss_pct = min(loss_pct, 30)
        lines.append(FinancialLine(
            "Flood exposure",
            "1-in-100yr modelled flood depth",
            f"{flood:.2f} m",
            loss_pct,
            revenue * loss_pct / 100.0,
            "If flooding hits this depth, expected damage to crops, equipment, and access roads is significant.",
        ))

    fire = _safe_float(metrics.get("fire_risk"))
    if fire is not None and fire > 5:
        loss_pct = A["fire_event_cost_pct"]
        lines.append(FinancialLine(
            "Recent fire signal",
            "Burned-area indicator",
            f"{fire:.1f}",
            loss_pct,
            revenue * loss_pct / 100.0,
            "Recent burn signal in the surrounding landscape raises the chance of damage to crops, fences and storage.",
        ))

    water = _safe_float(metrics.get("water_occ"))
    if water is not None and water < 5:
        loss_pct = A["water_stress_cost_pct"]
        lines.append(FinancialLine(
            "Water-availability stress",
            "Visible surface-water occurrence (%)",
            f"{water:.1f}%",
            loss_pct,
            revenue * loss_pct / 100.0,
            "Limited surface water raises pumping costs, increases reliance on boreholes, and lowers reliability.",
        ))

    # Opportunities (upside)
    if (ndvi is not None and ndvi >= 0.45) or (rain is not None and rain >= 0):
        gain_pct = -A["regen_practice_uplift_pct"]
        lines.append(FinancialLine(
            "Regenerative-practice upside",
            "Stable vegetation + adequate rainfall",
            "Stable",
            gain_pct,
            revenue * gain_pct / 100.0,
            "Conditions support cover crops, agroforestry and soil-building practices that lift yields and lower input costs.",
        ))
    tree_pct = _safe_float(metrics.get("tree_pct"))
    if tree_pct is not None and tree_pct > 5:
        gain_pct = -A["shade_tree_cooling_savings_pct"]
        lines.append(FinancialLine(
            "Shade & cooling benefit",
            "Tree-cover share of site",
            f"{tree_pct:.1f}%",
            gain_pct,
            revenue * gain_pct / 100.0,
            "Existing tree cover already cools the site and supports beneficial wildlife, modestly lifting margins.",
        ))

    # Carbon-credit potential (extremely conservative)
    if tree_pct and tree_pct > 10:
        ha_potential = max(1.0, tree_pct / 10.0)  # rough ha-equivalent of additional planting
        annual_credit = ha_potential * A["carbon_credit_per_ha_usd"]
        gain_pct = -(annual_credit / revenue * 100.0)
        lines.append(FinancialLine(
            "Carbon-credit potential",
            "Eligible canopy / restoration ha (proxy)",
            f"~{ha_potential:.1f} ha",
            gain_pct,
            -annual_credit,
            f"Site has space for tree-cover expansion. At ${A['carbon_credit_per_ha_usd']}/ha/year, this is potential carbon-credit revenue.",
        ))

    # Aggregate
    downside_usd = sum(l.business_impact_usd for l in lines if l.business_impact_usd > 0)
    upside_usd   = -sum(l.business_impact_usd for l in lines if l.business_impact_usd < 0)
    net_usd      = downside_usd - upside_usd

    return {
        "revenue_usd":   revenue,
        "lines":         [l.__dict__ for l in lines],
        "downside_usd":  downside_usd,
        "upside_usd":    upside_usd,
        "net_usd":       net_usd,
        "downside_pct":  downside_usd / revenue * 100 if revenue else 0,
        "upside_pct":    upside_usd / revenue * 100 if revenue else 0,
        "assumptions":   A,
    }


def assumptions_table(assumptions: dict | None = None) -> list[dict]:
    """Return the assumption pack as a list of {key, value, plain} rows for the UI."""
    A = {**DEFAULT_ASSUMPTIONS, **(assumptions or {})}
    descriptions = {
        "annual_revenue_usd":           "Assumed annual revenue for the SME (USD).",
        "gross_margin_pct":             "Assumed gross margin (%).",
        "yield_loss_per_neg10_rain":    "% of revenue lost per 10% below-baseline rainfall.",
        "yield_loss_per_3C_above_28":   "% of revenue lost per 3°C above 28°C land surface temperature.",
        "yield_loss_per_low_ndvi":      "% of revenue lost when site NDVI is below 0.25.",
        "pollination_loss_pct":         "Share of revenue from crops dependent on pollinators.",
        "pollination_realised_loss_per_010_bii_drop":
                                         "% of revenue lost per 0.10 drop in BII (pollination proxy).",
        "flood_damage_per_05m":         "% of revenue lost per 0.5 m of modelled 1-in-100yr flood depth.",
        "fire_event_cost_pct":          "% of revenue lost in years with detected burn signal.",
        "water_stress_cost_pct":        "% of revenue lost when surface-water occurrence is low.",
        "regen_practice_uplift_pct":    "% revenue uplift from regenerative practices when conditions allow.",
        "carbon_credit_per_ha_usd":     "USD per hectare per year of carbon-credit potential.",
        "shade_tree_cooling_savings_pct":
                                         "% revenue saved from shade & cooling provided by existing tree cover.",
    }
    rows = []
    for k, v in A.items():
        rows.append({
            "key": k,
            "value": v,
            "plain": descriptions.get(k, "Assumption used by the financial-translation engine."),
        })
    return rows
