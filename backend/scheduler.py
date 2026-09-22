"""
FreightMind AI — Background Data Refresh Scheduler
backend/scheduler.py

Runs data refresh jobs every 15 minutes:
  1. WeatherService.refresh()        → live weather events
  2. RatesService.refresh()          → BDI + freight rates + hire rates
  3. AISuggestionEngine.generate()   → AI suggestion cards
  4. LiveDataEngine.update*()        → persist all state

Uses APScheduler if installed, or gracefully falls back to a background
threading timer so it works without requiring external packages.
"""

from __future__ import annotations

import threading
import time
from typing import Any

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    _HAS_APSCHEDULER = True
except ImportError:
    _HAS_APSCHEDULER = False
    BackgroundScheduler = None
    IntervalTrigger = None

from backend.services.ai_suggestion_engine import ai_suggestion_engine
from backend.services.live_data_engine import live_engine
from backend.services.rates_service import rates_service
from backend.services.weather_service import weather_service
from src.utils.logger import logger

_scheduler: Any = None
_thread_stop_event = threading.Event()
_worker_thread: threading.Thread | None = None


def _run_refresh_cycle() -> None:
    """Single refresh cycle — runs every 15 minutes."""
    logger.info("[Scheduler] ─── Starting live data refresh cycle ───")

    try:
        # 1. Weather
        weather = weather_service.refresh()
        live_engine.update_weather(
            alerts=weather["alerts"],
            severity=weather["severity"],
            rate_adj_pct=weather["rate_adjustment_pct"],
        )

        # 2. Freight rates & hire rates
        rates, hire_rates = rates_service.refresh(
            weather_adjustment_pct=weather["rate_adjustment_pct"]
        )
        live_engine.update_freight_rates(rates)
        live_engine.update_hire_rates(hire_rates)

        # 3. Port status updates (driven by weather)
        if weather["severity"] in ("HIGH", "CRITICAL"):
            for port_id in weather.get("alerts", [{}])[0].get("affected_ports", []):
                live_engine.update_port_status(port_id, {
                    "status": "RESTRICTED",
                    "congestion": "HIGH",
                    "waiting_hours": 48,
                })

        # 4. AI suggestions (read full live state)
        state = live_engine.get_live_state()
        suggestions = ai_suggestion_engine.generate(
            freight_rates=state["freight_rates"],
            weather_alerts=state["weather_alerts"],
            weather_severity=state["weather_severity"],
            port_status=state["port_status"],
            hire_rates=state["hire_rates"],
        )
        live_engine.set_ai_suggestions(suggestions)

        logger.info("[Scheduler] ─── Refresh cycle complete ───")

    except Exception as exc:
        logger.error(f"[Scheduler] Refresh cycle error: {exc}", exc_info=True)


def _threading_loop() -> None:
    """Fallback timer loop if APScheduler is not installed."""
    while not _thread_stop_event.is_set():
        # Sleep for 15 minutes (900 seconds) in 1-second chunks to allow prompt shutdown
        for _ in range(900):
            if _thread_stop_event.is_set():
                return
            time.sleep(1)
        _run_refresh_cycle()


def start_scheduler() -> None:
    """Start the background refresh job. Called from FastAPI lifespan."""
    global _scheduler, _worker_thread

    # Run once immediately on startup
    _run_refresh_cycle()

    if _HAS_APSCHEDULER:
        if _scheduler is not None and _scheduler.running:
            logger.warning("[Scheduler] APScheduler already running.")
            return
        _scheduler = BackgroundScheduler(
            job_defaults={"coalesce": True, "max_instances": 1},
            timezone="UTC",
        )
        _scheduler.add_job(
            func=_run_refresh_cycle,
            trigger=IntervalTrigger(minutes=15),
            id="live_data_refresh",
            name="Live Data Refresh (15-min)",
            replace_existing=True,
        )
        _scheduler.start()
        logger.info("[Scheduler] Started via APScheduler — live data refresh every 15 minutes.")
    else:
        _thread_stop_event.clear()
        _worker_thread = threading.Thread(target=_threading_loop, name="LiveDataScheduler", daemon=True)
        _worker_thread.start()
        logger.info("[Scheduler] Started via background Thread — live data refresh every 15 minutes.")


def stop_scheduler() -> None:
    """Gracefully stop the scheduler. Called from FastAPI lifespan teardown."""
    global _scheduler, _worker_thread
    if _HAS_APSCHEDULER and _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] APScheduler stopped.")
    else:
        _thread_stop_event.set()
        logger.info("[Scheduler] Background Thread stopped.")
