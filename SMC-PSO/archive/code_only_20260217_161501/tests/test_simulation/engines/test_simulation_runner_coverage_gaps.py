#======================================================================================\\
#======= tests/test_simulation/engines/test_simulation_runner_coverage_gaps.py ========\\
#======================================================================================\\

"""
Coverage gap tests for Simulation Runner.
Target: Fill gaps from 60.20% to 95%+ coverage.
Focus: Exception handling, edge cases, parameter validation.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.simulation.engines.simulation_runner import (
    run_simulation,
    SimulationRunner,
    get_step_fn,
    _load_full_step,
    _load_lowrank_step,
    DYNAMICS_FULL_MODULE
)


class TestControllerEdgeCases:
    """Test edge cases in controller parameter extraction."""

    @pytest.fixture
    def simple_dynamics(self):
        """Simple dynamics for testing."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state + 0.01
        return SimpleDynamics()

    def test_invalid_u_max_falls_back_to_none(self, simple_dynamics):
        """Test u_max validation exception falls back to None (lines 224-226)."""
        class SimpleController:
            def __call__(self, t, x):
                return 10.0

        controller = SimpleController()

        # Pass invalid u_max that can't be converted to float
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=np.array([1.0, 0.0]),
            u_max="invalid"  # Will cause exception in float(u_max)
        )

        # Should complete without saturation (u_lim = None)
        assert len(t_arr) == 11
        # Control values may be large (not saturated)
        assert np.all(u_arr == 10.0)

    def test_invalid_max_force_attribute_falls_back_to_none(self, simple_dynamics):
        """Test controller.max_force exception handling (lines 229-233)."""
        class BadMaxForceController:
            # Use non-callable max_force that can't be converted to float
            max_force = "invalid"

            def __call__(self, t, x):
                return 10.0

        controller = BadMaxForceController()

        # Should handle max_force conversion exception gracefully
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=np.array([1.0, 0.0])
        )

        # Should complete without saturation (u_lim = None)
        assert len(t_arr) == 11
        assert np.all(u_arr == 10.0)

    def test_invalid_seed_falls_back_to_none(self, simple_dynamics):
        """Test seed parameter exception handling (lines 237-240)."""
        class SimpleController:
            def __call__(self, t, x):
                return 0.0

        controller = SimpleController()

        # Pass invalid seed that can't be converted to int
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=np.array([1.0, 0.0]),
            seed="invalid"  # Will cause exception in int(seed)
        )

        # Should complete with rng = None
        assert len(t_arr) == 11


class TestControllerInitializationFailures:
    """Test controller initialization failure paths."""

    @pytest.fixture
    def simple_dynamics(self):
        """Simple dynamics for testing."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state + 0.01
        return SimpleDynamics()

    def test_initialize_state_exception_handled(self, simple_dynamics):
        """Test initialize_state exception handling (lines 245-248)."""
        class FailingInitStateController:
            def initialize_state(self):
                raise RuntimeError("State initialization failed")

            def __call__(self, t, x):
                return -x[0]

        controller = FailingInitStateController()

        # Should handle exception gracefully, proceed with ctrl_state = None
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=np.array([1.0, 0.0])
        )

        # Should complete successfully
        assert len(t_arr) == 11

    def test_initialize_history_exception_handled(self, simple_dynamics):
        """Test initialize_history exception handling (lines 250-253)."""
        class FailingInitHistoryController:
            def initialize_history(self):
                raise RuntimeError("History initialization failed")

            def __call__(self, t, x):
                return -x[0]

        controller = FailingInitHistoryController()

        # Should handle exception gracefully, proceed with history = None
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=np.array([1.0, 0.0])
        )

        # Should complete successfully
        assert len(t_arr) == 11


class TestControlComputationEdgeCases:
    """Test edge cases in control computation."""

    @pytest.fixture
    def simple_dynamics(self):
        """Simple dynamics for testing."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state + 0.01
        return SimpleDynamics()

    def test_compute_control_returns_tuple_with_scalar(self, simple_dynamics):
        """Test compute_control returning (scalar,) tuple (lines 273-275)."""
        class TupleController:
            def compute_control(self, x, state, history):
                return (-x[0],)  # Tuple with single element

        controller = TupleController()

        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=np.array([1.0, 0.0])
        )

        # Should extract u_val correctly from tuple
        assert len(t_arr) == 11

    def test_compute_control_exception_in_unpacking(self, simple_dynamics):
        """Test exception in ret[1] unpacking (lines 277-282)."""
        class NonSubscriptableReturnController:
            def compute_control(self, x, state, history):
                # Return single value (no tuple unpacking possible)
                # This tests the except block at lines 281-282
                return -x[0]  # Single float, not a tuple

        controller = NonSubscriptableReturnController()

        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=simple_dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=np.array([1.0, 0.0])
        )

        # Should complete successfully (state/history remain None)
        assert len(t_arr) == 11


