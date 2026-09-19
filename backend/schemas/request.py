"""
FreightMind AI — API Request Schemas
backend/schemas/request.py

Pydantic v2 request models with strict type validation and documentation examples.
"""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    route_id: str = Field(
        default="ID_COAL_PARADIP",
        description="Trade route identifier (e.g. ID_COAL_PARADIP, AU_COAL_PARADIP)",
        examples=["ID_COAL_PARADIP"]
    )
    vessel_type: Literal["Handysize", "Supramax", "Panamax", "Capesize"] = Field(
        default="Supramax",
        description="Vessel class",
        examples=["Supramax"]
    )
    current_rate_override: float | None = Field(
        default=None,
        description="Optional manual spot rate override in $/MT",
        ge=1.0,
        le=150.0
    )


class PortFeasibilityRequest(BaseModel):
    port_id: str = Field(
        default="paradip",
        description="Destination port identifier (e.g. paradip, visakhapatnam, haldia)",
        examples=["paradip"]
    )
    vessel_type: Literal["Handysize", "Supramax", "Panamax", "Capesize"] = Field(
        default="Supramax",
        description="Vessel class to test against port draft/LOA/beam constraints",
        examples=["Supramax"]
    )
    cargo_quantity_mt: float = Field(
        default=55000.0,
        description="Required parcel tonnage to discharge",
        gt=0
    )


class VesselOptimizationRequest(BaseModel):
    origin_country: str = Field(default="Indonesia", examples=["Indonesia"])
    destination_port_id: str = Field(default="paradip", examples=["paradip"])
    commodity: str = Field(default="Iron Ore", examples=["Iron Ore"])
    cargo_quantity_mt: float = Field(default=250000.0, gt=0, examples=[250000.0])
    required_delivery_window: str = Field(default="September - October 2026")


class RiskAnalysisRequest(BaseModel):
    port_id: str = Field(default="paradip", examples=["paradip"])
    vessel_type: str = Field(default="Supramax", examples=["Supramax"])
    forecast_change_pct: float = Field(default=-6.4, examples=[-6.4])
    vessels_available_count: int = Field(default=12, ge=0)
    month: int = Field(default=9, ge=1, le=12)
    weather_alert: bool = Field(default=False)


class MarketEntryRequest(BaseModel):
    current_rate: float = Field(default=35.0, gt=0)
    forecasts: dict[int, float] = Field(
        default={7: 33.5, 14: 31.9, 30: 29.5},
        description="Horizon in days mapped to predicted rate"
    )
    vessels_available_count: int = Field(default=12, ge=0)
    congestion_level: Literal["low", "medium", "high"] = Field(default="low")


class VoyageAnalysisRequest(BaseModel):
    """
    Master unified request matching user inputs on the FreightMind AI dashboard.
    """
    origin: str = Field(default="Indonesia", description="Cargo origin country or port", examples=["Indonesia"])
    destination_port_id: str = Field(default="paradip", description="East Coast India destination port", examples=["paradip"])
    commodity: str = Field(default="Iron Ore", description="Bulk commodity name", examples=["Iron Ore"])
    cargo_quantity_mt: float = Field(default=250000.0, description="Total procurement tonnage", gt=0, examples=[250000.0])
    delivery_window: str = Field(default="September - October 2026", description="Required delivery timeframe")
    procurement_strategy: str = Field(default="Multiple Voyage Charter", description="Contract strategy preference")
    vessel_preference: str | None = Field(default="Supramax", description="Optional preferred vessel class")
