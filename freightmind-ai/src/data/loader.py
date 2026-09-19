"""
FreightMind AI — Data Loader
src/data/loader.py

Orchestrates the full data ingestion pipeline:
  1. Load from source (synthetic CSV or real CSV/DB)
  2. Validate
  3. Clean
  4. Save to data/processed/

Usage:
    python -m src.data.loader            # Load all datasets
    python -m src.data.loader --dataset freight_rates
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.data.cleaner import clean_dataset
from src.data.validator import validate_dataset
from src.utils.config import get_data_dir, is_demo_mode
from src.utils.logger import logger

_DATA_DIR = get_data_dir()
SYNTHETIC_DIR = _DATA_DIR / "synthetic"
PROCESSED_DIR = _DATA_DIR / "processed"

DATASET_NAMES = [
    "freight_rates",
    "commodity_prices",
    "market_indicators",
    "port_congestion",
    "vessels_master",
]


def _load_csv(name: str) -> pd.DataFrame:
    """
    Load a dataset CSV. In DEMO MODE loads from data/synthetic/.
    In real mode loads from data/raw/ (expected to be populated with real data).
    """
    demo = is_demo_mode()
    source_dir = SYNTHETIC_DIR if demo else (_DATA_DIR / "raw")
    path = source_dir / f"{name}.csv"

    if not path.exists():
        if demo:
            raise FileNotFoundError(
                f"Synthetic data not found at {path}.\n"
                "Run: python -m src.data.synthetic_generator"
            )
        else:
            raise FileNotFoundError(
                f"Real data not found at {path}.\n"
                "Set DEMO_MODE=true in .env to use synthetic data, or "
                "populate data/raw/ with real datasets."
            )

    source_label = "DEMO_DATA" if demo else "REAL_DATA"
    logger.info(f"Loading [{source_label}] {name} from {path}")
    df = pd.read_csv(path)
    return df


def load_and_process(name: str, save: bool = True) -> pd.DataFrame:
    """
    Full pipeline for one dataset:
      load → validate → clean → save to processed/

    Args:
        name: Dataset name (e.g. 'freight_rates')
        save: Whether to save the processed CSV

    Returns:
        Cleaned DataFrame
    """
    # Load
    df_raw = _load_csv(name)
    logger.info(f"  Loaded {len(df_raw):,} rows")

    # Validate
    report = validate_dataset(name, df_raw.copy())
    if not report.is_valid:
        logger.error(f"Validation FAILED for {name}. Check errors above.")
        # In demo mode, continue with warnings; in production, raise
        if not is_demo_mode():
            raise ValueError(f"Dataset {name} failed validation: {report.errors}")

    # Clean
    df_clean, clean_report = clean_dataset(name, df_raw)
    logger.info(f"  Cleaned: {len(df_raw):,} -> {len(df_clean):,} rows")

    # Save processed
    if save:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        out_path = PROCESSED_DIR / f"{name}.csv"
        df_clean.to_csv(out_path, index=False)
        logger.info(f"  Saved -> {out_path}")

    return df_clean


def load_all(save: bool = True) -> dict[str, pd.DataFrame]:
    """Load and process all datasets."""
    results: dict[str, pd.DataFrame] = {}
    mode = "DEMO" if is_demo_mode() else "REAL"
    logger.info(f"=== FreightMind AI Data Loader [{mode} MODE] ===")

    for name in DATASET_NAMES:
        logger.info(f"\n[*] Processing: {name}")
        try:
            df = load_and_process(name, save=save)
            results[name] = df
        except FileNotFoundError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(f"Unexpected error loading {name}: {e}")

    logger.info(f"\n[OK] Loaded {len(results)}/{len(DATASET_NAMES)} datasets")
    return results


def get_freight_rates(route_id: str | None = None, vessel_type: str | None = None) -> pd.DataFrame:
    """
    Convenience: load processed freight_rates and optionally filter.
    """
    path = PROCESSED_DIR / "freight_rates.csv"
    if not path.exists():
        raise FileNotFoundError(
            "Processed freight_rates.csv not found. "
            "Run: python -m src.data.loader"
        )
    df = pd.read_csv(path, parse_dates=["date"])
    if route_id:
        df = df[df["route_id"] == route_id]
    if vessel_type:
        df = df[df["vessel_type"] == vessel_type]
    return df.sort_values("date").reset_index(drop=True)


def get_market_indicators() -> pd.DataFrame:
    """Convenience: load processed market indicators."""
    path = PROCESSED_DIR / "market_indicators.csv"
    if not path.exists():
        raise FileNotFoundError("Run: python -m src.data.loader first")
    return pd.read_csv(path, parse_dates=["date"]).sort_values("date").reset_index(drop=True)


def get_port_congestion(port_id: str | None = None) -> pd.DataFrame:
    """Convenience: load processed port congestion."""
    path = PROCESSED_DIR / "port_congestion.csv"
    if not path.exists():
        raise FileNotFoundError("Run: python -m src.data.loader first")
    df = pd.read_csv(path, parse_dates=["date"])
    if port_id:
        df = df[df["port_id"] == port_id]
    return df.sort_values(["port_id", "date"]).reset_index(drop=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FreightMind AI Data Loader")
    parser.add_argument(
        "--dataset", "-d",
        choices=DATASET_NAMES + ["all"],
        default="all",
        help="Dataset to load (default: all)",
    )
    args = parser.parse_args()

    if args.dataset == "all":
        load_all(save=True)
    else:
        df = load_and_process(args.dataset, save=True)
        print(f"\nLoaded {len(df):,} rows of {args.dataset}")
        print(df.head())
