#==========================================================================================\\\
#============== src/utils/numerical_stability/safe_operations.py ======================\\\
#==========================================================================================\\\

"""Safe mathematical operations with numerical stability guarantees.

This module implements production-grade safe operations for control systems and
optimization algorithms. All functions protect against common numerical issues:

- **Division by zero**: safe_divide, safe_reciprocal
- **Negative domain violations**: safe_sqrt, safe_log
- **Overflow/underflow**: safe_exp, safe_power
- **Numerical instability**: safe_norm, safe_normalize

Mathematical Rationale:
    Epsilon values are chosen based on:
    - Double precision floating point limits (≈2.22e-16)
    - Control system stability margins (≈1e-12 for derivatives)
    - Optimization convergence criteria (≈1e-10 for gradient descent)
    - Physical parameter ranges in DIP system

References:
    - Golub & Van Loan, "Matrix Computations", 4th ed., Ch. 2
    - Higham, "Accuracy and Stability of Numerical Algorithms", 2nd ed.
    - IEEE 754 floating point standard

Example:
    >>> import numpy as np
    >>> from src.utils.numerical_stability import safe_divide, safe_sqrt
    >>> # Protect controller division operations
    >>> control_gain = safe_divide(error, velocity, epsilon=1e-12)
    >>> # Safe normalization for optimization
    >>> unit_vector = safe_normalize(gradient, min_norm=1e-10)
"""

from typing import Union, Optional
import numpy as np
import warnings

# Type aliases for clarity
NumericType = Union[float, np.ndarray]

#==========================================================================================
# Constants: Epsilon Thresholds
#==========================================================================================

# Division safety threshold (Issue #13)
# Chosen to prevent numerical instability in control law derivatives
# Value: 10^-12 ≈ 1000× machine epsilon for double precision
EPSILON_DIV: float = 1e-12

# Square root safety threshold
# Protects against negative values from numerical errors
# Value: 10^-15 allows sqrt near zero while preventing domain errors
EPSILON_SQRT: float = 1e-15

# Logarithm safety threshold
# Prevents log(0) and log(negative) in optimization objectives
# Value: 10^-15 allows log near zero with graceful handling
EPSILON_LOG: float = 1e-15

# Exponential overflow protection
# Prevents exp(x) overflow for large x
# Value: 700 ≈ max safe exponent for exp() in double precision
EPSILON_EXP: float = 700.0

# General small number threshold for comparisons
EPSILON_GENERAL: float = 1e-10


#==========================================================================================
# Core Safe Operations
#==========================================================================================

def safe_divide(
    numerator: NumericType,
    denominator: NumericType,
    epsilon: float = EPSILON_DIV,
    fallback: float = 0.0,
    warn: bool = False,
) -> NumericType:
    """Safe division with epsilon threshold protection against zero division.

    Protects against division by zero and near-zero denominators by replacing
    denominators with magnitude < epsilon with epsilon (preserving sign).

    Mathematical Definition:
        safe_divide(a, b) = a / max(|b|, ε) * sign(b)

    where ε is the safety threshold.

    Args:
        numerator: Dividend (scalar or array)
        denominator: Divisor (scalar or array)
        epsilon: Minimum safe denominator magnitude (default: 1e-12)
        fallback: Value to return if denominator is exactly zero (default: 0.0)
        warn: Issue warning when epsilon protection triggers (default: False)

    Returns:
        Safe division result with same shape as inputs (after broadcasting)

    Raises:
        ValueError: If epsilon is negative or zero

    Example:
        >>> safe_divide(1.0, 2.0)
        0.5
        >>> safe_divide(1.0, 1e-15)  # Protected division
        1000000000000.0
        >>> safe_divide(1.0, 0.0, fallback=np.inf)
        inf
        >>> safe_divide(np.array([1, 2, 3]), np.array([2, 1e-15, 4]))
        array([5.00000000e-01, 2.00000000e+12, 7.50000000e-01])

    Notes:
        - For denominators with |b| < ε, uses sign-preserving replacement
        - For exactly zero denominators, returns fallback value
        - Handles scalar and array inputs via NumPy broadcasting
        - Preserves input dtype for integer inputs (converts to float64)
    """
    if epsilon <= 0:
        raise ValueError(f"Epsilon must be positive, got: {epsilon}")

    # Convert to arrays for unified handling
    num_array = np.asarray(numerator, dtype=float)
    den_array = np.asarray(denominator, dtype=float)

    # Create result array
    result = np.zeros_like(num_array + den_array, dtype=float)  # Broadcasting

    # Handle exactly zero denominators with fallback
    zero_mask = (den_array == 0.0)
    if np.any(zero_mask):
        result[zero_mask] = fallback
        if warn:
            warnings.warn(
                f"Division by exactly zero detected, using fallback={fallback}",
                RuntimeWarning,
                stacklevel=2,
            )

    # Handle near-zero denominators with epsilon protection
    abs_den = np.abs(den_array)
    near_zero_mask = (abs_den < epsilon) & ~zero_mask
    safe_den = np.where(near_zero_mask, epsilon, abs_den)

    # Preserve sign: safe_divide(a, b) = a / (ε * sign(b)) if |b| < ε
    sign_den = np.sign(den_array)
    # Handle sign(0) = 0 edge case (convert to array to support item assignment)
    sign_den = np.atleast_1d(sign_den).copy()
    sign_den[sign_den == 0] = 1.0

    # Compute safe division (suppress numpy warnings since we handle them explicitly)
    with np.errstate(divide='ignore', invalid='ignore'):
        result_temp = num_array / (safe_den * sign_den)
        result = np.where(zero_mask, fallback, result_temp)

    if warn and np.any(near_zero_mask):
        num_protected = np.sum(near_zero_mask)
        warnings.warn(
            f"Protected {num_protected} near-zero divisions with epsilon={epsilon}",
            RuntimeWarning,
            stacklevel=2,
        )

    # Return scalar if inputs were scalar
    if np.isscalar(numerator) and np.isscalar(denominator):
        return float(result.item() if hasattr(result, 'item') else result)
    return result


