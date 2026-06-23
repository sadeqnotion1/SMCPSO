#======================================================================================
#================= src/controllers/sliding_surface_scheduler.py =======================
#======================================================================================

"""
Sliding Surface Based Gain Scheduling for SMC Controllers

Implements |s|-based gain scheduling to address the feedback loop instability
discovered in Phase 2.3 with the angle-based AdaptiveGainScheduler.

Problem with Angle-Based Scheduling (Phase 2.3 findings):
    - Chattering → large |θ| → conservative gains → MORE chattering (positive feedback)
    - Result: +176% chattering increase, +2.27x |s| variance (p<0.001, d=1.33)
    - Root cause: Monitoring angles (θ) creates indirect feedback through control performance

Solution with |s|-Based Scheduling:
    - Monitor sliding surface |s| directly (control performance metric)
    - Inverted logic: HIGH |s| → INCREASE gains (not decrease)
    - Rationale: Large |s| = poor convergence → need MORE aggressive control
    - Break feedback loop: Direct monitoring prevents chattering amplification

Key Differences from AdaptiveGainScheduler:
    1. Metric: |s| (sliding surface) instead of ||θ|| (angle magnitude)
    2. Logic: HIGH |s| → aggressive gains (inverted from angle-based)
    3. Purpose: Break feedback loop, not just adapt to IC range
    4. Thresholds: Tuned for |s| values (typically 0.1-0.5) not angles (0.1-0.2 rad)

References:
    - Phase 2.3 Report: benchmarks/research/phase2_3/PHASE2_3_VALIDATION_REPORT.md
    - Hybrid Controller Anomaly: benchmarks/research/HYBRID_CONTROLLER_ANOMALY_ANALYSIS.md
    - AdaptiveGainScheduler: src/controllers/adaptive_gain_scheduler.py

Author: Phase 3/4 Research Team
Created: November 9, 2025
"""

import numpy as np
import logging
from typing import List, Optional, Union, Sequence, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SlidingSurfaceScheduleConfig:
    """Configuration for sliding surface based gain scheduling."""

    # Sliding surface magnitude thresholds
    small_s_threshold: float = 0.1  # below this: control performing well, use conservative gains
    large_s_threshold: float = 0.5  # above this: control struggling, use aggressive gains

    # Gain scaling factors
    aggressive_scale: float = 1.0   # Full gains for poor performance (large |s|)
    conservative_scale: float = 0.5  # Reduced gains for good performance (small |s|)

    # Hysteresis to prevent rapid switching
    hysteresis_width: float = 0.05  # Add/subtract from thresholds

    # Sliding surface coefficients (c1, c2) for computing s
    c1: float = 10.149  # Default from MT-8 robust gains
    c2: float = 6.815   # Default from MT-8 robust gains


