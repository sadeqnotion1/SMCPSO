# fault_detection.fdi

**Source:** `src\fault_detection\fdi.py`

## Module Overview

Compatibility import for fault detection and isolation system.

This module provides backward compatibility for old import paths.
The actual implementation is in src.analysis.fault_detection.fdi.

Usage:
    from src.fault_detection.fdi import FDIsystem      # Old style (works)
    from src.analysis.fault_detection.fdi import FDIsystem # New style (preferred)

## Complete Source Code

```{literalinclude} ../../../src/fault_detection/fdi.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from ..analysis.fault_detection.fdi import *`
