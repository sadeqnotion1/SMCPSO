# controllers.smc.classic_smc

**Source:** `src\controllers\smc\classic_smc.py`

## Module Overview

*No module docstring available.*

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/classic_smc.py
:language: python
:linenos:
```



## Classes

### `ClassicalSMC`

Classical Sliding‑Mode Controller for a double‑inverted pendulum.

This controller implements the conventional first‑order sliding‑mode law
consisting of a model‑based equivalent control ``u_eq`` and a robust
discontinuous term.  The robust term uses a continuous approximation to
the sign function (either a hyperbolic tangent or a piecewise‑linear
saturation) within a boundary layer of width ``epsilon`` to attenuate
chattering.  Introducing a boundary layer around the switching surface
replaces the discontinuous signum control with a continuous function,
thereby reducing high‑frequency oscillations.  A number of authors
note that the boundary‑layer approximation attenuates chattering at
the cost of introducing a finite steady‑state tracking error; for
example, a discussion of chattering reduction methods emphasises
that the boundary‑layer method "reduces chattering but leads to a finite
steady state error".  The user should therefore
select ``epsilon`` to balance chattering reduction against steady‑state
accuracy.

Two switching functions are available: ``tanh`` (smooth hyperbolic
tangent) and ``linear`` (piecewise‑linear saturation).  The ``linear``
switch approximates the sign function more harshly by clipping the
sliding surface directly, which can degrade robustness near the origin
because the control gain effectively drops to zero for small errors.
In contrast, the ``tanh`` switch retains smoothness and maintains a
nonzero slope through the origin, preserving control authority in a
neighbourhood of the sliding surface.  Users should prefer
``tanh`` unless there is a compelling reason to adopt the linear
saturation and should be aware that linear saturation may cause
increased steady‑state error and slower convergence near the origin.

A small diagonal ``regularization`` is added to the inertia matrix during
inversion to ensure positive definiteness and numerical robustness.
Adding a tiny constant to the diagonal of a symmetric matrix is a
well‑known regularisation technique: in the context of covariance
matrices, Leung and colleagues recommend “adding a small, positive
constant to the diagonal” to ensure the matrix is invertible.

Parameters are typically supplied by a factory that reads a central
configuration.  Each gain vector must contain exactly six elements in the
order ``[k1, k2, lam1, lam2, K, kd]``.  The maximum force ``max_force``
sets the saturation limit for the final control command.

The optional ``controllability_threshold`` parameter decouples
controllability from the boundary layer ``epsilon``.  Earlier
implementations compared the magnitude of ``L·M^{-1}·B`` against
``epsilon`` to decide whether to compute the equivalent control.  This
conflation of chattering mitigation with controllability made it
difficult to tune each effect separately.  ``controllability_threshold``
defines a lower bound on ``|L·M^{-1}·B|`` below which the equivalent
control is suppressed.  If unspecified, a default of ``1e‑4`` is used
based on matrix conditioning guidelines.  The
boundary layer width ``epsilon`` should therefore be chosen solely to
trade off between chattering and steady‑state error, while
``controllability_threshold`` governs when the model‑based feedforward
term is applied.

**Gain positivity (F‑4.SMCDesign.2 / RC‑04)** – Sliding‑mode theory
requires that the sliding‑surface gains ``k1``, ``k2`` and the slope
coefficients ``lam1``, ``lam2`` be strictly positive.  Utkin and
Levant note that the discontinuous control gain ``k`` must be a
positive constant【Rhif2012†L563-L564】, and the slope ``λ`` of the
sliding function must be chosen positive to ensure Hurwitz
stability【ModelFreeSMC2018†L340-L345】.  The switching gain ``K`` must
also be strictly positive to drive the system to the sliding surface,
while the derivative gain ``kd`` should be non‑negative to provide
damping.  The constructor validates these constraints and raises
``ValueError`` when violated.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/classic_smc.py
:language: python
:pyobject: ClassicalSMC
:linenos:
```

#### Methods (13)

##### `__init__(self, gains, max_force, boundary_layer, dynamics_model, regularization, switch_method)`

Initialize the controller.

[View full source →](#method-classicalsmc-__init__)

##### `gains(self)`

Return the list of gains used by this controller.

[View full source →](#method-classicalsmc-gains)

##### `dyn(self)`

Access dynamics model via weakref.

[View full source →](#method-classicalsmc-dyn)

##### `dyn(self, value)`

Set dynamics model using weakref.

[View full source →](#method-classicalsmc-dyn)

##### `initialize_state(self)`

No internal state for classical SMC; returns an empty tuple.

[View full source →](#method-classicalsmc-initialize_state)

##### `initialize_history(self)`

No history tracked for classical SMC; returns an empty dict.

[View full source →](#method-classicalsmc-initialize_history)

##### `validate_gains(gains)`

Validate that exactly six gains have been provided for the classical SMC.

[View full source →](#method-classicalsmc-validate_gains)

##### `_compute_sliding_surface(self, state)`

Compute the sliding surface value, ``sigma``.

[View full source →](#method-classicalsmc-_compute_sliding_surface)

##### `_compute_equivalent_control(self, state)`

Compute the model-based equivalent control ``u_eq`` with enhanced robustness.

[View full source →](#method-classicalsmc-_compute_equivalent_control)

##### `compute_control(self, state, state_vars, history)`

Compute the control input for the classical SMC.

[View full source →](#method-classicalsmc-compute_control)

##### `reset(self)`

Reset ClassicalSMC controller state.

[View full source →](#method-classicalsmc-reset)

##### `cleanup(self)`

Explicit memory cleanup to prevent leaks.

[View full source →](#method-classicalsmc-cleanup)

##### `__del__(self)`

Destructor for automatic cleanup.

[View full source →](#method-classicalsmc-__del__)



## Dependencies

This module imports:

- `import numpy as np`
- `import logging`
- `import weakref`
- `from ...utils import saturate`
- `from ...utils import ClassicalSMCOutput`
- `from typing import TYPE_CHECKING, List, Tuple, Dict, Optional, Union, Sequence, Any`
