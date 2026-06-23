# optimization.objectives.multi.__init__

**Source:** `src\optimization\objectives\multi\__init__.py`

## Module Overview

Multi-objective optimization functions for control systems.
This module provides multi-objective cost functions that balance
competing control objectives like tracking performance, control effort,
robustness, and stability margins in control parameter tuning.

## Complete Source Code

```{literalinclude} ../../../src/optimization/objectives/multi/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .weighted_sum import WeightedSumObjective, AdaptiveWeightedSumObjective`
- `from .pareto import ParetoObjective`
