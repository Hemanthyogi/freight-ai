"""
FreightMind AI — Comprehensive Voyage Risk Aggregator
src/risk/risk_aggregator.py

Aggregates individual risk dimensions:
  - Freight Rate Volatility Risk (30%)
  - Port Congestion / Idle Delay Risk (30%)
  - Vessel Supply / Availability Risk (20%)
  - Operational / Maritime Weather Risk (20%)

Yields an overall composite score: 0 to 100
e.g., Score: 28/100 -> LOW - MEDIUM
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.risk.congestion_risk import CongestionRiskEngine, CongestionRiskResult
from src.risk.freight_risk import FreightRiskEngine, FreightRiskResult
from src.risk.vessel_risk import VesselAvailabilityRiskEngine, VesselRiskResult
from src.utils.config import get_app_config
from src.utils.logger import logger


@dataclass
class OverallRiskScore:
    total_score: int               # e.g., 28
    level_label: str               # "LOW - MEDIUM"
    freight_risk: FreightRiskResult
    congestion_risk: CongestionRiskResult
    vessel_risk: VesselRiskResult
    weather_risk_level: str        # "LOW", "MED", "HIGH"
    key_risk_drivers: list[str]
    mitigation_strategies: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_score": self.total_score,
            "level_label": self.level_label,
            "freight_risk": self.freight_risk.to_dict(),
            "congestion_risk": self.congestion_risk.to_dict(),
            "vessel_risk": self.vessel_risk.to_dict(),
            "weather_risk_level": self.weather_risk_level,
            "key_risk_drivers": self.key_risk_drivers,
            "mitigation_strategies": self.mitigation_strategies,
        }


class RiskAggregatorEngine:
    def __init__(self) -> None:
        cfg = get_app_config().get("risk", {})
        self.weights = cfg.get("weights", {
            "freight_risk": 0.30,
            "congestion_risk": 0.30,
            "vessel_availability_risk": 0.20,
            "operational_risk": 0.20,
        })
        self.freight_engine = FreightRiskEngine()
        self.congestion_engine = CongestionRiskEngine()
        self.vessel_engine = VesselAvailabilityRiskEngine()

    def evaluate(
        self,
        port_id: str,
        vessel_type: str,
        volatility_30d: float = 0.05,
        forecast_change_pct: float = -6.4,
        vessels_available_count: int = 5,
        month: int = 9,
        weather_alert: bool = False,
    ) -> OverallRiskScore:
        fr = self.freight_engine.evaluate(
            volatility_30d=volatility_30d,
            forecast_change_pct=forecast_change_pct,
        )
        cr = self.congestion_engine.evaluate(
            port_id=port_id,
            month=month,
            weather_alert=weather_alert,
        )
        vr = self.vessel_engine.evaluate(
            vessel_type=vessel_type,
            available_count=vessels_available_count,
        )

        weather_score = 45 if weather_alert else 15
        weather_level = "MED" if weather_alert else "LOW"

        weighted_sum = (
            fr.score * self.weights.get("freight_risk", 0.30) +
            cr.score * self.weights.get("congestion_risk", 0.30) +
            vr.score * self.weights.get("vessel_availability_risk", 0.20) +
            weather_score * self.weights.get("operational_risk", 0.20)
        )

        final_score = int(round(weighted_sum))
        final_score = max(5, min(95, final_score))

        if final_score <= 25:
            level_label = "LOW"
        elif final_score <= 40:
            level_label = "LOW - MEDIUM"
        elif final_score <= 65:
            level_label = "MEDIUM"
        else:
            level_label = "HIGH"

        drivers = []
        mitigations = []

        if cr.score >= 40:
            drivers.append(f"Destination port wait time ({cr.expected_wait_hours:.0f}h)")
            mitigations.append("Include flexible laytime and standard NOR terms in charter party")
        if fr.score >= 40:
            drivers.append("Short-term freight rate volatility")
            mitigations.append("Secure index-linked bunker adjustment or prompt fixture window")
        if vr.score >= 40:
            drivers.append("Limited immediate prompt tonnage")
            mitigations.append("Engage alternative broker channels for forward positioning")

        if not drivers:
            drivers.append("Favorable operational conditions across voyage parameters")
            mitigations.append("Proceed with regular fixture protocol")

        return OverallRiskScore(
            total_score=final_score,
            level_label=level_label,
            freight_risk=fr,
            congestion_risk=cr,
            vessel_risk=vr,
            weather_risk_level=weather_level,
            key_risk_drivers=drivers,
            mitigation_strategies=mitigations,
        )
