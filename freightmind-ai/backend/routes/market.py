"""
FreightMind AI — Market Timing Route
backend/routes/market.py
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas.request import MarketEntryRequest
from backend.schemas.response import MarketTimingResponse
from src.optimization.market_timing import MarketTimingEngine

router = APIRouter(prefix="/market-entry", tags=["Market Entry Timing"])

_engine = MarketTimingEngine()


@router.post("", response_model=MarketTimingResponse)
async def evaluate_market_entry(req: MarketEntryRequest) -> MarketTimingResponse:
    """
    Evaluate optimal chartering window (Favorable / Neutral / Unfavorable).
    """
    try:
        res = _engine.evaluate(
            current_rate=req.current_rate,
            forecasts=req.forecasts,
            vessels_available_count=req.vessels_available_count,
            congestion_level=req.congestion_level,
        )
        return MarketTimingResponse(**res.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
