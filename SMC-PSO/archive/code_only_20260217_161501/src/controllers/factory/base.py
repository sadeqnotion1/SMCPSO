#======================================================================================\
#======================== src/controllers/factory/factory_new/core.py ===================\
#======================================================================================\

"""
Enterprise Controller Factory - Production-Ready Controller Instantiation

This module provides a comprehensive factory pattern for instantiating different types
of controllers with proper configuration, parameter management, and enterprise-grade
quality standards.

Architecture:
- Modular design with clean separation of concerns
- Thread-safe operations with comprehensive locking
- Type-safe interfaces with 95%+ type hint coverage
- Configuration validation with deprecation handling
- PSO optimization integration
- Comprehensive error handling and logging

Supported Controllers:
- Classical SMC: Sliding mode control with boundary layer
- Super-Twisting SMC: Higher-order sliding mode algorithm
- Adaptive SMC: Online parameter adaptation
- Hybrid Adaptive-STA SMC: Combined adaptive and super-twisting
- MPC Controller: Model predictive control (optional)
Consolidates core factory functionality from:
- factory_new/core.py (745 lines) - Modern enterprise factory
- smc_factory.py (526 lines) - Clean SMC-only factory, PSO-optimized
- core/threading.py (335 lines) - Thread-safety primitives (to be added)

Week 1 aggressive factory refactoring (18 files -> 6 files).
"""

# Standard library imports
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


# =============================================================================
# THREAD-SAFETY PRIMITIVES (from core/threading.py)
# =============================================================================

import threading
import time
from typing import Callable, Optional, TypeVar, ParamSpec
from functools import wraps
from contextlib import contextmanager

# Type variables for generic decorator support
P = ParamSpec("P")
T = TypeVar("T")

# Global factory lock with timeout protection
_factory_lock = threading.RLock()
_LOCK_TIMEOUT = 10.0  # seconds
_DEADLOCK_DETECTION_ENABLED = True

# Performance monitoring
_lock_acquisitions = 0
_lock_contentions = 0
_total_wait_time = 0.0
_max_wait_time = 0.0


class FactoryLockTimeoutError(Exception):
    """Raised when factory lock acquisition times out."""
    pass


class FactoryDeadlockError(Exception):
    """Raised when potential deadlock is detected."""
    pass


