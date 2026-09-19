"""
FreightMind AI — Forecasting Models & Predictor Service Tests
tests/test_forecasting.py
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.forecasting.baseline import NaiveForecaster, MovingAverageForecaster
from src.forecasting.ml_models import MultiHorizonForecaster
from src.forecasting.predictor import FreightPredictorService


@pytest.fixture
def dummy_features_df():
    np.random.seed(42)
    n = 60
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    rates = 15.0 + np.sin(np.linspace(0, 5, n)) * 2.0 + np.random.normal(0, 0.2, n)
    
    df = pd.DataFrame({
        "date": dates,
        "route_id": ["AU_COAL_PARADIP"] * n,
        "vessel_type": ["Panamax"] * n,
        "freight_rate_usd_mt": rates,
        "freight_rate_usd_mt_lag_1": np.roll(rates, 1),
        "freight_rate_usd_mt_roll_7d_mean": rates,
        "feature_1": np.random.rand(n),
        "feature_2": np.random.rand(n),
        "target_7d": np.roll(rates, -7),
        "target_14d": np.roll(rates, -14),
    })
    return df


class TestBaselineModels:
    def test_naive_forecaster(self, dummy_features_df):
        naive = NaiveForecaster()
        preds = naive.predict(dummy_features_df)
        assert len(preds) == len(dummy_features_df)
        np.testing.assert_array_almost_equal(preds, dummy_features_df["freight_rate_usd_mt"].to_numpy())

    def test_moving_average_forecaster(self, dummy_features_df):
        ma = MovingAverageForecaster(window=7)
        preds = ma.predict(dummy_features_df)
        assert len(preds) == len(dummy_features_df)
        assert not np.isnan(preds).any()


class TestMLForecaster:
    def test_multi_horizon_fit_predict(self, dummy_features_df):
        X = dummy_features_df[["feature_1", "feature_2", "freight_rate_usd_mt_lag_1"]]
        forecaster = MultiHorizonForecaster(model_type="xgboost", params={"n_estimators": 10, "max_depth": 3})
        forecaster.fit(X, dummy_features_df, horizons=[7, 14])

        y_pred, lower, upper = forecaster.predict_with_interval(X, horizon=14, confidence_level=0.80)
        assert len(y_pred) == len(dummy_features_df)
        assert (lower <= y_pred).all()
        assert (y_pred <= upper).all()
        assert (lower >= 0).all()  # Rates cannot be negative
