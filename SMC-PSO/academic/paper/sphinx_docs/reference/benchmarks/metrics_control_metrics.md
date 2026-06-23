# benchmarks.metrics.control_metrics

**Source:** `src\benchmarks\metrics\control_metrics.py`

## Module Overview Control

performance metrics for dynamic systems

. This module computes fundamental control engineering metrics that measure


the quality of tracking performance and control effort. These metrics are
derived from classical control theory and provide quantitative measures
of system performance. Metrics implemented:
* **ISE (Integral of Squared Error)**: Measures cumulative tracking error
* **ITAE (Integral of Time-weighted Absolute Error)**: Emphasizes late-time errors
* **RMS Control Effort**: Measures actuator usage and energy consumption ## Complete Source Code ```{literalinclude} ../../../src/benchmarks/metrics/control_metrics.py
:language: python
:linenos:
```

---

## Functions

### `compute_ise(t, x)`

Compute Integral of Squared Error (ISE) for all state variables. The ISE metric integrates the squared state deviations over time:
ISE = ∫₀ᵀ ||x(t)||² dt This metric penalizes large deviations heavily and provides a measure
of overall tracking performance. Lower values indicate better control. Parameters
----------
t : np.ndarray Time vector of length N+1
x : np.ndarray State trajectories of shape (B, N+1, S) for B batches, S states Returns
-------
float ISE value averaged across batch dimension #### Source Code ```{literalinclude} ../../../src/benchmarks/metrics/control_metrics.py
:language: python
:pyobject: compute_ise
:linenos:
```

---

## `compute_itae(t, x)`

Compute Integral of Time-weighted Absolute Error (ITAE). The ITAE metric emphasizes errors that occur later in the trajectory:

ITAE = ∫₀ᵀ t·||x(t)||₁ dt This metric is particularly useful for evaluating settling behavior
and penalizes persistent steady-state errors more heavily than
transient errors early in the response. Parameters
----------
t : np.ndarray Time vector of length N+1
x : np.ndarray State trajectories of shape (B, N+1, S) Returns
-------
float ITAE value averaged across batch dimension #### Source Code ```{literalinclude} ../../../src/benchmarks/metrics/control_metrics.py
:language: python
:pyobject: compute_itae
:linenos:
```

---

### `compute_rms_control_effort(u)`

Compute Root Mean Square (RMS) control effort. The RMS control effort measures the average magnitude of control inputs:
RMS = √(⟨u²(t)⟩) This metric quantifies actuator usage and energy consumption. Lower
values indicate more efficient control that requires less actuation. Parameters
----------
u : np.ndarray Control input trajectories of shape (B, N) Returns
float RMS control effort averaged across batch dimension #### Source Code ```{literalinclude} ../../../src/benchmarks/metrics/control_metrics.py
:language: python
:pyobject: compute_rms_control_effort
:linenos:
```

---

### `calculate_control_metrics(t, x, u)`

Calculate control performance metrics. This function computes all available control performance metrics in one call,

providing a assessment of control system performance. Parameters
----------
t : np.ndarray Time vector of shape (N+1,)
x : np.ndarray State trajectories of shape (B, N+1, S) for B batches, S states
u : np.ndarray Control input trajectories of shape (B, N, U) for U control inputs Returns
-------
dict Dictionary containing all computed metrics: - 'ise': Integral of Squared Error - 'itae': Integral of Time-weighted Absolute Error - 'rms_control': RMS Control Effort Examples
--------
>>> metrics = calculate_control_metrics(t, x, u)
>>> print(f"ISE: {metrics['ise']:.3f}")
>>> print(f"ITAE: {metrics['itae']:.3f}")
>>> print(f"RMS Control: {metrics['rms_control']:.3f}") #### Source Code ```{literalinclude} ../../../src/benchmarks/metrics/control_metrics.py
:language: python
:pyobject: calculate_control_metrics
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `import numpy as np`
