# controllers.smc.algorithms.hybrid.config

**Source:** `src\controllers\smc\algorithms\hybrid\config.py`

## Module Overview

Configuration Schema for Hybrid SMC.

Type-safe configuration for Hybrid Sliding Mode Control that combines
multiple SMC algorithms with intelligent switching logic.

Mathematical Requirements:
- Individual controller gains must satisfy their respective stability conditions
- Switching thresholds must prevent chattering between controllers
- Hysteresis parameters must ensure stable mode transitions

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/config.py
:language: python
:linenos:
```



## Classes

### `HybridMode`

**Inherits from:** `Enum`

Available hybrid controller modes.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/config.py
:language: python
:pyobject: HybridMode
:linenos:
```



### `SwitchingCriterion`

**Inherits from:** `Enum`

Switching criteria for hybrid control.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/config.py
:language: python
:pyobject: SwitchingCriterion
:linenos:
```



### `HybridSMCConfig`

Type-safe configuration for Hybrid SMC controller.

Combines multiple SMC controllers with intelligent switching logic
for improved performance across different operating conditions.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/config.py
:language: python
:pyobject: HybridSMCConfig
:linenos:
```

#### Methods (17)

##### `__post_init__(self)`

Validate configuration after creation.

[View full source →](#method-hybridsmcconfig-__post_init__)

##### `_validate_gains(self)`

Validate sliding surface gains for PSO integration.

[View full source →](#method-hybridsmcconfig-_validate_gains)

##### `surface_gains(self)`

Surface parameters for sliding mode design [c1, λ1, c2, λ2].

[View full source →](#method-hybridsmcconfig-surface_gains)

##### `_validate_hybrid_mode(self)`

Validate hybrid mode and required controller configurations.

[View full source →](#method-hybridsmcconfig-_validate_hybrid_mode)

##### `_validate_switching_parameters(self)`

Validate switching logic parameters.

[View full source →](#method-hybridsmcconfig-_validate_switching_parameters)

##### `_validate_controller_configs(self)`

Validate individual controller configurations.

[View full source →](#method-hybridsmcconfig-_validate_controller_configs)

##### `_validate_performance_parameters(self)`

Validate performance monitoring parameters.

[View full source →](#method-hybridsmcconfig-_validate_performance_parameters)

##### `get_active_controllers(self)`

Get list of active controller types based on hybrid mode.

[View full source →](#method-hybridsmcconfig-get_active_controllers)

##### `get_controller_config(self, controller_type)`

Get configuration for specific controller type.

[View full source →](#method-hybridsmcconfig-get_controller_config)

##### `get_switching_thresholds_with_hysteresis(self)`

Get switching thresholds with hysteresis bands.

[View full source →](#method-hybridsmcconfig-get_switching_thresholds_with_hysteresis)

##### `is_switching_allowed(self, last_switch_time, current_time)`

Check if switching is allowed based on minimum switching time.

[View full source →](#method-hybridsmcconfig-is_switching_allowed)

##### `get_performance_metric_names(self)`

Get list of performance metric names.

[View full source →](#method-hybridsmcconfig-get_performance_metric_names)

##### `compute_weighted_performance(self, metrics)`

Compute weighted performance index.

[View full source →](#method-hybridsmcconfig-compute_weighted_performance)

##### `to_dict(self)`

Convert configuration to dictionary.

[View full source →](#method-hybridsmcconfig-to_dict)

##### `from_dict(cls, config_dict, dynamics_model)`

Create configuration from dictionary.

[View full source →](#method-hybridsmcconfig-from_dict)

##### `create_classical_adaptive_hybrid(cls, classical_gains, adaptive_gains, dt, max_force)`

Create Classical-Adaptive hybrid configuration.

[View full source →](#method-hybridsmcconfig-create_classical_adaptive_hybrid)

##### `create_adaptive_supertwisting_hybrid(cls, adaptive_gains, supertwisting_gains, dt, max_force)`

Create Adaptive-SuperTwisting hybrid configuration.

[View full source →](#method-hybridsmcconfig-create_adaptive_supertwisting_hybrid)



## Dependencies

This module imports:

- `from typing import List, Optional, Dict, Any, Union`
- `from dataclasses import dataclass, field`
- `from enum import Enum`
- `from ..classical.config import ClassicalSMCConfig`
- `from ..adaptive.config import AdaptiveSMCConfig`
- `from ..super_twisting.config import SuperTwistingSMCConfig`
