"""
Unit tests for time domain utilities (src/simulation/core/time_domain.py).

Tests cover:
- TimeManager (simulation time tracking)
- RealTimeScheduler (real-time execution)
- AdaptiveTimeStep (adaptive integration)
"""

import time
import numpy as np
import pytest

from src.simulation.core.time_domain import (
    TimeManager,
    RealTimeScheduler,
    AdaptiveTimeStep
)


# ======================================================================================
# TimeManager Tests - Initialization
# ======================================================================================

class TestTimeManagerInitialization:
    """Test TimeManager initialization and validation."""

    def test_init_with_total_time(self):
        """Should initialize with total_time and compute horizon."""
        tm = TimeManager(dt=0.01, total_time=1.0)

        assert tm.dt == 0.01
        assert tm.total_time == 1.0
        assert tm.horizon == 100

    def test_init_with_horizon(self):
        """Should initialize with horizon and compute total_time."""
        tm = TimeManager(dt=0.01, horizon=100)

        assert tm.dt == 0.01
        assert tm.horizon == 100
        assert tm.total_time == pytest.approx(1.0, abs=1e-10)

    def test_init_with_both_consistent(self):
        """Should accept consistent total_time and horizon."""
        tm = TimeManager(dt=0.01, total_time=1.0, horizon=100)

        assert tm.dt == 0.01
        assert tm.total_time == 1.0
        assert tm.horizon == 100

    def test_init_with_both_inconsistent_raises(self):
        """Should raise ValueError for inconsistent parameters."""
        with pytest.raises(ValueError, match="Inconsistent time specification"):
            TimeManager(dt=0.01, total_time=1.0, horizon=50)

    def test_init_with_neither(self):
        """Should initialize with just dt (no total_time or horizon)."""
        tm = TimeManager(dt=0.01)

        assert tm.dt == 0.01
        assert tm.total_time is None
        assert tm.horizon is None


# ======================================================================================
# TimeManager Tests - Properties and State
# ======================================================================================

class TestTimeManagerProperties:
    """Test TimeManager properties."""

    @pytest.fixture
    def tm(self):
        """Create time manager for testing."""
        return TimeManager(dt=0.01, total_time=1.0)

    def test_current_time_initial(self, tm):
        """Should start with current_time = 0."""
        assert tm.current_time == 0.0

    def test_current_step_initial(self, tm):
        """Should start with current_step = 0."""
        assert tm.current_step == 0

    def test_progress_initial(self, tm):
        """Should start with progress = 0."""
        assert tm.progress == 0.0

    def test_progress_no_total_time(self):
        """Should return 0 progress if no total_time set."""
        tm = TimeManager(dt=0.01)
        assert tm.progress == 0.0

    def test_progress_capped_at_one(self, tm):
        """Should cap progress at 1.0 even if time exceeds total_time."""
        tm._current_time = 2.0  # Beyond total_time
        assert tm.progress == 1.0


# ======================================================================================
# TimeManager Tests - Simulation Control
# ======================================================================================

class TestTimeManagerSimulation:
    """Test TimeManager simulation control methods."""

    @pytest.fixture
    def tm(self):
        """Create time manager for testing."""
        return TimeManager(dt=0.01, total_time=1.0)

    def test_start_simulation(self, tm):
        """Should reset state and mark wall clock start."""
        tm._current_time = 0.5  # Set to non-zero
        tm._current_step = 10
        tm.start_simulation()

        assert tm.current_time == 0.0
        assert tm.current_step == 0
        assert tm._start_wall_time is not None

    def test_advance_step_default_dt(self, tm):
        """Should advance by default dt."""
        new_time, new_step = tm.advance_step()

        assert new_time == pytest.approx(0.01, abs=1e-10)
        assert new_step == 1
        assert tm.current_time == pytest.approx(0.01, abs=1e-10)
        assert tm.current_step == 1

    def test_advance_step_custom_dt(self, tm):
        """Should advance by custom dt."""
        new_time, new_step = tm.advance_step(dt=0.02)

        assert new_time == pytest.approx(0.02, abs=1e-10)
        assert new_step == 1

    def test_advance_multiple_steps(self, tm):
        """Should accumulate time and steps correctly."""
        for i in range(10):
            tm.advance_step()

        assert tm.current_time == pytest.approx(0.1, abs=1e-9)
        assert tm.current_step == 10


