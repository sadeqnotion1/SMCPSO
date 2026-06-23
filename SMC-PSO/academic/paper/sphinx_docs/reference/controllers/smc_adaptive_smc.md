# controllers.smc.adaptive_smc

**Source:** `src\controllers\smc\adaptive_smc.py`

## Module Overview

Adaptive sliding‑mode controller with online gain adaptation.

This implementation follows the classical adaptive SMC structure in
which the switching gain ``K`` is increased when the sliding
surface magnitude exceeds a dead zone and decays toward a nominal
value otherwise.  No control‑rate term is included in the
adaptation law; theoretical analyses show that augmenting the
adaptation with a rate‑dependent term can destabilise the closed
loop and is not required for convergence.
A continuous boundary layer of width ``boundary_layer`` is used to
approximate the discontinuous sign function, reducing chattering
at the expense of steady‑state accuracy.  The
boundary layer thickness must therefore be selected to balance
robustness and tracking error.  All gains
are validated for positivity to satisfy sliding‑mode stability
conditions.

Parameters
----------
gains : list of float
    Five gains in the order ``[k1, k2, lam1, lam2, gamma]``.
dt : float
    Simulation timestep (s); must be strictly positive.
max_force : float
    Saturation limit for the total control input.  Final commands
    are clipped to the interval [−max_force, +max_force].
leak_rate : float
    Leak coefficient that pulls the adaptive gain ``K`` back toward
    its nominal value ``K_init`` over time.  Non‑negative.
adapt_rate_limit : float
    Maximum rate of change allowed for ``K``.  Limits sudden
    growth or decay of the adaptive gain.
K_min, K_max : float
    Lower and upper bounds for ``K``.  These must satisfy
    ``0 < K_min ≤ K_init ≤ K_max``.  Bounding the gain ensures
    the controller remains within a physically reasonable range.
smooth_switch : bool
    If ``True`` the continuous switching function uses a hyperbolic
    tangent; otherwise a linear saturation is used.
boundary_layer : float
    Width of the boundary layer (ε) used in the switching function.
    Must be strictly positive; see [Utkin 1992] for the effects of
    boundary‑layer size on chattering.
dead_zone : float
    Radius around σ=0 in which adaptation is frozen to prevent
    wind‑up.  Outside this zone the adaptive gain increases
    proportionally to ``|σ|``.
K_init : float, optional
    Initial and nominal value of the adaptive gain ``K``.
alpha : float, optional
    Proportional term weighting the sliding surface in the control
    law.  Must be non‑negative.
**kwargs : dict
    Additional unused keyword arguments for forward compatibility.

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/adaptive_smc.py
:language: python
:linenos:
```



## Classes

### `AdaptiveSMC`

Adaptive Sliding Mode Controller that adjusts gain K online.

The controller prevents gain wind-up by using a dead zone around the sliding surface.
When |σ| ≤ dead_zone, the gain K only decreases via the leak term, preventing
uncontrolled growth during chattering.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/adaptive_smc.py
:language: python
:pyobject: AdaptiveSMC
:linenos:
```

#### Methods (10)

##### `__init__(self, gains, dt, max_force, leak_rate, adapt_rate_limit, K_min, K_max, smooth_switch, boundary_layer, dead_zone, K_init, alpha)`

Initialize Adaptive SMC controller.

[View full source →](#method-adaptivesmc-__init__)

##### `gains(self)`

Return a copy of the gain vector supplied to this controller.

[View full source →](#method-adaptivesmc-gains)

##### `validate_gains(gains)`

Validate that a suitable gain sequence has been provided.

[View full source →](#method-adaptivesmc-validate_gains)

##### `initialize_state(self)`

Initialize internal state: (K, last_u, time_in_sliding).

[View full source →](#method-adaptivesmc-initialize_state)

##### `initialize_history(self)`

Initialize history dictionary.

[View full source →](#method-adaptivesmc-initialize_history)

##### `compute_control(self, state, state_vars, history)`

Compute the adaptive sliding–mode control law with unified anti‑windup.

[View full source →](#method-adaptivesmc-compute_control)

##### `set_dynamics(self, dynamics_model)`

Set dynamics model (for compatibility, not used in this implementation).

[View full source →](#method-adaptivesmc-set_dynamics)

##### `reset(self)`

Reset AdaptiveSMC controller state.

[View full source →](#method-adaptivesmc-reset)

##### `cleanup(self)`

Clean up controller resources (Issue #15).

[View full source →](#method-adaptivesmc-cleanup)

##### `__del__(self)`

Destructor for automatic cleanup.

[View full source →](#method-adaptivesmc-__del__)



## Dependencies

This module imports:

- `import numpy as np`
- `import weakref`
- `from typing import Dict, Tuple, Optional, List`
