#======================================================================================
#================================ src/utils/__init__.py ===============================
#======================================================================================

"""
Utilities package for DIP-SMC-PSO project (beta).

M3 FIRST SLICE (2026-06-24): types + validation only.

The source repo's utils package re-exports many domains (analysis,
infrastructure, monitoring, numerical_stability, testing, visualization) plus
backward-compat helpers (saturate, set_global_seed, Visualizer). Those modules
are NOT ported in this slice, so importing them here would raise ImportError.
This slice-scoped __init__ deliberately exposes ONLY the control types and
validation primitives that exist so far. Later M3 slices should widen these
re-exports as each domain is ported and audited.
"""

from . import control
from .control.types import (
    ClassicalSMCOutput,
    AdaptiveSMCOutput,
    STAOutput,
    HybridSTAOutput,
)
from .control.validation import (
    require_positive,
    require_finite,
    require_in_range,
    require_probability,
)

__all__ = [
    "control",
    "ClassicalSMCOutput",
    "AdaptiveSMCOutput",
    "STAOutput",
    "HybridSTAOutput",
    "require_positive",
    "require_finite",
    "require_in_range",
    "require_probability",
]

__version__ = "0.1.0-m3slice1"
