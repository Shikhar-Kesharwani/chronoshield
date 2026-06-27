# AnomalyWatch — Time-Series Anomaly Detection Dashboard

> **Real-time anomaly detection pipeline** over streaming time-series data using Redis Streams (or in-process mock), TimescaleDB / SQLite, rolling Z-Score and Isolation Forest detection, a live React dashboard, and configurable alerting.

---

## Architecture

```
Metric Generator ──► Stream (Redis / Mock Queue)
   (sine + noise,            │
    auto + manual            ▼
    anomaly injection)  Detection Worker
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
               Z-Score           Isolation Forest
           (rolling mean +    (trains on window,
            std-dev bands)     flags outliers)
                    │                 │
                    └────────┬────────┘
                             ▼
                    TimescaleDB / SQLite
                    (raw metrics + events)
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
               FastAPI SSE        Alert Manager
               (live stream)   (console / Slack)
                    │
                    ▼
             React Dashboard
          (live chart + comparison)
```

---

## Quick Start (No Docker Required)

> The project ships with **SQLite + in-process queue** mode — no Docker needed.

### 1. Start the Backend

```bat
start_backend.bat
```

This will:
- Create a Python virtual environment in `backend/.venv/`
- Install all dependencies from `backend/requirements.txt`
- Initialise the SQLite database
- Start the metric generator, detection worker, and FastAPI server on **http://localhost:8000**

### 2. Start the Frontend (new terminal)

```bat
start_frontend.bat
```

Opens the React dashboard at **http://localhost:5173**

### 3. Run Unit Tests

```bat
run_tests.bat
```

---

## Live Demo — Inject an Anomaly

1. Open the dashboard at `http://localhost:5173`
2. Wait ~60 seconds for the Z-Score detector to warm up
3. Click **"⚡ Inject Anomaly"** in the top-right
4. Watch the red dot appear on the chart within ~1 second
5. See the alert entry appear in the **Anomaly Events** panel

---

## Configuration

Edit `.env` in the project root:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_MODE` | `sqlite` | `sqlite` or `timescaledb` |
| `REDIS_MODE` | `mock` | `mock` (no Docker) or `real` (Redis required) |
| `ZSCORE_WINDOW` | `60` | Rolling window size (data points) |
| `ZSCORE_THRESHOLD` | `3.0` | Z-Score threshold (σ) for flagging |
| `IFOREST_WINDOW` | `200` | Training window for Isolation Forest |
| `IFOREST_CONTAMINATION` | `0.05` | Expected anomaly ratio (5%) |
| `ALERT_SEVERITY_THRESHOLD` | `0.7` | Min severity (0–1) to fire an alert |
| `ALERT_MODE` | `console` | `console` or `slack` |
| `SLACK_WEBHOOK_URL` | — | Slack Incoming Webhook URL |
| `GENERATOR_RATE` | `1.0` | Data points per second |
| `GENERATOR_ANOMALY_PROB` | `0.02` | Auto-inject probability (2%) |

---

## With Docker (Production-Grade)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bat
# Start Redis + TimescaleDB
docker-compose up -d

# Update .env
# DB_MODE=timescaledb
# REDIS_MODE=real

# Then start backend and frontend as above
start_backend.bat
start_frontend.bat
```

---

## Detection Methods

### Rolling Z-Score
- Maintains a sliding window of the last N data points
- Computes rolling mean (μ) and standard deviation (σ) in **O(1)** using running sums
- Flags points where |z| = |(x − μ) / σ| > threshold
- **Trade-off:** Fast, interpretable, adapts to drift — but assumes normality, struggles with seasonal patterns

### Isolation Forest
- Trains an ensemble of random decision trees on a historical window
- Points that are isolated quickly (short average path length) score as anomalies
- Features: `[value, delta]` — current reading + first derivative
- **Trade-off:** Handles multivariate / non-normal distributions, no stationarity assumption — but slower to train, less interpretable, needs warm-up data

### Precision / Recall Evaluation
- **Ground truth:** All manually injected spikes and auto-injected spikes are labelled (`injected=1`)
- The **Comparison** panel on the dashboard shows live precision/recall for both methods
- Tune `ZSCORE_THRESHOLD` to adjust false-positive/negative trade-off

---

## Project Structure

```
Time_Series_Detection/
├── .env                        # Configuration
├── docker-compose.yml          # Redis + TimescaleDB (optional)
├── start_backend.bat           # Windows: launch backend
├── start_frontend.bat          # Windows: launch frontend
├── run_tests.bat               # Windows: run unit tests
│
├── backend/
│   ├── api.py                  # FastAPI app (SSE + REST)
│   ├── worker.py               # Detection processing loop
│   ├── generator.py            # Synthetic metric generator
│   ├── alert_manager.py        # Console / Slack alerting
│   ├── config.py               # Centralised config from .env
│   ├── requirements.txt
│   ├── db/
│   │   ├── init_db.py          # Schema initialisation
│   │   └── store.py            # Read/write helpers
│   ├── detectors/
│   │   ├── zscore.py           # Rolling Z-Score detector
│   │   └── isolation_forest.py # Isolation Forest detector
│   └── tests/
│       └── test_zscore.py      # Pytest unit tests
│
└── frontend/
    ├── index.html
    ├── vite.config.js
    └── src/
        ├── App.jsx             # Main dashboard
        ├── index.css           # Design system
        ├── hooks/
        │   └── useMetricStream.js  # SSE + stats hook
        └── components/
            ├── LiveChart.jsx       # Recharts streaming chart
            ├── AlertFeed.jsx       # Anomaly event feed
            └── ComparisonPanel.jsx # Precision/recall comparison
```

---

## Resume Bullet

> Built a real-time anomaly detection pipeline over streaming time-series data using Redis Streams and TimescaleDB; implemented and benchmarked rolling Z-Score and Isolation Forest detection methods, measuring precision/recall trade-offs on a labeled evaluation set, with Slack alerting on threshold breach. Visualised results on a live React dashboard with Server-Sent Events streaming.
