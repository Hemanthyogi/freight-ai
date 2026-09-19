"""
FreightMind AI — Baseline Forecasting Models
src/forecasting/baseline.py

Implements essential baseline models for benchmark comparison:
  1. Naive Forecaster: y_{t+h} = y_t (tomorrow's rate equals today's rate)
  2. Moving Average Forecaster: y_{t+h} = (1/W) * sum_{i=0}^{W-1} y_{t-i} (7-day or 14-day rolling mean)

Any ML or deep learning model MUST outperform these baselines to justify deployment.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class NaiveForecaster:
    """
    Persistence / Random Walk benchmark.
    Predicts that future freight rates remain identical to the latest observed rate.
    """

    def __init__(self, rate_col: str = "freight_rate_usd_mt") -> None:
        self.rate_col = rate_col
        self.name = "Naive (Persistence)"

    def fit(self, X: pd.DataFrame, y: np.ndarray | None = None) -> NaiveForecaster:
        # No parameter training required for naive persistence
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.rate_col in X.columns:
            return X[self.rate_col].to_numpy()
        # Fallback to lag_1 if raw rate is excluded
        lag1_col = f"{self.rate_col}_lag_1"
        if lag1_col in X.columns:
            return X[lag1_col].to_numpy()
        raise ValueError(f"Neither {self.rate_col} nor {lag1_col} found in input features.")


class MovingAverageForecaster:
    """
    Rolling Moving Average benchmark.
    Predicts future freight rate as the recent W-day historical average.
    """

    def __init__(self, window: int = 7, target_col: str = "freight_rate_usd_mt") -> None:
        self.window = window
        self.target_col = target_col
        self.name = f"Moving Average ({window}d)"

    def fit(self, X: pd.DataFrame, y: np.ndarray | None = None) -> MovingAverageForecaster:
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        roll_col = f"{self.target_col}_roll_{self.window}d_mean"
        if roll_col in X.columns:
            return X[roll_col].to_numpy()
        # Fallback to 7d or raw lag
        if f"{self.target_col}_roll_7d_mean" in X.columns:
            return X[f"{self.target_col}_roll_7d_mean"].to_numpy()
        if f"{self.target_col}_lag_1" in X.columns:
            return X[f"{self.target_col}_lag_1"].to_numpy()
        raise ValueError(f"Required rolling column '{roll_col}' not found in features.")
