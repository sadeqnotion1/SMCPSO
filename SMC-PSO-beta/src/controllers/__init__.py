#=====================================================================================
#============================ src/controllers/__init__.py ============================
#=====================================================================================
"""Controllers package (beta).

M5 Slice 1: classical SMC ported (flat `classical_smc.py`).
M5 Slice 2: super-twisting SMC ported (flat `sta_smc.py`, class `SuperTwistingSMC`).
M5 Slice 3: adaptive SMC ported (flat `adaptive_smc.py`, from source
`smc/adaptive_smc.py`, class `AdaptiveSMC`). base.py (M4 S1) provides the
abstract ControllerInterface + shared validators/saturate. This slice-scoped
__init__ exposes ONLY what is ported so far; widen as hybrid/factory land (M5 S4-S5).
"""
from .base import (
    ControllerInterface,
    require_positive,
    require_in_range,
    saturate,
)
from .classical_smc import ClassicalSMC
from .sta_smc import SuperTwistingSMC
from .adaptive_smc import AdaptiveSMC

__all__ = [
    "ControllerInterface",
    "require_positive",
    "require_in_range",
    "saturate",
    "ClassicalSMC",
    "SuperTwistingSMC",
    "AdaptiveSMC",
]
