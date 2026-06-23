# benchmarks.metrics.stability_metrics

**Source:** `src\benchmarks\metrics\stability_metrics.py`

## Module Overview Stability

and transient response metrics for control systems

. This module implements metrics that characterize the stability and


transient behavior of controlled systems. These metrics are essential
for evaluating controller robustness and dynamic performance. Metrics implemented:
* **Maximum Overshoot**: Peak deviation from desired trajectory
* **Settling Time**: Time to reach steady-state (future extension)
* **Rise Time**: Time to reach target (future extension) ## Complete Source Code ```{literalinclude} ../../../src/benchmarks/metrics/stability_metrics.py
:language: python
:linenos:
```

---

## Classes

### `StabilityMetrics`

Stability analysis metrics for control system performance assessment.

This class provides a convenient interface to stability-related metrics including overshoot, peak time, and damping ratio estimation.

#### Source Code

```{literalinclude} ../../../src/benchmarks/metrics/stability_metrics.py
:language: python
:pyobject: StabilityMetrics
:linenos:
``` #### Methods (5) ##### `__init__(self)` Initialize the stability metrics analyzer. [View full source →](#method-stabilitymetrics-__init__) ##### `overshoot(x, angular_indices)` Compute percentage overshoot for system response. [View full source →](#method-stabilitymetrics-overshoot) ##### `peak_time(t, x, state_index)` Compute time to peak response. [View full source →](#method-stabilitymetrics-peak_time) ##### `damping_ratio(x, state_index)` Estimate damping ratio from response characteristics. [View full source →](#method-stabilitymetrics-damping_ratio) ##### `analyze_stability(self, t, x, state_index)` stability analysis of system response. [View full source →](#method-stabilitymetrics-analyze_stability)

---

## Functions

### `compute_overshoot(x, angular_indices)`

Compute maximum overshoot across specified state variables. For control systems, overshoot measures the maximum deviation from

the desired trajectory. For pendulum systems, this typically focuses
on angular states where overshoot can lead to instability. Mathematical Definition:
Overshoot = max(|x(t)|) for t ∈ [0, T] Parameters
----------
x : np.ndarray State trajectories of shape (B, N+1, S) for B batches, S states
angular_indices : list of int, optional Indices of angular states to analyze. Defaults to [1, 2] for typical double pendulum configuration. Returns
-------
float Maximum overshoot averaged across batch dimension Notes
-----
For pendulum systems, excessive overshoot in angular states can
lead to:
- Loss of linearization validity (large angle assumption)
- Physical constraint violations (cable wrapping)
- Reduced stability margins #### Source Code ```{literalinclude} ../../../src/benchmarks/metrics/stability_metrics.py
:language: python
:pyobject: compute_overshoot
:linenos:
```

---

### `compute_peak_time(t, x, state_index)`

Compute time to reach maximum overshoot for specified state. Parameters
----------
t : np.ndarray Time vector of length N+1
x : np.ndarray State trajectories of shape (B, N+1, S)
state_index : int Index of state variable to analyze Returns
float Peak time averaged across batch dimension #### Source Code ```{literalinclude} ../../../src/benchmarks/metrics/stability_metrics.py
:language: python
:pyobject: compute_peak_time
:linenos:
```

---

### `compute_damping_ratio_estimate(x, state_index)`

Estimate damping ratio from overshoot characteristics. For second-order systems, the damping ratio ζ can be estimated from

the overshoot using: ζ ≈ -ln(OS/100) / √(π² + ln²(OS/100)) Parameters
----------
x : np.ndarray State trajectories of shape (B, N+1, S)
state_index : int Index of state variable to analyze Returns
-------
float Estimated damping ratio #### Source Code ```{literalinclude} ../../../src/benchmarks/metrics/stability_metrics.py
:language: python
:pyobject: compute_damping_ratio_estimate
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `import numpy as np`
