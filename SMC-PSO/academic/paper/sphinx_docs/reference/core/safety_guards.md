# core.safety_guards

**Source:** `src\core\safety_guards.py`

## Module Overview

Safety guards compatibility layer.
This module re-exports the safety guard functions from their new modular location
for backward compatibility with legacy import paths.

## Complete Source Code

```{literalinclude} ../../../src/core/safety_guards.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from ..simulation.context.safety_guards import _guard_no_nan, _guard_energy, _guard_bounds`
