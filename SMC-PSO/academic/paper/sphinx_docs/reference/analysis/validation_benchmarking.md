# analysis.validation.benchmarking

**Source:** `src\analysis\validation\benchmarking.py`

## Module Overview Benchmarking

and comparison tools for analysis validation

. This module provides benchmarking features for comparing


analysis methods, controllers, and algorithms in control engineering applications. ## Complete Source Code ```{literalinclude} ../../../src/analysis/validation/benchmarking.py
:language: python
:linenos:
```

---

## Classes

### `BenchmarkConfig`

Configuration for benchmarking.

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/benchmarking.py
:language: python
:pyobject: BenchmarkConfig
:linenos:
```

---

## `BenchmarkSuite`

**Inherits from:** `StatisticalValidator`

Advanced benchmarking and comparison framework.

### Source Code ```

{literalinclude} ../../../src/analysis/validation/benchmarking.py

:language: python
:pyobject: BenchmarkSuite
:linenos:
``` #### Methods (24) ##### `__init__(self, config)` Initialize benchmark suite. [View full source →](#method-benchmarksuite-__init__) ##### `validation_methods(self)` List of validation methods supported. [View full source →](#method-benchmarksuite-validation_methods) ##### `validate(self, data)` Perform benchmarking analysis. [View full source →](#method-benchmarksuite-validate) ##### `_run_simulation_benchmarks(self, methods, simulation_function, test_cases)` Run simulation benchmarks for all methods and test cases. [View full source →](#method-benchmarksuite-_run_simulation_benchmarks) ##### `_run_method_trials(self, method, simulation_function, test_case)` Run multiple trials for a single method. [View full source →](#method-benchmarksuite-_run_method_trials) ##### `_analyze_trial_metrics(self, trial_results)` Analyze metrics from trial results. [View full source →](#method-benchmarksuite-_analyze_trial_metrics) ##### `_compute_metric_statistics(self, values)` Compute statistics for a metric. [View full source →](#method-benchmarksuite-_compute_metric_statistics) ##### `_analyze_provided_data(self, data)` Analyze provided benchmark data. [View full source →](#method-benchmarksuite-_analyze_provided_data) ##### `_perform_performance_comparison(self, results)` Perform performance comparison between methods. [View full source →](#method-benchmarksuite-_perform_performance_comparison) ##### `_perform_robustness_comparison(self, results)` Perform robustness comparison between methods. [View full source →](#method-benchmarksuite-_perform_robustness_comparison) ##### `_perform_significance_testing(self, results)` Perform statistical significance testing between methods. [View full source →](#method-benchmarksuite-_perform_significance_testing) ##### `_perform_effect_size_analysis(self, results)` Perform effect size analysis between methods. [View full source →](#method-benchmarksuite-_perform_effect_size_analysis) ##### `_perform_ranking_analysis(self, results)` Perform ranking analysis. [View full source →](#method-benchmarksuite-_perform_ranking_analysis) ##### `_extract_method_performance(self, results)` Extract method performance data from results. [View full source →](#method-benchmarksuite-_extract_method_performance) ##### `_extract_raw_performance_data(self, results)` Extract raw performance data for statistical testing. [View full source →](#method-benchmarksuite-_extract_raw_performance_data) ##### `_compare_two_methods(self, perf_a, perf_b, method_a, method_b)` Compare two methods on a single metric. [View full source →](#method-benchmarksuite-_compare_two_methods) ##### `_rank_methods_by_performance(self, method_performance)` Rank methods by performance on primary metric. [View full source →](#method-benchmarksuite-_rank_methods_by_performance) ##### `_perform_statistical_test(self, data_a, data_b, method_a, method_b)` Perform statistical test between two methods. [View full source →](#method-benchmarksuite-_perform_statistical_test) ##### `_apply_multiple_comparison_correction(self, test_results)` Apply multiple comparison correction to p-values. [View full source →](#method-benchmarksuite-_apply_multiple_comparison_correction) ##### `_holm_correction(self, p_values)` Apply Holm-Bonferroni correction. [View full source →](#method-benchmarksuite-_holm_correction) ##### `_benjamini_hochberg_correction(self, p_values)` Apply Benjamini-Hochberg FDR correction. [View full source →](#method-benchmarksuite-_benjamini_hochberg_correction) ##### `_compute_effect_size(self, data_a, data_b)` Compute effect size between two groups. [View full source →](#method-benchmarksuite-_compute_effect_size) ##### `_interpret_effect_size(self, effect_size)` Interpret effect size magnitude. [View full source →](#method-benchmarksuite-_interpret_effect_size) ##### `_generate_benchmark_summary(self, results)` Generate overall benchmark summary. [View full source →](#method-benchmarksuite-_generate_benchmark_summary)

---

## Functions

### `create_benchmark_suite(config)`

Factory function to create benchmark suite. Parameters
----------
config : Dict[str, Any], optional Configuration parameters Returns
-------
BenchmarkSuite Configured benchmark suite #### Source Code ```{literalinclude} ../../../src/analysis/validation/benchmarking.py
:language: python
:pyobject: create_benchmark_suite
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from typing import Dict, List, Optional, Tuple, Any, Union, Callable`
- `import numpy as np`
- `from scipy import stats`
- `import warnings`
- `from dataclasses import dataclass, field`
- `import time`
- `from concurrent.futures import ProcessPoolExecutor`
- `import multiprocessing`
- `from ..core.interfaces import StatisticalValidator, AnalysisResult, AnalysisStatus, DataProtocol` *... and 1 more*
