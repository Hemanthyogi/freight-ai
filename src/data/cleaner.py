"""
FreightMind AI — Data Cleaner
src/data/cleaner.py

Handles:
  - Missing value imputation (forward-fill for time-series)
  - Duplicate removal
  - Outlier detection + capping (IQR-based)
  - Type coercion
  - Sorting by date

Design principle: NEVER silently drop rows without logging.
Every change is recorded in a CleaningReport.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.utils.logger import logger


@dataclass
class CleaningReport:
    """Records every transformation applied to a dataset."""
    dataset_name: str
    original_rows: int
    final_rows: int
    duplicates_removed: int = 0
    null_imputed: dict[str, int] = field(default_factory=dict)
    outliers_capped: dict[str, int] = field(default_factory=dict)
    operations: list[str] = field(default_factory=list)

    def log(self) -> None:
        logger.info(
            f"CleaningReport [{self.dataset_name}]: "
            f"{self.original_rows} → {self.final_rows} rows | "
            f"dupes removed: {self.duplicates_removed} | "
            f"nulls imputed: {sum(self.null_imputed.values())}"
        )
        for op in self.operations:
            logger.debug(f"  {op}")


def clean_freight_rates(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """
    Clean the freight_rates dataset.

    Steps:
      1. Parse + sort by date
      2. Remove duplicate (date, route_id, vessel_type) rows
      3. Forward-fill missing freight_rate_usd_mt within each route/vessel group
      4. Cap extreme outliers (>3 IQR above Q3) — flag, do not drop
      5. Ensure numeric columns are float
    """
    report = CleaningReport(
        dataset_name="freight_rates",
        original_rows=len(df),
        final_rows=len(df),
    )

    # 1. Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values(["route_id", "vessel_type", "date"]).reset_index(drop=True)
    report.operations.append("Parsed and sorted by date")

    # 2. Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["date", "route_id", "vessel_type"])
    dupes = before - len(df)
    report.duplicates_removed = dupes
    if dupes:
        report.operations.append(f"Removed {dupes} duplicate rows")

    # 3. Forward-fill within groups
    col = "freight_rate_usd_mt"
    if col in df.columns:
        null_before = df[col].isna().sum()
        df[col] = df.groupby(["route_id", "vessel_type"])[col].transform(
            lambda s: s.ffill().bfill()
        )
        null_after = df[col].isna().sum()
        filled = int(null_before - null_after)
        report.null_imputed[col] = filled
        if filled:
            report.operations.append(f"Forward-filled {filled} null freight rates")

    # 4. Outlier capping (IQR method)
    if col in df.columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        upper = q3 + 3 * iqr
        lower = max(0.5, q1 - 3 * iqr)
        outliers = ((df[col] > upper) | (df[col] < lower)).sum()
        df[col] = df[col].clip(lower=lower, upper=upper)
        if outliers:
            report.operations.append(
                f"Capped {outliers} outlier freight rates to [{lower:.2f}, {upper:.2f}]"
            )

    # 5. Type coercion
    for num_col in ["freight_rate_usd_mt", "distance_nm"]:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

    report.final_rows = len(df)
    report.log()
    return df, report


def clean_commodity_prices(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """
    Clean commodity_prices dataset.

    Steps:
      1. Parse + sort by date
      2. Forward-fill missing values (prices don't change on weekends)
      3. Fill remaining gaps with column median
    """
    report = CleaningReport(
        dataset_name="commodity_prices",
        original_rows=len(df),
        final_rows=len(df),
    )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values("date").reset_index(drop=True)

    price_cols = [c for c in df.columns if c not in ("date", "data_source", "is_synthetic")]

    for col in price_cols:
        if col not in df.columns:
            continue
        null_before = df[col].isna().sum()
        df[col] = df[col].ffill().bfill()
        null_after = df[col].isna().sum()
        if null_before > 0:
            report.null_imputed[col] = int(null_before - null_after)
            report.operations.append(f"Forward-filled {null_before} nulls in {col}")

        # Remaining nulls -> median
        if df[col].isna().sum() > 0:
            median = df[col].median()
            df[col] = df[col].fillna(median)
            report.operations.append(f"Filled remaining nulls in {col} with median ({median:.2f})")

    report.final_rows = len(df)
    report.log()
    return df, report


def clean_port_congestion(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """
    Clean port_congestion dataset.

    Steps:
      1. Parse + sort by (port_id, date)
      2. Remove duplicates
      3. Forward-fill waiting times within each port
      4. Clip negative waiting times to 0
    """
    report = CleaningReport(
        dataset_name="port_congestion",
        original_rows=len(df),
        final_rows=len(df),
    )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values(["port_id", "date"]).reset_index(drop=True)

    before = len(df)
    df = df.drop_duplicates(subset=["date", "port_id"])
    report.duplicates_removed = before - len(df)

    col = "avg_waiting_time_hrs"
    if col in df.columns:
        null_before = df[col].isna().sum()
        df[col] = df.groupby("port_id")[col].transform(lambda s: s.ffill().bfill())
        null_after = df[col].isna().sum()
        report.null_imputed[col] = int(null_before - null_after)

        # Clip negatives
        neg = (df[col] < 0).sum()
        df[col] = df[col].clip(lower=0)
        if neg:
            report.operations.append(f"Clipped {neg} negative waiting times to 0")

    report.final_rows = len(df)
    report.log()
    return df, report


def clean_market_indicators(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Clean market_indicators dataset."""
    report = CleaningReport(
        dataset_name="market_indicators",
        original_rows=len(df),
        final_rows=len(df),
    )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values("date").reset_index(drop=True)

    numeric_cols = [c for c in df.columns if c not in ("date", "data_source", "is_synthetic")]
    for col in numeric_cols:
        null_before = df[col].isna().sum()
        df[col] = df[col].ffill().bfill()
        if null_before:
            report.null_imputed[col] = int(null_before)

    report.final_rows = len(df)
    report.log()
    return df, report


# ── Dispatcher ────────────────────────────────────────────────────────────────

CLEANERS = {
    "freight_rates":    clean_freight_rates,
    "commodity_prices": clean_commodity_prices,
    "port_congestion":  clean_port_congestion,
    "market_indicators": clean_market_indicators,
}


def clean_dataset(
    name: str, df: pd.DataFrame
) -> tuple[pd.DataFrame, CleaningReport]:
    """
    Clean a named dataset. Returns (cleaned_df, report).
    Falls back to identity transform + empty report if no specific cleaner.
    """
    if name in CLEANERS:
        return CLEANERS[name](df.copy())

    logger.warning(f"No specific cleaner for '{name}' — returning as-is")
    return df, CleaningReport(
        dataset_name=name,
        original_rows=len(df),
        final_rows=len(df),
    )
