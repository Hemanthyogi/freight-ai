"""
FreightMind AI — Total Voyage Cost Calculator
src/optimization/cost_calculator.py

Estimates total voyage cost for a given vessel/route combination.

Components:
  1. Freight Cost      = freight_rate (USD/MT) × cargo_quantity (MT)
  2. Bunker/Fuel Cost  = fuel_consumption (MT/day) × voyage_days × fuel_price (USD/MT)
  3. Port Costs        = port_cost_per_call × 2 (origin + destination)
  4. Idle/Waiting Cost = expected_idle_days × (hire_rate_usd/day × idle_factor)
  5. Demurrage/Delay   = estimated demurrage if cargo handling exceeds laytime

IMPORTANT:
  - These are ESTIMATES based on reference specifications, not actual charter quotes.
  - Real costs depend on negotiated rates, specific vessel condition, weather, etc.
  - Always clearly label these as ESTIMATES in the UI.

Output is per voyage (USD total) and per MT (USD/MT) for comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.utils.config import get_app_config, get_vessel_config
from src.utils.logger import logger


@dataclass
class CostBreakdown:
    """Detailed breakdown of estimated voyage cost."""
    vessel_type: str
    route_id: str
    cargo_quantity_mt: float

    # Estimated values
    freight_cost_usd: float = 0.0
    bunker_cost_usd: float = 0.0
    port_cost_usd: float = 0.0
    idle_waiting_cost_usd: float = 0.0
    demurrage_cost_usd: float = 0.0

    # Inputs used (for transparency)
    freight_rate_usd_mt: float = 0.0
    voyage_days: float = 0.0
    idle_days: float = 0.0
    fuel_price_usd_mt: float = 0.0

    # Labels
    is_estimate: bool = True

    @property
    def total_cost_usd(self) -> float:
        return (
            self.freight_cost_usd
            + self.bunker_cost_usd
            + self.port_cost_usd
            + self.idle_waiting_cost_usd
            + self.demurrage_cost_usd
        )

    @property
    def total_cost_per_mt(self) -> float:
        if self.cargo_quantity_mt > 0:
            return self.total_cost_usd / self.cargo_quantity_mt
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "vessel_type": self.vessel_type,
            "route_id": self.route_id,
            "cargo_quantity_mt": self.cargo_quantity_mt,
            "freight_cost_usd": round(self.freight_cost_usd, 0),
            "bunker_cost_usd": round(self.bunker_cost_usd, 0),
            "port_cost_usd": round(self.port_cost_usd, 0),
            "idle_waiting_cost_usd": round(self.idle_waiting_cost_usd, 0),
            "demurrage_cost_usd": round(self.demurrage_cost_usd, 0),
            "total_cost_usd": round(self.total_cost_usd, 0),
            "total_cost_per_mt": round(self.total_cost_per_mt, 2),
            "inputs": {
                "freight_rate_usd_mt": self.freight_rate_usd_mt,
                "voyage_days": self.voyage_days,
                "idle_days": self.idle_days,
                "fuel_price_usd_mt": self.fuel_price_usd_mt,
            },
            "is_estimate": self.is_estimate,
            "disclaimer": (
                "ESTIMATE ONLY — based on reference vessel specifications and "
                "model-predicted rates. Not a charter quote."
            ),
        }


class VoyageCostCalculator:
    """
    Calculates estimated total voyage costs.

    All values clearly labelled as estimates.
    Real charter costs depend on negotiated terms, not just reference specs.
    """

    def __init__(self) -> None:
        cfg = get_app_config()
        cost_cfg = cfg.get("cost_model", {})
        self._fuel_price = cost_cfg.get("bunker", {}).get("price_usd_mt", 580)
        self._idle_factor = cost_cfg.get("waiting_cost_factor", 0.5)
        self._demurrage_rate = cost_cfg.get("demurrage_rate_usd_day", 15000)

    def calculate(
        self,
        vessel_type: str,
        route_id: str,
        cargo_quantity_mt: float,
        freight_rate_usd_mt: float,
        voyage_days: float,
        expected_idle_days: float = 0.0,
        port_handling_days: float | None = None,
        laytime_days: float | None = None,
        fuel_price_override: float | None = None,
    ) -> CostBreakdown:
        """
        Estimate total voyage cost.

        Args:
            vessel_type:          e.g. 'Panamax'
            route_id:             e.g. 'AU_COAL_PARADIP'
            cargo_quantity_mt:    MT of cargo
            freight_rate_usd_mt:  Freight rate (predicted or current)
            voyage_days:          Estimated sailing + port days
            expected_idle_days:   Expected waiting/idle days (from idle engine)
            port_handling_days:   Actual cargo handling days (for demurrage)
            laytime_days:         Allowed free time at port
            fuel_price_override:  Override the config fuel price (USD/MT)

        Returns:
            CostBreakdown with itemised costs.
        """
        vessel = get_vessel_config(vessel_type)
        if vessel is None:
            raise ValueError(f"Unknown vessel type: {vessel_type}")

        fuel_price = fuel_price_override or self._fuel_price

        # 1. Freight cost
        freight_cost = freight_rate_usd_mt * cargo_quantity_mt

        # 2. Bunker cost
        fuel_per_day = vessel["fuel_consumption_mt_day"]
        bunker_cost = fuel_per_day * voyage_days * fuel_price

        # 3. Port cost (origin + destination)
        port_cost = vessel["port_cost_usd_call"] * 2

        # 4. Idle/waiting cost
        #    Assume idle time costs ~50% of daily hire rate (ballast/waiting mode)
        hire_rate = vessel["hire_rate_usd_day_ref"]
        idle_cost = expected_idle_days * hire_rate * self._idle_factor

        # 5. Demurrage/delay cost
        demurrage_cost = 0.0
        if port_handling_days is not None and laytime_days is not None:
            excess_days = max(0.0, port_handling_days - laytime_days)
            demurrage_cost = excess_days * self._demurrage_rate

        breakdown = CostBreakdown(
            vessel_type=vessel_type,
            route_id=route_id,
            cargo_quantity_mt=cargo_quantity_mt,
            freight_cost_usd=freight_cost,
            bunker_cost_usd=bunker_cost,
            port_cost_usd=port_cost,
            idle_waiting_cost_usd=idle_cost,
            demurrage_cost_usd=demurrage_cost,
            freight_rate_usd_mt=freight_rate_usd_mt,
            voyage_days=voyage_days,
            idle_days=expected_idle_days,
            fuel_price_usd_mt=fuel_price,
            is_estimate=True,
        )

        logger.debug(
            f"Cost estimate | {vessel_type} | {route_id} | "
            f"Total: ${breakdown.total_cost_usd:,.0f} "
            f"(${breakdown.total_cost_per_mt:.2f}/MT)"
        )
        return breakdown
