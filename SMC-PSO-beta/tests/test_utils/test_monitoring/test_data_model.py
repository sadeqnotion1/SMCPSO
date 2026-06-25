#======================================================================================
# tests/test_utils/test_monitoring/test_data_model.py
#======================================================================================
"""Unit tests for monitoring metrics data models and metric computations."""
import numpy as np
import pytest

from src.utils.monitoring.metrics.data_model import (
    RunStatus, MetricsSnapshot, PerformanceSummary, DashboardData, ComparisonData,
    compute_settling_time, compute_overshoot, compute_chattering_index,
)


def _snapshot(t, step):
    return MetricsSnapshot(
        timestamp_s=t, time_step=step, controller_type="classical_smc",
        state=np.array([0.1, 0.2, 0.0, 0.0]), control_output=1.5,
        error_norm=0.3, angle1_rad=0.1, angle2_rad=0.2,
        velocity1_rad_s=0.0, velocity2_rad_s=0.0,
    )


def test_snapshot_to_dict_serializes_state():
    d = _snapshot(0.5, 1).to_dict()
    assert d['state'] == [0.1, 0.2, 0.0, 0.0]
    assert d['controller_type'] == "classical_smc"


def test_performance_summary_score_bounds():
    good = PerformanceSummary(settling_time_s=0.5, overshoot_pct=1.0,
                             steady_state_error=0.0, energy_j=1.0,
                             chattering_amplitude=0.0, bounded_states=True)
    bad = PerformanceSummary(settling_time_s=float('inf'), overshoot_pct=100.0,
                            steady_state_error=1.0, energy_j=500.0,
                            chattering_amplitude=5.0, bounded_states=False)
    sg, sb = good.get_score(), bad.get_score()
    assert 0.0 <= sb <= sg <= 100.0
    assert sg > sb


def test_dashboard_roundtrip_json(tmp_path):
    run = DashboardData(run_id="r1", controller="classical_smc", scenario="s")
    for i in range(5):
        run.add_snapshot(_snapshot(i * 0.1, i))
    run.finalize(PerformanceSummary(settling_time_s=1.0))
    assert run.status == RunStatus.COMPLETE
    ts, vals = run.get_time_series('error_norm')
    assert len(ts) == 5 and len(vals) == 5
    with pytest.raises(ValueError):
        run.get_time_series('not_a_metric')
    fp = tmp_path / "run.json"
    run.to_json(str(fp))
    loaded = DashboardData.from_json(str(fp))
    assert loaded.run_id == "r1"
    assert len(loaded.snapshots) == 5
    assert loaded.status == RunStatus.COMPLETE


def test_comparison_ranking():
    c = ComparisonData()
    for name, st in [("a", 0.5), ("b", 2.0)]:
        run = DashboardData(run_id=name, controller=name, scenario="s")
        run.finalize(PerformanceSummary(settling_time_s=st, bounded_states=True))
        c.add_run(run)
    by_score = c.get_ranking('score')
    assert by_score[0][1] >= by_score[1][1]  # sorted high-to-low
    by_settle = c.get_ranking('settling_time_s')
    assert by_settle[0][1] <= by_settle[1][1]  # sorted low-to-high


def test_metric_computations():
    ts = np.linspace(0, 2, 201)
    errors = np.concatenate([np.linspace(1.0, 0.0, 100), np.full(101, 0.005)])
    st = compute_settling_time(ts, errors, threshold=0.02, min_duration=0.2)
    assert np.isfinite(st) and st > 0
    assert compute_settling_time(np.array([]), np.array([])) == float('inf')
    assert compute_overshoot(np.array([0.0, 1.5, -0.5]), setpoint=0.0) > 0
    ci = compute_chattering_index(np.array([0.0, 1.0, -1.0, 1.0]), dt=0.01)
    assert ci > 0
    assert compute_chattering_index(np.array([1.0]), dt=0.01) == 0.0
