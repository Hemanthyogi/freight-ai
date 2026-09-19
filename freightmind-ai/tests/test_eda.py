"""
FreightMind AI — EDA Engine Tests
tests/test_eda.py
"""

from pathlib import Path
import pytest
import json

from src.analysis.eda import run_eda, load_all_processed_data, compute_summary_statistics


class TestEDA:
    def test_load_all_processed_data(self):
        dfs = load_all_processed_data()
        assert "freight_rates" in dfs
        assert "commodity_prices" in dfs
        assert "market_indicators" in dfs
        assert "port_congestion" in dfs
        assert "vessels_master" in dfs
        assert len(dfs["freight_rates"]) > 1000

    def test_compute_summary_statistics(self):
        dfs = load_all_processed_data()
        summary = compute_summary_statistics(dfs)
        
        assert "overall_freight" in summary
        assert "route_wise" in summary
        assert "vessel_class_economies_of_scale" in summary
        assert "seasonality" in summary
        assert "macro_correlations" in summary
        assert "port_congestion" in summary
        
        assert summary["overall_freight"]["mean_rate_usd_mt"] > 0
        assert summary["seasonality"]["monsoon_discount_pct"] < 0  # Discount during monsoon
