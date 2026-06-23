#======================================================================================\\\
#================== src/controllers/smc/core/switching_functions.py ===================\\\
#======================================================================================\\\

"""
Switching Functions for SMC Chattering Reduction.

Provides continuous approximations to the discontinuous sign function used in SMC.
These functions reduce chattering while maintaining the robustness properties of SMC.

Mathematical Background:
- Sign function: sign(s) = {+1 if s>0, -1 if s<0, 0 if s=0}
- Continuous approximations smooth the switching to reduce high-frequency oscillations
- Trade-off: smoother switching reduces chattering but may increase steady-state error
"""

from typing import Union, Callable
import numpy as np
from enum import Enum


class SwitchingMethod(Enum):
    """Available switching function methods."""
    TANH = "tanh"
    LINEAR = "linear"
    SIGN = "sign"
    SIGMOID = "sigmoid"


class SwitchingFunction:
    """
    Continuous switching functions for SMC chattering reduction.

    Provides various approximations to the sign function, each with different
    smoothness and robustness characteristics.
    """

    def __init__(self, method: Union[str, SwitchingMethod] = SwitchingMethod.TANH):
        """
        Initialize switching function.

        Args:
            method: Switching method ("tanh", "linear", "sign", "sigmoid")
        """
        if isinstance(method, str):
            try:
                self.method = SwitchingMethod(method.lower())
            except ValueError:
                raise ValueError(f"Unknown switching method: {method}")
        else:
            self.method = method

        # Set the appropriate switching function
        self._switch_func = self._get_switching_function()

    def _get_switching_function(self) -> Callable[[float, float], float]:
        """Get the appropriate switching function implementation."""
        if self.method == SwitchingMethod.TANH:
            return self._tanh_switching
        elif self.method == SwitchingMethod.LINEAR:
            return self._linear_switching
        elif self.method == SwitchingMethod.SIGN:
            return self._sign_switching
        elif self.method == SwitchingMethod.SIGMOID:
            return self._sigmoid_switching
        else:
            raise ValueError(f"Unimplemented switching method: {self.method}")

    def compute(self, surface_value: float, boundary_layer: float) -> float:
        """
        Compute switching function value.

        Args:
            surface_value: Sliding surface value
            boundary_layer: Boundary layer thickness (ε > 0)

        Returns:
            Switching function output in range [-1, 1]
        """
        # Mathematical safety validation
        if not np.isfinite(surface_value):
            return 0.0  # Safe fallback for invalid input
        if not np.isfinite(boundary_layer) or boundary_layer <= 0:
            boundary_layer = 1e-12  # Use minimal positive value to prevent division by zero

        return self._switch_func(surface_value, boundary_layer)

    def _tanh_switching(self, s: float, epsilon: float, slope: float = 3.0) -> float:
        """
        Hyperbolic tangent switching function with configurable slope.

        Formula: tanh((slope * s)/ε)

        Properties:
        - Smooth and infinitely differentiable
        - Bounded output: [-1, 1]
        - Good balance between smoothness and approximation quality
        - Preserves nonzero slope at origin
        - Configurable slope parameter for tuning smoothness (default: 3.0)

        Args:
            s: Sliding surface value
            epsilon: Boundary layer thickness
            slope: Slope parameter (lower = smoother, typical range: 2-5)

        Note:
            Reduced default slope from implicit 10+ to 3.0 for better chattering reduction.
            Original steep slopes caused near-discontinuous behavior.
        """
        # Enhanced mathematical safety
        if epsilon <= 0:
            return np.sign(s)

        # Apply gentler slope for smoother transitions
        # Lower slope values (2-5) provide better chattering reduction
        # compared to steep slopes (10+) which behave like sign function
        ratio = (slope * s) / epsilon

        # Prevent numerical overflow in tanh computation
        if abs(ratio) > 700:  # tanh(700) ≈ 1, tanh(-700) ≈ -1
            return np.sign(s)

        return np.tanh(ratio)

    def _linear_switching(self, s: float, epsilon: float) -> float:
        """
        Piecewise-linear saturation switching function.

        Formula: sat(s/ε) = clip(s/ε, -1, 1)

        Properties:
        - Simple and computationally efficient
        - Bounded output: [-1, 1]
        - Linear in boundary layer, constant outside
        - Can cause degraded robustness near origin (zero slope outside boundary)
        """
        # Enhanced mathematical safety
        if epsilon <= 0:
            return np.sign(s)

        # Safe division with overflow check
        ratio = s / epsilon
        if not np.isfinite(ratio):
            return np.sign(s)

        return np.clip(ratio, -1, 1)

    def _sign_switching(self, s: float, epsilon: float) -> float:
        """
        Pure sign function (discontinuous).

        Formula: sign(s)

        Properties:
        - Theoretically optimal robustness
        - Discontinuous at origin
        - Causes chattering in practice
        - Use only when chattering is acceptable
        """
        # Epsilon is ignored for pure sign function
        return np.sign(s)

    def _sigmoid_switching(self, s: float, epsilon: float, slope: float = 4.0) -> float:
        """
        Sigmoid switching function with configurable slope.

        Formula: 2/(1 + exp(-slope*s/ε)) - 1

        Properties:
        - Smooth and bounded
        - Similar to tanh but different curvature
        - Good for adaptive controllers requiring sigmoid characteristics
        - Configurable slope (default: 4.0 for adaptive nature)

        Args:
            s: Sliding surface value
            epsilon: Boundary layer thickness
            slope: Slope parameter (typical: 3-5 for smooth control)
        """
        # Enhanced mathematical safety
        if epsilon <= 0:
            return np.sign(s)

        # Apply configurable slope for tuning
        ratio = -slope * s / epsilon

        # Prevent numerical overflow in exponential
        if ratio > 700:  # exp(700) overflows
            return -1.0
        elif ratio < -700:  # exp(-700) underflows
            return 1.0

        exp_term = np.exp(ratio)
        if not np.isfinite(exp_term):
            return np.sign(s)

        return 2.0 / (1.0 + exp_term) - 1.0

    def get_derivative(self, surface_value: float, boundary_layer: float) -> float:
        """
        Compute derivative of switching function.

        Useful for analysis and adaptive boundary layer methods.
        """
        s, epsilon = surface_value, boundary_layer

        if self.method == SwitchingMethod.TANH:
            if epsilon <= 0:
                return 0.0  # Sign function has zero derivative almost everywhere
            tanh_val = np.tanh(s / epsilon)
            return (1.0 - tanh_val**2) / epsilon

        elif self.method == SwitchingMethod.LINEAR:
            if epsilon <= 0 or abs(s) >= epsilon:
                return 0.0  # Zero derivative outside boundary layer
            return 1.0 / epsilon

        elif self.method == SwitchingMethod.SIGMOID:
            if epsilon <= 0:
                return 0.0
            exp_term = np.exp(-2.0 * s / epsilon)
            return (4.0 / epsilon) * exp_term / (1.0 + exp_term)**2

        else:  # SIGN
            return 0.0


