import pytest
from backend.services.live_data_engine import LiveDataEngine
from backend.services.weather_service import WeatherService
from backend.services.rates_service import RatesService
from backend.services.ai_suggestion_engine import AISuggestionEngine
from backend.services.diversion_engine import DiversionEngine


class TestLiveOperations:
    def test_live_engine_singleton(self):
        engine1 = LiveDataEngine()
        engine2 = LiveDataEngine()
        assert engine1 is engine2

    def test_live_engine_state_structure(self):
        engine = LiveDataEngine()
        state = engine.get_live_state()
        assert "freight_rates" in state
        assert "weather_alerts" in state
        assert "port_status" in state
        assert "ai_suggestions" in state
        assert "hire_rates" in state
        assert state["freight_rates"]["bdi"] > 0

    def test_weather_service_refresh(self):
        wx = WeatherService()
        result = wx.refresh()
        assert "alerts" in result
        assert result["severity"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert result["rate_adjustment_pct"] >= 0.0

    def test_rates_service_refresh(self):
        rs = RatesService()
        rates, hire_rates = rs.refresh(weather_adjustment_pct=5.0)
        assert rates["bdi"] > 500
        assert "Supramax" in rates["rates_by_class"]
        assert rates["rates_by_class"]["Supramax"]["rate_usd_mt"] > 0
        assert "Supramax" in hire_rates
        assert hire_rates["Supramax"]["day_rate_usd"] > 0

    def test_ai_suggestion_engine(self):
        engine = AISuggestionEngine()
        rates = {
            "bdi": 1950,
            "bdi_change_pct": 3.5,
            "bdi_trend": "rising",
            "rates_by_class": {"Supramax": {"rate_usd_mt": 10.5, "change_pct": 2.1}},
            "weather_adjustment_pct": 12.0
        }
        weather_alerts = [{
            "type": "CYCLONE",
            "name": "Cyclone Test",
            "intensity": "Severe Storm",
            "expected_landfall_hours": 48,
            "rate_impact_pct": 12.0,
            "distance_from_paradip_km": 250
        }]
        port_status = {"paradip": {"status": "OPEN", "congestion": "HIGH", "waiting_hours": 36}}
        hire_rates = {"Supramax": {"day_rate_usd": 12000, "monthly_usd": 360000}}

        suggestions = engine.generate(
            freight_rates=rates,
            weather_alerts=weather_alerts,
            weather_severity="HIGH",
            port_status=port_status,
            hire_rates=hire_rates
        )
        assert len(suggestions) > 0
        severities = [s["severity"] for s in suggestions]
        assert "HIGH" in severities or "CRITICAL" in severities

    def test_diversion_engine(self):
        engine = DiversionEngine()
        result = engine.calculate_diversion(
            vessel_type="Supramax",
            current_lat=14.0,
            current_lon=84.0,
            emergency_type="engine_fault",
            original_destination="paradip"
        )
        assert "recommended_diversion_port" in result
        assert result["recommended_diversion_port"]["distance_nm"] > 0
        assert result["cost_impact"]["total_extra_cost_usd"] > 0
        assert len(result["recommendations"]) > 0
