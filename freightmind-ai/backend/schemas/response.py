"""
FreightMind AI — API Response Schemas
backend/schemas/response.py

Pydantic v2 response models providing strictly-typed, structured JSON responses
for all analytical engines and the master dashboard.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ConstraintCheckResponse(BaseModel):
    name: str
    vessel_value: float | None
    port_limit: float | None
    passed: bool
    status: str
    message: str


class PortFeasibilityResponse(BaseModel):
    vessel_type: str
    port_id: str
    port_name: str
    feasible: bool
    cargo_feasible: bool
    checks: list[ConstraintCheckResponse]
    warnings: list[str]
    summary: str


class VesselMatchResponse(BaseModel):
    vessel_id: str
    vessel_name: str
    vessel_type: str
    dwt_mt: int
    eta: str
    match_score: int              # 0 - 100%
    freight_rate_usd_mt: float
    total_cost_usd: float
    cost_per_mt: float
    risk_level: str               # "LOW", "MED", "HIGH"
    feasible: bool
    reasons: list[str]
    disqualifications: list[str]


class ContractScenarioResponse(BaseModel):
    scenario_id: str             # "Scenario A", "Scenario B", "Scenario C"
    name: str                    # "Spot Charter", "Recommended", "Delayed Charter"
    badge: str                   # "AI OPTIMAL", ""
    expected_cost_usd: float
    expected_freight_usd_mt: float
    risk_level: str              # "Low", "Medium", "High"
    price_volatility_exposure: str
    operational_flexibility: str
    tonnage_security: str
    pros: list[str]
    cons: list[str]


class MarketTimingResponse(BaseModel):
    signal: str
    recommended_window: str
    current_rate: float
    forecast_7d: float
    forecast_14d: float
    forecast_30d: float
    expected_rate_change_pct: float
    confidence: str
    rationale: str
    reasons: list[str]
    risks_to_timing: list[str]


class RiskAnalysisResponse(BaseModel):
    total_score: int              # e.g. 28
    level_label: str              # "LOW - MEDIUM"
    weather_risk_level: str       # "LOW", "MED", "HIGH"
    key_risk_drivers: list[str]
    mitigation_strategies: list[str]
    freight_risk: dict[str, Any]
    congestion_risk: dict[str, Any]
    vessel_risk: dict[str, Any]


class MasterDashboardResponse(BaseModel):
    """
    Unified payload fueling the FreightMind AI dashboard view.
    """
    # Top KPI Bar
    kpis: dict[str, Any]

    # Forecast Section
    forecast_rate: float
    forecast_change_pct: float
    forecast_chart_historical: list[dict[str, Any]]
    forecast_chart_prediction: list[dict[str, Any]]
    forecast_insight: str
    quote_tagline: str

    # Optimal Voyage Route Map
    voyage_route: dict[str, Any]

    # AI Chartering Recommendation Card
    ai_recommendation: dict[str, Any]

    # Bulk Cargo Requirement Inputs
    cargo_requirement: dict[str, Any]

    # Candidate Vessels
    top_vessel_matches: list[VesselMatchResponse]

    # Contract Scenarios Comparison
    scenario_comparison: list[ContractScenarioResponse]

    # Why this recommendation
    why_recommendation: list[str]

    # Port Feasibility for top vessel
    port_feasibility: PortFeasibilityResponse

    # Metadata
    model_version: str
    data_mode: str               # "DEMO_DATA" or "REAL_DATA"
