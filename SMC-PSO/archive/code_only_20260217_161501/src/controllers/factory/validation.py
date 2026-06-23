#======================================================================================\\\
#===================== src/controllers/factory/core/validation.py =====================\\\
#======================================================================================\\\

"""
Comprehensive Validation Framework for Controller Factory

Provides enterprise-grade validation for controller gains, configurations, and parameters
with detailed error reporting and recovery mechanisms.Consolidates validation logic from core/validation.py and factory_new/validation.py
during Week 1 aggressive factory refactoring (18 files → 6 files).

Primary source: core/validation.py (413 lines) - enterprise-grade validation
Merged unique functions from factory_new/validation.py (213 lines, ~80% duplicate)
"""

import logging
from typing import Dict, Any, List, Union, Optional
import numpy as np
from numpy.typing import NDArray

from .types import GainsArray
from .registry import get_controller_info


logger = logging.getLogger(__name__)


# =============================================================================
# VALIDATION RESULT CLASSES
# =============================================================================

class ValidationResult:
    """Container for validation results with detailed feedback."""

    def __init__(self, valid: bool = True):
        self.valid = valid
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.metadata: Dict[str, Any] = {}

    def add_error(self, message: str) -> None:
        """Add an error message and mark result as invalid."""
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        """Add an informational message."""
        self.info.append(message)

    def has_issues(self) -> bool:
        """Check if there are any errors or warnings."""
        return bool(self.errors or self.warnings)

    def get_summary(self) -> str:
        """Get a summary of validation results."""
        if not self.has_issues():
            return "Validation passed with no issues"

        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")

        return f"Validation completed with {', '.join(parts)}"

    def __str__(self) -> str:
        """String representation of validation results."""
        lines = [f"ValidationResult(valid={self.valid})"]

        if self.errors:
            lines.append("Errors:")
            for error in self.errors:
                lines.append(f"  - {error}")

        if self.warnings:
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        if self.info:
            lines.append("Info:")
            for info in self.info:
                lines.append(f"  - {info}")

        return "\n".join(lines)


# =============================================================================
# CORE VALIDATION FUNCTIONS
# =============================================================================

def validate_controller_gains(
    gains: GainsArray,
    controller_type: str,
    check_bounds: bool = True,
    check_stability: bool = True
) -> ValidationResult:
    """
    Validate controller gains with comprehensive checks.

    Args:
        gains: Controller gains to validate
        controller_type: Type of controller
        check_bounds: Perform bounds checking
        check_stability: Perform stability analysis

    Returns:
        Detailed validation results
    """
    result = ValidationResult()

    try:
        controller_info = get_controller_info(controller_type)
    except (ValueError, TypeError) as e:
        result.add_error(f"Invalid controller type: {e}")
        return result

    # Convert gains to list for consistent handling
    if isinstance(gains, np.ndarray):
        gains_list = gains.tolist()
    else:
        gains_list = list(gains)

    # Basic type and structure validation
    if not isinstance(gains_list, list):
        result.add_error(f"Gains must be a list or array, got {type(gains)}")
        return result

    expected_count = controller_info['gain_count']
    if len(gains_list) != expected_count:
        result.add_error(
            f"Controller '{controller_info['description']}' requires exactly {expected_count} gains, "
            f"got {len(gains_list)}. Expected structure: {controller_info.get('gain_structure', 'N/A')}"
        )

    # Type validation for individual gains
    for i, gain in enumerate(gains_list):
        if not isinstance(gain, (int, float)):
            result.add_error(f"Gain at index {i} must be numeric, got {type(gain)}")

    if not result.valid:
        return result

    # Finite value validation
    if not all(np.isfinite(g) for g in gains_list):
        invalid_indices = [i for i, g in enumerate(gains_list) if not np.isfinite(g)]
        result.add_error(f"Gains at indices {invalid_indices} are not finite")

    # Positivity validation (SMC stability requirement)
    if any(g <= 0 for g in gains_list):
        negative_indices = [i for i, g in enumerate(gains_list) if g <= 0]
        result.add_error(
            f"Gains at indices {negative_indices} must be positive for SMC stability"
        )

    if not result.valid:
        return result

    # Bounds checking
    if check_bounds and 'gain_bounds' in controller_info:
        bounds = controller_info['gain_bounds']
        if bounds and len(bounds) == len(gains_list):
            for i, (gain, (lower, upper)) in enumerate(zip(gains_list, bounds)):
                if gain < lower:
                    result.add_warning(f"Gain {i} ({gain:.3f}) below recommended minimum ({lower})")
                elif gain > upper:
                    result.add_warning(f"Gain {i} ({gain:.3f}) above recommended maximum ({upper})")

    # Controller-specific validation
    if controller_type == 'classical_smc' and len(gains_list) >= 6:
        _validate_classical_smc_gains(gains_list, result, check_stability)
    elif controller_type == 'adaptive_smc' and len(gains_list) >= 5:
        _validate_adaptive_smc_gains(gains_list, result, check_stability)
    elif controller_type == 'sta_smc' and len(gains_list) >= 6:
        _validate_sta_smc_gains(gains_list, result, check_stability)
    elif controller_type == 'hybrid_adaptive_sta_smc' and len(gains_list) >= 4:
        _validate_hybrid_smc_gains(gains_list, result, check_stability)

    # Add metadata
    result.metadata['controller_type'] = controller_type
    result.metadata['gain_count'] = len(gains_list)
    result.metadata['gain_values'] = gains_list

    return result


