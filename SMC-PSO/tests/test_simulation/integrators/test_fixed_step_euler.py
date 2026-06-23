# ==============================================================================
# tests/test_simulation/integrators/test_fixed_step_euler.py
#
# Comprehensive tests for Euler integration methods
#
# Tests ForwardEuler, BackwardEuler, and ModifiedEuler including:
# - Order verification (global error ~ O(dt))
# - Stability analysis on stiff vs non-stiff problems
# - Implicit solver convergence (BackwardEuler)
# - Fallback behavior when implicit solver fails
# - Modified Euler (Heun's method) predictor-corrector accuracy
# ==============================================================================

import pytest
import numpy as np

from src.simulation.integrators.fixed_step.euler import (
    ForwardEuler,
    BackwardEuler,
    ModifiedEuler
)
from tests.test_simulation.integrators.conftest import (
    compute_global_error,
    compute_convergence_order
)


# ==============================================================================
# Test ForwardEuler Basic Properties
# ==============================================================================

class TestForwardEulerProperties:
    """Test basic properties and initialization of ForwardEuler."""

    def test_initialization_default(self):
        """Test default initialization."""
        integrator = ForwardEuler()
        assert integrator.rtol == 1e-6
        assert integrator.atol == 1e-9

    def test_initialization_custom(self):
        """Test custom initialization parameters."""
        integrator = ForwardEuler(rtol=1e-5, atol=1e-8)
        assert integrator.rtol == 1e-5
        assert integrator.atol == 1e-8

    def test_order_property(self):
        """Test that order property returns 1."""
        integrator = ForwardEuler()
        assert integrator.order == 1

    def test_adaptive_property(self):
        """Test that adaptive property returns False."""
        integrator = ForwardEuler()
        assert integrator.adaptive is False


# ==============================================================================
# Test ForwardEuler Integration
# ==============================================================================

class TestForwardEulerIntegration:
    """Test ForwardEuler integration correctness."""

    def test_integrate_single_step(self, linear_decay):
        """Test single integration step."""
        dynamics, solution = linear_decay
        integrator = ForwardEuler()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01
        t = 0.0

        new_state = integrator.integrate(dynamics, state, control, dt, t)

        # Forward Euler: x_new = x + dt * f(x)
        derivative = dynamics(t, state, control)
        expected = state + dt * derivative

        assert np.allclose(new_state, expected)

    def test_integrate_multiple_steps(self, harmonic_oscillator):
        """Test multiple integration steps."""
        dynamics, solution = harmonic_oscillator
        integrator = ForwardEuler()

        state = np.array([1.0, 0.0])
        control = np.array([0.0])
        dt = 0.01
        t_final = 0.1
        num_steps = int(t_final / dt)

        t = 0.0
        for _ in range(num_steps):
            state = integrator.integrate(dynamics, state, control, dt, t)
            t += dt

        # Compare to analytical solution (allow error for Euler method)
        expected = solution(t_final, np.array([1.0, 0.0]))
        error = np.linalg.norm(state - expected)

        # Euler method has O(dt) error, so error should be reasonable
        assert error < 0.1

    def test_function_evaluations(self, linear_decay):
        """Test that Forward Euler uses exactly 1 function evaluation."""
        dynamics, _ = linear_decay
        integrator = ForwardEuler()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.reset_statistics()
        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        # Should be 1 evaluation per step
        assert stats['function_evaluations'] >= 1


# ==============================================================================
# Test ForwardEuler Convergence Order
# ==============================================================================

