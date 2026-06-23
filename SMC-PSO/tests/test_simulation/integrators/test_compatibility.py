# ==============================================================================
# tests/test_simulation/integrators/test_compatibility.py
#
# Comprehensive tests for integrator compatibility wrappers
#
# Tests including:
# - DynamicsCompatibilityWrapper interface adaptation
# - LegacyDynamicsWrapper finite difference estimation
# - IntegratorSafetyWrapper fallback chain behavior
# - Non-finite detection and automatic fallback
# - Convenience functions
# ==============================================================================

import pytest
import numpy as np

from src.simulation.integrators.compatibility import (
    DynamicsCompatibilityWrapper,
    LegacyDynamicsWrapper,
    IntegratorSafetyWrapper,
    create_compatible_dynamics,
    create_safe_integrator,
    create_robust_euler_dynamics,
    create_robust_rk4_dynamics,
    create_robust_adaptive_dynamics
)
from src.simulation.integrators.fixed_step.euler import ForwardEuler
from src.simulation.integrators.fixed_step.runge_kutta import RungeKutta4
from src.simulation.integrators.adaptive.runge_kutta import DormandPrince45


class TestDynamicsCompatibilityWrapper:
    """Test DynamicsCompatibilityWrapper for interface adaptation."""

    def test_initialization(self, linear_decay):
        """Test wrapper initialization."""
        dynamics, _ = linear_decay
        integrator = ForwardEuler()

        wrapper = DynamicsCompatibilityWrapper(integrator, dynamics)

        assert wrapper.integrator is integrator
        assert wrapper.dynamics_fn is dynamics
        assert wrapper.current_time == 0.0

    def test_step_interface(self, linear_decay):
        """Test step() method matches expected interface."""
        dynamics, _ = linear_decay
        integrator = ForwardEuler()

        wrapper = DynamicsCompatibilityWrapper(integrator, dynamics)

        state = np.array([1.0])
        control = 0.0
        dt = 0.01

        new_state = wrapper.step(state, control, dt)

        assert isinstance(new_state, np.ndarray)
        assert new_state.shape == state.shape
        assert np.all(np.isfinite(new_state))

    def test_time_tracking(self, linear_decay):
        """Test that wrapper tracks time correctly."""
        dynamics, _ = linear_decay
        integrator = ForwardEuler()

        wrapper = DynamicsCompatibilityWrapper(integrator, dynamics)

        initial_time = wrapper.current_time
        state = np.array([1.0])
        control = 0.0
        dt = 0.01

        wrapper.step(state, control, dt)

        assert wrapper.current_time == initial_time + dt

    def test_reset_time(self, linear_decay):
        """Test resetting internal time counter."""
        dynamics, _ = linear_decay
        integrator = ForwardEuler()

        wrapper = DynamicsCompatibilityWrapper(integrator, dynamics)

        wrapper.step(np.array([1.0]), 0.0, 0.01)
        wrapper.reset_time(5.0)

        assert wrapper.current_time == 5.0

    def test_handles_array_control(self, harmonic_oscillator):
        """Test that wrapper handles array control inputs."""
        dynamics, _ = harmonic_oscillator
        integrator = RungeKutta4()

        wrapper = DynamicsCompatibilityWrapper(integrator, dynamics)

        state = np.array([1.0, 0.0])
        control = np.array([0.5])
        dt = 0.01

        new_state = wrapper.step(state, control, dt)

        assert isinstance(new_state, np.ndarray)
        assert new_state.shape == state.shape

    def test_handles_scalar_control(self, linear_decay):
        """Test that wrapper handles scalar control inputs."""
        dynamics, _ = linear_decay
        integrator = ForwardEuler()

        wrapper = DynamicsCompatibilityWrapper(integrator, dynamics)

        state = np.array([1.0])
        control = 0.0  # Scalar
        dt = 0.01

        new_state = wrapper.step(state, control, dt)

        assert isinstance(new_state, np.ndarray)


