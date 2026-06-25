#======================================================================================
# tests/test_utils/test_monitoring/test_stability.py
#======================================================================================
"""Unit tests for stability monitors (LDR, saturation, conditioning, system)."""
import numpy as np

from src.utils.monitoring.realtime.stability import (
    LyapunovDecreaseMonitor, SaturationMonitor, DynamicsConditioningMonitor,
    StabilityMonitoringSystem,
)


def test_ldr_decreasing_no_alert_increasing_alert():
    # Decreasing sliding surface -> Lyapunov decreasing -> LDR high -> no alert
    m = LyapunovDecreaseMonitor(window_size_ms=300.0, dt=0.01,
                                ldr_threshold=0.95, transient_time=0.5)
    res = {}
    for k in range(120):
        res = m.update(np.array([1.0 - k * 0.005]))
    assert res['status'] == 'monitoring'
    assert res['ldr'] >= 0.95
    assert not res['alert']  # note: monitors return numpy.bool_ (see AUDIT MON-STA-2 [P3])
    assert m.sample_count.get() == 120  # AtomicCounter wired correctly

    # Growing sliding surface -> Lyapunov increasing -> LDR low -> alert
    m2 = LyapunovDecreaseMonitor(dt=0.01, transient_time=0.5)
    res2 = {}
    for k in range(120):
        res2 = m2.update(np.array([0.1 + k * 0.01]))
    assert res2['ldr'] < 0.95
    assert bool(res2['alert']) is True


def test_saturation_duty_alert():
    m = SaturationMonitor(max_force=150.0, dt=0.01, duty_threshold=0.2,
                          rate_hit_threshold=0.01, transient_time=0.5)
    res = {}
    for _ in range(120):
        res = m.update(200.0)  # always saturated
    assert res['status'] == 'monitoring'
    assert res['duty'] > 0.2
    assert bool(res['alert']) is True

    m2 = SaturationMonitor(max_force=150.0, dt=0.01, transient_time=0.5)
    res2 = {}
    for _ in range(120):
        res2 = m2.update(0.0)  # never saturated
    assert res2['duty'] == 0.0
    assert not res2['alert']


def test_conditioning_monitor():
    m = DynamicsConditioningMonitor(condition_threshold=1e7, spike_threshold=1e9, dt=0.01)
    good = m.update(np.eye(3))
    assert not good['alert']
    bad = m.update(np.array([[1.0, 0.0], [0.0, 1e-12]]))
    assert bool(bad['alert']) is True
    assert bool(bad['spike_alert']) is True


def test_stability_system_integration():
    sys = StabilityMonitoringSystem({'dt': 0.01, 'transient_time': 0.2})
    out = sys.update(np.array([0.01]), 1.0, np.eye(3), used_fallback=False)
    for key in ('alert', 'ldr', 'saturation', 'conditioning', 'episode'):
        assert key in out
    report = sys.get_stability_report()
    assert 'stability_score' in report
    assert 0.0 <= report['stability_score'] <= 1.0
    sys.start_new_episode()
    assert sys.episode_count.get() == 1
    sys.reset()
    assert sys.episode_count.get() == 0
    assert sys.violation_history == []
