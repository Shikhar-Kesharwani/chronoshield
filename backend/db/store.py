"""
db/store.py — Database write/read helpers (SQLite & TimescaleDB compatible)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import sqlite3
import logging
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any

from config import DB_MODE
from db.init_db import get_connection

log = logging.getLogger(__name__)

# Thread-local SQLite connection pool (SQLite is not safe across threads)
_local = threading.local()


def _get_conn():
    if DB_MODE != "timescaledb":
        if not hasattr(_local, "conn") or _local.conn is None:
            _local.conn = get_connection()
        return _local.conn
    return get_connection()


def _close_pg(conn):
    if DB_MODE == "timescaledb":
        conn.close()


# ── Write helpers ──────────────────────────────────────────────────────────────

def insert_metric(
    ts: datetime,
    metric: str,
    value: float,
    is_anomaly_zscore: bool = False,
    is_anomaly_iforest: bool = False,
    zscore_value: Optional[float] = None,
    iforest_score: Optional[float] = None,
    injected: bool = False,
) -> None:
    conn = _get_conn()
    ph = "%s" if DB_MODE == "timescaledb" else "?"
    sql = f"""
        INSERT INTO metrics
            (ts, metric, value, is_anomaly_zscore, is_anomaly_iforest,
             zscore_value, iforest_score, injected)
        VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})
    """
    params = (
        ts.isoformat(),
        metric,
        value,
        int(is_anomaly_zscore),
        int(is_anomaly_iforest),
        zscore_value,
        iforest_score,
        int(injected),
    )
    try:
        with conn:
            conn.execute(sql, params)
    except Exception as e:
        log.error(f"insert_metric error: {e}")
    finally:
        _close_pg(conn)


def insert_anomaly_event(
    ts: datetime,
    metric: str,
    value: float,
    detector: str,
    severity: float,
    alerted: bool = False,
) -> None:
    conn = _get_conn()
    ph = "%s" if DB_MODE == "timescaledb" else "?"
    sql = f"""
        INSERT INTO anomaly_events (ts, metric, value, detector, severity, alerted)
        VALUES ({ph},{ph},{ph},{ph},{ph},{ph})
    """
    try:
        with conn:
            conn.execute(sql, (ts.isoformat(), metric, value, detector, severity, int(alerted)))
    except Exception as e:
        log.error(f"insert_anomaly_event error: {e}")
    finally:
        _close_pg(conn)


# ── Read helpers ───────────────────────────────────────────────────────────────

def _row_to_dict(row) -> Dict[str, Any]:
    if isinstance(row, sqlite3.Row):
        return dict(row)
    # psycopg2 returns tuples — caller must pass column names
    return row


def fetch_metrics(
    metric: str = "cpu",
    limit: int = 300,
    since_ts: Optional[str] = None,
) -> List[Dict[str, Any]]:
    conn = _get_conn()
    ph = "%s" if DB_MODE == "timescaledb" else "?"
    if since_ts:
        sql = f"""
            SELECT ts, metric, value, is_anomaly_zscore, is_anomaly_iforest,
                   zscore_value, iforest_score, injected
            FROM metrics
            WHERE metric={ph} AND ts > {ph}
            ORDER BY ts ASC LIMIT {ph}
        """
        params = (metric, since_ts, limit)
    else:
        sql = f"""
            SELECT ts, metric, value, is_anomaly_zscore, is_anomaly_iforest,
                   zscore_value, iforest_score, injected
            FROM metrics
            WHERE metric={ph}
            ORDER BY ts DESC LIMIT {ph}
        """
        params = (metric, limit)
    try:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        if DB_MODE == "timescaledb":
            cols = [d[0] for d in cur.description]
            result = [dict(zip(cols, r)) for r in rows]
        else:
            result = [dict(r) for r in rows]
        return result if since_ts else list(reversed(result))
    except Exception as e:
        log.error(f"fetch_metrics error: {e}")
        return []
    finally:
        _close_pg(conn)


def fetch_anomaly_events(limit: int = 50) -> List[Dict[str, Any]]:
    conn = _get_conn()
    ph = "%s" if DB_MODE == "timescaledb" else "?"
    sql = f"""
        SELECT ts, metric, value, detector, severity, alerted
        FROM anomaly_events
        ORDER BY ts DESC LIMIT {ph}
    """
    try:
        cur = conn.execute(sql, (limit,))
        rows = cur.fetchall()
        if DB_MODE == "timescaledb":
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in rows]
        return [dict(r) for r in rows]
    except Exception as e:
        log.error(f"fetch_anomaly_events error: {e}")
        return []
    finally:
        _close_pg(conn)


def fetch_detector_stats(metric: str = "cpu") -> Dict[str, Any]:
    """Return precision/recall-like stats for the labeled evaluation window."""
    conn = _get_conn()
    ph = "%s" if DB_MODE == "timescaledb" else "?"
    sql = f"""
        SELECT
            SUM(injected)                                        AS total_injected,
            SUM(is_anomaly_zscore)                              AS zscore_detected,
            SUM(is_anomaly_iforest)                             AS iforest_detected,
            SUM(CASE WHEN injected=1 AND is_anomaly_zscore=1  THEN 1 ELSE 0 END) AS zscore_tp,
            SUM(CASE WHEN injected=1 AND is_anomaly_iforest=1 THEN 1 ELSE 0 END) AS iforest_tp,
            SUM(CASE WHEN injected=0 AND is_anomaly_zscore=1  THEN 1 ELSE 0 END) AS zscore_fp,
            SUM(CASE WHEN injected=0 AND is_anomaly_iforest=1 THEN 1 ELSE 0 END) AS iforest_fp,
            COUNT(*)                                            AS total
        FROM metrics WHERE metric={ph}
    """
    try:
        cur = conn.execute(sql, (metric,))
        row = cur.fetchone()
        if row is None:
            return {}
        if DB_MODE == "timescaledb":
            cols = [d[0] for d in cur.description]
            d = dict(zip(cols, row))
        else:
            d = dict(row)

        def _safe(num, den):
            return round(num / den, 4) if den else 0.0

        ti  = d.get("total_injected") or 0
        zd  = d.get("zscore_detected") or 0
        ifd = d.get("iforest_detected") or 0
        ztp = d.get("zscore_tp") or 0
        itp = d.get("iforest_tp") or 0
        zfp = d.get("zscore_fp") or 0
        ifp = d.get("iforest_fp") or 0

        return {
            "total_points": d.get("total") or 0,
            "total_injected": ti,
            "zscore": {
                "detected": zd,
                "tp": ztp,
                "fp": zfp,
                "fn": ti - ztp,
                "precision": _safe(ztp, ztp + zfp),
                "recall": _safe(ztp, ti),
            },
            "iforest": {
                "detected": ifd,
                "tp": itp,
                "fp": ifp,
                "fn": ti - itp,
                "precision": _safe(itp, itp + ifp),
                "recall": _safe(itp, ti),
            },
        }
    except Exception as e:
        log.error(f"fetch_detector_stats error: {e}")
        return {}
    finally:
        _close_pg(conn)