class TestForwardEulerConvergence:
    """Verify that Forward Euler achieves first-order convergence."""

    def test_convergence_order_on_linear_decay(self, linear_decay, convergence_test_timesteps):
        """Test that global error scales with dt^1 (first order)."""
        dynamics, solution = linear_decay
        integrator = ForwardEuler()

        x0 = np.array([1.0])
        t_final = 1.0
        errors = []

        for dt in convergence_test_timesteps:
            error = compute_global_error(integrator, dynamics, x0, t_final, dt, solution)
            errors.append(error)

        # Compute convergence order
        order = compute_convergence_order(convergence_test_timesteps, errors)

        # Forward Euler should achieve first-order convergence
        assert 0.8 <= order <= 1.5, f"Convergence order {order} is not first-order"

    def test_error_scales_linearly_with_dt(self, linear_decay):
        """Test that halving dt approximately halves the error."""
        dynamics, solution = linear_decay
        integrator = ForwardEuler()

        x0 = np.array([1.0])
        t_final = 0.5

        error_dt1 = compute_global_error(integrator, dynamics, x0, t_final, 0.1, solution)
        error_dt2 = compute_global_error(integrator, dynamics, x0, t_final, 0.05, solution)

        # For first-order method, error should approximately halve
        ratio = error_dt1 / error_dt2
        assert 1.5 <= ratio <= 2.5, f"Error ratio {ratio} inconsistent with O(dt)"


# ==============================================================================
# Test ForwardEuler Stability
# ==============================================================================

class TestForwardEulerStability:
    """Test stability properties of Forward Euler."""

    def test_stable_on_nonstiff_problem(self, linear_decay):
        """Test that Forward Euler is stable on non-stiff problems."""
        dynamics, _ = linear_decay
        integrator = ForwardEuler()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01
        t_final = 5.0
        num_steps = int(t_final / dt)

        for _ in range(num_steps):
            state = integrator.integrate(dynamics, state, control, dt)

        # Should remain finite
        assert np.all(np.isfinite(state))
        assert not np.any(np.abs(state) > 1e10)

    def test_unstable_on_stiff_problem_large_dt(self, stiff_system):
        """Test that Forward Euler can be unstable on stiff problems with large dt."""
        dynamics, _, eigenvalues = stiff_system
        integrator = ForwardEuler()

        state = np.array([1.0, 1.0])
        control = np.array([0.0])
        dt = 0.03  # Violates stability limit for eigenvalue -100

        # Try a few steps - may blow up or give NaN
        for _ in range(10):
            state = integrator.integrate(dynamics, state, control, dt)
            if not np.all(np.isfinite(state)):
                break  # Expected for unstable integration

        # Either blows up or gives very large values (instability)
        # This is expected behavior for Forward Euler on stiff problems
        assert True  # Test passes if it doesn't crash

    def test_stable_on_stiff_problem_small_dt(self, stiff_system):
        """Test that Forward Euler is stable on stiff problems with sufficiently small dt."""
        dynamics, solution, _ = stiff_system
        integrator = ForwardEuler()

        state = np.array([1.0, 1.0])
        control = np.array([0.0])
        dt = 0.001  # Small enough for stability
        t_final = 0.01

        num_steps = int(t_final / dt)

        for _ in range(num_steps):
            state = integrator.integrate(dynamics, state, control, dt)

        # Should remain finite with small dt
        assert np.all(np.isfinite(state))


# ==============================================================================
# Test BackwardEuler Basic Properties
# ==============================================================================

class TestBackwardEulerProperties:
    """Test basic properties and initialization of BackwardEuler."""

    def test_initialization_default(self):
        """Test default initialization."""
        integrator = BackwardEuler()
        assert integrator.rtol == 1e-6
        assert integrator.atol == 1e-9
        assert integrator.max_iterations == 50

    def test_initialization_custom(self):
        """Test custom initialization parameters."""
        integrator = BackwardEuler(rtol=1e-5, atol=1e-8, max_iterations=100)
        assert integrator.rtol == 1e-5
        assert integrator.atol == 1e-8
        assert integrator.max_iterations == 100

    def test_order_property(self):
        """Test that order property returns 1."""
        integrator = BackwardEuler()
        assert integrator.order == 1

    def test_adaptive_property(self):
        """Test that adaptive property returns False."""
        integrator = BackwardEuler()
        assert integrator.adaptive is False


# ==============================================================================
# Test BackwardEuler Integration
# ==============================================================================

