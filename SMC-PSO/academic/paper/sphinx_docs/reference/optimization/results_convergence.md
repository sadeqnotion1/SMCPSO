# optimization.results.convergence

**Source:** `src\optimization\results\convergence.py`

## Module Overview

Convergence monitoring and analysis for optimization algorithms.

## Complete Source Code

```{literalinclude} ../../../src/optimization/results/convergence.py
:language: python
:linenos:
```



## Classes

### `ConvergenceMonitor`

**Inherits from:** `IConvergenceMonitor`

Professional convergence monitor with multiple criteria.

#### Source Code

```{literalinclude} ../../../src/optimization/results/convergence.py
:language: python
:pyobject: ConvergenceMonitor
:linenos:
```

#### Methods (5)

##### `__init__(self, max_iterations, tolerance, patience, min_improvement, target_fitness)`

Initialize convergence monitor.

[View full source →](#method-convergencemonitor-__init__)

##### `update(self, iteration, best_value, parameters)`

Update convergence monitor with new iteration data.

[View full source →](#method-convergencemonitor-update)

##### `check_convergence(self)`

Check if convergence criteria are met.

[View full source →](#method-convergencemonitor-check_convergence)

##### `reset(self)`

Reset convergence monitor.

[View full source →](#method-convergencemonitor-reset)

##### `convergence_history(self)`

Get convergence history data.

[View full source →](#method-convergencemonitor-convergence_history)



### `ConvergenceAnalyzer`

Analyze optimization convergence characteristics.

#### Source Code

```{literalinclude} ../../../src/optimization/results/convergence.py
:language: python
:pyobject: ConvergenceAnalyzer
:linenos:
```

#### Methods (7)

##### `__init__(self)`

Initialize convergence analyzer.

[View full source →](#method-convergenceanalyzer-__init__)

##### `analyze_convergence_rate(self, fitness_history)`

Analyze convergence rate characteristics.

[View full source →](#method-convergenceanalyzer-analyze_convergence_rate)

##### `_compute_linear_rate(self, log_fitness)`

Compute linear convergence rate in log space.

[View full source →](#method-convergenceanalyzer-_compute_linear_rate)

##### `_fit_exponential_decay(self, fitness)`

Fit exponential decay model to fitness.

[View full source →](#method-convergenceanalyzer-_fit_exponential_decay)

##### `_detect_plateaus(self, fitness, threshold)`

Detect plateau regions in fitness curve.

[View full source →](#method-convergenceanalyzer-_detect_plateaus)

##### `_identify_convergence_phases(self, fitness)`

Identify different phases of convergence.

[View full source →](#method-convergenceanalyzer-_identify_convergence_phases)

##### `compare_convergence_curves(self, curves)`

Compare multiple convergence curves.

[View full source →](#method-convergenceanalyzer-compare_convergence_curves)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Dict, List, Optional, Tuple`
- `import numpy as np`
- `from ..core.interfaces import ConvergenceMonitor as IConvergenceMonitor, ConvergenceStatus`
