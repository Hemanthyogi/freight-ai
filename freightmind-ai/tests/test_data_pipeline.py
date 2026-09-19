"""
FreightMind AI — Tests for Data Pipeline
tests/test_data_pipeline.py

Tests cover:
  - Synthetic data generation (shape, dtypes, required columns)
  - DEMO_DATA label presence
  - Validation logic (error detection)
  - Cleaner logic (imputation, deduplication)
  - Loader convenience functions

Run with:
    pytest tests/test_data_pipeline.py -v
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.synthetic_generator import (
    generate_freight_rates,
    generate_commodity_prices,
    generate_market_indicators,
    generate_port_congestion,
    generate_vessels_master,
    RANDOM_SEED,
    START_DATE,
    END_DATE,
)
from src.data.validator import (
    validate_freight_rates,
    validate_commodity_prices,
    validate_port_congestion,
)
from src.data.cleaner import (
    clean_freight_rates,
    clean_commodity_prices,
    clean_port_congestion,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def freight_df():
    return generate_freight_rates()


@pytest.fixture(scope="module")
def commodity_df():
    return generate_commodity_prices()


@pytest.fixture(scope="module")
def market_df():
    return generate_market_indicators()


@pytest.fixture(scope="module")
def congestion_df():
    return generate_port_congestion()


@pytest.fixture(scope="module")
def vessels_df():
    return generate_vessels_master()


# ── Synthetic Generator Tests ─────────────────────────────────────────────────

class TestSyntheticGenerator:
    def test_freight_rates_not_empty(self, freight_df):
        assert len(freight_df) > 1000

    def test_freight_rates_required_columns(self, freight_df):
        required = [
            "date", "route_id", "origin", "destination",
            "cargo_type", "vessel_type", "freight_rate_usd_mt",
            "distance_nm", "data_source", "is_synthetic"
        ]
        for col in required:
            assert col in freight_df.columns, f"Missing column: {col}"

    def test_freight_rates_demo_label(self, freight_df):
        """Every row must be labelled DEMO_DATA."""
        assert (freight_df["data_source"] == "DEMO_DATA").all()
        assert freight_df["is_synthetic"].all()

    def test_freight_rates_no_negative(self, freight_df):
        assert (freight_df["freight_rate_usd_mt"] > 0).all()

    def test_freight_rates_reasonable_range(self, freight_df):
        """Rates should be in a plausible bulk freight range."""
        assert freight_df["freight_rate_usd_mt"].min() > 0.5
        assert freight_df["freight_rate_usd_mt"].max() < 200

    def test_commodity_prices_no_negative(self, commodity_df):
        numeric_cols = commodity_df.select_dtypes(include=np.number).columns
        for col in numeric_cols:
            if col not in ("is_synthetic",):
                assert (commodity_df[col] >= 0).all(), f"Negative values in {col}"

    def test_market_indicators_bdi_range(self, market_df):
        """BDI proxy should stay in a realistic range (200-8000)."""
        assert market_df["bdi_proxy"].min() > 200
        assert market_df["bdi_proxy"].max() < 10000

    def test_port_congestion_seven_ports(self, congestion_df):
        """Should cover all 7 East Coast India ports."""
        assert congestion_df["port_id"].nunique() == 7

    def test_port_congestion_no_negative_wait(self, congestion_df):
        assert (congestion_df["avg_waiting_time_hrs"] >= 0).all()

    def test_vessels_master_four_types(self, vessels_df):
        assert vessels_df["vessel_type"].nunique() == 4

    def test_vessels_master_specs_positive(self, vessels_df):
        for col in ["dwt_mt", "draft_laden_m", "loa_m", "beam_m"]:
            assert (vessels_df[col] > 0).all()

    def test_reproducibility(self):
        """Two calls with same seed must produce identical data."""
        df1 = generate_freight_rates()
        df2 = generate_freight_rates()
        pd.testing.assert_frame_equal(df1, df2)

    def test_date_range(self, freight_df):
        dates = pd.to_datetime(freight_df["date"])
        assert str(dates.min().date()) == START_DATE
        assert str(dates.max().date()) <= END_DATE


# ── Validator Tests ───────────────────────────────────────────────────────────

class TestValidator:
    def test_freight_rates_valid(self, freight_df):
        report = validate_freight_rates(freight_df.copy())
        assert report.is_valid, f"Validation errors: {report.errors}"

    def test_freight_rates_detects_bad_vessel_type(self, freight_df):
        bad_df = freight_df.copy()
        bad_df.loc[0, "vessel_type"] = "GigantaShip9000"
        report = validate_freight_rates(bad_df)
        assert not report.is_valid or len(report.errors) > 0

    def test_freight_rates_detects_negative_rate(self, freight_df):
        bad_df = freight_df.copy()
        bad_df.loc[0, "freight_rate_usd_mt"] = -5.0
        report = validate_freight_rates(bad_df)
        assert len(report.warnings) > 0

    def test_commodity_prices_valid(self, commodity_df):
        report = validate_commodity_prices(commodity_df.copy())
        assert report.is_valid

    def test_port_congestion_valid(self, congestion_df):
        report = validate_port_congestion(congestion_df.copy())
        assert report.is_valid


# ── Cleaner Tests ─────────────────────────────────────────────────────────────

class TestCleaner:
    def test_freight_clean_removes_duplicates(self, freight_df):
        """Duplicate row should be removed."""
        dup_df = pd.concat([freight_df.head(5), freight_df.head(5)])
        cleaned, report = clean_freight_rates(dup_df)
        assert report.duplicates_removed == 5
        assert len(cleaned) == 5

    def test_freight_clean_imputes_nulls(self, freight_df):
        """Null freight rates should be forward-filled."""
        df_with_nulls = freight_df.copy()
        # Introduce 3 nulls in a group
        group_mask = (
            (df_with_nulls["route_id"] == "AU_COAL_PARADIP") &
            (df_with_nulls["vessel_type"] == "Panamax")
        )
        idx = df_with_nulls[group_mask].index[:3]
        df_with_nulls.loc[idx, "freight_rate_usd_mt"] = np.nan

        cleaned, report = clean_freight_rates(df_with_nulls)
        assert cleaned["freight_rate_usd_mt"].isna().sum() == 0

    def test_port_congestion_clips_negatives(self):
        """Negative waiting times should be clipped to 0."""
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=5),
            "port_id": ["paradip"] * 5,
            "avg_waiting_time_hrs": [-10, 5, -2, 30, 0],
            "congestion_level": ["low"] * 5,
        })
        cleaned, report = clean_port_congestion(df)
        assert (cleaned["avg_waiting_time_hrs"] >= 0).all()

    def test_cleaned_freight_has_no_nulls(self, freight_df):
        cleaned, _ = clean_freight_rates(freight_df.copy())
        assert cleaned["freight_rate_usd_mt"].isna().sum() == 0


# ── Edge Cases ────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_freight_df(self):
        """Empty DataFrame should not crash validator."""
        empty = pd.DataFrame(columns=["date", "route_id", "vessel_type",
                                       "freight_rate_usd_mt"])
        report = validate_freight_rates(empty)
        # Should report 0 valid rows, not crash
        assert report.total_rows == 0

    def test_single_row_cleaner(self):
        """Cleaner should handle single-row DataFrames."""
        df = pd.DataFrame({
            "date": ["2024-01-01"],
            "route_id": ["AU_COAL_PARADIP"],
            "vessel_type": ["Panamax"],
            "freight_rate_usd_mt": [15.5],
            "distance_nm": [4800.0],
        })
        cleaned, report = clean_freight_rates(df)
        assert len(cleaned) == 1

    def test_all_nulls_freight_rate(self):
        """All-null freight rate column — should use bfill or remain null."""
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=5),
            "route_id": ["AU_COAL_PARADIP"] * 5,
            "vessel_type": ["Panamax"] * 5,
            "freight_rate_usd_mt": [np.nan] * 5,
            "distance_nm": [4800.0] * 5,
        })
        cleaned, report = clean_freight_rates(df)
        # Can't fill if all nulls — column may remain null but no crash
        assert len(cleaned) == 5
