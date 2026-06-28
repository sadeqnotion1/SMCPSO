"""M4 Slice 2 - StateSpaceUtilities, incl. Trap A grouped-convention pin."""
import numpy as np
import pytest

from src.simulation.core.state_space import StateSpaceUtilities as S


def test_validate_dimensions_1d_2d():
    assert S.validate_state_dimensions(np.zeros(6), 6) is True
    assert S.validate_state_dimensions(np.zeros((10, 6)), 6) is True
    assert S.validate_state_dimensions(np.zeros(5), 6) is False


def test_normalize_batch_shapes():
    assert S.normalize_state_batch(np.zeros(6)).shape == (1, 1, 6)
    assert S.normalize_state_batch(np.zeros((10, 6))).shape == (1, 10, 6)
    assert S.normalize_state_batch(np.zeros((4, 10, 6))).shape == (4, 10, 6)
    with pytest.raises(ValueError):
        S.normalize_state_batch(np.zeros((2, 2, 2, 2)))


def test_extract_components():
    state = np.array([1, 2, 3, 4, 5, 6.0])
    out = S.extract_state_components(state, {"pos": slice(0, 3), "vx": 3})
    assert np.allclose(out["pos"], [1, 2, 3])
    assert out["vx"] == 4


def test_compute_energy_grouped_convention_trap_a():
    # CANONICAL GROUPED: [x, th1, th2, xdot, th1dot, th2dot]
    # Only the velocity block (second half) contributes to kinetic energy.
    state = np.array([10.0, 20.0, 30.0, 1.0, 2.0, 2.0])  # positions large, velocities small
    ke = S.compute_energy(state)  # unit mass -> 0.5*sum(v^2)
    assert np.isclose(ke, 0.5 * (1.0**2 + 2.0**2 + 2.0**2))  # = 4.5
    # Positions must NOT affect kinetic energy (guards against interleaved misread).
    state2 = np.array([999.0, -999.0, 0.0, 1.0, 2.0, 2.0])
    assert np.isclose(S.compute_energy(state2), ke)


def test_linearize_recovers_known_linear_system():
    # xdot = A x + B u  -> finite-diff Jacobians must recover A, B.
    A_true = np.array([[0.0, 1.0], [-2.0, -3.0]])
    B_true = np.array([[0.0], [1.0]])

    def dyn(x, u):
        return A_true @ x + B_true @ u

    A, B = S.linearize_about_equilibrium(dyn, np.zeros(2), np.zeros(1))
    assert np.allclose(A, A_true, atol=1e-6)
    assert np.allclose(B, B_true, atol=1e-6)


def test_compute_state_bounds():
    rng = np.random.default_rng(0)
    traj = rng.normal(size=(1000, 3))
    lo, hi = S.compute_state_bounds(traj, percentile=90.0)
    assert lo.shape == (3,) and hi.shape == (3,)
    assert np.all(lo < hi)
