# plant.models.dynamics

**Source:** `src\plant\models\dynamics.py`

## Module Overview

Plant models dynamics compatibility layer.
This module re-exports the dynamics classes and parameters from their new locations
for backward compatibility with legacy import paths.

## Complete Source Code

```{literalinclude} ../../../src/plant/models/dynamics.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from ...core.dynamics import DIPDynamics, DoubleInvertedPendulum, DIPParams`
