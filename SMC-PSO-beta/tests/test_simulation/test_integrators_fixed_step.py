"""M4 Slice 3 - fixed-step integrators (Euler family + RK2/RK4/RK38)."""
import math
import numpy as np
import pytest

from src.simulation.integrators.fixed_step.euler import (
    ForwardEuler, BackwardEuler, ModifiedEuler,
)
from src.simulation.integrators.fixed_step.runge_kutta import (
    RungeKutta2, RungeKutta4, RungeKutta38, ClassicalRungeKutta,
)

U = np.array([0.0])


def _const(c):
    return lambda t, x, u: np.array([c])


def _linear(lam):
    return lambda t, x, u: lam * x


@pytest.mark.parametrize("cls", [ForwardEuler, RungeKutta2, RungeKutta4,
                                 RungeKutta38, ModifiedEuler])
def test_constant_derivative_is_exact(cls):
    integ = cls()
    x0 = np.array([1.0])
    out = integ.integrate(_const(3.0), x0, U, 0.1)
    assert np.allclose(out, x0 + 0.1 * 3.0)


def test_forward_euler_formula():
    out = ForwardEuler().integrate(_linear(-0.7), np.array([2.0]), U, 0.05)
    assert np.allclose(out, 2.0 * (1 + (-0.7) * 0.05))


def test_rk4_matches_exponential_high_accuracy():
    lam, dt = -0.7, 0.05
    out = RungeKutta4().integrate(_linear(lam), np.array([1.0]), U, dt)
    assert np.allclose(out, math.exp(lam * dt), atol=1e-8)


def test_rk2_second_order_accuracy():
    lam, dt = -0.7, 0.05
    out = RungeKutta2().integrate(_linear(lam), np.array([1.0]), U, dt)
    assert np.allclose(out, math.exp(lam * dt), atol=1e-4)
    # but RK2 is less accurate than RK4
    err_rk2 = abs(out[0] - math.exp(lam * dt))
    err_rk4 = abs(RungeKutta4().integrate(_linear(lam), np.array([1.0]), U, dt)[0]
                  - math.exp(lam * dt))
    assert err_rk4 < err_rk2


def test_rk38_is_fourth_order():
    assert RungeKutta38().order == 4
    lam, dt = -0.5, 0.05
    out = RungeKutta38().integrate(_linear(lam), np.array([1.0]), U, dt)
    assert np.allclose(out, math.exp(lam * dt), atol=1e-8)


def test_classical_rk_is_rk4_alias():
    assert issubclass(ClassicalRungeKutta, RungeKutta4)


def test_orders_and_adaptive_flags():
    assert ForwardEuler().order == 1 and ForwardEuler().adaptive is False
    assert RungeKutta2().order == 2
    assert RungeKutta4().order == 4
    assert ModifiedEuler().order == 2
    assert BackwardEuler().order == 1


def test_backward_euler_implicit_linear():
    # y' = -y  =>  backward Euler: x_new = x/(1+dt)
    dt = 0.5
    out = BackwardEuler().integrate(_linear(-1.0), np.array([2.0]), U, dt)
    assert np.allclose(out, 2.0 / (1 + dt), atol=1e-6)


def test_validate_inputs_rejects_bad_dt():
    with pytest.raises(ValueError):
        RungeKutta4().integrate(_const(1.0), np.array([1.0]), U, -0.1)


def test_statistics_track_function_evaluations():
    integ = RungeKutta4()
    integ.integrate(_const(1.0), np.array([1.0]), U, 0.1)
    stats = integ.get_statistics()
    assert stats["total_steps"] == 1
    assert stats["function_evaluations"] == 4  # RK4 uses 4 evals
