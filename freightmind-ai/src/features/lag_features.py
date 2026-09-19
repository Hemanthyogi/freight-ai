"""
FreightMind AI — Lag & Rolling Feature Engineering
src/features/lag_features.py

Creates lag and rolling window features for time-series forecasting.

WHY THESE MATTER:
  Lag features give the model "memory" — the freight rate today is
  strongly influenced by yesterday's rate, last week's rate, etc.

  Rolling statistics capture trend and volatility over recent windows,
  which is far more informative than a single point value.

⚠️  CRITICAL: Always apply lags AFTER chronological sorting.
    Never apply lags across different groups (routes/vessels) without groupby.
    Leakage: Do NOT use lags from the test period during training.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.constants import FORECAST_HORIZONS


def add_lag_features(
    df: pd.DataFrame,
    target_col: str = "freight_rate_usd_mt",
    lag_days: list[int] | None = None,
    group_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Add lag features for the target column.

    Args:
        df:          DataFrame sorted chronologically.
        target_col:  Column to lag.
        lag_days:    List of lag periods in days (default: [1,7,14,30]).
        group_cols:  If provided, lag within each group (e.g. per route).

    Returns:
        DataFrame with lag columns appended.
    """
    if lag_days is None:
        lag_days = [1, 7, 14, 30]

    df = df.copy()

    for lag in lag_days:
        col_name = f"{target_col}_lag_{lag}"
        if group_cols:
            df[col_name] = df.groupby(group_cols)[target_col].shift(lag)
        else:
            df[col_name] = df[target_col].shift(lag)

    return df


def add_rolling_features(
    df: pd.DataFrame,
    target_col: str = "freight_rate_usd_mt",
    windows: list[int] | None = None,
    stats: list[str] | None = None,
    group_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Add rolling window statistics for the target column.

    Rolling features capture:
      - mean: Smoothed trend (noise-reduced signal)
      - std:  Volatility (key for market timing)
      - min/max: Range within window
      - pct_change: Momentum

    Args:
        df:          DataFrame sorted chronologically.
        target_col:  Column to compute rolling stats on.
        windows:     List of window sizes in days (default: [7,14,30]).
        stats:       List of statistics (default: ['mean','std','min','max']).
        group_cols:  If provided, compute rolling within each group.

    Returns:
        DataFrame with rolling feature columns appended.
    """
    if windows is None:
        windows = [7, 14, 30]
    if stats is None:
        stats = ["mean", "std", "min", "max"]

    df = df.copy()

    for window in windows:
        for stat in stats:
            col_name = f"{target_col}_roll_{window}d_{stat}"
            if group_cols:
                series = df.groupby(group_cols)[target_col]
            else:
                series = df[target_col]

            if group_cols:
                rolled = series.transform(
                    lambda s, w=window, st=stat: s.rolling(w, min_periods=1).agg(st)
                )
            else:
                rolled = series.rolling(window, min_periods=1).agg(stat)

            df[col_name] = rolled

    # Momentum: percentage change over 7 and 30 days
    for lag in [7, 30]:
        col_name = f"{target_col}_pct_change_{lag}d"
        if group_cols:
            df[col_name] = df.groupby(group_cols)[target_col].pct_change(lag)
        else:
            df[col_name] = df[target_col].pct_change(lag)

    return df


def get_lag_feature_names(
    target_col: str = "freight_rate_usd_mt",
    lag_days: list[int] | None = None,
    windows: list[int] | None = None,
    stats: list[str] | None = None,
) -> list[str]:
    """Return the list of lag/rolling feature column names."""
    if lag_days is None:
        lag_days = [1, 7, 14, 30]
    if windows is None:
        windows = [7, 14, 30]
    if stats is None:
        stats = ["mean", "std", "min", "max"]

    names = [f"{target_col}_lag_{lag}" for lag in lag_days]
    names += [f"{target_col}_roll_{w}d_{s}" for w in windows for s in stats]
    names += [f"{target_col}_pct_change_{lag}d" for lag in [7, 30]]
    return names