def validate_configuration(
    config: Any,
    controller_type: str,
    check_completeness: bool = True
) -> ValidationResult:
    """
    Validate controller configuration object.

    Args:
        config: Configuration object to validate
        controller_type: Type of controller
        check_completeness: Check for all required parameters

    Returns:
        Detailed validation results
    """
    result = ValidationResult()

    try:
        controller_info = get_controller_info(controller_type)
    except (ValueError, TypeError) as e:
        result.add_error(f"Invalid controller type: {e}")
        return result

    if config is None:
        if check_completeness:
            result.add_warning("Configuration is None, will use defaults")
        return result

    # Check required parameters
    if check_completeness:
        required_params = controller_info.get('required_params', [])
        for param in required_params:
            if not hasattr(config, param):
                result.add_error(f"Missing required parameter: {param}")

    # Validate specific configuration attributes
    if hasattr(config, 'gains'):
        gains_result = validate_controller_gains(config.gains, controller_type)
        if not gains_result.valid:
            result.add_error("Configuration gains validation failed")
            result.errors.extend(gains_result.errors)
        result.warnings.extend(gains_result.warnings)

    if hasattr(config, 'max_force'):
        if not isinstance(config.max_force, (int, float)) or config.max_force <= 0:
            result.add_error("max_force must be a positive number")

    if hasattr(config, 'dt'):
        if not isinstance(config.dt, (int, float)) or config.dt <= 0:
            result.add_error("dt must be a positive number")
        elif config.dt > 0.1:
            result.add_warning("Large timestep (dt > 0.1) may cause instability")

    # Controller-specific configuration validation
    if controller_type == 'classical_smc':
        if hasattr(config, 'boundary_layer'):
            if not isinstance(config.boundary_layer, (int, float)) or config.boundary_layer <= 0:
                result.add_error("boundary_layer must be a positive number")

    result.metadata['controller_type'] = controller_type
    result.metadata['config_type'] = type(config).__name__

    return result


# =============================================================================
# CONTROLLER-SPECIFIC VALIDATION FUNCTIONS
# =============================================================================

def _validate_classical_smc_gains(
    gains: List[float],
    result: ValidationResult,
    check_stability: bool
) -> None:
    """Validate Classical SMC specific gain constraints."""
    k1, k2, lam1, lam2, K, kd = gains[:6]

    # Surface gains ratio check
    if lam1 / k1 > 20:
        result.add_warning("High damping ratio λ1/k1 may cause sluggish response")
    if lam2 / k2 > 20:
        result.add_warning("High damping ratio λ2/k2 may cause sluggish response")

    # Switching gain check
    if K > 100:
        result.add_warning("Very high switching gain K may cause excessive chattering")
    elif K < 1:
        result.add_warning("Low switching gain K may cause poor disturbance rejection")

    # Derivative gain check
    if kd > 20:
        result.add_warning("High derivative gain kd may amplify noise")

    if check_stability:
        # Simplified stability check based on characteristic polynomial
        char_poly_coeffs = [1, lam1 + lam2, k1*lam2 + k2*lam1, k1*k2]
        if min(char_poly_coeffs[1:]) <= 0:
            result.add_warning("Gains may not satisfy Hurwitz stability criterion")

        stability_margin = min(char_poly_coeffs[1:])
        result.metadata['stability_margin'] = stability_margin


