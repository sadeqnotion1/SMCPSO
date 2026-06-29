"""M4 Slice 3 - adaptive integration + error control.

Resolves the carried watch-item S2-2: the adaptive integrator path is
ORDER-AWARE (exponent 1/order), unlike the standalone AdaptiveTimeStep in
core/time_domain.py which hard-codes 1/4.
"""
import math
import numpy as np
import pytest

from src.simulation.integrators.adaptive.runge_kutta import (
    AdaptiveRungeKutta, DormandPrince45, rk45_step, _original_rk45_step,
)
from src.simulation.integrators.adaptive.error_control import (
    ErrorController, PIController, DeadBeatController,
)

U = np.array([0.0])


class _BareAdaptive(AdaptiveRungeKutta):
    """Concrete subclass that does NOT override _adaptive_step."""
    @property
    def order(self):
        return 5
    @property
    def adaptive(self):
        return True


def test_dp45_order_and_adaptive():
    dp = DormandPrince45()
    assert dp.order == 5
    assert dp.adaptive is True


def test_adaptive_base_step_is_abstract():
    with pytest.raises(NotImplementedError):
        _BareAdaptive()._adaptive_step(lambda t, y: y, 0.0, np.array([1.0]), 0.1)


def test_dp45_matches_exponential():
    lam, dt = -0.7, 0.05
    out = DormandPrince45().integrate(lambda t, x, u: lam * x, np.array([1.0]), U, dt)
    assert np.allclose(out, math.exp(lam * dt), atol=1e-10)


def test_dp45_state_parity_with_legacy_rk45_step():
    # For an ACCEPTED step, the propagated 5th-order state must match the legacy
    # standalone rk45_step exactly (same Dormand-Prince formula).
    A = np.array([[0.0, 1.0], [-2.0, -3.0]])
    y = np.array([0.3, -0.2])
    dt = 1e-3  # small => accepted

    def f(t, yy):
        return A @ yy

    y_new_legacy, _ = _original_rk45_step(f, 0.0, y, dt, 1e-9, 1e-6)
    out = DormandPrince45().integrate(lambda t, x, u: A @ x, y, U, dt)
    assert y_new_legacy is not None
    assert np.allclose(out, y_new_legacy, atol=1e-12)


def test_rk45_step_wrapper_returns_state():
    A = np.array([[0.0, 1.0], [-2.0, -3.0]])
    y = np.array([0.3, -0.2])

    def f(t, yy):
        return A @ yy

    y_new, dt_new = rk45_step(f, 0.0, y, 1e-3, 1e-9, 1e-6)
    assert y_new is not None and dt_new > 0


# ---- ErrorController: the S2-2 fix lives here (order-aware) ----

def test_error_controller_accepts_below_tolerance():
    new_dt, accept = ErrorController().update_step_size(0.5, 0.1, 1e-12, 1.0, order=5)
    assert accept is True and new_dt > 0


def test_error_controller_rejects_above_tolerance():
    new_dt, accept = ErrorController().update_step_size(2.0, 0.1, 1e-12, 1.0, order=5)
    assert accept is False and new_dt < 0.1


def test_error_controller_is_order_aware():
    # SAME error, DIFFERENT method order -> DIFFERENT growth factor (1/order exponent).
    ec = ErrorController(safety_factor=0.9)
    dt5, _ = ec.update_step_size(0.5, 0.1, 1e-12, 10.0, order=5)
    dt2, _ = ec.update_step_size(0.5, 0.1, 1e-12, 10.0, order=2)
    # factor = 0.9*(1/0.5)^(1/order); higher order -> smaller exponent -> smaller factor
    assert not np.isclose(dt5, dt2)
    assert dt5 < dt2
    # cross-check exact formula
    assert np.isclose(dt5, 0.1 * 0.9 * (1.0 / 0.5) ** (1.0 / 5))
    assert np.isclose(dt2, 0.1 * 0.9 * (1.0 / 0.5) ** (1.0 / 2))


def test_error_controller_zero_error_grows():
    new_dt, accept = ErrorController().update_step_size(0.0, 0.1, 1e-12, 1.0, order=5)
    assert accept is True and np.isclose(new_dt, min(0.2, 1.0))


def test_pi_controller_history_and_reset():
    pi = PIController()
    pi.update_step_size(0.5, 0.1, 1e-12, 1.0, order=5)
    assert pi._previous_error == 0.5
    pi.reset()
    assert pi._previous_error is None


def test_deadbeat_controller_runs():
    db = DeadBeatController(target_error=0.1)
    new_dt, accept = db.update_step_size(0.05, 0.1, 1e-12, 1.0, order=5)
    assert accept is True and new_dt > 0
