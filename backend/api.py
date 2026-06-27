"""
api.py — FastAPI application

Endpoints:
  GET  /health                  — health check
  GET  /api/metrics             — last N raw metric points
  GET  /api/anomalies           — last N anomaly events
  GET  /api/stats               — detector precision/recall stats
  POST /api/inject              — manually inject an anomaly spike
  GET  /api/stream              — Server-Sent Events live data stream
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import json
import logging
import threading
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import API_HOST, API_PORT, CORS_ORIGINS
from db.init_db import init_db
from db.store import fetch_anomaly_events, fetch_detector_stats, fetch_metrics
from generator import run_generator, trigger_manual_anomaly
from worker import (run_worker, subscribe_sse, unsubscribe_sse,
                    update_detector_config)

log = logging.getLogger(__name__)

# ── Background threads ────────────────────────────────────────────────────────
_stop_event = threading.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start generator + worker threads on startup; stop on shutdown."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    log.info("Initialising database …")
    init_db()

    log.info("Starting background threads …")
    gen_thread = threading.Thread(
        target=run_generator,
        kwargs={"stop_event": _stop_event},
        daemon=True,
        name="generator",
    )
    worker_thread = threading.Thread(
        target=run_worker,
        kwargs={"stop_event": _stop_event},
        daemon=True,
        name="worker",
    )
    gen_thread.start()
    worker_thread.start()

    yield  # app is running

    log.info("Shutting down background threads …")
    _stop_event.set()
    gen_thread.join(timeout=3)
    worker_thread.join(timeout=3)


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Time-Series Anomaly Detection API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/health")
def health():
    return {"status": "ok", "service": "anomaly-detection-api"}


@app.get("/api/metrics")
def get_metrics(
    metric: str = Query("cpu"),
    limit: int = Query(300, ge=1, le=2000),
    since: str = Query(None),
):
    """Return stored metric data points."""
    rows = fetch_metrics(metric=metric, limit=limit, since_ts=since)
    return {"metric": metric, "count": len(rows), "data": rows}


@app.get("/api/anomalies")
def get_anomalies(limit: int = Query(50, ge=1, le=500)):
    """Return recent anomaly events."""
    rows = fetch_anomaly_events(limit=limit)
    return {"count": len(rows), "data": rows}


@app.get("/api/stats")
def get_stats(metric: str = Query("cpu")):
    """Return precision/recall comparison stats for both detectors."""
    stats = fetch_detector_stats(metric=metric)
    return {"metric": metric, "stats": stats}


@app.post("/api/inject")
def inject_anomaly():
    """Manually inject an anomaly spike into the metric stream."""
    trigger_manual_anomaly()
    return {
        "status": "queued",
        "message": "Anomaly will be injected on next generator tick.",
    }


class ConfigUpdate(BaseModel):
    zscore_threshold: float = None
    iforest_contamination: float = None


@app.post("/api/config")
def update_config(config: ConfigUpdate):
    """Dynamically update detection thresholds."""
    update_detector_config(
        zscore_threshold=config.zscore_threshold,
        iforest_contamination=config.iforest_contamination,
    )
    return {"status": "success", "config": config.dict(exclude_unset=True)}


@app.get("/api/stream")
def stream_metrics():
    """
    Server-Sent Events endpoint.
    Clients connect here and receive a new JSON event for every data point.
    """

    def event_generator():
        snapshot, wake_event = subscribe_sse()
        sent_count = 0

        # Send historical snapshot first so the chart loads immediately
        for point in snapshot:
            data = json.dumps(point)
            yield f"data: {data}\n\n"
            sent_count += 1

        try:
            while True:
                # Wait up to 30 s for a new point (keep-alive heartbeat)
                fired = wake_event.wait(timeout=30)
                if not fired:
                    yield ": heartbeat\n\n"
                    continue

                # Drain all new points accumulated since last wake
                from worker import _sse_buffer, _sse_lock

                with _sse_lock:
                    new_points = list(_sse_buffer)[sent_count:]
                    wake_event.clear()

                for point in new_points:
                    data = json.dumps(point)
                    yield f"data: {data}\n\n"
                    sent_count += 1
        except GeneratorExit:
            pass
        finally:
            unsubscribe_sse(wake_event)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info",
    )