class TestHistoryAttachmentFailures:
    """Test history attachment failure paths."""

    @pytest.fixture
    def simple_dynamics(self):
        """Simple dynamics for testing."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                if state[0] > 0.5:
                    raise ValueError("Dynamics failure")
                return state + 0.1
        return SimpleDynamics()

    def test_history_attachment_fails_on_controller_exception(self, simple_dynamics):
        """Test history attachment failure on controller exception (lines 298-302)."""
        class HistoryController:
            def __init__(self):
                self.__dict__['_frozen'] = True  # Make setattr fail

            def initialize_history(self):
                return {'count': 0}

            def compute_control(self, x, state, history):
                history['count'] += 1
                if history['count'] > 5:
                    raise RuntimeError("Controller failed")
                return 0.0, state, history

            def __setattr__(self, name, value):
                if self.__dict__.get('_frozen'):
                    raise AttributeError("Cannot set attribute")
                super().__setattr__(name, value)

        controller = HistoryController()

        # Should handle both controller exception and setattr failure
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=simple_dynamics,
            sim_time=1.0,
            dt=0.01,
            initial_state=np.array([0.0, 0.0]),
            strict_mode=False
        )

        # Should stop early due to controller exception
        assert len(t_arr) < 101

    def test_history_attachment_fails_on_dynamics_exception(self):
        """Test history attachment failure on dynamics exception (lines 329-333)."""
        class FailingDynamics:
            def step(self, state, u, dt):
                if state[0] > 0.05:
                    raise ValueError("Dynamics failure")
                return state + 0.01

        class HistoryController:
            def __init__(self):
                self.__dict__['_frozen'] = True

            def initialize_history(self):
                return {'count': 0}

            def compute_control(self, x, state, history):
                history['count'] += 1
                return 0.0, state, history

            def __setattr__(self, name, value):
                if self.__dict__.get('_frozen'):
                    raise AttributeError("Cannot set attribute")
                super().__setattr__(name, value)

        controller = HistoryController()
        dynamics = FailingDynamics()

        # Should handle both dynamics exception and setattr failure
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=dynamics,
            sim_time=1.0,
            dt=0.01,
            initial_state=np.array([0.0, 0.0]),
            strict_mode=False
        )

        # Should stop early
        assert len(t_arr) < 101

    def test_history_attachment_fails_on_nonfinite_state(self):
        """Test history attachment failure on non-finite state (lines 349-353)."""
        class NanDynamics:
            def step(self, state, u, dt):
                if state[0] > 0.05:
                    return np.array([np.nan, np.nan])
                return state + 0.01

        class HistoryController:
            def __init__(self):
                self.__dict__['_frozen'] = True

            def initialize_history(self):
                return {'count': 0}

            def compute_control(self, x, state, history):
                history['count'] += 1
                return 0.0, state, history

            def __setattr__(self, name, value):
                if self.__dict__.get('_frozen'):
                    raise AttributeError("Cannot set attribute")
                super().__setattr__(name, value)

        controller = HistoryController()
        dynamics = NanDynamics()

        # Should handle both NaN state and setattr failure
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=dynamics,
            sim_time=1.0,
            dt=0.01,
            initial_state=np.array([0.0, 0.0]),
            strict_mode=False
        )

        # Should stop early
        assert len(t_arr) < 101

    def test_history_attachment_succeeds_at_end(self):
        """Test history attachment at simulation end (lines 359-363)."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state + 0.01

        class HistoryController:
            def initialize_history(self):
                return {'states': [], 'controls': []}

            def compute_control(self, x, state, history):
                history['states'].append(x.copy())
                control = -x[0]
                history['controls'].append(control)
                return control, state, history

        controller = HistoryController()
        dynamics = SimpleDynamics()

        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=np.array([1.0, 0.0])
        )

        # History should be attached
        assert hasattr(controller, '_last_history')
        assert len(controller._last_history['states']) > 0

    def test_history_attachment_fails_at_end(self):
        """Test history attachment failure at simulation end (lines 361-363)."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state + 0.01

        class FrozenController:
            def __init__(self):
                self.__dict__['_frozen'] = True

            def initialize_history(self):
                return {'count': 0}

            def compute_control(self, x, state, history):
                history['count'] += 1
                return 0.0, state, history

            def __setattr__(self, name, value):
                if self.__dict__.get('_frozen'):
                    raise AttributeError("Cannot set attribute")
                super().__setattr__(name, value)

        controller = FrozenController()
        dynamics = SimpleDynamics()

        # Should complete but setattr will fail silently
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=dynamics,
            sim_time=0.1,
            dt=0.01,
            initial_state=np.array([1.0, 0.0])
        )

        # Should complete successfully despite setattr failure
        assert len(t_arr) == 11


class TestDynamicsStepFunctionLoading:
    """Test dynamics step function loading."""

    def test_load_full_step_raises_runtime_error(self):
        """Test _load_full_step raises RuntimeError on missing module."""
        # Monkeypatch DYNAMICS_FULL_MODULE to a non-existent module
        with patch('src.simulation.engines.simulation_runner.DYNAMICS_FULL_MODULE', 'nonexistent.module'):
            with pytest.raises(RuntimeError, match="Full dynamics unavailable"):
                _load_full_step()

    def test_load_lowrank_step_returns_callable(self):
        """Test _load_lowrank_step returns a callable."""
        try:
            step_fn = _load_lowrank_step()
            assert callable(step_fn)
        except ImportError:
            # If low-rank dynamics not available, skip
            pytest.skip("Low-rank dynamics not available")

    def test_get_step_fn_with_full_dynamics_enabled(self):
        """Test get_step_fn with use_full_dynamics=True."""
        # Mock config to enable full dynamics
        with patch('src.simulation.engines.simulation_runner.config') as mock_config:
            mock_config.simulation.use_full_dynamics = True

            # Should raise RuntimeError if full dynamics not available
            with pytest.raises(RuntimeError, match="Full dynamics unavailable"):
                get_step_fn()

    def test_get_step_fn_with_lowrank_dynamics(self):
        """Test get_step_fn with use_full_dynamics=False (default)."""
        # Mock config to disable full dynamics
        with patch('src.simulation.engines.simulation_runner.config') as mock_config:
            mock_config.simulation.use_full_dynamics = False

            try:
                step_fn = get_step_fn()
                assert callable(step_fn)
            except ImportError:
                # If low-rank dynamics not available, skip
                pytest.skip("Low-rank dynamics not available")


class TestSimulationRunnerClassEdgeCases:
    """Test SimulationRunner class edge cases."""

    def test_run_simulation_extracts_sim_time_from_kwargs(self):
        """Test run_simulation extracts sim_time from kwargs."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state + 0.01

        dynamics = SimpleDynamics()
        runner = SimulationRunner(dynamics, dt=0.01, max_time=10.0)

        # Pass sim_time via kwargs (should override max_time)
        result = runner.run_simulation(
            initial_state=np.array([1.0, 0.0]),
            sim_time=0.05  # Override max_time=10.0
        )

        # Should use sim_time=0.05 instead of max_time=10.0
        assert result['success'] is True
        assert len(result['time']) == 6  # 0.05/0.01 + 1 = 6

    def test_run_simulation_extracts_dt_from_kwargs(self):
        """Test run_simulation extracts dt from kwargs."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state + 0.01

        dynamics = SimpleDynamics()
        runner = SimulationRunner(dynamics, dt=0.01, max_time=1.0)

        # Pass dt via kwargs (should override self.dt)
        result = runner.run_simulation(
            initial_state=np.array([1.0, 0.0]),
            sim_time=0.1,
            dt=0.02  # Override self.dt=0.01
        )

        # Should use dt=0.02 instead of self.dt=0.01
        assert result['success'] is True
        assert len(result['time']) == 6  # 0.1/0.02 + 1 = 6

    def test_run_simulation_creates_zero_controller_when_none(self):
        """Test run_simulation creates ZeroController when controller is None."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state + 0.01

        dynamics = SimpleDynamics()
        runner = SimulationRunner(dynamics, dt=0.01, max_time=0.1)

        # Pass no controller
        result = runner.run_simulation(
            initial_state=np.array([1.0, 0.0])
        )

        # Should complete with zero control
        assert result['success'] is True
        assert np.all(result['controls'] == 0.0)

    def test_run_simulation_updates_simulation_history(self):
        """Test run_simulation updates simulation_history."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state + 0.01

        dynamics = SimpleDynamics()
        runner = SimulationRunner(dynamics, dt=0.01, max_time=0.1)

        # Run simulation twice
        runner.run_simulation(initial_state=np.array([1.0, 0.0]))
        runner.run_simulation(initial_state=np.array([2.0, 0.0]))

        # Should have 2 entries in history
        assert len(runner.simulation_history) == 2

    def test_run_simulation_updates_current_time_and_step_count(self):
        """Test run_simulation updates current_time and step_count."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state + 0.01

        dynamics = SimpleDynamics()
        runner = SimulationRunner(dynamics, dt=0.01, max_time=0.1)

        result = runner.run_simulation(initial_state=np.array([1.0, 0.0]))

        # Check state tracking
        assert runner.current_time == 0.1
        assert runner.step_count == 10

    def test_run_simulation_exception_returns_error_dict(self):
        """Test run_simulation returns error dict on exception."""
        class FailingDynamics:
            def step(self, state, u, dt):
                raise RuntimeError("Dynamics failure")

        dynamics = FailingDynamics()
        runner = SimulationRunner(dynamics, dt=0.01, max_time=0.1)

        result = runner.run_simulation(
            initial_state=np.array([1.0, 0.0]),
            strict_mode=True  # Force exception to be raised then caught by try/except
        )

        # Should return error dict
        assert result['success'] is False
        assert 'error' in result
        assert result['step_count'] == 0


