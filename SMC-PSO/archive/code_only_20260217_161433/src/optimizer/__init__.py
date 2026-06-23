#======================================================================================\\\
#============================= src/optimizer/__init__.py ==============================\\\
#======================================================================================\\\

"""
Optimizer compatibility layer (DEPRECATED).

This module provides backward compatibility by re-exporting optimizer classes
from their new modular locations, allowing legacy import paths to continue working.

.. deprecated:: 0.2.0
   Use :mod:`src.optimization` instead. This compatibility layer will be removed in v1.0.
"""

import warnings

# Issue deprecation warning on import
warnings.warn(
    "src.optimizer is deprecated and will be removed in v1.0. "
    "Use src.optimization instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export PSO optimizer from new location
from ..optimization.algorithms.pso_optimizer import PSOTuner

__all__ = ['PSOTuner']