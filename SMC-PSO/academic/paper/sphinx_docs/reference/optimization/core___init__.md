# optimization.core.__init__

**Source:** `src\optimization\core\__init__.py`

## Module Overview

Core optimization framework interfaces and abstractions.

## Complete Source Code

```{literalinclude} ../../../src/optimization/core/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .interfaces import Optimizer, ObjectiveFunction, Constraint, OptimizationProblem, OptimizationResult, ParameterSpace, ConvergenceMonitor`
- `from .problem import OptimizationProblemBuilder, ControlOptimizationProblem`
- `from .parameters import ParameterBounds, ParameterMapping, ParameterValidator, ContinuousParameter, DiscreteParameter, ContinuousParameterSpace`
- `from .context import OptimizationContext, optimize`
