# core.dynamics_full

**Source:** `src\core\dynamics_full.py`

## Module Overview

Full dynamics compatibility layer.
This module re-exports the full dynamics class from its new modular location
for backward compatibility with legacy import paths.

## Complete Source Code

```{literalinclude} ../../../src/core/dynamics_full.py
:language: python
:linenos:
```



## Classes

### `FullDIPParams`

Compatibility class for full DIP parameters.

#### Source Code

```{literalinclude} ../../../src/core/dynamics_full.py
:language: python
:pyobject: FullDIPParams
:linenos:
```

#### Methods (1)

##### `__init__(self, config)`

[View full source →](#method-fulldipparams-__init__)



## Dependencies

This module imports:

- `from ..plant.models.full.dynamics import FullDIPDynamics`
- `from .dynamics import step_rk4_numba, step_euler_numba`
