# analysis.validation.statistical_tests

**Source:** `src\analysis\validation\statistical_tests.py`

## Module Overview Statistical

testing framework for analysis validation

.

## Advanced Mathematical Theory

### Hypothesis Testing Framework


**Alternative:** $H_1: \theta \neq \theta_0$ (two-sided) **Type I error:** $\alpha = P(\text{Reject } H_0 | H_0 \text{ true})$
**Type II error:** $\beta = P(\text{Fail to reject } H_0 | H_1 \text{ true})$ **Power:** $1 - \beta = P(\text{Reject } H_0 | H_1 \text{ true})$ ### t-test **One-sample t-test:** ```{math}
t = \frac{\bar{x} - \mu_0}{s/\sqrt{n}} \sim t_{n-1}
``` **Two-sample t-test (pooled variance):** ```{math}
t = \frac{\bar{x}_1 - \bar{x}_2}{s_p\sqrt{\frac{1}{n_1} + \frac{1}{n_2}}}, \quad s_p^2 = \frac{(n_1-1)s_1^2 + (n_2-1)s_2^2}{n_1 + n_2 - 2}
``` ### Paired t-test **For paired samples:** ```{math}

t = \frac{\bar{d}}{s_d/\sqrt{n}} \sim t_{n-1}
``` Where $d_i = x_i - y_i$, $\bar{d} = \frac{1}{n}\sum d_i$, $s_d^2 = \frac{1}{n-1}\sum(d_i - \bar{d})^2$. ### ANOVA **Total sum of squares:** ```{math}
\text{SST} = \sum_i\sum_j (x_{ij} - \bar{x})^2
``` **Between-group sum of squares:** ```{math}

\text{SSB} = \sum_i n_i(\bar{x}_i - \bar{x})^2
``` **Within-group sum of squares:** ```{math}
\text{SSW} = \sum_i\sum_j (x_{ij} - \bar{x}_i)^2
``` **F-statistic:** ```{math}

F = \frac{\text{MSB}}{\text{MSW}} = \frac{\text{SSB}/(k-1)}{\text{SSW}/(N-k)} \sim F_{k-1, N-k}
``` ### Bonferroni Correction **For $m$ comparisons:** ```{math}
\alpha_{\text{corrected}} = \frac{\alpha}{m}
``` **Family-wise error rate (FWER):** ```{math}

\text{FWER} \leq 1 - (1-\alpha)^m \approx m\alpha
``` ### Chi-Square Test **Goodness-of-fit:** ```{math}
\chi^2 = \sum_{i=1}^k \frac{(O_i - E_i)^2}{E_i} \sim \chi^2_{k-1}
``` Where $O_i$ are observed, $E_i$ are expected frequencies. ### Kolmogorov-Smirnov Test **Test statistic:** ```{math}

