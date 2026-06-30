#======================================================================================
#===================== tests/test_controllers/test_adaptive_smc.py ====================
#======================================================================================
"""Unit tests for the ported adaptive SMC (M5 Slice 3).

Grouped state [x, th1, th2, xdot, th1dot, th2dot]:
    sigma = k1*(th1dot + lam1*th1) + k2*(th2dot + lam2*th2)
Control law (continuous boundary layer + proportional term):
    sw  = sat(sigma/eps)
    u   = -K*sw - alpha*sigma            (clamped +/- max_force)
Gain adaptation (dead-zone gated, leaky, rate-limited):
    dK  = 0                              if |sigma| <= dead_zone
    dK  = gamma*|sigma| - leak*(K-K0)    otherwise
    dK  = clip(dK, +/- adapt_rate_limit)
    K^+ = clip(K + dK*dt, K_min, K_max)
Gains order: [k1, k2, lam1, lam2, gamma] (n_gains=5; extras tolerated).
"""
import numpy as np
import pytest

from src.controllers.adaptive_smc import AdaptiveSMC
from src.utils import AdaptiveSMCOutput, saturate

GAINS = [5.0, 3.0, 2.0, 1.0, 4.0]  # k1,k2,lam1,lam2,gamma


def make(gains=None, **kw):
    kw.setdefault("dt", 0.01)
    kw.setdefault("max_force", 150.0)
    kw.setdefault("leak_rate", 0.01)
    kw.setdefault("adapt_rate_limit", 10.0)
    kw.setdefault("K_min", 0.1)
    kw.setdefault("K_max", 100.0)
    kw.setdefault("smooth_switch", True)
    kw.setdefault("boundary_layer", 0.4)
    kw.setdefault("dead_zone", 0.05)
    return AdaptiveSMC(gains if gains is not None else GAINS, **kw)


# --------------------------------------------------------------------- gains
def test_n_gains_and_storage():
    c = make()
    assert c.n_gains == 5
    assert c.gains == GAINS
    g = c.gains
    g[0] = 999.0
    assert c.gains[0] == GAINS[0]  # property returns a copy


def test_gain_unpacking():
    c = make()
    assert (c.k1, c.k2, c.lam1, c.lam2, c.gamma) == (5.0, 3.0, 2.0, 1.0, 4.0)


def test_extra_gains_tolerated_but_only_first_five_used():
    c = make([5.0, 3.0, 2.0, 1.0, 4.0, 7.0, 8.0])
    assert c.gains == [5.0, 3.0, 2.0, 1.0, 4.0, 7.0, 8.0]
    assert (c.k1, c.k2, c.lam1, c.lam2, c.gamma) == (5.0, 3.0, 2.0, 1.0, 4.0)


def test_validate_gains_is_static_and_rejects_too_few():
    with pytest.raises(ValueError):
        AdaptiveSMC.validate_gains([1, 2, 3, 4])
    with pytest.raises(ValueError):
        make([1, 2, 3, 4])


def test_nonpositive_surface_gains_rejected():
    for bad in ([0, 3, 2, 1, 4], [5, 0, 2, 1, 4], [5, 3, -1, 1, 4],
                [5, 3, 2, 0, 4], [5, 3, 2, 1, 0]):
        with pytest.raises(ValueError):
            make(bad)


def test_required_positive_params():
    with pytest.raises(ValueError):
        make(dt=0.0)
    with pytest.raises(ValueError):
        make(max_force=0.0)
    with pytest.raises(ValueError):
        make(K_min=0.0)
    with pytest.raises(ValueError):
        make(K_max=0.0)
    with pytest.raises(ValueError):
        make(boundary_layer=0.0)
    # negative values rejected even where zero is allowed
    with pytest.raises(ValueError):
        make(leak_rate=-0.1)
    with pytest.raises(ValueError):
        make(adapt_rate_limit=-1.0)
    with pytest.raises(ValueError):
        make(dead_zone=-0.1)


def test_zero_allowed_params_ok():
    c = make(leak_rate=0.0, adapt_rate_limit=0.0, dead_zone=0.0)
    assert c.leak_rate == 0.0 and c.adapt_rate_limit == 0.0 and c.dead_zone == 0.0


def test_K_envelope_validation():
    with pytest.raises(ValueError):
        make(K_min=0.1, K_max=100.0, K_init=200.0)  # K_init > K_max
    with pytest.raises(ValueError):
        make(K_min=20.0, K_max=100.0, K_init=10.0)   # K_init < K_min


# ---------------------------------------------------------- sliding surface
def test_sliding_surface_formula():
    c = make()
    state = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    out = c.compute_control(state, (10.0, 0.0, 0.0), {})
    # 5*(0.5+2*0.2) + 3*(0.6+1*0.3) = 4.5 + 2.7 = 7.2
    assert out.sigma == pytest.approx(7.2)


def test_grouped_state_convention_trap_a():
    c = make()
    only_cart = np.array([1.0, 0.0, 0.0, 2.0, 0.0, 0.0])
    assert c.compute_control(only_cart, (10.0, 0.0, 0.0), {}).sigma == pytest.approx(0.0)
    only_th1 = np.array([0.0, 0.5, 0.0, 0.0, 0.0, 0.0])
    assert c.compute_control(only_th1, (10.0, 0.0, 0.0), {}).sigma == pytest.approx(5.0 * (2.0 * 0.5))


