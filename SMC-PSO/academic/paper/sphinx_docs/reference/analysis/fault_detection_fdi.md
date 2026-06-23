# analysis.fault_detection.fdi

**Source:** `src\analysis\fault_detection\fdi.py`

## Module Overview *No module docstring available

.*

## Advanced Mathematical Theory

### Fault Detection & Isolation (FDI)


\begin{align}
\dot{\vec{x}} &= A\vec{x} + B\vec{u} + E\vec{f} \\
\vec{y} &= C\vec{x} + D\vec{u} + F\vec{f}
\end{align}
``` Where $\vec{f}$ is fault vector (actuator, sensor, or component faults). ### Observer-Based FDI **Luenberger observer:** ```{math}
\dot{\hat{\vec{x}}} = A\hat{\vec{x}} + B\vec{u} + L(\vec{y} - C\hat{\vec{x}})
``` **Residual:** ```{math}

\vec{r}(t) = \vec{y}(t) - \hat{\vec{y}}(t) = C(\vec{x} - \hat{\vec{x}})
``` **Fault-free:** $\vec{r}(t) \to 0$ as $t \to \infty$ **Faulty:** $\vec{r}(t) \neq 0$ ### Parity Space Methods **Parity equation:** ```{math}
\vec{r} = W \begin{bmatrix} \vec{y} \\ \vec{u} \end{bmatrix}
``` **Orthogonality condition:** ```{math}

W^T \begin{bmatrix} C \\ D \end{bmatrix} = 0
``` Ensures $\vec{r} = 0$ when fault-free, $\vec{r} \neq 0$ when faulty. ### Kalman Filter-Based FDI **Innovation residual:** ```{math}
\vec{r}_k = \vec{y}_k - C\hat{\vec{x}}_{k|k-1}
``` **Fault-free statistics:** ```{math}

E[\vec{r}_k] = 0, \quad \text{Cov}(\vec{r}_k) = C P_{k|k-1} C^T + R
``` ### Fault Isolation **Structured residuals:** Design $r_i$ sensitive to fault $f_i$, insensitive to $f_j, j \neq i$ **Fault signature matrix:** ```{math}
S = \begin{bmatrix}
s_{11} & s_{12} & \cdots \\
s_{21} & s_{22} & \cdots \\
\vdots & \vdots & \ddots
\end{bmatrix}
``` Where $s_{ij} = 1$ if residual $r_i$ sensitive to fault $f_j$, else $0$. ### Model-Based vs Data-Driven **Model-based:** Uses physics equations, robust to unseen faults, requires accurate model. **Data-driven:** Machine learning, no model required, needs extensive training data. ## Architecture Diagram ```{mermaid}

graph TD A[System] --> B[Sensors] B --> C[Measurements y] C --> D[Observer] E[Control u] --> D D --> F[State Estimate x̂] C --> G[Residual Generator] F --> G G --> H[Residual r] H --> I[Threshold Adapter] I --> J{|r| > τ?} J -->|Yes| K[Fault Detected] J -->|No| L[Normal] K --> M[Fault Isolation] M --> N[Fault Identification] style G fill:#9cf style J fill:#ff9 style K fill:#f99 style L fill:#9f9
``` ## Usage Examples ### Example 1: Basic Initialization ```python
from src.analysis import Component # Initialize component
component = Component(config)
result = component.process(data)
``` ### Example 2: Advanced Configuration ```python
# Configure with custom parameters

config = { 'threshold': 0.05, 'method': 'adaptive'
}
component = Component(config)
``` ### Example 3: Integration Workflow ```python
# Complete analysis workflow
from src.analysis import analyze results = analyze( data=sensor_data, method='enhanced', visualization=True
)
``` ### Example 4: Fault Detection Example ```python
# FDI system usage

from src.analysis.fault_detection import FDISystem fdi = FDISystem(config)
residual = fdi.generate_residual(y, u)
fault = fdi.detect(residual)
``` ### Example 5: Visualization Example ```python
# Generate analysis plots
from src.analysis.visualization import AnalysisPlotter plotter = AnalysisPlotter(style='professional')
fig = plotter.plot_time_series(data)
fig.savefig('analysis.pdf')
```
## Complete Source Code ```

{literalinclude} ../../../src/analysis/fault_detection/fdi.py

