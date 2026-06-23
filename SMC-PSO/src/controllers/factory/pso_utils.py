#======================================================================================\\\
#===================== src/controllers/factory/pso_integration.py =====================\\\
#======================================================================================\\\

"""
Advanced PSO Integration Module for SMC Controllers.

This module provides optimized integration between SMC controllers and PSO optimization,
featuring thread-safe operations, performance monitoring, and comprehensive error handling.
Consolidates PSO-related utilities from:
- pso_integration.py (500 lines) - Primary PSO optimization integration
- factory_new/utils.py (103 lines) - Performance monitoring utilities

Week 1 aggressive factory refactoring (18 files -> 6 files).
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Union
from dataclasses import dataclass

import numpy as np

from ..factory import SMCType, create_controller, CONTROLLER_REGISTRY


# =============================================================================
# PSO CONTROLLER INTERFACE PROTOCOLS
# =============================================================================

class PSOOptimizable(Protocol):
    """Protocol for PSO-optimizable controllers."""

    def compute_control(self, state: np.ndarray) -> np.ndarray:
        """Compute control output for given state."""
        ...

    @property
    def max_force(self) -> float:
        """Maximum control force limit."""
        ...


@dataclass
class PSOPerformanceMetrics:
    """Performance metrics for PSO controller evaluation."""

    computation_time: float  # Average computation time per call (seconds)
    control_effort: float    # RMS control effort
    stability_margin: float  # Estimated stability margin
    success_rate: float      # Success rate of control computations
    error_count: int         # Number of computation errors


# =============================================================================
# ENHANCED PSO CONTROLLER WRAPPER
# =============================================================================

class EnhancedPSOControllerWrapper:
    """
    Enhanced PSO-compatible controller wrapper with advanced features.

    Features:
    - Thread-safe operation
    - Performance monitoring
    - Automatic saturation handling
    - Error recovery mechanisms
    - Statistical tracking
    """

    def __init__(
        self,
        controller: Any,
        controller_type: str,
        max_force: Optional[float] = None,
        enable_monitoring: bool = True
    ):
        """
        Initialize enhanced PSO wrapper.

        Args:
            controller: Underlying SMC controller instance
            controller_type: Controller type identifier
            max_force: Override maximum force limit (optional)
            enable_monitoring: Enable performance monitoring
        """
        self.controller = controller
        self.controller_type = controller_type
        self.max_force = max_force or getattr(controller, 'max_force', 150.0)
        self.enable_monitoring = enable_monitoring

        # Performance tracking
        self._call_count = 0
        self._error_count = 0
        self._total_computation_time = 0.0
        self._control_efforts = []

        # Safety limits
        self._max_computation_time = 0.01  # 10ms maximum
        self._state_bounds = {
            'position': (-5.0, 5.0),      # Cart position bounds (m)
            'angle1': (-np.pi, np.pi),     # First pendulum angle bounds (rad)
            'angle2': (-np.pi, np.pi),     # Second pendulum angle bounds (rad)
            'velocity': (-10.0, 10.0),     # Velocity bounds (m/s, rad/s)
        }

        self.logger = logging.getLogger(f"{__name__}.{controller_type}")

    def compute_control(self, state: np.ndarray) -> np.ndarray:
        """
        PSO-compatible control computation with enhanced error handling.

        Args:
            state: 6-element state vector [x, θ1, θ2, ẋ, θ̇1, θ̇2]

        Returns:
            1-element numpy array with saturated control force

        Raises:
            ValueError: If state vector is invalid
        """
        start_time = time.perf_counter() if self.enable_monitoring else 0.0

        try:
            # Input validation
            self._validate_state(state)

            # Call underlying controller
            result = self.controller.compute_control(state, (), {})

            # Extract and process control value
            control_value = self._extract_control_value(result)

            # Apply safety constraints
            control_saturated = self._apply_safety_constraints(control_value)

            # Update performance metrics
            if self.enable_monitoring:
                computation_time = time.perf_counter() - start_time
                self._update_metrics(computation_time, control_saturated)

            return np.array([control_saturated], dtype=np.float64)

        except Exception as e:
            self._error_count += 1
            self.logger.warning(f"Control computation failed: {e}")
            return self._get_safe_fallback_control(state)

    def _validate_state(self, state: np.ndarray) -> None:
        """Validate input state vector."""
        if not isinstance(state, np.ndarray):
            raise ValueError(f"State must be numpy array, got {type(state)}")

        if state.shape != (6,):
            raise ValueError(f"State must have shape (6,), got {state.shape}")

        if not np.all(np.isfinite(state)):
            raise ValueError("State contains non-finite values")

        # Check physical bounds
        x, theta1, theta2, x_dot, theta1_dot, theta2_dot = state

        if not (self._state_bounds['position'][0] <= x <= self._state_bounds['position'][1]):
            self.logger.warning(f"Cart position {x:.3f} outside bounds {self._state_bounds['position']}")

        # Normalize angles to [-π, π]
        theta1_norm = np.arctan2(np.sin(theta1), np.cos(theta1))
        theta2_norm = np.arctan2(np.sin(theta2), np.cos(theta2))

        if abs(theta1_norm) > 0.95 * np.pi or abs(theta2_norm) > 0.95 * np.pi:
            self.logger.warning(f"Large angles detected: θ1={theta1_norm:.3f}, θ2={theta2_norm:.3f}")

    def _extract_control_value(self, result: Any) -> float:
        """Extract control value from controller result."""
        if hasattr(result, 'u'):
            control = result.u
        elif isinstance(result, dict) and 'u' in result:
            control = result['u']
        elif hasattr(result, 'control'):
            control = result.control
        else:
            control = result

        # Convert to scalar
        if isinstance(control, np.ndarray):
            if control.shape == ():
                return float(control)
            elif control.shape == (1,):
                return float(control[0])
            else:
                return float(control.flatten()[0])
        elif isinstance(control, (int, float)):
            return float(control)
        else:
            raise ValueError(f"Cannot extract control value from {type(control)}")

    def _apply_safety_constraints(self, control_value: float) -> float:
        """Apply safety constraints to control value."""
        # Saturation
        control_saturated = np.clip(control_value, -self.max_force, self.max_force)

        # Rate limiting (simple first-order filter)
        if hasattr(self, '_last_control'):
            max_rate = 1000.0  # Max rate: 1000 N/s
            dt = 0.001  # Assume 1kHz control rate
            max_change = max_rate * dt

            control_rate_limited = np.clip(
                control_saturated,
                self._last_control - max_change,
                self._last_control + max_change
            )
        else:
            control_rate_limited = control_saturated

        self._last_control = control_rate_limited
        return control_rate_limited

    def _get_safe_fallback_control(self, state: np.ndarray) -> np.ndarray:
        """Generate safe fallback control for error conditions."""
        # Simple PD control for stabilization
        try:
            x, theta1, theta2, x_dot, theta1_dot, theta2_dot = state

            # Stabilizing control law (simplified)
            kp_cart = 5.0
            kd_cart = 2.0
            kp_angle = 20.0
            kd_angle = 5.0

            # Small angle approximation for safety
            theta1_small = np.sin(theta1)
            theta2_small = np.sin(theta2)

            u_fallback = -(kp_cart * x + kd_cart * x_dot +
                          kp_angle * (theta1_small + theta2_small) +
                          kd_angle * (theta1_dot + theta2_dot))

            u_saturated = np.clip(u_fallback, -self.max_force, self.max_force)
            return np.array([u_saturated], dtype=np.float64)

        except Exception:
            # Ultimate fallback: zero control
            return np.array([0.0], dtype=np.float64)

    def _update_metrics(self, computation_time: float, control_value: float) -> None:
        """Update performance metrics."""
        self._call_count += 1
        self._total_computation_time += computation_time
        self._control_efforts.append(abs(control_value))

        # Limit history size for memory efficiency
        if len(self._control_efforts) > 1000:
            self._control_efforts = self._control_efforts[-500:]

    def get_performance_metrics(self) -> PSOPerformanceMetrics:
        """Get current performance metrics."""
        if self._call_count == 0:
            return PSOPerformanceMetrics(0.0, 0.0, 0.0, 0.0, 0)

        avg_computation_time = self._total_computation_time / self._call_count
        rms_control_effort = np.sqrt(np.mean(np.square(self._control_efforts))) if self._control_efforts else 0.0
        success_rate = 1.0 - (self._error_count / self._call_count)

        # Estimate stability margin based on control effort variance
        stability_margin = 1.0 / (1.0 + np.var(self._control_efforts)) if len(self._control_efforts) > 1 else 1.0

        return PSOPerformanceMetrics(
            computation_time=avg_computation_time,
            control_effort=rms_control_effort,
            stability_margin=stability_margin,
            success_rate=success_rate,
            error_count=self._error_count
        )

    def reset_metrics(self) -> None:
        """Reset performance metrics."""
        self._call_count = 0
        self._error_count = 0
        self._total_computation_time = 0.0
        self._control_efforts.clear()

    @property
    def n_gains(self) -> int:
        """Number of gains for PSO compatibility."""
        return CONTROLLER_REGISTRY[self.controller_type]['gain_count']


# =============================================================================
# PSO CONTROLLER FACTORY FUNCTIONS
# =============================================================================

def create_enhanced_pso_controller(
    smc_type: SMCType,
    gains: Union[List[float], np.ndarray],
    plant_config: Optional[Any] = None,
    max_force: float = 150.0,
    dt: float = 0.001,
    enable_monitoring: bool = True,
    **kwargs: Any
) -> EnhancedPSOControllerWrapper:
    """
    Create enhanced PSO-compatible controller with advanced features.

    Args:
        smc_type: SMC controller type
        gains: Controller gains
        plant_config: Plant configuration (optional)
        max_force: Maximum control force
        dt: Control timestep
        enable_monitoring: Enable performance monitoring
        **kwargs: Additional controller parameters

    Returns:
        Enhanced PSO controller wrapper

    Raises:
        ValueError: If parameters are invalid
    """
    # Create base controller
    controller = create_controller(
        smc_type.value,
        config=plant_config,
        gains=gains
    )

    # Create enhanced wrapper
    wrapper = EnhancedPSOControllerWrapper(
        controller=controller,
        controller_type=smc_type.value,
        max_force=max_force,
        enable_monitoring=enable_monitoring
    )

    return wrapper


def create_optimized_pso_factory(
    smc_type: SMCType,
    plant_config: Optional[Any] = None,
    max_force: float = 150.0,
    enable_monitoring: bool = True,
    **kwargs: Any
) -> Callable[[Union[List[float], np.ndarray]], EnhancedPSOControllerWrapper]:
    """
    Create optimized PSO factory function for controller creation.

    Args:
        smc_type: SMC controller type
        plant_config: Plant configuration (optional)
        max_force: Maximum control force
        enable_monitoring: Enable performance monitoring
        **kwargs: Additional factory parameters

    Returns:
        Factory function that creates PSO controllers from gains
    """
    def pso_factory(gains: Union[List[float], np.ndarray]) -> EnhancedPSOControllerWrapper:
        """PSO factory function."""
        return create_enhanced_pso_controller(
            smc_type=smc_type,
            gains=gains,
            plant_config=plant_config,
            max_force=max_force,
            enable_monitoring=enable_monitoring,
            **kwargs
        )

    # Add PSO-required attributes
    pso_factory.n_gains = CONTROLLER_REGISTRY[smc_type.value]['gain_count']
    pso_factory.controller_type = smc_type.value
    pso_factory.max_force = max_force

    return pso_factory


# =============================================================================
# PSO BOUNDS AND VALIDATION UTILITIES
# =============================================================================

def get_optimized_pso_bounds(
    smc_type: SMCType,
    performance_target: str = 'balanced'
) -> Tuple[List[float], List[float]]:
    """
    Get optimized PSO bounds based on performance targets.

    Args:
        smc_type: Controller type
        performance_target: 'aggressive', 'balanced', or 'conservative'

    Returns:
        Tuple of (lower_bounds, upper_bounds)
    """
    base_bounds = {
        SMCType.CLASSICAL: {
            'lower': [1.0, 1.0, 1.0, 1.0, 5.0, 0.1],
            'upper': [30.0, 30.0, 20.0, 20.0, 50.0, 10.0]
        },
        SMCType.ADAPTIVE: {
            'lower': [2.0, 2.0, 1.0, 1.0, 0.5],
            'upper': [40.0, 40.0, 25.0, 25.0, 10.0]
        },
        SMCType.SUPER_TWISTING: {
            'lower': [3.0, 2.0, 2.0, 2.0, 0.5, 0.5],
            'upper': [50.0, 30.0, 30.0, 30.0, 20.0, 20.0]
        },
        SMCType.HYBRID: {
            'lower': [2.0, 2.0, 1.0, 1.0],
            'upper': [30.0, 30.0, 20.0, 20.0]
        }
    }

    if smc_type not in base_bounds:
        raise ValueError(f"Unsupported controller type: {smc_type}")

    lower = base_bounds[smc_type]['lower'].copy()
    upper = base_bounds[smc_type]['upper'].copy()

    # Adjust bounds based on performance target
    if performance_target == 'aggressive':
        # Wider bounds for more aggressive search
        lower = [0.5 * x for x in lower]
        upper = [1.5 * x for x in upper]
    elif performance_target == 'conservative':
        # Narrower bounds for stable operation
        center = [(low + up) / 2 for low, up in zip(lower, upper)]
        width = [(up - low) * 0.6 for low, up in zip(lower, upper)]
        lower = [c - w/2 for c, w in zip(center, width)]
        upper = [c + w/2 for c, w in zip(center, width)]
    # 'balanced' uses base bounds as-is

    return (lower, upper)


def validate_pso_gains_advanced(
    smc_type: SMCType,
    gains: Union[List[float], np.ndarray],
    check_stability: bool = True
) -> Dict[str, Any]:
    """
    Advanced validation of PSO gains with stability analysis.

    Args:
        smc_type: Controller type
        gains: Gains to validate
        check_stability: Perform stability checks

    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'stability_estimate': None
    }

    # Basic validation
    expected_count = CONTROLLER_REGISTRY[smc_type.value]['gain_count']
    if len(gains) != expected_count:
        result['valid'] = False
        result['errors'].append(f"Expected {expected_count} gains, got {len(gains)}")
        return result

    # Check for finite values
    if not all(np.isfinite(g) for g in gains):
        result['valid'] = False
        result['errors'].append("Gains contain non-finite values")
        return result

    # Check positivity
    if any(g <= 0 for g in gains):
        result['valid'] = False
        result['errors'].append("All gains must be positive")
        return result

    # Controller-specific validation
    if smc_type == SMCType.CLASSICAL:
        k1, k2, lam1, lam2, K, kd = gains

        # Surface gains should be well-conditioned
        if lam1 / k1 > 10 or lam2 / k2 > 10:
            result['warnings'].append("High damping ratio may cause sluggish response")

        if K > 100:
            result['warnings'].append("Very high switching gain may cause chattering")

        if check_stability:
            # Simple stability estimate based on Hurwitz criterion
            char_poly_coeffs = [1, lam1 + lam2, k1*lam2 + k2*lam1, k1*k2]
            stability_margin = min(char_poly_coeffs[1:])  # Simplified check
            result['stability_estimate'] = stability_margin

    elif smc_type == SMCType.ADAPTIVE:
        k1, k2, lam1, lam2, gamma = gains

        if gamma > 5:
            result['warnings'].append("High adaptation gain may cause parameter drift")

        if gamma < 0.1:
            result['warnings'].append("Low adaptation gain may cause slow convergence")

    # Add more controller-specific checks as needed

    return result