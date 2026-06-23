#======================================================================================\\\
#====================== src/optimization/integration/__init__.py ======================\\\
#======================================================================================\\\

"""
PSO-Factory Integration Module.

Provides advanced integration between PSO optimization and controller factory patterns.
"""

from .pso_factory_bridge import (
    EnhancedPSOFactory,
    PSOFactoryConfig,
    ControllerType,
    create_optimized_controller_factory,
    optimize_classical_smc,
    optimize_adaptive_smc,
    optimize_sta_smc
)

__all__ = [
    'EnhancedPSOFactory',
    'PSOFactoryConfig',
    'ControllerType',
    'create_optimized_controller_factory',
    'optimize_classical_smc',
    'optimize_adaptive_smc',
    'optimize_sta_smc'
]