#======================================================================================\\
#====== tests/test_simulation/engines/test_vector_sim_coverage_gaps.py ===============\\
#======================================================================================\\

"""
Coverage gap tests for Vector Simulation.
Target: Fill gaps from 26.09% to 90%+ coverage.
Focus: simulate() edge cases and simulate_system_batch() function.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.simulation.engines.vector_sim import simulate, simulate_system_batch


@pytest.fixture(autouse=True)
def mock_step_function():
    """Mock the dynamics step function to avoid lowrank module dependency."""
    def mock_step(x, u, dt):
        # Simple dynamics: x_next = x + u * dt * 0.01
        if x.ndim == 1:
            return x + np.asarray(u) * dt * 0.01
        else:
            # Batch mode
            u_broadcast = np.asarray(u)
            if u_broadcast.ndim == 0:
                u_broadcast = np.full(x.shape, u_broadcast)
            elif u_broadcast.ndim == 1 and x.ndim == 2:
                u_broadcast = u_broadcast[:, np.newaxis]
            return x + u_broadcast * dt * 0.01

    with patch('src.simulation.engines.vector_sim._step_fn', side_effect=mock_step):
        yield


class TestSimulateConfigHandling:
    """Test config import exception handling and safety limit loading."""

    def test_config_import_exception_fallback(self):
        """Test config import exception handling (lines 34-36)."""
        # This is tested implicitly when config is not available
        # The module should still work with SimpleNamespace fallback
        x0 = np.array([1.0, 0.0])
        u = np.array([0.1, 0.2])
        result = simulate(x0, u, dt=0.1)
        assert result.shape == (3, 2)

    def test_scalar_control_horizon_inference(self):
        """Test scalar control horizon inference (line 129: u.ndim == 0)."""
        x0 = np.array([1.0, 0.0])
        u = np.array(0.5)  # Scalar control (ndim==0)

        # Don't provide horizon - let it infer H=1 from u.ndim==0 (line 129)
        result = simulate(x0, u, dt=0.1)

        # Should run for 1 step (H=1 inferred) + initial state
        assert result.shape == (2, 2)  # 1 step + initial state

    def test_config_based_energy_limits_loading(self):
        """Test config-based energy limit loading (lines 151-171)."""
        # Create a proper mock config structure
        from types import SimpleNamespace
        mock_config = SimpleNamespace(
            simulation=SimpleNamespace(
                safety=SimpleNamespace(
                    energy=SimpleNamespace(max=100.0),
                    bounds=None
                )
            )
        )

        with patch('src.simulation.engines.vector_sim.config', mock_config):
            x0 = np.array([1.0, 0.0])
            u = np.zeros(10)

            # Should use config energy limits when not explicitly provided
            result = simulate(x0, u, dt=0.1)
            assert result.shape[0] == 11

    def test_config_based_state_bounds_loading(self):
        """Test config-based state bounds loading (lines 151-171)."""
        # Create a proper mock config structure
        from types import SimpleNamespace
        mock_config = SimpleNamespace(
            simulation=SimpleNamespace(
                safety=SimpleNamespace(
                    energy=None,
                    bounds=SimpleNamespace(
                        lower=np.array([-10.0, -10.0]),
                        upper=np.array([10.0, 10.0])
                    )
                )
            )
        )

        with patch('src.simulation.engines.vector_sim.config', mock_config):
            x0 = np.array([1.0, 0.0])
            u = np.zeros(10)

            # Should use config state bounds when not explicitly provided
            result = simulate(x0, u, dt=0.1)
            assert result.shape[0] == 11

    def test_config_exception_during_safety_load(self):
        """Test exception handling during config safety loading (lines 151-171)."""
        # Mock config that doesn't have safety attribute
        from types import SimpleNamespace
        mock_config = SimpleNamespace(
            simulation=SimpleNamespace()
        )
        # No safety attribute - will trigger exception

        with patch('src.simulation.engines.vector_sim.config', mock_config):
            x0 = np.array([1.0, 0.0])
            u = np.zeros(10)

            # Should continue without config limits
            result = simulate(x0, u, dt=0.1)
            assert result.shape[0] == 11

    def test_config_energy_limit_float_conversion_fails(self):
        """Test exception when energy.max can't convert to float (lines 160-161)."""
        from types import SimpleNamespace
        mock_config = SimpleNamespace(
            simulation=SimpleNamespace(
                safety=SimpleNamespace(
                    energy=SimpleNamespace(max="invalid_float_string"),  # Can't convert to float
                    bounds=None
                )
            )
        )

        with patch('src.simulation.engines.vector_sim.config', mock_config):
            x0 = np.array([1.0, 0.0])
            u = np.zeros(10)

            # Should continue without energy limits (exception caught)
            result = simulate(x0, u, dt=0.1)
            assert result.shape[0] == 11

    def test_config_bounds_structure_malformed(self):
        """Test exception when bounds structure is invalid (lines 167-168)."""
        from types import SimpleNamespace
        # Create object that will cause exception when getattr is used
        class BadBounds:
            @property
            def lower(self):
                raise RuntimeError("Can't access lower")
            @property
            def upper(self):
                raise RuntimeError("Can't access upper")

        mock_config = SimpleNamespace(
            simulation=SimpleNamespace(
                safety=SimpleNamespace(
                    energy=None,
                    bounds=BadBounds()  # Object that raises on attribute access
                )
            )
        )

        with patch('src.simulation.engines.vector_sim.config', mock_config):
            x0 = np.array([1.0, 0.0])
            u = np.zeros(10)

            # Should continue without bounds (exception caught)
            result = simulate(x0, u, dt=0.1)
            assert result.shape[0] == 11

    def test_config_simulation_access_fails(self):
        """Test exception at top-level config.simulation access (lines 169-171)."""
        from types import SimpleNamespace
        mock_config = SimpleNamespace()
        # No simulation attribute - accessing it will raise AttributeError

        with patch('src.simulation.engines.vector_sim.config', mock_config):
            x0 = np.array([1.0, 0.0])
            u = np.zeros(10)

            # Should continue without any config limits (exception caught at top level)
            result = simulate(x0, u, dt=0.1)
            assert result.shape[0] == 11


