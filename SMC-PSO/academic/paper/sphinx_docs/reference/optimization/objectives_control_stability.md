# optimization.objectives.control.stability

**Source:** `src\optimization\objectives\control\stability.py`

## Module Overview Stability

margin objective functions for control optimization

.

## Complete Source Code ```

{literalinclude}

../../../src/optimization/objectives/control/stability.py


:language: python
:linenos:
```

---

## Classes

### `StabilityMarginObjective`

**Inherits from:** `SimulationBasedObjective` Objective function for optimizing stability margins. This objective computes various stability metrics including:
- Lyapunov stability analysis
- Phase and gain margins (if linearized model available)
- Settling time and damping characteristics
- Pole placement assessment #### Source Code ```{literalinclude} ../../../src/optimization/objectives/control/stability.py
:language: python
:pyobject: StabilityMarginObjective
:linenos:
``` #### Methods (11) ##### `__init__(self, simulation_config, controller_factory, stability_metric, min_gain_margin, min_phase_margin, max_settling_time, reference_trajectory)` Initialize stability margin objective. [View full source →](#method-stabilitymarginobjective-__init__) ##### `_compute_objective_from_simulation(self, times, states, controls)` Compute stability objective from simulation results. [View full source →](#method-stabilitymarginobjective-_compute_objective_from_simulation) ##### `_compute_lyapunov_stability(self, times, states, controls)` Compute Lyapunov-based stability metric. [View full source →](#method-stabilitymarginobjective-_compute_lyapunov_stability) ##### `_compute_stability_margins(self, times, states, controls)` Compute gain and phase margins (requires linearized model). [View full source →](#method-stabilitymarginobjective-_compute_stability_margins) ##### `_compute_pole_placement(self, times, states, controls)` Assess pole placement from trajectory characteristics. [View full source →](#method-stabilitymarginobjective-_compute_pole_placement) ##### `_compute_settling_characteristics(self, times, states, controls)` Compute settling time and damping characteristics. [View full source →](#method-stabilitymarginobjective-_compute_settling_characteristics) ##### `_compute_composite_stability(self, times, states, controls)` Compute composite stability metric combining multiple measures. [View full source →](#method-stabilitymarginobjective-_compute_composite_stability) ##### `_detect_oscillations(self, times, signal)` Detect oscillatory behavior in signal. [View full source →](#method-stabilitymarginobjective-_detect_oscillations) ##### `_detect_growth(self, times, signal)` Detect growth/instability in signal. [View full source →](#method-stabilitymarginobjective-_detect_growth) ##### `_estimate_decay_rate(self, times, transient)` Estimate exponential decay rate from transient response. [View full source →](#method-stabilitymarginobjective-_estimate_decay_rate) ##### `get_stability_analysis(self, times, states, controls)` Get stability analysis. [View full source →](#method-stabilitymarginobjective-get_stability_analysis)

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from typing import Any, Dict, Optional, Union, Callable, Tuple`
- `import numpy as np`
- `import warnings`
- `from ..base import SimulationBasedObjective`
