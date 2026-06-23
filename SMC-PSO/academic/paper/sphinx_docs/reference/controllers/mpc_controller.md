# controllers.mpc_controller

**Source:** `src\controllers\mpc_controller.py`

## Module Overview

Compatibility import for MPC controller.

This module provides backward compatibility for old import paths.
The actual implementation is in src.controllers.mpc.mpc_controller.

Usage:
    from src.controllers.mpc_controller import MPCController  # Old style (works)
    from src.controllers import MPCController                 # New style (preferred)

## Complete Source Code

```{literalinclude} ../../../src/controllers/mpc_controller.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .mpc.mpc_controller import MPCController, MPCWeights, _numeric_linearize_continuous`
