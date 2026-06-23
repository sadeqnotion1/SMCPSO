# analysis.validation.statistics

**Source:** `src\analysis\validation\statistics.py`

## Module Overview Statistical

analysis utilities for validation and benchmarking

. This module provides statistical functions for analyzing experimental results,


computing confidence intervals, and performing hypothesis testing. ## Complete Source Code ```{literalinclude} ../../../src/analysis/validation/statistics.py
:language: python
:linenos:
```

---

## Functions

### `compute_basic_confidence_intervals(data, confidence_level)`

Compute basic confidence intervals for data. Args: data: Input data array confidence_level: Confidence level (default 0.95) Returns: Dictionary containing confidence interval statistics

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistics.py
:language: python
:pyobject: compute_basic_confidence_intervals
:linenos:
```

---

## `bootstrap_confidence_interval(data, statistic_func, confidence_level, n_bootstrap, random_seed)`

Compute bootstrap confidence intervals. Args: data: Input data array statistic_func: Function to compute statistic (default: mean) confidence_level: Confidence level n_bootstrap: Number of bootstrap samples random_seed: Optional random seed Returns: Dictionary containing bootstrap confidence interval

### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistics.py

:language: python
:pyobject: bootstrap_confidence_interval
:linenos:
```

### `compare_groups_ttest(group1, group2, equal_var)`

Compare two groups using t-test. Args: group1: First group data group2: Second group data equal_var: Assume equal variances Returns: Dictionary containing t-test results

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistics.py
:language: python
:pyobject: compare_groups_ttest
:linenos:
```

### `anova_one_way()`

Perform one-way ANOVA on multiple groups. Args: *groups: Variable number of group arrays Returns: Dictionary containing ANOVA results

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistics.py

:language: python
:pyobject: anova_one_way
:linenos:
```

### `correlation_analysis(x, y, method)`

Compute correlation between two variables. Args: x: First variable y: Second variable method: Correlation method ('pearson', 'spearman', 'kendall') Returns: Dictionary containing correlation results

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistics.py
:language: python
:pyobject: correlation_analysis
:linenos:
```

### `normality_test(data)`

Test for normality using multiple methods. Args: data: Data to test Returns: Dictionary containing normality test results

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistics.py

:language: python
:pyobject: normality_test
:linenos:
```

### `outlier_detection(data, method, threshold)`

Detect outliers in data. Args: data: Input data method: Detection method ('iqr', 'zscore') threshold: Threshold for outlier detection Returns: Dictionary containing outlier information

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistics.py
:language: python
:pyobject: outlier_detection
:linenos:
```

### `statistical_summary(data)`

Compute statistical summary. Args: data: Input data Returns: Dictionary containing statistics

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/statistics.py

:language: python
:pyobject: statistical_summary
:linenos:
```

---

## Dependencies This module imports: - `from typing import Dict, List, Tuple, Any, Optional, Union`
- `import numpy as np`
- `from scipy import stats`
- `import warnings`
