# utils.validation.parameter_validators

**Source:** `src\utils\validation\parameter_validators.py`

## Module Overview

Parameter validation utilities for control systems.

Provides functions for validating control parameters to ensure stability
and proper system behavior.

## Complete Source Code

```{literalinclude} ../../../src/utils/validation/parameter_validators.py
:language: python
:linenos:
```



## Functions

### `require_positive(value, name)`

Validate that a numeric value is positive (or non‑negative).

Parameters
----------
value : float or int or None
    The numeric quantity to validate.
name : str
    The name of the parameter (used in the error message).
allow_zero : bool, optional
    When True, a value of exactly zero is allowed; otherwise values must
    be strictly greater than zero.

Returns
-------
float
    The validated value cast to ``float``.

Raises
------
ValueError
    If ``value`` is ``None``, not a finite number, or does not satisfy
    the positivity requirement.

Notes
-----
Many control gains and time constants must be positive to ensure
stability in sliding‑mode and adaptive control laws.

#### Source Code

```{literalinclude} ../../../src/utils/validation/parameter_validators.py
:language: python
:pyobject: require_positive
:linenos:
```



### `require_finite(value, name)`

Validate that a value is finite.

Parameters
----------
value : float or int or None
    The numeric quantity to validate.
name : str
    The name of the parameter.

Returns
-------
float
    The validated value cast to float.

Raises
------
ValueError
    If value is None, infinity, or NaN.

#### Source Code

```{literalinclude} ../../../src/utils/validation/parameter_validators.py
:language: python
:pyobject: require_finite
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
