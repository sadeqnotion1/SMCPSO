# optimization.core.results_manager

**Source:** `src\optimization\core\results_manager.py`

## Module Overview PSO

Optimization Results Management and Serialization

.

## Advanced Mathematical Theory

### Results Aggregation


\begin{align}
\mu_f &= \frac{1}{M} \sum_{i=1}^{M} f_i^* \\
\sigma_f^2 &= \frac{1}{M-1} \sum_{i=1}^{M} (f_i^* - \mu_f)^2
\end{align}
``` ### Convergence Tracking **Best-so-far curve:** ```{math}
f_{best}^t = \min_{\tau=0,\ldots,t} f(\vec{x}^{\tau})
``` **Average fitness over population:** ```{math}

\bar{f}^t = \frac{1}{N} \sum_{i=1}^{N} f(\vec{x}_i^t)
``` ### Statistical Analysis **Confidence intervals** for mean fitness: ```{math}
\text{CI}_{95\%} = \mu_f \pm 1.96 \frac{\sigma_f}{\sqrt{M}}
``` **Hypothesis testing** for algorithm comparison: ```{math}

H_0: \mu_A = \mu_B \quad \text{vs} \quad H_1: \mu_A \neq \mu_B
``` Use Welch's t-test: ```{math}
t = \frac{\bar{f}_A - \bar{f}_B}{\sqrt{\frac{s_A^2}{n_A} + \frac{s_B^2}{n_B}}}
``` ### Convergence Detection **Plateau detection:** ```{math}

\text{Plateau if } \max_{t-w \leq \tau \leq t} f_{best}^{\tau} - f_{best}^t < \epsilon \text{ for window } w
``` **Stagnation metric:** ```{math}
S^t = \frac{1}{w} \sum_{\tau=t-w}^{t} |f_{best}^{\tau+1} - f_{best}^{\tau}|
``` ### Performance Profiling **Function evaluation budget:** ```{math}

