"""Infrastructure utilities for the SMC-PSO project.

This package groups low-level infrastructure helpers. For the M3 slice-6
monitoring port, only the threading primitives subpackage is required and
shipped; the remaining infrastructure submodules are intentionally deferred.

NOTE: This minimal package initializer was authored additively by the
monitoring migration kit so that ``src.utils.infrastructure.threading`` can be
imported standalone without pulling in not-yet-ported submodules.
"""

from . import threading

__all__ = [
    'threading',
]