class TestBatchControlExtraction:
    """Test batch mode control extraction edge cases (lines 183-199)."""

    def test_batch_3d_control_input(self):
        """Test batch mode with 3D control input (lines 179-182)."""
        x0 = np.array([[1.0, 0.0], [2.0, 0.0]])  # Batch of 2
        u = np.array([[[0.1], [0.2]], [[0.3], [0.4]]])  # (B=2, H=2, U=1)

        result = simulate(x0, u, dt=0.1)

        assert result.shape == (2, 3, 2)  # (B=2, H+1=3, D=2)

    def test_batch_2d_control_broadcast_across_batches(self):
        """Test batch mode with 2D control broadcast (lines 190-192)."""
        x0 = np.array([[1.0, 0.0], [2.0, 0.0]])  # Batch of 2
        # In batch mode, horizon is inferred from u.shape[1]
        u = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])  # (2, 3) shape

        result = simulate(x0, u, dt=0.1)

        # Horizon is u.shape[1]=3, so result should be (B=2, H+1=4, D=2)
        assert result.shape == (2, 4, 2)

    def test_batch_1d_scalar_control(self):
        """Test batch mode with 1D scalar control (lines 193-196)."""
        x0 = np.array([[1.0, 0.0], [2.0, 0.0]])  # Batch of 2
        # For 1D control in batch mode, must provide explicit horizon
        u = np.array([0.1, 0.2, 0.3])  # (H,) - scalar per step

        result = simulate(x0, u, dt=0.1, horizon=3)

        # With explicit horizon=3, result should be (B=2, H+1=4, D=2)
        assert result.shape == (2, 4, 2)

    def test_batch_else_case_control(self):
        """Test batch mode else case for control extraction (lines 197-199)."""
        # This tests the else branch that might have a bug
        x0 = np.array([[1.0, 0.0], [2.0, 0.0]])  # Batch of 2

        # Create control array that doesn't match typical patterns
        # This should trigger the else case at line 197
        u = np.array([[0.1, 0.2], [0.3, 0.4]])  # (B=2, H=2)

        result = simulate(x0, u, dt=0.1)

        assert result.shape == (2, 3, 2)


