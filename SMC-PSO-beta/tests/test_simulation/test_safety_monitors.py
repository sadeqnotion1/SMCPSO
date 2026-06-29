"""M4 Slice 4 - safety monitors."""
import numpy as np
from src.simulation.safety.monitors import (
    SimulationPerformanceMonitor, SafetyMonitor, SystemHealthMonitor,
)

def test_performance_monitor_timing():
    pm = SimulationPerformanceMonitor()
    pm.start_timing("op")
    el = pm.end_timing("op")
    assert isinstance(el, float) and el >= 0.0
    assert pm.end_timing("never") == 0.0
    stats = pm.get_statistics()
    assert "op" in stats and stats["op"]["count"] == 1

def test_safety_monitor_report_and_score():
    sm = SafetyMonitor()
    assert sm.get_safety_report()["safety_score"] == 1.0
    sm.record_violation("nan", "bad", 3)
    sm.record_warning("warn", "meh", 4)
    rep = sm.get_safety_report()
    assert rep["violation_count"] == 1 and rep["warning_count"] == 1
    assert 0.0 <= rep["safety_score"] <= 1.0

def test_system_health_monitor():
    hm = SystemHealthMonitor(history_length=5)
    assert hm.get_health_status()["status"] == "no_data"
    for _ in range(3):
        hm.update(np.zeros(2), 0.0, {"err": 0.1})
    status = hm.get_health_status()
    assert "health_score" in status and 0.0 <= status["health_score"] <= 1.0
    assert status["data_points"] == 3
