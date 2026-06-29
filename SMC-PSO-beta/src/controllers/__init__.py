#=====================================================================================
#============================ src/controllers/__init__.py ============================
#=====================================================================================
"""Controllers package (beta).

M5 Slice 1: classical SMC ported (flat `classical_smc.py`).
M5 Slice 2: super-twisting SMC ported (flat `sta_smc.py`, from source
`smc/sta_smc.py`, class `SuperTwistingSMC`). base.py (M4 S1) provides the
abstract ControllerInterface + shared validators/saturate. This slice-scoped
__init__ exposes ONLY what is ported so far; widen as adaptive/hybrid/factory
land (M5 S3-S5).
"""
from .base import (
    ControllerInterface,
    require_positive,
    require_in_range,
    saturate,
)
from .classical_smc import ClassicalSMC
from .sta_smc import SuperTwistingSMC

__all__ = [
    "ControllerInterface",
    "require_positive",
    "require_in_range",
    "saturate",
    "ClassicalSMC",
    "SuperTwistingSMC",
]
