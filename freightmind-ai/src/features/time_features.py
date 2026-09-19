"""
FreightMind AI — Time Feature Engineering
src/features/time_features.py

Creates temporal features from a date column.
These features help models learn seasonal and cyclical patterns.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.constants import MONSOON_MONTHS, QUARTER_MAP, SEASON_MAP


def add_time_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """
    Add time-based features to the DataFrame.

    Why each feature matters:
      - day_of_week: Freight activity lower on weekends
      - month:       Seasonal cargo demand patterns
      - quarter:     Financial quarter affects procurement decisions
      - season:      Weather, monsoon, demand cycles
      - is_monsoon:  Indian East Coast ports see congestion spikes Jun-Sep
      - year:        Long-run trend capture
      - day_of_year: Fine-grained seasonality for XGBoost/LightGBM
      - week_of_year: Weekly trading patterns
      - sin/cos encodings: Cyclical encoding prevents ordinal bias

    Args:
        df:       DataFrame with a date column
        date_col: Name of the date column

    Returns:
        DataFrame with new time feature columns appended.
    """
    df = df.copy()
    dates = pd.to_datetime(df[date_col])

    df["day_of_week"] = dates.dt.dayofweek          # 0=Mon, 6=Sun
    df["day_of_month"] = dates.dt.day
    df["day_of_year"] = dates.dt.dayofyear
    df["week_of_year"] = dates.dt.isocalendar().week.astype(int)
    df["month"] = dates.dt.month
    df["quarter"] = dates.dt.quarter
    df["year"] = dates.dt.year

    # Categorical season
    df["season"] = dates.dt.month.map(SEASON_MAP)
    df["quarter_label"] = dates.dt.month.map(QUARTER_MAP)

    # Indian monsoon flag
    df["is_monsoon"] = dates.dt.month.isin(MONSOON_MONTHS).astype(int)

    # Weekend flag
    df["is_weekend"] = (dates.dt.dayofweek >= 5).astype(int)

    # Cyclical encodings — prevent model treating Dec→Jan as large jump
    df["month_sin"] = np.sin(2 * np.pi * dates.dt.month / 12)
    df["month_cos"] = np.cos(2 * np.pi * dates.dt.month / 12)
    df["dow_sin"] = np.sin(2 * np.pi * dates.dt.dayofweek / 7)
    df["dow_cos"] = np.cos(2 * np.pi * dates.dt.dayofweek / 7)

    return df
