# controllers.smc.algorithms.classical.__init__

**Source:** `src\controllers\smc\algorithms\classical\__init__.py`

## Module Overview

Classical SMC Algorithm Package.

Modular implementation of Classical Sliding Mode Control split into focused components:
- Controller: Main orchestration and control computation
- Boundary Layer: Chattering reduction through boundary layer method
- Configuration: Type-safe parameter configuration

This replaces the monolithic 458-line classical SMC with focused modules.

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/classical/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .controller import ModularClassicalSMC`
- `from .boundary_layer import BoundaryLayer`
- `from .config import ClassicalSMCConfig`
- `from .controller import ClassicalSMC`
