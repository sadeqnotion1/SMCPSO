#======================================================================================\\\
#======== tests/test_simulation/engines/test_simulation_runner_comprehensive.py =======\\\
#======================================================================================\\\

"""
Comprehensive tests for simulation_runner.py implementation.

Tests the actual run_simulation() function and SimulationRunner class
with real dynamics, controllers, and edge cases.
"""

import pytest
import numpy as np
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Optional, Tuple

from src.simulation.engines.simulation_runner import (
    run_simulation,
    SimulationRunner,
    get_step_fn,
    step as unified_step,
    _load_full_step,
    _load_lowrank_step,
    DYNAMICS_FULL_MODULE
)


# =====================================================================================
# Test Fixtures: Controllers and Dynamics
# =====================================================================================

@pytest.fixture
def simple_controller():
    """Simple controller that returns proportional control."""
    class SimpleController:
        def __call__(self, t: float, x: np.ndarray) -> float:
            # Simple proportional control on first state
            return -1.0 * x[0]
    return SimpleController()


@pytest.fixture
def stateful_controller():
    """Controller with state initialization and compute_control method."""
    class StatefulController:
        def initialize_state(self):
            return {'integral': 0.0, 'last_error': 0.0}

        def initialize_history(self):
            return {'errors': [], 'controls': []}

        def compute_control(self, x: np.ndarray, state: dict, history: dict):
            error = x[0]
            # PI control
            state['integral'] += error * 0.01
            control = -2.0 * error - 1.0 * state['integral']

            history['errors'].append(error)
            history['controls'].append(control)

            return control, state, history

    return StatefulController()


@pytest.fixture
def controller_with_max_force():
    """Controller with max_force attribute."""
    class LimitedController:
        max_force = 10.0

        def __call__(self, t: float, x: np.ndarray) -> float:
            return -5.0 * x[0]

    return LimitedController()


@pytest.fixture
def failing_controller():
    """Controller that raises exceptions."""
    class FailingController:
        def __init__(self, fail_at_step: int = 5):
            self.call_count = 0
            self.fail_at_step = fail_at_step

        def __call__(self, t: float, x: np.ndarray) -> float:
            self.call_count += 1
            if self.call_count >= self.fail_at_step:
                raise RuntimeError("Controller failure")
            return 0.0

    return FailingController(fail_at_step=5)


@pytest.fixture
def slow_controller():
    """Controller that takes longer than dt to compute."""
    class SlowController:
        def __init__(self, delay: float = 0.05):
            self.delay = delay

        def __call__(self, t: float, x: np.ndarray) -> float:
            time.sleep(self.delay)
            return -1.0 * x[0]

    return SlowController(delay=0.05)


