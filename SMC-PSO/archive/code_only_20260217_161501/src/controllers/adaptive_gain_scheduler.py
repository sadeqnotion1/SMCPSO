#======================================================================================
#=================== src/controllers/adaptive_gain_scheduler.py =======================
#======================================================================================

"""
Adaptive Gain Scheduling for SMC Controllers

Implements state-magnitude-based gain scheduling to address generalization failure
across wide initial condition ranges. Based on MT-8 Enhancement #3.

Key Insight:
- Small errors (||θ|| < 0.1 rad): Use aggressive gains for fast convergence
- Large errors (||θ|| > 0.2 rad): Use conservative gains to reduce chattering
- Transition zone (0.1-0.2 rad): Linear interpolation between gain sets

References:
- MT-8 Complete Report: benchmarks/MT8_COMPLETE_REPORT.md (Future Work #3)
- MT-7 Generalization Failure: 50.4x chattering increase at large perturbations
- LT-7 Research Paper: Section 8 (Robustness Analysis)

Author: MT-8 Enhancement Team
Created: November 8, 2025
"""

import numpy as np
import logging
from typing import List, Optional, Union, Sequence, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GainScheduleConfig:
    """Configuration for adaptive gain scheduling."""

    # State magnitude thresholds
    small_error_threshold: float = 0.1  # rad - below this use aggressive gains
    large_error_threshold: float = 0.2  # rad - above this use conservative gains

    # Gain reduction factor for conservative mode
    conservative_scale: float = 0.5  # Reduce gains by 50% for large errors

    # Hysteresis to prevent rapid switching
    hysteresis_width: float = 0.01  # rad - add/subtract from thresholds

    # Which state components to include in error norm
    use_angles_only: bool = True  # If True, use ||[θ1, θ2]||; if False, use full state norm


