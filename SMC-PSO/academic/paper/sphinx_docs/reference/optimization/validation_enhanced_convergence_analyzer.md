# optimization.validation.enhanced_convergence_analyzer

**Source:** `src\optimization\validation\enhanced_convergence_analyzer.py`

## Module Overview Enhanced

PSO Convergence Criteria and Validation Algorithms

.

## Advanced Mathematical Theory

### Convergence Detection


D(\mathcal{P}) = \frac{1}{N} \sum_{i=1}^{N} \|\vec{x}_i - \bar{\vec{x}}\|
``` **Convergence criterion:** ```{math}
D(\mathcal{P}^t) < \epsilon_d \quad \text{and} \quad |f^t_{best} - f^{t-w}_{best}| < \epsilon_f
``` ### Stagnation Detection **Improvement rate:** ```{math}

R_{imp}^t = \frac{f^{t-w}_{best} - f^t_{best}}{w}
``` **Stagnation if** $R_{imp}^t < \epsilon_{stag}$ for $T_{stag}$ iterations. ### Statistical Convergence Tests **Welch's t-test** for mean comparison: ```{math}
t = \frac{\bar{f}_A - \bar{f}_B}{\sqrt{\frac{s_A^2}{n_A} + \frac{s_B^2}{n_B}}}
``` **Confidence interval** for convergence value: ```{math}

\text{CI}_{95\%} = f_{best} \pm 1.96 \frac{\sigma}{\sqrt{M}}
``` ### Convergence Rate Analysis **Linear convergence:** ```{math}
\|\vec{x}^{t+1} - \vec{x}^*\| \leq c \|\vec{x}^t - \vec{x}^*\|, \quad c < 1
``` **Superlinear convergence:** ```{math}

\lim_{t \to \infty} \frac{\|\vec{x}^{t+1} - \vec{x}^*\|}{\|\vec{x}^t - \vec{x}^*\|} = 0
``` **Quadratic convergence:** ```{math}
\|\vec{x}^{t+1} - \vec{x}^*\| \leq c \|\vec{x}^t - \vec{x}^*\|^2
``` ### Plateau Detection **Plateau metric** over window $w$: ```{math}

P^t = \max_{\tau=t-w}^{t} f^{\tau}_{best} - f^t_{best}
``` **Plateau detected if** $P^t < \epsilon_p$ for $T_p$ iterations. ## Architecture Diagram ```{mermaid}
graph TD A[Optimization Results] --> B[Compute Diversity] B --> C[Compute Improvement Rate] C --> D[Statistical Tests] D --> E{Diversity Check} E -->|D < ε_d| F[Low Diversity] E -->|D ≥ ε_d| G[Good Diversity] F --> H[Stagnation Check] G --> H H --> I{R_imp < ε_stag?} I -->|Yes| J[Stagnation Detected] I -->|No| K[Still Improving] J --> L[Plateau Detection] K --> L L --> M{Plateau?} M -->|Yes| N[Convergence Confirmed] M -->|No| O[Continue Monitoring] N --> P[Convergence Report] O --> Q[Next Iteration] style E fill:#ff9 style I fill:#9cf style P fill:#9f9
``` ## Usage Examples ### Example 1: Basic Initialization ```python

from src.optimization.algorithms import * # Initialize with configuration
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
This module provides advanced convergence analysis and validation algorithms
for PSO optimization in the controller factory integration context. Features
include multi-criteria convergence detection, statistical validation, and
real-time convergence monitoring. Key Features:
- Multi-modal convergence detection
- Statistical significance testing
- Real-time convergence monitoring
- Adaptive convergence criteria
- Population diversity analysis
- Performance prediction algorithms ## Complete Source Code ```{literalinclude} ../../../src/optimization/validation/enhanced_convergence_analyzer.py
:language: python
:linenos:
```

---

## Classes

### `ConvergenceStatus`

**Inherits from:** `Enum` Enhanced convergence status indicators.

#### Source Code ```

{literalinclude} ../../../src/optimization/validation/enhanced_convergence_analyzer.py

:language: python
:pyobject: ConvergenceStatus
:linenos:
```

### `ConvergenceCriterion`

**Inherits from:** `Enum` Types of convergence criteria.

#### Source Code ```

{literalinclude} ../../../src/optimization/validation/enhanced_convergence_analyzer.py
:language: python
:pyobject: ConvergenceCriterion
:linenos:
```

### `ConvergenceMetrics`

convergence metrics.

#### Source Code ```

{literalinclude} ../../../src/optimization/validation/enhanced_convergence_analyzer.py

:language: python
:pyobject: ConvergenceMetrics
:linenos:
```

### `ConvergenceCriteria`

Adaptive convergence criteria configuration.

#### Source Code ```

