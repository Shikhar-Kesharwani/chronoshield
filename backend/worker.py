"""
worker.py — Core detection processing loop

Flow:
  1. Read next message from the stream (Redis or mock queue).
  2. Run both detectors (Z-Score + Isolation Forest).
  3. Persist the raw metric + detection flags to the DB.
  4. If anomaly detected, persist anomaly event + trigger alert.
  5. Push the fully-enriched data point onto a shared in-process
     deque so SSE subscribers in api.py can pick it up instantly.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import logging
import threading
import time
from collections import deque
from datetime import datetime
from typing import Any, Dict

from alert_manager import maybe_alert
from db.store import (fetch_metrics, insert_anomaly_event, insert_metric,
                      purge_old_data)
from detectors.isolation_forest import IsolationForestDetector
from detectors.zscore import ZScoreDetector
from generator import read_next

log = logging.getLogger(__name__)

# ── Shared SSE broadcast buffer ───────────────────────────────────────────────
# api.py subscribes to this deque for live streaming to clients.
_sse_buffer: deque = deque(maxlen=500)
_sse_lock = threading.Lock()
_sse_subscribers: list = []  # list of threading.Event objects


def _broadcast(point: Dict[str, Any]):
    """Append point to SSE buffer and wake all waiting subscribers."""
    with _sse_lock:
        _sse_buffer.append(point)
        for ev in _sse_subscribers:
            ev.set()


def subscribe_sse() -> "tuple[deque, threading.Event]":
    """
    Register a new SSE subscriber.
    Returns (buffer_snapshot, wake_event).
    """
    ev = threading.Event()
    with _sse_lock:
        _sse_subscribers.append(ev)
        snapshot = list(_sse_buffer)
    return snapshot, ev


def unsubscribe_sse(ev: threading.Event):
    with _sse_lock:
        try:
            _sse_subscribers.remove(ev)
        except ValueError:
            pass


# ── Detector instances (one per metric) ───────────────────────────────────────
_zscore_detectors: Dict[str, ZScoreDetector] = {}
_iforest_detectors: Dict[str, IsolationForestDetector] = {}


def _get_detectors(metric: str):
    if metric not in _zscore_detectors:
        zd = ZScoreDetector()
        ifd = IsolationForestDetector()

        # ── WARM START: Fetch last 200 points to prime the detectors ──
        log.info(f"Warm starting detectors for metric '{metric}'...")
        historical = fetch_metrics(metric=metric, limit=200)
        # fetch_metrics returns newest first, so we reverse to feed chronologically
        for row in reversed(historical):
            val = float(row["value"])
            zd.update(val)
            ifd.update(val)

        _zscore_detectors[metric] = zd
        _iforest_detectors[metric] = ifd
        log.info(
            f"Detectors for '{metric}' primed with {len(historical)} historical points."
        )

    return _zscore_detectors[metric], _iforest_detectors[metric]


def update_detector_config(
    zscore_threshold: float = None, iforest_contamination: float = None
):
    """Dynamically update thresholds for all active detectors."""
    for metric, zd in _zscore_detectors.items():
        if zscore_threshold is not None:
            zd.threshold = zscore_threshold
    for metric, ifd in _iforest_detectors.items():
        if iforest_contamination is not None:
            ifd.contamination = iforest_contamination
    log.info(
        f"Updated detector configs: ZScore={zscore_threshold}, IForest={iforest_contamination}"
    )


# ── Data Retention Daemon ─────────────────────────────────────────────────────


def _retention_worker():
    """Runs every hour to purge data older than 7 days."""
    while True:
        try:
            purge_old_data(days=7)
        except Exception as e:
            log.error(f"Retention worker error: {e}")
        time.sleep(3600)  # Sleep for 1 hour


threading.Thread(target=_retention_worker, daemon=True).start()


# ── Main processing loop ───────────────────────────────────────────────────────


def run_worker(stop_event: threading.Event = None):
    log.info("Detection worker started.")

    while True:
        if stop_event and stop_event.is_set():
            log.info("Worker stopping.")
            break

        try:
            msg = read_next()
        except Exception as e:
            log.error(f"Stream read error: {e}")
            continue

        ts_str = msg["ts"]
        metric = msg["metric"]
        value = float(msg["value"])
        injected = bool(msg.get("injected", False))
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))

        # ── Run detectors ──────────────────────────────────────────────────────
        zd, ifd = _get_detectors(metric)

        z_anomaly, z_severity, z_score = zd.update(value)
        if_anomaly, if_severity, if_score = ifd.update(value)

        # ── Persist raw metric ────────────────────────────────────────────────
        insert_metric(
            ts=ts,
            metric=metric,
            value=value,
            is_anomaly_zscore=z_anomaly,
            is_anomaly_iforest=if_anomaly,
            zscore_value=z_score,
            iforest_score=if_score,
            injected=injected,
        )

        # ── Persist anomaly events + alert ────────────────────────────────────
        for is_anom, severity, detector_name in [
            (z_anomaly, z_severity, "zscore"),
            (if_anomaly, if_severity, "iforest"),
        ]:
            if is_anom:
                alerted = maybe_alert(
                    ts_str, metric, value, detector_name, severity
                )
                insert_anomaly_event(
                    ts=ts,
                    metric=metric,
                    value=value,
                    detector=detector_name,
                    severity=severity,
                    alerted=alerted,
                )

        # ── Build enriched point for SSE broadcast ────────────────────────────
        point = {
            "ts": ts_str,
            "metric": metric,
            "value": round(value, 4),
            "injected": injected,
            # Z-Score
            "z_score": round(z_score, 4) if z_score is not None else None,
            "z_anomaly": z_anomaly,
            "z_severity": round(z_severity, 4),
            "z_mean": round(zd.current_mean, 4),
            "z_upper": round(zd.upper_band, 4),
            "z_lower": round(zd.lower_band, 4),
            # Isolation Forest
            "if_score": round(if_score, 4) if if_score is not None else None,
            "if_anomaly": if_anomaly,
            "if_severity": round(if_severity, 4),
        }

        _broadcast(point)

        if z_anomaly or if_anomaly:
            det = []
            if z_anomaly:
                det.append(f"ZScore(sev={z_severity:.2f})")
            if if_anomaly:
                det.append(f"IForest(sev={if_severity:.2f})")
            log.info(
                f"ANOMALY [{metric}] val={value:.2f} injected={injected} — {', '.join(det)}"
            )
