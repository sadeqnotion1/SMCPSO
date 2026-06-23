#======================================================================================\\\
#==================== src/controllers/smc/core/sliding_surface.py =====================\\\
#======================================================================================\\\

"""
Sliding Surface Calculations for SMC Controllers.

Provides unified sliding surface computation that can be shared across all SMC types.
Implements both linear and nonlinear sliding surface formulations with proper
mathematical foundations.

Mathematical Background:
- Linear sliding surface: s = c₁e₁ + c₂e₂ + λ₁ė₁ + λ₂ė₂
- Where e₁, e₂ are tracking errors and ė₁, ė₂ are error derivatives
- Coefficients c₁, c₂, λ₁, λ₂ must be positive for stability (Hurwitz requirement)
"""

from typing import List, Union
import numpy as np
from abc import ABC, abstractmethod


class SlidingSurface(ABC):
    """Abstract base class for sliding surface calculations."""

    def __init__(self, gains: Union[List[float], np.ndarray]):
        self.gains = np.asarray(gains, dtype=float)
        self._validate_gains()

    @abstractmethod
    def _validate_gains(self) -> None:
        """Validate gains for this specific sliding surface type."""
        pass

    @abstractmethod
    def compute(self, state: np.ndarray) -> float:
        """Compute sliding surface value for given state."""
        pass

    @abstractmethod
    def compute_derivative(self, state: np.ndarray, state_dot: np.ndarray) -> float:
        """Compute sliding surface derivative ds/dt."""
        pass


class LinearSlidingSurface(SlidingSurface):
    """
    Linear sliding surface for conventional SMC.

    Implements: s = λ₁ė₁ + c₁e₁ + λ₂ė₂ + c₂e₂

    For double-inverted pendulum:
    - e₁ = θ₁ (joint 1 angle error)
    - e₂ = θ₂ (joint 2 angle error)
    - ė₁ = θ̇₁ (joint 1 velocity error)
    - ė₂ = θ̇₂ (joint 2 velocity error)
    """

    def __init__(self, gains: Union[List[float], np.ndarray]):
        """
        Initialize linear sliding surface.

        Args:
            gains: [k1, k2, lam1, lam2] where:
                   k1, k2 = velocity gains (must be > 0)
                   lam1, lam2 = position gains (must be > 0)
        """
        super().__init__(gains)

        if len(self.gains) < 4:
            raise ValueError("Linear sliding surface requires at least 4 gains [k1, k2, lam1, lam2]")

        self.k1 = self.gains[0]      # Joint 1 velocity gain
        self.k2 = self.gains[1]      # Joint 2 velocity gain
        self.lam1 = self.gains[2]    # Joint 1 position gain
        self.lam2 = self.gains[3]    # Joint 2 position gain

    def _validate_gains(self) -> None:
        """Validate that surface gains satisfy stability requirements."""
        # Check for finite values
        if not np.all(np.isfinite(self.gains)):
            invalid_indices = np.where(~np.isfinite(self.gains))[0]
            raise ValueError(f"Sliding surface gains contain NaN or infinite values at indices: {invalid_indices}")

        if len(self.gains) >= 4:
            # First 4 gains must be positive for Hurwitz stability
            if any(g <= 0 for g in self.gains[:4]):
                raise ValueError(
                    "Sliding surface gains [k1, k2, lam1, lam2] must be positive for stability"
                )

            # Check for very small gains that might cause numerical issues
            if any(g < 1e-12 for g in self.gains[:4]):
                raise ValueError(
                    "Sliding surface gains are too small (minimum: 1e-12) which may cause numerical instability"
                )

    def compute(self, state: np.ndarray) -> float:
        """
        Compute linear sliding surface value.

        Args:
            state: [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]

        Returns:
            Sliding surface value: s = k1*theta1_dot + lam1*theta1 + k2*theta2_dot + lam2*theta2
        """
        if len(state) < 6:
            raise ValueError("State must have at least 6 elements for double-inverted pendulum")

        # Validate state input
        if not np.all(np.isfinite(state)):
            # Replace non-finite values with zeros for safe computation
            state = np.where(np.isfinite(state), state, 0.0)

        # Extract joint angles and velocities (reference is upright: theta=0)
        # Standard format: [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
        theta1 = state[1]      # Joint 1 angle error
        theta2 = state[2]      # Joint 2 angle error
        theta1_dot = state[4]  # Joint 1 velocity error
        theta2_dot = state[5]  # Joint 2 velocity error

        # Linear sliding surface: s = k₁ė₁ + λ₁e₁ + k₂ė₂ + λ₂e₂
        s = (self.k1 * theta1_dot + self.lam1 * theta1 +
             self.k2 * theta2_dot + self.lam2 * theta2)

        # Ensure finite result
        if not np.isfinite(s):
            return 0.0  # Safe fallback for numerical issues

        return float(s)

    def compute_surface(self, state: np.ndarray) -> float:
        """
        Compatibility method for test interface - alias for compute().

        Args:
            state: State vector

        Returns:
            Sliding surface value
        """
        return self.compute(state)

    def compute_derivative(self, state: np.ndarray, state_dot: np.ndarray) -> float:
        """
        Compute sliding surface derivative ds/dt.

        Args:
            state: Current state vector
            state_dot: State derivative vector

        Returns:
            Surface derivative: ṡ = k₁θ̈₁ + λ₁θ̇₁ + k₂θ̈₂ + λ₂θ̇₂
        """
        if len(state_dot) < 6:
            raise ValueError("State derivative must have at least 6 elements")

        # Extract joint accelerations and velocities
        # Standard format: [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
        theta1_dot = state[4]     # Joint 1 velocity
        theta1_ddot = state_dot[4] # Joint 1 acceleration
        theta2_dot = state[5]     # Joint 2 velocity
        theta2_ddot = state_dot[5] # Joint 2 acceleration

        # Surface derivative: ṡ = k₁θ̈₁ + λ₁θ̇₁ + k₂θ̈₂ + λ₂θ̇₂
        s_dot = (self.k1 * theta1_ddot + self.lam1 * theta1_dot +
                 self.k2 * theta2_ddot + self.lam2 * theta2_dot)

        return float(s_dot)

    def get_coefficients(self) -> dict:
        """Return surface coefficients for analysis."""
        return {
            'k1': self.k1,
            'k2': self.k2,
            'lambda1': self.lam1,
            'lambda2': self.lam2
        }


