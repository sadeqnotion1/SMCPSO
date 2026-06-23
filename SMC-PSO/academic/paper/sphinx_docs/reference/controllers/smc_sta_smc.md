# controllers.smc.sta_smc

**Source:** `src\controllers\smc\sta_smc.py`

## Module Overview

*No module docstring available.*

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/sta_smc.py
:language: python
:linenos:
```



## Classes

### `SuperTwistingSMC`

 Second‑order (super‑twisting) sliding‑mode controller for the double‑inverted pendulum.

 This controller implements the super‑twisting algorithm, a higher‑order
 sliding‑mode technique that achieves finite‑time convergence without
 requiring direct measurement of the sliding surface derivative.  Compared
 with conventional (first‑order) sliding‑mode control, the super‑twisting
 algorithm is known to mitigate chattering and reduce control effort,
 offering improved tracking accuracy.  The
 implementation uses a continuous saturation function within a boundary
 layer ``ε`` to approximate the sign of the sliding variable σ,
 consistent with the boundary‑layer approach for chattering reduction
.  The size of ``ε`` therefore controls
 the trade‑off between chattering attenuation and steady‑state accuracy
.

 **Gains:**

   - If a 2‑element sequence ``[K1, K2]`` is provided, the sliding‑surface
     gains and poles ``(k1, k2, λ1, λ2)`` are set to default values.
   - A 6‑element sequence ``[K1, K2, k1, k2, λ1, λ2]`` specifies all
     super‑twisting and surface parameters explicitly.

 **Sliding surface:**

 .. math::
     \sigma = k_1\,(\dot{\theta}_1 + \lambda_1\,\theta_1) + k_2\,(\dot{\theta}_2 + \lambda_2\,\theta_2).

 **Discrete‑time control law:**

 .. math::
     \begin{aligned}
     u &= u_{\\text{eq}} - K_1 \\sqrt{|\\sigma|}\\,\\operatorname{sat}\\left( \\frac{\\sigma}{\\epsilon} \\right) + z - d\\,\\sigma,\\\\
     z^+ &= z - K_2\\,\\operatorname{sat}\\left( \\frac{\\sigma}{\\epsilon} \\right)\\,dt,
     \end{aligned}

 where ``sat`` is a continuous approximation of ``sign`` (either linear or
 hyperbolic tangent), ``d`` is the optional damping gain and ``u_eq`` is
 the equivalent control derived from the dynamics model.  The final output
 ``u`` and the disturbance‑like internal state ``z`` are both saturated
 to lie within the actuator limits.

 The boundary layer ε (> 0) is validated at construction time to avoid
 division by zero in the saturated sign computation.  A well‑chosen ε
 ensures finite‑time convergence and reduces chattering.

 **Gain positivity (F‑4.SMCDesign.2 / RC‑04)**:  For finite‑time convergence of
 the super‑twisting algorithm the algorithmic gains ``K1`` and ``K2`` must
 be strictly positive and the sliding‑surface gains ``k1`` and ``k2`` together
 with the slope parameters ``λ1`` and ``λ2`` must also be strictly positive.
 Super‑twisting literature emphasises that positive constants are required to
 ensure robust finite‑time stability【MorenoOsorio2012†L27-L40】 and positive
 sliding‑surface coefficients guarantee that the error terms combine with
 positive weights【OkstateThesis2013†L1415-L1419】.  The constructor therefore
 validates all gains using ``require_positive`` and raises a ``ValueError``
 when any gain is non‑positive.

 **Returns:**

 A triple ``(u, (z, σ), history)`` containing the saturated control
 signal ``u``, the updated internal state and sliding surface value,
 and a history dictionary (empty for this controller).


#### Source Code

```{literalinclude} ../../../src/controllers/smc/sta_smc.py
:language: python
:pyobject: SuperTwistingSMC
:linenos:
```

#### Methods (14)

##### `__init__(self, gains, dt, max_force, damping_gain, boundary_layer, dynamics_model, switch_method, regularization, anti_windup_gain)`

Initialize a Super‑Twisting Sliding Mode Controller.

[View full source →](#method-supertwistingsmc-__init__)

##### `initialize_state(self)`

Return (z, sigma) initial internal state.

[View full source →](#method-supertwistingsmc-initialize_state)

##### `initialize_history(self)`

[View full source →](#method-supertwistingsmc-initialize_history)

##### `compute_control(self, state, state_vars, history)`

[View full source →](#method-supertwistingsmc-compute_control)

##### `validate_gains(self, gains_b)`

Vectorized feasibility check for super‑twisting SMC gains.

[View full source →](#method-supertwistingsmc-validate_gains)

##### `gains(self)`

Return a copy of the gains used to configure this controller.

[View full source →](#method-supertwistingsmc-gains)

##### `dyn(self)`

Access dynamics model via weakref.

[View full source →](#method-supertwistingsmc-dyn)

##### `dyn(self, value)`

Set dynamics model using weakref.

[View full source →](#method-supertwistingsmc-dyn)

##### `reset(self)`

Reset STA-SMC controller state.

[View full source →](#method-supertwistingsmc-reset)

##### `cleanup(self)`

Clean up controller resources (Issue #15).

[View full source →](#method-supertwistingsmc-cleanup)

##### `__del__(self)`

Destructor for automatic cleanup.

[View full source →](#method-supertwistingsmc-__del__)

##### `set_dynamics(self, dynamics_model)`

Attach dynamics model if available (used by u_eq if implemented).

[View full source →](#method-supertwistingsmc-set_dynamics)

##### `_compute_sliding_surface(self, state)`

[View full source →](#method-supertwistingsmc-_compute_sliding_surface)

##### `_compute_equivalent_control(self, state)`

Compute the model‑based equivalent control ``u_eq`` using Tikhonov regularisation.

[View full source →](#method-supertwistingsmc-_compute_equivalent_control)



## Functions

### `_sta_smc_control_numba(state, z, alg_gain_K1, alg_gain_K2, surf_gain_k1, surf_gain_k2, surf_lam1, surf_lam2, damping_gain, dt, max_force, boundary_layer, u_eq)`

**Decorators:** `@numba.njit(cache=True)`

Numba‑accelerated core of the Super‑Twisting SMC.

Uses a saturated sign function for sigma to maintain full control authority
outside the boundary layer and linear behavior inside it, which is required
for robust, finite‑time convergence of the super‑twisting algorithm.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/sta_smc.py
:language: python
:pyobject: _sta_smc_control_numba
:linenos:
```



### `_sta_smc_core(z, sigma, sgn_sigma, alg_gain_K1, alg_gain_K2, damping_gain, dt, max_force, u_eq, Kaw)`

**Decorators:** `@numba.njit(cache=True)`

Numba-accelerated core using precomputed sigma and its saturated sign.

Includes anti-windup back‑calculation: the integrator state ``z`` is
updated using the difference between the saturated and unsaturated
control multiplied by ``Kaw``【789743582768797†L224-L249】.  Returns
``(u_saturated, new_z, sigma)``.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/sta_smc.py
:language: python
:pyobject: _sta_smc_core
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import logging`
- `import weakref`
- `import numpy as np`
- `from ...utils import saturate`
- `from ...utils import STAOutput`
- `from typing import Optional, List, Tuple, Dict, Union`
