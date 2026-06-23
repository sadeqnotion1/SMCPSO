# controllers.factory.deprecation

**Source:** `src\controllers\factory\deprecation.py`

## Module Overview Controller

Factory Deprecation Warning System

. Provides systematic deprecation warnings for controller configuration changes,


parameter renames, and interface modifications to ensure smooth migration paths. ## Complete Source Code ```{literalinclude} ../../../src/controllers/factory/deprecation.py
:language: python
:linenos:
```

---

## Classes

### `DeprecationLevel`

**Inherits from:** `Enum` Levels of deprecation severity.

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/deprecation.py
:language: python
:pyobject: DeprecationLevel
:linenos:
```

---

## `DeprecationMapping`

Configuration for a deprecated parameter or feature.

### Source Code ```

{literalinclude} ../../../src/controllers/factory/deprecation.py

:language: python
:pyobject: DeprecationMapping
:linenos:
```

### `ControllerDeprecationWarner`

Systematic deprecation warning system for controller configurations. Tracks deprecated parameters, provides migration guidance, and ensures
backward compatibility during transition periods. #### Source Code ```{literalinclude} ../../../src/controllers/factory/deprecation.py
:language: python
:pyobject: ControllerDeprecationWarner
:linenos:
``` #### Methods (6) ##### `__init__(self)` [View full source →](#method-controllerdeprecationwarner-__init__) ##### `_initialize_deprecation_mappings(self)` Initialize deprecation mappings for all controller types. [View full source →](#method-controllerdeprecationwarner-_initialize_deprecation_mappings) ##### `check_deprecated_parameters(self, controller_type, config_params)` Check for deprecated parameters and issue appropriate warnings. [View full source →](#method-controllerdeprecationwarner-check_deprecated_parameters) ##### `_issue_deprecation_warning(self, controller_type, mapping, param_name, param_value)` Issue appropriate deprecation warning based on severity level. [View full source →](#method-controllerdeprecationwarner-_issue_deprecation_warning) ##### `get_migration_guide(self, controller_type)` Get migration guide for a controller type. [View full source →](#method-controllerdeprecationwarner-get_migration_guide) ##### `validate_configuration_compatibility(self, controller_type, config_params)` Validate configuration compatibility and return detailed issues. [View full source →](#method-controllerdeprecationwarner-validate_configuration_compatibility)

---

## Functions

### `check_deprecated_config(controller_type, config_params)`

Convenience function to check and migrate deprecated configuration parameters. Args: controller_type: Type of controller config_params: Configuration parameters Returns: Updated configuration with deprecated parameters migrated

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/deprecation.py

:language: python
:pyobject: check_deprecated_config
:linenos:
```

### `get_controller_migration_guide(controller_type)`

Get migration guide for a specific controller type. Args: controller_type: Type of controller Returns: List of migration guidance strings

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/deprecation.py
:language: python
:pyobject: get_controller_migration_guide
:linenos:
```

### `validate_config_compatibility(controller_type, config_params)`

Validate configuration compatibility for a controller type. Args: controller_type: Type of controller config_params: Configuration parameters to validate Returns: Dictionary of compatibility issues

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/deprecation.py

:language: python
:pyobject: validate_config_compatibility
:linenos:
```

---

## Dependencies This module imports: - `import warnings`
- `import logging`
- `from typing import Dict, Any, List, Optional, Union`
- `from dataclasses import dataclass`
- `from enum import Enum`
