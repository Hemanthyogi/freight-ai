"""
FreightMind AI — Vessel Optimization Route
backend/routes/vessel.py
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException

from backend.schemas.request import VesselOptimizationRequest
from src.optimization.vessel_optimizer import VesselOptimizationEngine
from src.utils.config import get_all_vessels

router = APIRouter(prefix="/vessel-recommendation", tags=["Vessel Optimization"])

_optimizer = VesselOptimizationEngine()


@router.post("")
async def get_vessel_rankings(req: VesselOptimizationRequest) -> list[dict[str, Any]]:
    """
    Rank candidate vessels by physical feasibility, capacity match, total cost, and operational risk.
    """
    try:
        rates = {"Supramax": 31.9, "Panamax": 32.8, "Handysize": 35.0, "Capesize": 29.5}
        results = _optimizer.optimize(
            cargo_quantity_mt=req.cargo_quantity_mt,
            origin_port_id=req.origin_country.lower(),
            destination_port_id=req.destination_port_id.lower(),
            freight_rates_by_type=rates,
        )
        return [r.to_dict() for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fleet")
async def get_fleet_master() -> list[dict[str, Any]]:
    """Return all standard vessel class definitions."""
    return get_all_vessels()
