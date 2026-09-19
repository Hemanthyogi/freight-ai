"""
FreightMind AI — Real-Time Freight Predictor & Inference Service
src/forecasting/predictor.py

Serves live predictions with uncertainty intervals for the API & Dashboard:
  - Multi-horizon forecasts: 7d, 14d, 30d, 60d, 90d
  - 80% Prediction Intervals (Lower / Upper corridor)
  - Historical + Forecast time series for interactive UI charting
  - Model confidence rating (High / Medium / Low)
  - Top feature drivers / feature importance
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.forecasting.ml_models import MultiHorizonForecaster
from src.utils.constants import FORECAST_HORIZONS
from src.utils.logger import logger

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = _PROJECT_ROOT / "data" / "processed"
MODELS_DIR = _PROJECT_ROOT / "models" / "freight_forecast"
PREPROCESSORS_DIR = _PROJECT_ROOT / "models" / "preprocessors"


@dataclass
class ForecastHorizonResult:
    horizon_days: int
    predicted_rate_usd_mt: float
    lower_bound_usd_mt: float
    upper_bound_usd_mt: float
    rate_change_pct: float         # Change vs current rate

    def to_dict(self) -> dict[str, Any]:
        return {
            "horizon_days": self.horizon_days,
            "predicted_rate_usd_mt": round(self.predicted_rate_usd_mt, 2),
            "lower_bound_usd_mt": round(self.lower_bound_usd_mt, 2),
            "upper_bound_usd_mt": round(self.upper_bound_usd_mt, 2),
            "rate_change_pct": round(self.rate_change_pct, 1),
        }


@dataclass
class FreightForecastResponse:
    route_id: str
    vessel_type: str
    current_rate_usd_mt: float
    confidence_level: str          # "High", "Medium", "Low"
    confidence_explanation: str
    horizons: dict[int, ForecastHorizonResult]
    historical_series: list[dict[str, Any]]
    forecast_series: list[dict[str, Any]]
    top_feature_drivers: list[dict[str, Any]]
    model_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "vessel_type": self.vessel_type,
            "current_rate_usd_mt": round(self.current_rate_usd_mt, 2),
            "confidence_level": self.confidence_level,
            "confidence_explanation": self.confidence_explanation,
            "horizons": {h: res.to_dict() for h, res in self.horizons.items()},
            "historical_series": self.historical_series,
            "forecast_series": self.forecast_series,
            "top_feature_drivers": self.top_feature_drivers,
            "model_version": self.model_version,
        }


class FreightPredictorService:
    """
    Inference service encapsulating the trained multi-horizon model.
    """

    def __init__(self) -> None:
        self.model: MultiHorizonForecaster | None = None
        self.feature_names: list[str] = []
        self.full_df: pd.DataFrame | None = None
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        model_path = MODELS_DIR / "best_freight_model.joblib"
        if not model_path.exists():
            logger.warning(f"Trained model not found at {model_path}. Run evaluator first.")
            return

        self.model = joblib.load(model_path)
        
        meta_path = PREPROCESSORS_DIR / "feature_names.json"
        if meta_path.exists():
            with open(meta_path, "r") as f:
                data = json.load(f)
                self.feature_names = data.get("feature_columns", [])

        features_path = DATA_DIR / "full_features.csv"
        if features_path.exists():
            self.full_df = pd.read_csv(features_path)
            self.full_df["date"] = pd.to_datetime(self.full_df["date"])

    def predict(
        self,
        route_id: str = "AU_COAL_PARADIP",
        vessel_type: str = "Panamax",
        current_rate_override: float | None = None,
    ) -> FreightForecastResponse:
        """
        Generate full forecast response with uncertainty corridor and historical context.
        """
        if self.model is None or self.full_df is None:
            self._load_artifacts()
            if self.model is None:
                raise RuntimeError("Forecasting model is not trained yet. Run 'python -m src.forecasting.evaluator'")

        # Find the latest available feature row for this route & vessel
        sub = self.full_df[
            (self.full_df["route_id"] == route_id) & (self.full_df["vessel_type"] == vessel_type)
        ].sort_values("date")

        if sub.empty:
            # Fallback to route alone or general sample
            sub = self.full_df[self.full_df["route_id"] == route_id].sort_values("date")
            if sub.empty:
                sub = self.full_df.sort_values("date")

        latest_row = sub.iloc[[-1]]
        latest_date = pd.to_datetime(latest_row["date"].iloc[0])
        current_rate = float(current_rate_override or latest_row["freight_rate_usd_mt"].iloc[0])

        horizon_results = {}
        forecast_points = []

        for h in FORECAST_HORIZONS:
            pred, low, up = self.model.predict_with_interval(
                latest_row[self.feature_names], horizon=h, confidence_level=0.80
            )
            val = float(pred[0])
            lo = float(low[0])
            hi = float(up[0])

            pct_change = ((val - current_rate) / current_rate) * 100 if current_rate > 0 else 0.0
            horizon_results[h] = ForecastHorizonResult(
                horizon_days=h,
                predicted_rate_usd_mt=val,
                lower_bound_usd_mt=lo,
                upper_bound_usd_mt=hi,
                rate_change_pct=pct_change,
            )

            fc_date = latest_date + pd.Timedelta(days=h)
            forecast_points.append({
                "date": str(fc_date.date()),
                "forecast_rate": round(val, 2),
                "lower_bound": round(lo, 2),
                "upper_bound": round(hi, 2),
                "horizon_days": h,
            })

        # Confidence assessment based on prediction interval spread
        ci_14_spread = (horizon_results[14].upper_bound_usd_mt - horizon_results[14].lower_bound_usd_mt) / current_rate
        if ci_14_spread <= 0.18:
            conf_level = "High"
            conf_exp = "Tight prediction interval; strong historical continuity and low route volatility."
        elif ci_14_spread <= 0.32:
            conf_level = "Medium"
            conf_exp = "Normal uncertainty corridor; represents market volatility and seasonal transitions."
        else:
            conf_level = "Low"
            conf_exp = "Wide prediction interval; heightened macro volatility or rapid freight fluctuations."

        # Extract last 90 days of historical data for UI chart
        recent_hist = sub.tail(90)
        hist_series = [
            {
                "date": str(pd.to_datetime(d).date()),
                "rate": round(float(r), 2),
            }
            for d, r in zip(recent_hist["date"], recent_hist["freight_rate_usd_mt"])
        ]

        # Top feature drivers from primary model (14d horizon)
        raw_drivers = self.model.get_feature_importances(horizon=14, top_n=5)
        clean_drivers = [
            {"feature": name.replace("_", " ").title(), "importance": round(imp, 3)}
            for name, imp in raw_drivers
        ]

        return FreightForecastResponse(
            route_id=route_id,
            vessel_type=vessel_type,
            current_rate_usd_mt=current_rate,
            confidence_level=conf_level,
            confidence_explanation=conf_exp,
            horizons=horizon_results,
            historical_series=hist_series,
            forecast_series=forecast_points,
            top_feature_drivers=clean_drivers,
            model_version=f"FreightMind-XGBoost-v1.0 ({latest_date.date()})",
        )
