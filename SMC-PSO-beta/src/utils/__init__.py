#======================================================================================
#================================ src/utils/__init__.py ===============================
#======================================================================================

"""
Utilities package for DIP-SMC-PSO project (beta).

M3 slices ported so far (2026-06-24): types + validation (slice 1), control
primitives / saturation (slice 2).

The source repo's utils package re-exports many more domains (analysis,
infrastructure, monitoring, numerical_stability, testing, visualization) plus
backward-compat helpers (set_global_seed, Visualizer). Those are NOT ported
yet, so importing them here would raise ImportError. This slice-scoped
__init__ deliberately exposes ONLY what exists so far. Later M3 slices should
widen these re-exports as each domain is ported and audited.
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
from .control.primitives import saturate

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
    "saturate",
]

__version__ = "0.2.0-m3slice2"
