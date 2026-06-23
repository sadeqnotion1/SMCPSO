#======================================================================================\\\
#====================== src/controllers/factory/core/registry.py ======================\\\
#======================================================================================\\\

"""
Controller Registry Management - Centralized Controller Metadata

Manages the central registry of available controllers with comprehensive metadata,
validation rules, and type-safe access patterns.

Consolidates controller registry from core/registry.py and factory_new/registration.py
during Week 1 aggressive factory refactoring (18 files → 6 files).

This module manages:
- CONTROLLER_REGISTRY: Central metadata for all controller types
- Controller aliases and normalization
- Registry access functions with validation
- Default gains and bounds management
"""

from typing import Dict, Any, List
import logging

# Import controller classes with fallback handling
try:
    from src.controllers.smc.algorithms.classical.controller import ModularClassicalSMC
    from src.controllers.smc.algorithms.super_twisting.controller import ModularSuperTwistingSMC
    from src.controllers.smc.algorithms.adaptive.controller import ModularAdaptiveSMC
    from src.controllers.smc.algorithms.hybrid.controller import ModularHybridSMC
    from src.controllers.smc.algorithms.conditional_hybrid.controller import ConditionalHybridController
except ImportError as e:
    logging.warning(f"Failed to import controller classes: {e}")
    # Define placeholder classes for development
    class ModularClassicalSMC:
        pass
    class ModularSuperTwistingSMC:
        pass
    class ModularAdaptiveSMC:
        pass
    class ModularHybridSMC:
        pass
    class ConditionalHybridController:
        pass

# Import configuration classes with fallback handling
try:
    from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
    from src.controllers.smc.algorithms.super_twisting.config import SuperTwistingSMCConfig as STASMCConfig
    from src.controllers.smc.algorithms.adaptive.config import AdaptiveSMCConfig
    from src.controllers.smc.algorithms.hybrid.config import HybridSMCConfig as HybridAdaptiveSTASMCConfig
    from src.controllers.smc.algorithms.conditional_hybrid.config import ConditionalHybridConfig
    CONFIG_CLASSES_AVAILABLE = True
except ImportError:
    from .fallback_configs import (
        ClassicalSMCConfig,
        STASMCConfig,
        AdaptiveSMCConfig,
        HybridAdaptiveSTASMCConfig
    )
    # Define placeholder for conditional hybrid if import fails
    class ConditionalHybridConfig:
        pass
    CONFIG_CLASSES_AVAILABLE = False

# Optional MPC controller
try:
    from src.controllers.mpc.controller import MPCController
    MPC_AVAILABLE = True
except ImportError:
    MPCController = None
    MPC_AVAILABLE = False


# =============================================================================
# CONTROLLER REGISTRY DEFINITION
# =============================================================================

