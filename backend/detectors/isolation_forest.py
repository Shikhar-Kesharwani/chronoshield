"""
detectors/isolation_forest.py — Isolation Forest anomaly detector

Algorithm:
    1. Accumulate a training window of historical data points.
    2. Once the window is full, train an IsolationForest model.
    3. Re-train every `retrain_every` new points to adapt to drift.
    4. Score new points with decision_function (negative = more anomalous).
    5. Normalise the score to a [0, 1] severity.

The IsolationForest natively handles multivariate data — pass additional
features (e.g., rate-of-change) to make it more expressive.
"""

import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from collections import deque
from typing import Tuple, List, Optional
import logging
import numpy as np

from config import IFOREST_WINDOW, IFOREST_CONTAMINATION

log = logging.getLogger(__name__)

try:
    from sklearn.ensemble import IsolationForest as _IF

    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False
    log.warning(
        "scikit-learn not installed — IsolationForest detector disabled."
    )


class IsolationForestDetector:
    """
    Stateful Isolation Forest detector.

    Features used per data point:
        [value, delta]  (current value + first derivative)
    """

    def __init__(
        self,
        window: int = IFOREST_WINDOW,
        contamination: float = IFOREST_CONTAMINATION,
        retrain_every: int = 50,
    ):
        self.window = window
        self.contamination = contamination
        self.retrain_every = retrain_every

        self._buf: deque = deque(maxlen=window)
        self._model: Optional[object] = None
        self._trained: bool = False
        self._last_value: Optional[float] = None
        self._points_since_retrain: int = 0
        self._score_min: float = -0.5
        self._score_max: float = 0.5

    def _build_features(self, value: float) -> List[float]:
        delta = (
            value - self._last_value if self._last_value is not None else 0.0
        )
        return [value, delta]

    def _train(self):
        if not _SKLEARN_AVAILABLE:
            return
        X = list(self._buf)
        if len(X) < max(10, self.window // 4):
            return
        arr = np.array(X)
        self._model = _IF(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42,
            n_jobs=-1,
        )
        self._model.fit(arr)
        scores = self._model.decision_function(arr)
        self._score_min = float(scores.min())
        self._score_max = float(scores.max())
        self._trained = True
        log.debug(
            f"IForest retrained on {len(X)} pts — score range [{self._score_min:.3f}, {self._score_max:.3f}]"
        )

    def _normalise_score(self, raw_score: float) -> float:
        """
        Map decision_function score to [0, 1] anomaly severity.
        Lower raw scores = more anomalous → severity closer to 1.
        """
        r = self._score_max - self._score_min
        if r < 1e-10:
            return 0.0
        # Invert: low score → high severity
        severity = 1.0 - (raw_score - self._score_min) / r
        return float(np.clip(severity, 0.0, 1.0))

    def update(self, value: float) -> Tuple[bool, float, Optional[float]]:
        """
        Feed a new data point.

        Returns:
            (is_anomaly, severity, raw_decision_score)
        """
        if not _SKLEARN_AVAILABLE:
            return False, 0.0, None

        features = self._build_features(value)
        self._last_value = value
        self._buf.append(features)
        self._points_since_retrain += 1

        # Trigger (re)training
        if (
            not self._trained and len(self._buf) >= max(10, self.window // 4)
        ) or (
            self._trained and self._points_since_retrain >= self.retrain_every
        ):
            self._train()
            self._points_since_retrain = 0

        if not self._trained or self._model is None:
            return False, 0.0, None

        arr = np.array([features])
        raw_score = float(self._model.decision_function(arr)[0])
        label = self._model.predict(arr)[0]  # -1 = anomaly, 1 = normal

        is_anomaly = bool(label == -1)
        severity = self._normalise_score(raw_score) if is_anomaly else 0.0

        return is_anomaly, severity, raw_score

    def reset(self):
        self._buf.clear()
        self._model = None
        self._trained = False
        self._last_value = None
        self._points_since_retrain = 0
