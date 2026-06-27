<div align="center">

<!-- Waving animated gradient banner -->
![Banner](https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=220&section=header&text=ChronoShield&fontSize=60&fontColor=fff&animation=twinkling&fontAlignY=38&desc=Enterprise-Grade%20Time-Series%20Anomaly%20Detection&descAlignY=58&descSize=20)

<!-- Typing SVG -->
![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=800&size=28&duration=2500&pause=800&color=00E5FF&background=00000000&center=true&vCenter=true&multiline=true&repeat=true&width=800&height=120&lines=Dual-Model+Anomaly+Detection;Real-Time+Metric+Streaming;Dynamic+Threshold+Tuning;Automated+Slack+Alerts)

<div align="center">

![Stars](https://img.shields.io/github/stars/AyushGU12/chronoshield?style=for-the-badge&logo=github&color=6366f1)
![Forks](https://img.shields.io/github/forks/AyushGU12/chronoshield?style=for-the-badge&logo=github&color=8b5cf6)
![Issues](https://img.shields.io/github/issues/AyushGU12/chronoshield?style=for-the-badge&logo=github&color=ec4899)
![License](https://img.shields.io/github/license/AyushGU12/chronoshield?style=for-the-badge&color=f97316)
![Last Commit](https://img.shields.io/github/last-commit/AyushGU12/chronoshield?style=for-the-badge&color=14b8a6)

</div>

<br />

[🌐 Live Demo](#) &nbsp;&nbsp; [📖 Documentation](#) &nbsp;&nbsp; [🐛 Report Bug](https://github.com/AyushGU12/chronoshield/issues) &nbsp;&nbsp; [✨ Request Feature](https://github.com/AyushGU12/chronoshield/issues) &nbsp;&nbsp; [💬 Discussions](https://github.com/AyushGU12/chronoshield/discussions)

<svg width="700" height="120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="neon-glow">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <linearGradient id="neon-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00E5FF">
        <animate attributeName="stop-color"
                 values="#00E5FF;#ec4899;#f97316;#14b8a6;#00E5FF"
                 dur="4s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="#ec4899">
        <animate attributeName="stop-color"
                 values="#ec4899;#f97316;#14b8a6;#00E5FF;#ec4899"
                 dur="4s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>
  </defs>
  <rect width="700" height="120" rx="15" fill="#0d1117"/>
  <text x="350" y="75" text-anchor="middle" font-size="48"
        font-family="'Segoe UI', Arial Black" font-weight="900"
        fill="url(#neon-grad)" filter="url(#neon-glow)">
    ⚡ ChronoShield ⚡
  </text>
</svg>

</div>

---

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 120">
  <defs>
    <pattern id="hexbg" width="30" height="34.6" patternUnits="userSpaceOnUse">
      <polygon points="15,0 30,8.66 30,25.98 15,34.64 0,25.98 0,8.66"
               fill="none" stroke="#6366f1" stroke-width="0.4" opacity="0.25"/>
    </pattern>
    <linearGradient id="hgrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="#00E5FF"/>
      <stop offset="50%"  stop-color="#ec4899"/>
      <stop offset="100%" stop-color="#f97316"/>
    </linearGradient>
  </defs>
  <rect width="900" height="120" fill="#0d1117"/>
  <rect width="900" height="120" fill="url(#hexbg)"/>
  <text x="450" y="68" text-anchor="middle"
        font-size="36" fill="url(#hgrad)"
        font-family="'Segoe UI', Arial Black" font-weight="900">
    ✨ OVERVIEW ✨
  </text>
</svg>

**ChronoShield** is a real-time, high-performance time-series anomaly detection engine designed for observability and infrastructure monitoring. 

It ingests streaming telemetry data (CPU, memory, latency) and utilizes a dual-model machine learning architecture—combining the statistical rigor of **Adaptive Z-Scores** with the multidimensional robustness of **Isolation Forests**. When a metric deviates from baseline behavior, ChronoShield instantly flags the anomaly on a beautifully animated React dashboard and dispatches alerts via webhooks.

### 🎯 Problem It Solves
Traditional static threshold alerts cause alert fatigue. Server loads fluctuate dynamically based on time of day, making hard-coded thresholds useless. ChronoShield applies unsupervised machine learning to understand the "normal" sinusoidal heartbeat of your infrastructure, dynamically adapting its thresholds and catching true anomalies instantly without spamming your engineers.

### 👤 Target Users
SREs, DevOps Engineers, and System Administrators who need intelligent, zero-configuration anomaly detection for their cloud infrastructure.

---

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 120">
  <defs>
    <pattern id="hexbg2" width="30" height="34.6" patternUnits="userSpaceOnUse">
      <polygon points="15,0 30,8.66 30,25.98 15,34.64 0,25.98 0,8.66"
               fill="none" stroke="#6366f1" stroke-width="0.4" opacity="0.25"/>
    </pattern>
  </defs>
  <rect width="900" height="120" fill="#0d1117"/>
  <rect width="900" height="120" fill="url(#hexbg2)"/>
  <text x="450" y="68" text-anchor="middle"
        font-size="36" fill="url(#hgrad)"
        font-family="'Segoe UI', Arial Black" font-weight="900">
    ✨ SYSTEM ARCHITECTURE ✨
  </text>
</svg>

### 1. Full System Architecture

```mermaid
graph TB
    subgraph Client["🖥️ Client Layer"]
        WEB[🌐 React Dashboard]
    end

    subgraph API["🚪 API Layer"]
        FAST[⚡ FastAPI Server]
        SSE[📡 Server-Sent Events]
    end

    subgraph Processing["⚙️ Core Engine"]
        WORK[🔄 Worker Thread]
        GEN[📈 Data Generator]
    end

    subgraph Intelligence["🧠 AI/ML Layer"]
        ZSC[📊 Z-Score Detector]
        IFOR[🌲 Isolation Forest]
    end

    subgraph Data["🗄️ Data Layer"]
        DB[(🐘 SQLite / TimescaleDB)]
    end

    subgraph Observability["👁️ Observability"]
        SLACK[🚨 Slack Webhooks]
    end

    Client <-->|HTTP / SSE| API
    API <--> Processing
    Processing --> Intelligence
    Processing <--> Data
    Processing --> Observability

    style Client fill:#1e1b4b,color:#fff,stroke:#6366f1,stroke-width:2px
    style API fill:#1a1a2e,color:#fff,stroke:#ec4899,stroke-width:2px
    style Processing fill:#0f3460,color:#fff,stroke:#0ea5e9,stroke-width:2px
    style Intelligence fill:#2d1b4e,color:#fff,stroke:#a855f7,stroke-width:2px
    style Data fill:#16213e,color:#fff,stroke:#84cc16,stroke-width:2px
    style Observability fill:#1a0a00,color:#fff,stroke:#f97316,stroke-width:2px
```

### 2. Request Lifecycle & Inference Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor U as 👤 Generator
    participant Q as 📨 Queue
    participant W as ⚙️ Worker
    participant DB as 🗄️ Database
    participant ML as 🤖 Models
    participant A as 🚨 AlertManager
    participant F as 🌐 Frontend

    U->>Q: Push metric (cpu/mem/latency)
    Q->>W: Pop metric
    W->>ML: Evaluate Z-Score & iForest
    ML-->>W: Anomaly Scores
    W->>DB: Store Data + ML Result
    
    alt is_anomaly == True
        W->>A: Trigger Alert
        A->>Slack: Webhook POST
    end
    
    W->>F: Stream via SSE
    F-->>User: Visualise on Dashboard
```

### 3. Tech Distribution

```mermaid
pie title Technology Distribution
    "Backend Logic (FastAPI)" : 40
    "ML Engine (Scikit-Learn)": 25
    "Frontend (React/Vite)"   : 25
    "Database (SQLite)"       : 10
```

---

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 120">
  <defs>
    <pattern id="hexbg3" width="30" height="34.6" patternUnits="userSpaceOnUse">
      <polygon points="15,0 30,8.66 30,25.98 15,34.64 0,25.98 0,8.66"
               fill="none" stroke="#6366f1" stroke-width="0.4" opacity="0.25"/>
    </pattern>
  </defs>
  <rect width="900" height="120" fill="#0d1117"/>
  <rect width="900" height="120" fill="url(#hexbg3)"/>
  <text x="450" y="68" text-anchor="middle"
        font-size="36" fill="url(#hgrad)"
        font-family="'Segoe UI', Arial Black" font-weight="900">
    ✨ DIRECTORY STRUCTURE ✨
  </text>
</svg>

```text
📦 chronoshield
├── 📂 backend
│   ├── 📂 db
│   │   ├── 📜 init_db.py         ← Database initialisation
│   │   └── 📜 store.py           ← Persistence layer & data purging
│   ├── 📂 detectors
│   │   ├── 📜 isolation_forest.py← Scikit-Learn iForest detector
│   │   └── 📜 zscore.py          ← Adaptive rolling Z-Score detector
│   ├── 📂 tests                  ← Pytest suite
│   ├── 📜 alert_manager.py       ← Slack webhook integration
│   ├── 📜 api.py                 ← FastAPI server & SSE router
│   ├── 📜 config.py              ← Environment configuration
│   ├── 📜 generator.py           ← Multi-metric telemetry simulator
│   ├── 📜 requirements.txt       ← Python dependencies
│   └── 📜 worker.py              ← Core inference daemon & queue processing
├── 📂 frontend
│   ├── 📂 src
│   │   ├── 📂 components         ← React UI (Charts, Modals, KPIs)
│   │   ├── 📂 hooks              ← SSE streaming hooks
│   │   ├── 📜 App.jsx            ← Router & Layout
│   │   ├── 📜 index.css          ← Cyberpunk Glassmorphism styles
│   │   └── 📜 main.jsx           ← Entry point
│   ├── 📜 package.json           ← Node dependencies
│   └── 📜 vite.config.js         ← Vite build & proxy config
├── 📜 start_backend.bat          ← Launch script
└── 📜 start_frontend.bat         ← Launch script
```

---

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 120">
  <defs>
    <pattern id="hexbg4" width="30" height="34.6" patternUnits="userSpaceOnUse">
      <polygon points="15,0 30,8.66 30,25.98 15,34.64 0,25.98 0,8.66"
               fill="none" stroke="#6366f1" stroke-width="0.4" opacity="0.25"/>
    </pattern>
  </defs>
  <rect width="900" height="120" fill="#0d1117"/>
  <rect width="900" height="120" fill="url(#hexbg4)"/>
  <text x="450" y="68" text-anchor="middle"
        font-size="36" fill="url(#hgrad)"
        font-family="'Segoe UI', Arial Black" font-weight="900">
    ✨ INSTALLATION & CONFIG ✨
  </text>
</svg>

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔥 Step 1 — Clone repository
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
git clone https://github.com/AyushGU12/chronoshield.git
cd chronoshield

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ Step 2 — Backend Setup
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m db.init_db

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🖥️ Step 3 — Frontend Setup
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cd ../frontend
npm install

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 Step 4 — Launch servers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# In terminal 1:
.\start_backend.bat
# In terminal 2:
.\start_frontend.bat
```

### Environment Variables (`backend/.env`)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_MODE` | ❌ | `sqlite` | `sqlite` or `timescaledb` |
| `ALERT_MODE` | ❌ | `console` | Set to `slack` for webhooks |
| `SLACK_WEBHOOK_URL`| ⚡ | — | URL for slack notifications |
| `GENERATOR_RATE` | ❌ | `1.0` | Telemetry points per second |

---

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 120">
  <defs>
    <pattern id="hexbg5" width="30" height="34.6" patternUnits="userSpaceOnUse">
      <polygon points="15,0 30,8.66 30,25.98 15,34.64 0,25.98 0,8.66"
               fill="none" stroke="#6366f1" stroke-width="0.4" opacity="0.25"/>
    </pattern>
  </defs>
  <rect width="900" height="120" fill="#0d1117"/>
  <rect width="900" height="120" fill="url(#hexbg5)"/>
  <text x="450" y="68" text-anchor="middle"
        font-size="36" fill="url(#hgrad)"
        font-family="'Segoe UI', Arial Black" font-weight="900">
    ✨ KEY FEATURES & ML PIPELINE ✨
  </text>
</svg>

- **Warm Starts:** Pre-loads the last 200 data points on server boot, ensuring immediate model calibration and zero blind spots.
- **Dynamic Threshold Tuning:** Exposes an API endpoint (`POST /api/config`) to hot-swap model sensitivity parameters directly from the React UI without dropping streams.
- **Automated Data Purging:** Background workers execute intelligent TTL sweeps every hour, preventing SQLite/TimescaleDB bloat by dropping data older than 7 days.
- **Multivariate Tracking:** Independently trains rolling models for `cpu`, `memory`, and `latency` in isolated dictionaries within the worker loop.
- **Slack Alert Integration:** Instantly broadcasts severe anomalies (severity > 0.8) directly to your SRE Slack channel.

### ML Stack
<div align="center">
<img src="https://skillicons.dev/icons?i=python,react,vite,fastapi,sqlite,docker&theme=dark&perline=8"/>
</div>

---

![Footer](https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=140&section=footer&animation=twinkling)

<div align="center">

⭐ **Star this repo** if you found it useful! <br>
Made with ❤️ by [AyushGU12](https://github.com/AyushGU12)

</div>