# Convenience functions for direct use
def tanh_switching(s: float, epsilon: float, slope: float = 3.0) -> float:
    """
    Hyperbolic tangent switching function with optimized slope.

    Args:
        s: Sliding surface value
        epsilon: Boundary layer thickness
        slope: Slope parameter (default: 3.0 for optimal chattering reduction)

    Returns:
        tanh((slope * s)/ε) ∈ [-1, 1]

    Note:
        Default slope reduced from steep (10+) to gentle (3.0) for better
        chattering reduction. Use slope=2-5 for smooth control, slope>5
        approaches discontinuous behavior.
    """
    if epsilon <= 0:
        return np.sign(s)
    ratio = (slope * s) / epsilon
    if abs(ratio) > 700:
        return np.sign(s)
    return np.tanh(ratio)


def linear_switching(s: float, epsilon: float) -> float:
    """
    Linear saturation switching function.

    Args:
        s: Sliding surface value
        epsilon: Boundary layer thickness

    Returns:
        sat(s/ε) = clip(s/ε, -1, 1)
    """
    if epsilon <= 0:
        return np.sign(s)
    return np.clip(s / epsilon, -1, 1)


def sign_switching(s: float, epsilon: float = 0.0) -> float:
    """
    Pure sign function (DEPRECATED - causes severe chattering).

    WARNING: Discontinuous switching causes chattering in real systems.
    Prefer tanh_switching() or linear_switching() with appropriate boundary layer.

    Args:
        s: Sliding surface value
        epsilon: Ignored (kept for interface consistency)

    Returns:
        sign(s) ∈ {-1, 0, 1}

    Deprecated:
        Use tanh_switching(s, epsilon, slope=3.0) instead for chattering reduction.
    """
    import warnings
    warnings.warn(
        "sign_switching() is deprecated and causes severe chattering. "
        "Use tanh_switching(s, epsilon, slope=3.0) for smooth control.",
        DeprecationWarning,
        stacklevel=2
    )
    return np.sign(s)


def adaptive_boundary_layer(surface_value: float, surface_derivative: float,
                           base_epsilon: float, adaptation_gain: float = 0.1) -> float:
    """
    Adaptive boundary layer thickness based on surface derivative.

    Larger ε when |ṡ| is large (fast surface motion) to increase smoothness.
    Smaller ε when |ṡ| is small (near surface) to maintain precision.

    Args:
        surface_value: Current sliding surface value
        surface_derivative: Surface time derivative ṡ
        base_epsilon: Base boundary layer thickness
        adaptation_gain: Adaptation coefficient

    Returns:
        Adaptive boundary layer thickness
    """
    adaptive_component = adaptation_gain * abs(surface_derivative)
    return base_epsilon + adaptive_component


def power_rate_reaching_law(surface_value: float, K: float, alpha: float,
                           epsilon: float = 0.01) -> float:
    """
    Power rate reaching law for finite-time convergence.

    Formula: -K * |s|^α * sign(s) ≈ -K * |s|^α * tanh(s/ε)

    Args:
        surface_value: Sliding surface value s
        K: Reaching law gain (> 0)
        alpha: Power exponent (0 < α < 1 for finite-time)
        epsilon: Boundary layer for sign approximation

    Returns:
        Power rate reaching law output
    """
    if K <= 0:
        raise ValueError("Reaching law gain K must be positive")
    if not (0 < alpha <= 1):
        raise ValueError("Power exponent α must be in (0, 1] for stability")

    s_abs_power = np.power(abs(surface_value), alpha)
    sign_approximation = tanh_switching(surface_value, epsilon)

    return -K * s_abs_power * sign_approximation