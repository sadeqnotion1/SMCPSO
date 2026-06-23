# controllers.factory.core.validation

**Source:** `src\controllers\factory\core\validation.py`

## Module Overview Validation

Framework for Controller Factory Provides enterprise-grade validation for controller gains, configurations, and parameters


with detailed error reporting and recovery mechanisms. ## Complete Source Code ```{literalinclude} ../../../src/controllers/factory/core/validation.py
:language: python
:linenos:
```

---

## Classes

### `ValidationResult`

Container for validation results with detailed feedback.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/validation.py
:language: python
:pyobject: ValidationResult
:linenos:
``` #### Methods (7) ##### `__init__(self, valid)` [View full source →](#method-validationresult-__init__) ##### `add_error(self, message)` Add an error message and mark result as invalid. [View full source →](#method-validationresult-add_error) ##### `add_warning(self, message)` Add a warning message. [View full source →](#method-validationresult-add_warning) ##### `add_info(self, message)` Add an informational message. [View full source →](#method-validationresult-add_info) ##### `has_issues(self)` Check if there are any errors or warnings. [View full source →](#method-validationresult-has_issues) ##### `get_summary(self)` Get a summary of validation results. [View full source →](#method-validationresult-get_summary) ##### `__str__(self)` String representation of validation results. [View full source →](#method-validationresult-__str__)

---

## Functions

### `validate_controller_gains(gains, controller_type, check_bounds, check_stability)`

Validate controller gains with checks. Args: gains: Controller gains to validate controller_type: Type of controller check_bounds: Perform bounds checking check_stability: Perform stability analysis Returns: Detailed validation results

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/validation.py

:language: python
:pyobject: validate_controller_gains
:linenos:
```

### `validate_configuration(config, controller_type, check_completeness)`

Validate controller configuration object. Args: config: Configuration object to validate controller_type: Type of controller check_completeness: Check for all required parameters Returns: Detailed validation results

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/validation.py
:language: python
:pyobject: validate_configuration
:linenos:
```

### `_validate_classical_smc_gains(gains, result, check_stability)`

Validate Classical SMC specific gain constraints.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/validation.py

:language: python
:pyobject: _validate_classical_smc_gains
:linenos:
```

### `_validate_adaptive_smc_gains(gains, result, check_stability)`

Validate Adaptive SMC specific gain constraints.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/validation.py
:language: python
:pyobject: _validate_adaptive_smc_gains
:linenos:
```

### `_validate_sta_smc_gains(gains, result, check_stability)`

Validate Super-Twisting SMC specific gain constraints.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/validation.py

:language: python
:pyobject: _validate_sta_smc_gains
:linenos:
```

### `_validate_hybrid_smc_gains(gains, result, check_stability)`

Validate Hybrid SMC specific gain constraints.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/validation.py
:language: python
:pyobject: _validate_hybrid_smc_gains
:linenos:
```

### `validate_state_vector(state)`

Validate system state vector.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/validation.py

:language: python
:pyobject: validate_state_vector
:linenos:
```

### `validate_control_output(control, max_force)`

Validate control output value.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/validation.py
:language: python
:pyobject: validate_control_output
:linenos:
```

---

## Dependencies This module imports: - `import logging`

- `from typing import Dict, Any, List, Optional, Union`
- `import numpy as np`
- `from numpy.typing import NDArray`
- `from .protocols import GainsArray, ConfigDict`
- `from .registry import get_controller_info, CONTROLLER_REGISTRY`
