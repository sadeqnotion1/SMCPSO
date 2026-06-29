#======================================================================================
#======================= tests/test_controllers/test_sta_smc.py =======================
#======================================================================================
"""Unit tests for the ported super-twisting SMC (M5 Slice 2).

Grouped state [x, th1, th2, xdot, th1dot, th2dot]:
    sigma = k1*(th1dot + lam1*th1) + k2*(th2dot + lam2*th2)
Control (super-twisting, 2nd-order sliding):
    sgn   = sat(sigma/eps)
    u     = u_eq - K1*sqrt(|sigma|)*sgn + z - d*sigma      (clamped +/- max_force)
    z^+   = z - K2*sgn*dt + Kaw*(u_sat - u_raw)*dt          (clamped +/- max_force)
Gains order: [K1, K2, k1, k2, lam1, lam2] (length 2 -> default surface gains).
"""
import numpy as np
import pytest

from src.controllers.sta_smc import SuperTwistingSMC
from src.utils import STAOutput, saturate

GAINS = [8.0, 4.0, 5.0, 3.0, 2.0, 1.0]  # K1,K2,k1,k2,lam1,lam2


def make(gains=None, **kw):
    kw.setdefault("dt", 0.01)
    kw.setdefault("max_force", 150.0)
    kw.setdefault("boundary_layer", 0.3)
    return SuperTwistingSMC(gains if gains is not None else GAINS, **kw)


class MockDyn:
    def _compute_physics_matrices(self, state):
        M = np.array([[2.0, 0.5, 0.3], [0.5, 1.5, 0.2], [0.3, 0.2, 1.0]])
        C = np.zeros(3)
        G = np.array([0.0, 1.2, 0.8])
        return M, C, G


# --------------------------------------------------------------------- gains
def test_two_gains_apply_surface_defaults():
    c = SuperTwistingSMC([8.0, 4.0], dt=0.01)
    assert (c.surf_gain_k1, c.surf_gain_k2, c.surf_lam1, c.surf_lam2) == (5.0, 3.0, 2.0, 1.0)
    assert c.alg_gain_K1 == 8.0 and c.alg_gain_K2 == 4.0
    assert c.n_gains == 6
    assert c.gains == [8.0, 4.0]


def test_six_gains_explicit():
    c = make()
    assert (c.alg_gain_K1, c.alg_gain_K2) == (8.0, 4.0)
    assert (c.surf_gain_k1, c.surf_gain_k2, c.surf_lam1, c.surf_lam2) == (5.0, 3.0, 2.0, 1.0)


def test_invalid_gain_length():
    with pytest.raises(ValueError):
        make([1, 2, 3])
    with pytest.raises(ValueError):
        make([1, 2, 3, 4, 5])


def test_nonpositive_gains_rejected():
    for bad in ([0, 4, 5, 3, 2, 1], [8, 0, 5, 3, 2, 1], [8, 4, -1, 3, 2, 1],
                [8, 4, 5, 0, 2, 1], [8, 4, 5, 3, -2, 1], [8, 4, 5, 3, 2, 0]):
        with pytest.raises(ValueError):
            make(bad)


def test_dt_max_force_boundary_switch_validation():
    with pytest.raises(ValueError):
        make(dt=0.0)
    with pytest.raises(ValueError):
        make(dt=-0.01)
    with pytest.raises(ValueError):
        make(max_force=0.0)
    with pytest.raises(ValueError):
        make(boundary_layer=0.0)
    with pytest.raises(ValueError):
        make(switch_method="bogus")


def test_gains_property_is_copy():
    c = make()
    g = c.gains
    g[0] = 999.0
    assert c.gains[0] == GAINS[0]


# ---------------------------------------------------------- sliding surface
def test_sliding_surface_formula():
    c = make()
    state = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    # 5*(0.5+2*0.2) + 3*(0.6+1*0.3) = 4.5 + 2.7 = 7.2
    assert c._compute_sliding_surface(state) == pytest.approx(7.2)


def test_grouped_state_convention_trap_a():
    c = make()
    only_cart = np.array([1.0, 0.0, 0.0, 2.0, 0.0, 0.0])
    assert c._compute_sliding_surface(only_cart) == pytest.approx(0.0)
    only_th1 = np.array([0.0, 0.5, 0.0, 0.0, 0.0, 0.0])
    assert c._compute_sliding_surface(only_th1) == pytest.approx(5.0 * (2.0 * 0.5))


