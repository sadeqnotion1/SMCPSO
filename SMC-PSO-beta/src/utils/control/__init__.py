#======================================================================================
#============================ src/utils/control/__init__.py ===========================
#======================================================================================

"""
Control engineering utilities.

M3 slices ported so far (2026-06-24):
  - slice 1: `types` and `validation` subpackages.
  - slice 2: `primitives` subpackage (saturation).

The remaining utils domains are later M3 slices and are intentionally NOT
imported here yet. Do not add a subpackage until it is ported + audited.
"""

from . import types
from . import validation
from . import primitives

__all__ = ["types", "validation", "primitives"]
