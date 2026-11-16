# SupeRR Selector – Cricket Intelligence Platform (Season 2 | Round 1)

A professional cricket analytics platform engineered for the **Rajasthan Royals (RR)** hackathon. This monorepo includes a high-performance **Python FastAPI backend** and a modern **React / TanStack Start dashboard**.

---

## 🏏 Overview

The platform evaluates cricket performance under pressure across both **T20 (IPL)** and **T20I** competitions using verified match situations, ball-by-ball leverage indices, and robust statistical models.

### Key Capabilities
- **FastAPI Analytical Engine**: In-memory dataset caching (~175 MB footprint) over 13 CSV datasets (853 matches, 193,988 deliveries, 103,976 pressure balls).
- **Verified Ranking Reproducibility**: 100% exact match against verified Top 10 T20 & T20I batter and bowler baseline rankings.
- **Pressure Leverage Studio**: Category breakdown (Moderate, High, Extreme) and phase-wise dynamics (Powerplay, Middle, Death overs).
- **Player Comparison Matrix**: Side-by-side percentile radar comparisons with leader badges.
- **Scenario Sensitivity Simulator**: Test alternative weighting frameworks (Volume-focused vs Efficiency-focused) and Bowler Accounting Sensitivity (Scenario A baseline vs Scenario B with all extras).
- **Data Governance Audit**: Comprehensive checklist tracking 100% verified checks, known warnings, and limitations.

---

## 🏗️ Monorepo Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application entrypoint & CORS middleware
│   │   ├── core/config.py              # Centralized environment & path resolution
│   │   ├── services/
│   │   │   ├── data_loader.py          # Centralized in-memory dataset cache
│   │   │   ├── overview_service.py     # Aggregates KPIs, distributions & Top 5
│   │   │   ├── batter_service.py       # Batter rankings, filtering, search & pagination
│   │   │   ├── bowler_service.py       # Bowler rankings & corrected legal ball denominators
│   │   │   ├── pressure_service.py     # Delivery leverage distributions & phase dynamics
│   │   │   ├── match_service.py        # Match metadata, innings & over-by-over timelines
│   │   │   ├── comparison_service.py   # Multi-player metric & percentile radar matrices
│   │   │   ├── scenario_service.py     # Sensitivity analyses & Bowler Scenario A vs B
│   │   │   ├── methodology_service.py  # Weights, eligibility rules & scoring formulas
│   │   │   └── audit_service.py        # System audit checkpoints & data quality metrics
│   │   ├── api/routes/                 # Versioned REST controllers (/api/v1)
│   │   └── schemas/                    # Pydantic v2 schemas
│   ├── tests/
│   │   ├── test_api.py                 # 14 comprehensive automated integration tests
│   │   └── verify_all.py               # Complete service endpoint verification runner
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── analytics-api.ts        # Direct FastAPI REST client & data normalizer
│   │   │   └── dashboard-context.tsx   # Singleton state, theme, format & search context
│   │   ├── components/
│   │   │   └── analytics-section.tsx   # Interactive visual modules
│   │   └── routes/
│   │       └── _dashboard.tsx          # Responsive layout, navigation & live health badge
│   ├── vite.config.ts                  # Vite + TanStack Start configuration with reverse proxy
│   ├── vercel.json                     # Vercel deployment configuration
│   └── package.json
├── data/
│   ├── raw/                            # ball_by_ball.csv, matches.csv, teams.csv, etc.
│   └── processed/                      # pressure_classified.csv, target_matches.csv, etc.
├── outputs/                            # Baseline ranking CSVs & Top 10 outputs
├── render.yaml                         # 1-click Render backend deployment blueprint
└── README.md
```

---

## ⚡ Quick Start

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Unix: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Health: `http://localhost:8000/health`
- Interactive Swagger UI: `http://localhost:8000/docs`

### 2. Frontend (React / Vite)
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev -- --host --port 8080
```
- Dashboard UI: `http://localhost:8080`

---

## 📐 Analytical Methodology

### Batter Eligibility & Weights
- **Sample Cutoff**: Minimum 100 pressure balls and minimum 10 pressure matches.
- **Baseline Weights**:
  - Pressure Strike Rate: 25% (higher is better)
  - Runs Per Match: 20% (higher is better)
  - Runs Per Dismissal: 15% (higher is better)
  - Dot Percentage: 15% (lower is better)
  - Consistency: 25% (60% based on 10+ runs; 40% based on 20+ runs)

### Bowler Eligibility & Weights
- **Sample Cutoff**: Minimum 60 pressure legal balls and minimum 10 verified pressure matches (matches with >= 1 legal pressure delivery).
- **Baseline Weights**:
  - Wickets Per 100 Legal Balls: 25% (higher is better)
  - Economy Rate: 20% (lower is better)
  - Dot Percentage: 15% (higher is better)
  - Consistency: 20% (70% based on 1+ wickets; 30% based on 2+ wickets)
  - Corrected Wickets Per Match: 20% (higher is better)

---

## 🧪 Verification & Automated Testing

All 14 backend test suites pass with 100% exact match against verified baseline ranking files:
```bash
cd backend
python tests/test_api.py
```
To verify all 17 live frontend and backend endpoints:
```bash
python tests/verify_all.py
```
Frontend lint & build verification:
```bash
cd frontend
npm run lint
npm run build
```

---

## 🚢 Deployment

- **Frontend on Vercel**: Import repository root, set root directory to `frontend/`, and output to `dist/client`.
- **Backend on Render**: Connect repository and deploy via `render.yaml` with runtime `Python 3`. Set `VITE_API_BASE_URL` on frontend to point to the backend service.
