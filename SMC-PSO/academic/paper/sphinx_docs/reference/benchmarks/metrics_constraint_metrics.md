# benchmarks.metrics.constraint_metrics

**Source:** `src\benchmarks\metrics\constraint_metrics.py`

## Module Overview

Constraint violation metrics for control systems.

This module implements metrics that quantify constraint violations in
control systems. Physical systems have operational limits that must be
respected for safe and feasible operation.

Constraint types:
* **Control Input Limits**: Actuator saturation bounds
* **State Constraints**: Physical or safety limits on system states
* **Rate Constraints**: Limits on control input rates (future extension)

## Complete Source Code

```{literalinclude} ../../../src/benchmarks/metrics/constraint_metrics.py
:language: python
:linenos:
```



## Functions

### `count_control_violations(u, max_force, violation_threshold)`

Count control input constraint violations.

Physical actuators have finite capacity and cannot provide unlimited
force or torque. Violations indicate control demands that exceed
hardware features, potentially leading to:
- Actuator saturation and performance degradation
- Hardware damage or safety hazards
- Loss of control authority

Parameters
----------
u : np.ndarray
    Control inputs of shape (B, N) for B batches, N time steps
max_force : float
    Maximum allowable control magnitude (symmetric bounds: ±max_force)
violation_threshold : float, optional
    Additional margin for violation detection. Default is 0.0.

Returns
-------
float
    Average number of violations per trajectory across batch

Notes
-----
A violation occurs when |u(t)| > max_force + violation_threshold
The threshold allows for numerical tolerance or safety margins.

#### Source Code

```{literalinclude} ../../../src/benchmarks/metrics/constraint_metrics.py
:language: python
:pyobject: count_control_violations
:linenos:
```



### `compute_violation_severity(u, max_force)`

Compute severity of constraint violations.

Beyond counting violations, this metric quantifies how severe the
violations are by measuring the magnitude of constraint exceedance.

Severity = Σ max(0, |u(t)| - max_force) for all t

Parameters
----------
u : np.ndarray
    Control inputs of shape (B, N)
max_force : float
    Maximum allowable control magnitude

Returns
-------
float
    Average violation severity across batch

#### Source Code

```{literalinclude} ../../../src/benchmarks/metrics/constraint_metrics.py
:language: python
:pyobject: compute_violation_severity
:linenos:
```



### `compute_violation_percentage(u, max_force)`

Compute percentage of time steps with violations.

This metric provides a normalized measure of how frequently
constraints are violated during the control trajectory.

Parameters
----------
u : np.ndarray
    Control inputs of shape (B, N)
max_force : float
    Maximum allowable control magnitude

Returns
-------
float
    Percentage of time steps with violations (0-100)

#### Source Code

```{literalinclude} ../../../src/benchmarks/metrics/constraint_metrics.py
:language: python
:pyobject: compute_violation_percentage
:linenos:
```



### `check_state_constraints(x, state_bounds)`

Check violations of state variable constraints.

Many systems have physical or safety limits on state variables:
- Cart position limits (track length)
- Angular limits (cable wrapping, clearance)
- Velocity limits (safety, actuator bandwidth)

Parameters
----------
x : np.ndarray
    State trajectories of shape (B, N+1, S)
state_bounds : dict, optional
    Mapping from state index to (min_value, max_value) bounds.
    If None, no state constraints are checked.

Returns
-------
dict
    Dictionary with constraint violation statistics per state

#### Source Code

```{literalinclude} ../../../src/benchmarks/metrics/constraint_metrics.py
:language: python
:pyobject: check_state_constraints
:linenos:
```



### `compute_constraint_margin(u, max_force)`

Compute margin to constraint violation.

The constraint margin measures how close the control inputs are
to violating constraints. This provides early warning of potential
violations and indicates control robustness.

Margin = min(max_force - |u(t)|) for all t

Parameters
----------
u : np.ndarray
    Control inputs of shape (B, N)
max_force : float
    Maximum allowable control magnitude

Returns
-------
float
    Minimum constraint margin across all trajectories and time steps

#### Source Code

```{literalinclude} ../../../src/benchmarks/metrics/constraint_metrics.py
:language: python
:pyobject: compute_constraint_margin
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import numpy as np`
- `from typing import Optional, Union`
