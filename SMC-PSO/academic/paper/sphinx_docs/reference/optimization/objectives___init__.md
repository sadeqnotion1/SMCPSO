# optimization.objectives.__init__

**Source:** `src\optimization\objectives\__init__.py`

## Module Overview

Optimization objective functions for control engineering applications.

## Complete Source Code

```{literalinclude} ../../../src/optimization/objectives/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .control.tracking import TrackingErrorObjective`
- `from .control.energy import EnergyConsumptionObjective, ControlEffortObjective`
- `from .control.stability import StabilityMarginObjective`
- `from .control.robustness import RobustnessObjective`
- `from .system.settling_time import SettlingTimeObjective, RiseTimeObjective`
- `from .system.overshoot import OvershootObjective, UndershootObjective`
- `from .system.steady_state import SteadyStateErrorObjective`
- `from .multi.weighted_sum import WeightedSumObjective, AdaptiveWeightedSumObjective`
- `from .multi.pareto import ParetoObjective`
- `from .base import SimulationBasedObjective, AnalyticalObjective, CompositeObjective`
