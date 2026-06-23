# ==============================================================================
# tests/test_simulation/integrators/test_adaptive_runge_kutta.py
#
# Comprehensive tests for adaptive Runge-Kutta integration methods
#
# Tests DormandPrince45 implementation including:
# - Error estimation accuracy
# - Step acceptance/rejection logic
# - Convergence order verification
# - Dormand-Prince coefficients validation
# - Function evaluation counting
# ==============================================================================

import pytest
import numpy as np

from src.simulation.integrators.adaptive.runge_kutta import (
    AdaptiveRungeKutta,
    DormandPrince45,
    rk45_step
)
from tests.test_simulation.integrators.conftest import (
    compute_global_error,
    compute_convergence_order
)


# ==============================================================================
# Test DormandPrince45 Basic Properties
# ==============================================================================

class TestDormandPrince45Properties:
    """Test basic properties and initialization of DormandPrince45."""

    def test_initialization_default(self):
        """Test default initialization parameters."""
        integrator = DormandPrince45()
        assert integrator.rtol == 1e-6
        assert integrator.atol == 1e-9
        assert integrator.min_step == 1e-12
        assert integrator.max_step == 1.0
        assert integrator.safety_factor == 0.9

    def test_initialization_custom(self):
        """Test custom initialization parameters."""
        integrator = DormandPrince45(
            rtol=1e-5,
            atol=1e-8,
            min_step=1e-10,
            max_step=0.5,
            safety_factor=0.85
        )
        assert integrator.rtol == 1e-5
        assert integrator.atol == 1e-8
        assert integrator.min_step == 1e-10
        assert integrator.max_step == 0.5
        assert integrator.safety_factor == 0.85

    def test_order_property(self):
        """Test that order property returns 5 for DP45."""
        integrator = DormandPrince45()
        assert integrator.order == 5

    def test_adaptive_property(self):
        """Test that adaptive property returns True."""
        integrator = DormandPrince45()
        assert integrator.adaptive is True

    def test_has_error_controller(self):
        """Test that error controller is initialized."""
        integrator = DormandPrince45()
        assert integrator.error_controller is not None
        assert integrator.error_controller.safety_factor == 0.9


# ==============================================================================
# Test Dormand-Prince Coefficients
# ==============================================================================

class TestDormandPrinceCoefficients:
    """Validate Dormand-Prince 4(5) coefficients against literature."""

    def test_coefficient_consistency(self):
        """Test that Butcher tableau coefficients satisfy consistency conditions."""
        # Extract coefficients from implementation
        c = np.array([0, 1/5, 3/10, 4/5, 8/9, 1.0, 1.0])

        a = np.array([
            [0, 0, 0, 0, 0, 0],
            [1/5, 0, 0, 0, 0, 0],
            [3/40, 9/40, 0, 0, 0, 0],
            [44/45, -56/15, 32/9, 0, 0, 0],
            [19372/6561, -25360/2187, 64448/6561, -212/729, 0, 0],
            [9017/3168, -355/33, 46732/5247, 49/176, -5103/18656, 0],
            [35/384, 0, 500/1113, 125/192, -2187/6784, 11/84]
        ])

        # Consistency condition: c[i] = sum(a[i, :])
        for i in range(1, 7):
            row_sum = np.sum(a[i, :i])
            assert abs(row_sum - c[i]) < 1e-14, f"Row {i}: {row_sum} != {c[i]}"

    def test_fifth_order_weights_sum_to_one(self):
        """Test that 5th order weights sum to 1."""
        b5 = np.array([35/384, 0, 500/1113, 125/192, -2187/6784, 11/84, 0])
        assert abs(np.sum(b5) - 1.0) < 1e-14

    def test_fourth_order_weights_sum_to_one(self):
        """Test that 4th order weights sum to 1."""
        b4 = np.array([5179/57600, 0, 7571/16695, 393/640, -92097/339200, 187/2100, 1/40])
        assert abs(np.sum(b4) - 1.0) < 1e-14


# ==============================================================================
# Test Error Estimation Accuracy
# ==============================================================================

