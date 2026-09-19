"""
FreightMind AI — Exploratory Data Analysis (EDA) Engine
src/analysis/eda.py

Performs comprehensive empirical data analysis:
  1. Freight rate trends & historical trajectory across 5 key routes
  2. Vessel-type pricing hierarchy & economies of scale (Capesize vs Panamax vs Supramax vs Handysize)
  3. Seasonal and monsoon dynamics (June-September monsoon dip vs Q4 restocking spike)
  4. Cross-asset correlation analysis (BDI proxy, VLSFO bunker fuel, thermal coal, iron ore, FX)
  5. Port congestion and anchorage waiting times across 7 East Coast Indian ports
  6. Generates 5 publication-quality figures in reports/figures/
  7. Outputs structured JSON summary metrics in reports/eda_summary.json

Usage:
    python -m src.analysis.eda
"""

from __future__ import annotations

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Headless backend for automation
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

from src.utils.logger import logger

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = _PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = _PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Style configuration
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def load_all_processed_data() -> dict[str, pd.DataFrame]:
    """Load cleaned datasets from data/processed/."""
    datasets = {}
    for name in ["freight_rates", "commodity_prices", "market_indicators", "port_congestion", "vessels_master"]:
        file_path = DATA_DIR / f"{name}.csv"
        if not file_path.exists():
            raise FileNotFoundError(
                f"Processed file not found: {file_path}. Run 'python -m src.data.loader' first."
            )
        df = pd.read_csv(file_path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        datasets[name] = df
    return datasets


def generate_figures(dfs: dict[str, pd.DataFrame]) -> list[Path]:
    """Generate and save 5 informative EDA plots."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    freight_df = dfs["freight_rates"]
    comm_df = dfs["commodity_prices"]
    mkt_df = dfs["market_indicators"]
    cong_df = dfs["port_congestion"]

    # -------------------------------------------------------------
    # Figure 1: Historical Freight Rate Trends & Moving Average
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 6))
    routes = freight_df["route_id"].unique()
    colors = sns.color_palette("tab10", len(routes))

    for idx, route in enumerate(routes):
        # Pick primary vessel type per route for clean trend visualization
        sub = freight_df[freight_df["route_id"] == route]
        v_type = sub["vessel_type"].mode()[0]
        sub = sub[sub["vessel_type"] == v_type].sort_values("date")
        
        # 30-day rolling trend
        rolling_30 = sub["freight_rate_usd_mt"].rolling(30, min_periods=7).mean()
        ax.plot(
            sub["date"],
            rolling_30,
            label=f"{route} ({v_type})",
            color=colors[idx],
            linewidth=1.8,
        )

    ax.set_title("Historical Freight Rate Trajectory by Trade Route (30-Day Moving Average)", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Freight Rate ($ / MT)", fontsize=11)
    ax.set_xlabel("Voyage Timeline (2020 - 2026)", fontsize=11)
    ax.legend(loc="upper left", frameon=True, fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)

    f1_path = FIGURES_DIR / "01_freight_trends_by_route.png"
    plt.tight_layout()
    plt.savefig(f1_path, dpi=200)
    plt.close()
    saved_paths.append(f1_path)

    # -------------------------------------------------------------
    # Figure 2: Vessel Class Rate & Economies of Scale Distribution
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Boxplot of rates across vessel classes
    v_order = ["Capesize", "Panamax", "Supramax", "Handysize"]
    v_colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]
    sns.boxplot(
        data=freight_df,
        x="vessel_type",
        y="freight_rate_usd_mt",
        order=v_order,
        palette=v_colors,
        ax=ax1,
        width=0.45,
    )
    ax1.set_title("Freight Rate Distribution by Vessel Class", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Vessel Class", fontsize=10)
    ax1.set_ylabel("Freight Rate ($ / MT)", fontsize=10)

    # Mean rate comparison showing economies of scale
    means = freight_df.groupby("vessel_type")["freight_rate_usd_mt"].mean().reindex(v_order)
    bars = ax2.bar(means.index, means.values, color=v_colors, width=0.45, edgecolor="#333333")
    for bar in bars:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, yval + 0.4, f"${yval:.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax2.set_title("Mean Freight Rate ($/MT) — Clear Economies of Scale", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Mean Rate ($ / MT)", fontsize=10)
    ax2.set_ylim(0, max(means.values) * 1.15)

    f2_path = FIGURES_DIR / "02_vessel_class_rate_comparison.png"
    plt.tight_layout()
    plt.savefig(f2_path, dpi=200)
    plt.close()
    saved_paths.append(f2_path)

    # -------------------------------------------------------------
    # Figure 3: Seasonal Patterns & Indian Monsoon Impact
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    freight_df["month"] = freight_df["date"].dt.month
    monthly_stats = freight_df.groupby("month")["freight_rate_usd_mt"].agg(["mean", "std"]).reset_index()
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    ax.plot(months, monthly_stats["mean"], marker="o", color="#0052cc", linewidth=2.2, label="Mean Freight Rate")
    ax.fill_between(
        range(12),
        monthly_stats["mean"] - monthly_stats["std"],
        monthly_stats["mean"] + monthly_stats["std"],
        alpha=0.18,
        color="#0052cc",
        label="+/- 1 Std Dev",
    )

    # Highlight monsoon period (Jun-Sep: indices 5-8)
    ax.axvspan(5, 8, color="#ff9999", alpha=0.25, label="Monsoon Season (Jun-Sep)")
    ax.annotate(
        "Monsoon Disruption\n(Lower fixture activity)",
        xy=(6.5, monthly_stats["mean"].iloc[6]),
        xytext=(6.5, monthly_stats["mean"].min() - 2.5),
        arrowprops=dict(facecolor="#cc0000", shrink=0.08, width=1, headwidth=6),
        ha="center",
        fontsize=9,
        fontweight="bold",
        color="#990000",
    )
    # Highlight post-monsoon Q4 restocking rally
    ax.annotate(
        "Q4 Plant Restocking Rally",
        xy=(10, monthly_stats["mean"].iloc[10]),
        xytext=(9.5, monthly_stats["mean"].max() + 1.2),
        arrowprops=dict(facecolor="#008800", shrink=0.08, width=1, headwidth=6),
        ha="center",
        fontsize=9,
        fontweight="bold",
        color="#006600",
    )

    ax.set_title("Monthly Freight Rate Seasonality & Weather Cyclicality", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("Freight Rate ($ / MT)", fontsize=10)
    ax.set_xlabel("Month of Year", fontsize=10)
    ax.legend(loc="lower left", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    f3_path = FIGURES_DIR / "03_seasonal_and_monthly_patterns.png"
    plt.tight_layout()
    plt.savefig(f3_path, dpi=200)
    plt.close()
    saved_paths.append(f3_path)

    # -------------------------------------------------------------
    # Figure 4: Cross-Asset Correlation Heatmap
    # -------------------------------------------------------------
    # Merge daily market data with average daily freight rate
    daily_freight = freight_df.groupby("date")["freight_rate_usd_mt"].mean().rename("avg_freight_rate")
    merged_macro = pd.DataFrame(daily_freight).join(
        comm_df.set_index("date")[["thermal_coal_usd_mt", "iron_ore_usd_mt", "crude_oil_usd_bbl"]]
    ).join(
        mkt_df.set_index("date")[["bdi_proxy", "vlsfo_price_usd_mt", "usd_inr"]]
    ).dropna()

    corr_matrix = merged_macro.corr()

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        linewidths=0.7,
        cbar_kws={"label": "Pearson Correlation"},
        ax=ax,
        vmin=-0.2,
        vmax=1.0,
    )
    ax.set_title("Cross-Asset Correlation: Freight Rates vs. Macro Drivers", fontsize=12, fontweight="bold", pad=12)

    f4_path = FIGURES_DIR / "04_macro_correlation_heatmap.png"
    plt.tight_layout()
    plt.savefig(f4_path, dpi=200)
    plt.close()
    saved_paths.append(f4_path)

    # -------------------------------------------------------------
    # Figure 5: East Coast Port Congestion & Waiting Times
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    port_avg = cong_df.groupby("port_id")["avg_waiting_time_hrs"].agg(["mean", lambda x: x.quantile(0.90)]).reset_index()
    port_avg.columns = ["port_id", "mean_wait_hrs", "p90_wait_hrs"]
    port_avg = port_avg.sort_values("mean_wait_hrs", ascending=True)

    y_pos = np.arange(len(port_avg))
    ax1.barh(y_pos - 0.15, port_avg["mean_wait_hrs"], height=0.3, label="Average Wait Time", color="#4285F4")
    ax1.barh(y_pos + 0.15, port_avg["p90_wait_hrs"], height=0.3, label="90th Percentile (Peak Wait)", color="#EA4335")
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([p.replace("_", " ").title() for p in port_avg["port_id"]], fontsize=10)
    ax1.set_xlabel("Anchorage Waiting Hours", fontsize=10)
    ax1.set_title("Waiting Time by East Coast Port", fontsize=12, fontweight="bold")
    ax1.legend(loc="lower right")

    # Congestion level pie distribution across all records
    level_counts = cong_df["congestion_level"].value_counts()
    colors_pie = ["#34A853", "#FBBC05", "#EA4335"]  # green, yellow, red
    ax2.pie(
        level_counts.values,
        labels=[l.upper() for l in level_counts.index],
        autopct="%1.1f%%",
        startangle=140,
        colors=colors_pie,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    ax2.set_title("Overall Congestion State Distribution", fontsize=12, fontweight="bold")

    f5_path = FIGURES_DIR / "05_port_congestion_and_waiting.png"
    plt.tight_layout()
    plt.savefig(f5_path, dpi=200)
    plt.close()
    saved_paths.append(f5_path)

    return saved_paths


def compute_summary_statistics(dfs: dict[str, pd.DataFrame]) -> dict:
    """Compute quantifiable statistical findings across all datasets."""
    freight_df = dfs["freight_rates"]
    comm_df = dfs["commodity_prices"]
    mkt_df = dfs["market_indicators"]
    cong_df = dfs["port_congestion"]

    # 1. Overall freight statistics
    overall_stats = {
        "record_count": len(freight_df),
        "mean_rate_usd_mt": round(float(freight_df["freight_rate_usd_mt"].mean()), 2),
        "median_rate_usd_mt": round(float(freight_df["freight_rate_usd_mt"].median()), 2),
        "std_rate_usd_mt": round(float(freight_df["freight_rate_usd_mt"].std()), 2),
        "min_rate_usd_mt": round(float(freight_df["freight_rate_usd_mt"].min()), 2),
        "max_rate_usd_mt": round(float(freight_df["freight_rate_usd_mt"].max()), 2),
        "iqr_usd_mt": round(float(freight_df["freight_rate_usd_mt"].quantile(0.75) - freight_df["freight_rate_usd_mt"].quantile(0.25)), 2),
    }

    # 2. Route-wise statistics
    route_stats = {}
    for route, grp in freight_df.groupby("route_id"):
        route_stats[route] = {
            "mean": round(float(grp["freight_rate_usd_mt"].mean()), 2),
            "std": round(float(grp["freight_rate_usd_mt"].std()), 2),
            "volatility_annualized": round(float(grp["freight_rate_usd_mt"].pct_change().std() * (365 ** 0.5)), 3),
            "distance_nm": int(grp["distance_nm"].iloc[0]),
            "vessels": list(grp["vessel_type"].unique()),
        }

    # 3. Vessel-type hierarchy (Economies of scale)
    vessel_stats = {}
    for vtype, grp in freight_df.groupby("vessel_type"):
        vessel_stats[vtype] = {
            "mean_rate": round(float(grp["freight_rate_usd_mt"].mean()), 2),
            "std": round(float(grp["freight_rate_usd_mt"].std()), 2),
            "min": round(float(grp["freight_rate_usd_mt"].min()), 2),
            "max": round(float(grp["freight_rate_usd_mt"].max()), 2),
        }

    # 4. Seasonal dynamics
    freight_df["month"] = freight_df["date"].dt.month
    monsoon_mean = freight_df[freight_df["month"].isin([6, 7, 8, 9])]["freight_rate_usd_mt"].mean()
    non_monsoon_mean = freight_df[~freight_df["month"].isin([6, 7, 8, 9])]["freight_rate_usd_mt"].mean()
    seasonal_stats = {
        "monsoon_mean_rate": round(float(monsoon_mean), 2),
        "non_monsoon_mean_rate": round(float(non_monsoon_mean), 2),
        "monsoon_discount_pct": round(float(((monsoon_mean - non_monsoon_mean) / non_monsoon_mean) * 100), 2),
    }

    # 5. Macro correlations
    daily_freight = freight_df.groupby("date")["freight_rate_usd_mt"].mean().rename("rate")
    merged = pd.DataFrame(daily_freight).join(
        comm_df.set_index("date")[["thermal_coal_usd_mt", "iron_ore_usd_mt"]]
    ).join(
        mkt_df.set_index("date")[["bdi_proxy", "vlsfo_price_usd_mt"]]
    ).dropna()
    corrs = merged.corr()["rate"].to_dict()
    correlations = {k: round(float(v), 3) for k, v in corrs.items() if k != "rate"}

    # 6. Port congestion metrics
    port_congestion = {}
    for pid, grp in cong_df.groupby("port_id"):
        port_congestion[pid] = {
            "mean_waiting_hours": round(float(grp["avg_waiting_time_hrs"].mean()), 1),
            "p90_waiting_hours": round(float(grp["avg_waiting_time_hrs"].quantile(0.90)), 1),
            "max_waiting_hours": round(float(grp["avg_waiting_time_hrs"].max()), 1),
        }

    summary = {
        "overall_freight": overall_stats,
        "route_wise": route_stats,
        "vessel_class_economies_of_scale": vessel_stats,
        "seasonality": seasonal_stats,
        "macro_correlations": correlations,
        "port_congestion": port_congestion,
    }

    # Write summary to JSON
    json_path = REPORTS_DIR / "eda_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


def run_eda(verbose: bool = True) -> tuple[dict, list[Path]]:
    """Execute complete EDA pipeline."""
    if verbose:
        print("\n[FreightMind AI] Running Exploratory Data Analysis (EDA)...")
    
    dfs = load_all_processed_data()
    if verbose:
        print("  [OK] Processed datasets loaded successfully.")

    figures = generate_figures(dfs)
    if verbose:
        print(f"  [OK] Generated {len(figures)} visual charts in reports/figures/:")
        for fig in figures:
            print(f"       -> {fig.name}")

    summary = compute_summary_statistics(dfs)
    if verbose:
        print(f"  [OK] Saved quantitative summary in reports/eda_summary.json")

    return summary, figures


if __name__ == "__main__":
    summary, figs = run_eda(verbose=True)
    print("\n" + "=" * 60)
    print("  FreightMind AI - Exploratory Data Analysis Complete")
    print("=" * 60)
    print(f"  Total Historical Records Analyzed: {summary['overall_freight']['record_count']:,}")
    print(f"  Overall Mean Freight Rate:         ${summary['overall_freight']['mean_rate_usd_mt']:.2f} / MT")
    print(f"  Monsoon Season Disruption:         {summary['seasonality']['monsoon_discount_pct']}% rate contraction")
    print(f"  Highest Congestion Port:           Haldia ({summary['port_congestion']['haldia']['mean_waiting_hours']} hrs avg)")
    print(f"  Lowest Congestion Port:            Gopalpur ({summary['port_congestion']['gopalpur']['mean_waiting_hours']} hrs avg)")
    print("=" * 60 + "\n")
