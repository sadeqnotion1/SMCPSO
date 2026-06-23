# controllers.factory.core.registry

**Source:** `src\controllers\factory\core\registry.py`

## Module Overview Controller

Registry Management - Centralized Controller Metadata Manages the central registry of available controllers with metadata,


validation rules, and type-safe access patterns. ## Complete Source Code ```{literalinclude} ../../../src/controllers/factory/core/registry.py
:language: python
:linenos:
```

---

## Functions

### `get_controller_info(controller_type)`

Get controller information from registry with validation. Args: controller_type: Canonical controller type name Returns: Controller registry information Raises: ValueError: If controller type is not recognized TypeError: If controller_type is not a string

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/registry.py
:language: python
:pyobject: get_controller_info
:linenos:
```

---

## `canonicalize_controller_type(name)`

Normalize and alias controller type names. Args: name: Controller type name to normalize Returns: Canonical controller type name Raises: ValueError: If name is not a string or is empty

### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/registry.py

:language: python
:pyobject: canonicalize_controller_type
:linenos:
```

### `list_available_controllers()`

Get list of available controller types. Returns: Sorted list of controller type names

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/registry.py
:language: python
:pyobject: list_available_controllers
:linenos:
```

### `get_controllers_by_category(category)`

Get controllers by category. Args: category: Controller category ('classical', 'adaptive', 'advanced', 'hybrid', 'predictive') Returns: List of controller names in the category

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/registry.py

:language: python
:pyobject: get_controllers_by_category
:linenos:
```

### `get_controllers_by_complexity(complexity)`

Get controllers by complexity level. Args: complexity: Complexity level ('low', 'medium', 'high', 'very_high') Returns: List of controller names with the specified complexity

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/registry.py
:language: python
:pyobject: get_controllers_by_complexity
:linenos:
```

### `get_default_gains(controller_type)`

Get default gains for a controller type. Args: controller_type: Type of controller Returns: Copy of default gains list Raises: ValueError: If controller_type is not recognized

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/registry.py

:language: python
:pyobject: get_default_gains
:linenos:
```

### `get_gain_bounds(controller_type)`

Get gain bounds for a controller type. Args: controller_type: Type of controller Returns: List of (lower, upper) bound tuples Raises: ValueError: If controller_type is not recognized

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/registry.py
:language: python
:pyobject: get_gain_bounds
:linenos:
```

### `validate_controller_type(controller_type)`

Check if a controller type is valid. Args: controller_type: Controller type to validate Returns: True if valid, False otherwise

#### Source Code ```

{literalinclude} ../../../src/controllers/factory/core/registry.py

:language: python
:pyobject: validate_controller_type
:linenos:
```

---

## Dependencies This module imports: - `from typing import Dict, Any, List, Optional`
- `import logging`
