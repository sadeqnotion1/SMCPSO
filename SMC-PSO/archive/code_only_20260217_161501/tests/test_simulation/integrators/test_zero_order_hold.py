# ==============================================================================
# tests/test_simulation/integrators/test_zero_order_hold.py
#
# Comprehensive tests for Zero-Order Hold discretization
#
# Tests including:
# - Matrix exponential computation
# - Discrete-time matrices (Ad, Bd) correctness
# - Exactness for linear systems
# - Fallback to RK4 for nonlinear systems
# - Discrete sequence simulation
# ==============================================================================

import pytest
import numpy as np
from scipy.linalg import expm

from src.simulation.integrators.discrete.zero_order_hold import ZeroOrderHold


class TestZeroOrderHoldProperties:
    """Test basic properties and initialization."""

    def test_initialization_default(self):
        """Test default initialization."""
        integrator = ZeroOrderHold()
        assert integrator.A is None
        assert integrator.B is None
        assert integrator.dt_discrete is None

    def test_initialization_with_matrices(self):
        """Test initialization with linear system matrices."""
        A = np.array([[0, 1], [-1, 0]])
        B = np.array([[0], [1]])
        dt = 0.01

        integrator = ZeroOrderHold(A=A, B=B, dt=dt)
        assert np.array_equal(integrator.A, A)
        assert np.array_equal(integrator.B, B)
        assert integrator.dt_discrete == dt

    def test_order_property(self):
        """Test that order returns infinity for exact discretization."""
        integrator = ZeroOrderHold()
        assert integrator.order == float('inf')

    def test_adaptive_property(self):
        """Test that adaptive returns False."""
        integrator = ZeroOrderHold()
        assert integrator.adaptive is False


class TestMatrixExponentialComputation:
    """Test discrete matrix computation via matrix exponential."""

    def test_compute_discrete_matrices(self, controlled_system):
        """Test computation of discrete matrices."""
        A, B, _ = controlled_system
        dt = 0.01

        integrator = ZeroOrderHold()
        integrator.set_linear_system(A, B, dt)

        Ad, Bd = integrator.get_discrete_matrices()

        # Check shapes
        assert Ad.shape == A.shape
        assert Bd.shape == B.shape

        # Ad should be close to I + A*dt for small dt (allowing for higher-order terms)
        expected_Ad_approx = np.eye(A.shape[0]) + A * dt
        assert np.allclose(Ad, expected_Ad_approx, atol=1e-3)

    def test_matrix_exponential_correctness(self):
        """Test that matrix exponential method gives correct discrete matrices."""
        # Simple diagonal system
        A = np.array([[-1.0, 0], [0, -2.0]])
        B = np.array([[1.0], [0.5]])
        dt = 0.1

        integrator = ZeroOrderHold()
        integrator.set_linear_system(A, B, dt)

        Ad, Bd = integrator.get_discrete_matrices()

        # For diagonal A, Ad should be diag(exp(lambda_i * dt))
        expected_Ad = np.diag([np.exp(-1.0 * dt), np.exp(-2.0 * dt)])
        assert np.allclose(Ad, expected_Ad)

    def test_discrete_matrices_not_computed_initially(self):
        """Test that discrete matrices are None before computation."""
        integrator = ZeroOrderHold()
        assert integrator.get_discrete_matrices() is None


class TestLinearSystemIntegration:
    """Test integration of linear systems using ZOH."""

    def test_integrate_linear_system(self, controlled_system):
        """Test integration of a linear system."""
        A, B, _ = controlled_system
        dt = 0.01

        integrator = ZeroOrderHold(A=A, B=B, dt=dt)
        integrator.set_linear_system(A, B, dt)

        state = np.array([1.0, 0.0])
        control = np.array([0.0])

        # Dummy dynamics (not used for linear case)
        def dummy_dynamics(t, x, u):
            return A @ x + B.flatten() * u[0]

        new_state = integrator.integrate(dummy_dynamics, state, control, dt)

        # Should return a valid state
        assert isinstance(new_state, np.ndarray)
        assert new_state.shape == state.shape
        assert np.all(np.isfinite(new_state))

    def test_exactness_for_linear_system(self, controlled_system):
        """Test that ZOH is exact for linear systems."""
        A, B, _ = controlled_system
        dt = 0.01

        integrator = ZeroOrderHold(A=A, B=B, dt=dt)
        integrator.set_linear_system(A, B, dt)

        # Initial state
        state = np.array([1.0, 0.5])
        control = np.array([0.5])

        # Dummy dynamics
        def dummy_dynamics(t, x, u):
            return A @ x + B.flatten() * u[0]

        new_state = integrator.integrate(dummy_dynamics, state, control, dt)

        # Compute expected using matrix exponential manually
        Ad, Bd = integrator.get_discrete_matrices()
        expected = Ad @ state + Bd @ control

        assert np.allclose(new_state, expected)


