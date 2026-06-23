# controllers.sta_smc

**Source:** `src\controllers\sta_smc.py`

## Module Overview

Compatibility import for Super-Twisting SMC controller.

This module provides backward compatibility for old import paths.
The actual implementation is in src.controllers.smc.sta_smc.

Usage:
    from src.controllers.sta_smc import SuperTwistingSMC  # Old style (works)
    from src.controllers import SuperTwistingSMC         # New style (preferred)

## Complete Source Code

```{literalinclude} ../../../src/controllers/sta_smc.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .smc.sta_smc import SuperTwistingSMC`
