"""
config.py — Centralised configuration loaded from .env
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (one level above backend/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

# ── Database ──────────────────────────────────────────────────────────────────
DB_MODE = os.getenv("DB_MODE", "sqlite")  # "sqlite" | "timescaledb"

TIMESCALE_HOST = os.getenv("TIMESCALE_HOST", "localhost")
TIMESCALE_PORT = int(os.getenv("TIMESCALE_PORT", "5432"))
TIMESCALE_DB = os.getenv("TIMESCALE_DB", "anomaly_detection")
TIMESCALE_USER = os.getenv("TIMESCALE_USER", "tsuser")
TIMESCALE_PASS = os.getenv("TIMESCALE_PASSWORD", "tspassword")

SQLITE_PATH = str(Path(__file__).resolve().parent / "anomaly_detection.db")

# ── Redis / Stream ────────────────────────────────────────────────────────────
REDIS_MODE = os.getenv("REDIS_MODE", "mock")  # "mock" | "real"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_STREAM_KEY = os.getenv("REDIS_STREAM_KEY", "metrics_stream")

# ── Anomaly Detection ─────────────────────────────────────────────────────────
ZSCORE_WINDOW = int(os.getenv("ZSCORE_WINDOW", "60"))
ZSCORE_THRESHOLD = float(os.getenv("ZSCORE_THRESHOLD", "3.0"))
IFOREST_WINDOW = int(os.getenv("IFOREST_WINDOW", "200"))
IFOREST_CONTAMINATION = float(os.getenv("IFOREST_CONTAMINATION", "0.05"))

# ── Alerting ──────────────────────────────────────────────────────────────────
ALERT_SEVERITY_THRESHOLD = float(os.getenv("ALERT_SEVERITY_THRESHOLD", "0.7"))
ALERT_MODE = os.getenv("ALERT_MODE", "console")  # "console" | "slack"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# ── Generator ─────────────────────────────────────────────────────────────────
GENERATOR_RATE = float(os.getenv("GENERATOR_RATE", "1.0"))
GENERATOR_ANOMALY_PROB = float(os.getenv("GENERATOR_ANOMALY_PROB", "0.02"))

# ── API ───────────────────────────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
    ).split(",")
]
