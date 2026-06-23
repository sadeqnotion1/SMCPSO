#======================================================================================\\\
#=========================== src/optimizer/pso_optimizer.py ===========================\\\
#======================================================================================\\\

"""
PSO optimizer compatibility layer.
This module re-exports the PSO optimizer from its new modular location
for backward compatibility with legacy import paths.
"""

# Re-export PSO optimizer from new location
from ..optimization.algorithms.pso_optimizer import PSOTuner

# Re-export simulate_system_batch for monkeypatching in tests
from ..simulation.engines.vector_sim import simulate_system_batch

__all__ = ['PSOTuner', 'simulate_system_batch']