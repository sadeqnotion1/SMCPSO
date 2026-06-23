# optimization.validation.pso_bounds_validator

**Source:** `src\optimization\validation\pso_bounds_validator.py`

## Module Overview PSO

Bounds Validation and Optimization Module

. This module provides validation and optimization of PSO parameter bounds


for control system optimization. It ensures bounds are appropriate for each controller
type and provides intelligent bounds adjustment based on system characteristics. Features:
- Controller-specific bounds validation
- Automatic bounds adjustment for stability
- Theoretical bounds derivation from system parameters
- Bounds optimization for convergence
- Statistical validation of bounds effectiveness References:
- Franklin, G.F., et al. "Feedback Control of Dynamic Systems"
- Utkin, V. "Sliding Modes in Control and Optimization" ## Complete Source Code ```{literalinclude} ../../../src/optimization/validation/pso_bounds_validator.py
:language: python
:linenos:
```

---

## Classes

### `BoundsValidationResult`

Result of bounds validation analysis.

#### Source Code ```

{literalinclude} ../../../src/optimization/validation/pso_bounds_validator.py
:language: python
:pyobject: BoundsValidationResult
:linenos:
```

---

## `PSOBoundsValidator`

Advanced PSO bounds validator for control system optimization.

This class provides validation and optimization of PSO parameter bounds to ensure effective controller tuning.

### Source Code

```{literalinclude} ../../../src/optimization/validation/pso_bounds_validator.py
:language: python
:pyobject: PSOBoundsValidator
:linenos:
```

#### Methods (11)

##### `__init__(self, config)`

[View full source →](#method-psoboundsvalidator-__init__)

##### `validate_bounds(self, controller_type, bounds_min, bounds_max)`

Validation of PSO bounds for a specific controller.

[View full source →](#method-psoboundsvalidator-validate_bounds)

##### `_classical_smc_constraints(self, bounds_min, bounds_max)`

Stability constraints for classical SMC.

[View full source →](#method-psoboundsvalidator-_classical_smc_constraints)

##### `_sta_smc_constraints(self, bounds_min, bounds_max)`

Stability constraints for super-twisting SMC.

[View full source →](#method-psoboundsvalidator-_sta_smc_constraints)

##### `_adaptive_smc_constraints(self, bounds_min, bounds_max)`

Stability constraints for adaptive SMC.

[View full source →](#method-psoboundsvalidator-_adaptive_smc_constraints)

##### `_hybrid_constraints(self, bounds_min, bounds_max)`

Stability constraints for hybrid adaptive-STA SMC.

[View full source →](#method-psoboundsvalidator-_hybrid_constraints)

##### `_analyze_stability_constraints(self, controller_type, bounds_min, bounds_max)`

Analyze stability constraints for given bounds.

[View full source →](#method-psoboundsvalidator-_analyze_stability_constraints)

##### `_estimate_convergence_difficulty(self, bounds_min, bounds_max)`

Estimate convergence difficulty based on bounds width.

[View full source →](#method-psoboundsvalidator-_estimate_convergence_difficulty)

##### `_generate_improved_bounds(self, controller_type)`

Generate improved bounds based on theoretical analysis.

[View full source →](#method-psoboundsvalidator-_generate_improved_bounds)

##### `optimize_bounds_for_convergence(self, controller_type, initial_bounds, target_convergence_time)`

Optimize bounds to achieve target convergence time.

[View full source →](#method-psoboundsvalidator-optimize_bounds_for_convergence)

##### `generate_bounds_report(self, controller_type)`

Generate a bounds analysis report.

[View full source →](#method-psoboundsvalidator-generate_bounds_report)

---

## Functions

### `validate_pso_configuration(config)`

Validate complete PSO configuration for all controllers. Parameters
----------
config : ConfigSchema Complete system configuration Returns
-------
BoundsValidationResult Aggregated validation results for all controllers #### Source Code ```{literalinclude} ../../../src/optimization/validation/pso_bounds_validator.py
:language: python
:pyobject: validate_pso_configuration
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`

- `import logging`
- `import numpy as np`
- `from typing import Any, Dict, List, Optional, Tuple, Union`
- `from dataclasses import dataclass`
- `import warnings`
- `from src.config import ConfigSchema`
- `from src.utils.numerical_stability import EPSILON_DIV`
