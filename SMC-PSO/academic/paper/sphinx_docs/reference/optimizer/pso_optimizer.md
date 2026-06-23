# optimizer.pso_optimizer

**Source:** `src\optimizer\pso_optimizer.py`

## Module Overview

PSO optimizer compatibility layer.
This module re-exports the PSO optimizer from its new modular location
for backward compatibility with legacy import paths.

## Complete Source Code

```{literalinclude} ../../../src/optimizer/pso_optimizer.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from ..optimization.algorithms.pso_optimizer import PSOTuner`
- `from ..simulation.engines.vector_sim import simulate_system_batch`