def safe_reciprocal(
    x: NumericType,
    epsilon: float = EPSILON_DIV,
    fallback: float = 0.0,
    warn: bool = False,
) -> NumericType:
    """Safe reciprocal (1/x) with epsilon protection.

    Convenience wrapper for safe_divide(1.0, x).

    Mathematical Definition:
        safe_reciprocal(x) = 1 / max(|x|, ε) * sign(x)

    Args:
        x: Input value(s) (scalar or array)
        epsilon: Minimum safe magnitude (default: 1e-12)
        fallback: Value for exactly zero inputs (default: 0.0)
        warn: Issue warnings for protected operations (default: False)

    Returns:
        Safe reciprocal with same shape as input

    Example:
        >>> safe_reciprocal(2.0)
        0.5
        >>> safe_reciprocal(1e-15)
        1000000000000.0
        >>> safe_reciprocal(np.array([1, 2, 1e-15]))
        array([1.00000000e+00, 5.00000000e-01, 1.00000000e+12])
    """
    return safe_divide(1.0, x, epsilon=epsilon, fallback=fallback, warn=warn)


def safe_sqrt(
    x: NumericType,
    min_value: float = EPSILON_SQRT,
    warn: bool = False,
) -> NumericType:
    """Safe square root with negative value protection.

    Clips input to [min_value, ∞) before applying sqrt to prevent domain errors
    from numerical noise producing negative values.

    Mathematical Definition:
        safe_sqrt(x) = √(max(x, min_value))

    Args:
        x: Input value(s) (scalar or array)
        min_value: Minimum value to clip to (default: 1e-15)
        warn: Warn if negative values are clipped (default: False)

    Returns:
        Safe square root with same shape as input

    Raises:
        ValueError: If min_value is negative

    Example:
        >>> safe_sqrt(4.0)
        2.0
        >>> safe_sqrt(-0.001)  # Numerical noise
        1e-07
        >>> safe_sqrt(np.array([4, -1e-10, 0]))
        array([2.0000000e+00, 1.0000000e-07, 1.0000000e-07])

    Notes:
        - Designed for control systems where sqrt(x²) may produce negative x
        - min_value should be chosen based on expected numerical precision
        - Use warn=True during development to detect unexpected negatives
    """
    if min_value < 0:
        raise ValueError(f"min_value must be non-negative, got: {min_value}")

    x_array = np.asarray(x, dtype=float)

    # Detect and handle negative values
    negative_mask = x_array < 0
    if np.any(negative_mask) and warn:
        num_negative = np.sum(negative_mask)
        min_negative = np.min(x_array[negative_mask])
        warnings.warn(
            f"Clipped {num_negative} negative values to {min_value}, "
            f"min was {min_negative:.2e}",
            RuntimeWarning,
            stacklevel=2,
        )

    # Clip to safe range and compute sqrt
    safe_x = np.maximum(x_array, min_value)
    result = np.sqrt(safe_x)

    # Return scalar if input was scalar
    if np.isscalar(x):
        return float(result.item() if hasattr(result, 'item') else result)
    return result


