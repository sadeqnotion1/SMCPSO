# controllers.mpc.mpc_controller

**Source:** `src\controllers\mpc\mpc_controller.py`

## Module Overview

*No module docstring available.*

## Complete Source Code

```{literalinclude} ../../../src/controllers/mpc/mpc_controller.py
:language: python
:linenos:
```



## Classes

### `MPCWeights`

#### Source Code

```{literalinclude} ../../../src/controllers/mpc/mpc_controller.py
:language: python
:pyobject: MPCWeights
:linenos:
```



### `MPCController`

Linear MPC for the double inverted pendulum on a cart.

State (nx=6): [x, th1, th2, xdot, th1dot, th2dot]
Input (nu=1): u = cart force

#### Source Code

```{literalinclude} ../../../src/controllers/mpc/mpc_controller.py
:language: python
:pyobject: MPCController
:linenos:
```

#### Methods (5)

##### `__init__(self, dynamics_model, horizon, dt, weights, max_force, max_cart_pos, max_theta_dev, use_exact_discretization)`

[View full source →](#method-mpccontroller-__init__)

##### `set_reference(self, ref_fn)`

Set a reference function ref_fn(t) -> R^6 (desired state).

[View full source →](#method-mpccontroller-set_reference)

##### `__call__(self, t, x)`

[View full source →](#method-mpccontroller-__call__)

##### `compute_control(self, t, x0)`

Build and solve a linear MPC QP around the current state x0 at time t.

[View full source →](#method-mpccontroller-compute_control)

##### `_safe_fallback(self, x0)`

Angle-aware, safe fallback:

[View full source →](#method-mpccontroller-_safe_fallback)



## Functions

### `_call_f(dyn, x, u)`

Robustly call continuous‑time dynamics: xdot = f(x,u)
Supports several common method names; last‑resort: finite‑difference via step(., dt).

#### Source Code

```{literalinclude} ../../../src/controllers/mpc/mpc_controller.py
:language: python
:pyobject: _call_f
:linenos:
```



### `_numeric_linearize_continuous(dyn, x_eq, u_eq, eps)`

Finite‑difference linearization around (x_eq, u_eq) using a central
difference with adaptive perturbations.

A continuous‑time dynamics function ``f(x,u)`` is linearised as
``xdot ≈ A (x - x_eq) + B (u - u_eq) + f(x_eq,u_eq)``.  Central
differences are second‑order accurate and reduce truncation error
relative to one‑sided (forward) differences【738473614585036†L239-L256】.
The perturbation for each state is scaled to the magnitude of
``x_eq[i]`` with a floor ``eps``.  This adaptive scaling balances
rounding and truncation errors【738473614585036†L239-L256】.

Parameters
----------
dyn : DoubleInvertedPendulum
    The continuous‑time dynamics model.
x_eq : np.ndarray
    Equilibrium state about which to linearise.
u_eq : float
    Equilibrium input about which to linearise.
eps : float, optional
    Minimum perturbation used when scaling the finite difference.

Returns
-------
Tuple[np.ndarray, np.ndarray]
    Continuous‑time state matrix A and input matrix B.

#### Source Code

```{literalinclude} ../../../src/controllers/mpc/mpc_controller.py
:language: python
:pyobject: _numeric_linearize_continuous
:linenos:
```



### `_discretize_forward_euler(Ac, Bc, dt)`

Simple forward‑Euler discretization (stable for small dt).

#### Source Code

```{literalinclude} ../../../src/controllers/mpc/mpc_controller.py
:language: python
:pyobject: _discretize_forward_euler
:linenos:
```



### `_discretize_exact(Ac, Bc, dt)`

Zero‑order hold (exact) discretization using matrix exponential.

#### Source Code

```{literalinclude} ../../../src/controllers/mpc/mpc_controller.py
:language: python
:pyobject: _discretize_exact
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import logging`
- `from dataclasses import dataclass`
- `from typing import Callable, Optional, Tuple`
- `import numpy as np`
- `from scipy.linalg import expm`
