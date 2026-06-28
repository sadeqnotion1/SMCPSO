"""M4 Slice 2 - TimeManager / RealTimeScheduler / AdaptiveTimeStep."""
import numpy as np
import pytest

from src.simulation.core.time_domain import (
    TimeManager, RealTimeScheduler, AdaptiveTimeStep,
)


def test_horizon_from_total_time():
    tm = TimeManager(dt=0.01, total_time=1.0)
    assert tm.horizon == 100
    assert np.isclose(tm.total_time, 1.0)


def test_total_time_from_horizon():
    tm = TimeManager(dt=0.01, horizon=50)
    assert np.isclose(tm.total_time, 0.5)


def test_inconsistent_spec_raises():
    with pytest.raises(ValueError):
        TimeManager(dt=0.01, total_time=1.0, horizon=99)


def test_advance_and_finish():
    tm = TimeManager(dt=0.1, horizon=3)
    tm.start_simulation()
    assert not tm.is_finished()
    for _ in range(3):
        tm.advance_step()
    assert tm.current_step == 3
    assert np.isclose(tm.current_time, 0.3)
    assert tm.is_finished()
    assert tm.remaining_steps() == 0


def test_progress_fraction():
    tm = TimeManager(dt=0.1, total_time=1.0)
    tm.start_simulation()
    for _ in range(5):
        tm.advance_step()
    assert np.isclose(tm.progress, 0.5)


def test_time_vector_length():
    tm = TimeManager(dt=0.1, horizon=10)
    tv = tm.get_time_vector()
    # horizon + 1 inclusive grid
    assert tv.shape == (11,)
    assert np.isclose(tv[0], 0.0)
    assert np.isclose(tv[-1], 1.0)


def test_time_vector_requires_horizon():
    tm = TimeManager(dt=0.1)
    with pytest.raises(ValueError):
        tm.get_time_vector()


def test_adaptive_accept_and_grow():
    a = AdaptiveTimeStep(initial_dt=0.01, max_dt=0.1)
    new_dt, accept = a.update_step_size(error_estimate=1e-9, tolerance=1e-3)
    assert accept is True
    assert new_dt >= 0.01  # small error -> grow (capped at max_dt)


def test_adaptive_reject_and_shrink():
    a = AdaptiveTimeStep(initial_dt=0.01, min_dt=1e-6)
    new_dt, accept = a.update_step_size(error_estimate=1.0, tolerance=1e-3)
    assert accept is False
    assert new_dt < 0.01  # large error -> shrink


def test_realtime_scheduler_stats_empty():
    s = RealTimeScheduler(target_dt=0.01)
    stats = s.get_timing_stats()
    assert stats["total_steps"] == 0
    assert stats["deadline_miss_rate"] == 0.0
