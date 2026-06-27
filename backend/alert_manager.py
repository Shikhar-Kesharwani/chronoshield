"""
alert_manager.py — Alerting layer

Supports two modes (configured via ALERT_MODE in .env):
  - "console"  : log to stdout (default, no external deps)
  - "slack"    : POST to Slack Incoming Webhook URL

To enable Slack:
  1. Create an Incoming Webhook in your Slack App settings.
  2. Set ALERT_MODE=slack and SLACK_WEBHOOK_URL=https://hooks.slack.com/...
"""

import sys, os

sys.path.insert(0, os.path.dirname(__file__))

import logging
import requests
from datetime import datetime
from typing import Dict

from config import ALERT_MODE, SLACK_WEBHOOK_URL, ALERT_SEVERITY_THRESHOLD

log = logging.getLogger(__name__)

# Track recently alerted anomalies to prevent spam (cooldown = 30 s per metric)
_last_alert: Dict[str, float] = {}
_COOLDOWN_SECONDS = 30


def _should_send(metric: str) -> bool:
    now = datetime.utcnow().timestamp()
    last = _last_alert.get(metric, 0)
    if now - last >= _COOLDOWN_SECONDS:
        _last_alert[metric] = now
        return True
    return False


def _format_message(
    ts: str,
    metric: str,
    value: float,
    detector: str,
    severity: float,
) -> str:
    sev_pct = int(severity * 100)
    bar = "█" * (sev_pct // 10) + "░" * (10 - sev_pct // 10)
    return (
        f"🚨 *Anomaly Detected* [{detector.upper()}]\n"
        f"  Metric  : `{metric}`\n"
        f"  Value   : `{value:.2f}`\n"
        f"  Severity: `{sev_pct}%` {bar}\n"
        f"  Time    : `{ts}`"
    )


def _send_slack(message: str):
    if not SLACK_WEBHOOK_URL or SLACK_WEBHOOK_URL.startswith(
        "https://hooks.slack.com/services/YOUR"
    ):
        log.warning("Slack alert skipped — SLACK_WEBHOOK_URL not configured.")
        return
    try:
        resp = requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": message},
            timeout=5,
        )
        if resp.status_code != 200:
            log.warning(
                f"Slack webhook returned {resp.status_code}: {resp.text}"
            )
        else:
            log.info("Slack alert sent.")
    except Exception as e:
        log.error(f"Slack alert failed: {e}")


def maybe_alert(
    ts: str,
    metric: str,
    value: float,
    detector: str,
    severity: float,
) -> bool:
    """
    Send an alert if severity exceeds threshold and cooldown has passed.

    Returns True if an alert was dispatched.
    """
    if severity < ALERT_SEVERITY_THRESHOLD:
        return False

    if not _should_send(metric):
        return False

    message = _format_message(ts, metric, value, detector, severity)

    if ALERT_MODE == "slack":
        _send_slack(message)
    else:
        # Console mode — pretty print
        log.warning(f"\n{'='*50}\n{message}\n{'='*50}")

    return True
