# analysis.performance.control_metrics

**Source:** `src\analysis\performance\control_metrics.py`

## Module Overview Enhanced

control performance metrics and analysis

.

## Advanced Mathematical Theory

### Integral Performance Indices


\text{ISE} = \int_0^\infty e^2(t) dt
``` Penalizes large errors, emphasizes transient response. **Integral of Absolute Error (IAE):** ```{math}
\text{IAE} = \int_0^\infty |e(t)| dt
``` Linear penalty, balanced transient and steady-state. **Integral of Time-weighted Absolute Error (ITAE):** ```{math}

\text{ITAE} = \int_0^\infty t|e(t)| dt
``` Heavily penalizes long settling time. **Integral of Time-weighted Squared Error (ITSE):** ```{math}
\text{ITSE} = \int_0^\infty t e^2(t) dt
``` ### Control Effort Metrics **Total Variation (TV):** ```{math}

\text{TV}(u) = \int_0^T \left|\frac{du}{dt}\right| dt
``` Measures control chattering. **Control Energy:** ```{math}
E_u = \int_0^T u^2(t) dt
``` ### Overshoot and Settling Time **Percent overshoot:** ```{math}

M_p = \frac{y_{max} - y_{ss}}{y_{ss}} \times 100\%
``` **Settling time** (2% criterion): ```{math}
t_s = \min\{t : |y(\tau) - y_{ss}| \leq 0.02|y_{ss}|, \, \forall \tau \geq t\}
``` ### Damping Ratio Estimation **From overshoot:** ```{math}

\zeta = \frac{-\ln(M_p/100)}{\sqrt{\pi^2 + \ln^2(M_p/100)}}
``` **From peak time:** ```{math}
\omega_d = \frac{\pi}{t_p}, \quad \omega_n = \frac{\omega_d}{\sqrt{1-\zeta^2}}
``` ### RMS Performance **Root Mean Square error:** ```{math}

e_{RMS} = \sqrt{\frac{1}{T}\int_0^T e^2(t) dt}
``` ### Weighted Performance Index **General form:** ```{math}
J = \int_0^\infty [q e^2(t) + r u^2(t)] dt
``` Where $q, r > 0$ are tuning weights. ## Architecture Diagram ```{mermaid}

graph TD A[Error Signal e(t)] --> B[Integral Metrics] A --> C[Time-Weighted Metrics] B --> D[ISE: ∫e²dt] B --> E[IAE: ∫|e|dt] C --> F[ITSE: ∫te²dt] C --> G[ITAE: ∫t|e|dt] A --> H[Response Analysis] H --> I[Overshoot Mp] H --> J[Settling Time ts] H --> K[Rise Time tr] L[Control Signal u(t)] --> M[Control Effort] M --> N[Energy: ∫u²dt] M --> O[Total Variation] D --> P[Metric Aggregation] E --> P F --> P G --> P I --> P J --> P K --> P N --> P P --> Q[Weighted Sum] Q --> R[Performance Index J] style B fill:#9cf style C fill:#fcf style R fill:#9f9
``` ## Usage Examples ### Example 1: Basic Analysis ```python
from src.analysis import Analyzer # Initialize analyzer
analyzer = Analyzer(config)
result = analyzer.analyze(data)
``` ### Example 2: Statistical Validation ```python
# Compute confidence intervals

from src.analysis.validation import compute_confidence_interval ci = compute_confidence_interval(samples, confidence=0.95)
print(f"95% CI: [{ci.lower:.3f}, {ci.upper:.3f}]")
``` ### Example 3: Performance Metrics ```python
# Compute metrics
from src.analysis.performance import compute_all_metrics metrics = compute_all_metrics( time=t, state=x, control=u, reference=r
)
print(f"ISE: {metrics.ise:.2f}, ITAE: {metrics.itae:.2f}")
``` ### Example 4: Batch Analysis ```python
# Analyze multiple trials

results = []
for trial in range(n_trials): result = run_simulation(trial_seed=trial) results.append(analyzer.analyze(result)) # Aggregate statistics
mean_performance = np.mean([r.performance for r in results])
``` ### Example 5: Robustness Analysis ```python
# Parameter sensitivity analysis
from src.analysis.performance import sensitivity_analysis sensitivity = sensitivity_analysis( system=plant, parameters={'mass': (0.8, 1.2), 'length': (0.9, 1.1)}, metric=compute_stability_margin
)
print(f"Most sensitive: {sensitivity.most_sensitive_param}")
```

This module provides control performance analysis tools
including advanced metrics, frequency domain analysis, and statistical
evaluation of controller performance. ## Complete Source Code ```{literalinclude} ../../../src/analysis/performance/control_metrics.py
:language: python
:linenos:
```

---

## Classes

### `AdvancedControlMetrics`

**Inherits from:** `PerformanceAnalyzer` Advanced control performance analyzer with frequency domain capabilities.

#### Source Code ```

