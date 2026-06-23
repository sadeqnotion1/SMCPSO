# controllers.smc.algorithms.super_twisting.config

**Source:** `src\controllers\smc\algorithms\super_twisting\config.py`

## Module Overview

Configuration Schema for Super-Twisting SMC.

Type-safe configuration for Super-Twisting Sliding Mode Control (STA-SMC).
Implements second-order sliding mode control for finite-time convergence.

Mathematical Requirements:
- Twisting gains: K1 > K2 > 0 for stability and finite-time convergence
- Surface gains: [k1, k2, λ1, λ2] must be positive for Hurwitz stability
- Anti-windup: Prevents integrator windup in the twisting algorithm

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/super_twisting/config.py
:language: python
:linenos:
```



## Classes

### `SuperTwistingSMCConfig`

Type-safe configuration for Super-Twisting SMC controller.

Based on Super-Twisting algorithm theory:
- Twisting gains K1, K2 must satisfy K1 > K2 > 0 for finite-time stability
- Surface gains [k1, k2, λ1, λ2] must be positive for Hurwitz stability
- Power exponent α ∈ (0, 1) determines convergence rate

#### Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/super_twisting/config.py
:language: python
:pyobject: SuperTwistingSMCConfig
:linenos:
```

#### Methods (18)

##### `__post_init__(self)`

Validate configuration after creation.

[View full source →](#method-supertwistingsmcconfig-__post_init__)

##### `_validate_gains(self)`

Validate gain vector according to Super-Twisting theory.

[View full source →](#method-supertwistingsmcconfig-_validate_gains)

##### `_validate_twisting_parameters(self)`

Validate Super-Twisting specific parameters.

[View full source →](#method-supertwistingsmcconfig-_validate_twisting_parameters)

##### `_validate_other_parameters(self)`

Validate other configuration parameters.

[View full source →](#method-supertwistingsmcconfig-_validate_other_parameters)

##### `K1(self)`

First twisting gain.

[View full source →](#method-supertwistingsmcconfig-k1)

##### `K2(self)`

Second twisting gain.

[View full source →](#method-supertwistingsmcconfig-k2)

##### `k1(self)`

Joint 1 position gain.

[View full source →](#method-supertwistingsmcconfig-k1)

##### `k2(self)`

Joint 2 position gain.

[View full source →](#method-supertwistingsmcconfig-k2)

##### `lam1(self)`

Joint 1 velocity gain (λ₁).

[View full source →](#method-supertwistingsmcconfig-lam1)

##### `lam2(self)`

Joint 2 velocity gain (λ₂).

[View full source →](#method-supertwistingsmcconfig-lam2)

##### `get_twisting_gains(self)`

Get Super-Twisting gains (K1, K2).

[View full source →](#method-supertwistingsmcconfig-get_twisting_gains)

##### `get_surface_gains(self)`

Get sliding surface gains [k1, k2, λ1, λ2].

[View full source →](#method-supertwistingsmcconfig-get_surface_gains)

##### `check_stability_conditions(self)`

Check Super-Twisting stability conditions.

[View full source →](#method-supertwistingsmcconfig-check_stability_conditions)

##### `get_effective_anti_windup_gain(self)`

Get effective anti-windup gain.

[View full source →](#method-supertwistingsmcconfig-get_effective_anti_windup_gain)

##### `to_dict(self)`

Convert configuration to dictionary.

[View full source →](#method-supertwistingsmcconfig-to_dict)

##### `from_dict(cls, config_dict, dynamics_model)`

Create configuration from dictionary.

[View full source →](#method-supertwistingsmcconfig-from_dict)

##### `create_default(cls, gains, max_force, dt)`

Create configuration with sensible defaults.

[View full source →](#method-supertwistingsmcconfig-create_default)

##### `create_from_classical_gains(cls, classical_gains, K1, K2)`

Create Super-Twisting config from classical SMC gains.

[View full source →](#method-supertwistingsmcconfig-create_from_classical_gains)



## Dependencies

This module imports:

- `from typing import List, Optional`
- `from dataclasses import dataclass, field`
- `import math`
