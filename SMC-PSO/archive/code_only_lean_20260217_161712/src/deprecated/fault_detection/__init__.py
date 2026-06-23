#======================================================================================\\\
#========================== src/fault_detection/__init__.py ===========================\\\
#======================================================================================\\\

"""
Compatibility import for fault detection system.

This module provides backward compatibility for old import paths.
The actual implementation is in src.analysis.fault_detection.
nimport warnings
warnings.warn(
    "src.fault_detection is deprecated. Use src.analysis.fault_detection instead.",
    DeprecationWarning,
    stacklevel=2
)

Usage:
    from src.fault_detection.fdi import FDIsystem      # Old style (works)
    from src.analysis.fault_detection import FDIsystem # New style (preferred)
"""

# Re-export everything from the actual location
from ..analysis.fault_detection import FaultDetectionInterface

__all__ = ["FaultDetectionInterface"]