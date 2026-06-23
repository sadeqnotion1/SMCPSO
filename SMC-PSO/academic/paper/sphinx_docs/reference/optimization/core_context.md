# optimization.core.context

**Source:** `src\optimization\core\context.py`

## Module Overview

Optimization context and configuration management.

## Complete Source Code

```{literalinclude} ../../../src/optimization/core/context.py
:language: python
:linenos:
```



## Classes

### `OptimizationContext`

Context manager for optimization runs.

#### Source Code

```{literalinclude} ../../../src/optimization/core/context.py
:language: python
:pyobject: OptimizationContext
:linenos:
```

#### Methods (10)

##### `__init__(self, random_seed, working_directory, config)`

Initialize optimization context.

[View full source →](#method-optimizationcontext-__init__)

##### `set_problem(self, problem)`

Set optimization problem.

[View full source →](#method-optimizationcontext-set_problem)

##### `set_optimizer(self, optimizer)`

Set optimizer.

[View full source →](#method-optimizationcontext-set_optimizer)

##### `set_convergence_monitor(self, monitor)`

Set convergence monitor.

[View full source →](#method-optimizationcontext-set_convergence_monitor)

##### `run_optimization(self)`

Run optimization with current configuration.

[View full source →](#method-optimizationcontext-run_optimization)

##### `save_results(self, filepath)`

Save optimization results to file.

[View full source →](#method-optimizationcontext-save_results)

##### `load_results(self, filepath)`

Load optimization results from file.

[View full source →](#method-optimizationcontext-load_results)

##### `_create_results_summary(self)`

Create JSON-serializable results summary.

[View full source →](#method-optimizationcontext-_create_results_summary)

##### `create_optimizer_factory(self, algorithm_name)`

Factory method to create optimizers.

[View full source →](#method-optimizationcontext-create_optimizer_factory)

##### `get_available_algorithms(self)`

Get list of available optimization algorithms.

[View full source →](#method-optimizationcontext-get_available_algorithms)



## Functions

### `optimize(problem, algorithm, random_seed)`

Quick optimization function.

Parameters
----------
problem : OptimizationProblem
    Problem to optimize
algorithm : str, optional
    Algorithm name (default: 'pso')
random_seed : int, optional
    Random seed
**kwargs
    Algorithm-specific parameters

Returns
-------
OptimizationResult
    Optimization results

#### Source Code

```{literalinclude} ../../../src/optimization/core/context.py
:language: python
:pyobject: optimize
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, Optional, Union`
- `import numpy as np`
- `from pathlib import Path`
- `from .interfaces import OptimizationProblem, Optimizer, ConvergenceMonitor`
