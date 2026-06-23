# plant.models.lowrank.__init__

**Source:** `src\plant\models\lowrank\__init__.py`

## Module Overview

Low-rank Double Inverted Pendulum (DIP) Model Package.

Simplified implementation optimized for computational efficiency and fast prototyping.
Provides reduced-order dynamics while maintaining essential system behavior.

## Complete Source Code

```{literalinclude} ../../../src/plant/models/lowrank/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .config import LowRankDIPConfig`
- `from .physics import LowRankPhysicsComputer`
- `from .dynamics import LowRankDIPDynamics`
