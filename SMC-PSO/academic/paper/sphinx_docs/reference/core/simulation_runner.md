# core.simulation_runner

**Source:** `src\core\simulation_runner.py`

## Module Overview

Simulation runner compatibility layer.
This module re-exports the simulation runner from its new modular location
for backward compatibility with legacy import paths.

## Complete Source Code

```{literalinclude} ../../../src/core/simulation_runner.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from ..simulation.engines.simulation_runner import run_simulation, SimulationRunner`
