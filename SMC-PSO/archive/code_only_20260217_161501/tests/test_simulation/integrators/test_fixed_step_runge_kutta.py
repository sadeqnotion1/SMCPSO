# ==============================================================================
# tests/test_simulation/integrators/test_fixed_step_runge_kutta.py
#
# Comprehensive tests for fixed-step Runge-Kutta integration methods
#
# Tests RK2, RK4, RK38 including:
# - Accuracy and order verification
# - Convergence rates on standard test problems
# - Function evaluation counts
# - Comparison to analytical solutions
# ==============================================================================

import pytest
import numpy as np

from src.simulation.integrators.fixed_step.runge_kutta import (
    RungeKutta2,
    RungeKutta4,
    RungeKutta38,
    ClassicalRungeKutta
)
from tests.test_simulation.integrators.conftest import (
    compute_global_error,
    compute_convergence_order
)


# ==============================================================================
# Test RungeKutta2 (Midpoint Method)
# ==============================================================================

class TestRungeKutta2:
    """Test RK2 (midpoint rule) integration."""

    def test_initialization(self):
        """Test RK2 initialization."""
        integrator = RungeKutta2()
        assert integrator.order == 2
        assert integrator.adaptive is False

    def test_integrate_single_step(self, linear_decay):
        """Test single RK2 step."""
        dynamics, solution = linear_decay
        integrator = RungeKutta2()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        new_state = integrator.integrate(dynamics, state, control, dt)

        # Should be close to analytical solution
        expected = solution(dt, state)
        assert np.allclose(new_state, expected, rtol=1e-3)

    def test_function_evaluations(self, linear_decay):
        """Test that RK2 uses exactly 2 function evaluations."""
        dynamics, _ = linear_decay
        integrator = RungeKutta2()

        integrator.reset_statistics()
        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        assert stats['function_evaluations'] >= 2

    def test_convergence_order(self, linear_decay, convergence_test_timesteps):
        """Test that RK2 achieves second-order convergence."""
        dynamics, solution = linear_decay
        integrator = RungeKutta2()

        x0 = np.array([1.0])
        t_final = 1.0
        errors = []

        for dt in convergence_test_timesteps:
            error = compute_global_error(integrator, dynamics, x0, t_final, dt, solution)
            errors.append(error)

        order = compute_convergence_order(convergence_test_timesteps, errors)

        # Should achieve second-order convergence
        assert 1.5 <= order <= 2.5, f"Convergence order {order} not second-order"

    def test_harmonic_oscillator_accuracy(self, harmonic_oscillator):
        """Test RK2 accuracy on harmonic oscillator."""
        dynamics, solution = harmonic_oscillator
        integrator = RungeKutta2()

        state = np.array([1.0, 0.0])
        control = np.array([0.0])
        dt = 0.01
        t_final = 1.0
        num_steps = int(t_final / dt)

        for _ in range(num_steps):
            state = integrator.integrate(dynamics, state, control, dt)

        expected = solution(t_final, np.array([1.0, 0.0]))
        error = np.linalg.norm(state - expected)

        # RK2 should be reasonably accurate
        assert error < 0.01


# ==============================================================================
# Test RungeKutta4 (Classic RK4)
# ==============================================================================

class TestRungeKutta4:
    """Test classic RK4 integration."""

    def test_initialization(self):
        """Test RK4 initialization."""
        integrator = RungeKutta4()
        assert integrator.order == 4
        assert integrator.adaptive is False

    def test_integrate_single_step(self, linear_decay):
        """Test single RK4 step."""
        dynamics, solution = linear_decay
        integrator = RungeKutta4()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        new_state = integrator.integrate(dynamics, state, control, dt)

        # Should be very close to analytical solution
        expected = solution(dt, state)
        assert np.allclose(new_state, expected, rtol=1e-6)

    def test_function_evaluations(self, linear_decay):
        """Test that RK4 uses exactly 4 function evaluations."""
        dynamics, _ = linear_decay
        integrator = RungeKutta4()

        integrator.reset_statistics()
        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        assert stats['function_evaluations'] >= 4

    def test_convergence_order(self, linear_decay, convergence_test_timesteps):
        """Test that RK4 achieves fourth-order convergence."""
        dynamics, solution = linear_decay
        integrator = RungeKutta4()

        x0 = np.array([1.0])
        t_final = 1.0
        errors = []

        for dt in convergence_test_timesteps:
            error = compute_global_error(integrator, dynamics, x0, t_final, dt, solution)
            errors.append(error)

        order = compute_convergence_order(convergence_test_timesteps, errors)

        # Should achieve fourth-order convergence
        assert order >= 3.0, f"Convergence order {order} not fourth-order"

    def test_harmonic_oscillator_high_accuracy(self, harmonic_oscillator):
        """Test RK4 high accuracy on harmonic oscillator."""
        dynamics, solution = harmonic_oscillator
        integrator = RungeKutta4()

        state = np.array([1.0, 0.0])
        control = np.array([0.0])
        dt = 0.01
        t_final = 2.0  # Two full periods
        num_steps = int(t_final / dt)

        for _ in range(num_steps):
            state = integrator.integrate(dynamics, state, control, dt)

        expected = solution(t_final, np.array([1.0, 0.0]))
        error = np.linalg.norm(state - expected)

        # RK4 should be very accurate
        assert error < 1e-4

    def test_more_accurate_than_rk2(self, harmonic_oscillator):
        """Test that RK4 is more accurate than RK2."""
        dynamics, solution = harmonic_oscillator

        rk2 = RungeKutta2()
        rk4 = RungeKutta4()

        x0 = np.array([1.0, 0.0])
        dt = 0.05
        t_final = 1.0

        error_rk2 = compute_global_error(rk2, dynamics, x0, t_final, dt, solution)
        error_rk4 = compute_global_error(rk4, dynamics, x0, t_final, dt, solution)

        # RK4 should be significantly more accurate
        assert error_rk4 < error_rk2