# ======================================================================================
# TimeManager Tests - Completion and Remaining
# ======================================================================================

class TestTimeManagerCompletion:
    """Test TimeManager completion checks and remaining time/steps."""

    def test_is_finished_by_time(self):
        """Should detect completion by total_time."""
        tm = TimeManager(dt=0.01, total_time=1.0)
        tm._current_time = 1.0

        assert tm.is_finished() == True

    def test_is_finished_by_horizon(self):
        """Should detect completion by horizon."""
        tm = TimeManager(dt=0.01, horizon=100)
        # When horizon=100, total_time is also computed (1.0)
        # So we need to advance time AND steps to finish
        tm._current_time = 1.0
        tm._current_step = 100

        assert tm.is_finished() == True

    def test_is_finished_not_yet(self):
        """Should return False if not finished."""
        tm = TimeManager(dt=0.01, total_time=1.0)
        tm._current_time = 0.5

        assert tm.is_finished() == False

    def test_is_finished_no_limit(self):
        """Should return False if no total_time or horizon."""
        tm = TimeManager(dt=0.01)
        tm._current_time = 1000.0

        assert tm.is_finished() == False

    def test_remaining_time(self):
        """Should compute remaining simulation time."""
        tm = TimeManager(dt=0.01, total_time=1.0)
        tm._current_time = 0.3

        assert tm.remaining_time() == pytest.approx(0.7, abs=1e-10)

    def test_remaining_time_no_limit(self):
        """Should return inf if no total_time."""
        tm = TimeManager(dt=0.01)
        assert tm.remaining_time() == float('inf')

    def test_remaining_time_negative_clamped(self):
        """Should clamp negative remaining time to 0."""
        tm = TimeManager(dt=0.01, total_time=1.0)
        tm._current_time = 1.5

        assert tm.remaining_time() == 0.0

    def test_remaining_steps(self):
        """Should compute remaining steps."""
        tm = TimeManager(dt=0.01, horizon=100)
        tm._current_step = 30

        assert tm.remaining_steps() == 70

    def test_remaining_steps_no_limit(self):
        """Should raise OverflowError when no horizon (int(inf) overflow)."""
        tm = TimeManager(dt=0.01)
        # Implementation does int(float('inf')) which raises OverflowError
        with pytest.raises(OverflowError):
            tm.remaining_steps()


# ======================================================================================
# TimeManager Tests - Time Vector and Wall Clock
# ======================================================================================

class TestTimeManagerUtilities:
    """Test TimeManager utility methods."""

    def test_get_time_vector(self):
        """Should generate correct time vector."""
        tm = TimeManager(dt=0.01, horizon=5)
        t = tm.get_time_vector()

        # Should have horizon+1 points: [0, dt, 2*dt, ..., horizon*dt]
        expected = np.array([0.0, 0.01, 0.02, 0.03, 0.04, 0.05])
        np.testing.assert_array_almost_equal(t, expected, decimal=10)

    def test_get_time_vector_no_horizon_raises(self):
        """Should raise ValueError if no horizon set."""
        tm = TimeManager(dt=0.01)

        with pytest.raises(ValueError, match="Cannot generate time vector without horizon"):
            tm.get_time_vector()

    def test_wall_clock_elapsed_before_start(self):
        """Should return 0 if simulation not started."""
        tm = TimeManager(dt=0.01)
        assert tm.wall_clock_elapsed() == 0.0

    def test_wall_clock_elapsed_after_start(self):
        """Should measure wall clock time after start."""
        tm = TimeManager(dt=0.01)
        tm.start_simulation()
        time.sleep(0.01)  # Sleep 10ms

        elapsed = tm.wall_clock_elapsed()
        assert elapsed >= 0.01  # At least 10ms

    def test_real_time_factor_zero_simulation_time(self):
        """Should return 0 if simulation time is 0 (even if wall time > 0)."""
        tm = TimeManager(dt=0.01)
        tm.start_simulation()
        # Immediately check: current_time=0, wall_elapsed>0 → 0/x = 0
        rtf = tm.real_time_factor()
        assert rtf == 0.0

    def test_real_time_factor_normal(self):
        """Should compute real-time factor correctly."""
        tm = TimeManager(dt=0.01)
        tm.start_simulation()
        time.sleep(0.01)
        tm._current_time = 0.1  # Simulated 100ms in 10ms wall time

        rtf = tm.real_time_factor()
        assert rtf >= 5.0  # Should be ~10x real-time


