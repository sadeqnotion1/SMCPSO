# optimization.validation.pso_bounds_optimizer

**Source:** `src\optimization\validation\pso_bounds_optimizer.py`

## Module Overview Advanced

PSO Parameter Bounds Optimization for Controller Factory Integration

. This module provides optimized parameter bounds validation and dynamic adjustment


for PSO optimization across all SMC controller types, addressing GitHub Issue #6
factory integration requirements. Features:
- Dynamic bounds optimization based on controller physics
- Multi-objective parameter space analysis
- Convergence-aware bounds adjustment
- Statistical validation of parameter effectiveness
- Performance-driven bounds refinement ## Complete Source Code ```{literalinclude} ../../../src/optimization/validation/pso_bounds_optimizer.py
:language: python
:linenos:
```

---

## Classes

### `BoundsOptimizationStrategy`

**Inherits from:** `Enum` Strategy for optimizing parameter bounds.

#### Source Code ```

{literalinclude} ../../../src/optimization/validation/pso_bounds_optimizer.py
:language: python
:pyobject: BoundsOptimizationStrategy
:linenos:
```

---

## `ControllerBoundsSpec`

Specification for controller parameter bounds.

### Source Code ```

{literalinclude} ../../../src/optimization/validation/pso_bounds_optimizer.py

:language: python
:pyobject: ControllerBoundsSpec
:linenos:
```

### `BoundsValidationResult`

Result of bounds validation analysis.

#### Source Code ```

{literalinclude} ../../../src/optimization/validation/pso_bounds_optimizer.py
:language: python
:pyobject: BoundsValidationResult
:linenos:
```

### `PSOBoundsOptimizer`

Advanced PSO parameter bounds optimizer for controller factory integration. Optimizes PSO parameter bounds for maximum convergence efficiency and

control performance across all SMC controller types. #### Source Code ```{literalinclude} ../../../src/optimization/validation/pso_bounds_optimizer.py
:language: python
:pyobject: PSOBoundsOptimizer
:linenos:
``` #### Methods (13) ##### `__init__(self, config_path)` Initialize PSO bounds optimizer. [View full source →](#method-psoboundsoptimizer-__init__) ##### `_initialize_controller_specifications(self)` Initialize controller-specific parameter specifications. [View full source →](#method-psoboundsoptimizer-_initialize_controller_specifications) ##### `optimize_bounds_for_controller(self, controller_type, strategy, max_optimization_time)` Optimize PSO parameter bounds for specific controller type. [View full source →](#method-psoboundsoptimizer-optimize_bounds_for_controller) ##### `_generate_bounds_candidates(self, controller_type, strategy, max_time)` Generate candidate bounds configurations for evaluation. [View full source →](#method-psoboundsoptimizer-_generate_bounds_candidates) ##### `_generate_performance_driven_bounds(self, controller_type)` Generate bounds based on empirical performance data. [View full source →](#method-psoboundsoptimizer-_generate_performance_driven_bounds) ##### `_generate_convergence_focused_bounds(self, controller_type)` Generate bounds optimized for PSO convergence properties. [View full source →](#method-psoboundsoptimizer-_generate_convergence_focused_bounds) ##### `_evaluate_bounds_candidates(self, controller_type, bounds_candidates, max_time)` Evaluate bounds candidates through PSO performance testing. [View full source →](#method-psoboundsoptimizer-_evaluate_bounds_candidates) ##### `_evaluate_single_bounds_candidate(self, controller_type, bounds, max_time)` Evaluate a single bounds candidate through PSO trials. [View full source →](#method-psoboundsoptimizer-_evaluate_single_bounds_candidate) ##### `_select_optimal_bounds(self, bounds_performance, strategy)` Select optimal bounds based on performance metrics and strategy. [View full source →](#method-psoboundsoptimizer-_select_optimal_bounds) ##### `_calculate_improvement_ratio(self, bounds_performance, original_bounds, optimal_bounds)` Calculate improvement ratio from bounds optimization. [View full source →](#method-psoboundsoptimizer-_calculate_improvement_ratio) ##### `_validate_optimized_bounds(self, controller_type, original_bounds, optimized_bounds)` Validate optimized bounds through testing. [View full source →](#method-psoboundsoptimizer-_validate_optimized_bounds) ##### `optimize_all_controller_bounds(self, strategy)` Optimize bounds for all controller types. [View full source →](#method-psoboundsoptimizer-optimize_all_controller_bounds) ##### `export_optimized_bounds_config(self, optimization_results, output_path)` Export optimized bounds as configuration file. [View full source →](#method-psoboundsoptimizer-export_optimized_bounds_config)

---

## Functions

### `run_pso_bounds_optimization()`

Run complete PSO bounds optimization workflow.

#### Source Code ```

{literalinclude} ../../../src/optimization/validation/pso_bounds_optimizer.py
:language: python
:pyobject: run_pso_bounds_optimization
:linenos:
```

---

## Dependencies This module imports: - `import numpy as np`

- `import logging`
- `from typing import Dict, List, Tuple, Any, Optional, Union`
- `from dataclasses import dataclass`
- `from enum import Enum`
- `import json`
- `from pathlib import Path`
- `from concurrent.futures import ThreadPoolExecutor, as_completed`
- `import time`
- `from src.controllers.factory import SMCType, create_smc_for_pso, get_gain_bounds_for_pso` *... and 4 more*