D_n = \sup_x |F_n(x) - F_0(x)|
``` Where $F_n$ is empirical CDF, $F_0$ is theoretical CDF. ## Architecture Diagram ```{mermaid}
graph TD A[Data Samples] --> B{Test Type} B -->|One Sample| C[t-test] B -->|Two Samples| D[Two-Sample t-test] B -->|Multiple Groups| E[ANOVA] B -->|Paired| F[Paired t-test] C --> G[Compute t-statistic] D --> H[Welch's t-test] F --> I[Difference t-test] E --> J[F-statistic] G --> K{|t| > t_crit?} H --> K I --> K J --> L{F > F_crit?} K -->|Yes| M[Reject H₀] K -->|No| N[Fail to Reject] L -->|Yes| M L -->|No| N M --> O[Significant] N --> P[Not Significant] E --> Q{Post-hoc?} Q -->|Yes| R[Bonferroni] R --> S[Pairwise Tests] style B fill:#ff9 style K fill:#9cf style L fill:#9cf style M fill:#9f9 style N fill:#f99
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
This module provides statistical testing features for
validating analysis results, comparing methods, and ensuring statistical
rigor in control engineering applications. ## Complete Source Code ```{literalinclude} ../../../src/analysis/validation/statistical_tests.py
:language: python
:linenos:
```

---

## Classes

### `TestType`

**Inherits from:** `Enum` Types of statistical tests.

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistical_tests.py

:language: python
:pyobject: TestType
:linenos:
```

### `AlternativeHypothesis`

**Inherits from:** `Enum` Alternative hypothesis types.

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistical_tests.py
:language: python
:pyobject: AlternativeHypothesis
:linenos:
```

### `StatisticalTestConfig`

Configuration for statistical tests.

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistical_tests.py

:language: python
:pyobject: StatisticalTestConfig
:linenos:
```

### `StatisticalTestSuite`

**Inherits from:** `StatisticalValidator` statistical testing suite.

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistical_tests.py
:language: python
:pyobject: StatisticalTestSuite
:linenos:
``` #### Methods (27) ##### `__init__(self, config)` Initialize statistical test suite. [View full source →](#method-statisticaltestsuite-__init__) ##### `validation_methods(self)` List of validation methods supported. [View full source →](#method-statisticaltestsuite-validation_methods) ##### `validate(self, data)` Perform statistical validation. [View full source →](#method-statisticaltestsuite-validate) ##### `_preprocess_data(self, data)` Preprocess data for statistical testing. [View full source →](#method-statisticaltestsuite-_preprocess_data) ##### `_perform_normality_tests(self, data)` Perform normality tests. [View full source →](#method-statisticaltestsuite-_perform_normality_tests) ##### `_perform_stationarity_tests(self, data)` Perform stationarity tests. [View full source →](#method-statisticaltestsuite-_perform_stationarity_tests) ##### `_perform_independence_tests(self, data)` Perform independence tests. [View full source →](#method-statisticaltestsuite-_perform_independence_tests) ##### `_perform_homoscedasticity_tests(self, data)` Perform homoscedasticity tests. [View full source →](#method-statisticaltestsuite-_perform_homoscedasticity_tests) ##### `_perform_hypothesis_tests(self, data, compare_groups)` Perform hypothesis tests. [View full source →](#method-statisticaltestsuite-_perform_hypothesis_tests) ##### `_perform_goodness_of_fit_tests(self, data, reference_distribution)` Perform goodness of fit tests. [View full source →](#method-statisticaltestsuite-_perform_goodness_of_fit_tests) ##### `_perform_power_analysis(self, data)` Perform power analysis. [View full source →](#method-statisticaltestsuite-_perform_power_analysis) ##### `_perform_effect_size_analysis(self, data, compare_groups)` Perform effect size analysis. [View full source →](#method-statisticaltestsuite-_perform_effect_size_analysis) ##### `_adf_test(self, data)` Simplified Augmented Dickey-Fuller test. [View full source →](#method-statisticaltestsuite-_adf_test) ##### `_kpss_test(self, data)` Simplified KPSS test. [View full source →](#method-statisticaltestsuite-_kpss_test) ##### `_variance_ratio_test(self, data)` Variance ratio test for random walk. [View full source →](#method-statisticaltestsuite-_variance_ratio_test) ##### `_ljung_box_test(self, data)` Ljung-Box test for autocorrelation. [View full source →](#method-statisticaltestsuite-_ljung_box_test) ##### `_durbin_watson_test(self, data)` Durbin-Watson test for autocorrelation. [View full source →](#method-statisticaltestsuite-_durbin_watson_test) ##### `_runs_test(self, data)` Runs test for randomness. [View full source →](#method-statisticaltestsuite-_runs_test) ##### `_one_sample_tests(self, data)` One-sample statistical tests. [View full source →](#method-statisticaltestsuite-_one_sample_tests) ##### `_two_sample_tests(self, data1, data2)` Two-sample statistical tests. [View full source →](#method-statisticaltestsuite-_two_sample_tests) ##### `_chi_square_goodness_of_fit(self, data, distribution)` Chi-square goodness of fit test. [View full source →](#method-statisticaltestsuite-_chi_square_goodness_of_fit) ##### `_ks_goodness_of_fit(self, data, distribution)` Kolmogorov-Smirnov goodness of fit test. [View full source →](#method-statisticaltestsuite-_ks_goodness_of_fit) ##### `_calculate_cohens_d(self, group1, group2)` Calculate Cohen's d effect size. [View full source →](#method-statisticaltestsuite-_calculate_cohens_d) ##### `_interpret_effect_size(self, effect_size)` Interpret effect size magnitude. [View full source →](#method-statisticaltestsuite-_interpret_effect_size) ##### `_interpret_durbin_watson(self, dw_stat)` Interpret Durbin-Watson statistic. [View full source →](#method-statisticaltestsuite-_interpret_durbin_watson) ##### `_calculate_required_sample_size(self, effect_size, power, alpha)` Calculate required sample size for given power. [View full source →](#method-statisticaltestsuite-_calculate_required_sample_size) ##### `_generate_validation_summary(self, results)` Generate overall validation summary. [View full source →](#method-statisticaltestsuite-_generate_validation_summary)

---

## Functions

### `create_statistical_test_suite(config)`

Factory function to create statistical test suite. Parameters

config : Dict[str, Any], optional Configuration parameters Returns
-------
StatisticalTestSuite Configured statistical test suite #### Source Code ```{literalinclude} ../../../src/analysis/validation/statistical_tests.py
:language: python
:pyobject: create_statistical_test_suite
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `from typing import Dict, List, Optional, Tuple, Any, Union`
- `import numpy as np`
- `from scipy import stats`
- `import warnings`
- `from dataclasses import dataclass, field`
- `from enum import Enum`
- `from ..core.interfaces import StatisticalValidator, AnalysisResult, AnalysisStatus`
- `from ..core.data_structures import StatisticalTestResult, ConfidenceInterval`
