"""
FreightMind AI — Market & Route Feature Engineering
src/features/market_features.py

Creates:
  - Commodity price change features
  - Fuel price change features
  - Price volatility (rolling std)
  - BDI proxy features
  - Route/origin/destination encodings

WHY THESE MATTER:
  Freight rates are not isolated — they co-move with commodity prices
  (higher iron ore demand → more Capesize demand → higher rates),
  fuel prices (bunker cost is ~40-60% of voyage cost), and the BDI
  (leading indicator of bulk shipping demand).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from src.utils.constants import CARGO_TYPES, EAST_COAST_PORTS, VESSEL_TYPES


def add_market_features(
    df: pd.DataFrame,
    market_df: pd.DataFrame | None = None,
    commodity_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Merge market indicators and commodity prices into the freight DataFrame.

    Args:
        df:           Main freight rates DataFrame (must have 'date' column)
        market_df:    market_indicators DataFrame (optional)
        commodity_df: commodity_prices DataFrame (optional)

    Returns:
        Enriched DataFrame with market features.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Merge market indicators (BDI proxy, bunker price, FX rate)
    if market_df is not None:
        market_df = market_df.copy()
        market_df["date"] = pd.to_datetime(market_df["date"])
        keep_cols = ["date", "bdi_proxy", "vlsfo_price_usd_mt", "usd_inr", "vessel_supply_index"]
        keep_cols = [c for c in keep_cols if c in market_df.columns]
        df = df.merge(market_df[keep_cols], on="date", how="left")

        # Derived features
        if "bdi_proxy" in df.columns:
            df["bdi_7d_change_pct"] = df["bdi_proxy"].pct_change(7)
            df["bdi_30d_change_pct"] = df["bdi_proxy"].pct_change(30)
            df["bdi_volatility_30d"] = df["bdi_proxy"].rolling(30, min_periods=5).std()

        if "vlsfo_price_usd_mt" in df.columns:
            df["bunker_7d_change_pct"] = df["vlsfo_price_usd_mt"].pct_change(7)
            df["bunker_30d_change_pct"] = df["vlsfo_price_usd_mt"].pct_change(30)

    # Merge commodity prices
    if commodity_df is not None:
        commodity_df = commodity_df.copy()
        commodity_df["date"] = pd.to_datetime(commodity_df["date"])
        keep_cols = [c for c in commodity_df.columns
                     if c not in ("data_source", "is_synthetic")]
        df = df.merge(commodity_df[keep_cols], on="date", how="left")

        # Price change features
        for col in ["thermal_coal_usd_mt", "iron_ore_usd_mt", "coking_coal_usd_mt"]:
            if col in df.columns:
                df[f"{col}_7d_change_pct"] = df[col].pct_change(7)
                df[f"{col}_30d_change_pct"] = df[col].pct_change(30)

    return df


def add_route_encodings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add label-encoded route, origin, destination, vessel_type, cargo_type columns.

    Encoding strategy:
      - Label encoding is used here (not one-hot) to keep dimensionality low.
      - XGBoost/LightGBM handle label-encoded categoricals well natively.
      - For LSTM or linear models, one-hot encoding may be preferred.
    """
    df = df.copy()

    categorical_cols = {
        "vessel_type":  VESSEL_TYPES,
        "cargo_type":   CARGO_TYPES,
        "destination":  EAST_COAST_PORTS,
    }

    for col, known_values in categorical_cols.items():
        if col not in df.columns:
            continue
        # Create a consistent mapping from known values
        mapping = {v: i for i, v in enumerate(sorted(known_values))}
        df[f"{col}_encoded"] = df[col].map(mapping).fillna(-1).astype(int)

    # Route ID encoding
    if "route_id" in df.columns:
        unique_routes = sorted(df["route_id"].dropna().unique())
        route_map = {r: i for i, r in enumerate(unique_routes)}
        df["route_encoded"] = df["route_id"].map(route_map).fillna(-1).astype(int)

    return df


def get_feature_columns(df: pd.DataFrame, exclude_cols: list[str] | None = None) -> list[str]:
    """
    Return the list of numeric feature columns suitable for ML model training.
    Excludes target, identifiers, and metadata columns.
    """
    if exclude_cols is None:
        exclude_cols = []

    # Always exclude these
    always_exclude = {
        "date", "freight_rate_usd_mt",  # target
        "route_id", "origin", "destination", "cargo_type", "vessel_type",  # raw categoricals
        "data_source", "is_synthetic",  # metadata
    } | set(exclude_cols)

    return [
        col for col in df.columns
        if col not in always_exclude
        and pd.api.types.is_numeric_dtype(df[col])
    ]