# ----------------------------------------------------------- compute_control
def test_output_type_and_state_shape():
    c = make()
    out = c.compute_control(np.array([0.0, 0.1, 0.2, 0.0, 0.3, 0.4]), (0.0, 0.0), {})
    assert isinstance(out, STAOutput)
    assert isinstance(out.u, float)
    assert abs(out.u) <= 150.0 + 1e-9
    new_z, sig = out.state
    assert np.isfinite(new_z) and np.isfinite(sig)
    assert out.sigma == pytest.approx(sig)


def test_super_twisting_law_matches_reference():
    for method in ("tanh", "linear"):
        c = make(switch_method=method, max_force=1e6, damping_gain=0.0)
        state = np.array([0.0, 0.15, -0.2, 0.0, 0.4, -0.3])
        out = c.compute_control(state, (0.0, 0.0), {})
        sigma = c._compute_sliding_surface(state)
        sgn = saturate(sigma, 0.3, method=method)
        exp_u = -c.alg_gain_K1 * np.sqrt(abs(sigma)) * sgn  # u_eq=0, z=0, d=0
        exp_z = -c.alg_gain_K2 * sgn * c.dt
        assert out.u == pytest.approx(exp_u, abs=1e-12)
        assert out.state[0] == pytest.approx(exp_z, abs=1e-12)


def test_integrator_state_advances():
    c = make(max_force=1e6)
    state = np.array([0.0, 0.1, 0.0, 0.0, 0.2, 0.0])
    sigma = c._compute_sliding_surface(state)
    sgn = saturate(sigma, 0.3, method=c.switch_method)
    z0 = 2.0
    out = c.compute_control(state, (z0, 0.0), {})
    assert out.state[0] == pytest.approx(z0 - c.alg_gain_K2 * sgn * c.dt, abs=1e-12)


def test_anti_windup_backcalculation():
    c = make(max_force=1.0, anti_windup_gain=2.0)  # tiny limit forces saturation
    state = np.array([0.0, 0.5, 0.4, 0.0, 0.6, 0.5])
    z0 = 0.3
    out = c.compute_control(state, (z0, 0.0), {})
    sigma = c._compute_sliding_surface(state)
    sgn = saturate(sigma, 0.3, method=c.switch_method)
    u_raw = -c.alg_gain_K1 * np.sqrt(abs(sigma)) * sgn + z0
    u_sat = float(np.clip(u_raw, -1.0, 1.0))
    exp_z = z0 - c.alg_gain_K2 * sgn * c.dt + 2.0 * (u_sat - u_raw) * c.dt
    exp_z = float(np.clip(exp_z, -1.0, 1.0))
    assert out.u == pytest.approx(u_sat, abs=1e-12)
    assert out.state[0] == pytest.approx(exp_z, abs=1e-12)


def test_scalar_state_vars_legacy_accepted():
    c = make()
    out = c.compute_control(np.array([0.0, 0.1, 0.1, 0.0, 0.1, 0.1]), 0.5, {})
    assert isinstance(out, STAOutput) and np.isfinite(out.u)


def test_equivalent_control_with_mock_dynamics():
    c = make(max_force=1e6)
    c.dyn = MockDyn()
    out = c.compute_control(np.array([0.05, 0.1, -0.05, 0.0, 0.3, -0.2]), (0.0, 0.0), {})
    assert np.isfinite(out.u)
    assert "u_eq" in out.history and np.isfinite(out.history["u_eq"][-1])


def test_validate_gains_vectorized():
    c = make()
    cand = np.array([
        [8.0, 4.0, 5.0, 3.0, 2.0, 1.0],   # ok: K1>K2>0, surface positive
        [4.0, 8.0, 5.0, 3.0, 2.0, 1.0],   # bad: K1 < K2
        [8.0, 4.0, -1.0, 3.0, 2.0, 1.0],  # bad: surface gain <= 0
    ])
    mask = c.validate_gains(cand)
    assert list(mask) == [True, False, False]


def test_history_keys_present():
    c = make()
    out = c.compute_control(np.array([0.0, 0.1, 0.1, 0.0, 0.2, 0.2]), (0.0, 0.0), {})
    for k in ("sigma", "z", "u", "u_eq"):
        assert k in out.history and len(out.history[k]) == 1


def test_reset_cleanup_and_init():
    c = make()
    c.reset()
    c.cleanup()
    assert c.initialize_state() == (0.0, 0.0)
    assert c.initialize_history() == {}


def test_no_citation_tokens_and_no_src_core():
    import src.controllers.sta_smc as mod
    text = open(mod.__file__, encoding="utf-8").read()
    assert "\u3010" not in text and "\u3011" not in text  # Trap E
    assert "src.core" not in text  # Trap B
    assert "from ...utils" not in text  # relocation
