"""
FreightMind AI — Vercel Serverless API Entry Point
api/index.py

This is a slim FastAPI handler for Vercel deployment.
It serves pre-computed demo responses without any heavy ML dependencies
(pandas, scikit-learn, xgboost, lightgbm, scipy, etc.) to stay under
Vercel's 500 MB serverless function limit.

The full ML stack runs separately (Railway / local) via backend/main.py.
"""

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── Load pre-baked demo data once at cold start ─────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent
_DEMO_DATA_PATH = _ROOT / "frontend" / "src" / "data" / "defaultDashboardData.json"

def _load_demo() -> dict:
    try:
        with open(_DEMO_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"error": "Demo data not available", "data_mode": "DEMO_DATA"}

_DEMO = _load_demo()

# ── Minimal ports/vessels config (no YAML needed at runtime) ────────────────
_PORTS = [
    {"id": "paradip", "name": "Paradip Port", "state": "Odisha", "latitude": 20.3194, "longitude": 86.6089, "max_draft_m": 17.0, "max_loa_m": 300.0, "max_beam_m": 45.0},
    {"id": "visakhapatnam", "name": "Visakhapatnam Port", "state": "Andhra Pradesh", "latitude": 17.6868, "longitude": 83.2185, "max_draft_m": 16.5, "max_loa_m": 280.0, "max_beam_m": 40.0},
    {"id": "haldia", "name": "Haldia Port", "state": "West Bengal", "latitude": 22.0667, "longitude": 88.0667, "max_draft_m": 8.5, "max_loa_m": 185.0, "max_beam_m": 28.0},
    {"id": "chennai", "name": "Chennai Port", "state": "Tamil Nadu", "latitude": 13.0827, "longitude": 80.2707, "max_draft_m": 14.5, "max_loa_m": 275.0, "max_beam_m": 42.0},
    {"id": "ennore", "name": "Kamarajar Port (Ennore)", "state": "Tamil Nadu", "latitude": 13.2000, "longitude": 80.3200, "max_draft_m": 16.5, "max_loa_m": 300.0, "max_beam_m": 45.0},
]

_VESSELS = [
    {"type": "Handysize", "dwt_range_mt": [25000, 40000], "typical_dwt_mt": 32000},
    {"type": "Supramax", "dwt_range_mt": [50000, 65000], "typical_dwt_mt": 58000},
    {"type": "Panamax", "dwt_range_mt": [65000, 82000], "typical_dwt_mt": 75000},
    {"type": "Capesize", "dwt_range_mt": [150000, 400000], "typical_dwt_mt": 180000},
]

# ── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="FreightMind AI",
    description=(
        "Intelligent Freight Forecasting & Vessel Charter Optimization API\n\n"
        "**Smart India Hackathon 2026 — Problem Statement ID 26006**"
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health & Root ─────────────────────────────────────────────────────────────
@app.get("/api")
@app.get("/api/")
async def root():
    return {
        "name": "FreightMind AI API",
        "tagline": "Data-Driven Decisions for a Resilient Maritime Supply Chain",
        "sih_ps_id": "26006",
        "version": "1.0.0",
        "status": "operational",
        "mode": "demo",
        "documentation": "/api/docs",
    }


@app.get("/api/v1/health")
@app.get("/health")
async def health():
    return {"status": "healthy", "demo_mode": True, "database": "none"}


# ── Voyage Analysis (serves pre-baked demo data) ─────────────────────────────
@app.get("/api/v1/voyage-analysis/default")
async def default_voyage():
    """Return the default SIH 2026 demonstration scenario."""
    return JSONResponse(content={**_DEMO, "data_mode": "DEMO_DATA"})


@app.post("/api/v1/voyage-analysis")
async def analyze_voyage(body: dict = None):
    """Accept any voyage request and return the demo dashboard data."""
    return JSONResponse(content={**_DEMO, "data_mode": "DEMO_DATA"})


# ── Freight Forecast ──────────────────────────────────────────────────────────
@app.post("/api/v1/forecast")
async def forecast(body: dict = None):
    """Return demo freight forecast."""
    return JSONResponse(content={
        "route_id": "ID_COAL_PARADIP",
        "vessel_type": "Supramax",
        "current_rate_usd_mt": _DEMO.get("forecast_rate", 9.9),
        "confidence_level": "Medium",
        "confidence_explanation": "Normal uncertainty corridor; represents market volatility and seasonal transitions.",
        "horizons": {
            "7":  {"horizon_days": 7,  "predicted_rate_usd_mt": 9.78, "lower_bound_usd_mt": 8.67, "upper_bound_usd_mt": 10.89, "rate_change_pct": -1.2},
            "14": {"horizon_days": 14, "predicted_rate_usd_mt": 9.90, "lower_bound_usd_mt": 8.51, "upper_bound_usd_mt": 11.29, "rate_change_pct":  0.1},
            "30": {"horizon_days": 30, "predicted_rate_usd_mt": 10.56, "lower_bound_usd_mt": 8.81, "upper_bound_usd_mt": 12.32, "rate_change_pct":  6.7},
            "60": {"horizon_days": 60, "predicted_rate_usd_mt": 11.15, "lower_bound_usd_mt": 9.14, "upper_bound_usd_mt": 13.15, "rate_change_pct": 12.6},
            "90": {"horizon_days": 90, "predicted_rate_usd_mt": 10.90, "lower_bound_usd_mt": 8.73, "upper_bound_usd_mt": 13.07, "rate_change_pct": 10.1},
        },
        "historical_series": _DEMO.get("forecast_chart_historical", []),
        "forecast_series":   _DEMO.get("forecast_chart_prediction", []),
        "top_feature_drivers": [
            {"feature": "Bdi Index 7D Ma",   "importance": 0.312},
            {"feature": "Freight Rate Lag7", "importance": 0.198},
            {"feature": "Port Congestion",   "importance": 0.147},
            {"feature": "Bunker Price",      "importance": 0.121},
            {"feature": "Commodity Price",   "importance": 0.098},
        ],
        "model_version": "FreightMind-RF-v1.0 (demo)",
        "data_mode": "DEMO_DATA",
    })


# ── Ports ─────────────────────────────────────────────────────────────────────
@app.get("/api/v1/ports")
async def list_ports():
    return {"ports": _PORTS}


@app.get("/api/v1/ports/{port_id}")
async def get_port(port_id: str):
    port = next((p for p in _PORTS if p["id"] == port_id), None)
    if port is None:
        return JSONResponse(status_code=404, content={"detail": f"Port '{port_id}' not found."})
    return port


@app.post("/api/v1/ports/feasibility")
async def port_feasibility(body: dict = None):
    return JSONResponse(content=_DEMO.get("port_feasibility", {}))


# ── Vessels ───────────────────────────────────────────────────────────────────
@app.get("/api/v1/vessels")
async def list_vessels():
    return {"vessels": _VESSELS}


@app.post("/api/v1/vessels/optimize")
async def optimize_vessels(body: dict = None):
    return JSONResponse(content={"top_vessels": _DEMO.get("top_vessel_matches", [])})


# ── Risk ──────────────────────────────────────────────────────────────────────
@app.post("/api/v1/risk")
async def risk_analysis(body: dict = None):
    kpis = _DEMO.get("kpis", {})
    return JSONResponse(content={
        "total_score": kpis.get("risk_score", 33),
        "level_label": kpis.get("risk_level", "LOW - MEDIUM"),
        "weather_risk_level": "LOW",
        "key_risk_drivers": ["Destination port wait time (50h)"],
        "mitigation_strategies": ["Include flexible laytime and standard NOR terms in charter party"],
        "freight_risk": {"score": 20, "level": "LOW"},
        "congestion_risk": {"score": 70, "level": "HIGH", "expected_wait_hours": 50.4},
        "vessel_risk": {"score": 15, "level": "LOW", "available_vessels_count": 12},
        "data_mode": "DEMO_DATA",
    })


# ── Market Timing ─────────────────────────────────────────────────────────────
@app.post("/api/v1/market/timing")
async def market_timing(body: dict = None):
    return JSONResponse(content={
        "signal": "NEUTRAL — Charter within 7-10 days for optimal rate capture",
        "recommended_window": "Within 7 - 10 Days",
        "current_rate": 9.89,
        "forecast_7d": 9.78,
        "forecast_14d": 9.90,
        "forecast_30d": 10.56,
        "expected_rate_change_pct": 0.1,
        "confidence": "Medium",
        "rationale": "Rates are broadly stable with a mild upward trend expected at 30+ days. Lock in near-current rates.",
        "reasons": ["BDI momentum is flat", "Indonesia supply steady", "Bay of Bengal demand stable"],
        "risks_to_timing": ["Monsoon disruption risk at origin ports"],
        "data_mode": "DEMO_DATA",
    })


# ── Recommendations ───────────────────────────────────────────────────────────
@app.post("/api/v1/recommend")
async def recommend(body: dict = None):
    return JSONResponse(content={
        "recommendation": _DEMO.get("ai_recommendation", {}),
        "scenario_comparison": _DEMO.get("scenario_comparison", []),
        "why_recommendation": _DEMO.get("why_recommendation", []),
        "data_mode": "DEMO_DATA",
    })


# ── Reports ───────────────────────────────────────────────────────────────────
@app.get("/api/v1/reports/eda")
async def eda_report():
    return {"message": "EDA summary not available in Vercel demo mode", "data_mode": "DEMO_DATA"}


@app.get("/api/v1/reports/models")
async def model_report():
    return [
        {"Model": "Random Forest Regressor", "MAE": 0.421, "RMSE": 0.618, "MAPE": 4.32, "R2": 0.961, "Training_Time_s": 2.1},
        {"Model": "HistGradientBoosting",    "MAE": 0.398, "RMSE": 0.589, "MAPE": 4.01, "R2": 0.965, "Training_Time_s": 1.8},
    ]


# ── Live Operations Endpoints (Vercel Compatibility) ──────────────────────────
@app.get("/api/v1/live/state")
async def live_state():
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    return {
        "last_updated": now,
        "next_update_in_seconds": 900,
        "freight_rates": {
            "bdi": 1842,
            "bdi_change_pct": 1.3,
            "bdi_trend": "rising",
            "rates_by_class": {
                "Handysize": {"rate_usd_mt": 7.2, "tce_usd_day": 8500,  "change_pct": 0.5, "trend": "rising"},
                "Supramax":  {"rate_usd_mt": 9.9, "tce_usd_day": 11200, "change_pct": 0.8, "trend": "rising"},
                "Panamax":   {"rate_usd_mt": 9.5, "tce_usd_day": 14800, "change_pct": 0.2, "trend": "stable"},
                "Capesize":  {"rate_usd_mt": 8.8, "tce_usd_day": 22000, "change_pct": -0.4, "trend": "falling"},
            },
            "weather_adjustment_pct": 5.0,
            "demand_factor": 1.03,
            "bunker_prices": {"vlsfo_usd_mt": 620.0, "ifo380_usd_mt": 510.0, "mdo_usd_mt": 890.0}
        },
        "weather_alerts": [
            {
                "id": "wx_live_cyclone",
                "type": "CYCLONE",
                "name": "Cyclone Dana (Bay of Bengal Advisory)",
                "severity": "MEDIUM",
                "zone": "Central Bay of Bengal",
                "position": {"lat": 14.5, "lon": 87.2},
                "wind_speed_kmh": 85,
                "distance_from_paradip_km": 340,
                "expected_landfall_hours": 48,
                "intensity": "Cyclonic Storm",
                "affected_ports": ["paradip", "visakhapatnam"],
                "message": "Cyclonic system moving NW towards Odisha coast. Swells 3-4m. Spot freight rates reflecting +5.0% risk premium.",
                "rate_impact_pct": 5.0,
                "generated_at": now
            }
        ],
        "weather_severity": "MEDIUM",
        "port_status": {
            "paradip":       {"status": "OPEN",      "congestion": "LOW",    "waiting_hours": 18},
            "visakhapatnam": {"status": "OPEN",      "congestion": "LOW",    "waiting_hours": 12},
            "haldia":        {"status": "CONGESTED", "congestion": "MEDIUM", "waiting_hours": 36},
            "chennai":       {"status": "OPEN",      "congestion": "LOW",    "waiting_hours": 14},
            "ennore":        {"status": "OPEN",      "congestion": "LOW",    "waiting_hours": 10},
        },
        "ai_suggestions": [
            {
                "id": "sug_live_01",
                "type": "WARNING",
                "severity": "HIGH",
                "title": "🌀 Cyclone Advisory Near Paradip — Lock Charter Now",
                "message": "Cyclonic storm in Central Bay of Bengal may cause freight rates to surge 5-10% over the next 48h. Recommended action: Lock prompt charter window.",
                "action_label": "Lock Charter",
                "action": "open_booking",
                "generated_at": now
            },
            {
                "id": "sug_live_02",
                "type": "INSIGHT",
                "severity": "INFO",
                "title": "📈 BDI Momentum Positive (+1.3%)",
                "message": "Baltic Dry Index reached 1,842 points. Asian thermal coal demand is steady across Indonesia-India trade lanes.",
                "action_label": "View Rates",
                "action": "view_rates",
                "generated_at": now
            },
            {
                "id": "sug_live_03",
                "type": "CAUTION",
                "severity": "MEDIUM",
                "title": "⚓ Haldia Draft & Congestion Advisory",
                "message": "Haldia waiting times increased to 36 hours. Supramax/Panamax charterers should prioritize Paradip deep draft berths.",
                "action_label": "Check Ports",
                "action": "open_port_feasibility",
                "generated_at": now
            }
        ],
        "active_emergencies": [],
        "hire_rates": {
            "Handysize": {"day_rate_usd": 8500,  "monthly_usd": 255000, "trend": "rising"},
            "Supramax":  {"day_rate_usd": 11200, "monthly_usd": 336000, "trend": "rising"},
            "Panamax":   {"day_rate_usd": 14800, "monthly_usd": 444000, "trend": "stable"},
            "Capesize":  {"day_rate_usd": 22000, "monthly_usd": 660000, "trend": "falling"},
        }
    }


@app.get("/api/v1/live/weather")
async def live_weather():
    st = await live_state()
    return {
        "severity": st["weather_severity"],
        "rate_adjustment_pct": st["freight_rates"]["weather_adjustment_pct"],
        "alerts": st["weather_alerts"],
        "last_updated": st["last_updated"]
    }


@app.get("/api/v1/live/suggestions")
async def live_suggestions():
    st = await live_state()
    return {
        "suggestions": st["ai_suggestions"],
        "count": len(st["ai_suggestions"]),
        "last_updated": st["last_updated"]
    }


@app.get("/api/v1/live/port-status")
async def live_port_status():
    st = await live_state()
    return {
        "ports": st["port_status"],
        "last_updated": st["last_updated"]
    }


@app.get("/api/v1/live/booking-costs")
async def live_booking_costs():
    st = await live_state()
    rates = st["freight_rates"]["rates_by_class"]
    hire = st["hire_rates"]
    bunker = st["freight_rates"]["bunker_prices"]
    booking_info = {}
    for v_type, h_data in hire.items():
        r_data = rates.get(v_type, {})
        spot = r_data.get("rate_usd_mt", 9.9)
        day_rate = h_data["day_rate_usd"]
        example_cargo = 55000
        f_cost = int(spot * example_cargo)
        b_cost = int(26 * 7.2 * bunker["vlsfo_usd_mt"])
        p_cost = int(day_rate * 0.5)
        tot = f_cost + b_cost + p_cost * 2
        booking_info[v_type] = {
            "spot_rate_usd_mt": spot,
            "tce_usd_day": r_data.get("tce_usd_day", 11200),
            "hire_rate_day_usd": day_rate,
            "hire_rate_monthly_usd": h_data["monthly_usd"],
            "trend": h_data["trend"],
            "example_cost_breakdown": {
                "cargo_mt": example_cargo,
                "voyage_days": 7.2,
                "freight_cost_usd": f_cost,
                "bunker_cost_usd": b_cost,
                "port_charges_usd": p_cost,
                "idle_cost_usd": p_cost,
                "total_voyage_cost_usd": tot,
                "cost_per_mt_usd": round(tot / example_cargo, 2)
            },
            "charter_options": {
                "voyage_charter": {
                    "description": "Single voyage — freight paid per MT",
                    "rate": f"${spot:.2f}/MT",
                    "total_usd": f_cost,
                    "risk": "Market spot rate"
                },
                "time_charter_6mo": {
                    "description": "6-month fixed daily hire",
                    "rate": f"${day_rate:,}/day",
                    "total_usd": day_rate * 180,
                    "risk": "Fixed cost commitment"
                },
                "coa_3_voyage": {
                    "description": "Contract of Affreightment (3 voyages)",
                    "rate": f"${spot * 0.97:.2f}/MT",
                    "total_usd": int(spot * 0.97 * example_cargo * 3),
                    "risk": "Volume discount (-3%)"
                }
            }
        }
    return {
        "booking_costs": booking_info,
        "bunker_prices": bunker,
        "weather_rate_adjustment_pct": st["freight_rates"]["weather_adjustment_pct"],
        "last_updated": st["last_updated"]
    }


@app.post("/api/v1/live/diversion")
async def live_diversion(body: dict = None):
    body = body or {}
    emergency_type = body.get("emergency_type", "engine_fault")
    vessel_type = body.get("vessel_type", "Supramax")
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    revised = now + timedelta(hours=34)
    return {
        "emergency_id": f"emg_{now.strftime('%Y%m%d%H%M%S')}",
        "emergency_type": emergency_type,
        "emergency_label": emergency_type.replace("_", " ").title(),
        "vessel_type": vessel_type,
        "current_position": {"lat": body.get("current_lat", 12.5), "lon": body.get("current_lon", 84.2)},
        "recommended_diversion_port": {
            "id": "visakhapatnam",
            "name": "Visakhapatnam Port",
            "country": "India",
            "distance_nm": 185.0,
            "eta_hours": 15.4,
            "services_available": ["Engine Repair", "Medical", "Bunkering", "Dry Dock"],
            "port_cost_usd": 18000
        },
        "alternate_ports": [
            {"id": "chennai", "name": "Chennai Port", "distance_nm": 210.0, "eta_hours": 17.5, "services": ["Engine Repair", "Medical"]},
            {"id": "colombo", "name": "Colombo (Sri Lanka)", "distance_nm": 340.0, "eta_hours": 28.3, "services": ["Engine Repair", "Dry Dock"]}
        ],
        "cost_impact": {
            "diversion_fuel_cost_usd": 12400,
            "diversion_port_charges_usd": 18000,
            "total_extra_cost_usd": 30400,
            "additional_delay_hours": 34.0,
            "revised_destination_eta": revised.strftime("%d %b %Y, %H:%M UTC")
        },
        "recommendations": [
            "Proceed immediately to Visakhapatnam Port — nearest facility with marine workshop.",
            "Alert Chennai MRCC and vessel superintendent.",
            "File preliminary deviation claim with P&I Club underwriters.",
            "Notify cargo receiver of Paradip ETA adjustment (+34h)."
        ],
        "status": "DIVERSION_REQUIRED",
        "generated_at": now.isoformat()
    }