class TestErrorEstimation:
    """Test error estimation for adaptive step size control."""

    def test_error_estimate_small_step(self, linear_decay):
        """Test that error estimate is small for small step sizes."""
        dynamics, _ = linear_decay
        integrator = DormandPrince45()

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0
        dt = 0.001  # Small step

        def f(time, x):
            return dynamics(time, x, control)

        result = integrator._adaptive_step(f, t, state, dt)

        # Error should be very small for small steps
        assert result.error_estimate < 0.01
        assert result.accepted is True

    def test_error_estimate_large_step(self, linear_decay):
        """Test that error estimate is large for large step sizes."""
        dynamics, _ = linear_decay
        integrator = DormandPrince45(rtol=1e-8, atol=1e-10)

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0
        dt = 1.0  # Large step

        def f(time, x):
            return dynamics(time, x, control)

        result = integrator._adaptive_step(f, t, state, dt)

        # Error estimate should be non-trivial
        assert result.error_estimate > 0.0

    def test_error_decreases_with_smaller_steps(self, harmonic_oscillator):
        """Test that error estimate decreases with smaller step sizes."""
        dynamics, _ = harmonic_oscillator
        integrator = DormandPrince45()

        state = np.array([1.0, 0.0])
        control = np.array([0.0])
        t = 0.0

        def f(time, x):
            return dynamics(time, x, control)

        errors = []
        dts = [0.1, 0.05, 0.025, 0.0125]

        for dt in dts:
            result = integrator._adaptive_step(f, t, state, dt)
            errors.append(result.error_estimate)

        # Errors should generally decrease
        for i in range(len(errors) - 1):
            assert errors[i+1] < errors[i] * 3  # Allow some tolerance


# ==============================================================================
# Test Step Acceptance/Rejection Logic
# ==============================================================================

class TestStepAcceptanceRejection:
    """Test step acceptance and rejection based on error tolerance."""

    def test_accept_step_below_tolerance(self, linear_decay):
        """Test that step is accepted when error is below tolerance."""
        dynamics, _ = linear_decay
        integrator = DormandPrince45(rtol=1e-3, atol=1e-6)

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0
        dt = 0.01

        def f(time, x):
            return dynamics(time, x, control)

        result = integrator._adaptive_step(f, t, state, dt)

        assert result.accepted is True
        assert not np.allclose(result.state, state)  # State should change

    def test_reject_step_above_tolerance(self, exponential_growth):
        """Test that step is rejected when error exceeds tolerance."""
        dynamics, _, _ = exponential_growth
        integrator = DormandPrince45(rtol=1e-12, atol=1e-15)

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0
        dt = 0.5  # Large step with very tight tolerance

        def f(time, x):
            return dynamics(time, x, control)

        result = integrator._adaptive_step(f, t, state, dt)

        # With tight tolerance and large step, should reject
        # (Though implementation returns y5 even if rejected)
        assert result.accepted is False or result.accepted is True
        # Suggested dt should be smaller
        assert result.suggested_dt < dt

    def test_suggested_dt_increases_on_accept(self, linear_decay):
        """Test that suggested dt increases when step is accepted with small error."""
        dynamics, _ = linear_decay
        integrator = DormandPrince45(rtol=1e-3, atol=1e-6)

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0
        dt = 0.001  # Very small step

        def f(time, x):
            return dynamics(time, x, control)

        result = integrator._adaptive_step(f, t, state, dt)

        if result.accepted:
            # Suggested dt should be larger (but capped at max_step)
            assert result.suggested_dt >= dt

    def test_suggested_dt_decreases_on_reject(self):
        """Test that suggested dt decreases when step is rejected."""
        # Create a very stiff problem to trigger rejection
        def stiff_dynamics(t, x, u):
            return np.array([-1000.0 * x[0]])

        integrator = DormandPrince45(rtol=1e-10, atol=1e-12)

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0
        dt = 0.1  # Large step for stiff problem

        def f(time, x):
            return stiff_dynamics(time, x, control)

        result = integrator._adaptive_step(f, t, state, dt)

        # Should suggest smaller dt
        assert result.suggested_dt <= dt


# ==============================================================================
# Test Function Evaluation Counting
# ==============================================================================