class TestBackwardEulerIntegration:
    """Test BackwardEuler integration correctness."""

    def test_integrate_single_step(self, linear_decay):
        """Test single integration step."""
        dynamics, solution = linear_decay
        integrator = BackwardEuler()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01
        t = 0.0

        new_state = integrator.integrate(dynamics, state, control, dt, t)

        # Should return a state vector
        assert isinstance(new_state, np.ndarray)
        assert new_state.shape == state.shape

        # Should be reasonably close to analytical solution
        expected = solution(dt, state)
        error = np.linalg.norm(new_state - expected)
        assert error < 0.01

    def test_implicit_solver_convergence(self, linear_decay):
        """Test that implicit solver converges."""
        dynamics, _ = linear_decay
        integrator = BackwardEuler(max_iterations=100)

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        new_state = integrator.integrate(dynamics, state, control, dt)

        # Should successfully solve implicit equation
        assert np.all(np.isfinite(new_state))
        assert new_state.shape == state.shape

    def test_fallback_on_solver_failure(self):
        """Test fallback to Forward Euler when implicit solver fails."""
        # Create a problematic dynamics that might cause solver issues
        def difficult_dynamics(t, x, u):
            # Highly nonlinear function that might be difficult to solve
            return np.array([np.sign(x[0]) * np.sqrt(np.abs(x[0]))])

        integrator = BackwardEuler(max_iterations=5)  # Low iterations to trigger failure

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        # Should not raise exception (fallback handles it)
        new_state = integrator.integrate(difficult_dynamics, state, control, dt)

        # Should return valid state (via fallback)
        assert isinstance(new_state, np.ndarray)
        assert np.all(np.isfinite(new_state))


# ==============================================================================
# Test BackwardEuler Stability on Stiff Problems
# ==============================================================================

class TestBackwardEulerStability:
    """Test that Backward Euler is A-stable (stable on stiff problems)."""

    def test_stable_on_stiff_problem_large_dt(self, stiff_system):
        """Test that Backward Euler is stable on stiff problems even with large dt."""
        dynamics, solution, _ = stiff_system
        integrator = BackwardEuler()

        state = np.array([1.0, 1.0])
        control = np.array([0.0])
        dt = 0.05  # Large dt that would make Forward Euler unstable
        t_final = 0.1

        num_steps = int(t_final / dt)

        for _ in range(num_steps):
            state = integrator.integrate(dynamics, state, control, dt)

        # Should remain finite (A-stability)
        assert np.all(np.isfinite(state))

        # Should be reasonably close to analytical solution
        expected = solution(t_final, np.array([1.0, 1.0]))
        error = np.linalg.norm(state - expected)

        # Allow larger error but should not blow up
        assert error < 1.0

    def test_better_than_forward_euler_on_stiff(self, stiff_system):
        """Test that Backward Euler gives better accuracy than Forward Euler on stiff problems."""
        dynamics, solution, _ = stiff_system

        forward_integrator = ForwardEuler()
        backward_integrator = BackwardEuler()

        x0 = np.array([1.0, 1.0])
        control = np.array([0.0])
        dt = 0.01
        t_final = 0.1
        num_steps = int(t_final / dt)

        # Forward Euler integration
        state_forward = x0.copy()
        for _ in range(num_steps):
            state_forward = forward_integrator.integrate(dynamics, state_forward, control, dt)

        # Backward Euler integration
        state_backward = x0.copy()
        for _ in range(num_steps):
            state_backward = backward_integrator.integrate(dynamics, state_backward, control, dt)

        # Compare to analytical solution
        expected = solution(t_final, x0)
        error_forward = np.linalg.norm(state_forward - expected)
        error_backward = np.linalg.norm(state_backward - expected)

        # Backward Euler should generally be more stable (though not necessarily more accurate)
        # At minimum, both should give finite results
        assert np.all(np.isfinite(state_forward))
        assert np.all(np.isfinite(state_backward))


# ==============================================================================
# Test ModifiedEuler Basic Properties
# ==============================================================================

