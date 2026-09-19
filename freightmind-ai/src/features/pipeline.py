"""
FreightMind AI — Master Feature Engineering Pipeline
src/features/pipeline.py

Builds unified feature matrices for machine learning training and online inference:
  1. Temporal Features: calendar, season, monsoon flag, cyclical sin/cos encodings.
  2. Autoregressive Lags: 1d, 7d, 14d, 30d (strictly grouped by route x vessel).
  3. Rolling Statistics: 7d, 14d, 30d rolling means, standard deviations, min, max, momentum.
  4. Macro & Market Features: BDI proxy changes, VLSFO fuel price changes, commodity trends.
  5. Port Congestion Signals: destination port waiting time & 7d rolling congestion.
  6. Route & Categorical Encodings: label encodings preserved for tree-based models.
  7. Multi-Horizon Future Targets: 7d, 14d, 30d, 60d, 90d ahead.
  8. Chronological Train/Val/Test Split: 70% / 15% / 15% with zero time-series leakage.
  9. Scaler & Feature Registry serialization in models/preprocessors/.

Usage:
    python -m src.features.pipeline
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.features.lag_features import add_lag_features, add_rolling_features
from src.features.market_features import add_market_features, add_route_encodings, get_feature_columns
from src.features.time_features import add_time_features
from src.utils.constants import FORECAST_HORIZONS
from src.utils.logger import logger

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = _PROJECT_ROOT / "data" / "processed"
PREPROCESSORS_DIR = _PROJECT_ROOT / "models" / "preprocessors"


class FeatureEngineeringPipeline:
    """
    End-to-end feature engineering pipeline for FreightMind AI.
    """

    def __init__(self, target_col: str = "freight_rate_usd_mt") -> None:
        self.target_col = target_col
        self.scaler: StandardScaler | None = None
        self.feature_columns: list[str] = []

    def build_features(
        self,
        freight_df: pd.DataFrame,
        commodity_df: pd.DataFrame | None = None,
        market_df: pd.DataFrame | None = None,
        congestion_df: pd.DataFrame | None = None,
        include_targets: bool = True,
    ) -> pd.DataFrame:
        """
        Transform raw dataframes into a rich feature table.
        """
        df = freight_df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(["route_id", "vessel_type", "date"]).reset_index(drop=True)

        group_cols = ["route_id", "vessel_type"]

        # 1. Temporal & Cyclical Features
        df = add_time_features(df, date_col="date")

        # 2. Autoregressive Lags (strictly grouped per route x vessel)
        df = add_lag_features(
            df,
            target_col=self.target_col,
            lag_days=[1, 7, 14, 30],
            group_cols=group_cols,
        )

        # 3. Rolling Window Statistics
        df = add_rolling_features(
            df,
            target_col=self.target_col,
            windows=[7, 14, 30],
            stats=["mean", "std", "min", "max"],
            group_cols=group_cols,
        )

        # 4. Macro & Market Features
        df = add_market_features(
            df,
            market_df=market_df,
            commodity_df=commodity_df,
        )

        # 5. Destination Port Congestion Features
        if congestion_df is not None:
            cong = congestion_df.copy()
            cong["date"] = pd.to_datetime(cong["date"])
            cong = cong.sort_values(["port_id", "date"])
            
            # Destination port 7d rolling average waiting hours
            cong["port_wait_7d_mean"] = cong.groupby("port_id")["avg_waiting_time_hrs"].transform(
                lambda s: s.rolling(7, min_periods=1).mean()
            )
            cong_sub = cong[["date", "port_id", "avg_waiting_time_hrs", "port_wait_7d_mean"]].rename(
                columns={
                    "port_id": "destination",
                    "avg_waiting_time_hrs": "dest_port_wait_hrs",
                    "port_wait_7d_mean": "dest_port_wait_7d_mean",
                }
            )
            df = df.merge(cong_sub, on=["date", "destination"], how="left")
            df["dest_port_wait_hrs"] = df["dest_port_wait_hrs"].fillna(24.0)
            df["dest_port_wait_7d_mean"] = df["dest_port_wait_7d_mean"].fillna(24.0)

        # 6. Route and Port Categorical Encodings
        df = add_route_encodings(df)

        # 7. Supervised Multi-Horizon Forecasting Targets
        if include_targets:
            for horizon in FORECAST_HORIZONS:
                target_name = f"target_{horizon}d"
                df[target_name] = df.groupby(group_cols)[self.target_col].shift(-horizon)

        # 8. Clean up warm-up rows (first 30 days lack lag_30)
        # For training, drop initial warm-up rows where lag_30 is NaN
        df = df.dropna(subset=[f"{self.target_col}_lag_30"]).reset_index(drop=True)

        # Fill any remaining macro NaNs from first 30 days with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if not col.startswith("target_") and df[col].isna().any():
                df[col] = df[col].ffill().bfill().fillna(0.0)

        return df

    def split_chronological(
        self,
        df: pd.DataFrame,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Chronological train / validation / test split based on calendar dates.
        Strictly prevents lookahead leakage.
        """
        unique_dates = np.sort(df["date"].unique())
        n_dates = len(unique_dates)

        train_end_idx = int(n_dates * train_ratio)
        val_end_idx = int(n_dates * (train_ratio + val_ratio))

        train_dates = unique_dates[:train_end_idx]
        val_dates = unique_dates[train_end_idx:val_end_idx]
        test_dates = unique_dates[val_end_idx:]

        train_df = df[df["date"].isin(train_dates)].reset_index(drop=True)
        val_df = df[df["date"].isin(val_dates)].reset_index(drop=True)
        test_df = df[df["date"].isin(test_dates)].reset_index(drop=True)

        logger.info(
            f"Chronological Split: "
            f"Train={len(train_df):,} rows ({pd.to_datetime(train_dates[0]).date()} to {pd.to_datetime(train_dates[-1]).date()}) | "
            f"Val={len(val_df):,} rows ({pd.to_datetime(val_dates[0]).date()} to {pd.to_datetime(val_dates[-1]).date()}) | "
            f"Test={len(test_df):,} rows ({pd.to_datetime(test_dates[0]).date()} to {pd.to_datetime(test_dates[-1]).date()})"
        )

        return train_df, val_df, test_df

    def fit_scaler(self, train_df: pd.DataFrame, feature_cols: list[str]) -> StandardScaler:
        """
        Fit standard scaler strictly on training split.
        """
        self.feature_columns = feature_cols
        self.scaler = StandardScaler()
        self.scaler.fit(train_df[feature_cols])
        return self.scaler

    def save_preprocessors(self, output_dir: Path = PREPROCESSORS_DIR) -> None:
        """Serialize fitted scaler and feature metadata."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.scaler is not None:
            scaler_path = output_dir / "feature_scaler.joblib"
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"Saved feature scaler -> {scaler_path}")

        names_path = output_dir / "feature_names.json"
        with open(names_path, "w", encoding="utf-8") as f:
            json.dump({
                "feature_columns": self.feature_columns,
                "target_col": self.target_col,
                "forecast_horizons": FORECAST_HORIZONS,
            }, f, indent=2)
        logger.info(f"Saved feature registry ({len(self.feature_columns)} features) -> {names_path}")


def run_feature_pipeline() -> dict[str, pd.DataFrame]:
    """
    Execute the feature engineering pipeline and persist datasets.
    """
    print("\n[FreightMind AI] Running Feature Engineering Pipeline...")
    
    # 1. Ingest processed datasets
    freight_df = pd.read_csv(DATA_DIR / "freight_rates.csv")
    comm_df = pd.read_csv(DATA_DIR / "commodity_prices.csv")
    mkt_df = pd.read_csv(DATA_DIR / "market_indicators.csv")
    cong_df = pd.read_csv(DATA_DIR / "port_congestion.csv")

    pipeline = FeatureEngineeringPipeline()
    full_df = pipeline.build_features(
        freight_df=freight_df,
        commodity_df=comm_df,
        market_df=mkt_df,
        congestion_df=cong_df,
        include_targets=True,
    )

    # 2. Extract feature columns (exclude targets, dates, and raw categoricals)
    target_cols = [f"target_{h}d" for h in FORECAST_HORIZONS]
    feature_cols = get_feature_columns(full_df, exclude_cols=target_cols)

    print(f"  [OK] Engineered {len(feature_cols)} predictor features across {len(full_df):,} records.")

    # 3. Chronological split (zero leakage)
    train_df, val_df, test_df = pipeline.split_chronological(full_df)

    # 4. Fit and save scaler & registry
    pipeline.fit_scaler(train_df, feature_cols)
    pipeline.save_preprocessors()

    # 5. Persist feature splits
    full_df.to_csv(DATA_DIR / "full_features.csv", index=False)
    train_df.to_csv(DATA_DIR / "train_features.csv", index=False)
    val_df.to_csv(DATA_DIR / "val_features.csv", index=False)
    test_df.to_csv(DATA_DIR / "test_features.csv", index=False)

    print(f"  [OK] Saved train_features.csv ({len(train_df):,} rows)")
    print(f"  [OK] Saved val_features.csv   ({len(val_df):,} rows)")
    print(f"  [OK] Saved test_features.csv  ({len(test_df):,} rows)")
    print(f"  [OK] Saved full_features.csv  ({len(full_df):,} rows)")

    return {
        "full": full_df,
        "train": train_df,
        "val": val_df,
        "test": test_df,
        "features": feature_cols,
    }


if __name__ == "__main__":
    results = run_feature_pipeline()
    feats = results["features"]
    print("\n" + "=" * 60)
    print("  FreightMind AI - Feature Engineering Complete")
    print("=" * 60)
    print(f"  Total Predictive Features: {len(feats)}")
    print("  Feature categories created:")
    print("    - Temporal:    month, day_of_week, day_of_year, is_monsoon, sin/cos")
    print("    - Lags:        lag_1, lag_7, lag_14, lag_30 (route x vessel grouped)")
    print("    - Rolling:     7d, 14d, 30d means, std (volatility), min, max, pct_change")
    print("    - Macro:       BDI 7d/30d change, bunker fuel change, commodity trends")
    print("    - Congestion:  dest_port_wait_hrs, dest_port_wait_7d_mean")
    print("    - Encodings:   route_encoded, vessel_type_encoded, destination_encoded")
    print(f"  Chronological Splits: Train {len(results['train']):,} | Val {len(results['val']):,} | Test {len(results['test']):,}")
    print("=" * 60 + "\n")
