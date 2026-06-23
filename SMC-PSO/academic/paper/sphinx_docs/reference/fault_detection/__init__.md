# fault_detection.__init__

**Source:** `src\fault_detection\__init__.py`

## Module Overview

Compatibility import for fault detection system.

This module provides backward compatibility for old import paths.
The actual implementation is in src.analysis.fault_detection.

Usage:
    from src.fault_detection.fdi import FDIsystem      # Old style (works)
    from src.analysis.fault_detection import FDIsystem # New style (preferred)

## Complete Source Code

```{literalinclude} ../../../src/fault_detection/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from ..analysis.fault_detection import *`
