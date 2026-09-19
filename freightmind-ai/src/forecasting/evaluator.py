"""
FreightMind AI — Model Training & Evaluation Engine
src/forecasting/evaluator.py

Compares candidate models on the chronological Test split:
  1. Naive (Persistence)
  2. Moving Average (7-Day)
  3. Moving Average (14-Day)
  4. Random Forest Regressor
  5. LightGBM Regressor
  6. XGBoost Regressor

Evaluates across:
  - MAE (Mean Absolute Error, $/MT)
  - RMSE (Root Mean Squared Error, $/MT)
  - MAPE (Mean Absolute Percentage Error, %)
  - R² (Coefficient of Determination)
  - Training Time (seconds)

Saves:
  - Best model -> models/freight_forecast/best_freight_model.joblib
  - Evaluation table -> reports/model_comparison.json
  - Visual plot -> reports/figures/06_forecast_vs_actual.png

Usage:
    python -m src.forecasting.evaluator
"""

from __future__ import annotations

import json
from pathlib import Path
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.forecasting.baseline import MovingAverageForecaster, NaiveForecaster
from src.forecasting.ml_models import MultiHorizonForecaster
from src.utils.constants import FORECAST_HORIZONS
from src.utils.logger import logger

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = _PROJECT_ROOT / "data" / "processed"
MODELS_DIR = _PROJECT_ROOT / "models" / "freight_forecast"
REPORTS_DIR = _PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Calculate standard time-series evaluation metrics."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    
    # Safe MAPE (avoid division by zero)
    non_zero = y_true > 0.1
    if non_zero.sum() > 0:
        mape = float(np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100.0)
    else:
        mape = 0.0

    r2 = r2_score(y_true, y_pred)

    return {
        "MAE": round(float(mae), 3),
        "RMSE": round(float(rmse), 3),
        "MAPE": round(float(mape), 2),
        "R2": round(float(r2), 4),
    }


