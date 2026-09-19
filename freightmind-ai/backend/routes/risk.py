"""
FreightMind AI — Risk Analysis Route
backend/routes/risk.py
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException

from backend.schemas.request import RiskAnalysisRequest
from backend.schemas.response import RiskAnalysisResponse
from src.risk.risk_aggregator import RiskAggregatorEngine

router = APIRouter(prefix="/risk-analysis", tags=["Risk Analysis"])

_risk_aggregator = RiskAggregatorEngine()


@router.post("", response_model=RiskAnalysisResponse)
async def analyze_voyage_risk(req: RiskAnalysisRequest) -> RiskAnalysisResponse:
    """
    Compute comprehensive composite 0-100 risk score and categorical breakdown.
    """
    try:
        res = _risk_aggregator.evaluate(
            port_id=req.port_id,
            vessel_type=req.vessel_type,
            forecast_change_pct=req.forecast_change_pct,
            vessels_available_count=req.vessels_available_count,
            month=req.month,
            weather_alert=req.weather_alert,
        )
        return RiskAnalysisResponse(**res.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
