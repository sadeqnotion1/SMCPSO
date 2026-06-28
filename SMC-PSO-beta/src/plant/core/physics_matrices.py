#======================================================================================
#========================= src/plant/core/physics_matrices.py =========================
#======================================================================================
"""
Physics Matrix Computation for DIP Systems.

Provides focused components for computing the fundamental physics matrices:
- Inertia Matrix (M): Mass and inertial properties
- Coriolis Matrix (C): Velocity-dependent forces
- Gravity Vector (G): Gravitational forces

This version wraps the verified-correct equations from physics_matrices_corrected.py
to resolve the M2 passivity/energy-drift inconsistency (Finding #2).
"""

from __future__ import annotations
from typing import Tuple, Protocol, Any
import numpy as np

try:
    from numba import njit
except ImportError:
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from .physics_matrices_corrected import DIPParameters, inertia_matrix, coriolis_matrix, gravity_vector


class PhysicsMatrixComputer(Protocol):
    """Protocol for physics matrix computation."""

    def compute_inertia_matrix(self, state: np.ndarray) -> np.ndarray:
        """Compute inertia matrix M(q)."""
        ...

    def compute_coriolis_matrix(self, state: np.ndarray) -> np.ndarray:
        """Compute Coriolis matrix C(q, q̇)."""
        ...

    def compute_gravity_vector(self, state: np.ndarray) -> np.ndarray:
        """Compute gravity vector G(q)."""
        ...


class DIPPhysicsMatrices:
    """
    Double Inverted Pendulum physics matrix computation.

    Wraps the verified-correct equations from physics_matrices_corrected.py.
    """

    def __init__(self, parameters: Any):
        """
        Initialize physics matrix computer.

        Args:
            parameters: Physical parameters for the DIP system
        """
        self.params = parameters

        # Map to verified parameters structure
        self.p = DIPParameters(
            m0=parameters.cart_mass,
            m1=parameters.pendulum1_mass,
            m2=parameters.pendulum2_mass,
            L1=parameters.pendulum1_length,
            L2=parameters.pendulum2_length,
            Lc1=parameters.pendulum1_com,
            Lc2=parameters.pendulum2_com,
            I1=parameters.pendulum1_inertia,
            I2=parameters.pendulum2_inertia,
            g=parameters.gravity
        )

    def compute_inertia_matrix(self, state: np.ndarray) -> np.ndarray:
        """
        Compute the inertia matrix M(q) for the DIP system.

        Args:
            state: System state [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
        """
        return inertia_matrix(self.p, state[1], state[2])

    def compute_coriolis_matrix(self, state: np.ndarray) -> np.ndarray:
        """
        Compute the Coriolis matrix C(q, q̇) for the DIP system.

        Args:
            state: System state [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
        """
        return coriolis_matrix(self.p, state[:3], state[3:])

    def compute_gravity_vector(self, state: np.ndarray) -> np.ndarray:
        """
        Compute the gravity vector G(q) for the DIP system.

        Args:
            state: System state [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
        """
        return gravity_vector(self.p, state[1], state[2])

    def compute_all_matrices(self, state: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute all physics matrices in a single call for efficiency.

        Args:
            state: System state [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
        """
        return (
            self.compute_inertia_matrix(state),
            self.compute_coriolis_matrix(state),
            self.compute_gravity_vector(state)
        )


class SimplifiedDIPPhysicsMatrices(DIPPhysicsMatrices):
    """
    Simplified physics matrices for computational efficiency.
    """

    def compute_inertia_matrix(self, state: np.ndarray) -> np.ndarray:
        """Simplified inertia matrix with reduced coupling terms."""
        _, theta1, theta2, _, _, _ = state

        return self._compute_simplified_inertia_matrix_numba(
            theta1, theta2, self.p.m0, self.p.m1, self.p.m2,
            self.p.L1, self.p.L2, self.p.Lc1, self.p.Lc2, self.p.I1, self.p.I2
        )

    @staticmethod
    @njit(cache=True)
    def _compute_simplified_inertia_matrix_numba(
        theta1: float, theta2: float,
        m0: float, m1: float, m2: float,
        L1: float, L2: float, Lc1: float, Lc2: float,
        I1: float, I2: float
    ) -> np.ndarray:
        """Simplified inertia matrix computation."""
        M11 = m0 + m1 + m2
        M22 = m1 * Lc1**2 + m2 * L1**2 + I1 + m2 * Lc2**2 + I2
        M33 = m2 * Lc2**2 + I2

        c1 = np.cos(theta1)
        c2 = np.cos(theta2)

        M12 = 0.5 * (m1 * Lc1 + m2 * L1) * c1 + 0.5 * m2 * Lc2 * c2
        M13 = 0.5 * m2 * Lc2 * c2
        M23 = 0.8 * (m2 * Lc2**2 + I2)

        M = np.array([
            [M11, M12, M13],
            [M12, M22, M23],
            [M13, M23, M33]
        ])

        return M