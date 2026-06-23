#==========================================================================================
#=================== src/plant/core/physics_matrices_corrected.py =========================
#==========================================================================================
"""
Verified-correct DIP physics matrices (M2 audit fix, ADDITIVE).

This module is a drop-in, dependency-light replacement for the inertia/Coriolis/
gravity computation in core/physics_matrices.py + models/full/physics.py. It is
intentionally NOT wired into the package yet -- review, then swap the call sites.

Conventions (state-order MUST be documented and applied consistently):
    q  = [x, theta1, theta2]
    qd = [x_dot, theta1_dot, theta2_dot]
    state = [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
    theta_i are ABSOLUTE angles. Potential energy uses U = m g L (1 - cos theta)
    (theta = 0 is the reference). Gravity is the CONSERVATIVE force G = +dU/dq,
    so the equation of motion is   M(q) qdd + C(q,qd) qd + G(q) = Q.
    Friction / aero / disturbance are SEPARATE dissipative/external terms in Q --
    they must NOT be folded into C.

Proven invariants (see proof/verify_fix.py):
    - M symmetric positive-definite
    - 0.5 qd^T M qd == kinetic energy
    - (Mdot - 2C) skew-symmetric        (passivity)
    - energy conserved, zero input + zero friction (rel drift ~1e-13)
"""
from __future__ import annotations
import numpy as np


class DIPParameters:
    """Minimal parameter holder; map your FullDIPConfig fields onto these."""
    def __init__(self, m0, m1, m2, L1, L2, Lc1, Lc2, I1, I2, g):
        self.m0, self.m1, self.m2 = m0, m1, m2
        self.L1, self.L2 = L1, L2
        self.Lc1, self.Lc2 = Lc1, Lc2
        self.I1, self.I2 = I1, I2
        self.g = g


def inertia_matrix(p: DIPParameters, theta1: float, theta2: float) -> np.ndarray:
    """Correct absolute-angle DIP inertia matrix M(q)."""
    c1 = np.cos(theta1)
    c2 = np.cos(theta2)
    c12 = np.cos(theta1 - theta2)
    M11 = p.m0 + p.m1 + p.m2
    M12 = (p.m1 * p.Lc1 + p.m2 * p.L1) * c1
    M13 = p.m2 * p.Lc2 * c2
    M22 = p.m1 * p.Lc1 ** 2 + p.m2 * p.L1 ** 2 + p.I1
    M23 = p.m2 * p.L1 * p.Lc2 * c12
    M33 = p.m2 * p.Lc2 ** 2 + p.I2
    return np.array([[M11, M12, M13],
                     [M12, M22, M23],
                     [M13, M23, M33]])


def _dM_dq(p: DIPParameters, q: np.ndarray, k: int, h: float = 1e-6) -> np.ndarray:
    qp = q.copy(); qm = q.copy()
    qp[k] += h; qm[k] -= h
    return (inertia_matrix(p, qp[1], qp[2]) - inertia_matrix(p, qm[1], qm[2])) / (2 * h)


def coriolis_matrix(p: DIPParameters, q: np.ndarray, qd: np.ndarray) -> np.ndarray:
    """Christoffel-symbol Coriolis matrix derived from M(q).
    Guarantees (Mdot - 2C) skew-symmetric => energy structure preserved.
    (Analytic closed form is preferred for speed once validated against this.)
    """
    dM = [_dM_dq(p, q, k) for k in range(3)]
    C = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            C[i, j] = 0.5 * sum(
                (dM[k][i, j] + dM[j][i, k] - dM[i][j, k]) * qd[k] for k in range(3)
            )
    return C


def gravity_vector(p: DIPParameters, theta1: float, theta2: float) -> np.ndarray:
    """Conservative gravity G = +dU/dq for U = sum m g L (1 - cos theta)."""
    return np.array([0.0,
                     (p.m1 * p.Lc1 + p.m2 * p.L1) * p.g * np.sin(theta1),
                     p.m2 * p.Lc2 * p.g * np.sin(theta2)])


def kinetic_energy(p: DIPParameters, state: np.ndarray) -> float:
    q = np.asarray(state[:3], float)
    qd = np.asarray(state[3:], float)
    return 0.5 * qd.dot(inertia_matrix(p, q[1], q[2]).dot(qd))


def potential_energy(p: DIPParameters, state: np.ndarray) -> float:
    _, th1, th2 = state[0], state[1], state[2]
    U1 = p.m1 * p.g * (p.Lc1 * (1 - np.cos(th1)))
    U2 = p.m2 * p.g * (p.L1 * (1 - np.cos(th1)) + p.Lc2 * (1 - np.cos(th2)))
    return U1 + U2


def rhs_conservative(p: DIPParameters, state: np.ndarray, u: float = 0.0) -> np.ndarray:
    """State derivative with control force u on the cart, no friction/aero.
    Add separate dissipative terms to `forcing` for the full model."""
    q = np.asarray(state[:3], float)
    qd = np.asarray(state[3:], float)
    M = inertia_matrix(p, q[1], q[2])
    C = coriolis_matrix(p, q, qd)
    G = gravity_vector(p, q[1], q[2])
    forcing = np.array([u, 0.0, 0.0]) - C.dot(qd) - G
    acc = np.linalg.solve(M, forcing)
    return np.concatenate([qd, acc])
