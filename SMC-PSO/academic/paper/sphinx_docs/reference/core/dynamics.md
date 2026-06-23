# core.dynamics

**Source:** `src\core\dynamics.py`

## Module Overview

Dynamics compatibility layer.
This module re-exports the main dynamics class from its new modular location
for backward compatibility with legacy import paths.

## Complete Source Code

```{literalinclude} ../../../src/core/dynamics.py
:language: python
:linenos:
```



## Classes

### `DIPParams`

Compatibility parameter class for DIP dynamics.
This class provides the interface expected by the optimization modules
while working with the new config-based system.

#### Source Code

```{literalinclude} ../../../src/core/dynamics.py
:language: python
:pyobject: DIPParams
:linenos:
```

#### Methods (2)

##### `__init__(self)`

Initialize DIP parameters from keyword arguments.

[View full source →](#method-dipparams-__init__)

##### `from_physics_config(cls, physics_config)`

Create DIPParams from a physics configuration object.

[View full source →](#method-dipparams-from_physics_config)



## Functions

### `rhs_numba(state, u, params)`

**Decorators:** `@njit`

Numba-optimized right-hand side function for DIP dynamics.
This is the same as compute_simplified_dynamics_numba but with parameter unpacking.

Args:
    state: Current state vector [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
    u: Control input (force)
    params: Dynamics parameters object

Returns:
    State derivative vector

#### Source Code

```{literalinclude} ../../../src/core/dynamics.py
:language: python
:pyobject: rhs_numba
:linenos:
```



### `step_euler_numba(state, u, dt, params)`

**Decorators:** `@njit`

Numba-optimized Euler integration step for DIP dynamics.

Args:
    state: Current state vector [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
    u: Control input (force)
    dt: Time step
    params: Dynamics parameters object

Returns:
    Next state vector after one Euler step

#### Source Code

```{literalinclude} ../../../src/core/dynamics.py
:language: python
:pyobject: step_euler_numba
:linenos:
```



### `step_rk4_numba(state, u, dt, params)`

**Decorators:** `@njit`

Numba-optimized 4th-order Runge-Kutta integration step for DIP dynamics.

Args:
    state: Current state vector [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
    u: Control input (force)
    dt: Time step
    params: Dynamics parameters object

Returns:
    Next state vector after one RK4 step

#### Source Code

```{literalinclude} ../../../src/core/dynamics.py
:language: python
:pyobject: step_rk4_numba
:linenos:
```



## Dependencies

This module imports:

- `from ..plant.models.simplified.dynamics import SimplifiedDIPDynamics as DIPDynamics`
- `from ..plant.models.simplified.physics import compute_simplified_dynamics_numba`
- `import numpy as np`
