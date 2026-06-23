# controllers.specialized.swing_up_smc

**Source:** `src\controllers\specialized\swing_up_smc.py`

## Module Overview

*No module docstring available.*

## Complete Source Code

```{literalinclude} ../../../src/controllers/specialized/swing_up_smc.py
:language: python
:linenos:
```



## Classes

### `_History`

**Inherits from:** `TypedDict`

#### Source Code

```{literalinclude} ../../../src/controllers/specialized/swing_up_smc.py
:language: python
:pyobject: _History
:linenos:
```



### `SwingUpSMC`

Energy-based swing-up + handoff to a stabilizing controller with hysteresis.

Modes:
  - 'swing': u = k_swing * cos(theta1) * theta1_dot
  - 'stabilize': delegate to provided SMC-like controller

Hysteresis:
  - 'swing' -> 'stabilize' when
        E_about_bottom >= switch_energy_factor * E_bottom
    AND |theta1|, |theta2| <= switch_angle_tolerance.
  - 'stabilize' -> 'swing' when
        E_about_bottom <  exit_energy_factor   * E_bottom
    AND (|theta1| > reentry_angle_tolerance OR |theta2| > reentry_angle_tolerance).

#### Source Code

```{literalinclude} ../../../src/controllers/specialized/swing_up_smc.py
:language: python
:pyobject: SwingUpSMC
:linenos:
```

#### Methods (9)

##### `__init__(self, dynamics_model, stabilizing_controller, energy_gain, switch_energy_factor, exit_energy_factor, switch_angle_tolerance, reentry_angle_tolerance, dt, max_force)`

Initialize controller.

[View full source →](#method-swingupsmc-__init__)

##### `initialize_state(self)`

[View full source →](#method-swingupsmc-initialize_state)

##### `initialize_history(self)`

[View full source →](#method-swingupsmc-initialize_history)

##### `_should_switch_to_swing(self, E_about_bottom, q1, q2)`

Determine if the controller should return to swing mode.

[View full source →](#method-swingupsmc-_should_switch_to_swing)

##### `_should_switch_to_stabilize(self, E_about_bottom, q1, q2)`

Return (should_switch, high_energy, small_angles).

[View full source →](#method-swingupsmc-_should_switch_to_stabilize)

##### `_update_mode(self, E_about_bottom, q1, q2, t, history)`

Centralized transition logic for both directions with detailed logging.

[View full source →](#method-swingupsmc-_update_mode)

##### `compute_control(self, state, state_vars, history)`

[View full source →](#method-swingupsmc-compute_control)

##### `mode(self)`

[View full source →](#method-swingupsmc-mode)

##### `switch_time(self)`

[View full source →](#method-swingupsmc-switch_time)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Any, Tuple, Dict, Optional, MutableMapping, Literal, TypedDict`
- `import numpy as np`
- `import logging`