CONTROLLER_REGISTRY: Dict[str, Dict[str, Any]] = {
    'classical_smc': {
        'class': ModularClassicalSMC,
        'config_class': ClassicalSMCConfig,
        'default_gains': [20.0, 15.0, 12.0, 8.0, 35.0, 5.0],  # [k1, k2, λ1, λ2, K, kd] - Optimized for DIP
        'gain_count': 6,
        'gain_structure': '[k1, k2, λ1, λ2, K, kd]',
        'description': 'Classical sliding mode controller with boundary layer',
        'supports_dynamics': True,
        'required_params': ['gains', 'max_force', 'boundary_layer'],
        'gain_bounds': [(1.0, 50.0), (1.0, 50.0), (1.0, 30.0), (1.0, 30.0), (5.0, 100.0), (0.1, 20.0)],
        'stability_margin': 0.1,
        'category': 'classical',
        'complexity': 'medium'
    },
    'sta_smc': {
        'class': ModularSuperTwistingSMC,
        'config_class': STASMCConfig,
        'default_gains': [25.0, 15.0, 20.0, 12.0, 8.0, 6.0],  # [K1, K2, k1, k2, λ1, λ2] - Enhanced for DIP
        'gain_count': 6,
        'gain_structure': '[K1, K2, k1, k2, λ1, λ2]',
        'description': 'Super-twisting sliding mode controller',
        'supports_dynamics': True,
        'required_params': ['gains', 'max_force', 'dt'],
        'gain_bounds': [(3.0, 100.0), (2.0, 50.0), (2.0, 50.0), (2.0, 50.0), (1.0, 40.0), (1.0, 40.0)],
        'stability_margin': 0.15,
        'category': 'advanced',
        'complexity': 'high'
    },
    'adaptive_smc': {
        'class': ModularAdaptiveSMC,
        'config_class': AdaptiveSMCConfig,
        'default_gains': [25.0, 18.0, 15.0, 10.0, 4.0],  # [k1, k2, λ1, λ2, γ] - Aggressive for DIP
        'gain_count': 5,
        'gain_structure': '[k1, k2, λ1, λ2, γ]',
        'description': 'Adaptive sliding mode controller with parameter estimation',
        'supports_dynamics': True,
        'required_params': ['gains', 'max_force', 'dt'],
        'gain_bounds': [(2.0, 60.0), (2.0, 60.0), (2.0, 40.0), (2.0, 40.0), (0.5, 15.0)],
        'stability_margin': 0.2,
        'category': 'adaptive',
        'complexity': 'high'
    },
    'hybrid_adaptive_sta_smc': {
        'class': ModularHybridSMC,
        'config_class': HybridAdaptiveSTASMCConfig,
        'default_gains': [18.0, 12.0, 10.0, 8.0],  # [k1, k2, λ1, λ2] - Enhanced for DIP
        'gain_count': 4,
        'gain_structure': '[k1, k2, λ1, λ2]',
        'description': 'Hybrid adaptive super-twisting sliding mode controller',
        'supports_dynamics': False,  # Uses sub-controllers
        'required_params': ['classical_config', 'adaptive_config', 'hybrid_mode'],
        'gain_bounds': [(2.0, 30.0), (2.0, 30.0), (1.0, 20.0), (1.0, 20.0)],
        'stability_margin': 0.25,
        'category': 'hybrid',
        'complexity': 'very_high'
    },
    'conditional_hybrid': {
        'class': ConditionalHybridController,
        'config_class': ConditionalHybridConfig,
        'default_gains': [20.0, 15.0, 9.0, 4.0],  # [k1, k2, λ1, λ2] - Baseline sliding surface gains
        'gain_count': 4,
        'gain_structure': '[k1, k2, λ1, λ2]',
        'description': 'Conditional hybrid SMC with adaptive baseline and conditional super-twisting activation',
        'supports_dynamics': True,
        'required_params': ['gains', 'max_force', 'angle_threshold', 'surface_threshold', 'B_eq_threshold'],
        'gain_bounds': [(2.0, 50.0), (2.0, 50.0), (1.0, 30.0), (1.0, 30.0)],
        'stability_margin': 0.3,
        'category': 'hybrid',
        'complexity': 'very_high'
    }
}

# Add MPC controller if available
if MPC_AVAILABLE:
    class MPCConfig:
        def __init__(self, horizon: int = 10, q_x: float = 1.0, q_theta: float = 1.0, r_u: float = 0.1, **kwargs: Any) -> None:
            self.horizon = horizon
            self.q_x = q_x
            self.q_theta = q_theta
            self.r_u = r_u
            for key, value in kwargs.items():
                setattr(self, key, value)

    CONTROLLER_REGISTRY['mpc_controller'] = {
        'class': MPCController,
        'config_class': MPCConfig,
        'default_gains': [],  # MPC doesn't use traditional gains
        'gain_count': 0,
        'gain_structure': 'N/A (uses horizon, weights)',
        'description': 'Model predictive controller',
        'supports_dynamics': True,
        'required_params': ['horizon', 'q_x', 'q_theta', 'r_u'],
        'gain_bounds': [],
        'stability_margin': 0.3,
        'category': 'predictive',
        'complexity': 'very_high'
    }


# =============================================================================
# CONTROLLER ALIASES AND NORMALIZATION
# =============================================================================

