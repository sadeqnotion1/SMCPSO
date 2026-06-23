# optimization.objectives.system.__init__

**Source:** `src\optimization\objectives\system\__init__.py`

## Module Overview

System-level objective functions for control optimization.
This module provides objective functions that evaluate system-wide
performance metrics including energy efficiency, stability margins,
disturbance rejection, and overall system robustness.

## Complete Source Code

```{literalinclude} ../../../src/optimization/objectives/system/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .settling_time import SettlingTimeObjective, RiseTimeObjective`
- `from .overshoot import OvershootObjective, UndershootObjective`
- `from .steady_state import SteadyStateErrorObjective`
