# analysis.performance.stability_analysis

**Source:** `src\analysis\performance\stability_analysis.py`

## Module Overview Stability

analysis tools for control systems

.

## Advanced Mathematical Theory

### Lyapunov Stability Theory


V: \mathbb{R}^n \to \mathbb{R}, \quad V(\vec{0}) = 0, \quad V(\vec{x}) > 0 \, \forall \vec{x} \neq \vec{0}
``` **Stability criterion:** ```{math}
\dot{V}(\vec{x}) = \frac{\partial V}{\partial \vec{x}} \cdot f(\vec{x}) < 0 \quad \forall \vec{x} \neq \vec{0}
``` If $\dot{V}(\vec{x}) < 0$, system is **asymptotically stable**. ### Eigenvalue Analysis **Linearized system:** ```{math}

\dot{\vec{x}} = A\vec{x}, \quad A = \frac{\partial f}{\partial \vec{x}}\bigg|_{\vec{x}^*}
``` **Stability conditions:** ```{math}
\begin{align}
\text{Asymptotically stable} &\iff \text{Re}(\lambda_i) < 0 \, \forall i \\
\text{Marginally stable} &\iff \text{Re}(\lambda_i) \leq 0, \text{some } \text{Re}(\lambda_i) = 0 \\
\text{Unstable} &\iff \exists i: \text{Re}(\lambda_i) > 0
\end{align}
``` ### Stability Margins **Gain margin:** ```{math}

GM = \frac{1}{|G(j\omega_{pc})|}
``` Where $\omega_{pc}$ is phase crossover frequency ($\angle G(j\omega_{pc}) = -180°$). **Phase margin:** ```{math}
PM = 180° + \angle G(j\omega_{gc})
``` Where $\omega_{gc}$ is gain crossover frequency ($|G(j\omega_{gc})| = 1$). ### Lyapunov Equation **For linear system** $\dot{\vec{x}} = A\vec{x}$: ```{math}

A^T P + P A = -Q
``` System is stable if $P > 0$ for any $Q > 0$. ### Quadratic Lyapunov Function **Common choice:** ```{math}
V(\vec{x}) = \vec{x}^T P \vec{x}
``` **Time derivative:** ```{math}

\dot{V} = \vec{x}^T (A^T P + P A) \vec{x} = -\vec{x}^T Q \vec{x} < 0
``` ## Architecture Diagram ```{mermaid}
graph TD A[System State] --> B[Linearization] B --> C[Jacobian Matrix] C --> D[Eigenvalue Analysis] D --> E{All Re(λ) < 0?} E -->|Yes| F[Asymptotically Stable] E -->|No| G{Some Re(λ) = 0?} G -->|Yes| H[Marginally Stable] G -->|No| I[Unstable] A --> J[Lyapunov Function] J --> K[Compute V̇] K --> L{V̇ < 0?} L -->|Yes| F L -->|No| M[Check Conditions] F --> N[Stability Margins] N --> O[Gain Margin] N --> P[Phase Margin] style E fill:#ff9 style L fill:#ff9 style F fill:#9f9 style I fill:#f99
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
This module provides stability analysis features including
Lyapunov analysis, eigenvalue analysis, and stability margin computation. ## Complete Source Code ```{literalinclude} ../../../src/analysis/performance/stability_analysis.py
:language: python
:linenos:
```

---

## Classes

### `StabilityAnalysisConfig`

Configuration for stability analysis.

#### Source Code ```

{literalinclude} ../../../src/analysis/performance/stability_analysis.py

:language: python
:pyobject: StabilityAnalysisConfig
:linenos:
```

### `StabilityAnalyzer`

**Inherits from:** `PerformanceAnalyzer` stability analysis for linear and nonlinear systems.

#### Source Code ```

