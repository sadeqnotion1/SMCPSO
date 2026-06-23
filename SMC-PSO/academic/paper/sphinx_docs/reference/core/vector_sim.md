# core.vector_sim

**Source:** `src\core\vector_sim.py`

## Module Overview

Compatibility import module for vector simulation functionality.

This module provides backward compatibility for test modules that expect
vector simulation components at src.core.vector_sim. All functionality
is re-exported from the actual implementation location.

## Complete Source Code

```{literalinclude} ../../../src/core/vector_sim.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from src.simulation.engines.vector_sim import *`
- `from src.simulation.engines.vector_sim import simulate, simulate_system_batch`
