#======================================================================================
#=========== src/controllers/smc/algorithms/conditional_hybrid/config.py =============
#======================================================================================

"""
Conditional Hybrid SMC Configuration.

Configuration for the Conditional Hybrid Architecture that applies super-twisting
conditionally in safe operating regions to avoid B_eq singularities.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConditionalHybridConfig:
    """
    Configuration for Conditional Hybrid SMC Controller.

    Architecture: Adaptive SMC baseline + conditional super-twisting enhancement
    """

    # === Controller Gains (PSO optimizable) ===
    gains: list = None  # [k1, k2, lambda1, lambda2] - Baseline sliding surface gains

    # === Safety Thresholds ===
    angle_threshold: float = 0.2  # rad - Maximum angle for ST activation
    surface_threshold: float = 1.0  # Maximum sliding surface value for ST
    B_eq_threshold: float = 0.1  # Minimum |B_eq| to avoid singularity

    # === Blend Weights (must sum to 1.0) ===
    w_angle: float = 0.3  # Weight for angle proximity
    w_surface: float = 0.3  # Weight for surface proximity
    w_singularity: float = 0.4  # Weight for singularity distance

    # === Super-Twisting Gains (regional application) ===
    gamma1: float = 1.0  # STA proportional gain
    gamma2: float = 1.0  # STA integral gain

    # === Adaptive SMC Configuration (baseline) ===
    epsilon_min: float = 0.017  # Boundary layer thickness
    alpha: float = 1.142  # Adaptation rate

    # === System Limits ===
    max_force: float = 150.0  # N - Hardware saturation limit
    dt: float = 0.001  # s - Control timestep

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Set default gains if not provided
        if self.gains is None:
            self.gains = [20.0, 15.0, 9.0, 4.0]

        # Validate blend weights sum to 1.0
        weight_sum = self.w_angle + self.w_surface + self.w_singularity
        if not (0.99 <= weight_sum <= 1.01):
            raise ValueError(
                f"Blend weights must sum to 1.0, got {weight_sum:.3f}"
            )

        # Validate thresholds are positive
        if self.angle_threshold <= 0:
            raise ValueError("angle_threshold must be positive")
        if self.surface_threshold <= 0:
            raise ValueError("surface_threshold must be positive")
        if self.B_eq_threshold <= 0:
            raise ValueError("B_eq_threshold must be positive")

        # Validate STA gains are positive
        if self.gamma1 <= 0 or self.gamma2 <= 0:
            raise ValueError("gamma1 and gamma2 must be positive")
