# utils.config_compatibility

**Source:** `src\utils\config_compatibility.py`

## Module Overview

Configuration compatibility utilities.

This module provides compatibility between dictionary-based and object-based
configuration access patterns, enabling integration between different
configuration systems used throughout the project.

## Complete Source Code

```{literalinclude} ../../../src/utils/config_compatibility.py
:language: python
:linenos:
```



## Classes

### `AttributeDictionary`

Dictionary-like object that supports both dictionary and attribute access.

This class wraps dictionaries to provide attribute access (obj.key) while
maintaining dictionary access (obj['key']) for maximum compatibility.

#### Source Code

```{literalinclude} ../../../src/utils/config_compatibility.py
:language: python
:pyobject: AttributeDictionary
:linenos:
```

#### Methods (12)

##### `__init__(self, data)`

Initialize with dictionary data.

[View full source →](#method-attributedictionary-__init__)

##### `__getattr__(self, name)`

Get attribute using dot notation.

[View full source →](#method-attributedictionary-__getattr__)

##### `__getitem__(self, key)`

Get item using dictionary notation.

[View full source →](#method-attributedictionary-__getitem__)

##### `__setattr__(self, name, value)`

Set attribute.

[View full source →](#method-attributedictionary-__setattr__)

##### `__setitem__(self, key, value)`

Set item using dictionary notation.

[View full source →](#method-attributedictionary-__setitem__)

##### `__contains__(self, key)`

Check if key exists.

[View full source →](#method-attributedictionary-__contains__)

##### `get(self, key, default)`

Get value with default.

[View full source →](#method-attributedictionary-get)

##### `keys(self)`

Get dictionary keys.

[View full source →](#method-attributedictionary-keys)

##### `values(self)`

Get dictionary values.

[View full source →](#method-attributedictionary-values)

##### `items(self)`

Get dictionary items.

[View full source →](#method-attributedictionary-items)

##### `to_dict(self)`

Convert back to plain dictionary.

[View full source →](#method-attributedictionary-to_dict)

##### `__repr__(self)`

String representation.

[View full source →](#method-attributedictionary-__repr__)



### `ConfigCompatibilityMixin`

Mixin class for components that need configuration compatibility.

This mixin provides methods to handle both dictionary and object-based
configurations seamlessly.

#### Source Code

```{literalinclude} ../../../src/utils/config_compatibility.py
:language: python
:pyobject: ConfigCompatibilityMixin
:linenos:
```

#### Methods (2)

##### `_ensure_config_compatibility(self, config)`

Ensure configuration has attribute access.

[View full source →](#method-configcompatibilitymixin-_ensure_config_compatibility)

##### `_ensure_config_dict(self, config)`

Ensure configuration is a dictionary.

[View full source →](#method-configcompatibilitymixin-_ensure_config_dict)



## Functions

### `ensure_attribute_access(config)`

Ensure configuration supports attribute access.

This function takes either a dictionary or an object and ensures that
the result supports attribute access (obj.key) for compatibility with
code that expects configuration objects.

Args:
    config: Configuration as dictionary or object

Returns:
    Configuration object supporting attribute access

#### Source Code

```{literalinclude} ../../../src/utils/config_compatibility.py
:language: python
:pyobject: ensure_attribute_access
:linenos:
```



### `ensure_dict_access(config)`

Ensure configuration is a dictionary.

This function takes either a dictionary or an object and ensures that
the result is a plain dictionary for compatibility with code that
expects dictionary access.

Args:
    config: Configuration as dictionary or object

Returns:
    Configuration as dictionary

#### Source Code

```{literalinclude} ../../../src/utils/config_compatibility.py
:language: python
:pyobject: ensure_dict_access
:linenos:
```



### `wrap_physics_config(physics_config)`

Wrap physics configuration for compatibility with plant models.

This function specifically handles physics configurations that need
to work with both the configuration loading system and the plant
model implementations. It also provides parameter name mapping
and default values for missing parameters.

Args:
    physics_config: Physics configuration from config loading

Returns:
    Configuration compatible with plant model requirements

#### Source Code

```{literalinclude} ../../../src/utils/config_compatibility.py
:language: python
:pyobject: wrap_physics_config
:linenos:
```



### `validate_physics_config(config)`

Validate that physics configuration has required parameters.

Args:
    config: Configuration to validate

Returns:
    True if configuration has all required physics parameters

#### Source Code

```{literalinclude} ../../../src/utils/config_compatibility.py
:language: python
:pyobject: validate_physics_config
:linenos:
```



### `create_minimal_physics_config()`

Create a minimal physics configuration with default values.

Returns:
    Minimal configuration with default physics parameters

#### Source Code

```{literalinclude} ../../../src/utils/config_compatibility.py
:language: python
:pyobject: create_minimal_physics_config
:linenos:
```



## Dependencies

This module imports:

- `from typing import Dict, Any, Union, Optional`
- `import warnings`