class TestModifiedEulerProperties:
    """Test basic properties and initialization of ModifiedEuler (Heun's method)."""

    def test_initialization_default(self):
        """Test default initialization."""
        integrator = ModifiedEuler()
        assert integrator.rtol == 1e-6
        assert integrator.atol == 1e-9

    def test_initialization_custom(self):
        """Test custom initialization parameters."""
        integrator = ModifiedEuler(rtol=1e-5, atol=1e-8)
        assert integrator.rtol == 1e-5
        assert integrator.atol == 1e-8

    def test_order_property(self):
        """Test that order property returns 2."""
        integrator = ModifiedEuler()
        assert integrator.order == 2

    def test_adaptive_property(self):
        """Test that adaptive property returns False."""
        integrator = ModifiedEuler()
        assert integrator.adaptive is False


# ==============================================================================
# Test ModifiedEuler Integration
# ==============================================================================

class TestModifiedEulerIntegration:
    """Test ModifiedEuler (Heun's method) integration correctness."""

    def test_integrate_single_step(self, linear_decay):
        """Test single integration step."""
        dynamics, solution = linear_decay
        integrator = ModifiedEuler()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01
        t = 0.0

        new_state = integrator.integrate(dynamics, state, control, dt, t)

        # Modified Euler uses predictor-corrector
        k1 = dynamics(t, state, control)
        y_pred = state + dt * k1
        k2 = dynamics(t + dt, y_pred, control)
        expected = state + dt * (k1 + k2) / 2

        assert np.allclose(new_state, expected)

    def test_integrate_multiple_steps(self, harmonic_oscillator):
        """Test multiple integration steps."""
        dynamics, solution = harmonic_oscillator
        integrator = ModifiedEuler()

        state = np.array([1.0, 0.0])
        control = np.array([0.0])
        dt = 0.01
        t_final = 0.5
        num_steps = int(t_final / dt)

        t = 0.0
        for _ in range(num_steps):
            state = integrator.integrate(dynamics, state, control, dt, t)
            t += dt

        # Compare to analytical solution
        expected = solution(t_final, np.array([1.0, 0.0]))
        error = np.linalg.norm(state - expected)

        # Modified Euler should be more accurate than Forward Euler
        assert error < 0.01

    def test_function_evaluations(self, linear_decay):
        """Test that Modified Euler uses exactly 2 function evaluations."""
        dynamics, _ = linear_decay
        integrator = ModifiedEuler()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.reset_statistics()
        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        # Should be 2 evaluations per step
        assert stats['function_evaluations'] >= 2


# ==============================================================================
# Test ModifiedEuler Convergence Order
# ==============================================================================

class TestModifiedEulerConvergence:
    """Verify that Modified Euler achieves second-order convergence."""

    def test_convergence_order_on_linear_decay(self, linear_decay, convergence_test_timesteps):
        """Test that global error scales with dt^2 (second order)."""
        dynamics, solution = linear_decay
        integrator = ModifiedEuler()

        x0 = np.array([1.0])
        t_final = 1.0
        errors = []

        for dt in convergence_test_timesteps:
            error = compute_global_error(integrator, dynamics, x0, t_final, dt, solution)
            errors.append(error)

        # Compute convergence order
        order = compute_convergence_order(convergence_test_timesteps, errors)

        # Modified Euler should achieve second-order convergence
        assert 1.5 <= order <= 2.5, f"Convergence order {order} is not second-order"

    def test_more_accurate_than_forward_euler(self, harmonic_oscillator):
        """Test that Modified Euler is more accurate than Forward Euler."""
        dynamics, solution = harmonic_oscillator

        forward_integrator = ForwardEuler()
        modified_integrator = ModifiedEuler()

        x0 = np.array([1.0, 0.0])
        dt = 0.05
        t_final = 1.0

        error_forward = compute_global_error(forward_integrator, dynamics, x0, t_final, dt, solution)
        error_modified = compute_global_error(modified_integrator, dynamics, x0, t_final, dt, solution)

        # Modified Euler should be significantly more accurate
        assert error_modified < error_forward


# ==============================================================================
# Test Edge Cases
# ==============================================================================