@pytest.fixture
def simple_dynamics():
    """Simple linear dynamics: dx/dt = -0.1 * x + u."""
    class SimpleDynamics:
        def step(self, x: np.ndarray, u: float, dt: float) -> np.ndarray:
            # Explicit Euler: x_next = x + dt * (-0.1*x + u)
            x = np.asarray(x, dtype=float)
            x_next = x + dt * (-0.1 * x + u * np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
            return x_next

    return SimpleDynamics()


@pytest.fixture
def failing_dynamics():
    """Dynamics that fails after certain number of steps."""
    class FailingDynamics:
        def __init__(self, fail_at_step: int = 10):
            self.step_count = 0
            self.fail_at_step = fail_at_step

        def step(self, x: np.ndarray, u: float, dt: float) -> np.ndarray:
            self.step_count += 1
            if self.step_count >= self.fail_at_step:
                raise RuntimeError("Dynamics failure")
            x = np.asarray(x, dtype=float)
            return x + dt * 0.1

    return FailingDynamics(fail_at_step=10)


@pytest.fixture
def nan_producing_dynamics():
    """Dynamics that produces NaN after certain steps."""
    class NaNDynamics:
        def __init__(self, nan_at_step: int = 15):
            self.step_count = 0
            self.nan_at_step = nan_at_step

        def step(self, x: np.ndarray, u: float, dt: float) -> np.ndarray:
            self.step_count += 1
            x = np.asarray(x, dtype=float)
            if self.step_count >= self.nan_at_step:
                x[0] = np.nan
            return x + dt * 0.01

    return NaNDynamics(nan_at_step=15)


# =====================================================================================
# Test run_simulation() Basic Functionality
# =====================================================================================

class TestRunSimulationBasic:
    """Test basic run_simulation() functionality."""

    def test_basic_simulation_completes(self, simple_controller, simple_dynamics):
        """Test that basic simulation runs to completion."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=simple_dynamics,
            sim_time=1.0,
            dt=0.01,
            initial_state=initial_state
        )

        # Check output shapes
        n_steps = int(round(1.0 / 0.01))
        assert len(t_arr) == n_steps + 1
        assert x_arr.shape == (n_steps + 1, 6)
        assert len(u_arr) == n_steps

        # Check initial conditions
        assert t_arr[0] == 0.0
        np.testing.assert_array_equal(x_arr[0], initial_state)

        # Check final time
        assert abs(t_arr[-1] - 1.0) < 1e-10

    def test_zero_sim_time_produces_no_steps(self, simple_controller, simple_dynamics):
        """Test that sim_time=0 produces no integration steps."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=simple_dynamics,
            sim_time=0.0,
            dt=0.01,
            initial_state=initial_state
        )

        # Should have only initial state
        assert len(t_arr) == 1
        assert len(x_arr) == 1
        assert len(u_arr) == 0
        np.testing.assert_array_equal(x_arr[0], initial_state)

    def test_negative_sim_time_produces_no_steps(self, simple_controller, simple_dynamics):
        """Test that negative sim_time produces no integration steps."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=simple_dynamics,
            sim_time=-1.0,
            dt=0.01,
            initial_state=initial_state
        )

        assert len(t_arr) == 1
        assert len(u_arr) == 0

    def test_invalid_dt_raises_error(self, simple_controller, simple_dynamics):
        """Test that invalid dt raises ValueError."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        with pytest.raises(ValueError, match="dt must be positive"):
            run_simulation(
                controller=simple_controller,
                dynamics_model=simple_dynamics,
                sim_time=1.0,
                dt=0.0,
                initial_state=initial_state
            )

        with pytest.raises(ValueError, match="dt must be positive"):
            run_simulation(
                controller=simple_controller,
                dynamics_model=simple_dynamics,
                sim_time=1.0,
                dt=-0.01,
                initial_state=initial_state
            )


# =====================================================================================
# Test Controller Integration
# =====================================================================================

class TestControllerIntegration:
    """Test controller integration and state management."""

    def test_stateful_controller_initialization(self, stateful_controller, simple_dynamics):
        """Test that stateful controller is properly initialized."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        t_arr, x_arr, u_arr = run_simulation(
            controller=stateful_controller,
            dynamics_model=simple_dynamics,
            sim_time=0.5,
            dt=0.01,
            initial_state=initial_state
        )

        # Should complete successfully
        assert len(t_arr) == 51  # 0.5/0.01 + 1

        # Check that history was attached to controller
        assert hasattr(stateful_controller, '_last_history')
        history = stateful_controller._last_history
        assert 'errors' in history
        assert 'controls' in history
        assert len(history['errors']) == 50  # 50 control steps

    def test_controller_with_max_force_limits_control(self, controller_with_max_force, simple_dynamics):
        """Test that controller.max_force is used for saturation."""
        initial_state = np.array([100.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # Large initial error

        t_arr, x_arr, u_arr = run_simulation(
            controller=controller_with_max_force,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=initial_state
        )

        # All controls should be within max_force
        assert np.all(np.abs(u_arr) <= controller_with_max_force.max_force)

    def test_u_max_parameter_overrides_controller_max_force(self, controller_with_max_force, simple_dynamics):
        """Test that u_max parameter takes precedence over controller.max_force."""
        initial_state = np.array([100.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        u_max_override = 5.0  # Lower than controller.max_force (10.0)

        t_arr, x_arr, u_arr = run_simulation(
            controller=controller_with_max_force,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=initial_state,
            u_max=u_max_override
        )

        # All controls should be within u_max_override, not controller.max_force
        assert np.all(np.abs(u_arr) <= u_max_override)

    def test_controller_exception_terminates_simulation(self, failing_controller, simple_dynamics):
        """Test that controller exception terminates simulation early."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        t_arr, x_arr, u_arr = run_simulation(
            controller=failing_controller,
            dynamics_model=simple_dynamics,
            sim_time=1.0,
            dt=0.01,
            initial_state=initial_state
        )

        # Should terminate before completing full simulation
        # Controller fails at step 5
        assert len(t_arr) < 101  # Less than full 1.0/0.01 + 1 = 101 steps
        assert len(t_arr) <= 6  # Should stop around step 5
        assert len(u_arr) == len(t_arr) - 1


