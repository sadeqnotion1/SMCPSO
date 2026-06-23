# benchmarks.statistics.confidence_intervals

**Source:** `src\benchmarks\statistics\confidence_intervals.py`

## Module Overview

Statistical analysis and confidence interval computation for benchmarks.

This module implements statistical methods for analyzing performance metrics
collected from multiple simulation trials. The Central Limit Theorem ensures
that sample means approach normal distributions for sufficiently large samples,
enabling reliable confidence interval estimation.

Statistical Methods:
* **T-distribution confidence intervals** for small samples
* **Normal approximation** for large samples
* **Bootstrap confidence intervals** for non-parametric estimation
* **Effect size calculations** for practical significance

## Complete Source Code

```{literalinclude} ../../../src/benchmarks/statistics/confidence_intervals.py
:language: python
:linenos:
```



## Classes

### `ConfidenceIntervalResult`

Container for confidence interval analysis results.

#### Source Code

```{literalinclude} ../../../src/benchmarks/statistics/confidence_intervals.py
:language: python
:pyobject: ConfidenceIntervalResult
:linenos:
```



## Functions

### `compute_basic_confidence_intervals(metrics_list, confidence_level)`

Compute 95% confidence intervals using normal approximation.

This function replicates the original statistical_benchmarks.py behavior
for backward compatibility.

Parameters
----------
metrics_list : list of dict
    List of metric dictionaries from individual trials
confidence_level : float, optional
    Confidence level (default 0.95 for 95% intervals)

Returns
-------
dict
    Mapping from metric names to (mean, margin_of_error) tuples

#### Source Code

```{literalinclude} ../../../src/benchmarks/statistics/confidence_intervals.py
:language: python
:pyobject: compute_basic_confidence_intervals
:linenos:
```



### `compute_t_confidence_intervals(metrics_list, confidence_level)`

Compute confidence intervals using t-distribution.

The t-distribution provides more accurate confidence intervals for
small sample sizes and unknown population variance. For large samples
(n > 30), t-distribution converges to normal distribution.

Parameters
----------
metrics_list : list of dict
    List of metric dictionaries from individual trials
confidence_level : float, optional
    Confidence level between 0 and 1

Returns
-------
dict
    Mapping from metric names to ConfidenceIntervalResult objects

#### Source Code

```{literalinclude} ../../../src/benchmarks/statistics/confidence_intervals.py
:language: python
:pyobject: compute_t_confidence_intervals
:linenos:
```



### `compute_bootstrap_confidence_intervals(metrics_list, confidence_level, n_bootstrap, random_seed)`

Compute bootstrap confidence intervals.

Bootstrap resampling provides non-parametric confidence intervals
that don't assume normality. This is particularly useful for metrics
with skewed distributions or outliers.

Parameters
----------
metrics_list : list of dict
    List of metric dictionaries from individual trials
confidence_level : float, optional
    Confidence level between 0 and 1
n_bootstrap : int, optional
    Number of bootstrap samples
random_seed : int, optional
    Random seed for reproducibility

Returns
-------
dict
    Mapping from metric names to ConfidenceIntervalResult objects

#### Source Code

```{literalinclude} ../../../src/benchmarks/statistics/confidence_intervals.py
:language: python
:pyobject: compute_bootstrap_confidence_intervals
:linenos:
```



### `perform_statistical_tests(metrics_list)`

Perform statistical tests on collected metrics.

Parameters
metrics_list : list of dict
    List of metric dictionaries from individual trials

Returns
-------
dict
    Statistical test results for each metric

#### Source Code

```{literalinclude} ../../../src/benchmarks/statistics/confidence_intervals.py
:language: python
:pyobject: perform_statistical_tests
:linenos:
```



### `compare_metric_distributions(metrics_list_a, metrics_list_b, alpha)`

Compare metric distributions between two groups.

Parameters
----------
metrics_list_a, metrics_list_b : list of dict
    Metric lists from two different conditions
alpha : float, optional
    Significance level for hypothesis tests

Returns
-------
dict
    Comparison results for each metric

#### Source Code

```{literalinclude} ../../../src/benchmarks/statistics/confidence_intervals.py
:language: python
:pyobject: compare_metric_distributions
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import numpy as np`
- `from typing import Dict, List, Tuple, Optional`
- `from scipy import stats`
- `from dataclasses import dataclass`