def safe_log(
    x: NumericType,
    min_value: float = EPSILON_LOG,
    warn: bool = False,
) -> NumericType:
    """Safe natural logarithm with zero/negative protection.

    Clips input to [min_value, ∞) before applying log to prevent domain errors.

    Mathematical Definition:
        safe_log(x) = ln(max(x, min_value))

    Args:
        x: Input value(s) (scalar or array)
        min_value: Minimum value to clip to (default: 1e-15)
        warn: Warn if values are clipped (default: False)

    Returns:
        Safe logarithm with same shape as input

    Raises:
        ValueError: If min_value is not positive

    Example:
        >>> safe_log(np.e)
        1.0
        >>> safe_log(0.0)
        -34.53877639491069
        >>> safe_log(np.array([1, 1e-20, -0.01]))
        array([  0.        , -34.53877639, -34.53877639])

    Notes:
        - Commonly used in optimization objective functions
        - min_value determines the floor of log output: log(min_value)
        - For log(0) → -∞ behavior, use min_value ≈ 1e-300 (near underflow)
    """
    if min_value <= 0:
        raise ValueError(f"min_value must be positive, got: {min_value}")

    x_array = np.asarray(x, dtype=float)

    # Detect and handle non-positive values
    non_positive_mask = x_array <= 0
    if np.any(non_positive_mask) and warn:
        num_clipped = np.sum(non_positive_mask)
        warnings.warn(
            f"Clipped {num_clipped} non-positive values to {min_value}",
            RuntimeWarning,
            stacklevel=2,
        )

    # Clip to safe range and compute log
    safe_x = np.maximum(x_array, min_value)
    result = np.log(safe_x)

    # Return scalar if input was scalar
    if np.isscalar(x):
        return float(result.item() if hasattr(result, 'item') else result)
    return result


def safe_exp(
    x: NumericType,
    max_value: float = EPSILON_EXP,
    warn: bool = False,
) -> NumericType:
    """Safe exponential with overflow protection.

    Clips input to (-∞, max_value] before applying exp to prevent overflow.

    Mathematical Definition:
        safe_exp(x) = exp(min(x, max_value))

    Args:
        x: Input value(s) (scalar or array)
        max_value: Maximum exponent value (default: 700.0)
        warn: Warn if values are clipped (default: False)

    Returns:
        Safe exponential with same shape as input

    Example:
        >>> safe_exp(0.0)
        1.0
        >>> safe_exp(1000.0)  # Would overflow without protection
        1.0142320547350045e+304
        >>> safe_exp(np.array([-1, 0, 1000]))
        array([3.67879441e-001, 1.00000000e+000, 1.01423205e+304])

    Notes:
        - Default max_value=700 is safe for IEEE 754 double precision
        - exp(700) ≈ 1.01e+304, near overflow limit of 1.79e+308
        - Underflow (exp(-x) → 0) is naturally safe and not clipped
    """
    x_array = np.asarray(x, dtype=float)

    # Detect and handle overflow-prone values
    overflow_mask = x_array > max_value
    if np.any(overflow_mask) and warn:
        num_clipped = np.sum(overflow_mask)
        max_clipped = np.max(x_array[overflow_mask])
        warnings.warn(
            f"Clipped {num_clipped} values to prevent overflow, "
            f"max was {max_clipped:.2e}",
            RuntimeWarning,
            stacklevel=2,
        )

    # Clip to safe range and compute exp
    safe_x = np.minimum(x_array, max_value)
    result = np.exp(safe_x)

    # Return scalar if input was scalar
    if np.isscalar(x):
        return float(result.item() if hasattr(result, 'item') else result)
    return result


