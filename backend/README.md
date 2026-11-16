# SupeRR Selector – Cricket Intelligence Backend

FastAPI Python analytical backend powering the **SupeRR Selector (Season 2 | Round 1)** cricket intelligence dashboard.

---

## 1. Quick Start

### Step 1: Activate Virtual Environment
```powershell
cd E:\SupeRR_Selector
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Required Dependencies
Dependencies are already configured. To verify or reinstall:
```powershell
pip install -r backend\requirements.txt
```

### Step 3: Launch FastAPI Server
From the project root:
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Or from the backend folder:
```powershell
cd E:\SupeRR_Selector\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Verify Health Endpoint
```powershell
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "ok",
  "version": "2.0.0",
  "project": "SupeRR Selector – Cricket Intelligence Platform",
  "datasets_loaded": true,
  "total_matches": 853,
  "total_pressure_deliveries": 103976
}
```

---

## 2. Interactive API Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

---

## 3. Endpoints Overview

| Category | Endpoint | Description |
|----------|----------|-------------|
| **General** | `GET /health` | System health and data loading status |
| **Overview** | `GET /api/v1/overview` | Platform-wide summary, formats, phases, and top 5 cards |
| **Batters** | `GET /api/v1/batters?format=T20` | Full batter rankings with search, sort & pagination |
| | `GET /api/v1/batters/top10?format=T20` | Exact verified Top 10 batters |
| | `GET /api/v1/batters/{player_id}` | Detailed batter profile and metric breakdown |
| **Bowlers** | `GET /api/v1/bowlers?format=T20` | Full bowler rankings with search, sort & pagination |
| | `GET /api/v1/bowlers/top10?format=T20` | Exact verified Top 10 bowlers |
| | `GET /api/v1/bowlers/{player_id}` | Detailed bowler profile and accounting sensitivity |
| **Pressure** | `GET /api/v1/pressure/summary` | Overall vs pressure performance comparison |
| | `GET /api/v1/pressure/categories` | Extreme, High, Moderate, Low breakdown |
| | `GET /api/v1/pressure/phases` | Powerplay, Middle, Death breakdown |
| | `GET /api/v1/pressure/batter-performance` | Player overall vs pressure batter splits |
| | `GET /api/v1/pressure/bowler-performance` | Player overall vs pressure bowler splits |
| **Matches** | `GET /api/v1/matches` | Filterable target match registry |
| | `GET /api/v1/matches/{match_id}` | Match detail metadata |
| | `GET /api/v1/matches/{match_id}/innings` | Innings scorecard breakdown |
| | `GET /api/v1/matches/{match_id}/pressure-timeline` | Ball-by-ball and over-by-over leverage timeline |
| **Comparison** | `GET /api/v1/compare/batters?player_ids=...` | Head-to-head batter matrix |
| | `GET /api/v1/compare/bowlers?player_ids=...` | Head-to-head bowler matrix |
| **Methodology** | `GET /api/v1/methodology` | Official analytical rules, formulas & weights |
| **Scenarios** | `GET /api/v1/scenarios/batters?format=T20` | Volume vs Efficiency vs Baseline rankings |
| | `GET /api/v1/scenarios/bowlers?format=T20` | Wicket Impact vs Control vs Baseline rankings |
| **Audit** | `GET /api/v1/audit/summary` | PASS, WARNING, NOT VERIFIED audit matrix |
| | `GET /api/v1/audit/data-quality` | Table diagnostics and documented limitations |
