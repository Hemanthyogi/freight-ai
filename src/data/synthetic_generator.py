"""
FreightMind AI — Reproducible Synthetic Data Generator
src/data/synthetic_generator.py

⚠️  ALL DATA PRODUCED BY THIS MODULE IS DEMO/SYNTHETIC DATA.
    It is NOT official market data, NOT Baltic Exchange data,
    and NOT actual historical freight rates.

    It is statistically calibrated to resemble real bulk freight
    market behaviour for DEMONSTRATION PURPOSES ONLY.

    The system is designed so that real data can replace these
    synthetic files with zero code changes.

Purpose:
    Generate realistic-looking but clearly-labelled synthetic datasets
    for:
        1. freight_rates.csv        — historical route freight rates
        2. commodity_prices.csv     — coal/iron ore/fertilizer prices
        3. market_indicators.csv    — BDI proxy, bunker fuel, USD/INR
        4. port_congestion.csv      — daily congestion level per port
        5. vessels_master.csv       — vessel fleet master data

Usage:
    python src/data/synthetic_generator.py
    # or from project root:
    python -m src.data.synthetic_generator

Output:
    data/synthetic/*.csv  (+ data/synthetic/README.txt)
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

# ── Reproducibility ───────────────────────────────────────────────────────────
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# ── Output directory ──────────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_DIR = _PROJECT_ROOT / "data" / "synthetic"

# ── Date range ────────────────────────────────────────────────────────────────
START_DATE = "2020-01-01"
END_DATE   = "2026-09-14"   # Yesterday (demo end date)


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

def _make_date_range(start: str = START_DATE, end: str = END_DATE) -> pd.DatetimeIndex:
    return pd.date_range(start=start, end=end, freq="D")


def _add_demo_label(df: pd.DataFrame) -> pd.DataFrame:
    """Stamp every row so downstream code knows this is synthetic."""
    df["data_source"] = "DEMO_DATA"
    df["is_synthetic"] = True
    return df


def _garch_like_series(
    n: int,
    base: float,
    vol: float,
    mean_revert: float = 0.03,
    shock_prob: float = 0.03,
    shock_magnitude: float = 0.15,
    seed: int = RANDOM_SEED,
) -> np.ndarray:
    """
    Generate a mean-reverting series with occasional shocks.
    Mimics bulk freight market behaviour: volatile with trend.

    This is a simplified AR(1)-GARCH-lite process for demo purposes.

    Args:
        n:               Number of data points.
        base:            Long-run mean value.
        vol:             Daily volatility (fraction of value).
        mean_revert:     Strength of mean reversion (0-1).
        shock_prob:      Probability of a large shock each day.
        shock_magnitude: Size of shock (fraction of value).
        seed:            Random seed for reproducibility.
    """
    rng = np.random.default_rng(seed)
    values = np.zeros(n)
    values[0] = base * rng.uniform(0.8, 1.2)

    for i in range(1, n):
        # Mean reversion pull
        reversion = mean_revert * (base - values[i - 1])
        # Daily noise
        noise = values[i - 1] * vol * rng.standard_normal()
        # Occasional shock
        shock = 0.0
        if rng.random() < shock_prob:
            direction = rng.choice([-1, 1])
            shock = direction * values[i - 1] * shock_magnitude * rng.uniform(0.5, 1.5)

        values[i] = max(values[i - 1] + reversion + noise + shock, base * 0.3)

    return values


def _seasonal_multiplier(months: pd.Series) -> np.ndarray:
    """
    Apply a seasonal pattern roughly matching East-Coast India bulk trade.
    Q1 (Jan-Mar): slightly elevated (post-monsoon restocking)
    Q2 (Apr-Jun): moderate
    Q3 (Jul-Sep): typically depressed (monsoon disruption)
    Q4 (Oct-Dec): elevated (pre-winter demand from steel/power plants)
    """
    m = months.values
    mult = np.where(np.isin(m, [1, 2, 3]),   1.08,
           np.where(np.isin(m, [4, 5, 6]),   1.02,
           np.where(np.isin(m, [7, 8, 9]),   0.93,
                                              1.06)))
    return mult


# ─────────────────────────────────────────────────────────────────────────────
# 1. Freight Rates
# ─────────────────────────────────────────────────────────────────────────────

ROUTE_CONFIGS = {
    "AU_COAL_PARADIP": {
        "origin": "Australia",
        "destination": "paradip",
        "cargo": "coal",
        "vessel_types": ["Panamax", "Capesize", "Supramax"],
        "base_rates": {"Panamax": 14.0, "Capesize": 11.5, "Supramax": 16.5},
        "distance_nm": 4800,
    },
    "AU_COAL_VIZAG": {
        "origin": "Australia",
        "destination": "visakhapatnam",
        "cargo": "coal",
        "vessel_types": ["Panamax", "Supramax"],
        "base_rates": {"Panamax": 13.5, "Supramax": 16.0},
        "distance_nm": 4700,
    },
    "AU_ORE_GANGAVARAM": {
        "origin": "Australia",
        "destination": "gangavaram",
        "cargo": "iron_ore",
        "vessel_types": ["Capesize", "Panamax"],
        "base_rates": {"Capesize": 10.0, "Panamax": 13.0},
        "distance_nm": 4500,
    },
    "ID_COAL_PARADIP": {
        "origin": "Indonesia",
        "destination": "paradip",
        "cargo": "coal",
        "vessel_types": ["Supramax", "Panamax", "Handysize"],
        "base_rates": {"Supramax": 10.5, "Panamax": 9.0, "Handysize": 13.5},
        "distance_nm": 2800,
    },
    "ZA_COAL_VIZAG": {
        "origin": "South Africa",
        "destination": "visakhapatnam",
        "cargo": "coal",
        "vessel_types": ["Panamax", "Supramax"],
        "base_rates": {"Panamax": 15.0, "Supramax": 17.5},
        "distance_nm": 4200,
    },
}


def generate_freight_rates() -> pd.DataFrame:
    """
    Generate daily freight rate records (USD/MT) for each route × vessel type.

    ⚠️ SYNTHETIC DATA — for demonstration only.
    """
    dates = _make_date_range()
    n = len(dates)
    df_month = pd.Series(dates.month)
    seasonal = _seasonal_multiplier(df_month)

    records = []
    seed_offset = 0

    for route_id, cfg in ROUTE_CONFIGS.items():
        for vessel_type in cfg["vessel_types"]:
            base = cfg["base_rates"][vessel_type]

            # Generate raw series
            raw = _garch_like_series(
                n=n,
                base=base,
                vol=0.012,           # ~1.2% daily vol
                mean_revert=0.025,
                shock_prob=0.03,
                shock_magnitude=0.12,
                seed=RANDOM_SEED + seed_offset,
            )
            seed_offset += 1

            # Apply seasonal pattern
            rates = raw * seasonal

            # Add COVID-era shock (2020 Q1): sharp drop
            covid_mask = (dates >= "2020-03-01") & (dates <= "2020-06-30")
            rates[covid_mask] *= np.linspace(0.70, 0.85, covid_mask.sum())

            # Add post-COVID rebound (2021): spike
            rebound_mask = (dates >= "2021-01-01") & (dates <= "2021-12-31")
            rates[rebound_mask] *= np.linspace(1.0, 1.45, rebound_mask.sum())

            # Weekly pattern: slightly lower on weekends (less activity)
            weekday = np.array([d.weekday() for d in dates])
            weekend_factor = np.where(weekday >= 5, 0.98, 1.0)
            rates = rates * weekend_factor

            for i, date in enumerate(dates):
                records.append({
                    "date": date.date(),
                    "route_id": route_id,
                    "origin": cfg["origin"],
                    "destination": cfg["destination"],
                    "cargo_type": cfg["cargo"],
                    "vessel_type": vessel_type,
                    "freight_rate_usd_mt": round(float(rates[i]), 2),
                    "distance_nm": cfg["distance_nm"],
                })

    df = pd.DataFrame(records)
    df = _add_demo_label(df)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. Commodity Prices
# ─────────────────────────────────────────────────────────────────────────────

def generate_commodity_prices() -> pd.DataFrame:
    """
    Generate daily commodity prices.

    ⚠️ SYNTHETIC DATA — calibrated to approximate World Bank Pink Sheet
       magnitude ranges, but NOT actual historical prices.
    """
    dates = _make_date_range()
    n = len(dates)

    commodity_configs = {
        "thermal_coal_usd_mt":   {"base": 85.0,  "vol": 0.015, "shock_prob": 0.025},
        "iron_ore_usd_mt":       {"base": 110.0, "vol": 0.018, "shock_prob": 0.03},
        "coking_coal_usd_mt":    {"base": 200.0, "vol": 0.016, "shock_prob": 0.03},
        "fertilizer_usd_mt":     {"base": 330.0, "vol": 0.010, "shock_prob": 0.02},
        "crude_oil_usd_bbl":     {"base": 75.0,  "vol": 0.020, "shock_prob": 0.04},
    }

    df_dict: dict[str, list] = {"date": list(dates.date)}

    for col, cfg in commodity_configs.items():
        series = _garch_like_series(
            n=n,
            base=cfg["base"],
            vol=cfg["vol"],
            shock_prob=cfg["shock_prob"],
            seed=RANDOM_SEED + hash(col) % 1000,
        )
        # COVID crash in oil (2020 Apr-May)
        if "crude_oil" in col:
            crash = (dates >= "2020-04-01") & (dates <= "2020-05-31")
            series[crash] *= np.linspace(0.35, 0.60, crash.sum())
        df_dict[col] = [round(v, 2) for v in series]

    df = pd.DataFrame(df_dict)
    df = _add_demo_label(df)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 3. Market Indicators
# ─────────────────────────────────────────────────────────────────────────────

def generate_market_indicators() -> pd.DataFrame:
    """
    Generate market indicator series:
        - BDI proxy (Baltic Dry Index-like)
        - VLSFO bunker fuel price
        - USD/INR exchange rate
        - Vessel supply index (proxy)

    ⚠️ SYNTHETIC DATA — NOT actual BDI or exchange rate data.
    """
    dates = _make_date_range()
    n = len(dates)

    # BDI proxy (index, not rate) — range ~500–5000
    bdi = _garch_like_series(
        n=n, base=1800, vol=0.018,
        mean_revert=0.02, shock_prob=0.04, shock_magnitude=0.20,
        seed=RANDOM_SEED + 10,
    )
    # Post-COVID spike
    spike = (dates >= "2021-06-01") & (dates <= "2022-03-31")
    bdi[spike] *= np.linspace(1.2, 2.5, spike.sum())

    # VLSFO bunker price (USD/MT)
    vlsfo = _garch_like_series(
        n=n, base=550, vol=0.015,
        mean_revert=0.02, shock_prob=0.03, shock_magnitude=0.15,
        seed=RANDOM_SEED + 20,
    )

    # USD/INR rate
    usd_inr = _garch_like_series(
        n=n, base=74.0, vol=0.003,
        mean_revert=0.01, shock_prob=0.01, shock_magnitude=0.04,
        seed=RANDOM_SEED + 30,
    )
    # Gradual INR depreciation trend
    trend = np.linspace(0, 10, n)   # ~₹10 depreciation over ~6 years
    usd_inr += trend

    # Vessel supply index (100 = normal)
    vessel_supply = _garch_like_series(
        n=n, base=100, vol=0.008,
        mean_revert=0.03, shock_prob=0.02, shock_magnitude=0.08,
        seed=RANDOM_SEED + 40,
    )

    df = pd.DataFrame({
        "date": list(dates.date),
        "bdi_proxy": [round(v, 1) for v in bdi],
        "vlsfo_price_usd_mt": [round(v, 2) for v in vlsfo],
        "usd_inr": [round(v, 2) for v in usd_inr],
        "vessel_supply_index": [round(v, 1) for v in vessel_supply],
    })
    df = _add_demo_label(df)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 4. Port Congestion
# ─────────────────────────────────────────────────────────────────────────────

PORT_CONGESTION_CONFIGS = {
    "paradip":        {"base_wait": 36, "vol": 0.20, "baseline": "medium"},
    "visakhapatnam":  {"base_wait": 28, "vol": 0.18, "baseline": "medium"},
    "gangavaram":     {"base_wait": 18, "vol": 0.15, "baseline": "low"},
    "gopalpur":       {"base_wait": 15, "vol": 0.12, "baseline": "low"},
    "dhamra":         {"base_wait": 20, "vol": 0.15, "baseline": "low"},
    "sagar_sandheads":{"base_wait": 55, "vol": 0.25, "baseline": "high"},
    "haldia":         {"base_wait": 60, "vol": 0.28, "baseline": "high"},
}


def _congestion_level(wait_hrs: float) -> str:
    if wait_hrs < 24:
        return "low"
    elif wait_hrs < 48:
        return "medium"
    else:
        return "high"


def generate_port_congestion() -> pd.DataFrame:
    """
    Generate daily port congestion records.

    ⚠️ SYNTHETIC DATA — NOT actual port authority data.
    """
    dates = _make_date_range()
    n = len(dates)
    records = []
    seed_off = 100

    for port_id, cfg in PORT_CONGESTION_CONFIGS.items():
        wait_series = _garch_like_series(
            n=n,
            base=cfg["base_wait"],
            vol=cfg["vol"],
            mean_revert=0.05,
            shock_prob=0.04,
            shock_magnitude=0.30,
            seed=RANDOM_SEED + seed_off,
        )
        seed_off += 1

        # Monsoon effect (Jul-Sep): congestion spikes for Indian East Coast
        months = pd.DatetimeIndex(dates).month
        monsoon = np.isin(months, [7, 8, 9])
        wait_series[monsoon] *= np.random.uniform(1.10, 1.35, monsoon.sum())

        for i, date in enumerate(dates):
            wh = max(0.0, float(wait_series[i]))
            records.append({
                "date": date.date(),
                "port_id": port_id,
                "avg_waiting_time_hrs": round(wh, 1),
                "congestion_level": _congestion_level(wh),
                "berths_occupied_pct": round(min(95, 40 + wh * 0.8), 1),
                "vessels_at_anchor": max(0, int(wh / 8)),
            })

    df = pd.DataFrame(records)
    df = _add_demo_label(df)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 5. Vessel Fleet Master
# ─────────────────────────────────────────────────────────────────────────────

VESSEL_NAMES = {
    "Handysize": [
        "MV Pacific Wind", "MV Eastern Dawn", "MV Ocean Breeze",
        "MV Coastal Star", "MV Harbour Light",
    ],
    "Supramax": [
        "MV Ocean Crest", "MV Eastern Star", "MV Pacific Trader",
        "MV Indian Crown", "MV Bulk Leader",
    ],
    "Panamax": [
        "MV Horizon Pioneer", "MV Pacific Voyager", "MV Asia Bridge",
        "MV Ocean Titan", "MV Route Master",
    ],
    "Capesize": [
        "MV Iron Giant", "MV Pacific Colossus", "MV Ocean Monarch",
        "MV Bulk Empire", "MV Trade Horizon",
    ],
}

VESSEL_SPECS = {
    "Handysize": {
        "dwt_mt": 28000, "cargo_capacity_mt": 26500,
        "draft_laden_m": 9.8, "draft_ballast_m": 5.5,
        "loa_m": 180.0, "beam_m": 28.0,
        "speed_laden_kn": 13.5, "speed_ballast_kn": 14.5,
        "fuel_consumption_mt_day": 22.0,
        "port_cost_usd_call": 35000,
        "hire_rate_usd_day_ref": 12000,
    },
    "Supramax": {
        "dwt_mt": 58000, "cargo_capacity_mt": 55100,
        "draft_laden_m": 12.5, "draft_ballast_m": 6.8,
        "loa_m": 200.0, "beam_m": 32.0,
        "speed_laden_kn": 14.0, "speed_ballast_kn": 15.0,
        "fuel_consumption_mt_day": 28.0,
        "port_cost_usd_call": 45000,
        "hire_rate_usd_day_ref": 18000,
    },
    "Panamax": {
        "dwt_mt": 75000, "cargo_capacity_mt": 71250,
        "draft_laden_m": 14.0, "draft_ballast_m": 7.5,
        "loa_m": 225.0, "beam_m": 32.3,
        "speed_laden_kn": 14.5, "speed_ballast_kn": 15.5,
        "fuel_consumption_mt_day": 32.0,
        "port_cost_usd_call": 55000,
        "hire_rate_usd_day_ref": 22000,
    },
    "Capesize": {
        "dwt_mt": 180000, "cargo_capacity_mt": 171000,
        "draft_laden_m": 18.0, "draft_ballast_m": 9.5,
        "loa_m": 290.0, "beam_m": 45.0,
        "speed_laden_kn": 14.5, "speed_ballast_kn": 15.5,
        "fuel_consumption_mt_day": 55.0,
        "port_cost_usd_call": 90000,
        "hire_rate_usd_day_ref": 35000,
    },
}

AVAILABILITY_STATUSES = ["available", "available", "available", "chartered", "in_port"]


def generate_vessels_master() -> pd.DataFrame:
    """
    Generate a fleet of demo vessels with realistic specifications.

    ⚠️ SYNTHETIC DATA — vessel names and IMO numbers are fictional.
    """
    rng = np.random.default_rng(RANDOM_SEED)
    records = []
    vessel_id = 1

    for v_type, names in VESSEL_NAMES.items():
        specs = VESSEL_SPECS[v_type]
        for name in names:
            # Slightly randomise individual vessel specs around class average
            records.append({
                "vessel_id": f"V{vessel_id:04d}",
                "vessel_name": name,
                "imo_number": f"IMO{9000000 + vessel_id}",   # fictional
                "vessel_type": v_type,
                "dwt_mt": specs["dwt_mt"] + int(rng.integers(-1000, 1000)),
                "cargo_capacity_mt": specs["cargo_capacity_mt"],
                "draft_laden_m": round(specs["draft_laden_m"] + rng.uniform(-0.2, 0.2), 1),
                "draft_ballast_m": specs["draft_ballast_m"],
                "loa_m": specs["loa_m"],
                "beam_m": specs["beam_m"],
                "speed_laden_kn": round(specs["speed_laden_kn"] + rng.uniform(-0.5, 0.5), 1),
                "speed_ballast_kn": specs["speed_ballast_kn"],
                "fuel_consumption_mt_day": round(specs["fuel_consumption_mt_day"] + rng.uniform(-1, 1), 1),
                "port_cost_usd_call": specs["port_cost_usd_call"],
                "hire_rate_usd_day_ref": specs["hire_rate_usd_day_ref"],
                "build_year": int(rng.integers(2010, 2023)),
                "flag": rng.choice(["Panama", "Marshall Islands", "Liberia", "Hong Kong", "Singapore"]),
                "availability_status": rng.choice(AVAILABILITY_STATUSES),
                "availability_date": (
                    pd.Timestamp("2026-09-15") + pd.Timedelta(days=int(rng.integers(0, 21)))
                ).date(),
            })
            vessel_id += 1

    df = pd.DataFrame(records)
    df = _add_demo_label(df)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Main — generate and save all datasets
# ─────────────────────────────────────────────────────────────────────────────

def save_datasets(output_dir: Path = SYNTHETIC_DIR, verbose: bool = True) -> dict[str, Path]:
    """
    Generate all synthetic datasets and save as CSV files.

    Returns:
        Dict mapping dataset name → saved file path.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    saved: dict[str, Path] = {}

    generators = {
        "freight_rates":      generate_freight_rates,
        "commodity_prices":   generate_commodity_prices,
        "market_indicators":  generate_market_indicators,
        "port_congestion":    generate_port_congestion,
        "vessels_master":     generate_vessels_master,
    }

    for name, gen_fn in generators.items():
        if verbose:
            print(f"  Generating {name}...", end="", flush=True)

        df = gen_fn()
        path = output_dir / f"{name}.csv"
        df.to_csv(path, index=False)
        saved[name] = path

        if verbose:
            print(f" [OK] {len(df):,} rows -> {path.name}")

    # Write README
    readme = output_dir / "README.txt"
    readme.write_text(
        "FREIGHTMIND AI - SYNTHETIC DEMO DATA\n"
        "=====================================\n\n"
        "[!] WARNING: ALL FILES IN THIS DIRECTORY ARE SYNTHETIC/SIMULATED DATA.\n"
        "    They are NOT official market data, NOT Baltic Exchange data,\n"
        "    and NOT actual historical freight rates or prices.\n\n"
        "    Purpose: Demonstration and testing only.\n"
        "    The system is designed so real data can replace these files.\n\n"
        f"Generated: {pd.Timestamp.now().isoformat()}\n"
        f"Seed:      {RANDOM_SEED}  (fully reproducible)\n"
        f"Range:     {START_DATE} to {END_DATE}\n\n"
        "Files:\n"
        "  freight_rates.csv      - Daily freight rates per route x vessel type\n"
        "  commodity_prices.csv   - Coal, iron ore, crude oil prices\n"
        "  market_indicators.csv  - BDI proxy, bunker fuel, USD/INR\n"
        "  port_congestion.csv    - Daily congestion per East Coast India port\n"
        "  vessels_master.csv     - Demo vessel fleet master data\n",
        encoding="utf-8",
    )

    return saved