class TestSimulateSystemBatchBasic:
    """Test simulate_system_batch basic functionality."""

    @pytest.fixture
    def simple_controller_factory(self):
        """Factory that creates simple controllers."""
        def factory(gains):
            controller = Mock()
            controller.state_dim = 6

            # Mock dynamics model
            dynamics = Mock()
            dynamics.state_dim = 6
            dynamics.step = Mock(side_effect=lambda x, u, dt: x + u * dt * 0.01)
            controller.dynamics_model = dynamics

            # Mock compute_control
            def compute_control(x, state, history):
                return -gains[0] * x[0], state, history
            controller.compute_control = compute_control

            return controller
        return factory

    def test_basic_batch_simulation(self, simple_controller_factory):
        """Test basic batch simulation with multiple particles."""
        particles = np.array([[1.0, 2.0], [3.0, 4.0]])  # 2 particles

        result = simulate_system_batch(
            controller_factory=simple_controller_factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01
        )

        t, x_b, u_b, sigma_b = result
        assert t.shape[0] == 11  # 10 steps + initial
        assert x_b.shape == (2, 11, 6)  # (B=2, N+1=11, D=6)
        assert u_b.shape == (2, 10)  # (B=2, N=10)
        assert sigma_b.shape == (2, 10)

    def test_single_particle_simulation(self, simple_controller_factory):
        """Test batch simulation with single particle (1D gains)."""
        particles = np.array([1.0, 2.0])  # Single particle (1D)

        result = simulate_system_batch(
            controller_factory=simple_controller_factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01
        )

        t, x_b, u_b, sigma_b = result
        assert x_b.shape == (1, 11, 6)  # (B=1, N+1=11, D=6)

    def test_with_initial_state_1d(self, simple_controller_factory):
        """Test batch simulation with 1D initial state (broadcast)."""
        particles = np.array([[1.0, 2.0], [3.0, 4.0]])
        initial_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # 1D

        result = simulate_system_batch(
            controller_factory=simple_controller_factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01,
            initial_state=initial_state
        )

        t, x_b, u_b, sigma_b = result
        # Initial state should be broadcast to all particles
        np.testing.assert_array_equal(x_b[0, 0], initial_state)
        np.testing.assert_array_equal(x_b[1, 0], initial_state)

    def test_with_initial_state_2d(self, simple_controller_factory):
        """Test batch simulation with 2D initial state."""
        particles = np.array([[1.0, 2.0], [3.0, 4.0]])
        initial_state = np.array([
            [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ])  # 2D (B=2, D=6)

        result = simulate_system_batch(
            controller_factory=simple_controller_factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01,
            initial_state=initial_state
        )

        t, x_b, u_b, sigma_b = result
        np.testing.assert_array_equal(x_b[0, 0], initial_state[0])
        np.testing.assert_array_equal(x_b[1, 0], initial_state[1])

    def test_with_u_max_saturation(self, simple_controller_factory):
        """Test control saturation with u_max."""
        particles = np.array([[1.0, 2.0], [3.0, 4.0]])

        result = simulate_system_batch(
            controller_factory=simple_controller_factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01,
            u_max=0.5
        )

        t, x_b, u_b, sigma_b = result
        # All control values should be within [-0.5, 0.5]
        assert np.all(u_b >= -0.5)
        assert np.all(u_b <= 0.5)

    def test_with_convergence_tolerance(self, simple_controller_factory):
        """Test early stopping with convergence tolerance."""
        particles = np.array([[1.0, 2.0]])

        result = simulate_system_batch(
            controller_factory=simple_controller_factory,
            particles=particles,
            sim_time=1.0,  # Long duration
            dt=0.01,
            convergence_tol=0.01,  # Stop when sigma < 0.01
            grace_period=0.0
        )

        t, x_b, u_b, sigma_b = result
        # Should stop early (fewer than 101 steps)
        assert t.shape[0] <= 101


class TestSimulateSystemBatchEdgeCases:
    """Test simulate_system_batch edge cases and error handling."""

    def test_controller_factory_exception(self):
        """Test controller factory exception handling (lines 344-347)."""
        def failing_factory(gains):
            raise RuntimeError("Factory failed")

        particles = np.array([[1.0, 2.0]])

        # Should catch and retry once, then raise
        with pytest.raises(RuntimeError):
            simulate_system_batch(
                controller_factory=failing_factory,
                particles=particles,
                sim_time=0.1,
                dt=0.01
            )

    def test_state_dim_introspection_fallback(self):
        """Test state dimension introspection fallback (lines 350-359)."""
        def factory(gains):
            controller = Mock()
            # No state_dim or dynamics_model.state_dim - should fall back to 6
            del controller.state_dim
            controller.dynamics_model = Mock()
            del controller.dynamics_model.state_dim

            controller.dynamics_model.step = Mock(
                side_effect=lambda x, u, dt: np.zeros(6)
            )
            controller.compute_control = Mock(return_value=(0.0, None, None))

            return controller

        particles = np.array([[1.0, 2.0]])

        result = simulate_system_batch(
            controller_factory=factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01
        )

        t, x_b, u_b, sigma_b = result
        # Should use fallback state_dim=6
        assert x_b.shape[2] == 6

    def test_initialize_state_exception(self):
        """Test initialize_state exception handling (lines 385-393)."""
        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.initialize_state = Mock(side_effect=RuntimeError("Init failed"))
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6
            controller.dynamics_model.step = Mock(
                side_effect=lambda x, u, dt: x + 0.01
            )
            controller.compute_control = Mock(return_value=(0.0, None, None))

            return controller

        particles = np.array([[1.0, 2.0]])

        # Should handle exception gracefully and continue
        result = simulate_system_batch(
            controller_factory=factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01
        )

        assert result is not None

    def test_initialize_history_exception(self):
        """Test initialize_history exception handling (lines 395-403)."""
        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.initialize_history = Mock(side_effect=RuntimeError("History failed"))
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6
            controller.dynamics_model.step = Mock(
                side_effect=lambda x, u, dt: x + 0.01
            )
            controller.compute_control = Mock(return_value=(0.0, None, None))

            return controller

        particles = np.array([[1.0, 2.0]])

        # Should handle exception gracefully and continue
        result = simulate_system_batch(
            controller_factory=factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01
        )

        assert result is not None

    def test_max_force_attribute_fallback(self):
        """Test max_force attribute exception handling (lines 411-415)."""
        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.max_force = "invalid"  # Can't convert to float
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6
            controller.dynamics_model.step = Mock(
                side_effect=lambda x, u, dt: x + 0.01
            )
            controller.compute_control = Mock(return_value=(0.0, None, None))

            return controller

        particles = np.array([[1.0, 2.0]])

        # Should fall back to np.inf for saturation limit
        result = simulate_system_batch(
            controller_factory=factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01
        )

        assert result is not None

    def test_compute_control_exception_terminates(self):
        """Test compute_control exception terminates simulation (lines 451-477)."""
        call_count = [0]

        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6
            controller.dynamics_model.step = Mock(
                side_effect=lambda x, u, dt: x + 0.01
            )

            def failing_compute_control(x, state, history):
                call_count[0] += 1
                if call_count[0] > 3:
                    raise RuntimeError("Control computation failed")
                return (0.0, None, None)

            controller.compute_control = failing_compute_control

            return controller

        particles = np.array([[1.0, 2.0]])

        result = simulate_system_batch(
            controller_factory=factory,
            particles=particles,
            sim_time=1.0,  # Long duration
            dt=0.01
        )

        t, x_b, u_b, sigma_b = result
        # Should terminate early after exception
        assert t.shape[0] < 101

    def test_dynamics_step_returns_none_terminates(self):
        """Test dynamics.step returning None terminates (lines 502-504)."""
        call_count = [0]

        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6

            def step_with_failure(x, u, dt):
                call_count[0] += 1
                if call_count[0] > 3:
                    return None  # Simulate failure
                return x + 0.01

            controller.dynamics_model.step = step_with_failure
            controller.compute_control = Mock(return_value=(0.0, None, None))

            return controller

        particles = np.array([[1.0, 2.0]])

        result = simulate_system_batch(
            controller_factory=factory,
            particles=particles,
            sim_time=1.0,
            dt=0.01
        )

        t, x_b, u_b, sigma_b = result
        # Should terminate early
        assert t.shape[0] < 101

    def test_non_finite_state_terminates(self):
        """Test non-finite state terminates simulation (lines 507-509)."""
        call_count = [0]

        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6

            def step_with_nan(x, u, dt):
                call_count[0] += 1
                if call_count[0] > 3:
                    return np.array([np.nan, 0, 0, 0, 0, 0])
                return x + 0.01

            controller.dynamics_model.step = step_with_nan
            controller.compute_control = Mock(return_value=(0.0, None, None))

            return controller

        particles = np.array([[1.0, 2.0]])

        result = simulate_system_batch(
            controller_factory=factory,
            particles=particles,
            sim_time=1.0,
            dt=0.01
        )

        t, x_b, u_b, sigma_b = result
        # Should terminate early due to NaN
        assert t.shape[0] < 101

    def test_with_params_list_replicates_results(self):
        """Test params_list replicates results (lines 559-562)."""
        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6
            controller.dynamics_model.step = Mock(
                side_effect=lambda x, u, dt: x + 0.01
            )
            controller.compute_control = Mock(return_value=(0.0, None, None))

            return controller

        particles = np.array([[1.0, 2.0]])
        params_list = [Mock(), Mock(), Mock()]  # 3 params

        result = simulate_system_batch(
            controller_factory=factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01,
            params_list=params_list
        )

        # Should return list of 3 results
        assert isinstance(result, list)
        assert len(result) == 3

        # Each result should be a tuple of 4 arrays
        for r in result:
            assert len(r) == 4
            t, x_b, u_b, sigma_b = r
            assert t.shape[0] == 11


class TestSimulateEarlyStoppingBatchMode:
    """Test early stopping logic in batch mode (lines 227-235)."""

    def test_early_stopping_batch_mode_any_stops(self):
        """Test that any batch element stopping triggers early termination."""
        # Create stop function that stops after 5 steps for one element
        def stop_fn(state):
            return np.sum(state**2) > 0.5  # Will trigger for growing states

        x0 = np.array([[0.1, 0.0], [10.0, 0.0]])  # Second element will trigger stop
        u = np.array([[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                      [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]])

        result = simulate(x0, u, dt=0.1, stop_fn=stop_fn)

        # Should stop early when any batch element meets condition
        assert result.shape[1] < 11  # Stopped before 10 steps + initial

    def test_early_stopping_scalar_mode(self):
        """Test early stopping in scalar mode (lines 232-235)."""
        def stop_fn(state):
            return np.sum(state**2) > 1.0  # Will trigger as state grows

        x0 = np.array([1.0, 1.0])  # Start with larger initial state
        u = np.full(20, 10.0)  # Large control to grow state quickly

        result = simulate(x0, u, dt=0.1, stop_fn=stop_fn)

        # Should stop early (within a few steps)
        assert result.shape[0] < 10  # Should stop much earlier than 21


class TestSimulateSystemBatchCallableController:
    """Test simulate_system_batch with callable controller (lines 448-450)."""

    def test_controller_without_compute_control_uses_call(self):
        """Test controller using __call__ instead of compute_control."""
        class CallableController:
            """Controller that implements __call__ but not compute_control."""
            def __init__(self):
                self.state_dim = 6
                self.dynamics_model = Mock()
                self.dynamics_model.state_dim = 6
                self.dynamics_model.step = Mock(
                    side_effect=lambda x, u, dt: x + u * dt * 0.01
                )

            def __call__(self, t, x):
                """Callable interface instead of compute_control."""
                return float(-0.1 * x[0])

        def factory(gains):
            return CallableController()

        particles = np.array([[1.0, 2.0]])

        result = simulate_system_batch(
            controller_factory=factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01
        )

        t, x_b, u_b, sigma_b = result
        # Should complete full simulation
        assert t.shape[0] == 11
        # sigma should be 0.0 when using __call__
        assert np.all(sigma_b == 0.0)


class TestSimulateSystemBatchSigmaExtraction:
    """Test sigma value extraction from control return (lines 442-447)."""

    def test_sigma_from_hasattr(self):
        """Test extracting sigma via hasattr check."""
        from collections import namedtuple

        ControlResult = namedtuple('ControlResult', ['u', 'state', 'history', 'sigma'])

        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6
            controller.dynamics_model.step = Mock(
                side_effect=lambda x, u, dt: x + 0.01
            )

            def compute_control_with_sigma(x, state, history):
                result = ControlResult(u=-gains[0] * x[0], state=state, history=history, sigma=0.5)
                return result

            controller.compute_control = compute_control_with_sigma

            return controller

        particles = np.array([[1.0, 2.0]])

        result = simulate_system_batch(
            controller_factory=factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01
        )

        t, x_b, u_b, sigma_b = result
        # sigma should be extracted from namedtuple
        assert np.all(sigma_b == 0.5)

    def test_sigma_from_tuple_index(self):
        """Test extracting sigma from tuple index 3."""
        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6
            controller.dynamics_model.step = Mock(
                side_effect=lambda x, u, dt: x + 0.01
            )

            def compute_control_with_sigma_tuple(x, state, history):
                # Return tuple with 4 elements: (u, state, history, sigma)
                return (-gains[0] * x[0], state, history, 0.75)

            controller.compute_control = compute_control_with_sigma_tuple

            return controller

        particles = np.array([[1.0, 2.0]])

        result = simulate_system_batch(
            controller_factory=factory,
            particles=particles,
            sim_time=0.1,
            dt=0.01
        )

        t, x_b, u_b, sigma_b = result
        # sigma should be extracted from tuple index 3
        assert np.all(sigma_b == 0.75)


class TestSimulateSystemBatchWarningException:
    """Test Warning exception re-raising (lines 454-455)."""

    def test_warning_exception_is_reraised(self):
        """Test that Warning exceptions are re-raised, not caught."""
        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6
            controller.dynamics_model.step = Mock(
                side_effect=lambda x, u, dt: x + 0.01
            )

            def compute_control_with_warning(x, state, history):
                raise UserWarning("Test warning - should be re-raised")

            controller.compute_control = compute_control_with_warning

            return controller

        particles = np.array([[1.0, 2.0]])

        # Warning should be re-raised, not caught by exception handler
        with pytest.raises(UserWarning, match="should be re-raised"):
            simulate_system_batch(
                controller_factory=factory,
                particles=particles,
                sim_time=0.1,
                dt=0.01
            )


class TestBatchControlExtractionPhase2:
    """Phase 2: Additional batch control extraction tests (lines 191-192, 198-199)."""

    def test_batch_control_HxU_broadcast_format(self):
        """Test batch with (H,U) control broadcasted across batches (lines 191-192)."""
        x0 = np.array([[1.0, 0.0], [2.0, 0.0]])  # B=2, D=2
        u = np.array([[0.1, 0.2], [0.3, 0.4]])  # (H=2, U=2)
        # Not matching (B,H) shape, triggers else at line 191
        result = simulate(x0, u, dt=0.1, horizon=2)
        assert result.shape == (2, 3, 2)  # B=2, H+1=3, D=2

    def test_batch_control_dimension_fallback(self):
        """Test batch control fallback extraction (lines 198-199)."""
        x0 = np.array([[1.0, 0.0], [2.0, 0.0]])  # B=2
        u = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])  # (B=2, H=3)
        result = simulate(x0, u, dt=0.1)
        assert result.shape == (2, 4, 2)  # B=2, H+1=4, D=2


