# controllers.smc.hybrid_adaptive_sta_smc

**Source:** `src\controllers\smc\hybrid_adaptive_sta_smc.py`

## Module Overview

*No module docstring available.*

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/hybrid_adaptive_sta_smc.py
:language: python
:linenos:
```



## Classes

### `HybridAdaptiveSTASMC`

Hybrid Adaptive Super–Twisting SMC for a double‑inverted pendulum.

This controller combines an adaptive gain law with a second‑order
sliding‑mode algorithm.  The sliding surface

    ``s = c1*(θ̇1 + λ1 θ1) + c2*(θ̇2 + λ2 θ2) + k_c*(ẋ + λ_c x)``

uses positive weights ``c1, c2, λ1, λ2`` for the pendulum joints and
optional cart gains ``k_c, λ_c``.  The default formulation uses **absolute
coordinates** for the second pendulum (``θ2`` and ``θ̇2``) because this
simplifies stability proofs【895515998216162†L326-L329】.  Setting
``use_relative_surface=True`` switches to a **relative formulation**
``θ2−θ1`` and ``θ̇2−θ̇1`` that can decouple the pendula.  Exposing this
toggle allows users to explore both designs without modifying code.

Control law:

    ``u = −k1 * sqrt(|s|) * sat(s) + u_int − k_d * s + u_eq``
    ``u̇_int = −k2 * sat(s)``

where ``sat(s)`` is a continuous approximation to ``sign(s)`` over a
boundary layer of width ``sat_soft_width``.  The gains ``k1`` and
``k2`` adapt online using piecewise‑linear laws with a dead zone
``dead_zone``; when ``|s|`` lies within the dead zone, adaptation halts
and the integral term ``u_int`` freezes.  External parameters
``k1_max`` and ``k2_max`` bound the adaptive gains to avoid runaway
growth, and ``u_int_max`` limits the integral state.  Separating these
bounds from the actuator saturation ``max_force`` preserves adaptation
capability even when the actuator saturates【895515998216162†L326-L329】.

The model‑based equivalent control ``u_eq`` can reduce steady‑state
error by cancelling nominal dynamics.  This implementation enables
``u_eq`` by default; its computation is controlled via the
``enable_equivalent`` parameter.  Setting ``enable_equivalent=False``
disables the feedforward term entirely.  A deprecated alias
``use_equivalent`` remains supported for backward compatibility: when
both flags are provided, the alias takes precedence and a
deprecation warning is emitted.  Earlier versions disabled the
equivalent control by default; however, the revised design enables it
because the second‑order sliding law and adaptive gain ensure
robustness even with the model term【895515998216162†L326-L329】.

**Gain and boundary relationships (F‑4.HybridController.4 / RC‑04)**:  The
sliding‑surface coefficients ``c1``, ``c2``, ``λ1`` and ``λ2`` must be strictly
positive to define a valid Lyapunov surface【OkstateThesis2013†L1415-L1419】.  The
soft saturation width ``sat_soft_width`` acts as a boundary layer for the
continuous sign function and should not be smaller than the dead zone
``dead_zone``; choosing ``sat_soft_width ≥ dead_zone`` prevents chattering by
ensuring the approximation remains smooth throughout the dead zone【OkstateThesis2013†L1415-L1419】.
Initial adaptive gains ``k1_init`` and ``k2_init`` must lie within the
prescribed maxima ``k1_max`` and ``k2_max`` to avoid runaway adaptation and
guarantee that adaptation begins in a feasible region【OkstateThesis2013†L1415-L1419】.

**Cart recentering hysteresis:**
A PD term drives the cart back toward the origin when the cart
displacement exceeds a configurable high threshold.  Once engaged, the
recentering term disengages when the displacement falls below a lower
threshold.  This hysteresis prevents rapid switching of the
recentering action when the cart oscillates near the origin.  The
recentering behaviour is tuned via ``cart_gain``, ``cart_lambda``,
``cart_p_gain`` and ``cart_p_lambda``, and the thresholds
``recenter_high_thresh`` and ``recenter_low_thresh`` must satisfy
``0 ≤ low < high``; invalid values raise an error instead of being
silently clipped.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/hybrid_adaptive_sta_smc.py
:language: python
:pyobject: HybridAdaptiveSTASMC
:linenos:
```

#### Methods (15)

##### `__init__(self, gains, dt, max_force, k1_init, k2_init, gamma1, gamma2, dead_zone, dynamics_model)`

[View full source →](#method-hybridadaptivestasmc-__init__)

##### `validate_gains(self, gains_b)`

Vectorized feasibility check for hybrid adaptive STA-SMC gains.

[View full source →](#method-hybridadaptivestasmc-validate_gains)

##### `gains(self)`

[View full source →](#method-hybridadaptivestasmc-gains)

##### `dyn(self)`

Access dynamics model via weakref.

[View full source →](#method-hybridadaptivestasmc-dyn)

##### `dyn(self, value)`

Set dynamics model using weakref.

[View full source →](#method-hybridadaptivestasmc-dyn)

##### `set_dynamics(self, dynamics_model)`

Attach dynamics model providing _compute_physics_matrices(state)->(M,C,G).

[View full source →](#method-hybridadaptivestasmc-set_dynamics)

##### `initialize_state(self)`

[View full source →](#method-hybridadaptivestasmc-initialize_state)

##### `initialize_history(self)`

[View full source →](#method-hybridadaptivestasmc-initialize_history)

##### `_compute_taper_factor(self, abs_s)`

Compute tapering factor for adaptive gain growth.

[View full source →](#method-hybridadaptivestasmc-_compute_taper_factor)

##### `_compute_sliding_surface(self, state)`

Compute the sliding surface value s.

[View full source →](#method-hybridadaptivestasmc-_compute_sliding_surface)

##### `_compute_equivalent_control(self, state)`

Compute an approximate equivalent control based on the system

[View full source →](#method-hybridadaptivestasmc-_compute_equivalent_control)

##### `compute_control(self, state, state_vars, history)`

[View full source →](#method-hybridadaptivestasmc-compute_control)

##### `reset(self)`

Reset HybridAdaptiveSTASMC controller state.

[View full source →](#method-hybridadaptivestasmc-reset)

##### `cleanup(self)`

Clean up controller resources (Issue #15).

[View full source →](#method-hybridadaptivestasmc-cleanup)

##### `__del__(self)`

Destructor for automatic cleanup.

[View full source →](#method-hybridadaptivestasmc-__del__)



## Functions

### `_sat_tanh(x, width)`

Smooth sign via tanh with width>0; behaves like sign(x) for |x|>>width.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/hybrid_adaptive_sta_smc.py
:language: python
:pyobject: _sat_tanh
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Dict, Tuple, Any, List, Optional`
- `import numpy as np`
- `import weakref`
- `from ...utils import HybridSTAOutput`