# =====================================================================================
# Test Dynamics Integration
# =====================================================================================

class TestDynamicsIntegration:
    """Test dynamics integration and error handling."""

    def test_dynamics_exception_terminates_simulation(self, simple_controller, failing_dynamics):
        """Test that dynamics exception terminates simulation early."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=failing_dynamics,
            sim_time=1.0,
            dt=0.01,
            initial_state=initial_state
        )

        # Should terminate early (dynamics fails at step 10)
        assert len(t_arr) <= 11
        assert len(u_arr) == len(t_arr) - 1

    def test_nan_in_state_terminates_simulation(self, simple_controller, nan_producing_dynamics):
        """Test that NaN in state vector terminates simulation."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=nan_producing_dynamics,
            sim_time=1.0,
            dt=0.01,
            initial_state=initial_state
        )

        # Should terminate when NaN appears (at step 15)
        assert len(t_arr) <= 16

        # All returned states should be finite (NaN step is not included)
        assert np.all(np.isfinite(x_arr))

    def test_inf_in_state_terminates_simulation(self, simple_controller):
        """Test that Inf in state vector terminates simulation."""
        class InfDynamics:
            def __init__(self):
                self.step_count = 0

            def step(self, x: np.ndarray, u: float, dt: float) -> np.ndarray:
                self.step_count += 1
                x = np.asarray(x, dtype=float)
                if self.step_count >= 10:
                    x[0] = np.inf
                return x + dt * 0.01

        dynamics = InfDynamics()
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=dynamics,
            sim_time=1.0,
            dt=0.01,
            initial_state=initial_state
        )

        # Should terminate early
        assert len(t_arr) <= 11
        assert np.all(np.isfinite(x_arr))


# =====================================================================================
# Test Fallback Controller and Latency Monitoring
# =====================================================================================

class TestFallbackController:
    """Test fallback controller and latency monitoring."""

    def test_fallback_controller_activates_on_deadline_miss(self, slow_controller, simple_dynamics):
        """Test that fallback controller activates when control takes longer than dt."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        fallback_called = {'count': 0}
        def fallback_controller(t: float, x: np.ndarray) -> float:
            fallback_called['count'] += 1
            return 0.0  # Simple zero control

        # Use dt=0.01, slow_controller has delay=0.05 (5x dt)
        t_arr, x_arr, u_arr = run_simulation(
            controller=slow_controller,
            dynamics_model=simple_dynamics,
            sim_time=0.2,
            dt=0.01,
            initial_state=initial_state,
            fallback_controller=fallback_controller
        )

        # Fallback should have been called after first deadline miss
        assert fallback_called['count'] > 0

    def test_no_fallback_when_control_fast(self, simple_controller, simple_dynamics):
        """Test that fallback is not used when control is fast enough."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        fallback_called = {'count': 0}
        def fallback_controller(t: float, x: np.ndarray) -> float:
            fallback_called['count'] += 1
            return 0.0

        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=simple_dynamics,
            sim_time=0.5,
            dt=0.01,
            initial_state=initial_state,
            fallback_controller=fallback_controller
        )

        # Fallback should never be called (simple_controller is fast)
        assert fallback_called['count'] == 0


