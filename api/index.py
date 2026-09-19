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
