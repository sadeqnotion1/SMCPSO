# analysis.core.metrics

**Source:** `src\analysis\core\metrics.py`

## Module Overview Core metric computation framework

.

## Advanced Mathematical Theory

### Core Performance Metrics


J = \sum_{i=1}^n w_i m_i
``` Where $w_i$ are weights, $m_i$ are individual metrics. ### Metric Normalization **Min-max normalization:** ```{math}
m_{norm} = \frac{m - m_{min}}{m_{max} - m_{min}}
``` **Z-score normalization:** ```{math}

m_{norm} = \frac{m - \mu_m}{\sigma_m}
``` ### Composite Metrics **Geometric mean:** ```{math}
M_g = \left(\prod_{i=1}^n m_i\right)^{1/n}
``` **Harmonic mean:** ```{math}

M_h = \frac{n}{\sum_{i=1}^n \frac{1}{m_i}}
``` ### Time-Domain Metrics **Peak time:** ```{math}
t_p = \arg\max_t |y(t) - y_{ss}|
``` **Rise time (10%-90%):** ```{math}

t_r = t_{90\%} - t_{10\%}
``` ### Frequency-Domain Metrics **Bandwidth:** ```{math}
\omega_B = \max\{\omega : |T(j\omega)| \geq \frac{1}{\sqrt{2}}|T(0)|\}
``` **Resonant peak:** ```{math}

M_r = \max_\omega |T(j\omega)|
``` ### Statistical Aggregation **Weighted average:** ```{math}
\bar{m}_w = \frac{\sum w_i m_i}{\sum w_i}
``` **Confidence interval for metric:** ```{math}

\text{CI}_{1-\alpha} = \bar{m} \pm t_{\alpha/2, n-1}\frac{s_m}{\sqrt{n}}
``` ## Architecture Diagram ```{mermaid}
graph TD A[Raw Metrics] --> B{Normalization} B -->|Min-Max| C[Scale [0,1]] B -->|Z-score| D[Standardize] C --> E[Normalized Metrics] D --> E E --> F[Aggregation] F --> G[Weighted Sum] F --> H[Geometric Mean] F --> I[Harmonic Mean] G --> J[Composite Metric] H --> J I --> J J --> K{Uncertainty?} K -->|Yes| L[Compute CI] K -->|No| M[Point Estimate] L --> N[t-interval] N --> O[Final Metric ± CI] M --> O style B fill:#ff9 style F fill:#9cf style O fill:#9f9
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
This module provides the foundation for computing various performance
metrics from simulation data, with emphasis on control engineering
applications and statistical rigor. ## Complete Source Code ```{literalinclude} ../../../src/analysis/core/metrics.py
:language: python
:linenos:
```

---

## Classes

### `BaseMetricCalculator`

**Inherits from:** `MetricCalculator` Base implementation of metric calculator with common functionality.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/metrics.py

:language: python
:pyobject: BaseMetricCalculator
:linenos:
``` #### Methods (4) ##### `__init__(self, validate_inputs)` Initialize base metric calculator. [View full source →](#method-basemetriccalculator-__init__) ##### `compute(self, data)` Compute metrics from simulation data. [View full source →](#method-basemetriccalculator-compute) ##### `_compute_metric(self, metric_name, data)` Compute a specific metric. Override in subclasses. [View full source →](#method-basemetriccalculator-_compute_metric) ##### `supported_metrics(self)` List of supported metrics. [View full source →](#method-basemetriccalculator-supported_metrics)

### `ControlPerformanceMetrics`

**Inherits from:** `BaseMetricCalculator` Calculator for control performance metrics.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/metrics.py
:language: python
:pyobject: ControlPerformanceMetrics
:linenos:
``` #### Methods (10) ##### `__init__(self, reference_tolerance)` Initialize control performance metrics calculator. [View full source →](#method-controlperformancemetrics-__init__) ##### `supported_metrics(self)` List of supported control performance metrics. [View full source →](#method-controlperformancemetrics-supported_metrics) ##### `_compute_metric(self, metric_name, data)` Compute specific control performance metric. [View full source →](#method-controlperformancemetrics-_compute_metric) ##### `_compute_tracking_error_metric(self, metric_name, data, reference, output_indices)` Compute tracking error metrics. [View full source →](#method-controlperformancemetrics-_compute_tracking_error_metric) ##### `_compute_transient_metric(self, metric_name, data, reference, output_indices)` Compute transient response metrics. [View full source →](#method-controlperformancemetrics-_compute_transient_metric) ##### `_compute_control_metric(self, metric_name, data)` Compute control effort metrics. [View full source →](#method-controlperformancemetrics-_compute_control_metric) ##### `_compute_settling_time(self, times, output)` Compute settling time using percentage criteria. [View full source →](#method-controlperformancemetrics-_compute_settling_time) ##### `_compute_overshoot(self, output)` Compute maximum overshoot percentage. [View full source →](#method-controlperformancemetrics-_compute_overshoot) ##### `_compute_rise_time(self, times, output)` Compute rise time (10% to 90% of final value). [View full source →](#method-controlperformancemetrics-_compute_rise_time) ##### `_compute_steady_state_error(self, output, reference)` Compute steady-state error. [View full source →](#method-controlperformancemetrics-_compute_steady_state_error)

### `StabilityMetrics`

**Inherits from:** `BaseMetricCalculator` Calculator for stability-related metrics.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/metrics.py

:language: python
:pyobject: StabilityMetrics
:linenos:
``` #### Methods (4) ##### `supported_metrics(self)` List of supported stability metrics. [View full source →](#method-stabilitymetrics-supported_metrics) ##### `_compute_metric(self, metric_name, data)` Compute specific stability metric. [View full source →](#method-stabilitymetrics-_compute_metric) ##### `_compute_lyapunov_exponent(self, data)` Estimate largest Lyapunov exponent from time series. [View full source →](#method-stabilitymetrics-_compute_lyapunov_exponent) ##### `_compute_bounded_states(self, data, bounds)` Compute fraction of time states remain within bounds. [View full source →](#method-stabilitymetrics-_compute_bounded_states)

### `RobustnessMetrics`

**Inherits from:** `BaseMetricCalculator` Calculator for robustness metrics.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/metrics.py
:language: python
:pyobject: RobustnessMetrics
:linenos:
``` #### Methods (2) ##### `supported_metrics(self)` List of supported robustness metrics. [View full source →](#method-robustnessmetrics-supported_metrics) ##### `_compute_metric(self, metric_name, data)` Compute specific robustness metric. [View full source →](#method-robustnessmetrics-_compute_metric)

---

## Functions

### `create_comprehensive_metrics(data, reference, include_stability, include_robustness)`

Create performance metrics from simulation data. Parameters

data : DataProtocol Simulation data
reference : np.ndarray, optional Reference trajectory for tracking metrics
include_stability : bool, optional Whether to include stability metrics
include_robustness : bool, optional Whether to include robustness metrics
**kwargs Additional parameters for metric calculation Returns
PerformanceMetrics collection of performance metrics #### Source Code ```{literalinclude} ../../../src/analysis/core/metrics.py
:language: python
:pyobject: create_comprehensive_metrics
:linenos:
```

---

### `_get_metric_unit(metric_name)`

Get appropriate unit for a metric.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/metrics.py
:language: python
:pyobject: _get_metric_unit
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from typing import Dict, List, Optional, Tuple, Any`
- `import numpy as np`
- `from scipy import signal, integrate`
- `import warnings`
- `from .interfaces import MetricCalculator, DataProtocol`
- `from .data_structures import MetricResult, PerformanceMetrics`
