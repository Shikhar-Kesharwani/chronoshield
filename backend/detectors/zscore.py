"""
detectors/zscore.py — Rolling Z-Score anomaly detector

Algorithm:
    1. Maintain a sliding window of the last N data points.
    2. Compute rolling mean (μ) and standard deviation (σ).
    3. For a new point x, compute z = (x − μ) / σ.
    4. Flag as anomaly if |z| > threshold.

Returns a severity score normalised to [0, 1] based on how far |z| exceeds
the threshold:  severity = min(1.0,  (|z| − threshold) / threshold)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
import math
from collections import deque
from typing import Optional, Tuple

from config import ZSCORE_THRESHOLD, ZSCORE_WINDOW

log = logging.getLogger(__name__)


class ZScoreDetector:
    """Stateful rolling Z-score detector for a single metric stream."""

    def __init__(
        self,
        window: int = ZSCORE_WINDOW,
        threshold: float = ZSCORE_THRESHOLD,
    ):
        self.window = window
        self.threshold = threshold
        self._buf: deque = deque(maxlen=window)
        # Running sum + sum-of-squares for O(1) mean/std updates
        self._sum: float = 0.0
        self._sum2: float = 0.0

    # ── Internal stats ─────────────────────────────────────────────────────────

    def _mean(self) -> float:
        n = len(self._buf)
        return self._sum / n if n else 0.0

    def _std(self) -> float:
        n = len(self._buf)
        if n < 2:
            return 0.0
        variance = (self._sum2 - (self._sum**2) / n) / (n - 1)
        return math.sqrt(max(variance, 0.0))

    # ── Public API ─────────────────────────────────────────────────────────────

    def update(self, value: float) -> Tuple[bool, float, Optional[float]]:
        """
        Feed a new data point into the detector.

        Returns:
            (is_anomaly, severity, z_score)
            - is_anomaly : True if |z| > threshold and window is full
            - severity   : float in [0, 1]; 0 if not enough data yet
            - z_score    : the computed Z-score (None if window not full)
        """
        # Evict oldest point if buffer is full
        if len(self._buf) == self.window:
            old = self._buf[0]
            self._sum -= old
            self._sum2 -= old * old

        # Insert new point
        self._buf.append(value)
        self._sum += value
        self._sum2 += value * value

        # Need at least 2 points to have a meaningful std
        if len(self._buf) < max(2, self.window // 4):
            return False, 0.0, None

        mean = self._mean()
        std = self._std()

        if std < 1e-10:
            # Flat signal — any deviation is suspicious but we stay conservative
            z_score = 0.0
        else:
            z_score = (value - mean) / std

        is_anomaly = abs(z_score) > self.threshold
        if is_anomaly:
            excess = abs(z_score) - self.threshold
            severity = min(1.0, excess / self.threshold)
        else:
            severity = 0.0

        return is_anomaly, severity, z_score

    @property
    def current_mean(self) -> float:
        return self._mean()

    @property
    def current_std(self) -> float:
        return self._std()

    @property
    def upper_band(self) -> float:
        return self._mean() + self.threshold * self._std()

    @property
    def lower_band(self) -> float:
        return self._mean() - self.threshold * self._std()

    def reset(self):
        self._buf.clear()
        self._sum = 0.0
        self._sum2 = 0.0
