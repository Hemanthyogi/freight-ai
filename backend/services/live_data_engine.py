"""
FreightMind AI — Live Data Engine (Central State Store)
backend/services/live_data_engine.py

Thread-safe singleton holding the latest live state:
  - Current freight rates (BDI, TCE per vessel class)
  - Active weather alerts (cyclones, monsoons, fog)
  - Port live status (open / congested / closed)
  - AI suggestion cards
  - Active voyage emergencies

Updated every 15 minutes by the APScheduler background job.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any


class LiveDataEngine:
    """
    Thread-safe singleton that stores the latest live operational state.
    All other services write INTO this engine; the API reads FROM it.
    """

    _instance: "LiveDataEngine | None" = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "LiveDataEngine":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._data_lock = threading.RLock()
        self._state: dict[str, Any] = self._default_state()
        self._initialized = True

    # ── Default / Bootstrap State ─────────────────────────────────────────────

    def _default_state(self) -> dict[str, Any]:
        return {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "next_update_in_seconds": 900,
            # Live freight rates
            "freight_rates": {
                "bdi": 1842,
                "bdi_change_pct": 0.0,
                "bdi_trend": "stable",
                "rates_by_class": {
                    "Handysize": {"rate_usd_mt": 7.2, "tce_usd_day": 8500,  "change_pct": 0.0},
                    "Supramax":  {"rate_usd_mt": 9.9, "tce_usd_day": 11200, "change_pct": 0.0},
                    "Panamax":   {"rate_usd_mt": 9.5, "tce_usd_day": 14800, "change_pct": 0.0},
                    "Capesize":  {"rate_usd_mt": 8.8, "tce_usd_day": 22000, "change_pct": 0.0},
                },
                "weather_adjustment_pct": 0.0,
                "demand_factor": 1.0,
            },
            # Weather alerts
            "weather_alerts": [],
            "weather_severity": "LOW",   # LOW | MEDIUM | HIGH | CRITICAL
            # Port live status
            "port_status": {
                "paradip":       {"status": "OPEN",      "congestion": "LOW",    "waiting_hours": 18},
                "visakhapatnam": {"status": "OPEN",      "congestion": "LOW",    "waiting_hours": 12},
                "haldia":        {"status": "CONGESTED", "congestion": "MEDIUM", "waiting_hours": 36},
                "chennai":       {"status": "OPEN",      "congestion": "LOW",    "waiting_hours": 14},
                "ennore":        {"status": "OPEN",      "congestion": "LOW",    "waiting_hours": 10},
            },
            # AI suggestion cards
            "ai_suggestions": [
                {
                    "id": "sug_001",
                    "type": "INFO",
                    "severity": "LOW",
                    "title": "Market Conditions Stable",
                    "message": "BDI is ranging at 1,842 with low volatility. Standard chartering timeline applies.",
                    "action_label": None,
                    "action": None,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            # Active voyage emergencies
            "active_emergencies": [],
            # Hire rates (per vessel class, per day)
            "hire_rates": {
                "Handysize": {"day_rate_usd": 8500,  "monthly_usd": 255000, "trend": "stable"},
                "Supramax":  {"day_rate_usd": 11200, "monthly_usd": 336000, "trend": "rising"},
                "Panamax":   {"day_rate_usd": 14800, "monthly_usd": 444000, "trend": "stable"},
                "Capesize":  {"day_rate_usd": 22000, "monthly_usd": 660000, "trend": "falling"},
            },
        }

    # ── Read / Write ──────────────────────────────────────────────────────────

    def get_live_state(self) -> dict[str, Any]:
        with self._data_lock:
            import copy
            return copy.deepcopy(self._state)

    def update(self, updates: dict[str, Any]) -> None:
        """Merge top-level keys into the state."""
        with self._data_lock:
            self._state.update(updates)
            self._state["last_updated"] = datetime.now(timezone.utc).isoformat()

    def update_freight_rates(self, rates: dict[str, Any]) -> None:
        with self._data_lock:
            self._state["freight_rates"].update(rates)
            self._state["last_updated"] = datetime.now(timezone.utc).isoformat()

    def update_weather(self, alerts: list[dict], severity: str, rate_adj_pct: float) -> None:
        with self._data_lock:
            self._state["weather_alerts"] = alerts
            self._state["weather_severity"] = severity
            self._state["freight_rates"]["weather_adjustment_pct"] = rate_adj_pct
            self._state["last_updated"] = datetime.now(timezone.utc).isoformat()

    def update_port_status(self, port_id: str, status: dict[str, Any]) -> None:
        with self._data_lock:
            self._state["port_status"][port_id] = status
            self._state["last_updated"] = datetime.now(timezone.utc).isoformat()

    def set_ai_suggestions(self, suggestions: list[dict[str, Any]]) -> None:
        with self._data_lock:
            self._state["ai_suggestions"] = suggestions
            self._state["last_updated"] = datetime.now(timezone.utc).isoformat()

    def add_emergency(self, emergency: dict[str, Any]) -> None:
        with self._data_lock:
            self._state["active_emergencies"].append(emergency)
            self._state["last_updated"] = datetime.now(timezone.utc).isoformat()

    def resolve_emergency(self, emergency_id: str) -> None:
        with self._data_lock:
            self._state["active_emergencies"] = [
                e for e in self._state["active_emergencies"]
                if e.get("id") != emergency_id
            ]

    def update_hire_rates(self, hire_rates: dict[str, Any]) -> None:
        with self._data_lock:
            self._state["hire_rates"].update(hire_rates)
            self._state["last_updated"] = datetime.now(timezone.utc).isoformat()


# Module-level singleton
live_engine = LiveDataEngine()
