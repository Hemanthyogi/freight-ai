"""
FreightMind AI — Vessel Selection & Optimization Engine
src/optimization/vessel_optimizer.py

Evaluates vessel classes and candidate fleet vessels for bulk cargo shipments:
  1. Filters by physical feasibility (port draft, LOA, beam, cargo capacity)
  2. Estimates total voyage cost (freight + bunker + port + idle)
  3. Computes a multi-criteria optimization match score (0-100%)
  4. Ranks candidate vessels and produces Recommended, Alternative 1, Alternative 2.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.optimization.cost_calculator import VoyageCostCalculator
from src.optimization.port_feasibility import PortFeasibilityEngine
from src.utils.config import get_all_vessels, get_port_config
from src.utils.logger import logger


@dataclass
class VesselCandidateScore:
    vessel_id: str
    vessel_name: str
    vessel_type: str
    dwt_mt: int
    eta: str
    match_score: int              # 0 - 100
    freight_rate_usd_mt: float
    total_cost_usd: float
    cost_per_mt: float
    risk_level: str               # "LOW", "MED", "HIGH"
    feasible: bool
    reasons: list[str]
    disqualifications: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "vessel_id": self.vessel_id,
            "vessel_name": self.vessel_name,
            "vessel_type": self.vessel_type,
            "dwt_mt": self.dwt_mt,
            "eta": self.eta,
            "match_score": self.match_score,
            "freight_rate_usd_mt": round(self.freight_rate_usd_mt, 2),
            "total_cost_usd": round(self.total_cost_usd, 0),
            "cost_per_mt": round(self.cost_per_mt, 2),
            "risk_level": self.risk_level,
            "feasible": self.feasible,
            "reasons": self.reasons,
            "disqualifications": self.disqualifications,
        }


class VesselOptimizationEngine:
    def __init__(self) -> None:
        self.feasibility_engine = PortFeasibilityEngine()
        self.cost_calculator = VoyageCostCalculator()

    def optimize(
        self,
        cargo_quantity_mt: float,
        origin_port_id: str,
        destination_port_id: str,
        freight_rates_by_type: dict[str, float],  # e.g. {"Panamax": 31.9, "Supramax": 32.4, ...}
        fleet_vessels: list[dict[str, Any]] | None = None,
        voyage_distance_nm: float = 4800.0,
        expected_idle_days: float = 1.5,
    ) -> list[VesselCandidateScore]:
        """
        Evaluate and rank vessels for a specific bulk voyage requirement.
        """
        # Default mock fleet if none provided
        if fleet_vessels is None:
            fleet_vessels = [
                {
                    "vessel_id": "V0006",
                    "vessel_name": "MV Ocean Crest",
                    "vessel_type": "Supramax",
                    "dwt_mt": 58000,
                    "eta": "18 Sep",
                    "risk_level": "LOW",
                },
                {
                    "vessel_id": "V0007",
                    "vessel_name": "MV Eastern Star",
                    "vessel_type": "Supramax",
                    "dwt_mt": 62000,
                    "eta": "21 Sep",
                    "risk_level": "LOW",
                },
                {
                    "vessel_id": "V0008",
                    "vessel_name": "MV Pacific Trader",
                    "vessel_type": "Supramax",
                    "dwt_mt": 55000,
                    "eta": "25 Sep",
                    "risk_level": "MED",
                },
                {
                    "vessel_id": "V0011",
                    "vessel_name": "MV Horizon Pioneer",
                    "vessel_type": "Panamax",
                    "dwt_mt": 75000,
                    "eta": "20 Sep",
                    "risk_level": "LOW",
                },
                {
                    "vessel_id": "V0016",
                    "vessel_name": "MV Iron Giant",
                    "vessel_type": "Capesize",
                    "dwt_mt": 180000,
                    "eta": "24 Sep",
                    "risk_level": "LOW",
                },
                {
                    "vessel_id": "V0001",
                    "vessel_name": "MV Pacific Wind",
                    "vessel_type": "Handysize",
                    "dwt_mt": 28000,
                    "eta": "19 Sep",
                    "risk_level": "LOW",
                },
            ]

        results: list[VesselCandidateScore] = []

        for v in fleet_vessels:
            v_type = v["vessel_type"]
            v_name = v["vessel_name"]
            v_id = v["vessel_id"]
            dwt = v.get("dwt_mt", 50000)
            eta = v.get("eta", "Prompt")
            risk_level = v.get("risk_level", "LOW")

            # Check port feasibility at destination
            feasibility = self.feasibility_engine.check(
                vessel_type=v_type,
                port_id=destination_port_id,
                cargo_quantity_mt=cargo_quantity_mt if cargo_quantity_mt <= dwt else 0.0,
            )

            disqualifications = []
            if not feasibility.feasible:
                for c in feasibility.checks:
                    if not c.passed:
                        disqualifications.append(f"{c.name} constraint failed: {c.message}")

            # Get estimated freight rate
            rate = freight_rates_by_type.get(v_type, 30.0)

            # Calculate transit days
            speed_kn = 14.0
            voyage_days = (voyage_distance_nm / (speed_kn * 24.0)) + 3.0  # +3 port ops days

            # Cost model
            # For multiple voyages or single voyage parcel
            parcel_qty = min(cargo_quantity_mt, float(dwt * 0.95))
            cost_res = self.cost_calculator.calculate(
                vessel_type=v_type,
                route_id=f"{origin_port_id}_{destination_port_id}",
                cargo_quantity_mt=parcel_qty,
                freight_rate_usd_mt=rate,
                voyage_days=voyage_days,
                expected_idle_days=expected_idle_days,
            )

            reasons = []
            score = 70

            if feasibility.feasible:
                score += 15
                reasons.append("Complies with all port draft, LOA, and beam limitations")
            else:
                score -= 40

            # Capacity match
            if dwt * 0.8 <= cargo_quantity_mt <= dwt * 1.05:
                score += 10
                reasons.append("Single-voyage capacity closely matches shipment lot size")
            elif cargo_quantity_mt > dwt:
                reasons.append(f"Suitable for parcel loading / multiple-voyage schedule ({dwt:,} DWT)")

            # Economic efficiency
            if cost_res.total_cost_per_mt < 45.0:
                score += 5
                reasons.append(f"Favorable estimated unit cost of ${cost_res.total_cost_per_mt:.2f}/MT")

            if risk_level == "LOW":
                score += 5
            elif risk_level == "MED":
                score -= 5
            elif risk_level == "HIGH":
                score -= 15

            match_score = max(5, min(98, score))

            results.append(
                VesselCandidateScore(
                    vessel_id=v_id,
                    vessel_name=v_name,
                    vessel_type=v_type,
                    dwt_mt=dwt,
                    eta=eta,
                    match_score=match_score,
                    freight_rate_usd_mt=rate,
                    total_cost_usd=cost_res.total_cost_usd,
                    cost_per_mt=cost_res.total_cost_per_mt,
                    risk_level=risk_level,
                    feasible=feasibility.feasible,
                    reasons=reasons,
                    disqualifications=disqualifications,
                )
            )

        # Sort: feasible first, then descending by match score
        results.sort(key=lambda x: (x.feasible, x.match_score), reverse=True)
        return results
