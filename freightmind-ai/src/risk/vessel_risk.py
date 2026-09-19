"""
FreightMind AI — Vessel Availability Risk Engine
src/risk/vessel_risk.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class VesselRiskResult:
    score: int                     # 0 - 100
    level: str                     # "LOW", "MEDIUM", "HIGH"
    available_vessels_count: int
    factors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "level": self.level,
            "available_vessels_count": self.available_vessels_count,
            "factors": self.factors,
        }


class VesselAvailabilityRiskEngine:
    def evaluate(
        self,
        vessel_type: str,
        available_count: int = 4,
        prompt_days: int = 7,
    ) -> VesselRiskResult:
        factors = []
        if available_count >= 5:
            score = 15
            factors.append(f"Ample spot fleet availability ({available_count} candidate vessels tracked)")
        elif available_count >= 3:
            score = 30
            factors.append(f"Adequate spot tonnage ({available_count} vessels available within window)")
        elif available_count >= 1:
            score = 60
            factors.append(f"Restricted tonnage supply ({available_count} vessel available); fixture urgency recommended")
        else:
            score = 90
            factors.append("No directly suitable vessels available in specified window; ballast positioning needed")

        if prompt_days <= 3:
            score += 15
            factors.append("Tight lead time (<3 days) limits fixture negotiations")

        score = max(5, min(95, score))

        if score <= 33:
            level = "LOW"
        elif score <= 66:
            level = "MEDIUM"
        else:
            level = "HIGH"

        return VesselRiskResult(
            score=score,
            level=level,
            available_vessels_count=available_count,
            factors=factors,
        )
