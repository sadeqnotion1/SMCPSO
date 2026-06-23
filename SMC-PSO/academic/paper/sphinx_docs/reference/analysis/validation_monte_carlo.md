# analysis.validation.monte_carlo

**Source:** `src\analysis\validation\monte_carlo.py`

## Module Overview Monte

Carlo analysis tools for validation and uncertainty quantification

.

## Advanced Mathematical Theory

### Monte Carlo Methods


\hat{\theta}_N = \frac{1}{N}\sum_{i=1}^N g(X_i), \quad X_i \sim p(x)
``` **Expectation:** ```{math}
E[g(X)] = \int g(x)p(x)dx \approx \hat{\theta}_N
``` ### Convergence Analysis **Law of Large Numbers:** ```{math}

\hat{\theta}_N \xrightarrow{a.s.} E[g(X)] \quad \text{as } N \to \infty
``` **Central Limit Theorem:** ```{math}
\sqrt{N}(\hat{\theta}_N - \theta) \xrightarrow{d} \mathcal{N}(0, \sigma^2)
``` Where $\sigma^2 = \text{Var}(g(X))$. ### Convergence Rate **Standard error:** ```{math}

\text{SE}(\hat{\theta}_N) = \frac{\sigma}{\sqrt{N}}
``` **Convergence rate:** $O(N^{-1/2})$, independent of dimension. ### Variance Reduction **Importance sampling:** ```{math}
E[g(X)] = \int g(x)\frac{p(x)}{q(x)}q(x)dx \approx \frac{1}{N}\sum_{i=1}^N g(X_i)\frac{p(X_i)}{q(X_i)}
``` Where $X_i \sim q(x)$ (importance distribution). **Optimal importance distribution:** ```{math}

q^*(x) = \frac{|g(x)|p(x)}{\int|g(y)|p(y)dy}
``` ### Antithetic Variates **Negative correlation sampling:** ```{math}
\hat{\theta}_{AV} = \frac{1}{2}\left[g(X) + g(F^{-1}(1-F(X)))\right]
``` **Variance reduction:** ```{math}

\text{Var}(\hat{\theta}_{AV}) \leq \frac{1}{2}\text{Var}(g(X))
``` ### Control Variates **Control variate estimator:** ```{math}
\hat{\theta}_{CV} = g(X) - c[h(X) - E[h(X)]]
``` Where $h(X)$ has known expectation. **Optimal coefficient:** ```{math}

c^* = \frac{\text{Cov}(g(X), h(X))}{\text{Var}(h(X))}
``` ### Markov Chain Monte Carlo (MCMC) **Metropolis-Hastings acceptance:** ```{math}
\alpha(x' | x) = \min\left(1, \frac{p(x')q(x|x')}{p(x)q(x'|x)}\right)
``` ## Architecture Diagram ```{mermaid}

graph TD A[Random Sampling] --> B{Sampling Method} B -->|Simple| C[Direct MC] B -->|Importance| D[Importance Sampling] B -->|Antithetic| E[Antithetic Variates] B -->|Control| F[Control Variates] C --> G[N Samples] D --> G E --> G F --> G G --> H[Estimator: 1/N Σg(Xi)] H --> I[Convergence Check] I --> J{SE < ε?} J -->|No| K[Increase N] J -->|Yes| L[Final Estimate] K --> A I --> M[Variance Analysis] M --> N{High Variance?} N -->|Yes| O[Apply Variance Reduction] N -->|No| L O --> D style B fill:#ff9 style J fill:#9cf style L fill:#9f9
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

