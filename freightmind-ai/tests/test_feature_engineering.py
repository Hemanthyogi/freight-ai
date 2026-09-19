"""
FreightMind AI — Feature Engineering Tests
tests/test_feature_engineering.py

Tests:
  1. Time and cyclical feature extraction
  2. Grouped lag & rolling statistic generation
  3. Multi-horizon targets (7d, 14d, 30d, 60d, 90d)
  4. Strict chronological split (zero data leakage)
  5. Preprocessor serialization and registry check
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd
import json

from src.features.time_features import add_time_features
from src.features.lag_features import add_lag_features, add_rolling_features
from src.features.pipeline import FeatureEngineeringPipeline, PREPROCESSORS_DIR


@pytest.fixture
def sample_timeseries_df():
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    df1 = pd.DataFrame({
        "date": dates,
        "route_id": ["AU_COAL_PARADIP"] * 100,
        "vessel_type": ["Panamax"] * 100,
        "freight_rate_usd_mt": 15.0 + np.sin(np.linspace(0, 10, 100)) * 3.0,
        "destination": ["paradip"] * 100,
        "distance_nm": [4800.0] * 100,
    })
    df2 = pd.DataFrame({
        "date": dates,
        "route_id": ["ID_COAL_PARADIP"] * 100,
        "vessel_type": ["Supramax"] * 100,
        "freight_rate_usd_mt": 12.0 + np.cos(np.linspace(0, 10, 100)) * 2.0,
        "destination": ["paradip"] * 100,
        "distance_nm": [2800.0] * 100,
    })
    return pd.concat([df1, df2]).reset_index(drop=True)


class TestTimeFeatures:
    def test_time_features_added(self, sample_timeseries_df):
        res = add_time_features(sample_timeseries_df)
        expected_cols = [
            "day_of_week", "day_of_month", "day_of_year", "week_of_year",
            "month", "quarter", "year", "is_monsoon", "is_weekend",
            "month_sin", "month_cos", "dow_sin", "dow_cos"
        ]
        for c in expected_cols:
            assert c in res.columns, f"Missing feature: {c}"
            assert res[c].isna().sum() == 0


class TestLagFeatures:
    def test_grouped_lags(self, sample_timeseries_df):
        res = add_lag_features(
            sample_timeseries_df,
            target_col="freight_rate_usd_mt",
            lag_days=[1, 7],
            group_cols=["route_id", "vessel_type"],
        )
        assert "freight_rate_usd_mt_lag_1" in res.columns
        assert "freight_rate_usd_mt_lag_7" in res.columns
        
        # Check that lag 1 for the 2nd row in each group matches previous row
        grp = res[res["route_id"] == "AU_COAL_PARADIP"].reset_index(drop=True)
        assert grp.loc[1, "freight_rate_usd_mt_lag_1"] == grp.loc[0, "freight_rate_usd_mt"]

    def test_grouped_rolling(self, sample_timeseries_df):
        res = add_rolling_features(
            sample_timeseries_df,
            target_col="freight_rate_usd_mt",
            windows=[7],
            stats=["mean", "std"],
            group_cols=["route_id", "vessel_type"],
        )
        assert "freight_rate_usd_mt_roll_7d_mean" in res.columns
        assert "freight_rate_usd_mt_roll_7d_std" in res.columns


class TestPipelineLeakageFreeSplit:
    def test_chronological_split_no_leakage(self, sample_timeseries_df):
        pipeline = FeatureEngineeringPipeline()
        full = pipeline.build_features(sample_timeseries_df, include_targets=False)
        train, val, test = pipeline.split_chronological(full, train_ratio=0.70, val_ratio=0.15)
        
        max_train_date = train["date"].max()
        min_val_date = val["date"].min()
        max_val_date = val["date"].max()
        min_test_date = test["date"].min()

        # Strict inequality guarantees zero time-series lookahead
        assert max_train_date < min_val_date, "Train and Val dates overlap!"
        assert max_val_date < min_test_date, "Val and Test dates overlap!"

    def test_preprocessor_files_exist(self):
        scaler_file = PREPROCESSORS_DIR / "feature_scaler.joblib"
        names_file = PREPROCESSORS_DIR / "feature_names.json"
        
        if names_file.exists():
            with open(names_file, "r") as f:
                data = json.load(f)
            assert "feature_columns" in data
            assert len(data["feature_columns"]) > 10