def print_summary(saved: dict[str, Path]) -> None:
    """Print a human-readable summary of generated datasets."""
    print("\n" + "=" * 60)
    print("  FreightMind AI - Synthetic Dataset Generation Complete")
    print("=" * 60)
    print(f"  [!] ALL DATA IS SYNTHETIC (seed={RANDOM_SEED})")
    print(f"  [DIR] Location: {SYNTHETIC_DIR}")
    print()
    for name, path in saved.items():
        df = pd.read_csv(path)
        print(f"  {name}.csv")
        print(f"     Rows: {len(df):,} | Columns: {list(df.columns)[:5]}...")
        print()
    print("  [OK] Run the data loader next:")
    print("     python -m src.data.loader")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Generate FreightMind AI synthetic datasets"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=SYNTHETIC_DIR,
        help=f"Output directory (default: {SYNTHETIC_DIR})",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output",
    )
    args = parser.parse_args()

    print("\nFreightMind AI - Synthetic Data Generator")
    print("  [!] Generating DEMO DATA (clearly labelled, not real market data)")
    print(f"  [*] Date range: {START_DATE} -> {END_DATE}")
    print(f"  [*] Random seed: {RANDOM_SEED} (fully reproducible)\n")

    saved = save_datasets(output_dir=args.output_dir, verbose=not args.quiet)

    if not args.quiet:
        print_summary(saved)
