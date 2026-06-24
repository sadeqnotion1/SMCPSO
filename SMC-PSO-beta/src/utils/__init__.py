#======================================================================================
#================================ src/utils/__init__.py ===============================
#======================================================================================

"""
Utilities package for DIP-SMC-PSO project (beta).

M3 slices ported so far (2026-06-24): types + validation (slice 1), control
primitives / saturation (slice 2), testing.reproducibility / seeding (slice 3).

The source repo's utils package re-exports more domains (analysis,
infrastructure, monitoring, numerical_stability, visualization) plus the
backward-compat `Visualizer`. Those are NOT ported yet, so importing them here
would raise ImportError. This slice-scoped __init__ deliberately exposes ONLY
what exists so far. Later M3 slices should widen these re-exports as each domain
is ported and audited.
"""

from . import control
from . import testing
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
from .testing.reproducibility import set_global_seed

__all__ = [
    "control",
    "testing",
    "ClassicalSMCOutput",
    "AdaptiveSMCOutput",
    "STAOutput",
    "HybridSTAOutput",
    "require_positive",
    "require_finite",
    "require_in_range",
    "require_probability",
    "saturate",
    "set_global_seed",
]

__version__ = "0.3.0-m3slice3"
