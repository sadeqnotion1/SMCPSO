#==========================================================================================\\\
#================ src/utils/numerical_stability/__init__.py ===========================\\\
#==========================================================================================\\\

"""Numerical stability utilities for robust mathematical operations.

This module provides safe mathematical operations that protect against:
- Division by zero and near-zero denominators
- Negative arguments to sqrt and log
- Numerical overflow/underflow
- Catastrophic cancellation

All operations use configurable epsilon thresholds tuned for control system
stability and optimization algorithm convergence.

Example:
    >>> from src.utils.numerical_stability import safe_divide, safe_sqrt
    >>> result = safe_divide(1.0, 1e-15)  # Protected division
    >>> root = safe_sqrt(-0.001)  # Safe sqrt with negative protection
"""

from src.utils.numerical_stability.safe_operations import (
    # Core safe operations
    safe_divide,
    safe_reciprocal,
    safe_sqrt,
    safe_log,
    safe_exp,
    safe_power,
    safe_norm,
    safe_normalize,
    # Constants
    EPSILON_DIV,
    EPSILON_SQRT,
    EPSILON_LOG,
    EPSILON_EXP,
    # Utility functions
    is_safe_denominator,
    clip_to_safe_range,
)

__all__ = [
    # Core operations
    "safe_divide",
    "safe_reciprocal",
    "safe_sqrt",
    "safe_log",
    "safe_exp",
    "safe_power",
    "safe_norm",
    "safe_normalize",
    # Constants
    "EPSILON_DIV",
    "EPSILON_SQRT",
    "EPSILON_LOG",
    "EPSILON_EXP",
    # Utilities
    "is_safe_denominator",
    "clip_to_safe_range",
]
