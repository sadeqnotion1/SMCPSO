#======================================================================================
# tests/test_utils/test_monitoring/test_latency.py
#======================================================================================
"""Unit tests for LatencyMonitor, including a characterization test for the
two distinct deadline-miss definitions (see AUDIT card: MON-LAT-1, [P2])."""
import src.utils.monitoring.realtime.latency as lat
from src.utils.monitoring.realtime.latency import LatencyMonitor


def test_stats_and_missed_rate_injected():
    m = LatencyMonitor(dt=0.01)
    m.samples = [0.001, 0.002, 0.003, 0.011, 0.012]  # two over dt
    median, p95 = m.stats()
    assert median == 0.003
    assert p95 > 0.003
    assert abs(m.missed_rate() - 2 / 5) < 1e-9


def test_enforce_weakly_hard():
    m = LatencyMonitor(dt=0.01)
    # last 4 samples: 1 miss (>0.01); window k=4 allows m=1
    m.samples = [0.001, 0.02, 0.001, 0.001, 0.001, 0.02]
    assert m.enforce(m=1, k=4) is True   # only 1 miss in last 4
    assert m.enforce(m=0, k=4) is False  # 1 miss > 0 allowed
    assert m.enforce(m=0, k=0) is True   # degenerate window


def test_reset_and_recent_stats():
    m = LatencyMonitor(dt=0.01)
    m.samples = [0.001] * 250
    rec_median, _ = m.get_recent_stats(n=100)
    assert rec_median == 0.001
    m.reset()
    assert m.samples == []
    assert m.stats() == (0.0, 0.0)


def test_end_vs_missed_rate_threshold_mismatch(monkeypatch):
    """[P2 MON-LAT-1] end() flags a 'miss' at latency > dt*margin (0.9*dt),
    while missed_rate()/enforce() count a miss only at latency > dt.
    A latency of 0.0095s (between 0.009 and 0.01) is therefore flagged by
    end() but NOT counted by missed_rate(). This is a characterization test
    documenting current behavior; do not 'fix' without maintainer sign-off."""
    seq = iter([100.0, 100.0095])
    monkeypatch.setattr(lat.time, "perf_counter", lambda: next(seq))
    m = LatencyMonitor(dt=0.01, margin=0.9)
    start = m.start()
    missed = m.end(start)
    assert missed is True            # end(): 0.0095 > 0.9*0.01 = 0.009
    assert m.missed_rate() == 0.0    # missed_rate(): 0.0095 is NOT > 0.01