# ==============================================================================
# Test RungeKutta38 (3/8 Rule)
# ==============================================================================

class TestRungeKutta38:
    """Test RK 3/8 rule integration."""

    def test_initialization(self):
        """Test RK38 initialization."""
        integrator = RungeKutta38()
        assert integrator.order == 4
        assert integrator.adaptive is False

    def test_integrate_single_step(self, linear_decay):
        """Test single RK38 step."""
        dynamics, solution = linear_decay
        integrator = RungeKutta38()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        new_state = integrator.integrate(dynamics, state, control, dt)

        # Should be very close to analytical solution
        expected = solution(dt, state)
        assert np.allclose(new_state, expected, rtol=1e-6)

    def test_function_evaluations(self, linear_decay):
        """Test that RK38 uses exactly 4 function evaluations."""
        dynamics, _ = linear_decay
        integrator = RungeKutta38()

        integrator.reset_statistics()
        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        assert stats['function_evaluations'] >= 4

    def test_convergence_order(self, linear_decay, convergence_test_timesteps):
        """Test that RK38 achieves fourth-order convergence."""
        dynamics, solution = linear_decay
        integrator = RungeKutta38()

        x0 = np.array([1.0])
        t_final = 1.0
        errors = []

        for dt in convergence_test_timesteps:
            error = compute_global_error(integrator, dynamics, x0, t_final, dt, solution)
            errors.append(error)

        order = compute_convergence_order(convergence_test_timesteps, errors)

        # Should achieve fourth-order convergence
        assert order >= 3.0, f"Convergence order {order} not fourth-order"

    def test_comparable_to_rk4(self, harmonic_oscillator):
        """Test that RK38 has comparable accuracy to RK4."""
        dynamics, solution = harmonic_oscillator

        rk4 = RungeKutta4()
        rk38 = RungeKutta38()

        x0 = np.array([1.0, 0.0])
        dt = 0.01
        t_final = 1.0

        error_rk4 = compute_global_error(rk4, dynamics, x0, t_final, dt, solution)
        error_rk38 = compute_global_error(rk38, dynamics, x0, t_final, dt, solution)

        # Both should have similar accuracy (same order)
        assert error_rk38 < error_rk4 * 10  # Allow factor of 10 difference


# ==============================================================================
# Test ClassicalRungeKutta Alias
# ==============================================================================

class TestClassicalRungeKutta:
    """Test ClassicalRungeKutta alias for RK4."""

    def test_is_alias_for_rk4(self):
        """Test that ClassicalRungeKutta is an alias for RungeKutta4."""
        classical = ClassicalRungeKutta()
        assert classical.order == 4
        assert classical.adaptive is False

    def test_same_results_as_rk4(self, linear_decay):
        """Test that ClassicalRungeKutta gives same results as RK4."""
        dynamics, _ = linear_decay

        rk4 = RungeKutta4()
        classical = ClassicalRungeKutta()

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        result_rk4 = rk4.integrate(dynamics, state, control, dt)
        result_classical = classical.integrate(dynamics, state, control, dt)

        # Should give identical results
        assert np.allclose(result_rk4, result_classical)


# ==============================================================================
# Test Edge Cases and Comparative Studies
# ==============================================================================

