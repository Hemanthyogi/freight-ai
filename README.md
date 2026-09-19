# FreightMind AI

> **AI-Powered Maritime Freight Forecasting & Vessel Charter Optimization**
> Smart India Hackathon 2026 | Problem Statement 26006

---

## Overview

FreightMind AI is an intelligent decision-support system for maritime logistics managers. It combines freight rate forecasting, vessel optimization, port feasibility checking, risk analysis, and explainable AI recommendations into a single professional dashboard.

**It answers 8 core questions before a chartering decision:**
1. What will freight rates likely be?
2. When is the best time to enter the charter market?
3. Which vessel type is most suitable?
4. Can the vessel safely use origin/destination ports?
5. What is the expected idle/waiting risk?
6. What risks could affect the voyage?
7. Spot or multiple-voyage contract?
8. What action should the manager take?

---

## ⚠️ Demo Mode

This prototype uses **clearly-labelled synthetic/demo data** when `DEMO_MODE=true`.

All synthetic data is:
- Statistically calibrated to resemble real bulk freight market behaviour
- **NOT** official Baltic Exchange, Clarkson's, or market data
- Clearly labelled `data_source=DEMO_DATA` in every dataset row

The system is designed so real data can replace demo data with zero code changes.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | FastAPI (Python 3.11+) |
| ML Models | XGBoost, LightGBM, SARIMA, scikit-learn |
| Explainability | SHAP |
| Frontend | React 18 + Vite + Tailwind CSS |
| Charts | Recharts |
| Maps | React-Leaflet |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Containerization | Docker + docker-compose |

---

## Quick Start

### 1. Clone and set up environment

```bash
cd freightmind-ai
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env if needed — DEMO_MODE=true by default
```

### 3. Generate synthetic demo data

```bash
python -m src.data.synthetic_generator
```

Expected output:
```
Generating freight_rates...  ✓  ~13,000 rows
Generating commodity_prices... ✓  ~2,418 rows
Generating market_indicators... ✓  ~2,418 rows
Generating port_congestion... ✓  ~16,926 rows
Generating vessels_master... ✓  20 rows
```

### 4. Run the data pipeline

```bash
python -m src.data.loader
```

### 5. Start the backend API

```bash
uvicorn backend.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 6. Start the frontend dashboard

```bash
cd frontend
npm install
npm run dev
```

Dashboard available at: http://localhost:5173

### 7. Or launch the full stack with one command (Windows PowerShell)

```powershell
.\scripts\run_all.ps1
```

---

## Project Structure

```
freightmind-ai/
├── data/
│   ├── synthetic/      ← Statistically calibrated demo data (DEMO_DATA)
│   └── processed/      ← Cleaned & validated features (29,028 rows)
├── src/
│   ├── data/           ← Synthetic generator, validator, cleaner, loader
│   ├── features/       ← 58 lag, rolling, cyclical & market features
│   ├── forecasting/    ← XGBoost, LightGBM, Random Forest, Baselines
│   ├── optimization/   ← Port feasibility, voyage cost, vessel optimizer
│   ├── risk/           ← Congestion, idle time, freight volatility risk
│   ├── recommendations/← Spot vs multi-voyage contract strategies
│   └── utils/          ← Config, logger, constants
├── backend/            ← FastAPI app (7 routers + orchestrator)
├── frontend/           ← React 18 + Vite + Tailwind CSS dashboard
├── models/             ← Serialized best model & feature scaler
├── reports/            ← EDA plots, comparison tables & charts
├── scripts/            ← PowerShell full-stack launch scripts
└── tests/              ← 49 passing pytest unit & integration tests
```

---

## Development Phases & Deliverables

| Phase | Description | Status | Verification |
|---|---|:---:|---|
| **Phase 1** | Requirements & Architecture | ✅ Completed | Complete schema & config registry |
| **Phase 2** | Synthetic Data Generator & Cleaner | ✅ Completed | 29,388 rows, calibrated mean-reverting AR(1) |
| **Phase 3** | Exploratory Data Analysis (EDA) | ✅ Completed | 5 publication figures & statistical insights |
| **Phase 4** | Feature Engineering Pipeline | ✅ Completed | 58 predictive features, 0 lookahead leakage |
| **Phase 5–6** | Multi-Horizon ML Forecasting Models | ✅ Completed | XGBoost multi-horizon (7d, 14d, 30d, 60d, 90d) |
| **Phase 7** | Model Evaluation & Benchmarking | ✅ Completed | XGBoost best model ($R^2=0.8192$, RMSE $1.259) |
| **Phase 8–12** | Decision & Risk Engines | ✅ Completed | Feasibility, cost, timing, risk, contract |
| **Phase 13** | FastAPI Backend & Orchestrator | ✅ Completed | 7 endpoints + master orchestration |
| **Phase 14–15** | React 18 + Vite Frontend Dashboard | ✅ Completed | 10 interactive widgets matching UI reference |
| **Phase 16** | End-to-End Verification & SIH Demo | ✅ Completed | 49/49 pytest suite passing, full stack active |

---

## SIH Demo Scenario

- **Corridor:** Balikpapan (Indonesia) → Malacca Strait → Bay of Bengal → Paradip Port
- **Cargo:** Iron Ore / Bulk Coal (250,000 MT)
- **AI Recommendation:** Multi-Voyage Charter fixture with *MV Ocean Crest* (Supramax, 58,000 DWT)
- **Projected Landed Savings:** **~$228,000** landed cost savings vs spot fixture
- **Chartering Window:** Within 7 – 10 Days (Neutral/Favorable entry signal)

---

## License

Developed for Smart India Hackathon 2026 (Problem Statement 26006). All demo datasets are clearly tagged `DEMO_DATA` / `is_synthetic=True`.
