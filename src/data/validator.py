"""
FreightMind AI — Data Validator
src/data/validator.py

Validates raw and synthetic datasets before they enter the pipeline.
Checks schema, types, ranges, and required fields.
Separates validation errors (reject row) from warnings (flag + keep).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from src.utils.constants import (
    CARGO_TYPES,
    EAST_COAST_PORTS,
    VESSEL_TYPES,
)
from src.utils.logger import logger


@dataclass
class ValidationReport:
    """Summary of a validation run."""
    dataset_name: str
    total_rows: int
    valid_rows: int
    error_rows: int
    warning_rows: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.error_rows == 0

    def summary(self) -> str:
        status = "[PASSED]" if self.is_valid else "[FAILED]"
        return (
            f"{status} | {self.dataset_name} | "
            f"{self.valid_rows}/{self.total_rows} valid rows | "
            f"{self.error_rows} errors | {self.warning_rows} warnings"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Freight Rates Validation
# ─────────────────────────────────────────────────────────────────────────────

FREIGHT_SCHEMA = {
    "date":                  "datetime64[ns]",
    "route_id":              str,
    "origin":                str,
    "destination":           str,
    "cargo_type":            str,
    "vessel_type":           str,
    "freight_rate_usd_mt":   float,
    "distance_nm":           float,
}

FREIGHT_RATE_MIN = 1.0    # USD/MT — below this is suspicious
FREIGHT_RATE_MAX = 100.0  # USD/MT — above this is suspicious for bulk


def validate_freight_rates(df: pd.DataFrame) -> ValidationReport:
    errors, warnings = [], []
    n = len(df)

    # 1. Required columns
    required = list(FREIGHT_SCHEMA.keys())
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {missing}")

    # 2. Date parsing
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        bad_dates = df["date"].isna().sum()
        if bad_dates:
            errors.append(f"{bad_dates} rows have unparseable dates")

    # 3. Vessel type
    if "vessel_type" in df.columns:
        bad_vt = ~df["vessel_type"].isin(VESSEL_TYPES)
        if bad_vt.any():
            vals = df.loc[bad_vt, "vessel_type"].unique()
            errors.append(f"Unknown vessel types: {vals}")

    # 4. Cargo type
    if "cargo_type" in df.columns:
        bad_ct = ~df["cargo_type"].isin(CARGO_TYPES)
        if bad_ct.any():
            vals = df.loc[bad_ct, "cargo_type"].unique()
            warnings.append(f"Unrecognised cargo types (will keep): {vals}")

    # 5. Freight rate range
    if "freight_rate_usd_mt" in df.columns:
        df["freight_rate_usd_mt"] = pd.to_numeric(df["freight_rate_usd_mt"], errors="coerce")
        null_rates = df["freight_rate_usd_mt"].isna().sum()
        if null_rates:
            errors.append(f"{null_rates} rows have null freight_rate_usd_mt")

        low = (df["freight_rate_usd_mt"] < FREIGHT_RATE_MIN).sum()
        high = (df["freight_rate_usd_mt"] > FREIGHT_RATE_MAX).sum()
        if low:
            warnings.append(f"{low} rows with freight_rate < {FREIGHT_RATE_MIN} (possible error)")
        if high:
            warnings.append(f"{high} rows with freight_rate > {FREIGHT_RATE_MAX} (outlier — check)")

    # 6. Duplicate check
    if "date" in df.columns and "route_id" in df.columns and "vessel_type" in df.columns:
        dups = df.duplicated(subset=["date", "route_id", "vessel_type"]).sum()
        if dups:
            warnings.append(f"{dups} duplicate (date, route_id, vessel_type) rows")

    valid_rows = n - (df["freight_rate_usd_mt"].isna().sum() if "freight_rate_usd_mt" in df.columns else 0)

    return ValidationReport(
        dataset_name="freight_rates",
        total_rows=n,
        valid_rows=int(valid_rows),
        error_rows=sum(1 for e in errors if "rows" not in e),
        warning_rows=len(warnings),
        errors=errors,
        warnings=warnings,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Commodity Prices Validation
# ─────────────────────────────────────────────────────────────────────────────

COMMODITY_COLUMNS = [
    "thermal_coal_usd_mt",
    "iron_ore_usd_mt",
    "coking_coal_usd_mt",
    "fertilizer_usd_mt",
    "crude_oil_usd_bbl",
]


def validate_commodity_prices(df: pd.DataFrame) -> ValidationReport:
    errors, warnings = [], []
    n = len(df)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if df["date"].isna().sum():
            errors.append("Null dates found in commodity prices")

    for col in COMMODITY_COLUMNS:
        if col not in df.columns:
            warnings.append(f"Optional column missing: {col}")
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")
        nulls = df[col].isna().sum()
        if nulls:
            warnings.append(f"{nulls} null values in {col}")
        if (df[col] < 0).any():
            errors.append(f"Negative values in {col}")

    return ValidationReport(
        dataset_name="commodity_prices",
        total_rows=n,
        valid_rows=n,
        error_rows=len(errors),
        warning_rows=len(warnings),
        errors=errors,
        warnings=warnings,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Port Congestion Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_port_congestion(df: pd.DataFrame) -> ValidationReport:
    errors, warnings = [], []
    n = len(df)

    if "port_id" in df.columns:
        unknown = ~df["port_id"].isin(EAST_COAST_PORTS)
        if unknown.any():
            vals = df.loc[unknown, "port_id"].unique()
            warnings.append(f"Port IDs not in known list (will keep): {vals}")

    if "avg_waiting_time_hrs" in df.columns:
        df["avg_waiting_time_hrs"] = pd.to_numeric(df["avg_waiting_time_hrs"], errors="coerce")
        if (df["avg_waiting_time_hrs"] < 0).any():
            errors.append("Negative waiting times found")
        if (df["avg_waiting_time_hrs"] > 720).any():  # >30 days is unrealistic
            warnings.append("Waiting times > 720 hrs (30 days) found — check data")

    return ValidationReport(
        dataset_name="port_congestion",
        total_rows=n,
        valid_rows=n,
        error_rows=len(errors),
        warning_rows=len(warnings),
        errors=errors,
        warnings=warnings,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher
# ─────────────────────────────────────────────────────────────────────────────

VALIDATORS = {
    "freight_rates":    validate_freight_rates,
    "commodity_prices": validate_commodity_prices,
    "port_congestion":  validate_port_congestion,
}


def validate_dataset(name: str, df: pd.DataFrame) -> ValidationReport:
    """
    Validate a named dataset. Falls back to a generic report if no
    specific validator exists.
    """
    if name in VALIDATORS:
        report = VALIDATORS[name](df.copy())
    else:
        logger.warning(f"No specific validator for '{name}' — running generic check")
        report = ValidationReport(
            dataset_name=name,
            total_rows=len(df),
            valid_rows=len(df),
            error_rows=0,
            warning_rows=0,
        )

    logger.info(report.summary())
    for err in report.errors:
        logger.error(f"  [ERROR] {err}")
    for warn in report.warnings:
        logger.warning(f"  [WARN] {warn}")

    return report
