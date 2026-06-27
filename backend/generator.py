"""
generator.py — Synthetic metric generator

Generates realistic time-series data with:
  - Base sinusoidal trend (simulates daily CPU usage patterns)
  - Gaussian noise
  - Random automatic anomaly injection (probability controlled by config)
  - Manual anomaly injection via shared flag (set by API endpoint)

Pushes each data point to the configured stream (Redis or in-process queue).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import time
import math
import random
import threading
import logging
from datetime import datetime, timezone
from typing import Dict, Any

from config import (
    REDIS_MODE, REDIS_HOST, REDIS_PORT, REDIS_STREAM_KEY,
    GENERATOR_RATE, GENERATOR_ANOMALY_PROB,
)

log = logging.getLogger(__name__)

# ── Shared in-process queue (used when REDIS_MODE=mock) ─────────────────────
from queue import Queue
_mock_queue: Queue = Queue(maxsize=10_000)

# ── Manual injection flag (set by API) ──────────────────────────────────────
_manual_inject_event = threading.Event()

def trigger_manual_anomaly():
    """Called by the API to inject a spike on the next generator tick."""
    _manual_inject_event.set()


def _get_redis_client():
    import redis as _redis
    return _redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def _push(message: Dict[str, Any]):
    """Push message to Redis Stream or mock queue."""
    if REDIS_MODE == "real":
        try:
            r = _get_redis_client()
            r.xadd(REDIS_STREAM_KEY, {k: str(v) for k, v in message.items()})
            r.close()
        except Exception as e:
            log.warning(f"Redis push failed ({e}), falling back to mock queue.")
            _mock_queue.put(message)
    else:
        if _mock_queue.full():
            _mock_queue.get_nowait()   # drop oldest to avoid blocking
        _mock_queue.put(message)


def run_generator(stop_event: threading.Event = None):
    """
    Continuously generate and push metric data points for multiple metrics.
    """
    interval = 1.0 / GENERATOR_RATE
    tick = 0
    log.info(f"Generator started — metrics=[cpu, memory, latency], rate={GENERATOR_RATE}/s, mode={REDIS_MODE}")

    # Baseline params
    metrics = {
        "cpu": {"mean": 40.0, "amp": 20.0, "noise": 3.0, "clamp": (0.0, 100.0)},
        "memory": {"mean": 65.0, "amp": 10.0, "noise": 1.0, "clamp": (0.0, 100.0)},
        "latency": {"mean": 150.0, "amp": 40.0, "noise": 15.0, "clamp": (10.0, 2000.0)},
    }
    PERIOD_TICKS = 300

    while True:
        if stop_event and stop_event.is_set():
            log.info("Generator stopping.")
            break

        t = tick / PERIOD_TICKS
        
        # ── Manual spike injection ──
        manual_spike = False
        if _manual_inject_event.is_set():
            manual_spike = True
            _manual_inject_event.clear()
            
        for metric, p in metrics.items():
            base  = p["mean"] + p["amp"] * math.sin(2 * math.pi * t)
            noise = random.gauss(0, p["noise"])
            value = base + noise
            injected = False

            if manual_spike:
                if metric == "cpu": spike = random.uniform(30, 60)
                elif metric == "memory": spike = random.uniform(15, 30)
                else: spike = random.uniform(300, 800)
                value += spike
                injected = True
                log.info(f"Manual anomaly injected on {metric}: {value:.2f}")
            elif random.random() < GENERATOR_ANOMALY_PROB:
                if metric == "cpu": spike = random.choice([-1, 1]) * random.uniform(20, 50)
                elif metric == "memory": spike = random.choice([-1, 1]) * random.uniform(10, 25)
                else: spike = random.choice([-1, 1]) * random.uniform(200, 600)
                value += spike
                injected = True
                log.debug(f"Auto anomaly injected on {metric}: {value:.2f}")

            # Clamp
            value = max(p["clamp"][0], min(p["clamp"][1], value))

            message = {
                "ts":       datetime.now(timezone.utc).isoformat(),
                "metric":   metric,
                "value":    f"{value:.4f}",
                "injected": "1" if injected else "0",
            }
            _push(message)

        tick += 1
        time.sleep(interval)


def read_next() -> Dict[str, Any]:
    """
    Read the next message from the stream (blocks until available).
    Returns a dict with keys: ts, metric, value, injected.
    """
    if REDIS_MODE == "real":
        r = _get_redis_client()
        last_id = "0"
        while True:
            results = r.xread({REDIS_STREAM_KEY: last_id}, count=1, block=1000)
            if results:
                _, messages = results[0]
                msg_id, data = messages[0]
                last_id = msg_id
                r.close()
                return {
                    "ts":       data["ts"],
                    "metric":   data["metric"],
                    "value":    float(data["value"]),
                    "injected": data.get("injected", "0") == "1",
                }
    else:
        msg = _mock_queue.get()
        return {
            "ts":       msg["ts"],
            "metric":   msg["metric"],
            "value":    float(msg["value"]),
            "injected": str(msg.get("injected", "0")) == "1",
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_generator()
