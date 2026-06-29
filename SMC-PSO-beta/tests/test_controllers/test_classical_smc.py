#======================================================================================
#==================== tests/test_controllers/test_classical_smc.py ====================
#======================================================================================
"""Unit tests for the ported classical SMC (M5 Slice 1).

Control law (grouped state [x, th1, th2, xdot, dth1, dth2]):
    sigma = lam1*th1 + lam2*th2 + k1*dth1 + k2*dth2
    u = u_eq - K*sat(sigma/eps) - kd*sigma,  clipped to +/- max_force
Gains order: [k1, k2, lam1, lam2, K, kd].
"""
import numpy as np
import pytest

from src.controllers.classical_smc import ClassicalSMC
from src.utils import ClassicalSMCOutput

GAINS = [2.0, 3.0, 4.0, 5.0, 10.0, 1.0]  # k1,k2,lam1,lam2,K,kd


def make(gains=None, **kw):
    kw.setdefault("max_force", 50.0)
    kw.setdefault("boundary_layer", 0.3)
    return ClassicalSMC(gains if gains is not None else GAINS, **kw)


class MockDyn:
    """Minimal dynamics model exposing _compute_physics_matrices(state)."""
    def _compute_physics_matrices(self, state):
        M = np.array([[2.0, 0.5, 0.3], [0.5, 1.5, 0.2], [0.3, 0.2, 1.0]])
        C = np.zeros(3)
        G = np.array([0.0, 1.2, 0.8])
        return M, C, G


# ----------------------------------------------------------------------- gains
def test_validate_gains_requires_six():
    with pytest.raises(ValueError):
        ClassicalSMC.validate_gains([1, 2, 3])
    with pytest.raises(ValueError):
        ClassicalSMC.validate_gains([1, 2, 3, 4, 5, 6, 7])
    ClassicalSMC.validate_gains([1, 2, 3, 4, 5, 6])  # no raise


def test_constructor_rejects_nonpositive_gains():
    for bad in ([0, 3, 4, 5, 10, 1], [2, 3, -4, 5, 10, 1], [2, 3, 4, 5, 0, 1]):
        with pytest.raises(ValueError):
            make(bad)


def test_kd_may_be_zero_but_not_negative():
    make([2, 3, 4, 5, 10, 0.0])  # ok
    with pytest.raises(ValueError):
        make([2, 3, 4, 5, 10, -0.1])


def test_boundary_layer_and_switch_validation():
    with pytest.raises(ValueError):
        make(boundary_layer=0.0)
    with pytest.raises(ValueError):
        make(switch_method="bogus")
    with pytest.raises(ValueError):
        make(hysteresis_ratio=1.5)
    with pytest.raises(ValueError):
        make(boundary_layer_slope=-1.0)


def test_gains_property_is_copy():
    c = make()
    g = c.gains
    g[0] = 999.0
    assert c.gains[0] == GAINS[0]
    assert c.n_gains == 6


# ------------------------------------------------------------- sliding surface
def test_sliding_surface_formula():
    c = make()
    state = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    # lam1*th1+lam2*th2+k1*dth1+k2*dth2 = 4*.2+5*.3+2*.5+3*.6 = 5.1
    assert c._compute_sliding_surface(state) == pytest.approx(5.1)


def test_grouped_state_convention_trap_a():
    """Confirms canonical GROUPED ordering: x and xdot do NOT enter sigma."""
    c = make()
    only_cart = np.array([1.0, 0.0, 0.0, 2.0, 0.0, 0.0])
    assert c._compute_sliding_surface(only_cart) == pytest.approx(0.0)
    only_th1 = np.array([0.0, 0.5, 0.0, 0.0, 0.0, 0.0])
    assert c._compute_sliding_surface(only_th1) == pytest.approx(4.0 * 0.5)


# -------------------------------------------------------------- compute_control
def test_output_type_and_saturation():
    c = make(max_force=20.0)
    out = c.compute_control(np.array([0.1, 0.2, 0.3, 0.0, 0.0, 0.0]), (), {})
    assert isinstance(out, ClassicalSMCOutput)
    assert isinstance(out.u, float)
    assert abs(out.u) <= 20.0 + 1e-9
    # huge surface -> clamp at max_force
    big = c.compute_control(np.array([0.0, 100.0, 100.0, 0.0, 0.0, 0.0]), (), {})
    assert abs(big.u) == pytest.approx(20.0)


def test_equivalent_control_zero_without_dynamics():
    c = make(max_force=100.0)
    state = np.array([0.0, 0.1, -0.1, 0.0, 0.2, -0.2])
    out = c.compute_control(state, (), {})
    sigma = c._compute_sliding_surface(state)
    sat = np.tanh((sigma / 0.3) / 3.0)
    expected = float(np.clip(-c.K * sat - c.kd * sigma, -100.0, 100.0))
    assert out.u == pytest.approx(expected, abs=1e-12)


def test_hysteresis_suppresses_robust_term():
    c = make([1, 1, 1, 1, 10, 2], max_force=100.0,
             boundary_layer=1.0, hysteresis_ratio=0.5)
    state = np.array([0.0, 0.05, 0.0, 0.0, 0.0, 0.0])  # sigma = 0.05 < 0.5
    out = c.compute_control(state, (), {})
    # robust K-term frozen; only -kd*sigma remains
    assert out.u == pytest.approx(-2.0 * 0.05, abs=1e-12)


def test_tanh_and_linear_both_run_and_differ():
    state = np.array([0.0, 0.4, 0.3, 0.0, 0.2, 0.1])
    ut = make(switch_method="tanh").compute_control(state, (), {}).u
    ul = make(switch_method="linear").compute_control(state, (), {}).u
    assert np.isfinite(ut) and np.isfinite(ul)
    assert ut != ul


def test_equivalent_control_with_mock_dynamics():
    c = make(max_force=100.0)
    c.dyn = MockDyn()
    state = np.array([0.05, 0.1, -0.05, 0.0, 0.3, -0.2])
    out = c.compute_control(state, (), {})
    assert np.isfinite(out.u)
    assert abs(out.u) <= 100.0 + 1e-9
    assert "u_eq" in out.history and np.isfinite(out.history["u_eq"][-1])


def test_reset_and_cleanup_are_safe():
    c = make()
    c.reset()
    c.cleanup()
    assert c.initialize_state() == ()
    assert c.initialize_history() == {}


# ------------------------------------------------------------------ port hygiene
def test_no_citation_tokens_and_no_src_core():
    import src.controllers.classical_smc as mod
    text = open(mod.__file__, encoding="utf-8").read()
    assert "\u3010" not in text and "\u3011" not in text  # Trap E
    assert "src.core" not in text  # Trap B
    assert "from ...utils" not in text and "from ...plant" not in text  # relocation