def evaluate_models() -> dict:
    """Execute complete multi-model evaluation pipeline."""
    print("\n[FreightMind AI] Running Model Comparison Pipeline on Chronological Test Set...")

    # 1. Load feature splits
    train_df = pd.read_csv(DATA_DIR / "train_features.csv")
    val_df = pd.read_csv(DATA_DIR / "val_features.csv")
    test_df = pd.read_csv(DATA_DIR / "test_features.csv")

    with open(_PROJECT_ROOT / "models" / "preprocessors" / "feature_names.json", "r") as f:
        feature_metadata = json.load(f)
    feature_cols = feature_metadata["feature_columns"]

    X_train = train_df[feature_cols]
    X_val = val_df[feature_cols]
    X_test = test_df[feature_cols]

    # Primary target for table comparison: 14-day forecast horizon
    eval_horizon = 14
    target_col = f"target_{eval_horizon}d"

    test_valid = ~test_df[target_col].isna()
    y_test = test_df.loc[test_valid, target_col].to_numpy()
    X_test_valid = X_test[test_valid]
    test_df_valid = test_df[test_valid]

    results_table = []
    trained_models = {}

    # -------------------------------------------------------------
    # Candidate 1: Naive (Persistence)
    # -------------------------------------------------------------
    start = time.time()
    naive = NaiveForecaster()
    y_pred_naive = naive.predict(test_df_valid)
    t_time = time.time() - start
    metrics_naive = compute_metrics(y_test, y_pred_naive)
    metrics_naive["Training_Time_s"] = round(t_time, 3)
    metrics_naive["Model"] = "Naive (Persistence)"
    results_table.append(metrics_naive)

    # -------------------------------------------------------------
    # Candidate 2: Moving Average (7d)
    # -------------------------------------------------------------
    start = time.time()
    ma7 = MovingAverageForecaster(window=7)
    y_pred_ma7 = ma7.predict(test_df_valid)
    t_time = time.time() - start
    metrics_ma7 = compute_metrics(y_test, y_pred_ma7)
    metrics_ma7["Training_Time_s"] = round(t_time, 3)
    metrics_ma7["Model"] = "Moving Average (7-Day)"
    results_table.append(metrics_ma7)

    # -------------------------------------------------------------
    # Candidate 3: Moving Average (14d)
    # -------------------------------------------------------------
    start = time.time()
    ma14 = MovingAverageForecaster(window=14)
    y_pred_ma14 = ma14.predict(test_df_valid)
    t_time = time.time() - start
    metrics_ma14 = compute_metrics(y_test, y_pred_ma14)
    metrics_ma14["Training_Time_s"] = round(t_time, 3)
    metrics_ma14["Model"] = "Moving Average (14-Day)"
    results_table.append(metrics_ma14)

    # -------------------------------------------------------------
    # Candidate 4: Random Forest
    # -------------------------------------------------------------
    rf = MultiHorizonForecaster(model_type="random_forest", params={"n_estimators": 80, "max_depth": 7})
    rf.fit(X_train, train_df, X_val, val_df, horizons=[eval_horizon])
    y_pred_rf = rf.predict_horizon(X_test_valid, horizon=eval_horizon)
    metrics_rf = compute_metrics(y_test, y_pred_rf)
    metrics_rf["Training_Time_s"] = round(rf.training_time_seconds, 3)
    metrics_rf["Model"] = "Random Forest Regressor"
    results_table.append(metrics_rf)

    # -------------------------------------------------------------
    # Candidate 5: LightGBM
    # -------------------------------------------------------------
    lgbm = MultiHorizonForecaster(model_type="lightgbm", params={"n_estimators": 150, "learning_rate": 0.05})
    lgbm.fit(X_train, train_df, X_val, val_df, horizons=[eval_horizon])
    y_pred_lgbm = lgbm.predict_horizon(X_test_valid, horizon=eval_horizon)
    metrics_lgbm = compute_metrics(y_test, y_pred_lgbm)
    metrics_lgbm["Training_Time_s"] = round(lgbm.training_time_seconds, 3)
    metrics_lgbm["Model"] = "LightGBM Regressor"
    results_table.append(metrics_lgbm)
    trained_models["lightgbm"] = lgbm

    # -------------------------------------------------------------
    # Candidate 6: XGBoost (Multi-Horizon Fit)
    # -------------------------------------------------------------
    xgb = MultiHorizonForecaster(model_type="xgboost", params={"n_estimators": 150, "learning_rate": 0.05, "max_depth": 5})
    # Fit across all horizons for production deployment
    xgb.fit(X_train, train_df, X_val, val_df, horizons=FORECAST_HORIZONS)
    y_pred_xgb, lower_xgb, upper_xgb = xgb.predict_with_interval(X_test_valid, horizon=eval_horizon, confidence_level=0.80)
    metrics_xgb = compute_metrics(y_test, y_pred_xgb)
    metrics_xgb["Training_Time_s"] = round(xgb.training_time_seconds, 3)
    metrics_xgb["Model"] = "XGBoost Regressor (Primary)"
    results_table.append(metrics_xgb)
    trained_models["xgboost"] = xgb

    # -------------------------------------------------------------
    # Save Model Comparison Table
    # -------------------------------------------------------------
    comparison_df = pd.DataFrame(results_table)[["Model", "MAE", "RMSE", "MAPE", "R2", "Training_Time_s"]]
    comparison_df = comparison_df.sort_values("MAE", ascending=True).reset_index(drop=True)

    json_path = REPORTS_DIR / "model_comparison.json"
    comparison_df.to_json(json_path, orient="records", indent=2)

    # Select best ML model for production deployment
    ml_models = comparison_df[comparison_df["Model"].str.contains("XGBoost|LightGBM|Random Forest")]
    best_ml_row = ml_models.sort_values(["RMSE", "MAE"], ascending=[True, True]).iloc[0]
    best_model_name = best_ml_row["Model"]

    if "LightGBM" in best_model_name:
        best_model = lgbm
        # Ensure it has all horizons
        lgbm.fit(X_train, train_df, X_val, val_df, horizons=FORECAST_HORIZONS)
    else:
        best_model = xgb

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    best_path = MODELS_DIR / "best_freight_model.joblib"
    joblib.dump(best_model, best_path)
    print(f"  [OK] Selected & Saved Best Model ({best_model_name}) -> {best_path}")

    # -------------------------------------------------------------
    # Generate Forecast vs Actual Plot
    # -------------------------------------------------------------
    # Pick sample trade route for clean time-series visualization
    sample_mask = (test_df_valid["route_id"] == "AU_COAL_PARADIP") & (test_df_valid["vessel_type"] == "Panamax")
    if sample_mask.sum() == 0:
        sample_mask = test_valid

    sub_test = test_df_valid[sample_mask].sort_values("date")
    sub_actual = sub_test[target_col].to_numpy()
    sub_pred, sub_lower, sub_upper = best_model.predict_with_interval(sub_test[feature_cols], horizon=eval_horizon)
    sub_dates = pd.to_datetime(sub_test["date"])

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(sub_dates, sub_actual, label="Actual Freight Rate ($/MT)", color="#1a73e8", linewidth=2.0)
    ax.plot(sub_dates, sub_pred, label=f"{best_model_name} (14d Forecast)", color="#0f9d58", linestyle="--", linewidth=2.0)
    ax.fill_between(
        sub_dates,
        sub_lower,
        sub_upper,
        color="#0f9d58",
        alpha=0.20,
        label="80% Prediction Interval (Uncertainty Corridor)",
    )

    ax.set_title(
        f"14-Day Freight Rate Forecast vs. Actual Ground Truth (Chronological Test Set)\nRoute: Australia -> Paradip (Panamax)",
        fontsize=12,
        fontweight="bold",
        pad=12,
    )
    ax.set_ylabel("Freight Rate ($ / MT)", fontsize=10)
    ax.set_xlabel("Test Timeline (2025 - 2026)", fontsize=10)
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)

    plot_path = FIGURES_DIR / "06_forecast_vs_actual.png"
    plt.tight_layout()
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"  [OK] Saved Forecast vs Actual plot -> {plot_path}")

    return {
        "comparison_table": comparison_df.to_dict(orient="records"),
        "best_model": best_model_name,
        "plot_path": str(plot_path),
    }


if __name__ == "__main__":
    res = evaluate_models()
    table = pd.DataFrame(res["comparison_table"])
    print("\n" + "=" * 70)
    print("  FreightMind AI — Model Comparison Table (14-Day Horizon, Test Split)")
    print("=" * 70)
    print(table.to_string(index=False))
    print("=" * 70)
    print(f"  Best Practical Model: {res['best_model']}\n")
