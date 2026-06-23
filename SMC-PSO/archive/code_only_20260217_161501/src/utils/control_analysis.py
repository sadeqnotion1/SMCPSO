#======================================================================================\\\
#=========================== src/utils/control_analysis.py ============================\\\
#======================================================================================\\\

"""
Control analysis utilities compatibility module.

This module provides backward compatibility for test modules that expect
control analysis utilities at src.utils.control_analysis. All functionality
is re-exported from the actual implementation location.
"""

# Import control analysis functionality
from ..analysis.performance.control_analysis import (
    ControlAnalyzer,
    controllability_matrix,
    observability_matrix,
    check_controllability_observability,
    linearize_dip,
)

__all__ = [
    'ControlAnalyzer',
    'controllability_matrix',
    'observability_matrix',
    'check_controllability_observability',
    'linearize_dip',
]