# ----------------------------------------------------------- compute_control
def test_output_type_and_state_shape():
    c = make()
    out = c.compute_control(np.array([0.0, 0.1, 0.2, 0.0, 0.3, 0.4]), (10.0, 0.0, 0.0), {})
    assert isinstance(out, AdaptiveSMCOutput)
    assert np.isfinite(out.u) and abs(out.u) <= 150.0 + 1e-9
    new_K, u_prev, t_in = out.state
    assert np.isfinite(new_K) and np.isfinite(t_in)
    assert u_prev == pytest.approx(out.u)


def test_control_law_matches_reference():
    for smooth in (True, False):
        c = make(smooth_switch=smooth, max_force=1e6, alpha=0.5)
        state = np.array([0.0, 0.15, -0.2, 0.0, 0.4, -0.3])
        K0 = 12.0
        out = c.compute_control(state, (K0, 0.0, 0.0), {})
        sigma = out.sigma
        sw = saturate(sigma, c.boundary_layer, method="tanh" if smooth else "linear")
        u_sw = -K0 * sw
        exp_u = float(np.clip(u_sw - c.alpha * sigma, -1e6, 1e6))
        assert out.u == pytest.approx(exp_u, abs=1e-12)
        assert out.history["u_sw"][-1] == pytest.approx(u_sw, abs=1e-12)


def test_adaptation_outside_dead_zone():
    c = make(dead_zone=0.05, leak_rate=0.2, adapt_rate_limit=1e6, K_min=0.1, K_max=1e6)
    state = np.array([0.0, 0.3, 0.2, 0.0, 0.5, 0.4])
    K0 = 15.0
    out = c.compute_control(state, (K0, 0.0, 0.0), {})
    sigma = out.sigma
    assert abs(sigma) > c.dead_zone
    dK = c.gamma * abs(sigma) - c.leak_rate * (K0 - c.K_init)
    exp_K = float(np.clip(K0 + dK * c.dt, c.K_min, c.K_max))
    assert out.state[0] == pytest.approx(exp_K, abs=1e-12)
    assert out.history["dK"][-1] == pytest.approx(dK, abs=1e-12)


def test_adaptation_frozen_inside_dead_zone():
    c = make(dead_zone=1.0)
    state = np.zeros(6)  # sigma = 0 -> inside dead zone
    K0 = 7.0
    out = c.compute_control(state, (K0, 0.0, 0.0), {})
    assert out.history["dK"][-1] == pytest.approx(0.0)
    assert out.state[0] == pytest.approx(K0)  # K held constant


def test_adapt_rate_limit_clamps_growth():
    c = make(dead_zone=0.0, leak_rate=0.0, adapt_rate_limit=0.5)
    state = np.array([0.0, 1.5, 1.5, 0.0, 2.0, 2.0])  # large sigma -> big raw dK
    out = c.compute_control(state, (10.0, 0.0, 0.0), {})
    assert out.history["dK"][-1] == pytest.approx(0.5, abs=1e-12)  # clipped to +limit


def test_K_clamped_to_K_max():
    c = make(K_max=15.0, dead_zone=0.0, leak_rate=0.0, adapt_rate_limit=1e6, dt=1.0)
    state = np.array([0.0, 1.0, 1.0, 0.0, 2.0, 2.0])
    out = c.compute_control(state, (14.5, 0.0, 0.0), {})
    assert out.state[0] == pytest.approx(15.0)  # clamped at K_max


def test_time_in_sliding_counter():
    c = make(boundary_layer=0.5)
    inside = np.array([0.0, 0.01, 0.0, 0.0, 0.0, 0.0])  # tiny sigma < boundary_layer
    out_in = c.compute_control(inside, (10.0, 0.0, 3.0), {})
    assert out_in.state[2] == pytest.approx(3.0 + c.dt)
    outside = np.array([0.0, 1.0, 1.0, 0.0, 2.0, 2.0])  # large sigma
    out_out = c.compute_control(outside, (10.0, 0.0, 3.0), {})
    assert out_out.state[2] == pytest.approx(0.0)


def test_history_keys_present():
    c = make()
    out = c.compute_control(np.array([0.0, 0.1, 0.1, 0.0, 0.2, 0.2]), (10.0, 0.0, 0.0), {})
    for k in ("K", "sigma", "u_sw", "dK", "time_in_sliding"):
        assert k in out.history and len(out.history[k]) == 1


def test_state_vars_legacy_unpacking():
    c = make()
    s = np.array([0.0, 0.1, 0.1, 0.0, 0.2, 0.2])
    # scalar K
    assert np.isfinite(c.compute_control(s, 8.0, {}).u)
    # empty -> defaults to K_init
    out_empty = c.compute_control(s, (), {})
    assert np.isfinite(out_empty.u)
    # 2-tuple and over-long tuple both accepted
    assert np.isfinite(c.compute_control(s, (8.0, 1.0), {}).u)
    assert np.isfinite(c.compute_control(s, (8.0, 1.0, 2.0, 9.0), {}).u)


def test_initialize_state_and_history():
    c = make(K_init=10.0)
    assert c.initialize_state() == (10.0, 0.0, 0.0)
    h = c.initialize_history()
    assert set(h.keys()) == {"K", "sigma", "u_sw", "dK", "time_in_sliding"}
    assert all(v == [] for v in h.values())


def test_reset_cleanup_set_dynamics_safe():
    c = make()
    c.reset()
    c.cleanup()
    c.set_dynamics(object())


def test_no_citation_tokens_and_no_src_core():
    import src.controllers.adaptive_smc as mod
    text = open(mod.__file__, encoding="utf-8").read()
    assert "\u3010" not in text and "\u3011" not in text  # Trap E
    assert "src.core" not in text                          # Trap B
    assert "from ...utils" not in text                      # relocation
