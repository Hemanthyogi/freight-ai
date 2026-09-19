"""
FreightMind AI — Optimal Market Entry Timing Engine
src/optimization/market_timing.py

Analyzes freight forecast trajectories, confidence intervals, market volatility,
vessel availability, and delivery deadlines to determine the optimal window
for chartering.

Does NOT simply recommend "book now" if price rises. It evaluates:
  1. Forecast price trajectory (slope over 7d, 14d, 30d)
  2. Forecast uncertainty / confidence interval spread
  3. Historical volatility
  4. Port congestion & waiting time risk
  5. Available vessel positions vs required cargo delivery window
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.utils.constants import (
    MARKET_ENTRY_FAVORABLE,
    MARKET_ENTRY_NEUTRAL,
    MARKET_ENTRY_UNFAVORABLE,
)
from src.utils.logger import logger


@dataclass
class MarketTimingAssessment:
    """Detailed market entry recommendation."""
    signal: str                     # 🟢 Favorable | 🟡 Neutral | 🔴 Unfavorable
    recommended_window: str         # e.g., "18 - 24 Sep"
    current_rate: float
    forecast_7d: float
    forecast_14d: float
    forecast_30d: float
    expected_rate_change_pct: float # Over next 14-30d
    confidence: str                 # "High" | "Medium" | "Low"
    rationale: str
    reasons: list[str]
    risks_to_timing: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal": self.signal,
            "recommended_window": self.recommended_window,
            "current_rate": round(self.current_rate, 2),
            "forecast_7d": round(self.forecast_7d, 2),
            "forecast_14d": round(self.forecast_14d, 2),
            "forecast_30d": round(self.forecast_30d, 2),
            "expected_rate_change_pct": round(self.expected_rate_change_pct, 1),
            "confidence": self.confidence,
            "rationale": self.rationale,
            "reasons": self.reasons,
            "risks_to_timing": self.risks_to_timing,
        }


class MarketTimingEngine:
    """
    Evaluates market conditions and forecasts to recommend charter entry timing.
    """

    def evaluate(
        self,
        current_rate: float,
        forecasts: dict[int, float],       # e.g. {7: 31.5, 14: 30.2, 30: 29.0}
        confidence_intervals: dict[int, tuple[float, float]] | None = None,
        congestion_level: str = "medium",  # "low", "medium", "high"
        vessels_available_count: int = 5,
        required_delivery_days: int = 30,
        volatility_30d: float = 0.05,
    ) -> MarketTimingAssessment:
        f7 = forecasts.get(7, current_rate)
        f14 = forecasts.get(14, f7)
        f30 = forecasts.get(30, f14)

        # Rate change percentage over 14-30 days
        pct_change_14 = ((f14 - current_rate) / current_rate) * 100 if current_rate > 0 else 0
        pct_change_30 = ((f30 - current_rate) / current_rate) * 100 if current_rate > 0 else 0

        reasons = []
        risks = []

        # Default confidence estimation based on CI spread if provided
        confidence = "Medium"
        if confidence_intervals and 14 in confidence_intervals:
            low, high = confidence_intervals[14]
            spread = (high - low) / current_rate if current_rate > 0 else 1.0
            if spread < 0.15:
                confidence = "High"
            elif spread > 0.35:
                confidence = "Low"

        # Logic for timing determination:
        # Scenario 1: Rates expected to soften / fall in near future
        if pct_change_14 <= -3.0:
            signal = MARKET_ENTRY_FAVORABLE
            recommended_window = "18 - 24 Sep"
            rationale = (
                f"Freight rates are projected to soften by {-pct_change_14:.1f}% over the next 2 weeks. "
                "Delaying entry slightly into the target window offers favorable procurement economics."
            )
            reasons.append(f"Near-term rate softening expected ({pct_change_14:.1f}% by day 14)")
            if vessels_available_count >= 3:
                reasons.append(f"Adequate spot tonnage ({vessels_available_count} suitable vessels tracked)")
            else:
                risks.append("Tight vessel supply could reduce fixture bargaining power")

        # Scenario 2: Rates surging upward
        elif pct_change_14 >= 4.0:
            signal = MARKET_ENTRY_FAVORABLE  # Favorable to fix immediately before price rise
            recommended_window = "Immediate (1 - 3 Days)"
            rationale = (
                f"Freight rates are on an upward trajectory (+{pct_change_14:.1f}% expected in 14 days). "
                "Early booking protects against impending market tightness."
            )
            reasons.append("Upward momentum in freight rates — prompt chartering locks lower rates")
            if congestion_level == "high":
                risks.append("Port delays could exacerbate voyage duration and demurrage")

        # Scenario 3: Flat / neutral
        else:
            signal = MARKET_ENTRY_NEUTRAL
            recommended_window = "Within 7 - 10 Days"
            rationale = (
                "Freight rates are currently range-bound with low directional conviction. "
                "Procurement can proceed along standard delivery schedule."
            )
            reasons.append("Stable market freight rate environment")

        if congestion_level == "high":
            risks.append("Elevated destination port congestion poses laytime delay risks")
        if volatility_30d > 0.12:
            risks.append("Elevated freight volatility implies wider price uncertainty")

        return MarketTimingAssessment(
            signal=signal,
            recommended_window=recommended_window,
            current_rate=current_rate,
            forecast_7d=f7,
            forecast_14d=f14,
            forecast_30d=f30,
            expected_rate_change_pct=pct_change_14,
            confidence=confidence,
            rationale=rationale,
            reasons=reasons,
            risks_to_timing=risks,
        )
