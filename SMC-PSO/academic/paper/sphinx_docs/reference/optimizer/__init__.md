# optimizer.__init__

**Source:** `src\optimizer\__init__.py`

## Module Overview

Optimizer compatibility layer.
This module provides backward compatibility by re-exporting optimizer classes
from their new modular locations, allowing legacy import paths to continue working.

## Complete Source Code

```{literalinclude} ../../../src/optimizer/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from ..optimization.algorithms.pso_optimizer import PSOTuner`
