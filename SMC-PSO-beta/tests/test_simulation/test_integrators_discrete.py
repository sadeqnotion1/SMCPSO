"""M4 Slice 3 - zero-order-hold discretization."""
import math
import numpy as np
import pytest

from src.simulation.integrators.discrete.zero_order_hold import ZeroOrderHold
from src.simulation.integrators.fixed_step.runge_kutta import RungeKutta4


def test_order_and_adaptive():
    z = ZeroOrderHold()
    assert z.order == float("inf")  # exact for LTI (documented type caveat S3-4)
    assert z.adaptive is False


def test_zoh_diagonal_matches_closed_form():
    # Diagonal A -> Ad = diag(exp(a_ii * dt)); independent closed-form check.
    A = np.diag([-1.0, -2.0])
    B = np.array([[1.0], [0.0]])
    dt = 0.1
    z = ZeroOrderHold()
    z.set_linear_system(A, B, dt)
    Ad, Bd = z.get_discrete_matrices()
    assert np.allclose(np.diag(Ad), [math.exp(-1.0 * dt), math.exp(-2.0 * dt)])


def test_zoh_is_exact_vs_fine_rk4():
    # ZOH is exact for LTI with constant control; a fine RK4 sub-integration must
    # converge to the SAME next state (validates Ad,Bd independent of expm trust).
    A = np.array([[0.0, 1.0], [-2.0, -3.0]])
    B = np.array([[0.0], [1.0]])
    dt = 0.1
    x0 = np.array([0.5, -0.3])
    u = np.array([0.7])

    z = ZeroOrderHold()
    z.set_linear_system(A, B, dt)
    x_zoh = z.integrate(lambda t, x, c: A @ x + B @ c, x0, u, dt)

    # reference: many small RK4 steps of x' = A x + B u, u held constant
    rk4 = RungeKutta4()
    n = 2000
    h = dt / n
    x = x0.copy()
    f = lambda t, xx, c: A @ xx + B @ c
    for _ in range(n):
        x = rk4.integrate(f, x, u, h)
    assert np.allclose(x_zoh, x, atol=1e-6)


def test_zoh_nonlinear_fallback_matches_rk4():
    # With no linear matrices set, ZOH falls back to an RK4 step.
    f = lambda t, x, u: np.array([x[1], -math.sin(x[0]) + u[0]])
    x0 = np.array([0.2, 0.0])
    u = np.array([0.1])
    dt = 0.01
    z = ZeroOrderHold()
    out_zoh = z.integrate(f, x0, u, dt)
    out_rk4 = RungeKutta4().integrate(f, x0, u, dt)
    assert np.allclose(out_zoh, out_rk4)


def test_zoh_simulate_sequence_shape():
    A = np.diag([-1.0, -2.0])
    B = np.array([[1.0], [1.0]])
    dt = 0.1
    z = ZeroOrderHold()
    z.set_linear_system(A, B, dt)
    traj = z.simulate_discrete_sequence(np.array([1.0, 1.0]), np.array([0.0]), horizon=5)
    assert traj.shape == (6, 2)


def test_zoh_requires_matrices_for_sequence():
    with pytest.raises(ValueError):
        ZeroOrderHold().simulate_discrete_sequence(np.array([1.0]), np.array([0.0]), 3)
