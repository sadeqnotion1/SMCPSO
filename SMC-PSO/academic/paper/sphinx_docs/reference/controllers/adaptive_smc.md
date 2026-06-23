# controllers.adaptive_smc

**Source:** `src\controllers\adaptive_smc.py`

## Module Overview

Compatibility import for Adaptive SMC controller.

This module provides backward compatibility for old import paths.
The actual implementation is in src.controllers.smc.adaptive_smc.

Usage:
    from src.controllers.adaptive_smc import AdaptiveSMC  # Old style (works)
    from src.controllers import AdaptiveSMC               # New style (preferred)

## Complete Source Code

```{literalinclude} ../../../src/controllers/adaptive_smc.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .smc.adaptive_smc import AdaptiveSMC`
