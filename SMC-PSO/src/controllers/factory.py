#======================================================================================\\
#============================= src/controllers/factory.py =============================\\
#======================================================================================\\

"""
Backward compatibility wrapper for refactored controller factory.

DEPRECATED: Import from src.controllers.factory (subpackage) instead.

This file maintained for backward compatibility with existing code that imports:
    from src.controllers.factory import create_controller
    from src.controllers.factory import SMCType, SMCConfig

New code should import directly from the subpackage:
    from src.controllers.factory import create_controller

The factory has been refactored from a monolithic 1,435-line file into a modular
subpackage with focused modules:
- factory/core.py: Main factory logic
- factory/__init__.py: Public API re-exports

All public APIs remain unchanged. This wrapper ensures zero breaking changes.
"""

import warnings

# Issue deprecation warning for direct imports of this file
warnings.warn(
    "Importing from src.controllers.factory (single file) is deprecated. "
    "Import from src.controllers.factory subpackage instead. "
    "Public API remains unchanged.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from the factory subpackage for backward compatibility
from src.controllers.factory import (  # noqa: F401
    # Main factory functions
    create_controller,
    list_available_controllers,
    list_all_controllers,
    get_default_gains,

    # Enums and config classes
    SMCType,
    SMCConfig,
    SMCFactory,
    PSOControllerWrapper,

    # Support functions
    create_smc_for_pso,
    create_pso_controller_factory,
    get_expected_gain_count,
    get_gain_bounds_for_pso,
    validate_smc_gains,
    SMCGainSpec,

    # Backwards compatibility functions
    create_classical_smc_controller,
    create_sta_smc_controller,
    create_adaptive_smc_controller,
    create_controller_legacy,

    # Constants and registry
    CONTROLLER_REGISTRY,
    CONTROLLER_ALIASES,

    # Exceptions
    ConfigValueError,
    ControllerProtocol,
)

__all__ = [
    # Main functions
    "create_controller",
    "list_available_controllers",
    "list_all_controllers",
    "get_default_gains",

    # Enums and configs
    "SMCType",
    "SMCConfig",
    "SMCFactory",
    "PSOControllerWrapper",

    # Support functions
    "create_smc_for_pso",
    "create_pso_controller_factory",
    "get_expected_gain_count",
    "get_gain_bounds_for_pso",
    "validate_smc_gains",
    "SMCGainSpec",

    # Backwards compatibility
    "create_classical_smc_controller",
    "create_sta_smc_controller",
    "create_adaptive_smc_controller",
    "create_controller_legacy",

    # Constants
    "CONTROLLER_REGISTRY",
    "CONTROLLER_ALIASES",

    # Exceptions
    "ConfigValueError",
    "ControllerProtocol",
]
