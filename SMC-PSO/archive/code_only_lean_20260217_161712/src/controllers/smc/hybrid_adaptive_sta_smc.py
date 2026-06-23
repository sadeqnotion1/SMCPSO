#======================================================================================\
#=================== src/controllers/smc/hybrid_adaptive_sta_smc.py ===================\
#======================================================================================\

from __future__ import annotations
from typing import Dict, Tuple, Any, List, Optional

import logging
import numpy as np
import weakref

from ...utils import HybridSTAOutput

logger = logging.getLogger(__name__)


def _sat_tanh(x: float, width: float) -> float:
    """Smooth sign via tanh with width>0; behaves like sign(x) for |x|>>width."""
    w = max(float(width), 1e-9)
    return float(np.tanh(x / w))


class HybridAdaptiveSTASMC:
    """
    Hybrid Adaptive Super–Twisting SMC for a double‑inverted pendulum.

    This controller combines an adaptive gain law with a second‑order
    sliding‑mode algorithm.

    Control law:
        ``u = −k1 * sqrt(|s|) * sat(s) + u_int − k_d * s + u_eq``
        ``u̇_int = −k2 * sat(s)``

    The controller includes an emergency reset mechanism to handle numerical
    instabilities and runaway adaptation.
    """

    n_gains: int = 4  # [c1, λ1, c2, λ2]

    # Numerical constants for stability and safety
    _TIKHONOV_REGULARIZATION: float = 1e-10  # Matrix inversion regularization
    _MIN_DENOMINATOR: float = 1e-6  # Safe division threshold
    _EQUIV_CONTROL_CLAMP_MULTIPLIER: float = 10.0  # u_eq clamp = multiplier * max_force
    _HARD_SATURATION_EPSILON: float = 1e-12  # Hard saturation check tolerance
    _MIN_DT_EPSILON: float = 1e-12  # Minimum safe timestep
    _TIME_TAPER_DECAY_RATE: float = 0.01  # Time-based adaptation tapering
    _TIME_TAPER_STEP_THRESHOLD: int = 1000  # Steps before time tapering starts
    _MAX_LEAK_RATE_DIVISOR: float = 10.0  # Limits leak rate: k/(divisor*dt)
    _MAX_K_DOT_RATE: float = 5.0  # Maximum gain rate of change
    _GAIN_WARNING_THRESHOLD: float = 0.8  # Fraction of k_max to trigger leak boost
    _LEAK_MULTIPLIER_NEAR_MAX: float = 2.0  # Leak boost when near k_max
    _MIN_TAPER_EPS: float = 1e-9  # Minimum tapering epsilon

    def __init__(
        self,
        gains: List[float],
        dt: float,
        max_force: float,
        k1_init: float,
        k2_init: float,
        gamma1: float,
        gamma2: float,
        dead_zone: float,
        dynamics_model: Optional[Any] = None,
        *,
        use_relative_surface: bool = False,
        enable_equivalent: Optional[bool] = None,
        use_equivalent: Optional[bool] = None,
        damping_gain: float = 3.0,
        adapt_rate_limit: float = 5.0,
        sat_soft_width: float = 0.03,
        cart_gain: float = 0.5,
        cart_lambda: float = 1.0,
        cart_p_gain: float = 80.0,
        cart_p_lambda: float = 2.0,
        recenter_high_thresh: float = 0.04,
        recenter_low_thresh: float = 0.0,
        k1_max: float = 50.0,
        k2_max: float = 50.0,
        u_int_max: float = 50.0,
        gain_leak: float = 1e-3,
        adaptation_sat_threshold: float = 0.02,
        taper_eps: float = 0.05,
    ) -> None:
        if not isinstance(gains, (list, tuple)) or len(gains) < self.n_gains:
            raise ValueError(f"HybridAdaptiveSTASMC requires ≥{self.n_gains} gains")
        
        self.c1, self.lambda1, self.c2, self.lambda2 = map(float, gains[:4])
        
        from src.utils import require_positive
        self.dt = require_positive(dt, "dt")
        self.max_force = require_positive(max_force, "max_force")
        self.k1_init = require_positive(k1_init, "k1_init", allow_zero=True)
        self.k2_init = require_positive(k2_init, "k2_init", allow_zero=True)
        self.gamma1 = require_positive(gamma1, "gamma1", allow_zero=True)
        self.gamma2 = require_positive(gamma2, "gamma2", allow_zero=True)
        self.dead_zone = require_positive(dead_zone, "dead_zone", allow_zero=True)
        self.adapt_rate_limit = require_positive(adapt_rate_limit, "adapt_rate_limit")

        self._gains = list(gains)
        self.damping_gain = float(damping_gain)
        self.sat_soft_width = float(sat_soft_width)
        self.cart_gain = float(cart_gain)
        self.cart_lambda = float(cart_lambda)
        self.cart_p_gain = float(cart_p_gain)
        self.cart_p_lambda = float(cart_p_lambda)
        self.recenter_low_thresh = float(recenter_low_thresh)
        self.recenter_high_thresh = float(recenter_high_thresh)
        if self.recenter_low_thresh < 0.0:
            raise ValueError("recenter_low_thresh must be ≥ 0")
        if self.recenter_high_thresh <= self.recenter_low_thresh:
            raise ValueError("recenter_high_thresh must be > recenter_low_thresh")

        self.use_relative_surface = bool(use_relative_surface)
        
        if enable_equivalent is not None:
            self.use_equivalent = bool(enable_equivalent)
        else:
            self.use_equivalent = True

        self.k1_max = require_positive(k1_max, "k1_max")
        self.k2_max = require_positive(k2_max, "k2_max")
        self.u_int_max = require_positive(u_int_max, "u_int_max")

        if self.k1_init > self.k1_max:
            raise ValueError(f"k1_init ({self.k1_init}) exceeds k1_max ({self.k1_max})")
        if self.k2_init > self.k2_max:
            raise ValueError(f"k2_init ({self.k2_init}) exceeds k2_max ({self.k2_max})")
        if self.sat_soft_width < self.dead_zone:
            raise ValueError(f"sat_soft_width ({self.sat_soft_width}) must be ≥ dead_zone ({self.dead_zone})")
        self.gain_leak = max(0.0, float(gain_leak))
        self.adaptation_sat_threshold = max(0.0, float(adaptation_sat_threshold))
        self.taper_eps = max(self._MIN_TAPER_EPS, float(taper_eps))

        if dynamics_model is not None:
            self._dynamics_ref = weakref.ref(dynamics_model)
        else:
            self._dynamics_ref = lambda: None

    @property
    def gains(self) -> List[float]:
        return list(self._gains)

    @property
    def dyn(self) -> Optional[Any]:
        return self._dynamics_ref() if self._dynamics_ref is not None else None

    def initialize_state(self) -> Tuple[float, float, float]:
        return (self.k1_init, self.k2_init, 0.0)

    def initialize_history(self) -> Dict[str, List[Any]]:
        return {"k1": [], "k2": [], "u_int": [], "s": []}

    def _compute_taper_factor(self, abs_s: float) -> float:
        return abs_s / (abs_s + self.taper_eps)

    def _compute_sliding_surface(self, state: np.ndarray) -> float:
        x, th1, th2, xdot, th1dot, th2dot = state
        if self.use_relative_surface:
            pendulum_term = self.c1 * (th1dot + self.lambda1 * th1) + self.c2 * ((th2dot - th1dot) + self.lambda2 * (th2 - th1))
        else:
            pendulum_term = self.c1 * (th1dot + self.lambda1 * th1) + self.c2 * (th2dot + self.lambda2 * th2)
        cart_term = self.cart_gain * (xdot + self.cart_lambda * x)
        return float(-(pendulum_term - cart_term))

    def _compute_equivalent_control(self, state: np.ndarray) -> float:
        if not self.use_equivalent or self.dyn is None:
            return 0.0
        try:
            M, C, G = self.dyn._compute_physics_matrices(state)
            M = np.asarray(M, dtype=float) + np.eye(3) * self._TIKHONOV_REGULARIZATION
            v = np.array([state[3], state[4], state[5]], dtype=float)
            Cvec = (C @ v) if (C is not None and C.ndim == 2) else (C if C is not None else np.zeros(3))
            L = np.array([0.0, self.c1, self.c2], dtype=float)
            Llam = np.array([0.0, self.c1*self.lambda1, self.c2*self.lambda2], dtype=float)
            B = np.array([1.0, 0.0, 0.0], dtype=float)
            Minv_B = np.linalg.solve(M, B)
            Minv_rhs = np.linalg.solve(M, Cvec + np.asarray(G, dtype=float))
            denom = float(L @ Minv_B)
            if abs(denom) < self._MIN_DENOMINATOR: return 0.0
            ueq = (L @ Minv_rhs - Llam @ v) / denom
            clamp = self._EQUIV_CONTROL_CLAMP_MULTIPLIER * self.max_force
            return float(np.clip(ueq, -clamp, clamp))
        except Exception:
            return 0.0

    def compute_control(
        self,
        state: np.ndarray,
        state_vars: Optional[Tuple[float, float, float]] = None,
        history: Optional[Dict[str, List[Any]]] = None,
    ) -> HybridSTAOutput:
        if not np.all(np.isfinite(state)):
            return HybridSTAOutput(0.0, self.initialize_state(), (history or self.initialize_history()), 0.0)

        try:
            k1_prev, k2_prev, u_int_prev = state_vars if state_vars else self.initialize_state()
        except Exception:
            k1_prev, k2_prev, u_int_prev = self.initialize_state()

        history = history if history is not None else self.initialize_history()
        s = self._compute_sliding_surface(state)
        abs_s = abs(s)
        in_dz = abs_s <= self.dead_zone
        sgn = 0.0 if in_dz else _sat_tanh(s, max(self.sat_soft_width, self.dead_zone))

        u_sw_temp = -k1_prev * np.sqrt(max(abs_s, 0.0)) * sgn
        u_damp_temp = -self.damping_gain * float(s)
        u_eq = self._compute_equivalent_control(state)
        
        x, xdot = state[0], state[3]
        abs_x = abs(x)
        rc_factor = 0.0 if abs_x <= self.recenter_low_thresh else (1.0 if abs_x >= self.recenter_high_thresh else (abs_x - self.recenter_low_thresh) / (self.recenter_high_thresh - self.recenter_low_thresh))
        u_cart = -rc_factor * self.cart_p_gain * (xdot + self.cart_p_lambda * x)

        u_pre_temp = u_sw_temp + u_int_prev + u_damp_temp + u_cart + u_eq
        hard_saturated = abs(u_pre_temp) > self.max_force + self._HARD_SATURATION_EPSILON
        near_equilibrium = abs_s < self.adaptation_sat_threshold

        if in_dz or (hard_saturated and near_equilibrium):
            k1_dot, k2_dot = -self.gain_leak, -self.gain_leak
        else:
            tf = self._compute_taper_factor(abs_s)
            time_f = 1.0 / (1.0 + self._TIME_TAPER_DECAY_RATE * max(0, len(history["k1"]) - self._TIME_TAPER_STEP_THRESHOLD))
            k1_dot = min(self.gamma1 * abs_s * tf * time_f, self.adapt_rate_limit)
            k2_dot = min(self.gamma2 * abs_s * tf * time_f, self.adapt_rate_limit)
            k1_dot = max(k1_dot - self.gain_leak, -k1_prev / (self._MAX_LEAK_RATE_DIVISOR * self.dt))
            k2_dot = max(k2_dot - self.gain_leak, -k2_prev / (self._MAX_LEAK_RATE_DIVISOR * self.dt))

        if k1_prev > self.k1_max * self._GAIN_WARNING_THRESHOLD: k1_dot = min(k1_dot, -self.gain_leak * self._LEAK_MULTIPLIER_NEAR_MAX)
        if k2_prev > self.k2_max * self._GAIN_WARNING_THRESHOLD: k2_dot = min(k2_dot, -self.gain_leak * self._LEAK_MULTIPLIER_NEAR_MAX)

        k1_new = float(np.clip(k1_prev + k1_dot * self.dt, 0.0, self.k1_max))
        k2_new = float(np.clip(k2_prev + k2_dot * self.dt, 0.0, self.k2_max))
        u_int_new = u_int_prev if in_dz else float(np.clip(u_int_prev + (-k2_new * sgn) * self.dt, -self.u_int_max, self.u_int_max))

        u_sw = -k1_new * np.sqrt(max(abs_s, 0.0)) * sgn
        u_pre = u_sw + u_int_new + u_damp_temp + u_cart + u_eq
        u_sat = float(np.clip(u_pre, -self.max_force, self.max_force))

        if u_sat != u_pre:
            u_int_new = u_int_prev
            u_pre = u_sw + u_int_new + u_damp_temp + u_cart + u_eq
            u_sat = float(np.clip(u_pre, -self.max_force, self.max_force))

        history["k1"].append(k1_new); history["k2"].append(k2_new); history["u_int"].append(u_int_new); history["s"].append(float(s))

        if self._check_emergency_conditions(u_sat, k1_new, k2_new, u_int_new, s, state):
            u_sat, u_int_new = 0.0, 0.0
            k1_new = max(0.0, min(self.k1_init * 0.05, self.k1_max * 0.05))
            k2_new = max(0.0, min(self.k2_init * 0.05, self.k2_max * 0.05))
            s = float(np.clip(s if np.isfinite(s) else 0.0, -1.0, 1.0))
        
        return HybridSTAOutput(u_sat, (k1_new, k2_new, u_int_new), history, float(s))

    def _check_emergency_conditions(self, u_sat: float, k1: float, k2: float, u_int: float, s: float, state: np.ndarray) -> bool:
        sn, vn = np.linalg.norm(state[:3]), np.linalg.norm(state[3:])
        return (not np.isfinite(u_sat) or k1 > self.k1_max * 1.5 or k2 > self.k2_max * 1.5 or 
                abs(u_int) > self.u_int_max * 2.0 or abs(s) > 200.0 or sn > 15.0 or vn > 75.0)

    def reset(self) -> None:
        pass

    def cleanup(self) -> None:
        if hasattr(self, '_dynamics_ref'): self._dynamics_ref = lambda: None

        def __del__(self) -> None:

            try:

                self.cleanup()

            except Exception:

                pass

    