class TestParameterValidationEdgeCases:
    """Test parameter validation edge cases."""

    def test_dt_zero_raises_value_error(self):
        """Test dt=0 raises ValueError."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state

        class SimpleController:
            def __call__(self, t, x):
                return 0.0

        with pytest.raises(ValueError, match="dt must be positive"):
            run_simulation(
                controller=SimpleController(),
                dynamics_model=SimpleDynamics(),
                sim_time=1.0,
                dt=0.0,
                initial_state=np.array([1.0, 0.0])
            )

    def test_dt_negative_raises_value_error(self):
        """Test dt<0 raises ValueError."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state

        class SimpleController:
            def __call__(self, t, x):
                return 0.0

        with pytest.raises(ValueError, match="dt must be positive"):
            run_simulation(
                controller=SimpleController(),
                dynamics_model=SimpleDynamics(),
                sim_time=1.0,
                dt=-0.01,
                initial_state=np.array([1.0, 0.0])
            )

    def test_sim_time_zero_produces_no_steps(self):
        """Test sim_time=0 produces no integration steps."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state

        class SimpleController:
            def __call__(self, t, x):
                return 0.0

        t_arr, x_arr, u_arr = run_simulation(
            controller=SimpleController(),
            dynamics_model=SimpleDynamics(),
            sim_time=0.0,
            dt=0.01,
            initial_state=np.array([1.0, 0.0])
        )

        # Should have only initial state, no steps
        assert len(t_arr) == 1
        assert len(x_arr) == 1
        assert len(u_arr) == 0

    def test_sim_time_negative_produces_no_steps(self):
        """Test sim_time<0 produces no integration steps."""
        class SimpleDynamics:
            def step(self, state, u, dt):
                return state

        class SimpleController:
            def __call__(self, t, x):
                return 0.0

        t_arr, x_arr, u_arr = run_simulation(
            controller=SimpleController(),
            dynamics_model=SimpleDynamics(),
            sim_time=-1.0,
            dt=0.01,
            initial_state=np.array([1.0, 0.0])
        )

        # Should have only initial state, no steps
        assert len(t_arr) == 1
        assert len(x_arr) == 1
        assert len(u_arr) == 0