# ======================================================================================
# RealTimeScheduler Tests
# ======================================================================================

class TestRealTimeScheduler:
    """Test RealTimeScheduler class."""

    def test_initialization(self):
        """Should initialize with target_dt and tolerance."""
        scheduler = RealTimeScheduler(target_dt=0.01, tolerance=0.001)

        assert scheduler.target_dt == 0.01
        assert scheduler.tolerance == 0.001
        assert scheduler._next_deadline is None
        assert scheduler._missed_deadlines == 0
        assert scheduler._total_steps == 0

    def test_start_step_sets_deadline(self):
        """Should set initial deadline on first start_step."""
        scheduler = RealTimeScheduler(target_dt=0.01)
        scheduler.start_step()

        assert scheduler._next_deadline is not None

    def test_wait_for_next_step_met_deadline(self):
        """Should return True if deadline was met."""
        scheduler = RealTimeScheduler(target_dt=0.1)  # 100ms
        scheduler.start_step()

        # Immediately wait (should meet deadline)
        met = scheduler.wait_for_next_step()
        assert met == True

    def test_wait_for_next_step_missed_deadline(self):
        """Should return False and track missed deadline."""
        scheduler = RealTimeScheduler(target_dt=0.001, tolerance=0.0001)  # 1ms
        scheduler.start_step()
        time.sleep(0.01)  # Sleep 10ms (way past deadline)

        met = scheduler.wait_for_next_step()
        assert met == False
        assert scheduler._missed_deadlines == 1

    def test_get_timing_stats_zero_steps(self):
        """Should return zero stats if no steps executed."""
        scheduler = RealTimeScheduler(target_dt=0.01)
        stats = scheduler.get_timing_stats()

        assert stats["deadline_miss_rate"] == 0.0
        assert stats["total_steps"] == 0
        assert stats["missed_deadlines"] == 0

    def test_get_timing_stats_after_steps(self):
        """Should compute correct statistics after steps."""
        scheduler = RealTimeScheduler(target_dt=0.1)
        scheduler.start_step()
        scheduler.wait_for_next_step()  # Met
        scheduler.start_step()
        scheduler.wait_for_next_step()  # Met

        stats = scheduler.get_timing_stats()
        assert stats["total_steps"] == 2
        assert stats["deadline_miss_rate"] <= 0.5  # At most 1 miss
        assert "target_dt" in stats
        assert "tolerance" in stats

    def test_reset(self):
        """Should reset scheduler state."""
        scheduler = RealTimeScheduler(target_dt=0.01)
        scheduler.start_step()
        scheduler.wait_for_next_step()
        scheduler.reset()

        assert scheduler._next_deadline is None
        assert scheduler._missed_deadlines == 0
        assert scheduler._total_steps == 0


# ======================================================================================
# AdaptiveTimeStep Tests
# ======================================================================================

