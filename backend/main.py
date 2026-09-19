"""
FreightMind AI — FastAPI Main Application
backend/main.py

Smart India Hackathon 2026 | Problem Statement 26006
Intelligent Freight Forecasting & Vessel Charter Optimization
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from backend.routes.forecast import router as forecast_router
from backend.routes.market import router as market_router
from backend.routes.port import router as port_router
from backend.routes.recommend import router as recommend_router
from backend.routes.risk import router as risk_router
from backend.routes.vessel import router as vessel_router
from backend.routes.voyage import router as voyage_router
from src.utils.config import get_app_config, is_demo_mode
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    mode = "DEMO_MODE" if is_demo_mode() else "PRODUCTION_REAL_DATA"
    logger.info(f"=== Starting FreightMind AI Backend [{mode}] ===")
    logger.info("  FastAPI backend active on port 8000")
    logger.info("  OpenAPI Documentation: http://localhost:8000/docs")
    yield
    logger.info("=== Stopping FreightMind AI Backend ===")


app = FastAPI(
    title="FreightMind AI",
    description=(
        "Intelligent Freight Forecasting & Vessel Charter Optimization API\n\n"
        "**Smart India Hackathon 2026 — Problem Statement ID 26006**\n\n"
        "Provides multi-horizon freight rate forecasting, port feasibility validation, "
        "vessel selection optimization, voyage risk quantification, and explainable charter recommendations."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# -------------------------------------------------------------
# CORS Middleware
# -------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local React Vite frontend (http://localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Include API Routers (under /api/v1)
# -------------------------------------------------------------
API_V1_PREFIX = "/api/v1"
app.include_router(voyage_router, prefix=API_V1_PREFIX)
app.include_router(forecast_router, prefix=API_V1_PREFIX)
app.include_router(vessel_router, prefix=API_V1_PREFIX)
app.include_router(port_router, prefix=API_V1_PREFIX)
app.include_router(risk_router, prefix=API_V1_PREFIX)
app.include_router(market_router, prefix=API_V1_PREFIX)
app.include_router(recommend_router, prefix=API_V1_PREFIX)


from fastapi.staticfiles import StaticFiles
import json

# Mount reports directory for publication charts
reports_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
if os.path.exists(reports_path):
    app.mount("/reports", StaticFiles(directory=reports_path), name="reports")


@app.get("/api/v1/reports/eda", tags=["Reports"])
async def get_eda_report() -> dict:
    summary_file = os.path.join(reports_path, "eda_summary.json")
    if os.path.exists(summary_file):
        with open(summary_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "EDA summary not found"}


@app.get("/api/v1/reports/models", tags=["Reports"])
async def get_model_comparison_report() -> list:
    comp_file = os.path.join(reports_path, "model_comparison.json")
    if os.path.exists(comp_file):
        with open(comp_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []



@app.get("/", tags=["General"])
async def root() -> dict:
    return {
        "name": "FreightMind AI API",
        "tagline": "Data-Driven Decisions for a Resilient Maritime Supply Chain",
        "sih_ps_id": "26006",
        "version": "1.0.0",
        "status": "operational",
        "demo_mode": is_demo_mode(),
        "documentation": "/docs",
        "default_scenario_endpoint": "/api/v1/voyage-analysis/default",
    }


@app.get("/health", tags=["General"])
@app.get("/api/v1/health", tags=["General"])
async def health_check() -> dict:
    return {
        "status": "healthy",
        "demo_mode": is_demo_mode(),
        "database": "sqlite_connected",
    }


# -------------------------------------------------------------
# Serve React frontend (production build)
# MUST come LAST — catch-all for SPA client-side routing
# -------------------------------------------------------------
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_dist = os.path.join(_root, "frontend", "dist")
if os.path.exists(_dist):
    # Serve /assets/* (JS/CSS bundles)
    app.mount("/assets", StaticFiles(directory=os.path.join(_dist, "assets")), name="frontend_assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(request: Request, full_path: str) -> FileResponse:
        """Catch-all: return index.html for any non-API path (SPA client routing)."""
        return FileResponse(os.path.join(_dist, "index.html"))