def safe_power(
    base: NumericType,
    exponent: NumericType,
    epsilon: float = EPSILON_SQRT,
    max_exp: float = EPSILON_EXP,
    warn: bool = False,
) -> NumericType:
    """Safe exponentiation (base^exponent) with domain and overflow protection.

    Handles negative bases with fractional exponents and prevents overflow.

    Mathematical Definition:
        safe_power(b, e) = sign(b) * |b|^e  for negative b
                         = b^e              for non-negative b
        where b is clipped to |b| ≥ epsilon and e is clipped to |e| ≤ max_exp

    Args:
        base: Base value(s) (scalar or array)
        exponent: Exponent value(s) (scalar or array)
        epsilon: Minimum base magnitude (default: 1e-15)
        max_exp: Maximum exponent magnitude (default: 700.0)
        warn: Warn if clipping occurs (default: False)

    Returns:
        Safe power with same shape as inputs (after broadcasting)

    Example:
        >>> safe_power(2.0, 3.0)
        8.0
        >>> safe_power(-2.0, 3.0)  # Negative base
        -8.0
        >>> safe_power(1e-20, 2.0)  # Small base protected
        1e-30
        >>> safe_power(np.array([2, -2, 1e-20]), 2.0)
        array([4.0e+00, 4.0e+00, 1.0e-30])

    Notes:
        - Handles negative bases by: (-b)^e = sign(-b) * |b|^e
        - Protects small bases to prevent underflow
        - Clips large exponents to prevent overflow
        - Use for robust polynomial and power-law calculations
    """
    base_array = np.asarray(base, dtype=float)
    exp_array = np.asarray(exponent, dtype=float)

    # Handle negative bases
    abs_base = np.abs(base_array)
    sign_base = np.sign(base_array)
    sign_base = np.where(sign_base == 0, 1.0, sign_base)  # Treat zero as positive

    # Protect small bases
    safe_base = np.maximum(abs_base, epsilon)

    # Clip exponents to prevent overflow
    safe_exp = np.clip(exp_array, -max_exp, max_exp)

    # Compute power with absolute base
    result = np.power(safe_base, safe_exp)

    # Apply sign for negative bases (sign^exp pattern)
    # For integer exponents: (-b)^n = b^n if n even, -b^n if n odd
    # For fractional exponents: use principal value (real part)
    is_integer_exp = np.equal(np.mod(exp_array, 1), 0)
    is_odd_exp = np.logical_and(is_integer_exp, np.mod(exp_array, 2) != 0)

    # Apply sign only for odd integer exponents
    result = np.where(is_odd_exp, result * sign_base, result)

    if warn:
        small_base_mask = abs_base < epsilon
        large_exp_mask = np.abs(exp_array) > max_exp
        if np.any(small_base_mask):
            warnings.warn(
                f"Protected {np.sum(small_base_mask)} small bases with epsilon",
                RuntimeWarning,
                stacklevel=2,
            )
        if np.any(large_exp_mask):
            warnings.warn(
                f"Clipped {np.sum(large_exp_mask)} large exponents",
                RuntimeWarning,
                stacklevel=2,
            )

    # Return scalar if inputs were scalar
    if np.isscalar(base) and np.isscalar(exponent):
        return float(result.item() if hasattr(result, 'item') else result)
    return result


def safe_norm(
    vector: np.ndarray,
    ord: Optional[Union[int, float, str]] = 2,
    axis: Optional[int] = None,
    min_norm: float = EPSILON_SQRT,
) -> Union[float, np.ndarray]:
    """Safe vector/matrix norm with zero-norm protection.

    Computes norm with minimum threshold to prevent zero division in
    normalization operations.

    Mathematical Definition:
        safe_norm(v) = max(||v||_p, min_norm)

    where ||·||_p is the p-norm.

    Args:
        vector: Input array (vector or matrix)
        ord: Norm order (default: 2 for Euclidean norm)
             - 1: L1 norm (sum of absolute values)
             - 2: L2 norm (Euclidean)
             - np.inf: L∞ norm (maximum absolute value)
        axis: Axis along which to compute norm (default: None = flatten)
        min_norm: Minimum norm value (default: 1e-15)

    Returns:
        Norm value(s) with minimum threshold applied

    Example:
        >>> safe_norm(np.array([3, 4]))
        5.0
        >>> safe_norm(np.array([1e-20, 1e-20]))
        1e-15
        >>> safe_norm(np.array([[1, 0], [0, 1]]), axis=1)
        array([1.00000000e+00, 1.00000000e+00])

    Notes:
        - Used to protect normalization: v / ||v|| becomes v / safe_norm(v)
        - min_norm should match expected numerical precision of application
        - Preserves norm semantics while preventing degenerate cases
    """
    norm_value = np.linalg.norm(vector, ord=ord, axis=axis)
    return np.maximum(norm_value, min_norm)


