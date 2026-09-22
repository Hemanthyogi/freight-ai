"""
FreightMind AI — Live Operations API Routes
backend/routes/live.py

Endpoints:
  GET  /api/v1/live/state           Full live dashboard state
  GET  /api/v1/live/weather         Current weather alerts + price impact
  GET  /api/v1/live/suggestions     AI suggestion cards
  GET  /api/v1/live/port-status     Live port open/congested/closed
  GET  /api/v1/live/booking-costs   Real-time hire rates + booking cost calc
  POST /api/v1/live/diversion       Ship emergency → diversion recommendation
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.diversion_engine import diversion_engine
from backend.services.live_data_engine import live_engine
from src.utils.logger import logger

router = APIRouter(prefix="/live", tags=["Live Operations"])


# ── Request models ────────────────────────────────────────────────────────────

class DiversionRequest(BaseModel):
    vessel_type: str = Field("Supramax", description="Vessel class (Supramax, Panamax, etc.)")
    current_lat: float = Field(..., description="Current latitude of vessel")
    current_lon: float = Field(..., description="Current longitude of vessel")
    emergency_type: str = Field(
        ...,
        description="engine_fault | storm_diversion | medical | port_closure | fire | grounding_risk"
    )
    original_destination: str = Field("paradip", description="Original destination port ID")
    cargo_quantity_mt: float = Field(55000.0, description="Cargo on board (MT)")
    speed_knots: float = Field(12.0, description="Current vessel speed (knots)")
    fuel_price_usd_mt: float = Field(620.0, description="Current bunker price (USD/MT)")


class BookingCostRequest(BaseModel):
    vessel_type: str = Field("Supramax")
    cargo_quantity_mt: float = Field(55000.0)
    voyage_distance_nm: float = Field(2450.0)
    voyage_days: float = Field(7.2)
    charter_type: str = Field("voyage", description="voyage | time_charter | coa")


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/state")
async def get_live_state() -> dict[str, Any]:
    """
    Full live dashboard state — freight rates, weather, port status,
    AI suggestions, hire rates. Refreshed every 15 minutes by scheduler.
    """
    return live_engine.get_live_state()


@router.get("/weather")
async def get_weather() -> dict[str, Any]:
    """Current weather alerts with freight rate impact."""
    state = live_engine.get_live_state()
    return {
        "severity": state["weather_severity"],
        "rate_adjustment_pct": state["freight_rates"].get("weather_adjustment_pct", 0),
        "alerts": state["weather_alerts"],
        "last_updated": state["last_updated"],
    }


@router.get("/suggestions")
async def get_suggestions() -> dict[str, Any]:
    """Latest AI suggestion cards sorted by severity."""
    state = live_engine.get_live_state()
    return {
        "suggestions": state["ai_suggestions"],
        "count": len(state["ai_suggestions"]),
        "last_updated": state["last_updated"],
    }


@router.get("/port-status")
async def get_port_status() -> dict[str, Any]:
    """Live port operational status."""
    state = live_engine.get_live_state()
    return {
        "ports": state["port_status"],
        "last_updated": state["last_updated"],
    }


@router.get("/booking-costs")
async def get_booking_costs() -> dict[str, Any]:
    """
    Real-time hire rates and booking cost estimates per vessel class.
    """
    state = live_engine.get_live_state()
    rates = state["freight_rates"]["rates_by_class"]
    hire = state["hire_rates"]
    bunker = state["freight_rates"].get("bunker_prices", {})

    booking_info: dict[str, Any] = {}
    for vessel_type, hire_data in hire.items():
        rate_data = rates.get(vessel_type, {})
        spot_rate = rate_data.get("rate_usd_mt", 9.9)
        tce = rate_data.get("tce_usd_day", 11200)
        day_rate = hire_data["day_rate_usd"]
        monthly = hire_data["monthly_usd"]

        # Example cost breakdown for 55,000 MT cargo, 7.2 day voyage
        example_cargo = 55000
        example_days = 7.2
        fuel_per_day = {"Handysize": 18, "Supramax": 26, "Panamax": 32, "Capesize": 52}.get(vessel_type, 26)
        bunker_price = bunker.get("vlsfo_usd_mt", 620)

        freight_cost = round(spot_rate * example_cargo, 0)
        bunker_cost = round(fuel_per_day * example_days * bunker_price, 0)
        port_cost = round(day_rate * 0.5, 0)  # ~half-day hire as port cost ref
        idle_cost = round(day_rate * 0.5, 0)
        total_cost = round(freight_cost + bunker_cost + port_cost + idle_cost, 0)

        booking_info[vessel_type] = {
            "spot_rate_usd_mt": spot_rate,
            "tce_usd_day": tce,
            "hire_rate_day_usd": day_rate,
            "hire_rate_monthly_usd": monthly,
            "trend": hire_data["trend"],
            "example_cost_breakdown": {
                "cargo_mt": example_cargo,
                "voyage_days": example_days,
                "freight_cost_usd": int(freight_cost),
                "bunker_cost_usd": int(bunker_cost),
                "port_charges_usd": int(port_cost),
                "idle_cost_usd": int(idle_cost),
                "total_voyage_cost_usd": int(total_cost),
                "cost_per_mt_usd": round(total_cost / example_cargo, 2),
            },
            "charter_options": {
                "voyage_charter": {
                    "description": "Single voyage — freight paid per MT of cargo",
                    "rate": f"${spot_rate:.2f}/MT",
                    "total_usd": int(freight_cost),
                    "risk": "Market rate at time of fixture",
                },
                "time_charter_6mo": {
                    "description": "6-month time charter — fixed daily hire",
                    "rate": f"${day_rate:,}/day",
                    "total_usd": int(day_rate * 180),
                    "risk": "Fixed cost, flexible cargo scheduling",
                },
                "coa_3_voyage": {
                    "description": "Contract of Affreightment — 3 consecutive voyages",
                    "rate": f"${spot_rate * 0.97:.2f}/MT (3% discount)",
                    "total_usd": int(spot_rate * 0.97 * example_cargo * 3),
                    "risk": "Volume commitment, rate protection",
                },
            },
        }

    return {
        "booking_costs": booking_info,
        "bunker_prices": bunker,
        "weather_rate_adjustment_pct": state["freight_rates"].get("weather_adjustment_pct", 0),
        "last_updated": state["last_updated"],
    }


@router.post("/diversion")
async def calculate_emergency_diversion(req: DiversionRequest) -> dict[str, Any]:
    """
    Calculate emergency vessel diversion plan.
    Returns: nearest alternate port, extra cost, revised ETA, recommendations.
    """
    valid_types = [
        "engine_fault", "storm_diversion", "medical",
        "port_closure", "fire", "grounding_risk",
    ]
    if req.emergency_type not in valid_types:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid emergency_type. Must be one of: {valid_types}"
        )

    try:
        result = diversion_engine.calculate_diversion(
            vessel_type=req.vessel_type,
            current_lat=req.current_lat,
            current_lon=req.current_lon,
            emergency_type=req.emergency_type,
            original_destination=req.original_destination,
            cargo_quantity_mt=req.cargo_quantity_mt,
            speed_knots=req.speed_knots,
            fuel_price_usd_mt=req.fuel_price_usd_mt,
        )

        # Register the emergency in live state
        live_engine.add_emergency({
            "id": result["emergency_id"],
            "type": req.emergency_type,
            "label": result["emergency_label"],
            "vessel_type": req.vessel_type,
            "diversion_port": result["recommended_diversion_port"]["name"],
            "extra_cost_usd": result["cost_impact"]["total_extra_cost_usd"],
            "status": "ACTIVE",
            "declared_at": result["generated_at"],
        })

        return result

    except Exception as exc:
        logger.error(f"Diversion calculation error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
