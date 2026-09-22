"""
FreightMind AI — Weather Intelligence Service
backend/services/weather_service.py

Simulates realistic maritime weather events affecting freight routes:
  - Cyclones / Tropical Storms (Bay of Bengal, Arabian Sea)
  - Monsoon intensity (June–September)
  - Port fog events (Haldia, Kolkata)
  - Visibility / sea state at origin ports

Maps severity to:
  - Freight rate adjustment percentage
  - Risk score delta
  - Port waiting time increase

Can be swapped for real OpenWeatherMap / IMD API calls by
replacing _fetch_weather_data() method.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timezone
from typing import Any

from src.utils.logger import logger


# ── Weather event templates ───────────────────────────────────────────────────

_CYCLONE_NAMES = [
    "Asna", "Biparjoy", "Dana", "Fengal", "Hamoon",
    "Michaung", "Remal", "Sitrang", "Tej", "Vayu",
]

_BAY_OF_BENGAL_ZONES = [
    {"name": "Northern Bay of Bengal", "lat": 18.5, "lon": 87.0},
    {"name": "Central Bay of Bengal",  "lat": 12.0, "lon": 88.0},
    {"name": "Paradip Coastal Zone",   "lat": 20.3, "lon": 86.6},
    {"name": "Visakhapatnam Coastal",  "lat": 17.7, "lon": 83.5},
]

_ARABIAN_SEA_ZONES = [
    {"name": "Arabian Sea (NE)",  "lat": 17.0, "lon": 68.5},
    {"name": "Mumbai Coastal",    "lat": 18.9, "lon": 72.8},
    {"name": "Lakshadweep Sea",   "lat": 11.0, "lon": 73.0},
]

# ── Severity → Rate Impact Mapping ───────────────────────────────────────────

_SEVERITY_RATE_IMPACT = {
    "LOW":      0.0,
    "MEDIUM":   5.0,    # +5% freight rate
    "HIGH":     12.0,   # +12%
    "CRITICAL": 22.0,   # +22%
}

_SEVERITY_RISK_DELTA = {
    "LOW":      0,
    "MEDIUM":   10,
    "HIGH":     25,
    "CRITICAL": 40,
}


class WeatherService:
    """
    Generates and maintains live weather event state for maritime routes.
    Uses realistic probabilistic simulation based on seasonal patterns.
    """

    def __init__(self) -> None:
        self._active_events: list[dict[str, Any]] = []
        self._current_severity: str = "LOW"
        self._rate_adjustment_pct: float = 0.0
        self._cycle_count: int = 0

    def refresh(self) -> dict[str, Any]:
        """
        Called by the scheduler every 15 minutes.
        Returns updated weather state.
        """
        self._cycle_count += 1
        month = datetime.now(timezone.utc).month
        self._active_events = self._generate_events(month)
        self._current_severity = self._compute_severity(self._active_events)
        self._rate_adjustment_pct = _SEVERITY_RATE_IMPACT[self._current_severity]

        logger.info(
            f"[Weather] Refresh #{self._cycle_count} — "
            f"severity={self._current_severity}, "
            f"rate_adj=+{self._rate_adjustment_pct:.1f}%, "
            f"events={len(self._active_events)}"
        )

        return {
            "alerts": self._active_events,
            "severity": self._current_severity,
            "rate_adjustment_pct": self._rate_adjustment_pct,
            "risk_delta": _SEVERITY_RISK_DELTA[self._current_severity],
        }

    def _generate_events(self, month: int) -> list[dict[str, Any]]:
        """Generate realistic weather events based on season."""
        events: list[dict[str, Any]] = []

        # Monsoon season (June–September) — higher probability of storms
        monsoon_active = 6 <= month <= 9
        cyclone_season = month in (4, 5, 10, 11, 12)  # Pre/post monsoon

        # Probability thresholds
        storm_prob = 0.30 if monsoon_active else (0.20 if cyclone_season else 0.08)
        fog_prob   = 0.15 if month in (12, 1, 2) else 0.05

        # ── Cyclone / Tropical Storm ──────────────────────────────────────────
        if random.random() < storm_prob:
            zone = random.choice(_BAY_OF_BENGAL_ZONES)
            intensity = random.choice(
                ["Tropical Depression", "Cyclonic Storm", "Severe Cyclonic Storm"]
                if monsoon_active else
                ["Cyclonic Storm", "Severe Cyclonic Storm", "Very Severe Cyclonic Storm"]
            )
            distance_km = random.randint(80, 600)
            wind_kmh = random.randint(55, 180)
            severity = (
                "CRITICAL" if wind_kmh >= 150 else
                "HIGH"     if wind_kmh >= 100 else
                "MEDIUM"
            )
            events.append({
                "id": f"wx_{self._cycle_count}_cyclone",
                "type": "CYCLONE",
                "name": f"Cyclone {random.choice(_CYCLONE_NAMES)}",
                "severity": severity,
                "zone": zone["name"],
                "position": {"lat": zone["lat"] + random.uniform(-2, 2),
                             "lon": zone["lon"] + random.uniform(-2, 2)},
                "wind_speed_kmh": wind_kmh,
                "distance_from_paradip_km": distance_km,
                "expected_landfall_hours": random.randint(18, 96),
                "intensity": intensity,
                "affected_ports": self._affected_ports(distance_km, zone),
                "message": (
                    f"{intensity} in {zone['name']} — {distance_km}km from Paradip. "
                    f"Wind: {wind_kmh} km/h. Expected landfall in ~{random.randint(18,96)}h. "
                    f"Freight rates may surge {_SEVERITY_RATE_IMPACT[severity]:.0f}%."
                ),
                "rate_impact_pct": _SEVERITY_RATE_IMPACT[severity],
                "generated_at": datetime.now(timezone.utc).isoformat(),
            })

        # ── Monsoon Heavy Rain ────────────────────────────────────────────────
        if monsoon_active and random.random() < 0.40:
            events.append({
                "id": f"wx_{self._cycle_count}_monsoon",
                "type": "MONSOON",
                "name": "Bay of Bengal Monsoon",
                "severity": "MEDIUM",
                "zone": "East Coast India",
                "message": (
                    "Active monsoon over Bay of Bengal. Heavy swells (4–6m) expected "
                    "along East Coast India. Port operations may be delayed 12–24h."
                ),
                "rate_impact_pct": 5.0,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            })

        # ── Port Fog (Haldia / Kolkata) ───────────────────────────────────────
        if random.random() < fog_prob:
            events.append({
                "id": f"wx_{self._cycle_count}_fog",
                "type": "FOG",
                "name": "Dense Fog Advisory",
                "severity": "LOW",
                "zone": "Haldia / Kolkata Port Zone",
                "message": (
                    "Dense fog advisory issued for Haldia and Kolkata ports. "
                    "Visibility <200m. Vessel movements restricted 0200–0800 IST."
                ),
                "rate_impact_pct": 0.0,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            })

        # ── High Seas / Swell Warning ────────────────────────────────────────
        if random.random() < 0.20:
            events.append({
                "id": f"wx_{self._cycle_count}_swell",
                "type": "HIGH_SEAS",
                "name": "High Swell Warning",
                "severity": "LOW",
                "zone": "Bay of Bengal Corridor",
                "message": (
                    "High swell warning (3–4m) issued for Bay of Bengal corridor. "
                    "Vessels advised to maintain safe speed. Minor transit delays expected."
                ),
                "rate_impact_pct": 2.0,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            })

        return events

    def _compute_severity(self, events: list[dict]) -> str:
        if not events:
            return "LOW"
        severities = [e["severity"] for e in events]
        if "CRITICAL" in severities:
            return "CRITICAL"
        if "HIGH" in severities:
            return "HIGH"
        if "MEDIUM" in severities:
            return "MEDIUM"
        return "LOW"

    def _affected_ports(self, distance_km: int, zone: dict) -> list[str]:
        ports = []
        if distance_km < 200:
            ports.append("paradip")
        if distance_km < 300:
            ports.append("visakhapatnam")
        if zone["name"] == "Paradip Coastal Zone":
            ports = ["paradip", "haldia"]
        return list(set(ports)) or ["paradip"]

    @property
    def current_severity(self) -> str:
        return self._current_severity

    @property
    def rate_adjustment_pct(self) -> float:
        return self._rate_adjustment_pct

    @property
    def active_events(self) -> list[dict[str, Any]]:
        return self._active_events


# Module-level singleton
weather_service = WeatherService()