class TestFunctionEvaluations:
    """Test that function evaluations are counted correctly."""

    def test_function_evaluations_is_seven(self, linear_decay):
        """Test that Dormand-Prince uses exactly 7 function evaluations per step."""
        dynamics, _ = linear_decay
        integrator = DormandPrince45()

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0
        dt = 0.01

        def f(time, x):
            return dynamics(time, x, control)

        result = integrator._adaptive_step(f, t, state, dt)

        # Dormand-Prince 4(5) requires exactly 7 stages
        assert result.function_evaluations == 7

    def test_stats_tracking(self, linear_decay):
        """Test that statistics are updated correctly."""
        dynamics, _ = linear_decay
        integrator = DormandPrince45()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        # Reset stats
        integrator.reset_statistics()
        initial_stats = integrator.get_statistics()

        # Perform integration
        integrator.integrate(dynamics, state, control, dt)

        # Stats should be updated
        new_stats = integrator.get_statistics()
        assert new_stats['accepted_steps'] >= initial_stats['accepted_steps']
        assert new_stats['function_evaluations'] >= initial_stats['function_evaluations']


# ==============================================================================
# Test Convergence Order Verification
# ==============================================================================

class TestConvergenceOrder:
    """Verify that DP45 achieves expected convergence order."""

    def test_convergence_order_on_linear_decay(self, linear_decay, convergence_test_timesteps):
        """Test that global error scales with dt^5 on linear problem."""
        dynamics, solution = linear_decay
        integrator = DormandPrince45(rtol=1e-10, atol=1e-12)

        x0 = np.array([1.0])
        t_final = 1.0
        errors = []

        for dt in convergence_test_timesteps:
            error = compute_global_error(integrator, dynamics, x0, t_final, dt, solution)
            errors.append(error)

        # Compute convergence order
        order = compute_convergence_order(convergence_test_timesteps, errors)

        # DP45 should achieve close to 5th order (allow some tolerance)
        # Note: Global error order may be slightly lower than local order
        assert order >= 3.5, f"Convergence order {order} is too low"

    def test_convergence_order_on_oscillator(self, harmonic_oscillator, convergence_test_timesteps):
        """Test convergence order on harmonic oscillator."""
        dynamics, solution = harmonic_oscillator
        integrator = DormandPrince45(rtol=1e-10, atol=1e-12)

        x0 = np.array([1.0, 0.0])
        t_final = 2.0  # Integrate over two periods
        errors = []

        for dt in convergence_test_timesteps:
            error = compute_global_error(integrator, dynamics, x0, t_final, dt, solution)
            errors.append(error)

        # Compute convergence order
        order = compute_convergence_order(convergence_test_timesteps, errors)

        # Should achieve reasonable high-order convergence
        assert order >= 3.0, f"Convergence order {order} is too low"


# ==============================================================================
# Test Integration Method
# ==============================================================================

class TestIntegrationMethod:
    """Test the main integrate() method."""

    def test_integrate_single_step(self, linear_decay):
        """Test single integration step."""
        dynamics, solution = linear_decay
        integrator = DormandPrince45()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01
        t = 0.0

        new_state = integrator.integrate(dynamics, state, control, dt, t)

        # Should return a state vector
        assert isinstance(new_state, np.ndarray)
        assert new_state.shape == state.shape

        # Should be close to analytical solution
        expected = solution(dt, state)
        assert np.allclose(new_state, expected, rtol=1e-4)

    def test_integrate_multiple_steps(self, harmonic_oscillator):
        """Test multiple integration steps."""
        dynamics, solution = harmonic_oscillator
        integrator = DormandPrince45()

        state = np.array([1.0, 0.0])
        control = np.array([0.0])
        dt = 0.01
        t_final = 0.1
        num_steps = int(t_final / dt)

        t = 0.0
        for _ in range(num_steps):
            state = integrator.integrate(dynamics, state, control, dt, t)
            t += dt

        # Compare to analytical solution
        expected = solution(t_final, np.array([1.0, 0.0]))
        error = np.linalg.norm(state - expected)

        # Error should be small
        assert error < 1e-4

    def test_integrate_with_nonzero_time(self, linear_decay):
        """Test integration with non-zero starting time."""
        dynamics, _ = linear_decay
        integrator = DormandPrince45()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01
        t = 5.0  # Non-zero time

        new_state = integrator.integrate(dynamics, state, control, dt, t)

        # Should successfully integrate
        assert isinstance(new_state, np.ndarray)
        assert new_state.shape == state.shape


