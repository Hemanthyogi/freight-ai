"""
FreightMind AI — Configuration Loader
src/utils/config.py

Loads app_config.yaml and ports_vessels.yaml once at startup.
Provides typed access to all configuration values.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


# ── Resolve config directory ─────────────────────────────────────────────────
# Works whether you run from the project root or from src/
_PROJECT_ROOT = Path(__file__).resolve().parents[2]   # freightmind-ai/
_CONFIGS_DIR = _PROJECT_ROOT / "configs"


def _load_yaml(filename: str) -> dict[str, Any]:
    """Load a YAML config file from the configs/ directory."""
    path = _CONFIGS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}\n"
            f"Make sure you are running from the project root: {_PROJECT_ROOT}"
        )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=1)
def get_app_config() -> dict[str, Any]:
    """Return the parsed app_config.yaml (cached after first load)."""
    return _load_yaml("app_config.yaml")


@lru_cache(maxsize=1)
def get_ports_vessels_config() -> dict[str, Any]:
    """Return the parsed ports_vessels.yaml (cached after first load)."""
    return _load_yaml("ports_vessels.yaml")


# ── Convenience accessors ─────────────────────────────────────────────────────

def is_demo_mode() -> bool:
    """Return True if running in DEMO MODE (synthetic data)."""
    env_val = os.getenv("DEMO_MODE", "").lower()
    if env_val in ("true", "1", "yes"):
        return True
    if env_val in ("false", "0", "no"):
        return False
    # Fall back to app_config
    return bool(get_app_config().get("app", {}).get("demo_mode", True))


def get_port_config(port_id: str) -> dict[str, Any] | None:
    """Return spec dict for a destination port by ID, or None if not found."""
    cfg = get_ports_vessels_config()
    for port in cfg.get("ports", []):
        if port["id"] == port_id:
            return port
    return None


def get_origin_port_config(port_id: str) -> dict[str, Any] | None:
    """Return spec dict for an origin port by ID, or None if not found."""
    cfg = get_ports_vessels_config()
    for port in cfg.get("origin_ports", []):
        if port["id"] == port_id:
            return port
    return None


def get_vessel_config(vessel_type: str) -> dict[str, Any] | None:
    """Return spec dict for a vessel type, or None if not found."""
    cfg = get_ports_vessels_config()
    for vessel in cfg.get("vessels", []):
        if vessel["type"].lower() == vessel_type.lower():
            return vessel
    return None


def get_all_ports() -> list[dict[str, Any]]:
    """Return all destination (East Coast India) port configs."""
    return get_ports_vessels_config().get("ports", [])


def get_all_vessels() -> list[dict[str, Any]]:
    """Return all vessel class configs."""
    return get_ports_vessels_config().get("vessels", [])


def get_all_routes() -> list[dict[str, Any]]:
    """Return all trade route configs."""
    return get_ports_vessels_config().get("routes", [])


def get_models_dir() -> Path:
    """Return the absolute path to the models/ directory."""
    d = Path(os.getenv("MODELS_DIR", str(_PROJECT_ROOT / "models")))
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_data_dir() -> Path:
    """Return the absolute path to the data/ directory."""
    d = Path(os.getenv("DATA_DIR", str(_PROJECT_ROOT / "data")))
    d.mkdir(parents=True, exist_ok=True)
    return d