{literalinclude} ../../../src/analysis/performance/stability_analysis.py
:language: python
:pyobject: StabilityAnalyzer
:linenos:
``` #### Methods (37) ##### `__init__(self, config)` Initialize stability analyzer. [View full source →](#method-stabilityanalyzer-__init__) ##### `analyzer_name(self)` Name of the analyzer. [View full source →](#method-stabilityanalyzer-analyzer_name) ##### `required_data_fields(self)` Required data fields for analysis. [View full source →](#method-stabilityanalyzer-required_data_fields) ##### `analyze(self, data)` Perform stability analysis. [View full source →](#method-stabilityanalyzer-analyze) ##### `_analyze_empirical_stability(self, data)` Analyze stability from simulation data. [View full source →](#method-stabilityanalyzer-_analyze_empirical_stability) ##### `_analyze_linear_stability(self, system_matrices)` Analyze stability of linear system. [View full source →](#method-stabilityanalyzer-_analyze_linear_stability) ##### `_analyze_frequency_domain_stability(self, system_matrices)` Analyze stability in frequency domain. [View full source →](#method-stabilityanalyzer-_analyze_frequency_domain_stability) ##### `_analyze_robustness(self, system_matrices, uncertainties)` Analyze robustness to parameter uncertainties. [View full source →](#method-stabilityanalyzer-_analyze_robustness) ##### `_analyze_lyapunov_stability(self, data, system_matrices)` Analyze Lyapunov stability. [View full source →](#method-stabilityanalyzer-_analyze_lyapunov_stability) ##### `_analyze_bibo_stability(self, data)` Analyze bounded-input bounded-output stability. [View full source →](#method-stabilityanalyzer-_analyze_bibo_stability) ##### `_check_state_boundedness(self, states)` Check if states remain bounded. [View full source →](#method-stabilityanalyzer-_check_state_boundedness) ##### `_analyze_trajectory_convergence(self, data)` Analyze trajectory convergence properties. [View full source →](#method-stabilityanalyzer-_analyze_trajectory_convergence) ##### `_analyze_energy_dissipation(self, data)` Analyze energy dissipation properties. [View full source →](#method-stabilityanalyzer-_analyze_energy_dissipation) ##### `_compute_time_series_stability_indicators(self, data)` Compute stability indicators from time series. [View full source →](#method-stabilityanalyzer-_compute_time_series_stability_indicators) ##### `_analyze_eigenvalues(self, eigenvalues)` Analyze eigenvalue properties for stability. [View full source →](#method-stabilityanalyzer-_analyze_eigenvalues) ##### `_check_controllability(self, A, B)` Check system controllability. [View full source →](#method-stabilityanalyzer-_check_controllability) ##### `_check_observability(self, A, C)` Check system observability. [View full source →](#method-stabilityanalyzer-_check_observability) ##### `_compute_continuous_stability_margins(self, A)` Compute stability margins for continuous-time systems. [View full source →](#method-stabilityanalyzer-_compute_continuous_stability_margins) ##### `_analyze_discrete_stability(self, A)` Analyze stability for discrete-time systems. [View full source →](#method-stabilityanalyzer-_analyze_discrete_stability) ##### `_analyze_nyquist_stability(self, frequencies, H)` Analyze stability using Nyquist criterion. [View full source →](#method-stabilityanalyzer-_analyze_nyquist_stability) ##### `_analyze_bode_stability(self, frequencies, H)` Analyze stability from Bode plots. [View full source →](#method-stabilityanalyzer-_analyze_bode_stability) ##### `_compute_stability_margins(self, frequencies, H)` Compute gain and phase margins. [View full source →](#method-stabilityanalyzer-_compute_stability_margins) ##### `_estimate_growth_rate(self, signal)` Estimate growth rate of a signal. [View full source →](#method-stabilityanalyzer-_estimate_growth_rate) ##### `_estimate_convergence_rate(self, times, magnitude)` Estimate convergence rate from trajectory magnitude. [View full source →](#method-stabilityanalyzer-_estimate_convergence_rate) ##### `_analyze_asymptotic_behavior(self, times, magnitude)` Analyze asymptotic behavior of trajectory. [View full source →](#method-stabilityanalyzer-_analyze_asymptotic_behavior) ##### `_check_signal_boundedness(self, signal)` Check if a signal is bounded. [View full source →](#method-stabilityanalyzer-_check_signal_boundedness) ##### `_estimate_empirical_lyapunov_function(self, data)` Estimate empirical Lyapunov function from data. [View full source →](#method-stabilityanalyzer-_estimate_empirical_lyapunov_function) ##### `_analyze_analytical_lyapunov(self, A)` Analyze Lyapunov stability analytically with robust numerical methods. [View full source →](#method-stabilityanalyzer-_analyze_analytical_lyapunov) ##### `_solve_lyapunov_svd(self, A, Q, regularizer)` Solve Lyapunov equation using SVD-based robust method. [View full source →](#method-stabilityanalyzer-_solve_lyapunov_svd) ##### `_estimate_largest_lyapunov_exponent(self, states)` Estimate largest Lyapunov exponent (simplified method). [View full source →](#method-stabilityanalyzer-_estimate_largest_lyapunov_exponent) ##### `_compute_stability_index(self, states)` Compute stability index based on variance growth. [View full source →](#method-stabilityanalyzer-_compute_stability_index) ##### `_analyze_recurrence(self, states)` Analyze recurrence properties (simplified). [View full source →](#method-stabilityanalyzer-_analyze_recurrence) ##### `_compute_damping_ratio_from_eigenvalue(self, eigenvalue)` Compute damping ratio from complex eigenvalue. [View full source →](#method-stabilityanalyzer-_compute_damping_ratio_from_eigenvalue)

### `_compute_robustness_margins(self, A, uncertainties)`

Compute robustness margins (simplified).

[View full source →](#method-stabilityanalyzer-_compute_robustness_margins) ##### `_compute_sensitivity_analysis(self, A)` Compute sensitivity of eigenvalues to parameter changes. [View full source →](#method-stabilityanalyzer-_compute_sensitivity_analysis) ##### `_monte_carlo_robustness(self, A, uncertainties, n_samples)` Monte Carlo robustness analysis. [View full source →](#method-stabilityanalyzer-_monte_carlo_robustness) ##### `_generate_overall_assessment(self, results)` Generate overall stability assessment. [View full source →](#method-stabilityanalyzer-_generate_overall_assessment)

---

## Functions

### `create_stability_analyzer(config)`

Factory function to create stability analyzer. Parameters

config : Dict[str, Any], optional Configuration parameters Returns
-------
StabilityAnalyzer Configured stability analyzer #### Source Code ```{literalinclude} ../../../src/analysis/performance/stability_analysis.py
:language: python
:pyobject: create_stability_analyzer
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `from typing import Dict, List, Optional, Tuple, Any, Union`
- `import numpy as np`
- `from scipy import linalg, signal`
- `import warnings`
- `from dataclasses import dataclass`
- `from ..core.interfaces import PerformanceAnalyzer, AnalysisResult, AnalysisStatus, DataProtocol`
- `from ..core.data_structures import MetricResult, PerformanceMetrics`