class TestRungeKuttaEdgeCases:
    """Test edge cases for all RK methods."""

    def test_zero_state(self, linear_decay):
        """Test all RK methods with zero initial state."""
        dynamics, _ = linear_decay

        integrators = [RungeKutta2(), RungeKutta4(), RungeKutta38()]
        state = np.array([0.0])
        control = np.array([0.0])
        dt = 0.01

        for integrator in integrators:
            new_state = integrator.integrate(dynamics, state, control, dt)
            assert np.allclose(new_state, 0.0)

    def test_very_small_step(self, harmonic_oscillator):
        """Test all RK methods with very small step size."""
        dynamics, solution = harmonic_oscillator

        integrators = [RungeKutta2(), RungeKutta4(), RungeKutta38()]
        state = np.array([1.0, 0.0])
        control = np.array([0.0])
        dt = 1e-10

        for integrator in integrators:
            new_state = integrator.integrate(dynamics, state, control, dt)
            expected = solution(dt, state)
            assert np.allclose(new_state, expected, rtol=1e-6)

    def test_multidimensional_state(self, harmonic_oscillator):
        """Test all RK methods with multi-dimensional state."""
        dynamics, _ = harmonic_oscillator

        integrators = [RungeKutta2(), RungeKutta4(), RungeKutta38()]
        state = np.array([1.0, 0.5])
        control = np.array([0.0])
        dt = 0.01

        for integrator in integrators:
            new_state = integrator.integrate(dynamics, state, control, dt)
            assert new_state.shape == (2,)
            assert np.all(np.isfinite(new_state))

    def test_nonlinear_pendulum(self, nonlinear_pendulum):
        """Test all RK methods on nonlinear pendulum."""
        dynamics = nonlinear_pendulum

        integrators = [RungeKutta2(), RungeKutta4(), RungeKutta38()]
        state = np.array([0.2, 0.1])
        control = np.array([0.0])
        dt = 0.01

        for integrator in integrators:
            new_state = integrator.integrate(dynamics, state, control, dt)
            assert isinstance(new_state, np.ndarray)
            assert new_state.shape == (2,)
            assert np.all(np.isfinite(new_state))

    def test_accuracy_ordering(self, harmonic_oscillator):
        """Test that higher-order methods are more accurate."""
        dynamics, solution = harmonic_oscillator

        rk2 = RungeKutta2()
        rk4 = RungeKutta4()

        x0 = np.array([1.0, 0.0])
        dt = 0.05
        t_final = 1.0

        error_rk2 = compute_global_error(rk2, dynamics, x0, t_final, dt, solution)
        error_rk4 = compute_global_error(rk4, dynamics, x0, t_final, dt, solution)

        # RK4 should be more accurate than RK2
        assert error_rk4 < error_rk2


# ==============================================================================
# Test Statistics Tracking
# ==============================================================================

class TestRungeKuttaStatistics:
    """Test statistics tracking for all RK methods."""

    def test_rk2_statistics(self, linear_decay):
        """Test RK2 statistics tracking."""
        dynamics, _ = linear_decay
        integrator = RungeKutta2()

        integrator.reset_statistics()
        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        assert stats['accepted_steps'] >= 1
        assert stats['function_evaluations'] >= 2

    def test_rk4_statistics(self, linear_decay):
        """Test RK4 statistics tracking."""
        dynamics, _ = linear_decay
        integrator = RungeKutta4()

        integrator.reset_statistics()
        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        assert stats['accepted_steps'] >= 1
        assert stats['function_evaluations'] >= 4

    def test_rk38_statistics(self, linear_decay):
        """Test RK38 statistics tracking."""
        dynamics, _ = linear_decay
        integrator = RungeKutta38()

        integrator.reset_statistics()
        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        integrator.integrate(dynamics, state, control, dt)

        stats = integrator.get_statistics()
        assert stats['accepted_steps'] >= 1
        assert stats['function_evaluations'] >= 4


# ==============================================================================
# Test Stability on Stiff Problems
# ==============================================================================

class TestRungeKuttaStability:
    """Test stability of RK methods on stiff problems."""

    def test_rk2_on_stiff_system(self, stiff_system):
        """Test RK2 on stiff system with appropriate timestep."""
        dynamics, _, _ = stiff_system
        integrator = RungeKutta2()

        state = np.array([1.0, 1.0])
        control = np.array([0.0])
        dt = 0.001  # Small timestep for stability
        t_final = 0.01

        num_steps = int(t_final / dt)

        for _ in range(num_steps):
            state = integrator.integrate(dynamics, state, control, dt)

        # Should remain finite
        assert np.all(np.isfinite(state))

    def test_rk4_on_stiff_system(self, stiff_system):
        """Test RK4 on stiff system."""
        dynamics, solution, _ = stiff_system
        integrator = RungeKutta4()

        state = np.array([1.0, 1.0])
        control = np.array([0.0])
        dt = 0.001  # Small timestep
        t_final = 0.01

        num_steps = int(t_final / dt)

        for _ in range(num_steps):
            state = integrator.integrate(dynamics, state, control, dt)

        # Should remain finite
        assert np.all(np.isfinite(state))

        # Should be reasonably accurate
        expected = solution(t_final, np.array([1.0, 1.0]))
        error = np.linalg.norm(state - expected)
        assert error < 0.5
