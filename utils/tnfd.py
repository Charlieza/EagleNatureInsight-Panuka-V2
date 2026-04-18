"""
TNFD (Taskforce on Nature-related Financial Disclosures) framework module.

This module encodes:
  1. The LEAP workflow (Locate → Evaluate → Assess → Prepare).
  2. The TNFD dependency & impact matrix at the sector level (TNFD 2023 Annex).
  3. The Nature Positive Initiative state-of-nature metrics
     (https://www.naturepositive.org/metrics/), including ecosystem extent,
     ecosystem condition (intactness), and species population trends.
  4. Plain-English explanations for non-expert SME users.

Sources cross-referenced with the materials in this repo:
  - "Recommendations of the Taskforce on Nature-related Financial Disclosures" (Sept 2023)
  - "Draft State of Nature Metrics for Piloting" (Nature Positive Initiative, Jan 2025)
  - "Supporting Information — State of Nature Metrics" (Oct 2024)
  - The Panuka SME consultation notes.

Everything in this file is deliberately readable: judges and SMEs should be able to
open it and understand what we're claiming, without specialist help.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

# ---------------------------------------------------------------------------
# LEAP workflow
# ---------------------------------------------------------------------------
LEAP_PHASES = [
    {
        "letter": "L",
        "name": "Locate",
        "headline": "Pin your site on the map",
        "plain": (
            "Tell us where your business operates so we can pull the right environmental "
            "data. You can pick a Panuka pilot site, drop a pin, or upload a farm boundary."
        ),
        "tnfd_questions": [
            "Where does the organisation operate?",
            "Are operations in or near sensitive locations (e.g., protected areas)?",
        ],
    },
    {
        "letter": "E",
        "name": "Evaluate",
        "headline": "Understand what nature gives you, and how you affect it",
        "plain": (
            "We translate satellite indicators into a short story about your "
            "dependencies (what you need from nature) and impacts (what you change about it)."
        ),
        "tnfd_questions": [
            "Which ecosystem services does the business depend on?",
            "What pressures does the business place on nature (land use, water, GHGs, pollution, invasives)?",
        ],
    },
    {
        "letter": "A",
        "name": "Assess",
        "headline": "Translate signals into business risk and opportunity",
        "plain": (
            "We score the size of physical, transition, and reputational risks — and where "
            "nature could be a competitive advantage — in plain English and dollar terms."
        ),
        "tnfd_questions": [
            "How material are nature-related risks and opportunities to revenue, costs, and capital?",
        ],
    },
    {
        "letter": "P",
        "name": "Prepare",
        "headline": "Create a report a banker, funder, or auditor can read",
        "plain": (
            "We produce a one-click PDF and Excel pack you can attach to a loan application, "
            "an investor update, or a sustainability disclosure."
        ),
        "tnfd_questions": [
            "How will the organisation respond, monitor, and disclose nature-related issues?",
        ],
    },
]


# ---------------------------------------------------------------------------
# TNFD ecosystem-service dependency map (sector → ecosystem services)
# ---------------------------------------------------------------------------
# Modelled on the TNFD additional sector guidance / ENCORE mapping.
# Each entry is a "high / medium / low" qualitative dependency, paired with a plain
# explanation a non-expert can read out loud.

@dataclass
class DependencyRow:
    service: str            # ecosystem service name
    rating: str             # 'High' | 'Medium' | 'Low' | 'Variable'
    why: str                # plain-English explanation
    nature_unit: str        # how it's measured in nature (e.g. mm of rainfall, BII score)


SECTOR_DEPENDENCIES: dict[str, list[DependencyRow]] = {
    "Agriculture / Agribusiness": [
        DependencyRow("Surface & ground water",        "High",
                      "Crops need reliable water from rivers, rain, or boreholes. Less water means lower yields and higher pumping costs.",
                      "Cubic metres / year"),
        DependencyRow("Pollination",                   "High",
                      "Bees, birds and other pollinators move pollen between flowers. Many fruit and vegetable crops will not set fruit without them.",
                      "% of pollinator-dependent crops × pollinator availability index"),
        DependencyRow("Soil quality & nutrient cycling","High",
                      "Healthy soils hold water and feed plants. Degraded soil means more fertiliser, more irrigation, and lower yields.",
                      "Soil organic carbon (% of mass)"),
        DependencyRow("Climate regulation",            "High",
                      "Trees, wetlands and the wider landscape buffer extreme heat and rainfall. Without that buffer, crop loss spikes in bad years.",
                      "Land surface temperature (°C)"),
        DependencyRow("Pest & disease control",        "High",
                      "Birds, insects and biodiversity around the farm naturally suppress pests. Plant ticks and other outbreaks rise when biodiversity drops.",
                      "Biodiversity Intactness Index (0–1)"),
        DependencyRow("Flood & storm protection",      "Medium",
                      "Vegetated buffers and intact catchments reduce flood damage to crops, roads, and storage.",
                      "1-in-100yr flood depth (m)"),
        DependencyRow("Genetic resources",             "Medium",
                      "Wild and cultivated diversity gives breeders the genes needed to develop drought- and heat-tolerant varieties.",
                      "Number of wild relatives within 50km"),
    ],
    "Food processing / Supply chain": [
        DependencyRow("Surface & ground water", "High",
                      "Processing uses water for cleaning, cooling, and product. Water shortages stop the line.",
                      "Cubic metres / year"),
        DependencyRow("Climate regulation",     "Medium",
                      "Heat events disrupt cold chain and worker safety; cooling costs scale with outdoor temperature.",
                      "Land surface temperature (°C)"),
        DependencyRow("Supplier-side ecosystem services", "High",
                      "Your raw materials sit downstream of farmers' dependencies. Anything that hits supplier farms eventually reaches your factory.",
                      "Supplier-area BII × dependency weight"),
    ],
    "Manufacturing / Industrial": [
        DependencyRow("Surface & ground water",  "High",
                      "Cooling, cleaning, and process water are critical to most manufacturing.",
                      "Cubic metres / year"),
        DependencyRow("Climate regulation",      "Medium",
                      "Heat events affect equipment efficiency and worker safety.",
                      "Land surface temperature (°C)"),
        DependencyRow("Air quality regulation",  "Low",
                      "Vegetation and clean air around the site reduce filtration and health costs.",
                      "PM2.5 (µg/m³)"),
    ],
    "Property / Built environment": [
        DependencyRow("Climate regulation", "High",
                      "Trees and green cover keep buildings cooler, reducing AC bills and improving liveability.",
                      "Land surface temperature (°C)"),
        DependencyRow("Flood & storm protection", "High",
                      "Permeable surfaces and intact catchments reduce flood damage to assets.",
                      "1-in-100yr flood depth (m)"),
        DependencyRow("Pollination", "Low",
                      "Mostly indirect; matters where landscaping or rooftop gardens contribute amenity value.",
                      "Pollinator habitat area"),
    ],
    "Energy / Infrastructure": [
        DependencyRow("Surface & ground water", "High",
                      "Hydro and thermal generation depend on reliable water; transmission corridors depend on stable vegetation.",
                      "Cubic metres / year"),
        DependencyRow("Climate regulation",     "High",
                      "Equipment ratings derate in extreme heat; storms damage transmission.",
                      "Land surface temperature (°C)"),
        DependencyRow("Habitat / biodiversity", "Medium",
                      "Project siting near sensitive habitat creates permitting and community risk.",
                      "% area inside KBA / WDPA"),
    ],
    "Water / Circular economy": [
        DependencyRow("Surface & ground water", "High",
                      "The whole business sits on water availability and quality.",
                      "Cubic metres / year"),
        DependencyRow("Soil & sediment retention", "Medium",
                      "Erosion upstream raises treatment costs; healthy catchments lower them.",
                      "Soil organic carbon, vegetation cover"),
    ],
}


SECTOR_IMPACTS: dict[str, list[DependencyRow]] = {
    "Agriculture / Agribusiness": [
        DependencyRow("Land-use change", "High",
                      "Clearing or converting land changes habitat and carbon stocks.",
                      "Hectares converted / year"),
        DependencyRow("Water withdrawal", "High",
                      "Irrigation can deplete rivers and aquifers if not planned.",
                      "m³ withdrawn / year"),
        DependencyRow("Nutrient runoff", "Medium",
                      "Excess fertiliser flows into waterways and damages downstream ecosystems.",
                      "kg N, P / ha / year"),
        DependencyRow("Pesticide load", "Medium",
                      "Pesticides reduce pollinators and soil life if over-applied.",
                      "kg active ingredient / ha / year"),
        DependencyRow("GHG emissions", "Medium",
                      "Soil disturbance and livestock release CO₂, N₂O, and methane.",
                      "tCO₂e / year"),
    ],
    "Food processing / Supply chain": [
        DependencyRow("Wastewater / effluent", "High",
                      "Process water released untreated harms downstream rivers.",
                      "m³, BOD load"),
        DependencyRow("Solid waste", "Medium",
                      "Organic waste streams can pollute or be turned into fertiliser.",
                      "tonnes / year"),
        DependencyRow("Embedded supply-chain impacts", "High",
                      "The biggest impact is usually upstream on supplier farms.",
                      "% sourced from impacted landscapes"),
    ],
    "Manufacturing / Industrial": [
        DependencyRow("Air pollution", "Medium",
                      "Local emissions affect nearby ecosystems and human health.",
                      "PM2.5, NOx (µg/m³)"),
        DependencyRow("Land sealing", "Medium",
                      "Built footprint reduces infiltration and habitat.",
                      "% built area"),
        DependencyRow("Wastewater", "Medium",
                      "Industrial effluent loads on local waterways.",
                      "m³ / year"),
    ],
    "Property / Built environment": [
        DependencyRow("Land sealing", "High",
                      "Hard surfaces reduce infiltration and biodiversity.",
                      "% built area"),
        DependencyRow("Heat island effect", "Medium",
                      "Built-up areas intensify local heat.",
                      "Land surface temperature delta (°C)"),
    ],
    "Energy / Infrastructure": [
        DependencyRow("Habitat fragmentation", "High",
                      "Linear infrastructure cuts through habitat and migration routes.",
                      "Length crossing KBAs (km)"),
        DependencyRow("GHG emissions", "Variable",
                      "Depends on the energy source.",
                      "tCO₂e / MWh"),
    ],
    "Water / Circular economy": [
        DependencyRow("Water abstraction", "High",
                      "Removing water from rivers and aquifers can stress ecosystems.",
                      "m³ / year"),
    ],
}


# ---------------------------------------------------------------------------
# Nature Positive state-of-nature metrics
# ---------------------------------------------------------------------------
# Source: Nature Positive Initiative — Draft State of Nature Metrics for Piloting (Jan 2025)
# Three pillars: ecosystem extent, ecosystem condition, and species populations.

NATURE_POSITIVE_METRICS = [
    {
        "pillar": "Ecosystem extent",
        "headline": "How much natural and semi-natural ecosystem is present",
        "indicator": "Natural habitat area (ha)",
        "source_layer": "ESA WorldCover 2021 + Hansen Forest Loss",
        "plain": "We measure the area of natural land cover (forests, wetlands, grasslands) and how that area has changed since 2017.",
    },
    {
        "pillar": "Ecosystem condition",
        "headline": "How healthy that ecosystem is",
        "indicator": "Biodiversity Intactness Index (BII, 0–1)",
        "source_layer": "PREDICTS / NHM BII 2020",
        "plain": "BII estimates how much of the original biodiversity remains, where 1.0 means fully intact and 0 means heavily degraded.",
    },
    {
        "pillar": "Ecosystem condition",
        "headline": "Forest landscape integrity",
        "indicator": "Forest Landscape Integrity Index (FLII, 0–10)",
        "source_layer": "Grantham et al. 2020",
        "plain": "Higher numbers mean more intact, less disturbed forest in the surrounding area.",
    },
    {
        "pillar": "Species populations",
        "headline": "Are threatened species likely to be in the area",
        "indicator": "Threatened species count (IUCN Red List, range overlap)",
        "source_layer": "IUCN Red List ranges via GBIF",
        "plain": "Count of species classified as Vulnerable, Endangered or Critically Endangered whose range overlaps the area.",
    },
    {
        "pillar": "Sensitive locations",
        "headline": "Distance to a Key Biodiversity Area or Protected Area",
        "indicator": "Distance to nearest KBA / WDPA polygon (km)",
        "source_layer": "WDPA April 2025 + KBA Partnership",
        "plain": "Operations close to KBAs / Protected Areas attract more scrutiny from regulators, banks and communities.",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def matrix_for_sector(sector: str) -> dict[str, list[DependencyRow]]:
    """Return both dependency and impact rows for a sector, with a sensible default."""
    deps = SECTOR_DEPENDENCIES.get(sector, SECTOR_DEPENDENCIES["Agriculture / Agribusiness"])
    impacts = SECTOR_IMPACTS.get(sector, SECTOR_IMPACTS["Agriculture / Agribusiness"])
    return {"dependencies": deps, "impacts": impacts}


def leap_phase(letter: str) -> dict:
    for p in LEAP_PHASES:
        if p["letter"].lower() == letter.lower():
            return p
    return LEAP_PHASES[0]


def all_leap_letters() -> list[str]:
    return [p["letter"] for p in LEAP_PHASES]
