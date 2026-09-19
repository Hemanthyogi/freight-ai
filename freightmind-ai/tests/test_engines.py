"""
FreightMind AI — Decision Engine Tests
tests/test_engines.py

Tests for:
  - Port Feasibility Engine (draft, LOA, beam, cargo capacity)
  - Voyage Cost Calculator
  - Market Timing Engine
  - Vessel Optimization Engine
  - Risk Aggregator Engine
  - Contract Strategy Engine
  - Master Recommendation Engine
"""

import pytest
from src.optimization.port_feasibility import PortFeasibilityEngine
from src.optimization.cost_calculator import VoyageCostCalculator
from src.optimization.market_timing import MarketTimingEngine
from src.optimization.vessel_optimizer import VesselOptimizationEngine
from src.risk.idle_time import IdleTimeEngine
from src.risk.risk_aggregator import RiskAggregatorEngine
from src.recommendations.contract_strategy import ContractStrategyEngine
from src.recommendations.recommender import MasterRecommendationEngine


class TestPortFeasibility:
    def setup_method(self):
        self.engine = PortFeasibilityEngine()

    def test_panamax_feasible_at_paradip(self):
        # Paradip max draft is 17.0m; Panamax draft is 14.0m -> Pass
        res = self.engine.check("Panamax", "paradip")
        assert res.feasible is True

    def test_capesize_infeasible_at_haldia(self):
        # Haldia max draft is 9.5m; Capesize draft is 18.0m -> Fail
        res = self.engine.check("Capesize", "haldia")
        assert res.feasible is False
        failed = [c.name for c in res.checks if not c.passed]
        assert "Draft" in failed

    def test_supramax_feasible_at_vizag(self):
        res = self.engine.check("Supramax", "visakhapatnam")
        assert res.feasible is True


class TestCostCalculator:
    def setup_method(self):
        self.calc = VoyageCostCalculator()

    def test_voyage_cost_positive(self):
        cost = self.calc.calculate(
            vessel_type="Supramax",
            route_id="AU_COAL_PARADIP",
            cargo_quantity_mt=55000,
            freight_rate_usd_mt=32.0,
            voyage_days=18.0,
            expected_idle_days=1.5,
        )
        assert cost.total_cost_usd > 1000000
        assert cost.total_cost_per_mt > 20.0
        assert cost.is_estimate is True


class TestMarketTiming:
    def setup_method(self):
        self.engine = MarketTimingEngine()

    def test_favorable_when_rates_soften(self):
        # Current 35, 14d forecast 31.5 (-10% drop)
        res = self.engine.evaluate(
            current_rate=35.0,
            forecasts={7: 33.0, 14: 31.5, 30: 30.0},
            vessels_available_count=8,
        )
        assert "Favorable" in res.signal


class TestRiskAggregator:
    def setup_method(self):
        self.aggregator = RiskAggregatorEngine()

    def test_composite_risk_score_range(self):
        score = self.aggregator.evaluate(
            port_id="paradip",
            vessel_type="Supramax",
            forecast_change_pct=-6.4,
            vessels_available_count=12,
        )
        assert 0 <= score.total_score <= 100
        assert score.level_label in ["LOW", "LOW – MEDIUM", "MEDIUM", "HIGH"]


class TestRecommendationSynthesis:
    def setup_method(self):
        self.recommender = MasterRecommendationEngine()

    def test_full_recommendation_output(self):
        rec = self.recommender.generate_recommendation(
            origin_country="indonesia",
            destination_port_id="paradip",
            commodity="coal",
            cargo_quantity_mt=250000,
            current_freight_rate=35.0,
            forecast_7d=33.5,
            forecast_14d=31.9,
            forecast_30d=29.0,
            forecast_change_pct=-6.4,
        )
        assert rec.recommended_action == "CHARTER"
        assert rec.recommended_vessel_type in ["Supramax", "Panamax"]
        assert len(rec.why) >= 3
        assert len(rec.alternatives) >= 1
        assert len(rec.contract_scenarios) == 3
