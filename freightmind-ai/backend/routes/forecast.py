"""
FreightMind AI — Freight Forecasting Route
backend/routes/forecast.py
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException

from backend.schemas.request import ForecastRequest
from src.forecasting.predictor import FreightPredictorService
from src.utils.logger import logger

router = APIRouter(prefix="/forecast", tags=["Freight Forecasting"])

_predictor = FreightPredictorService()


@router.post("")
async def get_freight_forecast(req: ForecastRequest) -> dict[str, Any]:
    """
    Generate multi-horizon freight rate forecast with calibrated 80% prediction intervals.
    """
    try:
        res = _predictor.predict(
            route_id=req.route_id,
            vessel_type=req.vessel_type,
            current_rate_override=req.current_rate_override,
        )
        return res.to_dict()
    except Exception as e:
        logger.error(f"Forecasting error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