:language: python
:linenos:
```

---

## Classes

### `DynamicsProtocol`

**Inherits from:** `Protocol` Protocol defining the expected interface for dynamics models. This protocol ensures type safety and compatibility across different
dynamics model implementations used in fault detection. #### Source Code ```{literalinclude} ../../../src/analysis/fault_detection/fdi.py
:language: python
:pyobject: DynamicsProtocol
:linenos:
``` #### Methods (1) ##### `step(self, state, u, dt)` Advance the system dynamics by one timestep. [View full source →](#method-dynamicsprotocol-step)

### `FDIsystem`

Lightweight, modular Fault Detection and Isolation (FDI) system with

optional adaptive thresholds and CUSUM drift detection. A residual is formed by comparing the one‑step state prediction from a
dynamics model with the actual measurement. If an extended Kalman
filter (EKF) is available it may provide a more statistically
informed residual (future enhancement). The residual norm is
monitored against a threshold; persistent violations indicate a fault. To improve robustness the detector can adapt its threshold based on
recent residual statistics and can optionally use a cumulative sum
(CUSUM) statistic to detect slow drifts. Adaptive thresholding has
been shown to enhance the robustness of fault diagnosis by
automatically adjusting to operating conditions【218697608892619†L682-L687】. CUSUM
methods accumulate deviations from a reference and are sensitive to
faint changes【675426604190490†L699-L722】; however the choice of threshold and
reference value is critical to avoid false alarms【675426604190490†L746-L752】. Attributes
----------
residual_threshold : float Base threshold for the residual norm. Used when adaptive thresholding is disabled or insufficient samples are available.
persistence_counter : int Number of consecutive threshold violations required to declare a fault. Helps filter sporadic spikes.
use_ekf_residual : bool Placeholder for future EKF innovation residual.
residual_states : list[int] Indices of state variables to include in the residual.
residual_weights : list[float], optional Optional weights applied elementwise to the residual before computing the norm.
adaptive : bool adaptive thresholding. When True the threshold is computed as ``mu + threshold_factor * sigma`` over the last ``window_size`` residuals. This dynamic threshold adjusts to changing operating conditions【218697608892619†L682-L687】.
window_size : int Number of recent residuals used to estimate the mean and standard deviation for adaptive thresholding.
threshold_factor : float Multiplicative factor applied to the standard deviation when computing the adaptive threshold. Larger values reduce sensitivity.
cusum_enabled : bool simple CUSUM drift detection. When True the detector accumulates deviations of the residual norm from its running average and compares the sum against ``cusum_threshold`` to detect slow drifts【675426604190490†L699-L722】.
cusum_threshold : float Threshold for the cumulative sum. When the cumulative sum exceeds this value a fault is declared.
hysteresis_enabled : bool hysteresis mechanism to prevent rapid oscillation between OK and FAULT states near threshold boundaries. When False, uses original single-threshold behavior.
hysteresis_upper : float Upper threshold for fault detection when hysteresis is enabled. Residual must exceed this value to trigger fault state. Typically set to threshold * 1.1 (10% deadband).
hysteresis_lower : float Lower threshold for potential fault recovery (future use). Residual must drop below this value for recovery. Typically set to threshold * 0.9 (10% deadband). Notes
-----
* Adaptive thresholding and CUSUM can be enabled independently.
* When both methods are enabled the residual must exceed either the adaptive threshold persistently or the CUSUM threshold to trigger a fault.
* Hysteresis prevents rapid state oscillations near threshold boundaries by creating a deadband between fault trigger and recovery thresholds (Issue #18).
* The FDI system reports status only ("OK"/"FAULT") and does not modify the control command path; external supervisors decide safe-state actions. # [CIT-064] #### Source Code ```{literalinclude} ../../../src/analysis/fault_detection/fdi.py
:language: python
:pyobject: FDIsystem
:linenos:
``` #### Methods (4) ##### `reset(self)` Reset the FDI system state. [View full source →](#method-fdisystem-reset) ##### `_append_to_bounded_history(self, t, residual_norm)` Append to history with memory bounds for production safety. [View full source →](#method-fdisystem-_append_to_bounded_history) ##### `check(self, t, meas, u, dt, dynamics_model)` Check for a fault at the current time step. [View full source →](#method-fdisystem-check) ##### `get_detection_statistics(self)` Get detection statistics for analysis. [View full source →](#method-fdisystem-get_detection_statistics)

---

### `FaultDetectionInterface`

**Inherits from:** `Protocol` Protocol defining the interface for fault detection systems. This interface ensures compatibility across different fault detection
implementations and provides a standard API for testing and usage. #### Source Code ```{literalinclude} ../../../src/analysis/fault_detection/fdi.py
:language: python
:pyobject: FaultDetectionInterface
:linenos:
``` #### Methods (1) ##### `check(self, t, meas, u, dt, dynamics_model)` Check for a fault at the current time step. [View full source →](#method-faultdetectioninterface-check)

---

## Functions

### `_verify_interface()`

Verify that FDIsystem correctly implements FaultDetectionInterface.

#### Source Code ```

{literalinclude} ../../../src/analysis/fault_detection/fdi.py

:language: python
:pyobject: _verify_interface
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `from dataclasses import dataclass, field`
- `from typing import Optional, Tuple, List, Protocol, Union, Any, Dict`
- `import numpy as np`
- `import numpy.typing as npt`
- `import logging`
- `from pathlib import Path`
