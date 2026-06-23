# core.__init__

**Source:** `src\core\__init__.py`

## Module Overview

Core module compatibility layer.
This module provides backward compatibility by re-exporting classes and functions
from their new modular locations, allowing legacy import paths to continue working
while maintaining the improved project structure.

## Complete Source Code

```{literalinclude} ../../../src/core/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from ..plant.models.simplified.dynamics import SimplifiedDIPDynamics as DIPDynamics`
- `from ..plant.models.full.dynamics import FullDIPDynamics`
- `from ..plant.models.lowrank.dynamics import LowRankDIPDynamics`
- `from ..simulation.core.simulation_context import SimulationContext`
- `from ..simulation.engines.simulation_runner import run_simulation`
