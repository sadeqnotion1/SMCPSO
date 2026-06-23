# utils.validation.range_validators

**Source:** `src\utils\validation\range_validators.py`

## Module Overview

Range validation utilities for control parameters.

Provides functions for validating that parameters fall within specified ranges,
which is critical for control system stability and performance.

## Complete Source Code

```{literalinclude} ../../../src/utils/validation/range_validators.py
:language: python
:linenos:
```



## Functions

### `require_in_range(value, name)`

Validate that a numeric value lies within a closed or open interval.

Parameters
----------
value : float or int or None
    The numeric quantity to validate.
name : str
    The name of the parameter (used in the error message).
minimum : float
    Lower bound of the allowed interval.
maximum : float
    Upper bound of the allowed interval.
allow_equal : bool, optional
    If True (default) the bounds are inclusive; if False the value
    must satisfy ``minimum < value < maximum``.

Returns
-------
float
    The validated value cast to ``float``.

Raises
------
ValueError
    If ``value`` is ``None``, not finite, or lies outside the
    specified interval.

Notes
-----
Range constraints arise frequently in control law design; for
example, a controllability threshold should be positive but small,
whereas adaptation gains must lie within finite bounds to ensure stability.

#### Source Code

```{literalinclude} ../../../src/utils/validation/range_validators.py
:language: python
:pyobject: require_in_range
:linenos:
```



### `require_probability(value, name)`

Validate that a value is a valid probability (0 <= p <= 1).

Parameters
----------
value : float or int or None
    The probability value to validate.
name : str
    The name of the parameter.

Returns
-------
float
    The validated probability.

Raises
------
ValueError
    If value is not in [0, 1].

#### Source Code

```{literalinclude} ../../../src/utils/validation/range_validators.py
:language: python
:pyobject: require_probability
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import math`
- `from typing import Union`


## Architecture Diagram

```{mermaid}
graph TD
    A[Component] --> B[Subcomponent 1]
    A --> C[Subcomponent 2]
    B --> D[Output]
    C --> D

    style A fill:#e1f5ff
    style D fill:#e8f5e9
```


## Usage Examples

### Example 1: Basic Usage

```python
# Basic usage example
from src.utils import Component

component = Component()
result = component.process(data)
```

## Example 2: Advanced Configuration

```python
# Advanced configuration
component = Component(
    option1=value1,
    option2=value2
)
```

## Example 3: Integration with Framework

```python
# Integration example
from src.simulation import SimulationRunner

runner = SimulationRunner()
runner.use_component(component)
```

## Example 4: Performance Optimization

```python
# Performance-optimized usage
component = Component(enable_caching=True)
```

## Example 5: Error Handling

```python
# Error handling
try:
    result = component.process(data)
except ComponentError as e:
    print(f"Error: {e}")
```