This module provides Monte Carlo simulation features for
analyzing system behavior under uncertainty, validating controller performance,
and quantifying confidence in analysis results. ## Architecture Diagram ```{mermaid}
graph TD A[Nominal Parameters] --> B[Uncertainty Model] B --> C{For Each Sample i=1..N} C --> D[Perturb Parameters] D --> E[Create Scenario] E --> F[Run Simulation] F --> G[Evaluate Stability] G --> H{Stable?} H -->|Yes| I[Compute Performance] H -->|No| J[Record Failure] I --> K[Metrics Collection] J --> K K --> L{All Samples Done?} L -->|No| C L -->|Yes| M[Robustness Analysis] M --> N[Success Rate] M --> O[Worst-Case Metrics] M --> P[Percentile Analysis] N --> Q[Monte Carlo Report] O --> Q P --> Q style D fill:#9cf style G fill:#fcf style M fill:#ff9 style Q fill:#9f9
``` **Data Flow:**
1. Define uncertainty model (e.g., ±20% mass, ±10% length)
2. Sample $N$ parameter sets from uncertainty distribution
3. For each sample: simulate system and evaluate stability
4. Collect metrics for successful trials
5. Robustness analysis: success rate, worst-case, percentiles
6. Generate report with uncertainty quantification **Sampling Methods:**
- **Uniform**: $\theta \sim \mathcal{U}(\theta_0(1-\epsilon), \theta_0(1+\epsilon))$
- **Gaussian**: $\theta \sim \mathcal{N}(\theta_0, \sigma^2)$
- **Latin Hypercube**: Stratified sampling for high dimensions ## Mathematical Foundation ### Monte Carlo Validation Theory Monte Carlo methods assess controller robustness by evaluating performance distributions across random perturbations. #### Uncertainty Propagation Given parameter uncertainty $\vec{\theta} \sim P(\vec{\theta})$, estimate expected performance: ```{math}
\mathbb{E}[J] = \int J(\vec{\theta}) P(\vec{\theta}) d\vec{\theta} \approx \frac{1}{N} \sum_{i=1}^{N} J(\vec{\theta}_i)
``` Where $\vec{\theta}_i \sim P(\vec{\theta})$ are i.i.d. samples. **Convergence Rate**: Error decreases as $O(1/\sqrt{N})$ (independent of dimension). #### Robustness Metrics **Success Rate**:

```{math}
SR = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}_{\text{stable}}(\vec{\theta}_i)
``` Where $\mathbb{1}_{\text{stable}} = 1$ if system remains stable. **Worst-Case Performance**:

```{math}
J_{\text{worst}} = \max_{i \in [1,N]} J(\vec{\theta}_i)
``` Critical for safety-critical systems. **Performance Percentiles**:

```{math}
J_{p} = \text{quantile}(\{J(\vec{\theta}_i)\}_{i=1}^N, p)
``` Example: $J_{95}$ = 95th percentile (worst 5% performance). #### Sampling Strategies **Uniform Perturbations**:

```{math}
\theta_i = \theta_0 (1 + \delta_i), \quad \delta_i \sim \mathcal{U}(-\epsilon, +\epsilon)
``` **Gaussian Perturbations**:

```{math}
\theta_i \sim \mathcal{N}(\theta_0, \sigma^2 \theta_0^2)
``` **Latin Hypercube Sampling**: Ensures stratified coverage of parameter space (more efficient than uniform for high dimensions). ### Confidence Bounds For estimated mean $\bar{J}$: ```{math}

CI_{95\%} = \bar{J} \pm 1.96 \frac{s_J}{\sqrt{N}}
``` **Rule of Thumb**: $N \geq 30$ trials for reliable statistics, $N \geq 100$ for robust estimation. **See:** {doc}`../../../validation/monte_carlo_methodology` ## Complete Source Code ```{literalinclude} ../../../src/analysis/validation/monte_carlo.py
:language: python
:linenos:
```

---

## Classes

### `MonteCarloConfig`

Configuration for Monte Carlo analysis.

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/monte_carlo.py

:language: python
:pyobject: MonteCarloConfig
:linenos:
```

### `MonteCarloAnalyzer`

