#======================================================================================
#============================ src/utils/control/__init__.py ===========================
#======================================================================================

"""
Control engineering utilities.

M3 first slice (2026-06-24): only the `types` and `validation` subpackages are
ported. The `primitives` subpackage (saturation) is a later M3 slice and is
intentionally NOT imported here yet. Do not add it until it is ported + audited.
"""

from . import types
from . import validation

__all__ = ["types", "validation"]