class TestLegacyDynamicsWrapper:
    """Test LegacyDynamicsWrapper for finite difference estimation."""

    def test_initialization(self):
        """Test wrapper initialization."""
        class LegacyDynamics:
            def step(self, state, control, dt):
                return state - 0.5 * state * dt  # Simple decay

        legacy = LegacyDynamics()
        wrapper = LegacyDynamicsWrapper(legacy)

        assert wrapper.legacy_dynamics is legacy

    def test_callable_interface(self):
        """Test that wrapper is callable with (t, state, control) signature."""
        class LegacyDynamics:
            def step(self, state, control, dt):
                return state - 0.5 * state * dt

        legacy = LegacyDynamics()
        wrapper = LegacyDynamicsWrapper(legacy)

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0

        derivative = wrapper(t, state, control)

        assert isinstance(derivative, np.ndarray)
        assert derivative.shape == state.shape

    def test_finite_difference_estimation(self):
        """Test that finite difference gives reasonable derivative estimate."""
        class LegacyDynamics:
            def step(self, state, control, dt):
                # Exact: dx/dt = -0.5*x
                # So x(t+dt) = x * exp(-0.5*dt) ≈ x * (1 - 0.5*dt)
                return state * np.exp(-0.5 * dt)

        legacy = LegacyDynamics()
        wrapper = LegacyDynamicsWrapper(legacy)

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0

        derivative = wrapper(t, state, control)

        # Expected derivative: -0.5 * state
        expected = -0.5 * state

        assert np.allclose(derivative, expected, rtol=1e-4)

    def test_handles_failing_legacy_dynamics(self):
        """Test that wrapper handles exceptions in legacy dynamics."""
        class FailingLegacyDynamics:
            def step(self, state, control, dt):
                raise RuntimeError("Legacy dynamics failed")

        legacy = FailingLegacyDynamics()
        wrapper = LegacyDynamicsWrapper(legacy)

        state = np.array([1.0])
        control = np.array([0.0])
        t = 0.0

        # Should return zero derivative on failure
        derivative = wrapper(t, state, control)

        assert np.allclose(derivative, 0.0)


class TestIntegratorSafetyWrapper:
    """Test IntegratorSafetyWrapper for automatic fallback."""

    def test_initialization(self):
        """Test safety wrapper initialization."""
        base = RungeKutta4()
        fallback = ForwardEuler()

        wrapper = IntegratorSafetyWrapper(base, fallback)

        assert wrapper.base_integrator is base
        assert wrapper.fallback_integrator is fallback
        assert wrapper.fallback_active is False
        assert wrapper.failure_count == 0

    def test_initialization_default_fallback(self):
        """Test that default fallback is Forward Euler."""
        base = RungeKutta4()
        wrapper = IntegratorSafetyWrapper(base)

        assert isinstance(wrapper.fallback_integrator, ForwardEuler)

    def test_successful_integration(self, linear_decay):
        """Test that successful integration uses base integrator."""
        dynamics, _ = linear_decay
        base = RungeKutta4()
        wrapper = IntegratorSafetyWrapper(base)

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        new_state = wrapper.integrate(dynamics, state, control, dt)

        assert isinstance(new_state, np.ndarray)
        assert wrapper.fallback_active is False
        assert wrapper.failure_count == 0

    def test_fallback_on_nonfinite_result(self):
        """Test automatic fallback when integrator returns non-finite values."""
        def bad_dynamics(t, x, u):
            return np.array([np.inf])  # Returns infinity

        base = RungeKutta4()
        wrapper = IntegratorSafetyWrapper(base)

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        # Should detect non-finite and use fallback
        new_state = wrapper.integrate(bad_dynamics, state, control, dt)

        # Should still return finite values (via fallback)
        assert np.all(np.isfinite(new_state))

    def test_fallback_activation_after_failures(self):
        """Test that fallback is activated after 3 failures."""
        def failing_dynamics(t, x, u):
            raise RuntimeError("Integration failed")

        base = RungeKutta4()
        wrapper = IntegratorSafetyWrapper(base)

        state = np.array([1.0])
        control = np.array([0.0])
        dt = 0.01

        # Trigger 3 failures
        for _ in range(3):
            wrapper.integrate(failing_dynamics, state, control, dt)

        assert wrapper.fallback_active is True
        assert wrapper.failure_count >= 3

    def test_reset_clears_state(self, linear_decay):
        """Test that reset() clears wrapper state."""
        dynamics, _ = linear_decay
        base = RungeKutta4()
        wrapper = IntegratorSafetyWrapper(base)

        # Trigger some failures
        wrapper.failure_count = 5
        wrapper.fallback_active = True

        # Reset
        wrapper.reset()

        assert wrapper.fallback_active is False
        assert wrapper.failure_count == 0


