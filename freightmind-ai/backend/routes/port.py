"""
FreightMind AI — Port Feasibility & Directory Routes
backend/routes/port.py
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException

from backend.schemas.request import PortFeasibilityRequest
from backend.schemas.response import PortFeasibilityResponse
from src.optimization.port_feasibility import PortFeasibilityEngine
from src.utils.config import get_all_ports, get_port_config

router = APIRouter(prefix="/port-feasibility", tags=["Port Feasibility"])

_engine = PortFeasibilityEngine()


@router.post("", response_model=PortFeasibilityResponse)
async def check_port_feasibility(req: PortFeasibilityRequest) -> PortFeasibilityResponse:
    """
    Check physical draft, LOA, beam, and cargo handling constraints at target port.
    """
    try:
        res = _engine.check(
            vessel_type=req.vessel_type,
            port_id=req.port_id,
            cargo_quantity_mt=req.cargo_quantity_mt,
        )
        return PortFeasibilityResponse(
            vessel_type=res.vessel_type,
            port_id=res.port_id,
            port_name=res.port_name,
            feasible=res.feasible,
            cargo_feasible=res.cargo_feasible,
            checks=[
                {
                    "name": c.name,
                    "vessel_value": c.vessel_value,
                    "port_limit": c.port_limit,
                    "passed": c.passed,
                    "status": c.status_label,
                    "message": c.message,
                }
                for c in res.checks
            ],
            warnings=res.warnings,
            summary=res.summary(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ports")
async def list_ports() -> list[dict[str, Any]]:
    """Return all East Coast India port master records."""
    return get_all_ports()