**Inherits from:** `StatisticalValidator` Monte Carlo analyzer for uncertainty quantification and validation.

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/monte_carlo.py
:language: python
:pyobject: MonteCarloAnalyzer
:linenos:
``` #### Methods (32) ##### `__init__(self, config)` Initialize Monte Carlo analyzer. [View full source →](#method-montecarloanalyzer-__init__) ##### `validation_methods(self)` List of validation methods supported. [View full source →](#method-montecarloanalyzer-validation_methods) ##### `validate(self, data)` Perform Monte Carlo validation analysis. [View full source →](#method-montecarloanalyzer-validate) ##### `_perform_monte_carlo_simulation(self, simulation_function, parameter_distributions)` Perform Monte Carlo simulation. [View full source →](#method-montecarloanalyzer-_perform_monte_carlo_simulation) ##### `_generate_parameter_samples(self, parameter_distributions)` Generate parameter samples according to specified distributions. [View full source →](#method-montecarloanalyzer-_generate_parameter_samples) ##### `_random_sampling(self, parameter_distributions)` Generate random samples. [View full source →](#method-montecarloanalyzer-_random_sampling) ##### `_latin_hypercube_sampling(self, parameter_distributions)` Latin Hypercube Sampling for better space coverage. [View full source →](#method-montecarloanalyzer-_latin_hypercube_sampling) ##### `_sobol_sampling(self, parameter_distributions)` Sobol sequence sampling (simplified implementation). [View full source →](#method-montecarloanalyzer-_sobol_sampling) ##### `_halton_sampling(self, parameter_distributions)` Halton sequence sampling. [View full source →](#method-montecarloanalyzer-_halton_sampling) ##### `_sample_from_distribution(self, distribution_info)` Sample from a distribution specification. [View full source →](#method-montecarloanalyzer-_sample_from_distribution) ##### `_inverse_transform_sample(self, uniform_value, distribution_info)` Transform uniform sample to target distribution using inverse CDF. [View full source →](#method-montecarloanalyzer-_inverse_transform_sample) ##### `_van_der_corput_sequence(self, n, base)` Generate van der Corput sequence value. [View full source →](#method-montecarloanalyzer-_van_der_corput_sequence) ##### `_generate_antithetic_variate(self, value, distribution_info)` Generate antithetic variate for variance reduction. [View full source →](#method-montecarloanalyzer-_generate_antithetic_variate) ##### `_run_simulations(self, simulation_function, parameter_samples)` Run Monte Carlo simulations. [View full source →](#method-montecarloanalyzer-_run_simulations) ##### `_run_simulations_sequential(self, simulation_function, parameter_samples)` Run simulations sequentially. [View full source →](#method-montecarloanalyzer-_run_simulations_sequential) ##### `_run_simulations_parallel(self, simulation_function, parameter_samples)` Run simulations in parallel. [View full source →](#method-montecarloanalyzer-_run_simulations_parallel) ##### `_safe_simulation_wrapper(self, simulation_function, params)` Wrapper for safe simulation execution. [View full source →](#method-montecarloanalyzer-_safe_simulation_wrapper) ##### `_analyze_simulation_results(self, results)` Analyze Monte Carlo simulation results. [View full source →](#method-montecarloanalyzer-_analyze_simulation_results) ##### `_compute_statistical_summary(self, values)` Compute statistical summary. [View full source →](#method-montecarloanalyzer-_compute_statistical_summary) ##### `_analyze_convergence(self, results)` Analyze Monte Carlo convergence. [View full source →](#method-montecarloanalyzer-_analyze_convergence) ##### `_analyze_data_with_monte_carlo(self, data)` Analyze existing data using Monte Carlo methods. [View full source →](#method-montecarloanalyzer-_analyze_data_with_monte_carlo) ##### `_perform_bootstrap_analysis(self, data)` Perform bootstrap analysis. [View full source →](#method-montecarloanalyzer-_perform_bootstrap_analysis) ##### `_bootstrap_analysis(self, values)` Perform bootstrap resampling analysis. [View full source →](#method-montecarloanalyzer-_bootstrap_analysis) ##### `_subsampling_analysis(self, values)` Perform subsampling analysis. [View full source →](#method-montecarloanalyzer-_subsampling_analysis) ##### `_perform_sensitivity_analysis(self, simulation_function, parameter_distributions)` Perform sensitivity analysis. [View full source →](#method-montecarloanalyzer-_perform_sensitivity_analysis) ##### `_simple_sensitivity_analysis(self, simulation_function, parameter_distributions)` Simple one-at-a-time sensitivity analysis. [View full source →](#method-montecarloanalyzer-_simple_sensitivity_analysis) ##### `_sobol_sensitivity_analysis(self, simulation_function, parameter_distributions)` Simplified Sobol sensitivity analysis. [View full source →](#method-montecarloanalyzer-_sobol_sensitivity_analysis) ##### `_morris_sensitivity_analysis(self, simulation_function, parameter_distributions)` Simplified Morris sensitivity analysis. [View full source →](#method-montecarloanalyzer-_morris_sensitivity_analysis) ##### `_analyze_distributions(self, data)` Analyze and fit distributions to data. [View full source →](#method-montecarloanalyzer-_analyze_distributions) ##### `_perform_risk_analysis(self, data)` Perform risk analysis including tail risk assessment. [View full source →](#method-montecarloanalyzer-_perform_risk_analysis) ##### `_extreme_value_analysis(self, values)` Perform extreme value analysis. [View full source →](#method-montecarloanalyzer-_extreme_value_analysis) ##### `_generate_validation_summary(self, results)` Generate validation summary. [View full source →](#method-montecarloanalyzer-_generate_validation_summary)

---

## Functions

### `create_monte_carlo_analyzer(config)`

Factory function to create Monte Carlo analyzer. Parameters

config : Dict[str, Any], optional Configuration parameters Returns
-------
MonteCarloAnalyzer Configured Monte Carlo analyzer #### Source Code ```{literalinclude} ../../../src/analysis/validation/monte_carlo.py
:language: python
:pyobject: create_monte_carlo_analyzer
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `from typing import Dict, List, Optional, Tuple, Any, Union, Callable`
- `import numpy as np`
- `from scipy import stats`
- `import warnings`
- `from dataclasses import dataclass, field`
- `from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor`
- `import multiprocessing`
- `from functools import partial`
- `from ..core.interfaces import StatisticalValidator, AnalysisResult, AnalysisStatus, DataProtocol` *... and 1 more* ## Usage Examples ### Basic Monte Carlo Robustness Analysis ```python
from src.analysis.validation.monte_carlo import MonteCarloValidator
from src.controllers.factory import create_smc_for_pso, SMCType # Define controller
controller_factory = lambda: create_smc_for_pso( SMCType.CLASSICAL, gains=[10, 8, 15, 12, 50, 5], max_force=100.0
) # Configure uncertainty model (±20% on masses, ±10% on lengths)
uncertainty = { 'cart_mass': {'type': 'uniform', 'range': (-0.2, 0.2)}, 'pole1_mass': {'type': 'uniform', 'range': (-0.2, 0.2)}, 'pole2_mass': {'type': 'uniform', 'range': (-0.2, 0.2)}, 'pole1_length': {'type': 'uniform', 'range': (-0.1, 0.1)}, 'pole2_length': {'type': 'uniform', 'range': (-0.1, 0.1)},
} # Run Monte Carlo validation
validator = MonteCarloValidator( controller_factory=controller_factory, uncertainty_model=uncertainty, n_samples=100, seed=42
) results = validator.run() # Analyze robustness
print(f"Success Rate: {results['success_rate']*100:.1f}%")
print(f"Mean ISE: {results['mean_ise']:.4f}")
print(f"Worst-case ISE: {results['worst_case_ise']:.4f}")
print(f"95th Percentile ISE: {results['percentile_95_ise']:.4f}")
``` ### Gaussian Uncertainty with Correlation ```python