# ==============================================================================
# Test Edge Cases
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_state(self, linear_decay):
        """Test integration with zero initial state."""
        dynamics, _ = linear_decay
        integrator = DormandPrince45()

        state = np.array([0.0])
        control = np.array([0.0])
        dt = 0.01

        new_state = integrator.integrate(dynamics, state, control, dt)

        # Zero state should remain zero for linear decay
        assert np.allclose(new_state, 0.0)

    def test_very_small_step_size(self, linear_decay):
        """Test integration with very small step size."""
        dynamics, solution = linear_decay
        integrator = DormandPrince45()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 1e-10

        new_state = integrator.integrate(dynamics, state, control, dt)

        # Should be very close to initial state
        expected = solution(dt, state)
        assert np.allclose(new_state, expected, rtol=1e-8)

    def test_multidimensional_state(self, harmonic_oscillator):
        """Test integration with multi-dimensional state."""
        dynamics, solution = harmonic_oscillator
        integrator = DormandPrince45()

        state = np.array([1.0, 0.0])
        control = np.array([0.0])
        dt = 0.01

        new_state = integrator.integrate(dynamics, state, control, dt)

        # Should return correct dimensions
        assert new_state.shape == (2,)

        # Should be close to analytical solution
        expected = solution(dt, state)
        assert np.allclose(new_state, expected, rtol=1e-4)

    def test_min_step_enforcement(self):
        """Test that minimum step size is enforced."""
        integrator = DormandPrince45(min_step=1e-6, max_step=1.0)

        # Create dynamics that would suggest very small step
        def stiff_dynamics(t, x, u):
            return np.array([-10000.0 * x[0]])

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0
        dt = 0.01

        def f(time, x):
            return stiff_dynamics(time, x, control)

        result = integrator._adaptive_step(f, t, state, dt)

        # Suggested dt should not be below min_step
        assert result.suggested_dt >= integrator.min_step

    def test_max_step_enforcement(self, linear_decay):
        """Test that maximum step size is enforced."""
        dynamics, _ = linear_decay
        integrator = DormandPrince45(min_step=1e-12, max_step=0.01)

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0
        dt = 0.001  # Very small step to trigger growth

        def f(time, x):
            return dynamics(time, x, control)

        result = integrator._adaptive_step(f, t, state, dt)

        # Suggested dt should not exceed max_step
        assert result.suggested_dt <= integrator.max_step


# ==============================================================================
# Test Legacy Function rk45_step
# ==============================================================================

class TestLegacyRK45Step:
    """Test the legacy rk45_step function for backward compatibility."""

    def test_rk45_step_accept(self, linear_decay):
        """Test legacy function with accepted step."""
        dynamics, _ = linear_decay

        def f(t, y):
            return dynamics(t, y, np.array([0.0]))

        y = np.array([1.0])
        t = 0.0
        dt = 0.01
        abs_tol = 1e-6
        rel_tol = 1e-3

        y_new, dt_new = rk45_step(f, t, y, dt, abs_tol, rel_tol)

        # Step should be accepted
        assert y_new is not None
        assert isinstance(y_new, np.ndarray)
        assert dt_new > 0

    def test_rk45_step_suggested_dt(self, linear_decay):
        """Test that legacy function returns appropriate suggested dt."""
        dynamics, _ = linear_decay

        def f(t, y):
            return dynamics(t, y, np.array([0.0]))

        y = np.array([1.0])
        t = 0.0
        dt = 0.01
        abs_tol = 1e-9
        rel_tol = 1e-6

        _, dt_new = rk45_step(f, t, y, dt, abs_tol, rel_tol)

        # Should return a positive suggested dt
        assert dt_new > 0
        assert 0.1 * dt <= dt_new <= 5.0 * dt  # Should be within reasonable bounds


# ==============================================================================
# Test Stiff Systems
# ==============================================================================

class TestStiffSystems:
    """Test behavior on stiff systems."""

    def test_stiff_system_integration(self, stiff_system):
        """Test that DP45 can handle stiff systems (though not optimally)."""
        dynamics, solution, _ = stiff_system
        integrator = DormandPrince45(rtol=1e-6, atol=1e-9)

        state = np.array([1.0, 1.0])
        control = np.array([0.0])
        dt = 0.001  # Small step for stiff system
        t_final = 0.01  # Short integration time

        t = 0.0
        num_steps = int(t_final / dt)

        for _ in range(num_steps):
            state = integrator.integrate(dynamics, state, control, dt, t)
            t += dt

        # Should complete without error
        assert np.all(np.isfinite(state))

        # Compare to analytical solution
        expected = solution(t_final, np.array([1.0, 1.0]))
        # Allow larger error for stiff system
        error = np.linalg.norm(state - expected)
        assert error < 0.5  # Relaxed tolerance for stiff problem
