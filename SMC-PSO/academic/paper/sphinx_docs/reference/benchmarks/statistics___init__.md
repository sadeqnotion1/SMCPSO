# benchmarks.statistics.__init__

**Source:** `src\benchmarks\statistics\__init__.py`

## Module Overview Statistical

analysis package for control system benchmarking

. This package provides statistical tools for analyzing


performance metrics collected from simulation trials: - **Confidence Intervals**: Normal, t-distribution, and bootstrap methods
- **Hypothesis Testing**: Normality tests, group comparisons
- **Effect Size Analysis**: Practical significance assessment
- **Outlier Detection**: Robust statistical validation ## Complete Source Code ```{literalinclude} ../../../src/benchmarks/statistics/__init__.py
:language: python
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `from .confidence_intervals import ConfidenceIntervalResult, compute_basic_confidence_intervals, compute_t_confidence_intervals, compute_bootstrap_confidence_intervals, perform_statistical_tests, compare_metric_distributions`