{literalinclude} ../../../src/analysis/performance/control_metrics.py
:language: python
:pyobject: AdvancedControlMetrics
:linenos:
``` #### Methods (26) ##### `__init__(self, reference_tolerance, include_frequency_analysis, frequency_range)` Initialize advanced control metrics analyzer. [View full source →](#method-advancedcontrolmetrics-__init__) ##### `analyzer_name(self)` Name of the analyzer. [View full source →](#method-advancedcontrolmetrics-analyzer_name) ##### `required_data_fields(self)` Required data fields for analysis. [View full source →](#method-advancedcontrolmetrics-required_data_fields) ##### `analyze(self, data)` Perform control performance analysis. [View full source →](#method-advancedcontrolmetrics-analyze) ##### `_validate_input_data(self, data)` Validate input data for analysis. [View full source →](#method-advancedcontrolmetrics-_validate_input_data) ##### `_analyze_time_domain(self, data, reference, output_indices)` Perform time domain analysis. [View full source →](#method-advancedcontrolmetrics-_analyze_time_domain) ##### `_analyze_step_response(self, data, output_indices)` Analyze step response characteristics. [View full source →](#method-advancedcontrolmetrics-_analyze_step_response) ##### `_analyze_tracking_performance(self, data, reference, output_indices)` Analyze tracking performance. [View full source →](#method-advancedcontrolmetrics-_analyze_tracking_performance) ##### `_analyze_control_effort(self, data)` Analyze control effort characteristics. [View full source →](#method-advancedcontrolmetrics-_analyze_control_effort) ##### `_analyze_frequency_domain(self, system_matrices)` Perform frequency domain analysis. [View full source →](#method-advancedcontrolmetrics-_analyze_frequency_domain) ##### `_compute_advanced_metrics(self, data, reference, output_indices)` Compute advanced performance metrics. [View full source →](#method-advancedcontrolmetrics-_compute_advanced_metrics) ##### `_compute_settling_time_advanced(self, times, output)` Compute settling time with multiple criteria. [View full source →](#method-advancedcontrolmetrics-_compute_settling_time_advanced) ##### `_compute_overshoot_advanced(self, output)` Compute overshoot analysis. [View full source →](#method-advancedcontrolmetrics-_compute_overshoot_advanced) ##### `_compute_rise_time_advanced(self, times, output)` Compute rise time with multiple definitions. [View full source →](#method-advancedcontrolmetrics-_compute_rise_time_advanced) ##### `_compute_peak_time(self, times, output)` Compute time to peak value. [View full source →](#method-advancedcontrolmetrics-_compute_peak_time) ##### `_analyze_error_convergence(self, times, error_envelope)` Analyze error convergence characteristics. [View full source →](#method-advancedcontrolmetrics-_analyze_error_convergence) ##### `_compute_control_smoothness(self, controls)` Compute control signal smoothness metric. [View full source →](#method-advancedcontrolmetrics-_compute_control_smoothness) ##### `_analyze_saturation(self, controls, saturation_limit)` Analyze control signal saturation. [View full source →](#method-advancedcontrolmetrics-_analyze_saturation) ##### `_compute_bandwidth(self, frequencies, magnitude_db)` Compute -3dB bandwidth. [View full source →](#method-advancedcontrolmetrics-_compute_bandwidth) ##### `_compute_resonance_peak(self, magnitude_db)` Compute resonance peak information. [View full source →](#method-advancedcontrolmetrics-_compute_resonance_peak) ##### `_compute_stability_margins(self, sys)` Compute stability margins. [View full source →](#method-advancedcontrolmetrics-_compute_stability_margins) ##### `_estimate_snr(self, data, reference, output_indices)` Estimate signal-to-noise ratio. [View full source →](#method-advancedcontrolmetrics-_estimate_snr) ##### `_analyze_transient_behavior(self, data, output_indices)` Analyze transient behavior characteristics. [View full source →](#method-advancedcontrolmetrics-_analyze_transient_behavior) ##### `_analyze_settling_behavior(self, times, output)` Analyze settling behavior in detail. [View full source →](#method-advancedcontrolmetrics-_analyze_settling_behavior) ##### `_compute_settling_time_tolerance(self, times, output, tolerance)` Compute settling time for specific tolerance. [View full source →](#method-advancedcontrolmetrics-_compute_settling_time_tolerance) ##### `_analyze_energy_consumption(self, data)` Analyze energy consumption characteristics. [View full source →](#method-advancedcontrolmetrics-_analyze_energy_consumption)

---

## Functions

### `compute_ise(t, x)`

Compute Integral of Squared Error (ISE) for all state variables. The ISE metric integrates the squared state deviations over time:

ISE = ∫₀ᵀ ||x(t)||² dt This metric penalizes large deviations heavily and provides a measure
of overall tracking performance. Lower values indicate better control. Parameters
----------
t : np.ndarray Time vector of length N+1
x : np.ndarray State trajectories of shape (B, N+1, S) for B batches, S states Returns
float ISE value averaged across batch dimension #### Source Code ```{literalinclude} ../../../src/analysis/performance/control_metrics.py
:language: python
:pyobject: compute_ise
:linenos:
```

---

### `compute_itae(t, x)`

Compute Integral of Time-weighted Absolute Error (ITAE). The ITAE metric emphasizes errors that occur later in the trajectory:
ITAE = ∫₀ᵀ t·||x(t)||₁ dt This metric is particularly useful for evaluating settling behavior
and penalizes persistent steady-state errors more heavily than
transient errors early in the response. Parameters
----------
t : np.ndarray Time vector of length N+1
x : np.ndarray State trajectories of shape (B, N+1, S) Returns
float ITAE value averaged across batch dimension #### Source Code ```{literalinclude} ../../../src/analysis/performance/control_metrics.py
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
-------
float RMS control effort averaged across batch dimension #### Source Code ```{literalinclude} ../../../src/analysis/performance/control_metrics.py
:language: python
:pyobject: compute_rms_control_effort
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `from typing import Dict, List, Optional, Tuple, Any, Union`
- `import numpy as np`
- `from scipy import signal, optimize, integrate`
- `import warnings`
- `from ..core.interfaces import PerformanceAnalyzer, AnalysisResult, AnalysisStatus, DataProtocol`
- `from ..core.data_structures import MetricResult, PerformanceMetrics, SimulationData`
- `from ..core.metrics import ControlPerformanceMetrics`
