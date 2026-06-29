"""M4 Slice 3 - integrator/dynamics compatibility wrappers."""
import numpy as np
import pytest

from src.simulation.integrators.compatibility import (
    DynamicsCompatibilityWrapper, LegacyDynamicsWrapper, IntegratorSafetyWrapper,
    create_compatible_dynamics, create_safe_integrator,
)
from src.simulation.integrators.fixed_step.runge_kutta import RungeKutta4
from src.simulation.integrators.fixed_step.euler import ForwardEuler


def test_compatibility_wrapper_matches_direct_rk4():
    f = lambda t, x, u: np.array([x[1], -x[0] + u[0]])
    x0 = np.array([0.2, 0.0])
    dt = 0.01
    wrapped = create_compatible_dynamics("rk4", f)
    out = wrapped.step(x0, np.array([0.5]), dt)
    direct = RungeKutta4().integrate(f, x0, np.array([0.5]), dt)
    assert np.allclose(out, direct)


def test_compatibility_wrapper_advances_time():
    f = lambda t, x, u: np.array([0.0])
    w = DynamicsCompatibilityWrapper(ForwardEuler(), f)
    assert w.current_time == 0.0
    w.step(np.array([1.0]), np.array([0.0]), 0.1)
    assert np.isclose(w.current_time, 0.1)
    w.reset_time()
    assert w.current_time == 0.0


def test_create_compatible_requires_a_source():
    with pytest.raises(ValueError):
        create_compatible_dynamics("rk4")


def test_safety_wrapper_returns_finite_state():
    f = lambda t, x, u: np.array([x[1], -x[0]])
    safe = create_safe_integrator("rk4")
    out = safe.integrate(f, np.array([0.1, 0.0]), np.array([0.0]), 0.01)
    assert np.all(np.isfinite(out))


def test_safety_wrapper_falls_back_on_failure():
    class Bomb(ForwardEuler):
        def integrate(self, *a, **k):
            raise RuntimeError("boom")
    w = IntegratorSafetyWrapper(Bomb(), ForwardEuler())
    out = w.integrate(lambda t, x, u: np.array([1.0]), np.array([0.0]),
                      np.array([0.0]), 0.1)
    # fallback ForwardEuler: 0 + 0.1*1 = 0.1
    assert np.allclose(out, 0.1)


def test_legacy_dynamics_wrapper_estimates_derivative():
    class Legacy:
        def step(self, state, control, dt):
            # x' = control (constant) => next = state + dt*control
            return state + dt * control
    wrap = LegacyDynamicsWrapper(Legacy())
    deriv = wrap(0.0, np.array([1.0]), np.array([2.0]))
    assert np.allclose(deriv, 2.0, atol=1e-3)
