# benchmarks.statistical_benchmarks_v2

**Source:** `src\benchmarks\statistical_benchmarks_v2.py`

## Module Overview Statistical

benchmarking utilities for the Double Inverted Pendulum project

. This is the refactored version using modular architecture while maintaining


full backward compatibility with the original statistical_benchmarks.py. The module now delegates to specialized submodules:
- **metrics/**: Performance metric calculations
- **core/**: Trial execution and orchestration
- **statistics/**: Confidence interval analysis This refactoring provides:
* **Modularity**: Clear separation of concerns
* **Extensibility**: Easy addition of new metrics or analysis methods
* **Maintainability**: Smaller, focused modules
* **Testability**: Individual components can be tested in isolation
* **Compatibility**: Original API preserved for existing code Usage remains identical to the original: from src.benchmarks.statistical_benchmarks_v2 import run_trials metrics_list, ci_results = run_trials(controller_factory, cfg) ## Architecture Diagram ```{mermaid}
graph TD A[Controller Factory] --> B[Multi-Trial Execution] B --> C{For Each Trial i=1..N} C --> D[Simulation] D --> E[Compute Metrics] E --> F[Metrics Collection] F --> G{All Trials Done?} G -->|No| C G -->|Yes| H[Statistical Analysis] H --> I[Confidence Intervals] H --> J[Hypothesis Tests] H --> K[Distribution Fitting] I --> L[Results Package] J --> L K --> L L --> M[Validation Report] style B fill:#9cf style E fill:#fcf style H fill:#ff9 style L fill:#9f9 style M fill:#9f9
``` **Data Flow:**
1. Controller factory creates instances for each trial
2. Execute $N$ independent simulations with different seeds
3. Compute performance metrics: ISE, settling time, control effort
4. Statistical analysis: CIs (t-distribution or bootstrap), hypothesis testing
5. Generate validation report with results and visualizations **Key Components:**
- **Trial Runner**: Orchestrates parallel execution
- **Metrics Computer**: Unified metric calculations
- **Statistics Engine**: CI computation, t-tests, ANOVA
- **Report Generator**: LaTeX/Markdown output ## Mathematical Foundation ### Statistical Performance Evaluation Statistical benchmarking provides rigorous quantification of controller performance across multiple trials with uncertainty quantification. #### Confidence Intervals For a performance metric $m$ measured across $n$ trials, the $(1-\alpha)$ confidence interval estimates the true population mean $\mu_m$: **t-Distribution (Parametric)**:
```{math}

CI_{1-\alpha} = \bar{m} \pm t_{\alpha/2, n-1} \frac{s_m}{\sqrt{n}}
``` Where:
- $\bar{m}$: Sample mean
- $s_m$: Sample standard deviation
- $t_{\alpha/2, n-1}$: Critical t-value
- Assumes: Normal distribution of metrics **Bootstrap (Non-Parametric)**:
```{math}

CI_{1-\alpha} = \left[m_{\alpha/2}^*, m_{1-\alpha/2}^*\right]
``` Computed via $B$ bootstrap resamples:
1. Draw $n$ samples with replacement from original data
2. Compute metric for each resample
3. Use empirical quantiles for interval bounds **No assumptions** about underlying distribution. #### Hypothesis Testing **Welch's t-test** for comparing two controller means: ```{math}
t = \frac{\bar{m}_1 - \bar{m}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}
``` - **Null Hypothesis**: $H_0: \mu_1 = \mu_2$

- **Alternative**: $H_1: \mu_1 \neq \mu_2$
- **Degrees of Freedom**: Welch-Satterthwaite approximation (unequal variances) **Interpretation**: Reject $H_0$ if $p < 0.05$ → significant performance difference. ### Performance Metrics **Integral Squared Error (ISE)**:
```{math}
ISE = \int_0^T ||\vec{x}(t)||^2 dt \approx \sum_{k=0}^{N} ||\vec{x}_k||^2 \Delta t
``` **Settling Time** ($t_s$): Time until $||\vec{x}(t)|| < 0.02$ permanently. **Control Effort**:

```{math}
RMS_u = \sqrt{\frac{1}{T} \int_0^T u^2(t) dt}
``` **Chattering Index**:

```{math}
CI = \frac{1}{N-1} \sum_{k=1}^{N} |u_k - u_{k-1}|
``` **See:** {doc}`../../../mathematical_foundations/statistical_analysis` ## Complete Source Code ```{literalinclude} ../../../src/benchmarks/statistical_benchmarks_v2.py

:language: python
:linenos:
```

---

## Functions

### `compute_metrics(t, x, u, sigma, max_force)`

Compute performance metrics for a batch of trajectories. This function maintains exact compatibility with the original
implementation while delegating to the new modular structure. Parameters
----------
t : np.ndarray One‑dimensional array of time stamps of length ``N+1``.
x : np.ndarray Array of shape ``(B, N+1, S)`` containing the state trajectories for ``B`` particles over ``S`` state dimensions.
u : np.ndarray Array of shape ``(B, N)`` containing the control inputs.
sigma : np.ndarray Array of shape ``(B, N)`` containing sliding variables or auxiliary outputs. (Not used in basic metrics but preserved for compatibility)
max_force : float Maximum allowable magnitude of the control input. Used to count constraint violations. Returns
-------
dict Mapping of metric names to scalar values. Each metric is averaged across the batch dimension. #### Source Code ```{literalinclude} ../../../src/benchmarks/statistical_benchmarks_v2.py
:language: python
:pyobject: compute_metrics
:linenos:
```

---

## `run_trials(controller_factory, cfg, n_trials, seed, randomise_physics, noise_std)`

Run multiple simulations and return per‑trial metrics with confidence intervals. This function maintains exact compatibility with the original implementation

while using the new modular architecture under the hood. The function executes ``n_trials`` independent simulations of the
double inverted pendulum under the supplied controller factory and
configuration. For each trial it collects performance metrics and
computes a 95 % confidence interval for the mean of each metric. A
sample size of at least 25–30 trials is recommended to invoke the
Central Limit Theorem for skewed distributions. Parameters
----------
controller_factory : Callable[[np.ndarray], Any] Factory function that returns a controller instance when provided with a gain vector. The returned controller must define an ``n_gains`` attribute and may define ``max_force``.
cfg : Any Full configuration object (e.g., ``ConfigSchema``) supplying physics and simulation parameters. Only ``simulation.duration`` and ``simulation.dt`` are required by this harness.
n_trials : int, optional Number of independent trials to run. Defaults to 30.
seed : int, optional Base random seed used to initialise each trial. Individual trials draw their seeds from a NumPy generator seeded with this value.
randomise_physics : bool, optional When True, randomly perturb the physical parameters between trials. Not implemented in this harness; reserved for future use.
noise_std : float, optional Standard deviation of additive Gaussian noise applied to the state trajectories before metric computation. Returns
-------
list of dict, dict A list containing the raw metrics for each trial and a dictionary mapping metric names to tuples ``(mean, ci)`` where ``ci`` is half the width of the 95 % confidence interval. #### Source Code ```{literalinclude} ../../../src/benchmarks/statistical_benchmarks_v2.py
:language: python
:pyobject: run_trials
:linenos:
```

---

### `run_trials_with_advanced_statistics(controller_factory, cfg, n_trials, seed, confidence_level, use_bootstrap)`

Run trials with advanced statistical analysis. This function extends the original capability with additional
statistical analysis options. Parameters
----------
controller_factory, cfg, n_trials, seed : Same as run_trials()
confidence_level : float, optional Confidence level for intervals (default 0.95)
use_bootstrap : bool, optional Whether to use bootstrap confidence intervals
**kwargs : Additional arguments passed to trial runner Returns
list of dict, dict Metrics list and statistical analysis results #### Source Code ```{literalinclude} ../../../src/benchmarks/statistical_benchmarks_v2.py
:language: python
:pyobject: run_trials_with_advanced_statistics
:linenos:
```

---

### `compare_controllers(controller_factory_a, controller_factory_b, cfg, n_trials, seed)`

Compare two controllers using statistical analysis. Parameters

controller_factory_a, controller_factory_b : Callable Controller factories to compare
cfg : Any Configuration object
n_trials : int, optional Number of trials per controller
seed : int, optional Base random seed
**kwargs : Additional arguments Returns
-------
dict comparison results #### Source Code ```{literalinclude} ../../../src/benchmarks/statistical_benchmarks_v2.py
:language: python
:pyobject: compare_controllers
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `from typing import Callable, Dict, Any, List, Tuple, Optional`
- `import numpy as np`
- `from .metrics import compute_basic_metrics`
- `from .core import run_multiple_trials, validate_trial_configuration`
- `from .statistics import compute_basic_confidence_intervals` ## Usage Examples ### Basic Statistical Benchmarking ```python
from src.benchmarks.statistical_benchmarks_v2 import run_trials
from src.controllers.factory import create_smc_for_pso, SMCType # Define controller factory
def controller_factory(): return create_smc_for_pso( SMCType.CLASSICAL, gains=[10, 8, 15, 12, 50, 5], max_force=100.0 ) # Configure benchmarking
from src.config import load_config
config = load_config("config.yaml") # Run trials with statistical analysis
metrics_list, ci_results = run_trials( controller_factory, config, n_trials=30, confidence_level=0.95
) # Access results
print(f"Mean ISE: {ci_results['ise']['mean']:.4f}")
print(f"95% CI: [{ci_results['ise']['ci_lower']:.4f}, {ci_results['ise']['ci_upper']:.4f}]")
print(f"Std Dev: {ci_results['ise']['std']:.4f}")
``` ### Advanced: Bootstrap Confidence Intervals ```python

from src.benchmarks.statistical_benchmarks_v2 import run_trials_with_advanced_statistics # Run with bootstrap CI (non-parametric, no normality assumption)
metrics_list, analysis = run_trials_with_advanced_statistics( controller_factory, config, n_trials=50, confidence_level=0.99, use_bootstrap=True, n_bootstrap=10000
) # Bootstrap results more robust for non-normal distributions
print(f"Bootstrap 99% CI for settling time:")
print(f" [{analysis['settling_time']['bootstrap_ci'][0]:.3f}, " f"{analysis['settling_time']['bootstrap_ci'][1]:.3f}]")
``` ### Controller Comparison with Hypothesis Testing ```python
from src.benchmarks.statistical_benchmarks_v2 import compare_controllers # Define two controllers
def classical_factory(): return create_smc_for_pso(SMCType.CLASSICAL, [10, 8, 15, 12, 50, 5]) def adaptive_factory(): return create_smc_for_pso(SMCType.ADAPTIVE, [10, 8, 15, 12, 0.5]) # Statistical comparison
comparison = compare_controllers( controller_a_factory=classical_factory, controller_b_factory=adaptive_factory, config=config, n_trials=40
) # Interpret results
for metric, result in comparison.items(): print(f"
{metric.upper()}:") print(f" Classical: {result['mean_a']:.4f} ± {result['std_a']:.4f}") print(f" Adaptive: {result['mean_b']:.4f} ± {result['std_b']:.4f}") print(f" p-value: {result['p_value']:.4e}") if result['p_value'] < 0.05: better = 'Classical' if result['mean_a'] < result['mean_b'] else 'Adaptive' print(f" → {better} is significantly better (p < 0.05)") else: print(f" → No significant difference (p ≥ 0.05)")
``` ### Batch Benchmarking Multiple Controllers ```python

from src.benchmarks.core import run_multiple_trials controllers = { 'Classical': lambda: create_smc_for_pso(SMCType.CLASSICAL, [10, 8, 15, 12, 50, 5]), 'Adaptive': lambda: create_smc_for_pso(SMCType.ADAPTIVE, [10, 8, 15, 12, 0.5]), 'STA': lambda: create_smc_for_pso(SMCType.SUPER_TWISTING, [25, 10, 15, 12, 20, 15]), 'Hybrid': lambda: create_smc_for_pso(SMCType.HYBRID, [15, 12, 18, 15])
} results = {}
for name, factory in controllers.items(): metrics_list, ci_results = run_trials(factory, config, n_trials=30) results[name] = ci_results # Compare ISE across all controllers
import pandas as pd
comparison_df = pd.DataFrame({ name: { 'ISE': r['ise']['mean'], 'ISE_CI': f"[{r['ise']['ci_lower']:.3f}, {r['ise']['ci_upper']:.3f}]", 'Settling Time': r['settling_time']['mean'] } for name, r in results.items()
}).T print(comparison_df)
``` **See:** {doc}`../../../benchmarking_workflows/statistical_analysis_guide` 
