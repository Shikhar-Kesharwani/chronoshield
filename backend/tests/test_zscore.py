"""
tests/test_zscore.py — Unit tests for the Z-Score detector

Run with:  python -m pytest backend/tests/ -v
"""

import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from detectors.zscore import ZScoreDetector


class TestZScoreDetector:

    def test_no_anomaly_on_empty_buffer(self):
        d = ZScoreDetector(window=10, threshold=3.0)
        is_anom, sev, z = d.update(50.0)
        assert not is_anom
        assert sev == 0.0
        assert z is None

    def test_normal_values_not_flagged(self):
        d = ZScoreDetector(window=30, threshold=3.0)
        # Warm up with 30 normal values
        for v in [50.0 + (i % 5) for i in range(30)]:
            is_anom, _, _ = d.update(v)
        assert not is_anom

    def test_large_spike_flagged(self):
        d = ZScoreDetector(window=30, threshold=3.0)
        # Warm up
        for _ in range(30):
            d.update(50.0)
        # Inject massive spike
        is_anom, severity, z = d.update(200.0)
        assert is_anom, "200 should be flagged as anomaly after warm-up"
        assert severity > 0.0
        assert z is not None and z > 3.0

    def test_severity_between_0_and_1(self):
        d = ZScoreDetector(window=30, threshold=3.0)
        for _ in range(30):
            d.update(50.0)
        _, sev, _ = d.update(500.0)
        assert 0.0 <= sev <= 1.0

    def test_negative_spike_flagged(self):
        d = ZScoreDetector(window=30, threshold=3.0)
        for _ in range(30):
            d.update(50.0)
        is_anom, sev, z = d.update(-200.0)
        assert is_anom
        assert z is not None and z < -3.0

    def test_rolling_window_adapts(self):
        """Detector should adapt its baseline after a sustained shift."""
        d = ZScoreDetector(window=20, threshold=3.0)
        # Warm up at level 50
        for _ in range(20):
            d.update(50.0)
        # Shift to level 90 (should stop being anomalous after window fills)
        for _ in range(20):
            d.update(90.0)
        # Now 90 is the new normal
        is_anom, _, _ = d.update(90.0)
        assert not is_anom, "90 should be normal after window adapts"

    def test_bands_computed_correctly(self):
        d = ZScoreDetector(window=10, threshold=3.0)
        values = [10.0] * 10
        for v in values:
            d.update(v)
        # Flat signal → std ≈ 0 → bands should collapse near mean
        assert abs(d.upper_band - d.lower_band) < 1e-6

    def test_reset_clears_state(self):
        d = ZScoreDetector(window=10, threshold=3.0)
        for _ in range(10):
            d.update(50.0)
        d.reset()
        is_anom, sev, z = d.update(50.0)
        assert not is_anom
        assert z is None

    def test_running_sum_consistency(self):
        """Running sum should match direct computation."""
        d = ZScoreDetector(window=20, threshold=3.0)
        vals = [float(i) for i in range(20)]
        for v in vals:
            d.update(v)
        expected_mean = sum(vals) / len(vals)
        assert abs(d.current_mean - expected_mean) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
