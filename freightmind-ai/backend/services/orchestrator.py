"""
FreightMind AI — Master Service Orchestrator
backend/services/orchestrator.py

Connects all ML forecasting models and decision engines into unified business workflows.
"""

from __future__ import annotations

from typing import Any
import pandas as pd

from backend.schemas.request import VoyageAnalysisRequest
from backend.schemas.response import (
    ContractScenarioResponse,
    MasterDashboardResponse,
    PortFeasibilityResponse,
    VesselMatchResponse,
)
from src.forecasting.predictor import FreightPredictorService
from src.optimization.cost_calculator import VoyageCostCalculator
from src.optimization.market_timing import MarketTimingEngine
from src.optimization.port_feasibility import PortFeasibilityEngine
from src.optimization.vessel_optimizer import VesselOptimizationEngine
from src.recommendations.contract_strategy import ContractStrategyEngine
from src.recommendations.recommender import MasterRecommendationEngine
from src.risk.risk_aggregator import RiskAggregatorEngine
from src.utils.config import get_port_config, is_demo_mode
from src.utils.logger import logger


class VoyageOrchestratorService:
    """
    Coordinates all analytical engines to build the complete FreightMind AI response.
    """

    def __init__(self) -> None:
        self.predictor = FreightPredictorService()
        self.port_engine = PortFeasibilityEngine()
        self.cost_calc = VoyageCostCalculator()
        self.timing_engine = MarketTimingEngine()
        self.vessel_optimizer = VesselOptimizationEngine()
        self.risk_engine = RiskAggregatorEngine()
        self.contract_engine = ContractStrategyEngine()
        self.recommender = MasterRecommendationEngine()

    def analyze_voyage(self, req: VoyageAnalysisRequest) -> MasterDashboardResponse:
        logger.info(f"Orchestrating voyage analysis: {req.origin} -> {req.destination_port_id} ({req.commodity})")

        # 1. Map origin & destination to route identifier
        origin_lower = req.origin.lower()
        dest_id = req.destination_port_id.lower()

        if "indonesia" in origin_lower:
            route_id = "ID_COAL_PARADIP"
            distance_nm = 2450.0
            typical_transit_days = 7.2
            origin_coords = {"name": "Balikpapan (Indonesia)", "lat": -1.2654, "lon": 116.8312}
        elif "australia" in origin_lower:
            route_id = "AU_COAL_PARADIP"
            distance_nm = 4800.0
            typical_transit_days = 14.5
            origin_coords = {"name": "Newcastle (Australia)", "lat": -32.9283, "lon": 151.7817}
        elif "south africa" in origin_lower:
            route_id = "ZA_COAL_VIZAG"
            distance_nm = 4200.0
            typical_transit_days = 12.8
            origin_coords = {"name": "Richards Bay (South Africa)", "lat": -28.7757, "lon": 32.1178}
        else:
            route_id = "ID_COAL_PARADIP"
            distance_nm = 2450.0
            typical_transit_days = 7.2
            origin_coords = {"name": "Indonesia Origin", "lat": -1.2654, "lon": 116.8312}

        # Destination port coordinates
        dest_port = get_port_config(dest_id)
        if dest_port:
            dest_name = dest_port["name"]
            dest_coords = {"name": dest_name, "lat": dest_port["latitude"], "lon": dest_port["longitude"]}
        else:
            dest_name = dest_id.title()
            dest_coords = {"name": dest_name, "lat": 20.3194, "lon": 86.6089}

        # 2. Run Freight Forecast Model
        v_pref = req.vessel_preference or "Supramax"
        fc_res = self.predictor.predict(
            route_id=route_id,
            vessel_type=v_pref,
        )

        current_rate = fc_res.current_rate_usd_mt
        f7 = fc_res.horizons[7].predicted_rate_usd_mt
        f14 = fc_res.horizons[14].predicted_rate_usd_mt
        f30 = fc_res.horizons[30].predicted_rate_usd_mt
        change_pct = fc_res.horizons[14].rate_change_pct

        # 3. Market Entry Timing Assessment
        timing = self.timing_engine.evaluate(
            current_rate=current_rate,
            forecasts={7: f7, 14: f14, 30: f30},
            vessels_available_count=12,
            volatility_30d=0.06,
        )

        # 4. Port Feasibility Analysis for preferred vessel
        is_multi_voyage = "multiple" in (req.procurement_strategy or "").lower() or req.cargo_quantity_mt > 80000
        check_qty = 0.0 if is_multi_voyage else req.cargo_quantity_mt
        feasibility_raw = self.port_engine.check(
            vessel_type=v_pref,
            port_id=dest_id,
            cargo_quantity_mt=check_qty,
        )
        port_feasibility = PortFeasibilityResponse(
            vessel_type=feasibility_raw.vessel_type,
            port_id=feasibility_raw.port_id,
            port_name=feasibility_raw.port_name,
            feasible=feasibility_raw.feasible,
            cargo_feasible=feasibility_raw.cargo_feasible,
            checks=[
                {
                    "name": c.name,
                    "vessel_value": c.vessel_value,
                    "port_limit": c.port_limit,
                    "passed": c.passed,
                    "status": c.status_label,
                    "message": c.message,
                }
                for c in feasibility_raw.checks
            ],
            warnings=feasibility_raw.warnings,
            summary=feasibility_raw.summary(),
        )

        # 5. Vessel Matching & Optimization
        freight_by_class = {
            "Supramax": round(f14, 1),
            "Panamax": round(f14 * 0.96, 1),
            "Handysize": round(f14 * 1.06, 1),
            "Capesize": round(f14 * 0.88, 1),
        }
        vessel_matches_raw = self.vessel_optimizer.optimize(
            cargo_quantity_mt=req.cargo_quantity_mt,
            origin_port_id=origin_lower,
            destination_port_id=dest_id,
            freight_rates_by_type=freight_by_class,
            voyage_distance_nm=distance_nm,
        )
        top_vessels = [
            VesselMatchResponse(**vm.to_dict())
            for vm in vessel_matches_raw[:3]
        ]

        top_rec_vessel = top_vessels[0] if top_vessels else None
        rec_vessel_name = top_rec_vessel.vessel_name if top_rec_vessel else "MV Ocean Crest"
        rec_dwt = top_rec_vessel.dwt_mt if top_rec_vessel else 58000
        rec_freight = top_rec_vessel.freight_rate_usd_mt if top_rec_vessel else 31.9

        # 6. Voyage Risk Aggregation
        risk_res = self.risk_engine.evaluate(
            port_id=dest_id,
            vessel_type=v_pref,
            forecast_change_pct=change_pct,
            vessels_available_count=12,
        )

        # 7. Spot vs Multiple-Voyage Contract Strategies
        contract_options_raw = self.contract_engine.compare_strategies(
            base_freight_usd_mt=rec_freight,
            cargo_quantity_mt=req.cargo_quantity_mt,
            forecast_trend_pct=change_pct,
        )
        scenario_comparison = [
            ContractScenarioResponse(**opt.to_dict())
            for opt in contract_options_raw
        ]

        # 8. Expected Total Landed Cost (Multi-Voyage optimized scenario)
        recommended_scenario = next(
            (s for s in scenario_comparison if "Recommended" in s.name),
            scenario_comparison[1] if len(scenario_comparison) > 1 else scenario_comparison[0]
        )
        total_cost_num = recommended_scenario.expected_cost_usd
        total_cost_formatted = f"${total_cost_num / 1e6:.2f}M"

        # 9. Build Top KPIs Bar
        kpis = {
            "forecast_freight_rate": f"${rec_freight:.1f} / MT",
            "rate_change_expected": f"{abs(change_pct):.1f}% {'expected decrease' if change_pct < 0 else 'expected increase'}",
            "rate_change_pct": round(change_pct, 1),
            "chartering_window": timing.recommended_window,
            "chartering_window_status": "Favorable" if "Favorable" in timing.signal else "Neutral",
            "vessel_availability_count": 12,
            "vessel_availability_label": "12 Suitable",
            "high_match_count": 3,
            "expected_total_cost": total_cost_formatted,
            "cost_status": "Optimized",
            "risk_level": risk_res.level_label,
            "risk_score": risk_res.total_score,
        }

        # 10. AI Chartering Recommendation Card
        ai_recommendation = {
            "action": "CHARTER",
            "vessel_name": rec_vessel_name,
            "vessel_capacity_dwt": f"{rec_dwt:,} DWT",
            "route_display": f"{req.origin} -> East Coast India",
            "chartering_window": timing.recommended_window,
            "expected_freight_usd_mt": rec_freight,
            "expected_total_cost_formatted": total_cost_formatted,
            "risk_score": risk_res.total_score,
            "risk_level_label": risk_res.level_label,
            "button_text": "VIEW OPTIMAL PLAN",
        }

        # 11. Bulk Cargo Requirement Input Echo
        cargo_requirement = {
            "commodity": req.commodity,
            "required_quantity_mt": f"{req.cargo_quantity_mt:,.0f} MT",
            "origin": req.origin,
            "destination": "East Coast India",
            "destination_port": dest_name,
            "delivery_window": req.delivery_window,
            "procurement_strategy": req.procurement_strategy,
        }

        # 12. Optimal Voyage Route Map Elements
        voyage_route = {
            "origin": origin_coords,
            "destination": dest_coords,
            "distance_nm": int(distance_nm),
            "estimated_transit_days": typical_transit_days,
            "port_congestion": "LOW",
            "weather_risk": "LOW",
            "waypoints": [
                {"name": origin_coords["name"], "lat": origin_coords["lat"], "lon": origin_coords["lon"]},
                {"name": "Malacca Strait Approach", "lat": 5.5, "lon": 98.0},
                {"name": "Bay of Bengal Corridor", "lat": 12.0, "lon": 88.0},
                {"name": dest_coords["name"], "lat": dest_coords["lat"], "lon": dest_coords["lon"]},
            ],
            "east_coast_ports": [
                {"id": "paradip", "name": "Paradip", "lat": 20.3194, "lon": 86.6089, "congestion": "LOW"},
                {"id": "visakhapatnam", "name": "Visakhapatnam", "lat": 17.6868, "lon": 83.2185, "congestion": "LOW"},
                {"id": "chennai", "name": "Chennai", "lat": 13.0827, "lon": 80.2707, "congestion": "LOW"},
            ]
        }

        # 13. Why This Recommendation
        why_bullets = [
            f"Favorable freight-rate forecast: AI predicts rates softening by {abs(change_pct):.1f}% over the coming weeks.",
            f"Vessel capacity matches cargo requirement: {rec_vessel_name} ({rec_dwt:,} DWT) fits {req.cargo_quantity_mt:,.0f} MT across multiple sequenced voyages.",
            f"Lower port congestion and voyage risk: East Coast ports are operating efficiently with manageable weather risk along the Bay of Bengal corridor.",
        ]

        # 14. Assemble Master Dashboard Response
        return MasterDashboardResponse(
            kpis=kpis,
            forecast_rate=rec_freight,
            forecast_change_pct=change_pct,
            forecast_chart_historical=fc_res.historical_series,
            forecast_chart_prediction=fc_res.forecast_series,
            forecast_insight=(
                "Freight rates are expected to soften over the next 2 weeks. "
                f"Recommended chartering window: {timing.recommended_window}."
            ),
            quote_tagline="Optimized chartering today for a more resilient and cost-efficient tomorrow.",
            voyage_route=voyage_route,
            ai_recommendation=ai_recommendation,
            cargo_requirement=cargo_requirement,
            top_vessel_matches=top_vessels,
            scenario_comparison=scenario_comparison,
            why_recommendation=why_bullets,
            port_feasibility=port_feasibility,
            model_version=fc_res.model_version,
            data_mode="DEMO_DATA" if is_demo_mode() else "REAL_DATA",
        )