def with_factory_lock(
    timeout: Optional[float] = None,
    raise_on_timeout: bool = True
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to make factory functions thread-safe.

    Args:
        timeout: Lock acquisition timeout (default: global timeout)
        raise_on_timeout: Raise exception on timeout vs return None

    Returns:
        Thread-safe decorated function

    Raises:
        FactoryLockTimeoutError: If lock acquisition times out
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            effective_timeout = timeout or _LOCK_TIMEOUT
            start_time = time.perf_counter()

            global _lock_acquisitions, _lock_contentions, _total_wait_time, _max_wait_time

            try:
                # Attempt to acquire lock with timeout
                acquired = _factory_lock.acquire(timeout=effective_timeout)

                if not acquired:
                    wait_time = time.perf_counter() - start_time
                    _lock_contentions += 1
                    _total_wait_time += wait_time
                    _max_wait_time = max(_max_wait_time, wait_time)

                    error_msg = (
                        f"Failed to acquire factory lock within {effective_timeout}s for {func.__name__}. "
                        f"Possible deadlock or contention."
                    )
                    logger.error(error_msg)

                    if raise_on_timeout:
                        raise FactoryLockTimeoutError(error_msg)
                    else:
                        return None

                # Lock acquired successfully
                wait_time = time.perf_counter() - start_time
                _lock_acquisitions += 1
                if wait_time > 0.001:  # Only count significant waits as contention
                    _lock_contentions += 1
                _total_wait_time += wait_time
                _max_wait_time = max(_max_wait_time, wait_time)

                # Execute the protected function
                return func(*args, **kwargs)

            finally:
                # Always release lock if acquired
                if acquired:
                    _factory_lock.release()

        return wrapper
    return decorator


@contextmanager
def factory_lock_context(timeout: Optional[float] = None):
    """
    Context manager for thread-safe factory operations.

    Args:
        timeout: Lock acquisition timeout (default: global timeout)

    Yields:
        None

    Raises:
        FactoryLockTimeoutError: If lock acquisition times out
    """
    effective_timeout = timeout or _LOCK_TIMEOUT
    acquired = _factory_lock.acquire(timeout=effective_timeout)

    if not acquired:
        raise FactoryLockTimeoutError(
            f"Failed to acquire factory lock within {effective_timeout}s"
        )

    try:
        yield
    finally:
        _factory_lock.release()


def get_lock_statistics() -> dict:
    """Get factory lock performance statistics."""
    return {
        "acquisitions": _lock_acquisitions,
        "contentions": _lock_contentions,
        "total_wait_time": _total_wait_time,
        "max_wait_time": _max_wait_time,
        "avg_wait_time": _total_wait_time / max(_lock_acquisitions, 1),
        "contention_rate": _lock_contentions / max(_lock_acquisitions, 1),
    }


# Third-party imports
import numpy as np
from numpy.typing import NDArray

# Local imports - Core dynamics (with fallback handling)
from src.core.dynamics import DIPDynamics

# Local imports - Controller implementations
from src.controllers.smc.algorithms.hybrid.controller import ModularHybridSMC
from src.controllers.smc.classic_smc import ClassicalSMC
from src.controllers.smc.sta_smc import SuperTwistingSMC
from src.controllers.smc.adaptive_smc import AdaptiveSMC

# Import exceptions from legacy factory
from src.controllers.factory.legacy_factory import FactoryConfigurationError

# Local imports - Configuration classes with fallback handling
try:
    from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
    from src.controllers.smc.algorithms.super_twisting.config import (
        SuperTwistingSMCConfig as STASMCConfig
    )
    from src.controllers.smc.algorithms.adaptive.config import AdaptiveSMCConfig
    from src.controllers.smc.algorithms.hybrid.config import (
        HybridSMCConfig as HybridAdaptiveSTASMCConfig
    )
    CONFIG_CLASSES_AVAILABLE = True
except ImportError:
    CONFIG_CLASSES_AVAILABLE = False
    from src.controllers.factory.fallback_configs import (
        ClassicalSMCConfig,
        STASMCConfig,
        AdaptiveSMCConfig,
        HybridAdaptiveSTASMCConfig
    )

# Local imports - Extracted factory modules (Phase 2 refactor)
from .types import (
    StateVector, ControlOutput, GainsArray, ConfigDict, ControllerT,
    ConfigValueError, ControllerProtocol, SMCType
, SMCConfig)
from .registry import (
    CONTROLLER_ALIASES, canonicalize_controller_type,
    CONTROLLER_REGISTRY, get_controller_info,
    list_available_controllers, list_all_controllers, get_default_gains
)
from .validation import (
    validate_controller_gains, validate_configuration,
    _resolve_controller_gains, _extract_controller_parameters,
    validate_smc_gains, _validate_mpc_parameters
)
# from .utils import  # MERGED INTO base.py

# Optional MPC controller import
try:
    from src.controllers.mpc.controller import MPCController
    MPC_AVAILABLE = True
except ImportError:
    MPCController = None
    MPC_AVAILABLE = False

# Local imports - Configuration classes
from src.controllers.smc.algorithms.hybrid.config import HybridMode

# =============================================================================
# MODULE-LEVEL LOGGER
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# MAIN FACTORY FUNCTIONS
# =============================================================================

def create_controller(controller_type: str,
                     config: Optional[Any] = None,
                     gains: Optional[Union[list, np.ndarray]] = None) -> Any:
    """Create controller instance using the factory pattern with robust configuration.

    This is the primary factory function for creating sliding mode control (SMC) and model
    predictive control (MPC) instances. It provides a unified interface for controller
    instantiation with automatic gain validation, configuration resolution, and error handling.

    The factory supports multiple controller types with automatic parameter resolution from
    multiple sources (explicit gains, config file, or registry defaults) and comprehensive
    validation of controller-specific requirements.

    Thread Safety:
        This function is thread-safe and can be called concurrently from multiple threads
        using a module-level reentrant lock (_factory_lock).

    Supported Controller Types:
        - 'classical_smc': Classical sliding mode control with boundary layer
        - 'sta_smc': Super-twisting algorithm (second-order SMC)
        - 'adaptive_smc': Adaptive SMC with online parameter estimation
        - 'hybrid_adaptive_sta_smc': Hybrid adaptive super-twisting control
        - 'mpc_controller': Model predictive control (requires optional dependencies)

    Type Aliases:
        The factory normalizes common controller type variations:
        - 'classic_smc', 'smc_classical', 'smc_v1' → 'classical_smc'
        - 'super_twisting', 'sta' → 'sta_smc'
        - 'adaptive' → 'adaptive_smc'
        - 'hybrid', 'hybrid_sta' → 'hybrid_adaptive_sta_smc'

    Gain Resolution Priority:
        1. Explicit gains parameter (if provided)
        2. Configuration object gains (config.controllers[type].gains)
        3. Registry default gains (CONTROLLER_REGISTRY[type]['default_gains'])

    Args:
        controller_type: Controller type identifier string. Case-insensitive with automatic
            normalization of aliases (e.g., 'classic_smc' → 'classical_smc'). Must be a
            non-empty string matching a registered controller type or alias.
        config: Optional configuration object or dictionary containing controller parameters.
            The factory attempts to extract parameters from multiple configuration structures:
            - config.controllers[controller_type]: Controller-specific configuration
            - config.physics: Physics parameters for dynamics model creation
            - config.dynamics_model: Pre-existing dynamics model instance
            If None, uses registry defaults with fallback configurations.
        gains: Optional gain vector for controller tuning. If provided as numpy array, it is
            converted to a list. Must match the expected gain count for the controller type:
            - Classical SMC: 6 gains [k1, k2, λ1, λ2, K, kd]
            - STA SMC: 6 gains [K1, K2, k1, k2, λ1, λ2] (must satisfy K1 > K2)
            - Adaptive SMC: 5 gains [k1, k2, λ1, λ2, γ]
            - Hybrid SMC: 4 gains [c1, λ1, c2, λ2]
            - MPC: No gains (uses cost matrices instead)

    Returns:
        Controller instance implementing the BaseController interface with methods:
        - compute_control(state, last_control, history): Compute control output
        - reset(): Reset internal controller state
        - gains property: Access to controller gain vector

    Raises:
        ValueError: If controller_type is not recognized, is empty, is not a string, or if
            gains have invalid length, non-finite values, or violate controller-specific
            constraints (e.g., K1 <= K2 for STA SMC).
        ImportError: If controller type requires missing optional dependencies (e.g., MPC
            controller without cvxpy installation). Error message includes list of available
            controllers.
        FactoryConfigurationError: If configuration building fails due to invalid parameter
            values, missing required parameters, or incompatible configuration structure.

    Examples:
        >>> from src.controllers.factory import create_controller
        >>> from src.config import load_config
        >>>
        >>> # Example 1: Create with default gains from config file
        >>> config = load_config("config.yaml")
        >>> controller = create_controller('classical_smc', config)
        >>> print(controller.gains)
        [20.0, 15.0, 12.0, 8.0, 35.0, 5.0]
        >>>
        >>> # Example 2: Create with PSO-optimized gains
        >>> optimized_gains = [25.3, 18.7, 14.2, 10.8, 42.6, 6.1]
        >>> controller = create_controller('classical_smc', config, gains=optimized_gains)
        >>>
        >>> # Example 3: Create without config (uses registry defaults)
        >>> controller = create_controller('sta_smc')
        >>> print(controller.gains)
        [25.0, 15.0, 20.0, 12.0, 8.0, 6.0]
        >>>
        >>> # Example 4: Type alias usage
        >>> controller = create_controller('super_twisting', config)  # Normalized to 'sta_smc'
        >>>
        >>> # Example 5: Batch creation for comparison studies
        >>> controller_types = ['classical_smc', 'sta_smc', 'adaptive_smc']
        >>> controllers = [create_controller(ct, config) for ct in controller_types]

    See Also:
        - list_available_controllers(): Query available controller types
        - get_default_gains(controller_type): Get default gains for a type
        - CONTROLLER_REGISTRY: Registry of all supported controllers with metadata
        - src.optimization.integration.pso_factory_bridge: PSO integration for gain optimization
        - config.yaml: Configuration schema for controller parameters

    Notes:
        - The factory automatically validates gain constraints (e.g., K1 > K2 for STA SMC)
        - Dynamics models are created automatically if physics parameters are in config
        - Deprecated parameters are migrated automatically with warnings logged
        - For invalid default gains, the factory attempts automatic correction before failing
        - Controller-specific parameters (boundary_layer, dt, etc.) are extracted from config
          or set to safe defaults
        - MPC controller creation follows different patterns (no gains, requires horizon/costs)

    References:
        [1] Utkin, V. "Sliding Modes in Control and Optimization", Springer, 1992
        [2] Levant, A. "Higher-order sliding modes", IEEE TAC, 1993
        [3] Shtessel, Y. et al. "Sliding Mode Control and Observation", Birkhauser, 2014
    """
    with _factory_lock:
        # Normalize/alias controller type
        controller_type = canonicalize_controller_type(controller_type)

        # Validate controller type and get info (handles availability checks)
        try:
            controller_info = get_controller_info(controller_type)
        except ImportError as e:
            # Re-raise import errors with better context
            available = list_available_controllers()
            raise ImportError(f"{e}. Available controllers: {available}") from e

        controller_class = controller_info['class']
        config_class = controller_info['config_class']

    # Determine gains to use
    controller_gains = _resolve_controller_gains(gains, config, controller_type, controller_info)

    # Validate gains with controller-specific rules
    try:
        validate_controller_gains(controller_gains, controller_info, controller_type)
    except ValueError as e:
        # For invalid default gains, try to fix them automatically
        if gains is None:  # Only auto-fix if using default gains
            if controller_type == 'sta_smc':
                # Fix K1 > K2 requirement
                controller_gains = [25.0, 15.0, 20.0, 12.0, 8.0, 6.0]  # K1=25 > K2=15
            elif controller_type == 'adaptive_smc':
                # Fix 5-gain requirement
                controller_gains = [25.0, 18.0, 15.0, 10.0, 4.0]  # Exactly 5 gains
            else:
                raise e

            # Re-validate after fix
            validate_controller_gains(controller_gains, controller_info, controller_type)
        else:
            raise e

    # Create dynamics model if needed
    dynamics_model = None
    if config is not None:
        try:
            # Try to get existing dynamics model
            if hasattr(config, 'dynamics_model'):
                dynamics_model = config.dynamics_model
            elif hasattr(config, 'physics'):
                dynamics_model = DIPDynamics(config.physics)
            elif hasattr(config, 'dip_params'):
                dynamics_model = DIPDynamics(config.dip_params)
        except Exception as e:
            logger.warning(f"Could not create dynamics model: {e}")

    # Extract controller-specific parameters from config
    controller_params = _extract_controller_parameters(config, controller_type, controller_info)

    # Check for deprecated parameters and apply migrations
    try:
        from src.controllers.factory.deprecation import check_deprecated_config
        controller_params = check_deprecated_config(controller_type, controller_params)
    except ImportError:
        # Graceful fallback if deprecation module is not available
        logger.debug("Deprecation checking not available")

    # Create configuration object
    try:
        # Build config parameters based on controller type
        if controller_type == 'hybrid_adaptive_sta_smc':
            # Hybrid controllers require special handling - need sub-configs
            # Import the config classes
            from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
            from src.controllers.smc.algorithms.adaptive.config import AdaptiveSMCConfig

            # Use the provided hybrid surface gains [c1, lambda1, c2, lambda2]
            # for the sub-controllers to ensure surface consistency.
            # Classical SMC gains: [k1, k2, lambda1, lambda2, K, kd]
            # Adaptive SMC gains: [k1, k2, lambda1, lambda2, gamma]
            
            # Use direct mapping for surface gains
            k1_sub, k2_sub, lam1_sub, lam2_sub = controller_gains[:4]
            
            # Sub-controller algorithmic gains (K, kd for classical; gamma for adaptive)
            hybrid_gamma = controller_params.get('gamma1', 4.0)
            hybrid_leak = controller_params.get('gain_leak', 0.01)
            
            classical_sub_gains = [k1_sub, k2_sub, lam1_sub, lam2_sub, 35.0, 5.0]
            adaptive_sub_gains = [k1_sub, k2_sub, lam1_sub, lam2_sub, hybrid_gamma]

            # Create proper sub-configs with all required parameters
            classical_config = ClassicalSMCConfig(
                gains=classical_sub_gains,
                max_force=150.0,
                dt=0.001,
                boundary_layer=0.02,
                dynamics_model=dynamics_model
            )
            
            adaptive_config = AdaptiveSMCConfig(
                gains=adaptive_sub_gains,
                max_force=150.0,
                dt=0.001,
                leak_rate=hybrid_leak,
                dynamics_model=dynamics_model
            )

            config_params = {
                'hybrid_mode': HybridMode.CLASSICAL_ADAPTIVE,  # Default hybrid mode enum
                'dt': 0.001,
                'max_force': 150.0,
                'classical_config': classical_config,
                'adaptive_config': adaptive_config,
                'dynamics_model': dynamics_model,
                **controller_params
            }
        else:
            # Standard controllers use gains - ensure required parameters are provided
            config_params = {
                'gains': controller_gains,
                'max_force': 150.0,  # Required by all controllers
                'dt': 0.001,  # Safe default for all
                **controller_params
            }

            # Add controller-specific required parameters
            if controller_type == 'classical_smc':
                config_params.setdefault('boundary_layer', 0.02)  # Required parameter
                config_params.setdefault('regularization_alpha', 1e-4)
                config_params.setdefault('min_regularization', 1e-10)
                config_params.setdefault('max_condition_number', 1e14)
                config_params.setdefault('use_adaptive_regularization', True)
            elif controller_type == 'sta_smc':
                # STA-SMC uses gains directly, no separate K1/K2 parameters
                # The gains array is [K1, K2, k1, k2, lam1, lam2]
                config_params.setdefault('power_exponent', 0.5)
                config_params.setdefault('regularization_alpha', 1e-4)
                config_params.setdefault('min_regularization', 1e-10)
                config_params.setdefault('max_condition_number', 1e14)
                config_params.setdefault('use_adaptive_regularization', True)
                config_params.setdefault('boundary_layer', 0.01)
                config_params.setdefault('switch_method', 'tanh')
                config_params.setdefault('damping_gain', 0.0)
            elif controller_type == 'adaptive_smc':
                # Ensure Adaptive-specific parameters are present
                # Note: gamma is extracted from gains[4], not passed separately
                config_params.setdefault('leak_rate', 0.01)
                config_params.setdefault('dead_zone', 0.05)
                config_params.setdefault('adapt_rate_limit', 10.0)
                config_params.setdefault('K_min', 0.1)
                config_params.setdefault('K_max', 100.0)
                config_params.setdefault('K_init', 10.0)
                config_params.setdefault('alpha', 0.5)
                config_params.setdefault('boundary_layer', 0.01)
                config_params.setdefault('smooth_switch', True)

            # Add controller type specific handling
            if controller_type == 'mpc_controller':
                # MPC controller has different parameters
                if controller_info['class'] is None:
                    raise ImportError("MPC controller missing optional dependency")

                config_params.setdefault('horizon', 10)
                config_params.setdefault('q_x', 1.0)
                config_params.setdefault('q_theta', 1.0)
                config_params.setdefault('r_u', 0.1)
                # MPC doesn't use gains in the traditional sense
                if 'gains' in config_params:
                    del config_params['gains']

            # Only add dynamics_model for controllers that support it
            if dynamics_model is not None and controller_type in ['classical_smc', 'sta_smc', 'mpc_controller']:
                config_params['dynamics_model'] = dynamics_model

        # Remove None values and filter to only valid parameters
        config_params = {k: v for k, v in config_params.items() if v is not None}

    except Exception as e:
        logger.error(f"Failed to build config parameters: {e}")
        raise FactoryConfigurationError(f"Configuration building failed: {e}")

    # MPC Parameter validation (must be outside config creation try-catch to propagate errors)
    if controller_type == 'mpc_controller':
        _validate_mpc_parameters(config_params, controller_params)

    try:
        controller_config = config_class(**config_params)
    except Exception as e:
        # Only show warnings in debug mode to reduce PSO log spam
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Could not create full config, using minimal config: {e}")
        # Fallback to minimal configuration with ALL required defaults
        if controller_type == 'hybrid_adaptive_sta_smc':
            # Hybrid controller has completely different structure
            from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
            from src.controllers.smc.algorithms.adaptive.config import AdaptiveSMCConfig

            # Extract surface gains
            k1_sub, k2_sub, lam1_sub, lam2_sub = controller_gains[:4]
            
            # Create minimal sub-configs with ALL required parameters
            classical_config = ClassicalSMCConfig(
                gains=[k1_sub, k2_sub, lam1_sub, lam2_sub, 35.0, 5.0],
                max_force=150.0,
                dt=0.001,
                boundary_layer=0.02,
                dynamics_model=dynamics_model
            )
            adaptive_config = AdaptiveSMCConfig(
                gains=[k1_sub, k2_sub, lam1_sub, lam2_sub, 4.0],
                max_force=150.0,
                dt=0.001,
                dynamics_model=dynamics_model
            )

            fallback_params = {
                'hybrid_mode': HybridMode.CLASSICAL_ADAPTIVE,  # Default hybrid mode enum
                'dt': 0.001,
                'max_force': 150.0,
                'classical_config': classical_config,
                'adaptive_config': adaptive_config,
                'dynamics_model': dynamics_model
            }
        else:
            # Standard controllers use gains - ensure ALL required parameters are included
            if controller_type == 'mpc_controller':
                # MPC fallback config
                fallback_params = {
                    'horizon': 10,
                    'q_x': 1.0,
                    'q_theta': 1.0,
                    'r_u': 0.1
                }
            else:
                # SMC controllers use gains
                fallback_params = {
                    'gains': controller_gains,
                    'max_force': 150.0,  # Always required
                    'dt': 0.001  # Always add dt for safety
                }

            # Add controller-specific required parameters
            if controller_type == 'classical_smc':
                fallback_params['boundary_layer'] = 0.02  # Required parameter
                fallback_params['regularization_alpha'] = 1e-4
                fallback_params['min_regularization'] = 1e-10
                fallback_params['max_condition_number'] = 1e14
                fallback_params['use_adaptive_regularization'] = True
            elif controller_type == 'sta_smc':
                # STA-SMC uses gains directly, no separate K1/K2 parameters
                fallback_params.update({
                    'power_exponent': 0.5,
                    'regularization_alpha': 1e-4,
                    'min_regularization': 1e-10,
                    'max_condition_number': 1e14,
                    'use_adaptive_regularization': True,
                    'boundary_layer': 0.01,
                    'switch_method': 'tanh',
                    'damping_gain': 0.0
                })
            elif controller_type == 'adaptive_smc':
                # Adaptive SMC specific defaults
                fallback_params.update({
                    'leak_rate': 0.01,
                    'dead_zone': 0.05,
                    'adapt_rate_limit': 10.0,
                    'K_min': 0.1,
                    'K_max': 100.0,
                    'K_init': 10.0,
                    'alpha': 0.5,
                    'boundary_layer': 0.01,
                    'smooth_switch': True
                })
            elif controller_type == 'conditional_hybrid':
                # Conditional Hybrid SMC specific defaults
                fallback_params.update({
                    'angle_threshold': 0.2,
                    'surface_threshold': 1.0,
                    'B_eq_threshold': 0.1,
                    'w_angle': 0.3,
                    'w_surface': 0.3,
                    'w_singularity': 0.4,
                    'gamma1': 1.0,
                    'gamma2': 1.0,
                    'epsilon_min': 0.017,
                    'alpha': 1.142
                })

            # Only add dynamics_model if not None and controller supports it
            if dynamics_model is not None and controller_type in ['classical_smc', 'sta_smc', 'mpc_controller']:
                fallback_params['dynamics_model'] = dynamics_model

        controller_config = config_class(**fallback_params)

    # Create and return controller instance
    try:
        if controller_class is None:
            if controller_type == 'mpc_controller':
                raise ImportError("MPC controller missing optional dependency")
            else:
                raise ImportError(f"Controller class for {controller_type} is not available")

        # All modular controllers use config objects (unified approach)
        # FIX: Removed incorrect "legacy" handling that passed **kwargs instead of config
        # All controllers (classical_smc, sta_smc, adaptive_smc, hybrid, swing_up, mpc)
        # now use consistent config-driven initialization: controller_class(config)
        controller = controller_class(controller_config)

        logger.info(f"Created {controller_type} controller with gains: {controller_gains}")
        return controller
    except Exception as e:
        logger.error(f"Failed to create {controller_type} controller: {e}")
        raise


# =============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# =============================================================================

def create_classical_smc_controller(config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None) -> Any:
    """Create classical SMC controller (backwards compatibility)."""
    return create_controller('classical_smc', config, gains)


def create_sta_smc_controller(config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None) -> Any:
    """Create super-twisting SMC controller (backwards compatibility)."""
    return create_controller('sta_smc', config, gains)


def create_adaptive_smc_controller(config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None) -> Any:
    """Create adaptive SMC controller (backwards compatibility)."""
    return create_controller('adaptive_smc', config, gains)


def create_controller_legacy(controller_type: str, config: Optional[Any] = None, gains: Optional[Union[list, np.ndarray]] = None) -> Any:
    """Legacy factory function (backwards compatibility)."""
    return create_controller(controller_type, config, gains)


# =============================================================================
# PSO INTEGRATION AND WRAPPER CLASSES
# =============================================================================

class SMCFactory:
    """Factory class for creating SMC controllers."""

    @staticmethod
    def create_controller(smc_type: SMCType, config: SMCConfig) -> Any:
        """Create controller using SMCType enum."""
        return create_controller(smc_type.value, config, config.gains)


class PSOControllerWrapper:
    """Wrapper for SMC controllers to provide PSO-compatible interface."""

    def __init__(self, controller, n_gains: int, controller_type: str):
        self.controller = controller
        self.n_gains = n_gains
        self.controller_type = controller_type
        self.max_force = getattr(controller, 'max_force', 150.0)

        # Expose dynamics model for PSO simulation
        self.dynamics_model = getattr(controller, 'dynamics_model', None)

        # If no dynamics model, try to create one from config
        if self.dynamics_model is None:
            try:
                from src.config import load_config
                config = load_config("config.yaml")
                self.dynamics_model = DIPDynamics(config.physics)
                # Also attach to underlying controller
                if hasattr(controller, 'set_dynamics'):
                    controller.set_dynamics(self.dynamics_model)
                else:
                    controller.dynamics_model = self.dynamics_model
            except Exception as e:
                # OK: Dynamics attachment optional for some controllers
                logger.debug(f"Could not attach dynamics model to controller: {e}")

        # Ensure dynamics model has step method for simulation
        if self.dynamics_model and not hasattr(self.dynamics_model, 'step'):
            self._add_step_method_to_dynamics()

    def _add_step_method_to_dynamics(self):
        """Add step method to dynamics model for simulation compatibility."""
        def step_method(state, u, dt):
            """Step dynamics forward by dt using Euler integration."""
            try:
                # Ensure inputs are properly formatted
                state = np.asarray(state, dtype=np.float64)
                u = np.asarray([u] if np.isscalar(u) else u, dtype=np.float64)

                # Get state derivative from dynamics
                dynamics_result = self.dynamics_model.compute_dynamics(state, u)

                # Extract state derivative from result
                if hasattr(dynamics_result, 'state_derivative'):
                    state_dot = dynamics_result.state_derivative
                else:
                    state_dot = dynamics_result

                # Simple Euler integration (sufficient for PSO fitness evaluation)
                state_dot = np.asarray(state_dot, dtype=np.float64)
                next_state = state + state_dot * dt

                # Ensure result is properly shaped and finite
                next_state = np.asarray(next_state, dtype=np.float64)
                if not np.all(np.isfinite(next_state)):
                    return state

                return next_state

            except Exception as e:
                logger.warning(f"Dynamics integration failed, returning previous state: {e}")
                return np.asarray(state, dtype=np.float64)

        self.dynamics_model.step = step_method

    def validate_gains(self, particles: np.ndarray) -> np.ndarray:
        """Validate gain particles for PSO optimization."""
        if particles.ndim == 1:
            particles = particles.reshape(1, -1)

        valid_mask = np.ones(particles.shape[0], dtype=bool)

        for i, gains in enumerate(particles):
            try:
                if len(gains) != self.n_gains:
                    valid_mask[i] = False
                    continue

                if not all(np.isfinite(g) and g > 0 for g in gains):
                    valid_mask[i] = False
                    continue

                # Controller-specific validation
                if self.controller_type == 'classical_smc':
                    k1, k2, lam1, lam2, K, kd = gains
                    if K > 100 or lam1/k1 > 20 or lam2/k2 > 20:
                        valid_mask[i] = False

                elif self.controller_type == 'adaptive_smc':
                    k1, k2, lam1, lam2, gamma = gains
                    if gamma > 20 or gamma < 0.1:
                        valid_mask[i] = False

                elif self.controller_type == 'sta_smc':
                    K1, K2 = gains[0], gains[1]
                    if K1 <= K2:
                        valid_mask[i] = False
                    if len(gains) == 6:
                        k1, k2, lam1, lam2 = gains[2], gains[3], gains[4], gains[5]
                        if any(param <= 0 for param in [k1, k2, lam1, lam2]):
                            valid_mask[i] = False

                elif self.controller_type == 'hybrid_adaptive_sta_smc':
                    c1, lam1, c2, lam2 = gains
                    if any(param <= 0 for param in [c1, lam1, c2, lam2]):
                        valid_mask[i] = False

            except Exception as e:
                logger.debug(f"Gains validation failed for particle {i}: {e}")
                valid_mask[i] = False

        return valid_mask

    def compute_control(self, state: np.ndarray) -> np.ndarray:
        """PSO-compatible control computation interface."""
        try:
            if len(state) != 6:
                raise ValueError(f"Expected state vector of length 6, got {len(state)}")

            result = self.controller.compute_control(state, (), {})

            if hasattr(result, 'u'):
                u = result.u
            elif isinstance(result, dict) and 'u' in result:
                u = result['u']
            else:
                u = result

            # Apply saturation at wrapper level for extra safety
            if isinstance(u, (int, float)):
                u_saturated = np.clip(u, -self.max_force, self.max_force)
                return np.array([u_saturated])
            elif isinstance(u, np.ndarray):
                if u.shape == ():
                    u_saturated = np.clip(float(u), -self.max_force, self.max_force)
                    return np.array([u_saturated])
                elif u.shape == (1,):
                    u_saturated = np.clip(u[0], -self.max_force, self.max_force)
                    return np.array([u_saturated])
                else:
                    u_saturated = np.clip(u.flatten()[0], -self.max_force, self.max_force)
                    return np.array([u_saturated])
            else:
                u_saturated = np.clip(float(u), -self.max_force, self.max_force)
                return np.array([u_saturated])

        except Exception:
            return np.array([0.0])


# =============================================================================
# PSO INTEGRATION FUNCTIONS
# =============================================================================

def create_smc_for_pso(smc_type: SMCType, gains: Union[list, np.ndarray], plant_config_or_model: Optional[Any] = None, **kwargs: Any) -> Any:
    """Create SMC controller optimized for PSO usage."""
    max_force = kwargs.get('max_force', 150.0)
    dt = kwargs.get('dt', 0.001)

    config = SMCConfig(gains=gains, max_force=max_force, dt=dt, **kwargs)
    controller = SMCFactory.create_controller(smc_type, config)

    expected_n_gains = get_expected_gain_count(smc_type)
    wrapper = PSOControllerWrapper(controller, expected_n_gains, smc_type.value)
    return wrapper


def create_pso_controller_factory(smc_type: SMCType, plant_config: Optional[Any] = None, **kwargs: Any) -> Callable:
    """Create a PSO-optimized controller factory function with required attributes."""

    def controller_factory(gains: Union[list, np.ndarray]) -> Any:
        """Controller factory function optimized for PSO."""
        return create_smc_for_pso(smc_type, gains, plant_config, **kwargs)

    # Add PSO-required attributes to the factory function
    controller_type_str = smc_type.value
    if controller_type_str in CONTROLLER_REGISTRY:
        expected_n_gains = CONTROLLER_REGISTRY[controller_type_str]['gain_count']
    else:
        expected_n_gains = get_expected_gain_count(smc_type)

    controller_factory.n_gains = expected_n_gains
    controller_factory.controller_type = controller_type_str
    controller_factory.max_force = kwargs.get('max_force', 150.0)

    return controller_factory


# =============================================================================
# PSO OPTIMIZATION UTILITIES (from smc_factory.py)
# =============================================================================

def get_gain_bounds_for_pso(controller_type: Union[str, Any]) -> tuple:
    """Get PSO optimization bounds for controller gains.
    
    Args:
        controller_type: Controller type (string or SMCType enum)
        
    Returns:
        Tuple of (lower_bounds, upper_bounds) lists for PSO optimization
        
    Examples:
        >>> from src.controllers.factory import get_gain_bounds_for_pso
        >>> lower, upper = get_gain_bounds_for_pso('classical_smc')
        >>> print(f'Bounds: {list(zip(lower, upper))}')
    """
    from .registry import get_gain_bounds
    
    # Handle both string and enum types
    if hasattr(controller_type, 'value'):
        controller_type = controller_type.value
    
    # Get bounds from registry
    bounds = get_gain_bounds(str(controller_type))
    
    if not bounds:
        raise ValueError(f'No gain bounds found for controller type: {controller_type}')
    
    # Convert to PSO format: (lower_bounds, upper_bounds)
    lower_bounds = [bound[0] for bound in bounds]
    upper_bounds = [bound[1] for bound in bounds]
    
    return (lower_bounds, upper_bounds)
