"""
Demo / offline-mode data.

When Google Earth Engine credentials are not available (judges, low-bandwidth SMEs,
or air-gapped pilots), the app falls back to these cached values so the entire
LEAP workflow can be demonstrated end-to-end without internet.

Numbers are realistic for the Panuka pilot context (Chongwe District, ~25km east
of Lusaka, Zambia) and were calibrated against published studies of the area.

Source notes for each value live in utils.datasets so users can audit them.
"""
from __future__ import annotations

import pandas as pd

PANUKA_SITES = {
    "Panuka Site 1 — Open-field (citrus, banana, mango)": {
        "lat": -15.251194, "lon": 28.144500, "buffer_m": 1200, "zoom": 15,
        "category": "Agriculture / Agribusiness",
    },
    "Panuka Site 2 — Protected farming (greenhouses)": {
        "lat": -15.251472, "lon": 28.147417, "buffer_m": 1200, "zoom": 15,
        "category": "Agriculture / Agribusiness",
    },
    "Demo SME — Lusaka peri-urban food processor": {
        "lat": -15.4067, "lon": 28.2871, "buffer_m": 800, "zoom": 14,
        "category": "Food processing / Supply chain",
    },
    "Demo SME — Manufacturing site (Kafue)": {
        "lat": -15.7706, "lon": 28.1789, "buffer_m": 1500, "zoom": 14,
        "category": "Manufacturing / Industrial",
    },
}


# ---------------------------------------------------------------------------
# Pre-cached metric snapshots
# ---------------------------------------------------------------------------
DEMO_METRICS = {
    "Panuka Site 1 — Open-field (citrus, banana, mango)": {
        "ndvi_current":   0.41,
        "ndvi_trend":    -0.018,
        "rain_anom_pct": -12.4,
        "lst_mean":       30.6,
        "soil_moisture":  0.16,
        "evapotranspiration": 22.0,
        "water_occ":      6.4,
        "flood_risk":     0.22,
        "fire_risk":      3.1,
        "tree_pct":       12.0,
        "built_pct":      4.5,
        "forest_loss_pct": 2.3,
        "greenhouse_pct": 0.4,
        "greenhouse_pest_risk": 56,
        "travel_time_to_market": 75,
        "bii":            0.78,
        "flii":           5.6,
        "kba_distance_km": 22.0,
        "wdpa_distance_km": 18.0,
        "threatened_species_count": 4,
        "pollinator_suitability": 0.62,
        "aqueduct_stress": 3,
        "soc_pct":        1.8,
        "bio_proxy":      6.0,
    },
    "Panuka Site 2 — Protected farming (greenhouses)": {
        "ndvi_current":   0.38,
        "ndvi_trend":    -0.022,
        "rain_anom_pct": -12.4,
        "lst_mean":       31.2,
        "soil_moisture":  0.14,
        "evapotranspiration": 24.0,
        "water_occ":      4.9,
        "flood_risk":     0.18,
        "fire_risk":      2.6,
        "tree_pct":        9.0,
        "built_pct":      11.0,
        "forest_loss_pct": 1.9,
        "greenhouse_pct":  4.7,
        "greenhouse_pest_risk": 71,
        "travel_time_to_market": 75,
        "bii":            0.76,
        "flii":           5.4,
        "kba_distance_km": 22.0,
        "wdpa_distance_km": 18.0,
        "threatened_species_count": 4,
        "pollinator_suitability": 0.58,
        "aqueduct_stress": 3,
        "soc_pct":        1.7,
        "bio_proxy":      5.2,
    },
    "Demo SME — Lusaka peri-urban food processor": {
        "ndvi_current":   0.22,
        "ndvi_trend":    -0.012,
        "rain_anom_pct": -8.0,
        "lst_mean":       32.4,
        "soil_moisture":  0.10,
        "evapotranspiration": 26.0,
        "water_occ":      2.1,
        "flood_risk":     0.05,
        "fire_risk":      0.8,
        "tree_pct":        3.0,
        "built_pct":      62.0,
        "forest_loss_pct": 0.5,
        "greenhouse_pct":  0.0,
        "travel_time_to_market": 25,
        "bii":            0.51,
        "flii":           2.1,
        "kba_distance_km": 65.0,
        "wdpa_distance_km": 40.0,
        "threatened_species_count": 1,
        "pollinator_suitability": 0.21,
        "aqueduct_stress": 4,
        "soc_pct":        0.9,
        "bio_proxy":      1.5,
    },
    "Demo SME — Manufacturing site (Kafue)": {
        "ndvi_current":   0.32,
        "ndvi_trend":    -0.005,
        "rain_anom_pct": -3.0,
        "lst_mean":       29.8,
        "soil_moisture":  0.18,
        "evapotranspiration": 19.0,
        "water_occ":     12.5,
        "flood_risk":     0.65,
        "fire_risk":      1.2,
        "tree_pct":       18.0,
        "built_pct":      28.0,
        "forest_loss_pct": 1.1,
        "greenhouse_pct":  0.0,
        "travel_time_to_market": 95,
        "bii":            0.69,
        "flii":           4.3,
        "kba_distance_km": 9.0,
        "wdpa_distance_km": 4.0,
        "threatened_species_count": 7,
        "pollinator_suitability": 0.44,
        "aqueduct_stress": 3,
        "soc_pct":        1.4,
        "bio_proxy":      4.1,
    },
}


# ---------------------------------------------------------------------------
# Time-series for trend charts (synthetic but plausible)
# ---------------------------------------------------------------------------
def demo_ndvi_series(site_key: str) -> pd.DataFrame:
    base = DEMO_METRICS[site_key]["ndvi_current"]
    trend = DEMO_METRICS[site_key]["ndvi_trend"]
    years = list(range(2015, 2026))
    vals = []
    for i, y in enumerate(years):
        offset = (len(years) - 1 - i) * trend  # earlier years had higher NDVI
        wobble = 0.02 * ((i % 3) - 1)
        vals.append(round(base + offset + wobble, 3))
    return pd.DataFrame({"year": years, "value": vals})


def demo_rain_series(site_key: str) -> pd.DataFrame:
    anom = DEMO_METRICS[site_key]["rain_anom_pct"]
    years = list(range(2015, 2026))
    base = 800
    vals = []
    for i, y in enumerate(years):
        v = base * (1 + (anom / 100) * (i / len(years))) + (-30 if y % 2 == 0 else 25)
        vals.append(round(v, 1))
    return pd.DataFrame({"year": years, "value": vals})


def demo_lst_series(site_key: str) -> pd.DataFrame:
    base = DEMO_METRICS[site_key]["lst_mean"]
    years = list(range(2015, 2026))
    vals = [round(base - 0.05 * (len(years) - 1 - i) + ((i % 3) * 0.1), 2) for i, y in enumerate(years)]
    return pd.DataFrame({"year": years, "value": vals})


def demo_landcover(site_key: str) -> pd.DataFrame:
    """Return a coarse land-cover composition table for the area."""
    m = DEMO_METRICS[site_key]
    rows = [
        {"class_name": "Cropland",        "area_ha": round((100 - m["tree_pct"] - m["built_pct"]) * 1.4, 1)},
        {"class_name": "Tree cover",      "area_ha": round(m["tree_pct"] * 1.4, 1)},
        {"class_name": "Built-up",        "area_ha": round(m["built_pct"] * 1.4, 1)},
        {"class_name": "Bare / sparse",   "area_ha": round(8 + m["forest_loss_pct"] * 0.6, 1)},
        {"class_name": "Permanent water", "area_ha": round(m["water_occ"] * 0.4, 1)},
    ]
    return pd.DataFrame(rows)