def _validate_adaptive_smc_gains(
    gains: List[float],
    result: ValidationResult,
    check_stability: bool
) -> None:
    """Validate Adaptive SMC specific gain constraints."""
    k1, k2, lam1, lam2, gamma = gains[:5]

    # Adaptation gain validation
    if gamma > 10:
        result.add_warning("High adaptation gain γ may cause parameter drift")
    elif gamma < 0.1:
        result.add_warning("Low adaptation gain γ may cause slow convergence")

    # Surface stability check
    if lam1 / k1 < 0.5 or lam2 / k2 < 0.5:
        result.add_warning("Low damping ratios may cause oscillatory behavior")


def _validate_sta_smc_gains(
    gains: List[float],
    result: ValidationResult,
    check_stability: bool
) -> None:
    """Validate Super-Twisting SMC specific gain constraints."""
    K1, K2, k1, k2, lam1, lam2 = gains[:6]

    # Super-twisting parameter relationships
    if K2 / K1 > 2:
        result.add_warning("Ratio K2/K1 > 2 may affect convergence properties")
    elif K2 / K1 < 0.1:
        result.add_warning("Ratio K2/K1 < 0.1 may cause slow convergence")

    # Switching gains validation
    if K1 < K2:
        result.add_warning("K1 should typically be larger than K2 for STA")


def _validate_hybrid_smc_gains(
    gains: List[float],
    result: ValidationResult,
    check_stability: bool
) -> None:
    """Validate Hybrid SMC specific gain constraints."""
    k1, k2, lam1, lam2 = gains[:4]

    # Balance between classical and adaptive components
    if k1 / k2 > 5 or k2 / k1 > 5:
        result.add_warning("Large imbalance between k1 and k2 may affect hybrid performance")

    if lam1 / lam2 > 5 or lam2 / lam1 > 5:
        result.add_warning("Large imbalance between λ1 and λ2 may affect hybrid performance")


# =============================================================================
# UTILITY VALIDATION FUNCTIONS
# =============================================================================

def validate_state_vector(state: NDArray[np.float64]) -> ValidationResult:
    """Validate system state vector."""
    result = ValidationResult()

    if not isinstance(state, np.ndarray):
        result.add_error(f"State must be numpy array, got {type(state)}")
        return result

    if state.shape != (6,):
        result.add_error(f"State must have shape (6,), got {state.shape}")
        return result

    if not np.all(np.isfinite(state)):
        result.add_error("State contains non-finite values")
        return result

    # Physical reasonableness checks
    x, theta1, theta2, x_dot, theta1_dot, theta2_dot = state

    if abs(x) > 10:
        result.add_warning(f"Large cart position: {x:.3f} m")

    if abs(theta1) > np.pi or abs(theta2) > np.pi:
        result.add_warning("Pendulum angles outside [-π, π] range")

    if abs(x_dot) > 20:
        result.add_warning(f"High cart velocity: {x_dot:.3f} m/s")

    if abs(theta1_dot) > 50 or abs(theta2_dot) > 50:
        result.add_warning("High angular velocities detected")

    return result


def validate_control_output(control: Union[float, NDArray[np.float64]], max_force: float = 150.0) -> ValidationResult:
    """Validate control output value."""
    result = ValidationResult()

    # Convert to scalar if needed
    if isinstance(control, np.ndarray):
        if control.shape == ():
            control_value = float(control)
        elif control.shape == (1,):
            control_value = float(control[0])
        else:
            result.add_error(f"Control output has invalid shape: {control.shape}")
            return result
    else:
        control_value = float(control)

    if not np.isfinite(control_value):
        result.add_error("Control output is not finite")
        return result

    if abs(control_value) > max_force:
        result.add_warning(f"Control output {control_value:.3f} exceeds max_force {max_force}")

    if abs(control_value) > 2 * max_force:
        result.add_error(f"Control output {control_value:.3f} severely exceeds limits")

    result.metadata['control_value'] = control_value
    result.metadata['saturation_required'] = abs(control_value) > max_force

    return result

# =============================================================================
# GAIN RESOLUTION AND VALIDATION (from factory_new/validation.py)
# =============================================================================

