# optimization.tuning.pso_hyperparameter_optimizer

**Source:** `src\optimization\tuning\pso_hyperparameter_optimizer.py`

## Module Overview Advanced

PSO Hyperparameter Optimization for Factory-Generated Controllers

. This module provides sophisticated hyperparameter optimization for PSO algorithms


specifically tuned for factory-generated SMC controllers. Features include adaptive
parameter adjustment, multi-objective optimization, and controller-specific tuning. Key Features:
- Adaptive PSO hyperparameter optimization
- Controller-specific parameter tuning
- Multi-objective optimization (convergence speed vs quality)
- Population dynamics optimization
- Real-time parameter adaptation
- Performance-driven hyperparameter selection ## Complete Source Code ```{literalinclude} ../../../src/optimization/tuning/pso_hyperparameter_optimizer.py
:language: python
:linenos:
```

---

## Classes

### `OptimizationObjective`

**Inherits from:** `Enum` PSO optimization objectives.

#### Source Code ```

{literalinclude} ../../../src/optimization/tuning/pso_hyperparameter_optimizer.py
:language: python
:pyobject: OptimizationObjective
:linenos:
```

---

## `PSOParameterType`

**Inherits from:** `Enum` Types of PSO parameters to optimize.

### Source Code ```

{literalinclude} ../../../src/optimization/tuning/pso_hyperparameter_optimizer.py

:language: python
:pyobject: PSOParameterType
:linenos:
```

### `PSOHyperparameters`

PSO hyperparameter configuration.

#### Source Code ```

{literalinclude} ../../../src/optimization/tuning/pso_hyperparameter_optimizer.py
:language: python
:pyobject: PSOHyperparameters
:linenos:
```

### `OptimizationResult`

Result of hyperparameter optimization.

#### Source Code ```

{literalinclude} ../../../src/optimization/tuning/pso_hyperparameter_optimizer.py

:language: python
:pyobject: OptimizationResult
:linenos:
```

### `PSOHyperparameterOptimizer`

Advanced PSO hyperparameter optimizer for factory-generated controllers. Optimizes PSO hyperparameters specifically for each controller type to maximize
convergence efficiency and solution quality in the factory integration context. #### Source Code ```{literalinclude} ../../../src/optimization/tuning/pso_hyperparameter_optimizer.py
:language: python
:pyobject: PSOHyperparameterOptimizer
:linenos:
``` #### Methods (13) ##### `__init__(self, config_path)` Initialize PSO hyperparameter optimizer. [View full source →](#method-psohyperparameteroptimizer-__init__) ##### `_initialize_parameter_bounds(self)` Initialize search bounds for PSO hyperparameters. [View full source →](#method-psohyperparameteroptimizer-_initialize_parameter_bounds) ##### `_initialize_baseline_parameters(self)` Initialize baseline PSO parameters for each controller type. [View full source →](#method-psohyperparameteroptimizer-_initialize_baseline_parameters) ##### `optimize_hyperparameters(self, controller_type, objective, max_time)` Optimize PSO hyperparameters for specific controller type. [View full source →](#method-psohyperparameteroptimizer-optimize_hyperparameters) ##### `_create_objective_function(self, controller_type, objective)` Create objective function for hyperparameter optimization. [View full source →](#method-psohyperparameteroptimizer-_create_objective_function) ##### `_parameters_from_vector(self, vector)` Convert optimization vector to PSO hyperparameters. [View full source →](#method-psohyperparameteroptimizer-_parameters_from_vector) ##### `_parameters_to_vector(self, params)` Convert PSO hyperparameters to optimization vector. [View full source →](#method-psohyperparameteroptimizer-_parameters_to_vector) ##### `_evaluate_pso_performance(self, controller_type, params)` Evaluate PSO performance with given hyperparameters. [View full source →](#method-psohyperparameteroptimizer-_evaluate_pso_performance) ##### `_run_optimization(self, objective_function, controller_type, max_time)` Run hyperparameter optimization using differential evolution. [View full source →](#method-psohyperparameteroptimizer-_run_optimization) ##### `_validate_optimized_parameters(self, controller_type, optimized_params, max_time)` Validate optimized parameters through testing. [View full source →](#method-psohyperparameteroptimizer-_validate_optimized_parameters) ##### `_calculate_improvement_ratio(self, baseline_params, optimized_params, controller_type)` Calculate improvement ratio from parameter optimization. [View full source →](#method-psohyperparameteroptimizer-_calculate_improvement_ratio) ##### `optimize_all_controllers(self, objective)` Optimize hyperparameters for all controller types. [View full source →](#method-psohyperparameteroptimizer-optimize_all_controllers) ##### `export_optimized_configuration(self, optimization_results, output_path)` Export optimized hyperparameters as configuration file. [View full source →](#method-psohyperparameteroptimizer-export_optimized_configuration)

---

## Functions

### `run_pso_hyperparameter_optimization()`

Run complete PSO hyperparameter optimization workflow.

#### Source Code ```

{literalinclude} ../../../src/optimization/tuning/pso_hyperparameter_optimizer.py

:language: python
:pyobject: run_pso_hyperparameter_optimization
:linenos:
```

---

## Dependencies This module imports: - `import numpy as np`
- `import logging`
- `from typing import Dict, List, Tuple, Any, Optional, Union, Callable`
- `from dataclasses import dataclass, field`
- `from enum import Enum`
- `import time`
- `import json`
- `from concurrent.futures import ThreadPoolExecutor, as_completed`
- `from scipy.optimize import differential_evolution, minimize`
- `import warnings` *... and 4 more*
