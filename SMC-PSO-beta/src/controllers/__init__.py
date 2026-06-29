#=====================================================================================
#============================ src/controllers/__init__.py ============================
#=====================================================================================
"""Controllers package (beta).

M5 Slice 1: classical SMC ported (flat `classical_smc.py`, from source
`smc/classic_smc.py`). base.py (M4 S1) provides the abstract ControllerInterface
+ shared validators/saturate. This slice-scoped __init__ exposes ONLY what is
ported so far; widen as sta/adaptive/hybrid/factory land (M5 S2-S5).
"""
from .base import (
    ControllerInterface,
    require_positive,
    require_in_range,
    saturate,
)
from .classical_smc import ClassicalSMC

__all__ = [
    "ControllerInterface",
    "require_positive",
    "require_in_range",
    "saturate",
    "ClassicalSMC",
]