def _resolve_controller_gains(
    gains: Optional[Union[List[float], np.ndarray]],
    config: Optional[Any],
    controller_type: str,
    controller_info: Dict[str, Any]
) -> List[float]:
    """Resolve controller gains from multiple sources.

    Args:
        gains: Explicitly provided gains
        config: Configuration object
        controller_type: Controller type name
        controller_info: Controller registry information

    Returns:
        Resolved gains list
    """
    if gains is not None:
        if isinstance(gains, np.ndarray):
            gains = gains.tolist()
        return gains

    # Try to extract gains from config
    if config is not None:
        try:
            # Try different config structures
            if hasattr(config, 'controller_defaults'):
                defaults = config.controller_defaults
                if isinstance(defaults, dict) and controller_type in defaults:
                    config_gains = defaults[controller_type].get('gains')
                    if config_gains is not None:
                        return config_gains
                elif hasattr(defaults, controller_type):
                    controller_config = getattr(defaults, controller_type)
                    if hasattr(controller_config, 'gains'):
                        return controller_config.gains

            elif hasattr(config, 'controllers'):
                controllers = config.controllers
                if isinstance(controllers, dict) and controller_type in controllers:
                    config_gains = controllers[controller_type].get('gains')
                    if config_gains is not None:
                        return config_gains
                elif hasattr(controllers, controller_type):
                    controller_config = getattr(controllers, controller_type)
                    if hasattr(controller_config, 'gains'):
                        return controller_config.gains
        except Exception as e:
            # OK: Config loading optional - fall back to default gains
            logger.debug(f"Could not load config gains for {controller_type}, using defaults: {e}")

    return controller_info['default_gains']


def _extract_controller_parameters(
    config: Optional[Any],
    controller_type: str,
    controller_info: Dict[str, Any]
) -> Dict[str, Any]:
    """Extract controller-specific parameters from configuration.

    Args:
        config: Configuration object
        controller_type: Controller type name
        controller_info: Controller registry information

    Returns:
        Dictionary of controller parameters
    """
    if config is None:
        return {}

    controller_params = {}

    try:
        if hasattr(config, 'controllers') and controller_type in config.controllers:
            controller_config = config.controllers[controller_type]

            if hasattr(controller_config, 'model_dump'):
                controller_params = controller_config.model_dump()
            elif isinstance(controller_config, dict):
                controller_params = controller_config.copy()
            else:
                # Extract attributes from config object
                controller_params = {
                    attr: getattr(controller_config, attr)
                    for attr in dir(controller_config)
                    if not attr.startswith('_') and not callable(getattr(controller_config, attr))
                }
    except Exception as e:
        # OK: Config introspection optional - return empty params
        logger.debug(f"Could not extract controller params from config: {e}")

    return controller_params


def validate_smc_gains(smc_type, gains: Union[list, np.ndarray]) -> bool:
    """Validate gains for a controller type.

    Args:
        smc_type: SMC controller type (from SMCType enum or string)
        gains: Gains to validate

    Returns:
        True if gains are valid, False otherwise
    """
    from .types import SMCType
    
    expected_lengths = {
        SMCType.CLASSICAL: 6,
        SMCType.ADAPTIVE: 5,
        SMCType.SUPER_TWISTING: 6,
        SMCType.HYBRID: 4,
    }
    
    # Handle string types
    if isinstance(smc_type, str):
        try:
            smc_type = SMCType(smc_type)
        except ValueError:
            return False
    
    expected_len = expected_lengths.get(smc_type, 6)
    return len(gains) == expected_len and all(isinstance(g, (int, float)) and g > 0 for g in gains)


def _validate_mpc_parameters(config_params: Dict[str, Any], controller_params: Dict[str, Any]) -> None:
    """Validate MPC controller parameters.

    Args:
        config_params: Main configuration parameters
        controller_params: Controller-specific parameters

    Raises:
        ValueError: If any parameter is invalid (changed from ConfigValueError for consistency)
    """
    from .types import ConfigValueError
    
    # Merge parameters from both sources
    all_params = {**config_params, **controller_params}

    # Validate horizon parameter
    if 'horizon' in all_params:
        horizon = all_params['horizon']
        if not isinstance(horizon, int):
            raise ConfigValueError("horizon must be an integer")
        if horizon < 1:
            raise ConfigValueError("horizon must be >= 1")

    # Validate geometric constraints
    if 'max_cart_pos' in all_params:
        max_cart_pos = all_params['max_cart_pos']
        if not isinstance(max_cart_pos, (int, float)) or max_cart_pos <= 0:
            raise ConfigValueError("max_cart_pos must be > 0")
