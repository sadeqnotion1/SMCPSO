# utils.analysis.statistics

**Source:** `src\utils\analysis\statistics.py`

## Module Overview Statistical

analysis utilities for control system performance evaluation

. Provides statistical tools for analyzing control system


performance, including confidence intervals, hypothesis testing, and
Monte Carlo analysis validation. ## Complete Source Code ```{literalinclude} ../../../src/utils/analysis/statistics.py
:language: python
:linenos:
```

---

## Functions

### `confidence_interval(data, confidence)`

Return the mean and half‑width of a Student‑t confidence interval. Given an array of samples, compute the sample mean and the half‑width
of the two‑sided confidence interval at the specified confidence
level. The half‑width is ``tcrit * s / sqrt(n)``, where ``tcrit`` is
the t‑distribution critical value, ``s`` is the sample standard
deviation (ddof=1) and ``n`` is the number of samples. Parameters
----------
data : np.ndarray One‑dimensional array of observations.
confidence : float, optional Desired confidence level in (0,1). Defaults to 0.95. Returns
-------
mean : float Sample mean.
half_width : float Half‑width of the confidence interval. ``NaN`` when ``n < 2``. #### Source Code ```{literalinclude} ../../../src/utils/analysis/statistics.py
:language: python
:pyobject: confidence_interval
:linenos:
```

---

## `bootstrap_confidence_interval(data, statistic_func, confidence, n_bootstrap)`

Compute bootstrap confidence interval for any statistic. Parameters

data : np.ndarray Original sample data.
statistic_func : callable Function to compute the statistic of interest.
confidence : float Confidence level (default: 0.95).
n_bootstrap : int Number of bootstrap samples. Returns
-------
statistic : float Original statistic value.
ci : tuple (lower_bound, upper_bound) of confidence interval. #### Source Code ```{literalinclude} ../../../src/utils/analysis/statistics.py
:language: python
:pyobject: bootstrap_confidence_interval
:linenos:
```

---

### `welch_t_test(group1, group2, alpha)`

Perform Welch's t-test for unequal variances. Parameters
----------
group1, group2 : np.ndarray Two independent samples to compare.
alpha : float Significance level (default: 0.05). Returns
results : dict Dictionary containing test statistic, p-value, degrees of freedom, and decision about null hypothesis. #### Source Code ```{literalinclude} ../../../src/utils/analysis/statistics.py
:language: python
:pyobject: welch_t_test
:linenos:
```

---

### `one_way_anova(groups, alpha)`

Perform one-way ANOVA. Parameters

groups : list of np.ndarray List of independent groups to compare.
alpha : float Significance level. Returns
results : dict ANOVA results including F-statistic, p-value, and effect size. #### Source Code ```{literalinclude} ../../../src/utils/analysis/statistics.py
:language: python
:pyobject: one_way_anova
:linenos:
```

---

### `monte_carlo_analysis(simulation_func, parameter_distributions, n_trials, confidence_level)`

Perform Monte Carlo analysis of system performance. Parameters
----------
simulation_func : callable Function that takes parameters and returns performance metrics.
parameter_distributions : dict Dictionary mapping parameter names to random sampling functions.
n_trials : int Number of Monte Carlo trials.
confidence_level : float Confidence level for intervals. Returns
results : dict Monte Carlo analysis results including statistics and confidence intervals. #### Source Code ```{literalinclude} ../../../src/utils/analysis/statistics.py
:language: python
:pyobject: monte_carlo_analysis
:linenos:
```

---

### `performance_comparison_summary(controller_results, metric_name, confidence_level)`

Generate comparison summary for multiple controllers. Parameters

controller_results : dict Dictionary mapping controller names to performance arrays.
metric_name : str Name of the performance metric being compared.
confidence_level : float Confidence level for intervals. Returns
summary : dict comparison summary with statistics and tests. #### Source Code ```{literalinclude} ../../../src/utils/analysis/statistics.py
:language: python
:pyobject: performance_comparison_summary
:linenos:
```

---

### `sample_size_calculation(effect_size, power, alpha, test_type)`

Calculate required sample size for statistical tests. Parameters
----------
effect_size : float Expected effect size (Cohen's d for t-test).
power : float Desired statistical power (1 - beta).
alpha : float Significance level (Type I error rate).
test_type : str Type of test ('t_test' or 'anova'). Returns
-------
sample_size : int Required sample size per group. #### Source Code ```{literalinclude} ../../../src/utils/analysis/statistics.py
:language: python
:pyobject: sample_size_calculation
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`

- `import numpy as np`
- `from scipy.stats import t, f, chi2`
- `from typing import Tuple, Dict, List, Optional`
- `import warnings` ## Advanced Mathematical Theory ### Analysis Utilities Theory (Detailed mathematical theory for analysis utilities to be added...) **Key concepts:**
- Mathematical foundations
- Algorithmic principles
- Performance characteristics
- Integration patterns ## Architecture Diagram \`\`\`{mermaid}
graph TD A[Component] --> B[Subcomponent 1] A --> C[Subcomponent 2] B --> D[Output] C --> D style A fill:#e1f5ff style D fill:#e8f5e9
\`\`\` ## Usage Examples ### Example 1: Basic Usage \`\`\`python
from src.utils.analysis_statistics import Component component = Component()
result = component.process(data)
\`\`\` ### Example 2: Advanced Configuration \`\`\`python
component = Component( option1=value1, option2=value2
)
\`\`\` ### Example 3: Integration with Simulation \`\`\`python
# Integration example

for k in range(num_steps): result = component.process(x) x = update(x, result)
\`\`\` ### Example 4: Performance Optimization \`\`\`python
component = Component(enable_caching=True)
\`\`\` ### Example 5: Error Handling \`\`\`python
try: result = component.process(data)
except ComponentError as e: print(f"Error: {e}")
\`\`\` 
