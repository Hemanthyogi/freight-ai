"""
FreightMind AI — API Endpoint Tests
tests/test_api.py

Tests all FastAPI routes using TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "FreightMind AI API"
    assert data["status"] == "operational"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_default_voyage_scenario():
    response = client.get("/api/v1/voyage-analysis/default")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "forecast_rate" in data
    assert "ai_recommendation" in data
    assert "top_vessel_matches" in data
    assert "scenario_comparison" in data
    assert len(data["top_vessel_matches"]) > 0
    assert len(data["scenario_comparison"]) == 3


def test_post_custom_voyage_analysis():
    payload = {
        "origin": "Australia",
        "destination_port_id": "visakhapatnam",
        "commodity": "Coking Coal",
        "cargo_quantity_mt": 75000.0,
        "delivery_window": "October 2026",
        "procurement_strategy": "Spot Charter",
        "vessel_preference": "Panamax",
    }
    response = client.post("/api/v1/voyage-analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["cargo_requirement"]["commodity"] == "Coking Coal"
    assert data["ai_recommendation"]["action"] in ["CHARTER", "HOLD"]


def test_post_freight_forecast():
    payload = {
        "route_id": "AU_COAL_PARADIP",
        "vessel_type": "Panamax",
    }
    response = client.post("/api/v1/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "horizons" in data
    assert "14" in data["horizons"]
    assert data["horizons"]["14"]["predicted_rate_usd_mt"] > 0


def test_post_port_feasibility():
    payload = {
        "port_id": "paradip",
        "vessel_type": "Panamax",
        "cargo_quantity_mt": 70000.0,
    }
    response = client.post("/api/v1/port-feasibility", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["port_name"] == "Paradip Port"
    assert data["feasible"] is True


def test_list_ports():
    response = client.get("/api/v1/port-feasibility/ports")
    assert response.status_code == 200
    ports = response.json()
    assert len(ports) >= 5