class TestAdaptiveTimeStep:
    """Test AdaptiveTimeStep class."""

    def test_initialization(self):
        """Should initialize with default parameters."""
        ats = AdaptiveTimeStep(initial_dt=0.01)

        assert ats.dt == 0.01
        assert ats.min_dt == 1e-6
        assert ats.max_dt == 1e-1
        assert ats.safety_factor == 0.9
        assert ats.growth_factor == 1.5
        assert ats.shrink_factor == 0.5

    def test_initialization_custom_params(self):
        """Should initialize with custom parameters."""
        ats = AdaptiveTimeStep(
            initial_dt=0.05,
            min_dt=1e-4,
            max_dt=0.5,
            safety_factor=0.8,
            growth_factor=2.0,
            shrink_factor=0.3
        )

        assert ats.dt == 0.05
        assert ats.min_dt == 1e-4
        assert ats.max_dt == 0.5

    def test_update_step_size_small_error_grows(self):
        """Should increase dt for very small error."""
        ats = AdaptiveTimeStep(initial_dt=0.01, growth_factor=1.5)
        error = 0.001  # Very small
        tolerance = 1.0

        new_dt, accept = ats.update_step_size(error, tolerance)

        assert accept == True
        assert new_dt > 0.01  # Should grow

    def test_update_step_size_acceptable_error_unchanged(self):
        """Should keep dt unchanged for acceptable error."""
        ats = AdaptiveTimeStep(initial_dt=0.01)
        error = 0.5  # Acceptable but not tiny
        tolerance = 1.0

        new_dt, accept = ats.update_step_size(error, tolerance)

        assert accept == True
        assert new_dt == 0.01  # Unchanged

    def test_update_step_size_large_error_shrinks(self):
        """Should decrease dt for large error."""
        ats = AdaptiveTimeStep(initial_dt=0.01, shrink_factor=0.5)
        error = 2.0  # Too large
        tolerance = 1.0

        new_dt, accept = ats.update_step_size(error, tolerance)

        assert accept == False
        assert new_dt < 0.01  # Should shrink

    def test_update_step_size_respects_min_dt(self):
        """Should not go below min_dt."""
        ats = AdaptiveTimeStep(initial_dt=1e-5, min_dt=1e-6)
        error = 1e10  # Extremely large
        tolerance = 1.0

        new_dt, accept = ats.update_step_size(error, tolerance)

        assert new_dt >= 1e-6  # Clamped to min_dt

    def test_update_step_size_respects_max_dt(self):
        """Should not exceed max_dt."""
        ats = AdaptiveTimeStep(initial_dt=0.05, max_dt=0.1, growth_factor=5.0)
        error = 0.001  # Very small
        tolerance = 1.0

        new_dt, accept = ats.update_step_size(error, tolerance)

        assert new_dt <= 0.1  # Clamped to max_dt

    def test_get_statistics_empty(self):
        """Should return empty dict if no steps taken."""
        ats = AdaptiveTimeStep(initial_dt=0.01)
        stats = ats.get_statistics()

        assert stats == {}

    def test_get_statistics_after_updates(self):
        """Should compute correct statistics after updates."""
        ats = AdaptiveTimeStep(initial_dt=0.01)

        # Take 3 steps with different errors
        ats.update_step_size(0.001, 1.0)  # Small error
        ats.update_step_size(0.5, 1.0)    # Medium error
        ats.update_step_size(2.0, 1.0)    # Large error

        stats = ats.get_statistics()

        assert stats["total_steps"] == 3
        assert "average_dt" in stats
        assert "min_dt_used" in stats
        assert "max_dt_used" in stats
        assert "current_dt" in stats
        assert "average_error" in stats
        assert stats["average_error"] > 0.0


# ======================================================================================
# Integration Tests
# ======================================================================================

class TestTimeDomainIntegration:
    """Integration tests across time domain components."""

    def test_time_manager_full_simulation(self):
        """Should run complete simulation with TimeManager."""
        tm = TimeManager(dt=0.01, total_time=0.1)
        tm.start_simulation()

        steps = 0
        while not tm.is_finished():
            tm.advance_step()
            steps += 1

        assert tm.current_time >= 0.1
        # Due to floating point precision, horizon ceil(0.1/0.01)=10, but
        # 0.01*10 may not exactly equal 0.1, causing one extra step
        assert tm.current_step in [10, 11]
        assert tm.progress == 1.0
        assert steps in [10, 11]

    def test_adaptive_timestep_sequence(self):
        """Should adapt time step across multiple updates."""
        ats = AdaptiveTimeStep(initial_dt=0.01, min_dt=0.001, max_dt=0.1)

        # Simulate alternating error conditions
        errors = [0.001, 2.0, 0.5, 0.001, 5.0, 0.1]
        tolerance = 1.0

        for error in errors:
            ats.update_step_size(error, tolerance)

        stats = ats.get_statistics()
        assert stats["total_steps"] == 6
        assert 0.001 <= stats["min_dt_used"] <= 0.1
        assert 0.001 <= stats["max_dt_used"] <= 0.1
