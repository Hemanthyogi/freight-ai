"""
FreightMind AI — Machine Learning Forecasting Models
src/forecasting/ml_models.py

Implements Multi-Horizon Gradient Boosted Forecasters:
  1. XGBoost Forecaster (Primary candidate)
  2. LightGBM Forecaster (High-efficiency candidate)
  3. Random Forest Forecaster (Ensemble benchmark)

Each forecaster:
  - Trains dedicated models per forecast horizon: 7d, 14d, 30d, 60d, 90d
  - Computes empirical residual standard deviation on validation set
  - Produces calibrated 80% prediction intervals [y_hat - 1.28*sigma, y_hat + 1.28*sigma]
  - Provides feature importance rankings
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor

try:
    from lightgbm import LGBMRegressor
except ImportError:
    LGBMRegressor = None

try:
    from xgboost import XGBRegressor
except ImportError:
    XGBRegressor = None

from src.utils.constants import FORECAST_HORIZONS
from src.utils.logger import logger


class MultiHorizonForecaster:
    """
    Base wrapper training independent regressor models for each forecast horizon.
    """

    def __init__(self, model_type: str = "random_forest", params: dict[str, Any] | None = None) -> None:
        self.model_type = model_type.lower()
        self.params = params or {}
        self.models: dict[int, Any] = {}
        self.residual_std: dict[int, float] = {}  # For 80% confidence intervals
        self.feature_names: list[str] = []
        self.training_time_seconds: float = 0.0

    def _create_regressor(self) -> Any:
        if self.model_type == "xgboost":
            if XGBRegressor is None:
                logger.warning("XGBoost not installed; falling back to HistGradientBoostingRegressor.")
                return HistGradientBoostingRegressor(max_iter=150, learning_rate=0.05, max_depth=5, random_state=42)
            default_params = {
                "n_estimators": 150,
                "learning_rate": 0.05,
                "max_depth": 5,
                "subsample": 0.85,
                "colsample_bytree": 0.85,
                "random_state": 42,
                "n_jobs": -1,
            }
            default_params.update(self.params)
            return XGBRegressor(**default_params)
        elif self.model_type == "lightgbm":
            if LGBMRegressor is None:
                logger.warning("LightGBM not installed; falling back to HistGradientBoostingRegressor.")
                return HistGradientBoostingRegressor(max_iter=150, learning_rate=0.05, max_depth=5, random_state=42)
            default_params = {
                "n_estimators": 150,
                "learning_rate": 0.05,
                "num_leaves": 31,
                "subsample": 0.85,
                "colsample_bytree": 0.85,
                "random_state": 42,
                "verbose": -1,
                "n_jobs": -1,
            }
            default_params.update(self.params)
            return LGBMRegressor(**default_params)
        elif self.model_type == "random_forest":
            default_params = {
                "n_estimators": 100,
                "max_depth": 8,
                "random_state": 42,
                "n_jobs": -1,
            }
            default_params.update(self.params)
            return RandomForestRegressor(**default_params)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def fit(
        self,
        X_train: pd.DataFrame,
        train_df: pd.DataFrame,
        X_val: pd.DataFrame | None = None,
        val_df: pd.DataFrame | None = None,
        horizons: list[int] | None = None,
    ) -> MultiHorizonForecaster:
        """
        Fit models for each horizon.
        """
        if horizons is None:
            horizons = FORECAST_HORIZONS

        self.feature_names = list(X_train.columns)
        start_time = time.time()

        for h in horizons:
            target_col = f"target_{h}d"
            if target_col not in train_df.columns:
                continue

            # Drop unobservable forward targets at end of series
            valid_mask = ~train_df[target_col].isna()
            X_h = X_train[valid_mask]
            y_h = train_df.loc[valid_mask, target_col]

            model = self._create_regressor()
            model.fit(X_h, y_h)
            self.models[h] = model

            # Compute residual std on validation split for confidence intervals
            if X_val is not None and val_df is not None and target_col in val_df.columns:
                val_mask = ~val_df[target_col].isna()
                if val_mask.sum() > 0:
                    y_val = val_df.loc[val_mask, target_col]
                    y_pred = model.predict(X_val[val_mask])
                    residuals = y_val - y_pred
                    self.residual_std[h] = float(np.std(residuals))
                else:
                    self.residual_std[h] = 1.5
            else:
                self.residual_std[h] = 1.5

        self.training_time_seconds = time.time() - start_time
        return self

    def predict_horizon(self, X: pd.DataFrame, horizon: int = 14) -> np.ndarray:
        if horizon not in self.models:
            raise ValueError(f"Model for horizon {horizon}d was not trained.")
        return self.models[horizon].predict(X[self.feature_names])

    def predict_with_interval(
        self, X: pd.DataFrame, horizon: int = 14, confidence_level: float = 0.80
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Returns (y_pred, lower_bound, upper_bound) for the given horizon.
        80% confidence uses z ~ 1.28; 95% confidence uses z ~ 1.96.
        """
        y_pred = self.predict_horizon(X, horizon)
        std = self.residual_std.get(horizon, 1.5)

        # z-score multiplier
        z = 1.28 if confidence_level <= 0.80 else 1.96
        margin = z * std

        lower = np.maximum(0.5, y_pred - margin)
        upper = y_pred + margin
        return y_pred, lower, upper

    def get_feature_importances(self, horizon: int = 14, top_n: int = 10) -> list[tuple[str, float]]:
        """Return top N feature importances for a specific horizon."""
        if horizon not in self.models:
            return []
        model = self.models[horizon]
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            pairs = sorted(zip(self.feature_names, importances), key=lambda x: x[1], reverse=True)
            return [(name, round(float(imp), 4)) for name, imp in pairs[:top_n]]
        return []