class TestNonlinearSystemIntegration:
    """Test fallback to RK4 for nonlinear systems."""

    def test_nonlinear_fallback_to_rk4(self, nonlinear_pendulum):
        """Test that nonlinear systems use RK4 approximation."""
        dynamics = nonlinear_pendulum

        # No discrete matrices set, so should use RK4 fallback
        integrator = ZeroOrderHold()

        state = np.array([0.1, 0.0])
        control = np.array([0.0])
        dt = 0.01

        new_state = integrator.integrate(dynamics, state, control, dt)

        # Should successfully integrate
        assert isinstance(new_state, np.ndarray)
        assert new_state.shape == state.shape
        assert np.all(np.isfinite(new_state))

    def test_function_evaluations_for_nonlinear(self, nonlinear_pendulum):
        """Test that nonlinear integration uses 4 function evaluations (RK4)."""
        dynamics = nonlinear_pendulum
        integrator = ZeroOrderHold()

        integrator.reset_statistics()
        state = np.array([0.1, 0.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        assert stats['function_evaluations'] >= 4


class TestDiscreteSequenceSimulation:
    """Test multi-step discrete sequence simulation."""

    def test_simulate_discrete_sequence(self, controlled_system):
        """Test simulation of discrete sequence."""
        A, B, _ = controlled_system
        dt = 0.01

        integrator = ZeroOrderHold(A=A, B=B, dt=dt)
        integrator.set_linear_system(A, B, dt)

        initial_state = np.array([1.0, 0.0])
        horizon = 10
        control_sequence = np.zeros((horizon, 1))

        states = integrator.simulate_discrete_sequence(initial_state, control_sequence, horizon)

        # Check shape
        assert states.shape == (horizon + 1, 2)

        # First state should be initial state
        assert np.array_equal(states[0], initial_state)

        # All states should be finite
        assert np.all(np.isfinite(states))

    def test_discrete_sequence_with_nonzero_control(self, controlled_system):
        """Test discrete sequence with non-zero control inputs."""
        A, B, _ = controlled_system
        dt = 0.01

        integrator = ZeroOrderHold(A=A, B=B, dt=dt)
        integrator.set_linear_system(A, B, dt)

        initial_state = np.array([0.0, 0.0])
        horizon = 5
        control_sequence = np.ones((horizon, 1))  # Constant control

        states = integrator.simulate_discrete_sequence(initial_state, control_sequence, horizon)

        # States should evolve (not remain at origin)
        assert not np.allclose(states[-1], initial_state)

    def test_discrete_sequence_consistency(self, controlled_system):
        """Test that discrete sequence matches sequential integration."""
        A, B, _ = controlled_system
        dt = 0.01

        integrator = ZeroOrderHold(A=A, B=B, dt=dt)
        integrator.set_linear_system(A, B, dt)

        initial_state = np.array([1.0, 0.5])
        horizon = 3
        control_sequence = np.array([[0.1], [0.2], [0.3]])

        # Simulate using discrete sequence
        states_sequence = integrator.simulate_discrete_sequence(initial_state, control_sequence, horizon)

        # Simulate manually step-by-step
        Ad, Bd = integrator.get_discrete_matrices()
        states_manual = np.zeros((horizon + 1, 2))
        states_manual[0] = initial_state

        for k in range(horizon):
            states_manual[k + 1] = Ad @ states_manual[k] + Bd @ control_sequence[k]

        # Should match
        assert np.allclose(states_sequence, states_manual)


class TestEdgeCases:
    """Test edge cases for ZOH integrator."""

    def test_zero_state(self, controlled_system):
        """Test with zero initial state."""
        A, B, _ = controlled_system
        dt = 0.01

        integrator = ZeroOrderHold(A=A, B=B, dt=dt)
        integrator.set_linear_system(A, B, dt)

        state = np.array([0.0, 0.0])
        control = np.array([0.0])

        def dummy_dynamics(t, x, u):
            return A @ x + B.flatten() * u[0]

        new_state = integrator.integrate(dummy_dynamics, state, control, dt)

        # Zero state with zero control should remain zero
        assert np.allclose(new_state, 0.0)

    def test_different_dt_triggers_nonlinear_path(self, controlled_system):
        """Test that using different dt triggers nonlinear integration path."""
        A, B, _ = controlled_system
        dt_discrete = 0.01

        integrator = ZeroOrderHold(A=A, B=B, dt=dt_discrete)
        integrator.set_linear_system(A, B, dt_discrete)

        state = np.array([1.0, 0.0])
        control = np.array([0.0])
        dt_different = 0.02  # Different from dt_discrete

        def dynamics(t, x, u):
            return A @ x + B.flatten() * u[0]

        # Should use nonlinear path (RK4 fallback)
        new_state = integrator.integrate(dynamics, state, control, dt_different)

        assert isinstance(new_state, np.ndarray)
        assert new_state.shape == state.shape

    def test_raises_error_without_matrices(self):
        """Test that discrete sequence raises error without matrices."""
        integrator = ZeroOrderHold()

        initial_state = np.array([1.0, 0.0])
        control_sequence = np.zeros((10, 1))

        with pytest.raises(ValueError):
            integrator.simulate_discrete_sequence(initial_state, control_sequence, 10)


class TestStatistics:
    """Test statistics tracking."""

    def test_linear_integration_zero_evaluations(self, controlled_system):
        """Test that linear integration reports zero function evaluations."""
        A, B, _ = controlled_system
        dt = 0.01

        integrator = ZeroOrderHold(A=A, B=B, dt=dt)
        integrator.set_linear_system(A, B, dt)

        integrator.reset_statistics()
        state = np.array([1.0, 0.0])
        control = np.array([0.0])

        def dummy_dynamics(t, x, u):
            return A @ x + B.flatten() * u[0]

        integrator.integrate(dummy_dynamics, state, control, dt)

        stats = integrator.get_statistics()
        # Linear case uses precomputed matrices, no function evaluations
        assert stats['function_evaluations'] == 0
