#======================================================================================
#================================ src/utils/__init__.py ===============================
#======================================================================================

"""
Utilities package for DIP-SMC-PSO project (beta).

M3 slices ported so far (2026-06-24): types + validation (slice 1), control
primitives / saturation (slice 2), testing.reproducibility / seeding (slice 3),
numerical_stability / safe operations (slice 4), analysis / statistics (slice 5).

NOTE: the analysis package (slice 5) depends on SciPy (scipy.stats). SciPy must
be present in the environment; it is the first scipy dependency in the beta utils
port. See APPLY.md / the audit card.

The source repo's utils package re-exports more domains (infrastructure,
monitoring, visualization) plus the backward-compat `Visualizer`. Those are NOT
ported yet, so importing them here would raise ImportError. This slice-scoped
__init__ deliberately exposes ONLY what exists so far. Later M3 slices should
widen these re-exports as each domain is ported and audited.
"""

from . import analysis
from . import control
from . import numerical_stability
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
    "analysis",
    "control",
    "numerical_stability",
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

__version__ = "0.5.0-m3slice7"

# >>> M3-SLICE6-MONITORING (added by APPLY; idempotent) >>>
# Registers the monitoring + infrastructure subpackages and bumps the utils
# version for M3 slice 6. Guarded so re-applying is a no-op.
try:
    for _m3s6 in ("monitoring", "infrastructure"):
        if _m3s6 not in __all__:
            __all__.append(_m3s6)
except (NameError, AttributeError):
    pass
__version__ = "0.5.0-m3slice7"
# <<< M3-SLICE6-MONITORING <<<
