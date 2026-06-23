#======================================================================================#======================== src/controllers/factory/__init__.py =========================#======================================================================================
"""
Controller Factory Package

Consolidated factory module after Week 1 aggressive refactoring (18 files -> 6 files).

Primary interfaces:
- create_controller() - Modern factory from base.py
- Registry functions - From registry.py
- Validation - From validation.py
- PSO utilities - From pso_utils.py
- Legacy factory - For backward compatibility (legacy_factory.py)

Structure (Week 1 final):
- base.py: Main factory, thread-safety, PSO integration
- registry.py: Controller metadata and registry
- validation.py: Comprehensive validation framework
- types.py: Type definitions and protocols
- pso_utils.py: PSO optimization utilities
- legacy_factory.py: Backward compatibility (includes deprecation mapping)
- fallback_configs.py: Fallback config classes
"""

# Core factory functions from base.py
from .base import (
    create_controller,
    create_classical_smc_controller,
    create_sta_smc_controller,
    create_adaptive_smc_controller,
    create_controller_legacy,
    create_smc_for_pso,
    create_pso_controller_factory,
    get_gain_bounds_for_pso,
    
    # Thread-safety
    with_factory_lock,
    factory_lock_context,
    get_lock_statistics,
    FactoryLockTimeoutError,
    FactoryDeadlockError,
    
    # Classes
    SMCFactory,
    PSOControllerWrapper,
)

# Registry functions
from .registry import (
    CONTROLLER_REGISTRY,
    CONTROLLER_ALIASES,
    get_controller_info,
    canonicalize_controller_type,
    list_available_controllers,
    list_all_controllers,
    get_controllers_by_category,
    get_controllers_by_complexity,
    get_default_gains,
    get_gain_bounds,
    validate_controller_type,
)

# Validation functions
from .validation import (
    ValidationResult,
    validate_controller_gains,
    validate_configuration,
    validate_state_vector,
    validate_control_output,
    validate_smc_gains,
)

# Type definitions
from .types import (
    StateVector,
    ControlOutput,
    GainsArray,
    ConfigDict,
    ControllerT,
    ConfigValueError,
    ControllerProtocol,
    ConfigurationProtocol,
    SMCType,
    SMCConfig,
)

# Legacy factory (backward compatibility)
from .legacy_factory import (
    create_controller as create_controller_legacy_v1,
    build_controller as build_controller_legacy,
    build_all as build_all_legacy,
    _canonical,
    FactoryConfigurationError,
    UnknownConfigKeyError,
)

# PSO utilities (optional, may fail if dependencies missing)
try:
    from .pso_utils import (
        create_optimized_controller_factory as create_pso_optimized_controller,
    )
except ImportError:
    create_pso_optimized_controller = None

# Fallback configs
from .fallback_configs import (
    ClassicalSMCConfig,
    STASMCConfig,
    AdaptiveSMCConfig,
    HybridAdaptiveSTASMCConfig,
)

# Backward compatibility aliases
create_controller_new = create_controller  # New factory is now primary
SMCProtocol = ControllerProtocol  # Alias for backward compatibility
build_controller = build_controller_legacy  # Legacy API compatibility

__all__ = [
    # Primary factory
    'create_controller',
    'create_classical_smc_controller',
    'create_sta_smc_controller',
    'create_adaptive_smc_controller',
    
    # Registry
    'CONTROLLER_REGISTRY',
    'list_available_controllers',
    'get_default_gains',
    'get_controller_info',
    
    # Validation
    'ValidationResult',
    'validate_controller_gains',
    'validate_smc_gains',
    
    # Types
    'SMCType',
    'SMCConfig',
    'ControllerProtocol',
    'ConfigValueError',
    
    # PSO
    'create_smc_for_pso',
    'get_gain_bounds_for_pso',
    'PSOControllerWrapper',
    
    # Legacy
    'create_controller_legacy',
    'build_controller_legacy',
    'build_controller',  # Backward compatibility alias

    # Thread-safety
    'with_factory_lock',
    'FactoryLockTimeoutError',
]
