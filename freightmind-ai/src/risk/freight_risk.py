"""
FreightMind AI — Freight Rate Risk Engine
src/risk/freight_risk.py

Quantifies market risk from price volatility, spike likelihood, and trend divergence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FreightRiskResult:
    score: int                     # 0 - 100
    level: str                     # "LOW", "MEDIUM", "HIGH"
    volatility_annualized: float
    max_drawup_pct_30d: float
    factors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "level": self.level,
            "volatility_annualized": round(self.volatility_annualized, 3),
            "max_drawup_pct_30d": round(self.max_drawup_pct_30d, 1),
            "factors": self.factors,
        }


class FreightRiskEngine:
    def evaluate(
        self,
        volatility_30d: float = 0.05,
        forecast_change_pct: float = 0.0,
        bdi_volatility: float = 0.08,
    ) -> FreightRiskResult:
        factors = []
        score = int(volatility_30d * 400)  # 5% vol -> 20 score

        if forecast_change_pct > 10.0:
            score += 25
            factors.append(f"Steep upward freight rate rally (+{forecast_change_pct:.1f}%) projected")
        elif forecast_change_pct < -10.0:
            score += 15
            factors.append("Downside price volatility indicates unstable market equilibrium")
        else:
            factors.append("Moderate freight price trajectory within historical corridor")

        if bdi_volatility > 0.15:
            score += 20
            factors.append("Elevated Baltic Dry Index volatility spills over into regional fixture rates")

        score = max(5, min(95, score))

        if score <= 33:
            level = "LOW"
        elif score <= 66:
            level = "MEDIUM"
        else:
            level = "HIGH"

        return FreightRiskResult(
            score=score,
            level=level,
            volatility_annualized=volatility_30d * (365 ** 0.5),
            max_drawup_pct_30d=abs(forecast_change_pct),
            factors=factors,
        )