def safe_normalize(
    vector: np.ndarray,
    ord: Optional[Union[int, float, str]] = 2,
    axis: Optional[int] = None,
    min_norm: float = EPSILON_SQRT,
    fallback: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Safe vector normalization with zero-norm protection.

    Normalizes vector to unit norm with protection against zero-length vectors.

    Mathematical Definition:
        safe_normalize(v) = v / max(||v||, min_norm)

    Args:
        vector: Input vector(s) to normalize
        ord: Norm order (default: 2 for Euclidean)
        axis: Normalization axis (default: None = flatten)
        min_norm: Minimum norm threshold (default: 1e-15)
        fallback: Value to return for zero vectors (default: zeros)

    Returns:
        Normalized vector with same shape as input

    Example:
        >>> safe_normalize(np.array([3, 4]))
        array([0.6, 0.8])
        >>> safe_normalize(np.array([0, 0]))
        array([0., 0.])
        >>> safe_normalize(np.array([[1, 0], [0, 2]]), axis=1)
        array([[1., 0.],
               [0., 1.]])

    Notes:
        - For zero vectors, returns fallback (default: zero vector)
        - Use in gradient descent, direction finding, unit vector generation
        - Preserves direction while guaranteeing unit magnitude
    """
    vector_array = np.asarray(vector, dtype=float)

    # Compute safe norm
    norm_value = safe_norm(vector_array, ord=ord, axis=axis, min_norm=min_norm)

    # Expand norm dimensions for broadcasting if needed
    if axis is not None and vector_array.ndim > 1:
        norm_value = np.expand_dims(norm_value, axis=axis)

    # Normalize with safe division
    normalized = vector_array / norm_value

    # Handle exactly zero vectors with fallback
    is_zero = np.linalg.norm(vector_array, ord=ord, axis=axis) < min_norm
    if fallback is not None and np.any(is_zero):
        if axis is not None:
            is_zero = np.expand_dims(is_zero, axis=axis)
        normalized = np.where(is_zero, fallback, normalized)

    return normalized


#==========================================================================================
# Utility Functions
#==========================================================================================

def is_safe_denominator(
    denominator: NumericType,
    epsilon: float = EPSILON_DIV,
) -> Union[bool, np.ndarray]:
    """Check if denominator is safe for division (|x| >= epsilon).

    Args:
        denominator: Value(s) to check
        epsilon: Safety threshold (default: 1e-12)

    Returns:
        Boolean or boolean array indicating safety

    Example:
        >>> is_safe_denominator(1.0)
        True
        >>> is_safe_denominator(1e-15)
        False
        >>> is_safe_denominator(np.array([1, 1e-15, -2]))
        array([ True, False,  True])
    """
    den_array = np.asarray(denominator, dtype=float)
    is_safe = np.abs(den_array) >= epsilon

    if np.isscalar(denominator):
        return bool(is_safe)
    return is_safe


def clip_to_safe_range(
    x: NumericType,
    min_value: float = -1e10,
    max_value: float = 1e10,
    warn: bool = False,
) -> NumericType:
    """Clip values to safe numerical range to prevent overflow/underflow.

    Args:
        x: Input value(s)
        min_value: Minimum safe value (default: -1e10)
        max_value: Maximum safe value (default: 1e10)
        warn: Warn if clipping occurs (default: False)

    Returns:
        Clipped values with same shape as input

    Example:
        >>> clip_to_safe_range(1e15)
        10000000000.0
        >>> clip_to_safe_range(np.array([-1e12, 0, 1e12]))
        array([-1.0e+10,  0.0e+00,  1.0e+10])
    """
    x_array = np.asarray(x, dtype=float)
    clipped = np.clip(x_array, min_value, max_value)

    if warn:
        num_clipped = np.sum(x_array != clipped)
        if num_clipped > 0:
            warnings.warn(
                f"Clipped {num_clipped} values to range [{min_value}, {max_value}]",
                RuntimeWarning,
                stacklevel=2,
            )

    if np.isscalar(x):
        return float(clipped)
    return clipped
