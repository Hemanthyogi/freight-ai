"""
FreightMind AI — Live Freight Rates Service
backend/services/rates_service.py

Maintains live freight rates with realistic drift:
  - Baltic Dry Index (BDI) simulation
  - Time Charter Equivalent (TCE) per vessel class
  - Spot freight rate (USD/MT) per vessel class
  - Demand factor (seasonal + weather-driven)
  - Bunker fuel price (VLSFO, IFO380)

Called every 15 minutes by the scheduler.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any

from src.utils.logger import logger


# ── Base reference rates ──────────────────────────────────────────────────────

_BASE_BDI = 1842

_BASE_RATES: dict[str, dict[str, float]] = {
    "Handysize": {"rate_usd_mt": 7.20,  "tce_usd_day": 8500.0},
    "Supramax":  {"rate_usd_mt": 9.90,  "tce_usd_day": 11200.0},
    "Panamax":   {"rate_usd_mt": 9.50,  "tce_usd_day": 14800.0},
    "Capesize":  {"rate_usd_mt": 8.80,  "tce_usd_day": 22000.0},
}

_BASE_BUNKER = {
    "vlsfo_usd_mt": 620.0,   # Very Low Sulphur Fuel Oil
    "ifo380_usd_mt": 510.0,  # IFO 380 (scrubber vessels)
    "mdo_usd_mt": 890.0,     # Marine Diesel Oil
}

# Seasonal demand multipliers (month 1–12)
_SEASONAL_DEMAND = {
    1: 0.95, 2: 0.93, 3: 0.97,
    4: 1.02, 5: 1.05, 6: 1.00,
    7: 0.98, 8: 0.97, 9: 1.03,
    10: 1.06, 11: 1.08, 12: 1.04,
}


class RatesService:
    """
    Maintains live freight rates with realistic random walk drift.
    Applies weather adjustments received from WeatherService.
    """

    def __init__(self) -> None:
        self._bdi = float(_BASE_BDI)
        self._bdi_prev = float(_BASE_BDI)
        self._rates: dict[str, dict[str, float]] = {
            k: {"rate_usd_mt": v["rate_usd_mt"], "tce_usd_day": v["tce_usd_day"]}
            for k, v in _BASE_RATES.items()
        }
        self._bunker = dict(_BASE_BUNKER)
        self._weather_adj: float = 0.0
        self._cycle: int = 0

    def refresh(self, weather_adjustment_pct: float = 0.0) -> dict[str, Any]:
        """
        Update all rates for one scheduler cycle.
        weather_adjustment_pct: additional % from WeatherService (e.g. +12.0)
        Returns full rates payload for LiveDataEngine.
        """
        self._cycle += 1
        self._weather_adj = weather_adjustment_pct
        month = datetime.now(timezone.utc).month
        seasonal = _SEASONAL_DEMAND.get(month, 1.0)

        # BDI random walk (±1.5% per cycle with seasonal bias)
        bdi_drift = random.gauss(mu=seasonal - 1.0, sigma=0.012)
        self._bdi_prev = self._bdi
        self._bdi = max(600, min(4500, self._bdi * (1 + bdi_drift)))

        bdi_change_pct = ((self._bdi - self._bdi_prev) / self._bdi_prev) * 100
        bdi_trend = "rising" if bdi_change_pct > 0.3 else ("falling" if bdi_change_pct < -0.3 else "stable")

        # Update rates per vessel class
        rates_by_class: dict[str, dict] = {}
        for vessel_type, base in _BASE_RATES.items():
            # Individual class drift (±0.8%)
            class_drift = random.gauss(mu=0, sigma=0.008)
            weather_factor = 1.0 + (weather_adjustment_pct / 100.0)
            bdi_ratio = self._bdi / _BASE_BDI

            new_rate_mt = base["rate_usd_mt"] * bdi_ratio * weather_factor * (1 + class_drift)
            new_tce = base["tce_usd_day"] * bdi_ratio * weather_factor * (1 + class_drift)

            new_rate_mt = max(3.0, round(new_rate_mt, 2))
            new_tce = max(2000, round(new_tce, 0))

            # Compute change vs stored
            old_rate = self._rates[vessel_type]["rate_usd_mt"]
            change_pct = ((new_rate_mt - old_rate) / old_rate) * 100

            self._rates[vessel_type] = {"rate_usd_mt": new_rate_mt, "tce_usd_day": new_tce}

            rates_by_class[vessel_type] = {
                "rate_usd_mt": new_rate_mt,
                "tce_usd_day": int(new_tce),
                "change_pct": round(change_pct, 2),
                "trend": "rising" if change_pct > 0.2 else ("falling" if change_pct < -0.2 else "stable"),
            }

        # Bunker price drift (±0.5%)
        for fuel, price in self._bunker.items():
            drift = random.gauss(0, 0.005)
            self._bunker[fuel] = max(200, round(price * (1 + drift), 1))

        # Hire rates (slightly slower drift ±0.3%)
        hire_rates: dict[str, dict] = {}
        for vessel_type, base in _BASE_RATES.items():
            drift = random.gauss(0, 0.003)
            day_rate = round(rates_by_class[vessel_type]["tce_usd_day"] * (1 + drift), 0)
            hire_rates[vessel_type] = {
                "day_rate_usd": int(day_rate),
                "monthly_usd": int(day_rate * 30),
                "trend": rates_by_class[vessel_type]["trend"],
            }

        result = {
            "bdi": round(self._bdi, 0),
            "bdi_change_pct": round(bdi_change_pct, 2),
            "bdi_trend": bdi_trend,
            "rates_by_class": rates_by_class,
            "weather_adjustment_pct": weather_adjustment_pct,
            "demand_factor": round(seasonal, 3),
            "bunker_prices": self._bunker,
        }

        logger.info(
            f"[Rates] Cycle #{self._cycle} — BDI={self._bdi:.0f} ({bdi_change_pct:+.2f}%), "
            f"Supramax={rates_by_class['Supramax']['rate_usd_mt']:.2f} USD/MT"
        )
        return result, hire_rates


# Module-level singleton
rates_service = RatesService()
