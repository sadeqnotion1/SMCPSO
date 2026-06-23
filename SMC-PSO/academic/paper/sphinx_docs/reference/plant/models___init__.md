# plant.models.__init__

**Source:** `src\plant\models\__init__.py`

## Module Overview

Plant Dynamics Models.

Collection of dynamics models for the double inverted pendulum system
organized in a modular architecture for clarity and maintainability.

## Complete Source Code

```{literalinclude} ../../../src/plant/models/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .base import DynamicsModel, DynamicsResult, IntegrationMethod, BaseDynamicsModel, LinearDynamicsModel`
- `from .simplified import SimplifiedDIPConfig, SimplifiedPhysicsComputer, SimplifiedDIPDynamics`
- `from .full import FullDIPConfig, FullFidelityPhysicsComputer, FullDIPDynamics`
- `from .lowrank import LowRankDIPConfig, LowRankPhysicsComputer, LowRankDIPDynamics as ModularLowRankDynamics`