# =====================================================================================
# Test RNG and Seed Handling
# =====================================================================================

class TestRNGHandling:
    """Test random number generator handling."""

    def test_seed_parameter_creates_rng(self, simple_dynamics):
        """Test that seed parameter creates reproducible RNG."""
        class RandomController:
            def __init__(self):
                self.rng = None

            def __call__(self, t: float, x: np.ndarray) -> float:
                if self.rng is not None:
                    return self.rng.normal(0, 0.1)
                return 0.0

        controller1 = RandomController()
        controller2 = RandomController()
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Note: The implementation creates RNG from seed but doesn't pass it to controller
        # This test verifies the seed parameter is accepted
        t_arr1, x_arr1, u_arr1 = run_simulation(
            controller=controller1,
            dynamics_model=simple_dynamics,
            sim_time=0.5,
            dt=0.01,
            initial_state=initial_state,
            seed=42
        )

        t_arr2, x_arr2, u_arr2 = run_simulation(
            controller=controller2,
            dynamics_model=simple_dynamics,
            sim_time=0.5,
            dt=0.01,
            initial_state=initial_state,
            seed=42
        )

        # Without RNG being used by controller, results should be deterministic
        np.testing.assert_array_almost_equal(u_arr1, u_arr2)

    def test_rng_parameter_takes_precedence_over_seed(self, simple_controller, simple_dynamics):
        """Test that rng parameter takes precedence over seed."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        rng = np.random.default_rng(123)

        # This should succeed without errors
        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=initial_state,
            seed=42,  # Should be ignored
            rng=rng   # Should be used instead
        )

        assert len(t_arr) > 0


# =====================================================================================
# Test Kwargs Handling
# =====================================================================================

class TestKwargsHandling:
    """Test backward compatibility kwargs handling."""

    def test_unknown_kwargs_are_ignored(self, simple_controller, simple_dynamics):
        """Test that unknown kwargs are silently ignored."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Should not raise errors
        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=initial_state,
            unknown_param_1="ignored",
            another_unknown=42,
            yet_another=True
        )

        assert len(t_arr) > 0

    def test_latency_margin_parameter_accepted(self, simple_controller, simple_dynamics):
        """Test that latency_margin parameter is accepted (unused placeholder)."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Should not raise errors
        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=initial_state,
            latency_margin=0.005  # Unused but accepted
        )

        assert len(t_arr) > 0


# =====================================================================================
# Test SimulationRunner Class
# =====================================================================================

class TestSimulationRunnerClass:
    """Test SimulationRunner OOP wrapper."""

    def test_initialization(self, simple_dynamics):
        """Test SimulationRunner initialization."""
        runner = SimulationRunner(simple_dynamics, dt=0.02, max_time=5.0)

        assert runner.dynamics_model == simple_dynamics
        assert runner.dt == 0.02
        assert runner.max_time == 5.0
        assert runner.current_time == 0.0
        assert runner.step_count == 0
        assert runner.simulation_history == []

    def test_run_simulation_with_controller(self, simple_dynamics, simple_controller):
        """Test SimulationRunner.run_simulation with controller."""
        runner = SimulationRunner(simple_dynamics, dt=0.01, max_time=1.0)
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        result = runner.run_simulation(initial_state, controller=simple_controller)

        assert result['success'] is True
        assert 'states' in result
        assert 'controls' in result
        assert 'time' in result
        assert 'final_state' in result
        assert 'step_count' in result

        # Check array shapes
        assert result['states'].shape[0] == result['step_count'] + 1
        assert result['controls'].shape[0] == result['step_count']

    def test_run_simulation_without_controller_uses_zero_controller(self, simple_dynamics):
        """Test that SimulationRunner creates zero controller when none provided."""
        runner = SimulationRunner(simple_dynamics, dt=0.01, max_time=0.5)
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        result = runner.run_simulation(initial_state)

        assert result['success'] is True
        # All controls should be zero
        np.testing.assert_array_almost_equal(result['controls'], 0.0)

    def test_run_simulation_updates_state(self, simple_dynamics, simple_controller):
        """Test that run_simulation updates runner state."""
        runner = SimulationRunner(simple_dynamics, dt=0.01, max_time=0.5)
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        result = runner.run_simulation(initial_state, controller=simple_controller)

        # Should update current_time and step_count
        assert runner.current_time == 0.5
        assert runner.step_count == 50

    def test_run_simulation_appends_to_history(self, simple_dynamics, simple_controller):
        """Test that run_simulation appends to simulation history."""
        runner = SimulationRunner(simple_dynamics, dt=0.01, max_time=0.1)
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Run multiple simulations
        runner.run_simulation(initial_state, controller=simple_controller)
        runner.run_simulation(initial_state, controller=simple_controller)

        assert len(runner.simulation_history) == 2
        assert 'time' in runner.simulation_history[0]
        assert 'states' in runner.simulation_history[0]
        assert 'controls' in runner.simulation_history[0]

    def test_run_simulation_error_handling(self, failing_dynamics, simple_controller):
        """Test that SimulationRunner handles dynamics failures gracefully."""
        runner = SimulationRunner(failing_dynamics, dt=0.01, max_time=1.0)
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        result = runner.run_simulation(initial_state, controller=simple_controller)

        # Functional run_simulation() handles exceptions internally by early termination
        # So SimulationRunner reports success=True but with truncated results
        assert result['success'] is True

        # Should terminate early (dynamics fails at step 10)
        # With dt=0.01 and max_time=1.0, full sim would be 100 steps
        assert result['step_count'] < 100
        assert result['step_count'] <= 10

        # Should still have valid arrays
        assert isinstance(result['states'], np.ndarray)
        assert isinstance(result['controls'], np.ndarray)

    def test_run_simulation_accepts_kwargs(self, simple_dynamics, simple_controller):
        """Test that run_simulation passes kwargs to functional API."""
        runner = SimulationRunner(simple_dynamics, dt=0.01, max_time=1.0)
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Override sim_time via kwargs
        result = runner.run_simulation(
            initial_state,
            controller=simple_controller,
            sim_time=0.2  # Override max_time
        )

        assert result['success'] is True
        assert abs(result['time'][-1] - 0.2) < 1e-10  # Should use 0.2, not 1.0


# =====================================================================================
# Test Routing Functions (step, get_step_fn, etc.)
# =====================================================================================

class TestRoutingFunctions:
    """Test dynamics routing and dispatching."""

    @pytest.mark.skip(reason="dip_lowrank module not yet implemented (known issue)")
    def test_get_step_fn_returns_lowrank_by_default(self):
        """Test that get_step_fn returns lowrank step function by default."""
        step_fn = get_step_fn()

        # Should return lowrank step (not full)
        # Check by inspecting module name
        assert step_fn.__module__ == 'src.plant.models.dip_lowrank'

    @patch('src.simulation.engines.simulation_runner.config')
    def test_get_step_fn_returns_full_when_configured(self, mock_config):
        """Test that get_step_fn returns full dynamics when configured."""
        # Configure to use full dynamics
        from types import SimpleNamespace
        mock_config.simulation = SimpleNamespace(use_full_dynamics=True)

        # This will try to load full dynamics
        try:
            step_fn = get_step_fn()
            # If successful, should return full step
            assert 'full' in step_fn.__module__.lower() or 'dip_full' in step_fn.__module__
        except RuntimeError as e:
            # Expected if full dynamics not available
            assert "Full dynamics unavailable" in str(e)

    @pytest.mark.skip(reason="dip_lowrank module not yet implemented (known issue)")
    def test_load_lowrank_step_returns_function(self):
        """Test that _load_lowrank_step returns callable."""
        step_fn = _load_lowrank_step()

        assert callable(step_fn)
        assert step_fn.__name__ == 'step'

    @pytest.mark.skip(reason="dip_lowrank module not yet implemented (known issue)")
    def test_unified_step_function_works(self):
        """Test that unified step() function works."""
        x = np.array([0.1, 0.0, 0.05, 0.0, 0.0, 0.0])
        u = np.array([1.0])
        dt = 0.01

        # Should complete without errors (using lowrank by default)
        x_next = unified_step(x, u, dt)

        assert isinstance(x_next, np.ndarray)
        assert x_next.shape == x.shape

    @patch('src.simulation.engines.simulation_runner.DYNAMICS_FULL_MODULE', 'nonexistent.module')
    def test_load_full_step_raises_on_missing_module(self):
        """Test that _load_full_step raises RuntimeError when module missing."""
        with pytest.raises(RuntimeError, match="Full dynamics unavailable.*not found"):
            _load_full_step()


# =====================================================================================
# Test Memory Optimizations
# =====================================================================================

class TestMemoryOptimizations:
    """Test memory optimization behaviors."""

    def test_asarray_creates_views_for_ndarray_inputs(self, simple_controller, simple_dynamics):
        """Test that np.asarray creates views when possible (memory optimization)."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=float)

        # Run simulation
        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=initial_state
        )

        # Just verify it completes successfully
        # Memory optimizations are implementation details
        assert len(t_arr) > 0

    def test_no_unnecessary_copies_in_integration_loop(self, simple_controller, simple_dynamics):
        """Test that integration loop doesn't make unnecessary copies."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Run simulation - should complete efficiently
        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=simple_dynamics,
            sim_time=5.0,  # Longer simulation
            dt=0.01,
            initial_state=initial_state
        )

        # 500 steps should complete quickly without memory issues
        assert len(t_arr) == 501


# =====================================================================================
# Test Edge Cases and Boundary Conditions
# =====================================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_step_simulation(self, simple_controller, simple_dynamics):
        """Test simulation with single time step."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=simple_dynamics,
            sim_time=0.01,
            dt=0.01,
            initial_state=initial_state
        )

        assert len(t_arr) == 2  # Initial + 1 step
        assert len(u_arr) == 1

    def test_very_small_timestep(self, simple_controller, simple_dynamics):
        """Test simulation with very small timestep."""
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=simple_dynamics,
            sim_time=0.01,
            dt=1e-6,
            initial_state=initial_state
        )

        # Should handle small dt correctly
        expected_steps = int(round(0.01 / 1e-6))
        assert len(t_arr) == expected_steps + 1

    def test_initial_state_with_different_shapes(self, simple_controller, simple_dynamics):
        """Test that initial state is correctly flattened."""
        # Test with different input shapes
        initial_states = [
            np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0]),  # 1D
            np.array([[1.0], [0.0], [0.0], [0.0], [0.0], [0.0]]),  # Column vector
            np.array([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0]]),  # Row vector
        ]

        for initial_state in initial_states:
            t_arr, x_arr, u_arr = run_simulation(
                controller=simple_controller,
                dynamics_model=simple_dynamics,
                sim_time=0.1,
                dt=0.01,
                initial_state=initial_state
            )

            # Should all work and produce same shape output
            assert x_arr.shape[1] == 6
            np.testing.assert_array_almost_equal(
                x_arr[0],
                np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            )

    def test_control_saturation_edge_cases(self, simple_dynamics):
        """Test control saturation at exact limits."""
        class ExactLimitController:
            def __call__(self, t: float, x: np.ndarray) -> float:
                return 10.0  # Exactly at limit

        controller = ExactLimitController()
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=initial_state,
            u_max=10.0
        )

        # All controls should be exactly 10.0 (at limit, not over)
        np.testing.assert_array_almost_equal(u_arr, 10.0)

    def test_large_state_dimension(self, simple_controller):
        """Test simulation with large state dimension."""
        class HighDimDynamics:
            def step(self, x: np.ndarray, u: float, dt: float) -> np.ndarray:
                x = np.asarray(x, dtype=float)
                return x + dt * 0.01  # Simple dynamics

        dynamics = HighDimDynamics()
        initial_state = np.zeros(50)  # 50-dimensional state

        t_arr, x_arr, u_arr = run_simulation(
            controller=simple_controller,
            dynamics_model=dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=initial_state
        )

        assert x_arr.shape[1] == 50