class AdaptiveGainScheduler:
    """
    Adaptive gain scheduler that wraps SMC controllers and adjusts gains based on system state.

    This addresses the generalization failure problem where controllers optimized for small
    perturbations exhibit severe chattering (50.4x increase) at large perturbations. By using
    aggressive gains for small errors and conservative gains for large errors, we achieve:

    1. Fast convergence from small perturbations (using MT-8 robust PSO gains)
    2. Reduced chattering from large perturbations (using scaled-down gains)
    3. Smooth transitions via linear interpolation in transition zone

    Example Usage:
        # Create base controller with MT-8 robust PSO gains
        base_controller = create_controller('classical_smc', gains=mt8_robust_gains)

        # Wrap with adaptive scheduler
        scheduler = AdaptiveGainScheduler(base_controller, config=GainScheduleConfig())

        # Use scheduler transparently (same interface as base controller)
        result = scheduler.compute_control(state, state_vars, history)

    Note:
        The scheduler updates the base controller's gains before each control computation,
        so the base controller always sees the appropriately scheduled gains.
    """

    def __init__(
        self,
        base_controller: Any,
        config: Optional[GainScheduleConfig] = None,
        conservative_gains: Optional[Sequence[float]] = None
    ):
        """
        Initialize adaptive gain scheduler.

        Args:
            base_controller: The SMC controller to wrap (Classical, STA, Adaptive, Hybrid)
            config: Scheduling configuration (uses defaults if None)
            conservative_gains: Optional explicit conservative gains. If None, computed
                               as aggressive_gains * config.conservative_scale

        Raises:
            ValueError: If base_controller doesn't have required attributes
        """
        self.base_controller = base_controller
        self.config = config or GainScheduleConfig()

        # Extract aggressive gains (MT-8 robust PSO optimized)
        if not hasattr(base_controller, '_gains'):
            raise ValueError("Base controller must have '_gains' attribute")

        self.aggressive_gains = np.array(base_controller._gains, dtype=float)

        # Compute or use provided conservative gains
        if conservative_gains is not None:
            self.conservative_gains = np.array(conservative_gains, dtype=float)
            if len(self.conservative_gains) != len(self.aggressive_gains):
                raise ValueError(
                    f"Conservative gains length ({len(self.conservative_gains)}) "
                    f"must match aggressive gains ({len(self.aggressive_gains)})"
                )
        else:
            # Default: scale down aggressive gains
            self.conservative_gains = self.aggressive_gains * self.config.conservative_scale

        # State tracking for hysteresis
        self._last_mode = 'aggressive'  # Track previous gain mode

        logger.info(
            f"AdaptiveGainScheduler initialized: "
            f"{len(self.aggressive_gains)} gains, "
            f"thresholds=[{self.config.small_error_threshold:.3f}, "
            f"{self.config.large_error_threshold:.3f}] rad"
        )

    def compute_error_magnitude(self, state: np.ndarray) -> float:
        """
        Compute error magnitude from system state.

        Args:
            state: System state [x, θ1, θ2, x_dot, θ1_dot, θ2_dot]

        Returns:
            Error magnitude (rad or m, depending on configuration)
        """
        if self.config.use_angles_only:
            # Use only pendulum angles [θ1, θ2]
            error = state[1:3]
        else:
            # Use full state (position, angles, velocities)
            error = state

        return np.linalg.norm(error)

    def schedule_gains(self, state: np.ndarray) -> np.ndarray:
        """
        Determine scheduled gains based on current state magnitude.

        Uses hysteresis to prevent rapid switching between gain sets.

        Args:
            state: Current system state

        Returns:
            Scheduled gains (either aggressive, conservative, or interpolated)
        """
        error_mag = self.compute_error_magnitude(state)

        # Apply hysteresis based on last mode
        if self._last_mode == 'aggressive':
            # Use higher threshold to switch to conservative (add hysteresis)
            small_thresh = self.config.small_error_threshold + self.config.hysteresis_width
        else:
            # Use lower threshold to switch to aggressive (subtract hysteresis)
            small_thresh = self.config.small_error_threshold - self.config.hysteresis_width

        if self._last_mode == 'conservative':
            large_thresh = self.config.large_error_threshold - self.config.hysteresis_width
        else:
            large_thresh = self.config.large_error_threshold + self.config.hysteresis_width

        # Determine gain mode
        if error_mag < small_thresh:
            # Small error: aggressive gains for fast convergence
            scheduled_gains = self.aggressive_gains
            self._last_mode = 'aggressive'
        elif error_mag > large_thresh:
            # Large error: conservative gains to reduce chattering
            scheduled_gains = self.conservative_gains
            self._last_mode = 'conservative'
        else:
            # Transition zone: linear interpolation
            alpha = (error_mag - small_thresh) / (large_thresh - small_thresh)
            alpha = np.clip(alpha, 0.0, 1.0)  # Safety clamp
            scheduled_gains = (1 - alpha) * self.aggressive_gains + alpha * self.conservative_gains
            # Keep last mode for hysteresis continuity

        return scheduled_gains

    def update_controller_gains(self, new_gains: np.ndarray) -> None:
        """
        Update base controller's gains.

        This modifies the internal state of the base controller to use the scheduled gains.

        Args:
            new_gains: New gain values to apply
        """
        # Update stored gains list
        self.base_controller._gains = new_gains.tolist()

        # Update unpacked gain attributes (controller-specific)
        controller_type = type(self.base_controller).__name__

        if controller_type == 'ClassicalSMC':
            # ClassicalSMC: [k1, k2, lam1, lam2, K, kd]
            (self.base_controller.k1, self.base_controller.k2,
             self.base_controller.lam1, self.base_controller.lam2,
             self.base_controller.K, self.base_controller.kd) = new_gains

        elif controller_type in ['STASMC', 'SuperTwistingSMC']:
            # STA SMC: [K1, K2, k1, k2, lam1, lam2]
            (self.base_controller.K1, self.base_controller.K2,
             self.base_controller.k1, self.base_controller.k2,
             self.base_controller.lam1, self.base_controller.lam2) = new_gains

        elif controller_type == 'AdaptiveSMC':
            # Adaptive SMC: [k1, k2, k3, k4, k5]
            (self.base_controller.k1, self.base_controller.k2,
             self.base_controller.k3, self.base_controller.k4,
             self.base_controller.k5) = new_gains

        elif controller_type == 'HybridAdaptiveSTASMC':
            # Hybrid: [c1, lambda1, c2, lambda2]
            (self.base_controller.c1, self.base_controller.lambda1,
             self.base_controller.c2, self.base_controller.lambda2) = new_gains

        else:
            # Generic fallback: just update _gains
            logger.warning(
                f"Unknown controller type {controller_type}, only updating _gains list"
            )

    def compute_control(
        self,
        state: np.ndarray,
        state_vars: Optional[Any] = None,
        history: Optional[Any] = None
    ) -> Any:
        """
        Compute control with adaptively scheduled gains.

        Args:
            state: Current system state
            state_vars: Controller internal state
            history: Controller history buffer

        Returns:
            Control output from base controller
        """
        # Schedule gains based on current state
        scheduled_gains = self.schedule_gains(state)

        # Update base controller with scheduled gains
        self.update_controller_gains(scheduled_gains)

        # Delegate to base controller
        return self.base_controller.compute_control(state, state_vars, history)

    def initialize_state(self) -> Any:
        """Initialize controller state (delegates to base controller)."""
        return self.base_controller.initialize_state()

    def initialize_history(self) -> Any:
        """Initialize history buffer (delegates to base controller)."""
        return self.base_controller.initialize_history()

    def cleanup(self) -> None:
        """Cleanup resources (delegates to base controller)."""
        if hasattr(self.base_controller, 'cleanup'):
            self.base_controller.cleanup()

    def get_current_gains(self) -> np.ndarray:
        """Get currently active gains."""
        return np.array(self.base_controller._gains)

    def get_gain_mode_history(self) -> str:
        """Get current gain mode (for debugging/analysis)."""
        return self._last_mode
