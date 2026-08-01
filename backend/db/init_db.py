"""
db/init_db.py — Database initialisation
Supports TimescaleDB (Postgres) and SQLite (fallback, no Docker required).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
import sqlite3

from config import (DATABASE_URL, DB_MODE, SQLITE_PATH, TIMESCALE_DB, TIMESCALE_HOST,
                    TIMESCALE_PASS, TIMESCALE_PORT, TIMESCALE_USER)

log = logging.getLogger(__name__)

# ── Schema (identical for both engines, minus TimescaleDB hypertable) ─────────
_CREATE_METRICS = """
CREATE TABLE IF NOT EXISTS metrics (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TIMESTAMP NOT NULL,
    metric    TEXT      NOT NULL,
    value     REAL      NOT NULL,
    is_anomaly_zscore     INTEGER DEFAULT 0,
    is_anomaly_iforest    INTEGER DEFAULT 0,
    zscore_value          REAL,
    iforest_score         REAL,
    injected              INTEGER DEFAULT 0
);
"""

_CREATE_ANOMALIES = """
CREATE TABLE IF NOT EXISTS anomaly_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TIMESTAMP NOT NULL,
    metric      TEXT      NOT NULL,
    value       REAL      NOT NULL,
    detector    TEXT      NOT NULL,
    severity    REAL      NOT NULL,
    alerted     INTEGER   DEFAULT 0
);
"""


def get_connection():
    """Return a DB connection based on DB_MODE or DATABASE_URL."""
    if DATABASE_URL:
        try:
            import psycopg2
            # Connect using the dynamic connection string
            conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
            return conn
        except Exception as e:
            log.warning(f"Failed to connect to DATABASE_URL ({e}). Falling back to SQLite.")
            
    elif DB_MODE in ("timescaledb", "postgres"):
        try:
            import psycopg2

            conn = psycopg2.connect(
                host=TIMESCALE_HOST,
                port=TIMESCALE_PORT,
                dbname=TIMESCALE_DB,
                user=TIMESCALE_USER,
                password=TIMESCALE_PASS,
                connect_timeout=5,
            )
            return conn
        except Exception as e:
            log.warning(
                f"TimescaleDB/Postgres unavailable ({e}). Falling back to SQLite."
            )

    # SQLite fallback
    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables (and hypertable for TimescaleDB) if they don't exist."""
    conn = get_connection()

    if DATABASE_URL or DB_MODE in ("timescaledb", "postgres"):
        # Use psycopg2-compatible schema
        pg_metrics = (
            _CREATE_METRICS.replace(
                "INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY"
            )
            .replace("INTEGER DEFAULT 0", "SMALLINT DEFAULT 0")
            .replace("INTEGER   DEFAULT 0", "SMALLINT DEFAULT 0")
            .replace("TIMESTAMP", "TIMESTAMPTZ")
        )
        pg_anomalies = (
            _CREATE_ANOMALIES.replace(
                "INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY"
            )
            .replace("INTEGER   DEFAULT 0", "SMALLINT DEFAULT 0")
            .replace("TIMESTAMP", "TIMESTAMPTZ")
        )

        with conn:
            cur = conn.cursor()
            cur.execute(pg_metrics)
            cur.execute(pg_anomalies)
            # Create TimescaleDB hypertables (idempotent, fails safely if not Timescale extension)
            if DB_MODE == "timescaledb":
                for tbl in ("metrics", "anomaly_events"):
                    try:
                        cur.execute(f"""
                            SELECT create_hypertable('{tbl}', 'ts',
                                if_not_exists => TRUE,
                                migrate_data  => TRUE);
                        """)
                    except Exception as e:
                        log.warning(f"Hypertable creation failed, continuing as standard Postgres: {e}")
        log.info("Postgres/TimescaleDB tables ready.")
    else:
        with conn:
            conn.execute(_CREATE_METRICS)
            conn.execute(_CREATE_ANOMALIES)
        log.info(f"SQLite DB ready at {SQLITE_PATH}")

    conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    print("Database initialised successfully.")
