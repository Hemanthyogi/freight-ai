"""
FreightMind AI — Port Congestion Risk Engine
src/risk/congestion_risk.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.risk.idle_time import IdleTimeEngine


@dataclass
class CongestionRiskResult:
    score: int                     # 0 - 100
    level: str                     # "LOW", "MEDIUM", "HIGH"
    expected_wait_hours: float
    factors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "level": self.level,
            "expected_wait_hours": round(self.expected_wait_hours, 1),
            "factors": self.factors,
        }


class CongestionRiskEngine:
    def __init__(self) -> None:
        self.idle_engine = IdleTimeEngine()

    def evaluate(
        self,
        port_id: str,
        month: int = 9,
        vessels_at_anchorage: int | None = None,
        weather_alert: bool = False,
    ) -> CongestionRiskResult:
        idle_est = self.idle_engine.estimate(
            port_id=port_id,
            month=month,
            vessels_at_anchorage=vessels_at_anchorage,
            weather_alert=weather_alert,
        )

        # Scale hours into a 0-100 risk score (72 hrs = 100 max)
        score = int(min(100, (idle_est.expected_idle_hours / 72.0) * 100))
        score = max(5, score)

        if score <= 33:
            level = "LOW"
        elif score <= 66:
            level = "MEDIUM"
        else:
            level = "HIGH"

        return CongestionRiskResult(
            score=score,
            level=level,
            expected_wait_hours=idle_est.expected_idle_hours,
            factors=idle_est.contributing_factors,
        )
