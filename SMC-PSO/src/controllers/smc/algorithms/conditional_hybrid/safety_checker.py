#======================================================================================
#========= src/controllers/smc/algorithms/regional_hybrid/safety_checker.py ==========
#======================================================================================

"""
Safety Region Checker for Regional Hybrid SMC.

Implements the safety conditions that determine when super-twisting can be
safely applied without encountering B_eq singularities.

Based on Gemini's theoretical proof of architectural incompatibility:
- B_eq(q) = λ₁H₁₁ + λ₂H₂₁ + λ₃H₃₁
- Singularity occurs when B_eq → 0 (cancellation of coupling terms)
"""

import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def compute_equivalent_gain(state: np.ndarray, gains: np.ndarray) -> float:
    """
    Compute equivalent control gain B_eq from state and sliding surface gains.

    Based on Gemini's derivation:
        B_eq(q) = λ₁H₁₁ + λ₂H₂₁ + λ₃H₃₁

    Where:
        - H₁₁: Cart diagonal term (always positive)
        - H₂₁, H₃₁: Inertial coupling terms (oscillate with cos(θ))
        - λᵢ: Sliding surface gains

    Args:
        state: State vector [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]
        gains: Sliding surface gains [k1, k2, lambda1, lambda2]

    Returns:
        B_eq: Equivalent control gain (scalar)

    Note:
        For DIP, exact H(q) computation requires full mass matrix inversion.
        This implementation uses a simplified approximation based on typical
        DIP parameters. For production, should use dynamics.get_mass_matrix_inverse().
    """
    theta1, theta2 = state[1], state[2]

    # Extract sliding surface gains
    # Note: gains format from LinearSlidingSurface is [k1, k2, lambda1, lambda2]
    # where k1, k2 are velocity gains and lambda1, lambda2 are position gains
    lambda1, lambda2 = gains[2], gains[3]  # Position gains affect accelerations

    # Simplified approximation of H(q) terms for typical DIP
    # These are approximations; full computation requires dynamics model
    # H₁₁ ≈ constant (cart diagonal, always positive)
    H11 = 1.0  # Normalized

    # H₂₁, H₃₁ ≈ coupling terms that oscillate with cos(θ)
    # These become negative at certain angles, causing cancellation
    H21 = 0.3 * np.cos(theta1)  # Approximate coupling coefficient
    H31 = 0.2 * np.cos(theta2)  # Approximate coupling coefficient

    # Compute B_eq per Gemini's formula
    B_eq = lambda1 * H11 + lambda2 * H21 + lambda2 * H31

    return B_eq


def compute_sliding_surface(state: np.ndarray, gains: np.ndarray) -> float:
    """
    Compute sliding surface value s.

    s = k₁θ̇₁ + λ₁θ₁ + k₂θ̇₂ + λ₂θ₂

    Args:
        state: State vector [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]
        gains: Sliding surface gains [k1, k2, lambda1, lambda2]

    Returns:
        s: Sliding surface value (scalar)
    """
    theta1, theta2 = state[1], state[2]
    theta1_dot, theta2_dot = state[4], state[5]

    k1, k2, lambda1, lambda2 = gains

    s = k1 * theta1_dot + lambda1 * theta1 + k2 * theta2_dot + lambda2 * theta2

    return s


def is_safe_for_supertwisting(
    state: np.ndarray,
    gains: np.ndarray,
    angle_threshold: float,
    surface_threshold: float,
    B_eq_threshold: float
) -> Tuple[bool, dict]:
    """
    Check if super-twisting can be safely applied in current state.

    Three conditions must ALL be satisfied:
    1. Near equilibrium: |θ₁|, |θ₂| < angle_threshold
    2. On or near sliding surface: |s| < surface_threshold
    3. No singularity: |B_eq| > B_eq_threshold (away from zero)

    Args:
        state: State vector [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]
        gains: Sliding surface gains [k1, k2, lambda1, lambda2]
        angle_threshold: Maximum angle for ST activation (rad)
        surface_threshold: Maximum sliding surface value for ST
        B_eq_threshold: Minimum |B_eq| to avoid singularity

    Returns:
        Tuple of:
            - is_safe: Boolean indicating if all conditions met
            - diagnostics: Dict with condition details for logging/debugging
    """
    theta1, theta2 = state[1], state[2]

    # Condition 1: Near equilibrium (small angles)
    near_equilibrium = (abs(theta1) < angle_threshold) and (abs(theta2) < angle_threshold)

    # Condition 2: On or near sliding surface
    s = compute_sliding_surface(state, gains)
    on_surface = abs(s) < surface_threshold

    # Condition 3: B_eq away from singularity
    B_eq = compute_equivalent_gain(state, gains)
    no_singularity = abs(B_eq) > B_eq_threshold

    # All conditions must be True
    is_safe = near_equilibrium and on_surface and no_singularity

    # Diagnostics for logging/debugging (convert numpy.bool_ to Python bool)
    diagnostics = {
        "near_equilibrium": bool(near_equilibrium),
        "on_surface": bool(on_surface),
        "no_singularity": bool(no_singularity),
        "theta1": float(theta1),
        "theta2": float(theta2),
        "s": float(s),
        "B_eq": float(B_eq),
        "is_safe": bool(is_safe),
    }

    return bool(is_safe), diagnostics


def compute_blend_weight(
    state: np.ndarray,
    gains: np.ndarray,
    angle_threshold: float,
    surface_threshold: float,
    B_eq_threshold: float,
    w_angle: float,
    w_surface: float,
    w_singularity: float
) -> float:
    """
    Compute blending weight for smooth transition between Adaptive SMC and STA.

    Weight ranges from 0.0 (pure Adaptive SMC) to 1.0 (pure super-twisting).
    Uses sigmoid function for smooth transitions.

    Args:
        state: State vector [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]
        gains: Sliding surface gains [k1, k2, lambda1, lambda2]
        angle_threshold: Maximum angle for ST activation (rad)
        surface_threshold: Maximum sliding surface value for ST
        B_eq_threshold: Minimum |B_eq| to avoid singularity
        w_angle: Weight for angle proximity (0-1)
        w_surface: Weight for surface proximity (0-1)
        w_singularity: Weight for singularity distance (0-1)

    Returns:
        weight: Blending weight in [0.0, 1.0]
    """
    theta1, theta2 = state[1], state[2]
    s = compute_sliding_surface(state, gains)
    B_eq = compute_equivalent_gain(state, gains)

    # Proximity to equilibrium (closer → higher weight)
    max_angle = max(abs(theta1), abs(theta2))
    angle_proximity = 1.0 - min(max_angle / angle_threshold, 1.0)

    # Proximity to surface (closer → higher weight)
    surface_proximity = 1.0 - min(abs(s) / surface_threshold, 1.0)

    # Distance from singularity (farther → higher weight)
    singularity_distance = min(abs(B_eq) / B_eq_threshold, 1.0)

    # Weighted combination
    weight_raw = (
        w_angle * angle_proximity +
        w_surface * surface_proximity +
        w_singularity * singularity_distance
    )

    # Smooth transition using sigmoid
    # Maps [0, 1] to smooth S-curve centered at 0.5
    weight_smoothed = 1.0 / (1.0 + np.exp(-10 * (weight_raw - 0.5)))

    return weight_smoothed
