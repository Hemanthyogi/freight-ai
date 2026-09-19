"""
FreightMind AI — Idle & Waiting Time Estimation Engine
src/risk/idle_time.py

Estimates expected waiting / anchorage idle time for a vessel arriving at a port.
Combines:
  - Destination port baseline congestion
  - Active vessels at anchorage
  - Weather / seasonal conditions (monsoon effect)
  - Berth handling velocity
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.utils.config import get_port_config
from src.utils.logger import logger


@dataclass
class IdleTimeEstimate:
    port_id: str
    port_name: str
    expected_idle_hours: float
    expected_idle_days: float
    congestion_category: str       # "LOW", "MEDIUM", "HIGH"
    risk_level: str                # "🟢 Low", "🟡 Medium", "🔴 High"
    contributing_factors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "port_id": self.port_id,
            "port_name": self.port_name,
            "expected_idle_hours": round(self.expected_idle_hours, 1),
            "expected_idle_days": round(self.expected_idle_days, 2),
            "congestion_category": self.congestion_category,
            "risk_level": self.risk_level,
            "contributing_factors": self.contributing_factors,
        }


class IdleTimeEngine:
    def estimate(
        self,
        port_id: str,
        month: int = 9,
        vessels_at_anchorage: int | None = None,
        weather_alert: bool = False,
    ) -> IdleTimeEstimate:
        port = get_port_config(port_id)
        if not port:
            port_name = port_id.title()
            base_turnaround = 60.0
            baseline = "medium"
        else:
            port_name = port.get("name", port_id)
            base_turnaround = float(port.get("turnaround_time_hrs", 60.0))
            baseline = port.get("congestion_baseline", "medium")

        factors = []
        # Anchorage wait multiplier
        multiplier = 0.5  # Typical waiting is ~50% of port turnaround time

        if baseline == "high":
            multiplier += 0.3
            factors.append("Port historically experiences high berth waiting delays")
        elif baseline == "low":
            multiplier -= 0.1
            factors.append("Port features quick turnaround and modern mechanical handling")

        # Monsoon season (June-September)
        if month in [6, 7, 8, 9]:
            multiplier += 0.2
            factors.append("Monsoon swells and heavy precipitation increase pilotage & cargo handling downtime")

        if vessels_at_anchorage is not None:
            if vessels_at_anchorage > 10:
                multiplier += 0.35
                factors.append(f"Elevated roadstead queue ({vessels_at_anchorage} vessels currently waiting)")
            elif vessels_at_anchorage < 4:
                multiplier -= 0.1
                factors.append("Low anchorage queue observed")

        if weather_alert:
            multiplier += 0.4
            factors.append("Adverse maritime weather advisory active for coastal approach")

        expected_hours = max(4.0, base_turnaround * multiplier)
        expected_days = expected_hours / 24.0

        if expected_hours < 24.0:
            category = "LOW"
            risk = "🟢 Low"
        elif expected_hours < 48.0:
            category = "MEDIUM"
            risk = "🟡 Medium"
        else:
            category = "HIGH"
            risk = "🔴 High"

        return IdleTimeEstimate(
            port_id=port_id,
            port_name=port_name,
            expected_idle_hours=expected_hours,
            expected_idle_days=expected_days,
            congestion_category=category,
            risk_level=risk,
            contributing_factors=factors,
        )
