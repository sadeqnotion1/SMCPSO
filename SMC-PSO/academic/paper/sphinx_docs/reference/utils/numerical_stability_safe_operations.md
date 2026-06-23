# utils.numerical_stability.safe_operations

**Source:** `src\utils\numerical_stability\safe_operations.py`

## Module Overview

Safe mathematical operations with numerical stability guarantees.

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

## Complete Source Code

```{literalinclude} ../../../src/utils/numerical_stability/safe_operations.py
:language: python
:linenos:
```



## Functions

### `safe_divide(numerator, denominator, epsilon, fallback, warn)`

Safe division with epsilon threshold protection against zero division.

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

#### Source Code

```{literalinclude} ../../../src/utils/numerical_stability/safe_operations.py
:language: python
:pyobject: safe_divide
:linenos:
```



### `safe_reciprocal(x, epsilon, fallback, warn)`

Safe reciprocal (1/x) with epsilon protection.

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

#### Source Code

```{literalinclude} ../../../src/utils/numerical_stability/safe_operations.py
:language: python
:pyobject: safe_reciprocal
:linenos:
```



### `safe_sqrt(x, min_value, warn)`

Safe square root with negative value protection.

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

#### Source Code

```{literalinclude} ../../../src/utils/numerical_stability/safe_operations.py
:language: python
:pyobject: safe_sqrt
:linenos:
```



### `safe_log(x, min_value, warn)`

Safe natural logarithm with zero/negative protection.

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

#### Source Code

```{literalinclude} ../../../src/utils/numerical_stability/safe_operations.py
:language: python
:pyobject: safe_log
:linenos:
```



### `safe_exp(x, max_value, warn)`

Safe exponential with overflow protection.

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

#### Source Code

```{literalinclude} ../../../src/utils/numerical_stability/safe_operations.py
:language: python
:pyobject: safe_exp
:linenos:
```



### `safe_power(base, exponent, epsilon, max_exp, warn)`

Safe exponentiation (base^exponent) with domain and overflow protection.

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

#### Source Code

```{literalinclude} ../../../src/utils/numerical_stability/safe_operations.py
:language: python
:pyobject: safe_power
:linenos:
```



### `safe_norm(vector, ord, axis, min_norm)`

Safe vector/matrix norm with zero-norm protection.

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

#### Source Code

```{literalinclude} ../../../src/utils/numerical_stability/safe_operations.py
:language: python
:pyobject: safe_norm
:linenos:
```



### `safe_normalize(vector, ord, axis, min_norm, fallback)`

Safe vector normalization with zero-norm protection.

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

#### Source Code

```{literalinclude} ../../../src/utils/numerical_stability/safe_operations.py
:language: python
:pyobject: safe_normalize
:linenos:
```



### `is_safe_denominator(denominator, epsilon)`

Check if denominator is safe for division (|x| >= epsilon).

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

#### Source Code

```{literalinclude} ../../../src/utils/numerical_stability/safe_operations.py
:language: python
:pyobject: is_safe_denominator
:linenos:
```



### `clip_to_safe_range(x, min_value, max_value, warn)`

Clip values to safe numerical range to prevent overflow/underflow.

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

#### Source Code

```{literalinclude} ../../../src/utils/numerical_stability/safe_operations.py
:language: python
:pyobject: clip_to_safe_range
:linenos:
```



## Dependencies

This module imports:

- `from typing import Union, Optional`
- `import numpy as np`
- `import warnings`


## Advanced Mathematical Theory

### Numerical Utilities Theory

(Detailed mathematical theory for numerical utilities to be added...)

**Key concepts:**
- Mathematical foundations
- Algorithmic principles
- Performance characteristics
- Integration patterns


## Architecture Diagram

\`\`\`{mermaid}
graph TD
    A[Component] --> B[Subcomponent 1]
    A --> C[Subcomponent 2]
    B --> D[Output]
    C --> D

    style A fill:#e1f5ff
    style D fill:#e8f5e9
\`\`\`


## Usage Examples

### Example 1: Basic Usage

\`\`\`python
from src.utils.numerical_stability_safe_operations import Component

component = Component()
result = component.process(data)
\`\`\`

### Example 2: Advanced Configuration

\`\`\`python
component = Component(
    option1=value1,
    option2=value2
)
\`\`\`

### Example 3: Integration with Simulation

\`\`\`python
# Integration example

for k in range(num_steps):
    result = component.process(x)
    x = update(x, result)
\`\`\`

## Example 4: Performance Optimization

\`\`\`python
component = Component(enable_caching=True)
\`\`\`

### Example 5: Error Handling

\`\`\`python
try:
    result = component.process(data)
except ComponentError as e:
    print(f"Error: {e}")
\`\`\`
