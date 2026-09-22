"""
FreightMind AI — AI Suggestion Engine
backend/services/ai_suggestion_engine.py

Generates proactive, contextual natural-language AI alert cards
based on the current live state:

  - Market timing alerts (lock charter / wait)
  - Weather impact warnings (rate surge imminent)
  - Vessel availability alerts (tight supply)
  - Port congestion warnings
  - Cost optimisation tips

Each suggestion card has:
  - id, type, severity (CRITICAL / HIGH / MEDIUM / LOW / INFO)
  - title, message
  - action_label, action (optional CTA)
  - generated_at

Called after each WeatherService + RatesService refresh.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from src.utils.logger import logger


class AISuggestionEngine:
    """
    Reads latest live state and produces a ranked list of AI suggestion cards.
    """

    def generate(
        self,
        freight_rates: dict[str, Any],
        weather_alerts: list[dict],
        weather_severity: str,
        port_status: dict[str, Any],
        hire_rates: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Generate a ranked list of AI suggestion cards based on current live state.
        Returns at most 6 cards, sorted by severity.
        """
        cards: list[dict[str, Any]] = []

        # 1. Weather-driven rate surge warning
        if weather_severity in ("HIGH", "CRITICAL"):
            cyclone = next((a for a in weather_alerts if a["type"] == "CYCLONE"), None)
            if cyclone:
                hours = cyclone.get("expected_landfall_hours", 48)
                rate_impact = cyclone.get("rate_impact_pct", 12)
                cards.append(self._card(
                    severity="CRITICAL" if weather_severity == "CRITICAL" else "HIGH",
                    title=f"🌀 {cyclone['name']} — Rate Surge Risk",
                    message=(
                        f"{cyclone['name']} ({cyclone['intensity']}) is {cyclone.get('distance_from_paradip_km',200)}km "
                        f"from Paradip with expected landfall in ~{hours}h. "
                        f"Freight rates may spike +{rate_impact:.0f}%. "
                        "Consider locking your charter today to protect against surge pricing."
                    ),
                    action_label="Lock Charter Now",
                    action="open_booking",
                ))

        elif weather_severity == "MEDIUM":
            weather_adj = freight_rates.get("weather_adjustment_pct", 0)
            if weather_adj > 0:
                cards.append(self._card(
                    severity="MEDIUM",
                    title="⛈️ Adverse Weather — Rate Pressure Building",
                    message=(
                        f"Active weather system is applying +{weather_adj:.1f}% pressure on freight rates. "
                        "Monitor conditions closely. Consider prompt charter if cargo delivery window is firm."
                    ),
                    action_label="View Weather Details",
                    action="open_weather",
                ))

        # 2. BDI market signal
        bdi = freight_rates.get("bdi", 1842)
        bdi_change = freight_rates.get("bdi_change_pct", 0)
        bdi_trend = freight_rates.get("bdi_trend", "stable")

        if bdi_change >= 3.0:
            cards.append(self._card(
                severity="HIGH",
                title="📈 BDI Rising Fast — Lock Charter Before Rate Spike",
                message=(
                    f"Baltic Dry Index surged +{bdi_change:.1f}% to {bdi:.0f} points. "
                    "Rates are trending sharply upward. "
                    "Booking immediately will save an estimated 5–12% vs waiting."
                ),
                action_label="Book Now",
                action="open_booking",
            ))
        elif bdi_change <= -2.5:
            cards.append(self._card(
                severity="INFO",
                title="📉 BDI Falling — Favorable Spot Window Opening",
                message=(
                    f"BDI dropped {abs(bdi_change):.1f}% to {bdi:.0f} today. "
                    "Spot freight rates are softening. "
                    "This is a favorable window to lock in a competitive charter rate."
                ),
                action_label="View Rates",
                action="view_rates",
            ))
        elif bdi_trend == "stable" and weather_severity == "LOW":
            cards.append(self._card(
                severity="INFO",
                title="✅ Market Conditions Stable",
                message=(
                    f"BDI is holding at {bdi:.0f} with low directional volatility. "
                    "Standard procurement timeline recommended. "
                    "No immediate market trigger to accelerate or delay charter."
                ),
                action_label=None,
                action=None,
            ))

        # 3. Port congestion warnings
        paradip_status = port_status.get("paradip", {})
        haldia_status = port_status.get("haldia", {})

        if paradip_status.get("congestion") == "HIGH":
            wait = paradip_status.get("waiting_hours", 36)
            cards.append(self._card(
                severity="HIGH",
                title="⚓ Paradip Port Congested — Laytime Risk",
                message=(
                    f"Paradip Port is reporting HIGH congestion with estimated waiting time of {wait}h. "
                    "Consider switching destination to Visakhapatnam or Ennore "
                    "to avoid demurrage charges of ~$15,000/day."
                ),
                action_label="Check Alternate Ports",
                action="open_port_feasibility",
            ))
        elif haldia_status.get("status") == "CLOSED":
            cards.append(self._card(
                severity="HIGH",
                title="🚫 Haldia Port Closed",
                message=(
                    "Haldia Port is currently CLOSED due to weather/operational restrictions. "
                    "Reroute cargo to Paradip or Kolkata alternatives."
                ),
                action_label="Find Alternate Port",
                action="open_diversion",
            ))
        elif paradip_status.get("congestion") == "MEDIUM":
            wait = paradip_status.get("waiting_hours", 24)
            cards.append(self._card(
                severity="MEDIUM",
                title="🕐 Paradip — Moderate Congestion Advisory",
                message=(
                    f"Paradip Port shows medium congestion. Estimated waiting: {wait}h. "
                    "Build waiting time into voyage schedule to avoid demurrage."
                ),
                action_label=None,
                action=None,
            ))

        # 4. Supramax rate change tip
        supramax_rate = freight_rates.get("rates_by_class", {}).get("Supramax", {})
        rate_val = supramax_rate.get("rate_usd_mt", 9.9)
        rate_change = supramax_rate.get("change_pct", 0)
        if rate_val < 9.0:
            cards.append(self._card(
                severity="INFO",
                title="💰 Supramax Rates Below Average — Opportunity",
                message=(
                    f"Supramax freight rate is at ${rate_val:.2f}/MT, "
                    "below the 12-month average of $9.90/MT. "
                    "This is an optimal window for spot or short-term time charter."
                ),
                action_label="Calculate Cost",
                action="open_booking",
            ))
        elif rate_val > 12.0:
            cards.append(self._card(
                severity="MEDIUM",
                title="⚠️ Supramax Rates Elevated",
                message=(
                    f"Supramax freight rate has reached ${rate_val:.2f}/MT. "
                    "Consider whether Panamax or Handysize tonnage can service this cargo "
                    "more cost-effectively."
                ),
                action_label="Compare Vessels",
                action="open_vessel_matching",
            ))

        # Limit and sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3, "LOW": 4}
        cards.sort(key=lambda c: severity_order.get(c["severity"], 5))
        result = cards[:6]

        logger.info(f"[AI Suggestions] Generated {len(result)} suggestion cards.")
        return result

    def _card(
        self,
        severity: str,
        title: str,
        message: str,
        action_label: str | None = None,
        action: str | None = None,
    ) -> dict[str, Any]:
        return {
            "id": f"sug_{uuid.uuid4().hex[:8]}",
            "type": self._type_from_severity(severity),
            "severity": severity,
            "title": title,
            "message": message,
            "action_label": action_label,
            "action": action,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _type_from_severity(self, severity: str) -> str:
        return {
            "CRITICAL": "ALERT",
            "HIGH": "WARNING",
            "MEDIUM": "CAUTION",
            "INFO": "INSIGHT",
            "LOW": "INFO",
        }.get(severity, "INFO")


# Module-level singleton
ai_suggestion_engine = AISuggestionEngine()