{literalinclude} ../../../src/optimization/validation/enhanced_convergence_analyzer.py
:language: python
:pyobject: ConvergenceCriteria
:linenos:
```

### `EnhancedConvergenceAnalyzer`

Advanced PSO convergence analysis with multi-criteria validation. Provides convergence monitoring, statistical validation,

and performance prediction for PSO optimization in controller factory
integration scenarios. #### Source Code ```{literalinclude} ../../../src/optimization/validation/enhanced_convergence_analyzer.py
:language: python
:pyobject: EnhancedConvergenceAnalyzer
:linenos:
``` #### Methods (17) ##### `__init__(self, criteria, controller_type)` Initialize enhanced convergence analyzer. [View full source →](#method-enhancedconvergenceanalyzer-__init__) ##### `_apply_controller_specific_tuning(self)` Apply controller-specific convergence criteria tuning. [View full source →](#method-enhancedconvergenceanalyzer-_apply_controller_specific_tuning) ##### `analyze_convergence(self, iteration, best_fitness, population_fitness, population_positions)` convergence analysis for current PSO iteration. [View full source →](#method-enhancedconvergenceanalyzer-analyze_convergence) ##### `check_convergence(self, metrics)` Multi-criteria convergence check with detailed analysis. [View full source →](#method-enhancedconvergenceanalyzer-check_convergence) ##### `_calculate_population_diversity(self, positions)` Calculate population diversity using average pairwise distance. [View full source →](#method-enhancedconvergenceanalyzer-_calculate_population_diversity) ##### `_calculate_convergence_velocity(self)` Calculate convergence velocity using fitness improvement rate. [View full source →](#method-enhancedconvergenceanalyzer-_calculate_convergence_velocity) ##### `_calculate_improvement_rate(self)` Calculate relative improvement rate over recent iterations. [View full source →](#method-enhancedconvergenceanalyzer-_calculate_improvement_rate) ##### `_calculate_stagnation_score(self)` Calculate stagnation score based on recent fitness variations. [View full source →](#method-enhancedconvergenceanalyzer-_calculate_stagnation_score) ##### `_calculate_diversity_loss_rate(self)` Calculate rate of population diversity loss. [View full source →](#method-enhancedconvergenceanalyzer-_calculate_diversity_loss_rate) ##### `_predict_remaining_iterations(self)` Predict remaining iterations until convergence. [View full source →](#method-enhancedconvergenceanalyzer-_predict_remaining_iterations) ##### `_estimate_convergence_probability(self)` Estimate probability of successful convergence. [View full source →](#method-enhancedconvergenceanalyzer-_estimate_convergence_probability) ##### `_calculate_statistical_confidence(self)` Calculate statistical confidence in convergence assessment. [View full source →](#method-enhancedconvergenceanalyzer-_calculate_statistical_confidence) ##### `_check_statistical_convergence(self)` Check for statistical convergence using hypothesis testing. [View full source →](#method-enhancedconvergenceanalyzer-_check_statistical_convergence) ##### `_detect_premature_convergence(self, metrics)` Detect premature convergence conditions. [View full source →](#method-enhancedconvergenceanalyzer-_detect_premature_convergence) ##### `_update_convergence_status(self, metrics)` Update internal convergence status based on metrics. [View full source →](#method-enhancedconvergenceanalyzer-_update_convergence_status) ##### `get_convergence_diagnostics(self)` Get convergence diagnostics. [View full source →](#method-enhancedconvergenceanalyzer-get_convergence_diagnostics) ##### `export_convergence_analysis(self, output_path)` Export detailed convergence analysis. [View full source →](#method-enhancedconvergenceanalyzer-export_convergence_analysis)

### `PSOConvergenceValidator`

Validation framework for PSO convergence algorithms. Tests and validates convergence detection accuracy across different
optimization scenarios and controller types. #### Source Code ```{literalinclude} ../../../src/optimization/validation/enhanced_convergence_analyzer.py
:language: python
:pyobject: PSOConvergenceValidator
:linenos:
``` #### Methods (3) ##### `__init__(self)` Initialize PSO convergence validator. [View full source →](#method-psoconvergencevalidator-__init__) ##### `validate_convergence_detection(self, controller_type, test_scenarios)` Validate convergence detection accuracy for controller type. [View full source →](#method-psoconvergencevalidator-validate_convergence_detection) ##### `_run_convergence_test_scenario(self, controller_type, scenario)` Run a single convergence detection test scenario. [View full source →](#method-psoconvergencevalidator-_run_convergence_test_scenario)

---

## Functions

### `run_enhanced_convergence_validation()`

Run PSO convergence validation.

#### Source Code ```

{literalinclude} ../../../src/optimization/validation/enhanced_convergence_analyzer.py

:language: python
:pyobject: run_enhanced_convergence_validation
:linenos:
```

---

## Dependencies This module imports: - `import numpy as np`
- `import logging`
- `from typing import Dict, List, Tuple, Any, Optional, Callable, Union`
- `from dataclasses import dataclass, field`
- `from enum import Enum`
- `import time`
- `from scipy import stats`
- `from scipy.signal import savgol_filter`
- `import warnings`
- `from src.controllers.factory import SMCType` *... and 3 more*
