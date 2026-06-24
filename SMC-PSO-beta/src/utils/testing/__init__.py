#======================================================================================
#============================ src/utils/testing/__init__.py ===========================
#======================================================================================

"""
Testing and development utilities.

M3 slice 3 (2026-06-24): only the `reproducibility` subpackage (seed management)
is ported. The `dev_tools` and `fault_injection` subpackages are later M3 slices
and are intentionally NOT imported here yet. Do not add them until ported + audited.
"""

from . import reproducibility

__all__ = ["reproducibility"]
