#======================================================================================
#========== src/controllers/smc/algorithms/conditional_hybrid/__init__.py ============
#======================================================================================

"""
Conditional Hybrid SMC Controller Module.

Implements the Conditional Hybrid Architecture that combines:
- Adaptive SMC baseline (proven 0.036 chattering performance)
- Super-twisting enhancement applied CONDITIONALLY in safe regions
- Avoids B_eq singularities through conditional activation

This architecture addresses the fundamental incompatibility discovered in
the full-state Hybrid Adaptive STA-SMC (Gemini's theoretical proof).
"""

from .config import ConditionalHybridConfig
from .controller import ConditionalHybridController

__all__ = [
    "ConditionalHybridConfig",
    "ConditionalHybridController",
]
