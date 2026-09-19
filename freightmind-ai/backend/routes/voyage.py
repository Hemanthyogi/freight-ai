"""
FreightMind AI — Master Voyage Analysis Routes
backend/routes/voyage.py
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas.request import VoyageAnalysisRequest
from backend.schemas.response import MasterDashboardResponse
from backend.services.orchestrator import VoyageOrchestratorService
from src.utils.logger import logger

router = APIRouter(prefix="/voyage-analysis", tags=["Voyage Analysis"])

_orchestrator = VoyageOrchestratorService()


@router.post("", response_model=MasterDashboardResponse)
async def analyze_custom_voyage(request: VoyageAnalysisRequest) -> MasterDashboardResponse:
    """
    Execute full multi-engine voyage evaluation based on user inputs.
    """
    try:
        return _orchestrator.analyze_voyage(request)
    except Exception as e:
        logger.error(f"Error executing voyage analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Voyage analysis failed: {str(e)}")


@router.get("/default", response_model=MasterDashboardResponse)
async def get_default_voyage_scenario() -> MasterDashboardResponse:
    """
    Return the default Smart India Hackathon 2026 demonstration scenario:
    Origin: Indonesia, Destination: Paradip, Commodity: Iron Ore, Qty: 250,000 MT.
    """
    default_req = VoyageAnalysisRequest(
        origin="Indonesia",
        destination_port_id="paradip",
        commodity="Iron Ore",
        cargo_quantity_mt=250000.0,
        delivery_window="September - October 2026",
        procurement_strategy="Multiple Voyage Charter",
        vessel_preference="Supramax",
    )
    return _orchestrator.analyze_voyage(default_req)
