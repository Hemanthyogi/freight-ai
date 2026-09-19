"""
FreightMind AI — Recommendation Route
backend/routes/recommend.py
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.recommendations.recommender import MasterRecommendationEngine

router = APIRouter(prefix="/recommendation", tags=["Charter Recommendation"])

_recommender = MasterRecommendationEngine()


class RecommendationRequest(BaseModel):
    origin: str = Field(default="Indonesia")
    destination_port_id: str = Field(default="paradip")
    commodity: str = Field(default="Iron Ore")
    cargo_quantity_mt: float = Field(default=250000.0)
    current_rate: float = Field(default=35.0)
    forecast_7d: float = Field(default=33.5)
    forecast_14d: float = Field(default=31.9)
    forecast_30d: float = Field(default=29.0)
    forecast_change_pct: float = Field(default=-6.4)


@router.post("")
async def generate_recommendation(req: RecommendationRequest) -> dict[str, Any]:
    """
    Synthesize complete actionable chartering recommendation.
    """
    try:
        rec = _recommender.generate_recommendation(
            origin_country=req.origin,
            destination_port_id=req.destination_port_id,
            commodity=req.commodity,
            cargo_quantity_mt=req.cargo_quantity_mt,
            current_freight_rate=req.current_rate,
            forecast_7d=req.forecast_7d,
            forecast_14d=req.forecast_14d,
            forecast_30d=req.forecast_30d,
            forecast_change_pct=req.forecast_change_pct,
        )
        return rec.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
