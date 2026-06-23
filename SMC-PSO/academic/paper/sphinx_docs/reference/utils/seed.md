# utils.seed

**Source:** `src\utils\seed.py`

## Module Overview

Seed utilities compatibility layer.
This module re-exports the seed functions from their new modular location
for backward compatibility with legacy import paths.

## Complete Source Code

```{literalinclude} ../../../src/utils/seed.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .reproducibility.seed import set_global_seed, create_rng`