\text{FE}_{total} = N_{pop} \times T_{iter}
``` **Success rate** across runs: ```{math}
P_{success} = \frac{\#\{f_i^* < f_{target}\}}{M}
``` ## Architecture Diagram ```{mermaid}

graph TD A[Optimization Results] --> B[Store Best Solution] B --> C[Store Convergence History] C --> D[Compute Statistics] D --> E[Mean Fitness] D --> F[Std Deviation] D --> G[Confidence Intervals] E --> H[Statistical Analysis] F --> H G --> H H --> I{Multiple Runs?} I -->|Yes| J[Compare Algorithms] I -->|No| K[Single Run Report] J --> L[Hypothesis Testing] K --> L L --> M[Results Summary] style D fill:#9cf style H fill:#ff9 style M fill:#9f9
``` ## Usage Examples ### Example 1: Basic Initialization ```python
from src.optimization.core import * # Initialize with configuration
config = {'parameter': 'value'}
instance = Component(config)
``` ### Example 2: Performance Tuning ```python
# Adjust parameters for better performance

optimized_params = tune_parameters(instance, target_performance)
``` ### Example 3: Integration with Optimization ```python
# Use in complete optimization loop
optimizer = create_optimizer(opt_type, config)
result = optimize(optimizer, problem, max_iter=100)
``` ### Example 4: Edge Case Handling ```python

try: output = instance.compute(parameters)
except ValueError as e: handle_edge_case(e)
``` ### Example 5: Performance Analysis ```python
# Analyze metrics
metrics = compute_metrics(result)
print(f"Best fitness: {metrics.best_fitness:.3f}")
```

This module provides management of PSO optimization results including
serialization, loading, analysis, and comparison features. It ensures reproducible
optimization workflows and provides result analysis. Features:
- result serialization (JSON, HDF5, NPZ)
- Metadata tracking and provenance
- Result comparison and benchmarking
- Statistical analysis of optimization runs
- Convergence analysis and visualization
- Result validation and integrity checking References:
- IEEE Standard for Software Configuration Management Plans
- Best practices for scientific computing reproducibility ## Complete Source Code ```{literalinclude} ../../../src/optimization/core/results_manager.py
:language: python
:linenos:
```

---

## Classes

### `OptimizationMetadata`

metadata for optimization results.

#### Source Code ```

{literalinclude} ../../../src/optimization/core/results_manager.py
:language: python
:pyobject: OptimizationMetadata
:linenos:
```

---

## `OptimizationResults`

Complete optimization results structure.

### Source Code ```

{literalinclude} ../../../src/optimization/core/results_manager.py

:language: python
:pyobject: OptimizationResults
:linenos:
```

### `OptimizationResultsManager`

Advanced management system for PSO optimization results. This class provides functionality for storing, loading, analyzing,
and comparing optimization results with full provenance tracking. #### Source Code ```{literalinclude} ../../../src/optimization/core/results_manager.py
:language: python
:pyobject: OptimizationResultsManager
:linenos:
``` #### Methods (16) ##### `__init__(self, results_directory)` [View full source →](#method-optimizationresultsmanager-__init__) ##### `save_results(self, results, run_id, format)` Save optimization results with metadata. [View full source →](#method-optimizationresultsmanager-save_results) ##### `_save_json(self, results, run_id)` Save results in JSON format. [View full source →](#method-optimizationresultsmanager-_save_json) ##### `_save_hdf5(self, results, run_id)` Save results in HDF5 format for large datasets. [View full source →](#method-optimizationresultsmanager-_save_hdf5) ##### `_save_npz(self, results, run_id)` Save results in NumPy NPZ format. [View full source →](#method-optimizationresultsmanager-_save_npz) ##### `load_results(self, filepath)` Load optimization results from file. [View full source →](#method-optimizationresultsmanager-load_results) ##### `_load_json(self, filepath)` Load results from JSON file. [View full source →](#method-optimizationresultsmanager-_load_json) ##### `_load_npz(self, filepath)` Load results from NPZ file. [View full source →](#method-optimizationresultsmanager-_load_npz) ##### `compare_results(self, result_paths, metrics)` Compare multiple optimization results. [View full source →](#method-optimizationresultsmanager-compare_results) ##### `_calculate_statistics(self, results)` Calculate statistics for optimization results. [View full source →](#method-optimizationresultsmanager-_calculate_statistics) ##### `_detect_stagnation_periods(self, convergence, threshold)` Detect periods of stagnation in convergence history. [View full source →](#method-optimizationresultsmanager-_detect_stagnation_periods) ##### `_calculate_clustering_coefficient(self, population)` Calculate clustering coefficient of final population. [View full source →](#method-optimizationresultsmanager-_calculate_clustering_coefficient) ##### `_perform_statistical_tests(self, results)` Perform statistical significance tests on results. [View full source →](#method-optimizationresultsmanager-_perform_statistical_tests) ##### `_generate_comparison_recommendations(self, results, comparison)` Generate recommendations based on comparison analysis. [View full source →](#method-optimizationresultsmanager-_generate_comparison_recommendations) ##### `_make_json_serializable(self, obj)` Convert object to JSON-serializable format. [View full source →](#method-optimizationresultsmanager-_make_json_serializable) ##### `generate_results_summary(self, run_id_pattern)` Generate summary of all results matching pattern. [View full source →](#method-optimizationresultsmanager-generate_results_summary)

---

## Functions

### `create_optimization_metadata(controller_type, config, seed)`

Create optimization metadata from configuration. Parameters

controller_type : str Type of controller being optimized
config : Dict[str, Any] Configuration dictionary
seed : int, optional Random seed used Returns
-------
OptimizationMetadata Complete metadata object #### Source Code ```{literalinclude} ../../../src/optimization/core/results_manager.py
:language: python
:pyobject: create_optimization_metadata
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `import json`
- `import logging`
- `import numpy as np`
- `import hashlib`
- `from datetime import datetime`
- `from pathlib import Path`
- `from typing import Any, Dict, List, Optional, Tuple, Union`
- `from dataclasses import dataclass, asdict`
- `import warnings` *... and 1 more*