import numpy as np # Define correlated uncertainties (masses tend to vary together)
mean_params = np.array([1.0, 0.1, 0.05]) # cart, pole1, pole2 masses
cov_matrix = np.array([ [0.04, 0.01, 0.005], # cart mass variance and covariances [0.01, 0.004, 0.002], # pole1 mass [0.005, 0.002, 0.001] # pole2 mass
]) # Gaussian Monte Carlo
validator = MonteCarloValidator( controller_factory=controller_factory, uncertainty_model={ 'masses': { 'type': 'gaussian', 'mean': mean_params, 'cov': cov_matrix } }, n_samples=200
) results = validator.run() # Visualize uncertainty propagation
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
plt.hist(results['ise_samples'], bins=30, alpha=0.7, edgecolor='black')
plt.xlabel('ISE')
plt.ylabel('Frequency')
plt.title('Performance Distribution under Uncertainty') plt.subplot(1, 2, 2)
plt.scatter(results['param_samples'][:, 0], results['ise_samples'], alpha=0.5)
plt.xlabel('Cart Mass Perturbation')
plt.ylabel('ISE')
plt.title('Sensitivity to Cart Mass')
plt.tight_layout()
plt.show()
``` ### Latin Hypercube Sampling for High-Dimensional Uncertainty ```python
from src.analysis.validation.monte_carlo import LatinHypercubeSampler # High-dimensional uncertainty (all 8 physics parameters)
uncertainty_full = { 'cart_mass': (-0.2, 0.2), 'pole1_mass': (-0.2, 0.2), 'pole2_mass': (-0.2, 0.2), 'pole1_length': (-0.1, 0.1), 'pole2_length': (-0.1, 0.1), 'friction_cart': (-0.3, 0.3), 'friction_pole1': (-0.3, 0.3), 'friction_pole2': (-0.3, 0.3),
} # Latin Hypercube Sampling (more efficient than random for high dimensions)
sampler = LatinHypercubeSampler(uncertainty_full, n_samples=150, seed=42)
param_samples = sampler.generate() # Run validation with LHS samples
validator = MonteCarloValidator( controller_factory=controller_factory, param_samples=param_samples # Pre-generated samples
) results = validator.run() # Analyze which parameters drive failures
failure_params = param_samples[~results['stability_mask']]
print(f"Failure modes analysis:")
print(f" Cart mass range in failures: [{failure_params[:, 0].min():.3f}, {failure_params[:, 0].max():.3f}]")
print(f" Pole1 length range in failures: [{failure_params[:, 3].min():.3f}, {failure_params[:, 3].max():.3f}]")
``` ### Robustness Comparison Across Controllers ```python
# example-metadata:

# runnable: false controllers

= { 'Classical': lambda: create_smc_for_pso(SMCType.CLASSICAL, [10, 8, 15, 12, 50, 5]), 'Adaptive': lambda: create_smc_for_pso(SMCType.ADAPTIVE, [10, 8, 15, 12, 0.5]),

} uncertainty = { 'cart_mass': {'type': 'uniform', 'range': (-0.3, 0.3)}, # Aggressive uncertainty 'pole1_mass': {'type': 'uniform', 'range': (-0.3, 0.3)},
} robustness_results = {}
for name, factory in controllers.items(): validator = MonteCarloValidator(factory, uncertainty, n_samples=200) robustness_results[name] = validator.run() # Compare success rates
for name, res in robustness_results.items(): print(f"{name}:") print(f" Success Rate: {res['success_rate']*100:.1f}%") print(f" Mean ISE (successful): {res['mean_ise']:.4f}") print(f" Worst-case ISE: {res['worst_case_ise']:.4f}")
``` **See:** {doc}`../../../validation/monte_carlo_robustness_guide` 