class SlidingSurfaceScheduler:
    """
    Sliding surface based gain scheduler with INVERTED logic to break feedback loop.

    Unlike AdaptiveGainScheduler which monitors angles (creating positive feedback),
    this scheduler monitors the sliding surface |s| directly:

    - Small |s| (<0.1): Control performing well → use conservative gains (save energy)
    - Large |s| (>0.5): Control struggling → use aggressive gains (improve performance)

    This INVERTED logic breaks the feedback loop discovered in Phase 2.3:
        Old (angle-based): Chattering → large θ → conservative gains → MORE chattering
        New (|s|-based):   Chattering → large |s| → AGGRESSIVE gains → LESS chattering

    Example Usage:
        # Create base controller with MT-8 robust PSO gains
        base_controller = create_controller('hybrid_adaptive_sta_smc', gains=mt8_robust_gains)

        # Wrap with |s|-based scheduler
        config = SlidingSurfaceScheduleConfig(
            small_s_threshold=0.1,
            large_s_threshold=0.5,
            c1=10.149,
            c2=6.815
        )
        scheduler = SlidingSurfaceScheduler(base_controller, config=config)

        # Use scheduler transparently (same interface as base controller)
        result = scheduler.compute_control(state, state_vars, history)

    Note:
        This scheduler is designed to replace AdaptiveGainScheduler for the Hybrid
        controller to fix the deployment blockage (666.9° overshoot issue).
    """

    def __init__(
        self,
        base_controller: Any,
        config: Optional[SlidingSurfaceScheduleConfig] = None,
        robust_gains: Optional[Sequence[float]] = None
    ):
        """
        Initialize sliding surface based gain scheduler.

        Args:
            base_controller: The SMC controller to wrap (typically Hybrid)
            config: Scheduling configuration (uses defaults if None)
            robust_gains: Base gains to scale [c1, lambda1, c2, lambda2].
                         If None, extracted from base_controller._gains

        Raises:
            ValueError: If base_controller doesn't have required attributes
        """
        self.base_controller = base_controller
        self.config = config or SlidingSurfaceScheduleConfig()

        # Extract robust gains (baseline for scheduling)
        if robust_gains is not None:
            self.robust_gains = np.array(robust_gains, dtype=float)
        elif hasattr(base_controller, '_gains'):
            self.robust_gains = np.array(base_controller._gains, dtype=float)
        else:
            raise ValueError("Base controller must have '_gains' attribute or provide robust_gains")

        # Compute aggressive and conservative gain sets
        self.aggressive_gains = self.robust_gains * self.config.aggressive_scale
        self.conservative_gains = self.robust_gains * self.config.conservative_scale

        # State tracking for hysteresis
        self._last_mode = 'conservative'  # Start conservative (assume good initial performance)

        logger.info(
            f"SlidingSurfaceScheduler initialized: "
            f"{len(self.robust_gains)} gains, "
            f"|s| thresholds=[{self.config.small_s_threshold:.3f}, "
            f"{self.config.large_s_threshold:.3f}], "
            f"INVERTED LOGIC (high |s| -> aggressive)"
        )

    def compute_sliding_surface(self, state: np.ndarray) -> float:
        """
        Compute sliding surface magnitude |s| from system state.

        For the hybrid controller, the sliding surface is:
            s = c1 * θ1 + c2 * θ1_dot

        Args:
            state: System state [x, θ1, θ2, x_dot, θ1_dot, θ2_dot]

        Returns:
            Sliding surface magnitude |s|
        """
        # Extract relevant state components
        theta1 = state[1]      # θ1 (first pendulum angle)
        theta1_dot = state[4]  # θ1_dot (first pendulum angular velocity)

        # Compute sliding surface
        s = self.config.c1 * theta1 + self.config.c2 * theta1_dot

        return abs(s)

    def schedule_gains(self, state: np.ndarray) -> np.ndarray:
        """
        Determine scheduled gains based on sliding surface magnitude.

        CRITICAL: Uses INVERTED logic compared to AdaptiveGainScheduler:
            - Small |s| (<0.1): Control performing well → conservative gains
            - Large |s| (>0.5): Control struggling → AGGRESSIVE gains
            - Transition zone: Linear interpolation

        This inversion breaks the positive feedback loop from Phase 2.3.

        Args:
            state: Current system state

        Returns:
            Scheduled gains (aggressive, conservative, or interpolated)
        """
        s_mag = self.compute_sliding_surface(state)

        # Apply hysteresis based on last mode
        if self._last_mode == 'aggressive':
            # Currently aggressive, need lower |s| to switch to conservative
            small_thresh = self.config.small_s_threshold - self.config.hysteresis_width
        else:
            # Currently conservative, need higher |s| to stay conservative
            small_thresh = self.config.small_s_threshold + self.config.hysteresis_width

        if self._last_mode == 'conservative':
            # Currently conservative, need higher |s| to switch to aggressive
            large_thresh = self.config.large_s_threshold + self.config.hysteresis_width
        else:
            # Currently aggressive, need lower |s| to stay aggressive
            large_thresh = self.config.large_s_threshold - self.config.hysteresis_width

        # Determine gain mode (INVERTED LOGIC)
        if s_mag < small_thresh:
            # Small |s|: Control performing well → use conservative gains
            scheduled_gains = self.conservative_gains
            self._last_mode = 'conservative'
        elif s_mag > large_thresh:
            # Large |s|: Control struggling → use AGGRESSIVE gains (inverted!)
            scheduled_gains = self.aggressive_gains
            self._last_mode = 'aggressive'
        else:
            # Transition zone: linear interpolation
            # alpha=0 at small_thresh (conservative), alpha=1 at large_thresh (aggressive)
            alpha = (s_mag - small_thresh) / (large_thresh - small_thresh)
            alpha = np.clip(alpha, 0.0, 1.0)  # Safety clamp
            scheduled_gains = (1 - alpha) * self.conservative_gains + alpha * self.aggressive_gains
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
        Compute control with |s|-based adaptively scheduled gains.

        Args:
            state: Current system state
            state_vars: Controller internal state
            history: Controller history buffer

        Returns:
            Control output from base controller
        """
        # Schedule gains based on current |s|
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

    def get_last_s_magnitude(self, state: np.ndarray) -> float:
        """Get most recent sliding surface magnitude (for analysis)."""
        return self.compute_sliding_surface(state)
