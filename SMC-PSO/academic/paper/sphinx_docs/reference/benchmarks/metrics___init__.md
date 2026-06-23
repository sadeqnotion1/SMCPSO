# benchmarks.metrics.__init__

**Source:** `src\benchmarks\metrics\__init__.py`

## Module Overview Performance

metrics package for control system evaluation

. This package provides metrics for evaluating control system


performance across multiple dimensions: - **Control Metrics**: ISE, ITAE, RMS effort
- **Stability Metrics**: Overshoot, damping, transient response
- **Constraint Metrics**: Violation counting and severity analysis Usage: from src.benchmarks.metrics import compute_all_metrics metrics = compute_all_metrics(t, x, u, max_force=150.0) ## Complete Source Code ```{literalinclude} ../../../src/benchmarks/metrics/__init__.py
:language: python
:linenos:
```

---

## Functions

### `compute_basic_metrics(t, x, u, max_force, angular_indices)`

Compute the basic metrics from original statistical_benchmarks.py. This function maintains compatibility with the original implementation
while using the new modular structure. Parameters
----------
t : np.ndarray Time vector of length N+1
x : np.ndarray State trajectories of shape (B, N+1, S)
u : np.ndarray Control inputs of shape (B, N)
max_force : float Maximum allowable control magnitude
angular_indices : list of int, optional Indices for angular states. Defaults to [1, 2]. Returns
-------
dict Dictionary with metric names and values matching original format #### Source Code ```{literalinclude} ../../../src/benchmarks/metrics/__init__.py
:language: python
:pyobject: compute_basic_metrics
:linenos:
```

---

## `compute_all_metrics(t, x, u, max_force, angular_indices, state_bounds, include_advanced)`

Compute performance metrics. Parameters

t : np.ndarray Time vector of length N+1
x : np.ndarray State trajectories of shape (B, N+1, S)
u : np.ndarray Control inputs of shape (B, N)
max_force : float Maximum allowable control magnitude
angular_indices : list of int, optional Indices for angular states
state_bounds : dict, optional State constraint bounds
include_advanced : bool, optional Whether to include advanced metrics (damping, severity, etc.) Returns
-------
dict dictionary of performance metrics #### Source Code ```{literalinclude} ../../../src/benchmarks/metrics/__init__.py
:language: python
:pyobject: compute_all_metrics
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `import numpy as np`
- `from typing import Dict`
- `from .control_metrics import compute_ise, compute_itae, compute_rms_control_effort`
- `from .stability_metrics import compute_overshoot, compute_peak_time, compute_damping_ratio_estimate`
- `from .constraint_metrics import count_control_violations, compute_violation_severity, compute_violation_percentage, check_state_constraints, compute_constraint_margin`