CONTROLLER_ALIASES = {
    'classic_smc': 'classical_smc',
    'smc_classical': 'classical_smc',
    'smc_v1': 'classical_smc',
    'super_twisting': 'sta_smc',
    'sta': 'sta_smc',
    'adaptive': 'adaptive_smc',
    'hybrid': 'hybrid_adaptive_sta_smc',
    'hybrid_sta': 'hybrid_adaptive_sta_smc',
    'conditional': 'conditional_hybrid',
    'conditional_hybrid_smc': 'conditional_hybrid',
}


# =============================================================================
# REGISTRY ACCESS FUNCTIONS
# =============================================================================

def get_controller_info(controller_type: str) -> Dict[str, Any]:
    """Get controller information from registry with validation.

    Args:
        controller_type: Canonical controller type name

    Returns:
        Controller registry information

    Raises:
        ValueError: If controller type is not recognized
        TypeError: If controller_type is not a string
    """
    if not isinstance(controller_type, str):
        raise TypeError(f"Controller type must be string, got {type(controller_type)}")

    if controller_type not in CONTROLLER_REGISTRY:
        available = sorted(CONTROLLER_REGISTRY.keys())
        raise ValueError(
            f"Unknown controller type '{controller_type}'. "
            f"Available: {available}. "
            f"Use canonicalize_controller_type() for normalization."
        )
    return CONTROLLER_REGISTRY[controller_type].copy()


def canonicalize_controller_type(name: str) -> str:
    """Normalize and alias controller type names.

    Args:
        name: Controller type name to normalize

    Returns:
        Canonical controller type name

    Raises:
        ValueError: If name is not a string or is empty
    """
    if not isinstance(name, str):
        raise ValueError(f"Controller type must be string, got {type(name)}")

    if not name.strip():
        raise ValueError("Controller type cannot be empty")

    key = name.strip().lower().replace('-', '_').replace(' ', '_')
    return CONTROLLER_ALIASES.get(key, key)


def list_available_controllers() -> List[str]:
    """Get list of available controller types.

    Returns:
        Sorted list of controller type names
    """
    return sorted(CONTROLLER_REGISTRY.keys())


def get_controllers_by_category(category: str) -> List[str]:
    """Get controllers by category.

    Args:
        category: Controller category ('classical', 'adaptive', 'advanced', 'hybrid', 'predictive')

    Returns:
        List of controller names in the category
    """
    return [
        name for name, info in CONTROLLER_REGISTRY.items()
        if info.get('category') == category
    ]


def get_controllers_by_complexity(complexity: str) -> List[str]:
    """Get controllers by complexity level.

    Args:
        complexity: Complexity level ('low', 'medium', 'high', 'very_high')

    Returns:
        List of controller names with the specified complexity
    """
    return [
        name for name, info in CONTROLLER_REGISTRY.items()
        if info.get('complexity') == complexity
    ]


def get_default_gains(controller_type: str) -> List[float]:
    """Get default gains for a controller type.

    Args:
        controller_type: Type of controller

    Returns:
        Copy of default gains list

    Raises:
        ValueError: If controller_type is not recognized
    """
    controller_info = get_controller_info(controller_type)
    return controller_info['default_gains'].copy()


def get_gain_bounds(controller_type: str) -> List[tuple]:
    """Get gain bounds for a controller type.

    Args:
        controller_type: Type of controller

    Returns:
        List of (lower, upper) bound tuples

    Raises:
        ValueError: If controller_type is not recognized
    """
    controller_info = get_controller_info(controller_type)
    return controller_info.get('gain_bounds', []).copy()


def validate_controller_type(controller_type: str) -> bool:
    """Check if a controller type is valid.

    Args:
        controller_type: Controller type to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        canonicalized = canonicalize_controller_type(controller_type)
        return canonicalized in CONTROLLER_REGISTRY
    except (ValueError, TypeError):
        return False

def list_all_controllers() -> List[str]:
    """Get list of all registered controller types, including unavailable ones.

    Returns:
        List of all controller type names in the registry
    """
    return sorted(CONTROLLER_REGISTRY.keys())