class TestConvenienceFunctions:
    """Test convenience functions for creating wrappers."""

    def test_create_compatible_dynamics_euler(self, linear_decay):
        """Test creating Euler-integrated compatible dynamics."""
        dynamics, _ = linear_decay

        wrapper = create_compatible_dynamics('euler', dynamics_fn=dynamics)

        assert isinstance(wrapper, DynamicsCompatibilityWrapper)
        assert isinstance(wrapper.integrator, ForwardEuler)

    def test_create_compatible_dynamics_rk4(self, harmonic_oscillator):
        """Test creating RK4-integrated compatible dynamics."""
        dynamics, _ = harmonic_oscillator

        wrapper = create_compatible_dynamics('rk4', dynamics_fn=dynamics)

        assert isinstance(wrapper, DynamicsCompatibilityWrapper)
        assert isinstance(wrapper.integrator, RungeKutta4)

    def test_create_compatible_dynamics_adaptive(self, linear_decay):
        """Test creating adaptive-integrated compatible dynamics."""
        dynamics, _ = linear_decay

        wrapper = create_compatible_dynamics('rk45', dynamics_fn=dynamics, rtol=1e-8)

        assert isinstance(wrapper, DynamicsCompatibilityWrapper)
        assert isinstance(wrapper.integrator, DormandPrince45)

    def test_create_compatible_dynamics_with_legacy(self):
        """Test creating compatible dynamics from legacy dynamics."""
        class LegacyDynamics:
            def step(self, state, control, dt):
                return state - 0.5 * state * dt

        legacy = LegacyDynamics()
        wrapper = create_compatible_dynamics('rk4', legacy_dynamics=legacy)

        assert isinstance(wrapper, DynamicsCompatibilityWrapper)
        assert isinstance(wrapper.dynamics_fn, LegacyDynamicsWrapper)

    def test_create_safe_integrator_euler(self):
        """Test creating safe Euler integrator."""
        wrapper = create_safe_integrator('euler')

        assert isinstance(wrapper, IntegratorSafetyWrapper)
        assert isinstance(wrapper.base_integrator, ForwardEuler)

    def test_create_safe_integrator_rk4(self):
        """Test creating safe RK4 integrator."""
        wrapper = create_safe_integrator('rk4')

        assert isinstance(wrapper, IntegratorSafetyWrapper)
        assert isinstance(wrapper.base_integrator, RungeKutta4)

    def test_create_robust_euler_dynamics(self, linear_decay):
        """Test creating robust Euler dynamics."""
        dynamics, _ = linear_decay

        wrapper = create_robust_euler_dynamics(dynamics)

        assert isinstance(wrapper, DynamicsCompatibilityWrapper)
        assert isinstance(wrapper.integrator, IntegratorSafetyWrapper)

    def test_create_robust_rk4_dynamics(self, harmonic_oscillator):
        """Test creating robust RK4 dynamics."""
        dynamics, _ = harmonic_oscillator

        wrapper = create_robust_rk4_dynamics(dynamics)

        assert isinstance(wrapper, DynamicsCompatibilityWrapper)
        assert isinstance(wrapper.integrator, IntegratorSafetyWrapper)

    def test_create_robust_adaptive_dynamics(self, linear_decay):
        """Test creating robust adaptive dynamics."""
        dynamics, _ = linear_decay

        wrapper = create_robust_adaptive_dynamics(dynamics, rtol=1e-7)

        assert isinstance(wrapper, DynamicsCompatibilityWrapper)
        assert isinstance(wrapper.integrator, IntegratorSafetyWrapper)


class TestErrorHandling:
    """Test error handling in compatibility wrappers."""

    def test_create_compatible_dynamics_unknown_type(self, linear_decay):
        """Test that unknown integrator type raises error."""
        dynamics, _ = linear_decay

        with pytest.raises(ValueError, match="Unknown integrator type"):
            create_compatible_dynamics('unknown_type', dynamics_fn=dynamics)

    def test_create_compatible_dynamics_no_dynamics(self):
        """Test that missing dynamics raises error."""
        with pytest.raises(ValueError, match="Must provide either"):
            create_compatible_dynamics('rk4')

    def test_create_safe_integrator_unknown_type(self):
        """Test that unknown integrator type raises error."""
        with pytest.raises(ValueError, match="Unknown integrator type"):
            create_safe_integrator('unknown_type')


class TestIntegrationWorkflows:
    """Test end-to-end integration workflows."""

    def test_compatible_dynamics_workflow(self, harmonic_oscillator):
        """Test complete workflow with compatible dynamics."""
        dynamics, solution = harmonic_oscillator

        # Create compatible dynamics
        wrapped_dynamics = create_compatible_dynamics('rk4', dynamics_fn=dynamics)

        # Use it for simulation
        state = np.array([1.0, 0.0])
        control = 0.0
        dt = 0.01
        t_final = 0.5
        num_steps = int(t_final / dt)

        for _ in range(num_steps):
            state = wrapped_dynamics.step(state, control, dt)

        # Should match analytical solution
        expected = solution(t_final, np.array([1.0, 0.0]))
        error = np.linalg.norm(state - expected)

        assert error < 1e-3

    def test_robust_dynamics_with_failures(self):
        """Test robust dynamics handling failures gracefully."""
        failure_count = [0]

        def sometimes_failing_dynamics(t, x, u):
            failure_count[0] += 1
            if failure_count[0] < 5:
                return np.array([np.nan])  # Fail first few times
            return np.array([-0.5 * x[0]])  # Then work normally

        wrapped_dynamics = create_robust_euler_dynamics(sometimes_failing_dynamics)

        state = np.array([1.0])
        control = 0.0
        dt = 0.01

        # Should handle failures and continue
        for _ in range(10):
            state = wrapped_dynamics.step(state, control, dt)

        # Should still be finite
        assert np.all(np.isfinite(state))