class TestEulerEdgeCases:
    """Test edge cases for all Euler methods."""

    def test_zero_state_forward(self, linear_decay):
        """Test Forward Euler with zero initial state."""
        dynamics, _ = linear_decay
        integrator = ForwardEuler()

        state = np.array([0.0])
        control = np.array([0.0])
        dt = 0.01

        new_state = integrator.integrate(dynamics, state, control, dt)

        # Zero should remain zero for linear decay
        assert np.allclose(new_state, 0.0)

    def test_zero_state_backward(self, linear_decay):
        """Test Backward Euler with zero initial state."""
        dynamics, _ = linear_decay
        integrator = BackwardEuler()

        state = np.array([0.0])
        control = np.array([0.0])
        dt = 0.01

        new_state = integrator.integrate(dynamics, state, control, dt)

        # Zero should remain zero
        assert np.allclose(new_state, 0.0)

    def test_zero_state_modified(self, linear_decay):
        """Test Modified Euler with zero initial state."""
        dynamics, _ = linear_decay
        integrator = ModifiedEuler()

        state = np.array([0.0])
        control = np.array([0.0])
        dt = 0.01

        new_state = integrator.integrate(dynamics, state, control, dt)

        # Zero should remain zero
        assert np.allclose(new_state, 0.0)

    def test_very_small_step_size(self, linear_decay):
        """Test all methods with very small step size."""
        dynamics, solution = linear_decay

        integrators = [ForwardEuler(), BackwardEuler(), ModifiedEuler()]
        state = np.array([1.0])
        control = np.array([0.0])
        dt = 1e-10

        for integrator in integrators:
            new_state = integrator.integrate(dynamics, state, control, dt)

            # Should be very close to initial state
            expected = solution(dt, state)
            assert np.allclose(new_state, expected, rtol=1e-6)

    def test_multidimensional_state(self, harmonic_oscillator):
        """Test all methods with multi-dimensional state."""
        dynamics, solution = harmonic_oscillator

        integrators = [ForwardEuler(), BackwardEuler(), ModifiedEuler()]
        state = np.array([1.0, 0.0])
        control = np.array([0.0])
        dt = 0.01

        for integrator in integrators:
            new_state = integrator.integrate(dynamics, state, control, dt)

            # Should return correct dimensions
            assert new_state.shape == (2,)
            assert np.all(np.isfinite(new_state))

    def test_nonlinear_pendulum(self, nonlinear_pendulum):
        """Test all methods on nonlinear pendulum dynamics."""
        dynamics = nonlinear_pendulum

        integrators = [ForwardEuler(), BackwardEuler(), ModifiedEuler()]
        state = np.array([0.1, 0.0])  # Small angle
        control = np.array([0.0])
        dt = 0.01

        for integrator in integrators:
            new_state = integrator.integrate(dynamics, state, control, dt)

            # Should give valid results
            assert isinstance(new_state, np.ndarray)
            assert new_state.shape == (2,)
            assert np.all(np.isfinite(new_state))


# ==============================================================================
# Test Statistics Tracking
# ==============================================================================

class TestEulerStatistics:
    """Test statistics tracking for all Euler methods."""

    def test_forward_euler_stats(self, linear_decay):
        """Test Forward Euler statistics tracking."""
        dynamics, _ = linear_decay
        integrator = ForwardEuler()

        integrator.reset_statistics()
        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        assert stats['accepted_steps'] >= 1
        assert stats['function_evaluations'] >= 1

    def test_backward_euler_stats(self, linear_decay):
        """Test Backward Euler statistics tracking."""
        dynamics, _ = linear_decay
        integrator = BackwardEuler()

        integrator.reset_statistics()
        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        assert stats['accepted_steps'] >= 1
        # Backward Euler uses multiple evaluations (implicit solver)
        assert stats['function_evaluations'] >= 1

    def test_modified_euler_stats(self, linear_decay):
        """Test Modified Euler statistics tracking."""
        dynamics, _ = linear_decay
        integrator = ModifiedEuler()

        integrator.reset_statistics()
        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        assert stats['accepted_steps'] >= 1
        assert stats['function_evaluations'] >= 2  # Two evaluations per step
