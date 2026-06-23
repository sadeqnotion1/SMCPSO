# controllers.swing_up_smc

**Source:** `src\controllers\swing_up_smc.py`

## Module Overview

Swing-up SMC controller compatibility module.

This module provides backward compatibility for test modules that expect
swing-up SMC functionality at src.controllers.swing_up_smc. All functionality
is re-exported from the actual implementation location.

## Complete Source Code

```{literalinclude} ../../../src/controllers/swing_up_smc.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .specialized.swing_up_smc import *`
