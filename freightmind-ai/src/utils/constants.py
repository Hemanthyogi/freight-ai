"""
FreightMind AI — Application Constants
src/utils/constants.py

Central source of truth for all static mappings.
Do NOT embed domain constants directly in business logic.
"""

# ── Vessel types ────────────────────────────────────────────────────────────
VESSEL_TYPES = ["Handysize", "Supramax", "Panamax", "Capesize"]

# ── East Coast India destination ports (IDs matching ports_vessels.yaml) ───
EAST_COAST_PORTS = [
    "paradip",
    "visakhapatnam",
    "gangavaram",
    "gopalpur",
    "dhamra",
    "sagar_sandheads",
    "haldia",
]

# ── Overseas origin ports ───────────────────────────────────────────────────
ORIGIN_PORTS = [
    "newcastle_au",
    "hay_point_au",
    "port_hedland_au",
    "dampier_au",
    "south_africa_rbct",
    "indonesia_balikpapan",
]

# ── Cargo types supported ───────────────────────────────────────────────────
CARGO_TYPES = [
    "coal",
    "iron_ore",
    "fertilizer",
    "grain",
    "limestone",
    "chrome_ore",
    "general_bulk",
]

# ── Route IDs (matching ports_vessels.yaml) ─────────────────────────────────
ROUTE_IDS = [
    "AU_COAL_PARADIP",
    "AU_COAL_VIZAG",
    "AU_ORE_GANGAVARAM",
    "ID_COAL_PARADIP",
    "ZA_COAL_VIZAG",
]

# ── Risk levels ─────────────────────────────────────────────────────────────
RISK_LOW_THRESHOLD = 33        # score 0-33  → LOW
RISK_MEDIUM_THRESHOLD = 66     # score 34-66 → MEDIUM
                               # score 67+   → HIGH

RISK_LABELS = {
    "low": "🟢 Low",
    "medium": "🟡 Medium",
    "high": "🔴 High",
}

# ── Market entry signals ─────────────────────────────────────────────────────
MARKET_ENTRY_FAVORABLE = "🟢 Favorable"
MARKET_ENTRY_NEUTRAL   = "🟡 Neutral"
MARKET_ENTRY_UNFAVORABLE = "🔴 Unfavorable"

# ── Contract strategy types ──────────────────────────────────────────────────
CONTRACT_SPOT = "spot"
CONTRACT_SHORT_TERM = "short_term"   # ~3 months
CONTRACT_MEDIUM_TERM = "medium_term" # ~6 months

# ── Forecast horizons (days) ─────────────────────────────────────────────────
FORECAST_HORIZONS = [7, 14, 30, 60, 90]

# ── Data source labels ───────────────────────────────────────────────────────
DATA_SOURCE_REAL = "REAL_DATA"
DATA_SOURCE_DEMO = "DEMO_DATA"          # Clearly labelled synthetic data
DATA_SOURCE_ESTIMATED = "ESTIMATED"     # Best-guess from secondary sources

# ── Seasonal definitions ─────────────────────────────────────────────────────
SEASON_MAP = {
    12: "winter", 1: "winter", 2: "winter",
    3: "spring",  4: "spring", 5: "spring",
    6: "summer",  7: "summer", 8: "summer",
    9: "autumn", 10: "autumn", 11: "autumn",
}

QUARTER_MAP = {
    1: "Q1", 2: "Q1", 3: "Q1",
    4: "Q2", 5: "Q2", 6: "Q2",
    7: "Q3", 8: "Q3", 9: "Q3",
    10: "Q4", 11: "Q4", 12: "Q4",
}

# Indian monsoon season (affects port operations)
MONSOON_MONTHS = [6, 7, 8, 9]

# ── Freight rate reference ranges (USD/MT) — for sanity checks ──────────────
# Based on approximate historical BDI-derived ranges; not official data
FREIGHT_RATE_RANGES = {
    "Handysize":  {"min": 8.0,  "max": 45.0,  "typical": 18.0},
    "Supramax":   {"min": 8.0,  "max": 42.0,  "typical": 16.0},
    "Panamax":    {"min": 6.0,  "max": 40.0,  "typical": 14.0},
    "Capesize":   {"min": 4.0,  "max": 35.0,  "typical": 12.0},
}

# ── Model evaluation metrics ─────────────────────────────────────────────────
EVAL_METRICS = ["MAE", "RMSE", "MAPE", "R2"]
