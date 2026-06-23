# controllers.__init__

**Source:** `src\controllers\__init__.py`

## Module Overview

Clean SMC Controllers Package

Provides unified access to 4 core SMC controllers optimized for research and PSO tuning:
- Classical SMC
- Adaptive SMC
- Super-Twisting SMC
- Hybrid Adaptive-STA SMC

Usage Examples:
    # PSO-optimized controller creation
    from controllers import create_smc_for_pso, SMCType
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains=[10, 8, 15, 12, 50, 5])

    # Direct controller instantiation
    from controllers import ClassicalSMC
    controller = ClassicalSMC(gains=[10, 8, 15, 12, 50, 5], max_force=100.0)

    # Clean factory usage
    from controllers import SMCFactory, SMCConfig
    config = SMCConfig(gains=[10, 8, 15, 12, 50, 5], max_force=100.0)
    controller = SMCFactory.create_controller(SMCType.CLASSICAL, config)

## Complete Source Code

```{literalinclude} ../../../src/controllers/__init__.py
:language: python
:linenos:
```



## Functions

### `create_all_smc_controllers(gains_dict, max_force, dt)`

Create all 4 SMC controllers at once for comparison studies.

Args:
    gains_dict: Dictionary mapping controller names to their gains
               e.g., {"classical": [10,8,15,12,50,5], "adaptive": [10,8,15,12,0.5]}
    max_force: Maximum control force
    dt: Control timestep

Returns:
    Dictionary of initialized SMC controllers

Example:
    gains = {
        "classical": [10, 8, 15, 12, 50, 5],
        "adaptive": [10, 8, 15, 12, 0.5],
        "sta": [25, 10, 15, 12, 20, 15],
        "hybrid": [15, 12, 18, 15]
    }
    controllers = create_all_smc_controllers(gains)

#### Source Code

```{literalinclude} ../../../src/controllers/__init__.py
:language: python
:pyobject: create_all_smc_controllers
:linenos:
```



### `get_all_gain_bounds()`

Get PSO gain bounds for all SMC controller types.

#### Source Code

```{literalinclude} ../../../src/controllers/__init__.py
:language: python
:pyobject: get_all_gain_bounds
:linenos:
```



## Dependencies

This module imports:

- `from .factory import SMCType, SMCConfig, SMCFactory, create_smc_for_pso, get_gain_bounds_for_pso, validate_smc_gains, SMC_GAIN_SPECS`
- `from .factory import create_controller_legacy`