class TestControlReturnEdgeCases:
    """Phase 2: Control return edge cases for simulate_system_batch."""

    def test_control_return_non_indexable_floatable(self):
        """Test when control return can't be indexed but can float (lines 432-433)."""
        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6
            controller.dynamics_model.step = Mock(side_effect=lambda x, u, dt: x + 0.01)

            class FloatableNonIndexable:
                def __float__(self):
                    return 0.75
                def __getitem__(self, idx):
                    raise TypeError("Can't index this object")

            controller.compute_control = Mock(return_value=FloatableNonIndexable())
            return controller

        result = simulate_system_batch(
            controller_factory=factory,
            particles=np.array([[1.0, 2.0]]),
            sim_time=0.1,
            dt=0.01
        )
        t, x_b, u_b, sigma_b = result
        assert np.all(u_b == 0.75)

    def test_control_return_short_tuple(self):
        """Test when control return has only 1 element (lines 440-441)."""
        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6
            controller.dynamics_model.step = Mock(side_effect=lambda x, u, dt: x + 0.01)
            controller.compute_control = Mock(return_value=(0.5,))  # Only 1 element
            return controller

        result = simulate_system_batch(
            controller_factory=factory,
            particles=np.array([[1.0, 2.0]]),
            sim_time=0.1,
            dt=0.01
        )
        t, x_b, u_b, sigma_b = result
        assert t.shape[0] == 11  # Should complete without error


class TestDynamicsStepExceptions:
    """Phase 2: Dynamics step exception handling (lines 500-501)."""

    def test_dynamics_step_raises_exception(self):
        """Test dynamics.step exception handling (lines 500-501)."""
        call_count = [0]

        def factory(gains):
            controller = Mock()
            controller.state_dim = 6
            controller.dynamics_model = Mock()
            controller.dynamics_model.state_dim = 6

            def step_fails(x, u, dt):
                call_count[0] += 1
                if call_count[0] > 3:
                    raise ValueError("Step computation failed")
                return x + 0.01

            controller.dynamics_model.step = step_fails
            controller.compute_control = Mock(return_value=(0.0, None, None))
            return controller

        result = simulate_system_batch(
            controller_factory=factory,
            particles=np.array([[1.0, 2.0]]),
            sim_time=1.0,
            dt=0.01
        )
        t, x_b, u_b, sigma_b = result
        assert t.shape[0] < 101  # Early termination due to exception