class HigherOrderSlidingSurface(SlidingSurface):
    """
    Higher-order sliding surface for Super-Twisting and advanced SMC.

    Implements surfaces that include higher-order derivatives for
    finite-time convergence and better disturbance rejection.
    """

    def __init__(self, gains: Union[List[float], np.ndarray], order: int = 2):
        """
        Initialize higher-order sliding surface.

        Args:
            gains: Gain vector for higher-order surface
            order: Surface order (1=classical, 2=super-twisting, etc.)
        """
        super().__init__(gains)
        self.order = order

        if order < 1:
            raise ValueError("Surface order must be >= 1")

        expected_gains = 2 * order  # 2 gains per order for 2-DOF system
        if len(self.gains) < expected_gains:
            raise ValueError(f"Order {order} surface requires at least {expected_gains} gains")

    def _validate_gains(self) -> None:
        """Validate gains for higher-order stability."""
        # For higher-order surfaces, gain positivity requirements are more complex
        # Basic requirement: all gains should be positive
        if any(g <= 0 for g in self.gains):
            raise ValueError("All gains must be positive for higher-order sliding surface")

    def compute(self, state: np.ndarray) -> float:
        """Compute higher-order sliding surface (simplified implementation)."""
        # This would implement more complex surface formulations
        # For now, fall back to linear surface computation
        if len(self.gains) >= 4:
            linear_surface = LinearSlidingSurface(self.gains[:4])
            return linear_surface.compute(state)
        return 0.0

    def compute_derivative(self, state: np.ndarray, state_dot: np.ndarray) -> float:
        """Compute higher-order surface derivative."""
        # Simplified implementation
        if len(self.gains) >= 4:
            linear_surface = LinearSlidingSurface(self.gains[:4])
            return linear_surface.compute_derivative(state, state_dot)
        return 0.0


def create_sliding_surface(surface_type: str, gains: Union[List[float], np.ndarray]) -> SlidingSurface:
    """
    Factory function for creating sliding surfaces.

    Args:
        surface_type: "linear" or "higher_order"
        gains: Gain vector

    Returns:
        Appropriate sliding surface instance
    """
    if surface_type.lower() == "linear":
        return LinearSlidingSurface(gains)
    elif surface_type.lower() in ("higher_order", "higher-order"):
        return HigherOrderSlidingSurface(gains)
    else:
        raise ValueError(f"Unknown surface type: {surface_type}")