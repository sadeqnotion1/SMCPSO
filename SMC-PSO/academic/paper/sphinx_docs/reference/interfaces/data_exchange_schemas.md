# interfaces.data_exchange.schemas

**Source:** `src\interfaces\data_exchange\schemas.py`

## Module Overview Schema

validation framework for data exchange

.


This module provides schema validation features including JSON Schema, custom data schemas, field validation,
and type checking for ensuring data integrity and consistency. ## Complete Source Code ```{literalinclude} ../../../src/interfaces/data_exchange/schemas.py
:language: python
:linenos:
```

---

## Classes

### `FieldType`

**Inherits from:** `Enum` Field type enumeration for schema validation.

#### Source Code ```

{literalinclude} ../../../src/interfaces/data_exchange/schemas.py
:language: python
:pyobject: FieldType
:linenos:
```

---

## `ValidationSeverity`

**Inherits from:** `Enum` Validation error severity levels.

### Source Code ```

{literalinclude} ../../../src/interfaces/data_exchange/schemas.py

:language: python
:pyobject: ValidationSeverity
:linenos:
```

### `ValidationError`

Validation error information.

#### Source Code ```

{literalinclude} ../../../src/interfaces/data_exchange/schemas.py
:language: python
:pyobject: ValidationError
:linenos:
```

### `FieldConstraint`

Field validation constraint.

#### Source Code ```

{literalinclude} ../../../src/interfaces/data_exchange/schemas.py

:language: python
:pyobject: FieldConstraint
:linenos:
```

### `FieldSchema`

Schema definition for a data field.

#### Source Code ```

{literalinclude} ../../../src/interfaces/data_exchange/schemas.py
:language: python
:pyobject: FieldSchema
:linenos:
``` #### Methods (8) ##### `add_constraint(self, name, validator, error_message, severity)` Add custom validation constraint. [View full source →](#method-fieldschema-add_constraint) ##### `validate_value(self, value, field_path)` Validate a value against this field schema. [View full source →](#method-fieldschema-validate_value) ##### `_validate_type(self, value, field_path)` Validate the type of a value. [View full source →](#method-fieldschema-_validate_type) ##### `_validate_constraints(self, value, field_path)` Validate value constraints. [View full source →](#method-fieldschema-_validate_constraints) ##### `_validate_custom_constraints(self, value, field_path)` Validate custom constraints. [View full source →](#method-fieldschema-_validate_custom_constraints) ##### `_is_valid_uuid(value)` Check if string is a valid UUID. [View full source →](#method-fieldschema-_is_valid_uuid) ##### `_is_valid_email(value)` Check if string is a valid email. [View full source →](#method-fieldschema-_is_valid_email) ##### `_is_valid_url(value)` Check if string is a valid URL. [View full source →](#method-fieldschema-_is_valid_url)

### `DataSchema`

Complete schema definition for data validation.

#### Source Code ```

{literalinclude} ../../../src/interfaces/data_exchange/schemas.py

:language: python
:pyobject: DataSchema
:linenos:
``` #### Methods (5) ##### `add_field(self, field_schema)` Add field schema to the data schema. [View full source →](#method-dataschema-add_field) ##### `validate(self, data)` Validate data against this schema. [View full source →](#method-dataschema-validate) ##### `is_valid(self, data)` Check if data is valid according to this schema. [View full source →](#method-dataschema-is_valid) ##### `get_field_names(self)` Get list of all field names. [View full source →](#method-dataschema-get_field_names) ##### `get_required_field_names(self)` Get list of required field names. [View full source →](#method-dataschema-get_required_field_names)

### `SchemaValidator`

Main schema validator with caching and performance optimization.

#### Source Code ```

{literalinclude} ../../../src/interfaces/data_exchange/schemas.py
:language: python
:pyobject: SchemaValidator
:linenos:
``` #### Methods (9) ##### `__init__(self)` [View full source →](#method-schemavalidator-__init__) ##### `register_schema(self, schema)` Register a schema for validation. [View full source →](#method-schemavalidator-register_schema) ##### `validate_data(self, data, schema_name, schema_version, use_cache)` Validate data against a registered schema. [View full source →](#method-schemavalidator-validate_data) ##### `is_data_valid(self, data, schema_name, schema_version)` Check if data is valid against a schema. [View full source →](#method-schemavalidator-is_data_valid) ##### `get_schema(self, schema_name, schema_version)` Get a registered schema. [View full source →](#method-schemavalidator-get_schema) ##### `list_schemas(self)` List all registered schemas. [View full source →](#method-schemavalidator-list_schemas) ##### `clear_cache(self)` Clear validation cache. [View full source →](#method-schemavalidator-clear_cache) ##### `_hash_data(self, data)` Generate hash for data caching. [View full source →](#method-schemavalidator-_hash_data) ##### `_cache_validation_result(self, cache_key, errors)` Cache validation result. [View full source →](#method-schemavalidator-_cache_validation_result)

### `JSONSchema`

JSON Schema integration for standards-compliant validation.

#### Source Code ```

{literalinclude} ../../../src/interfaces/data_exchange/schemas.py

:language: python
:pyobject: JSONSchema
:linenos:
``` #### Methods (3) ##### `__init__(self)` [View full source →](#method-jsonschema-__init__) ##### `add_schema(self, schema_id, schema_definition)` Add JSON Schema definition. [View full source →](#method-jsonschema-add_schema) ##### `validate(self, data, schema_id)` Validate data against JSON Schema. [View full source →](#method-jsonschema-validate)

### `MessageSchema`

Schema specifically for message validation.

#### Source Code ```

{literalinclude} ../../../src/interfaces/data_exchange/schemas.py
:language: python
:pyobject: MessageSchema
:linenos:
``` #### Methods (1) ##### `validate_message(self, message_data)` Validate complete message structure. [View full source →](#method-messageschema-validate_message)

---

## Functions

### `create_control_message_schema()`

Create schema for control messages.

#### Source Code ```

{literalinclude} ../../../src/interfaces/data_exchange/schemas.py

:language: python
:pyobject: create_control_message_schema
:linenos:
```

### `create_telemetry_message_schema()`

Create schema for telemetry messages.

#### Source Code ```

{literalinclude} ../../../src/interfaces/data_exchange/schemas.py
:language: python
:pyobject: create_telemetry_message_schema
:linenos:
```

---

## Dependencies This module imports: - `import re`

- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass, field`
- `from typing import Any, Dict, List, Optional, Union, Type, Callable, Set`
- `from enum import Enum`
- `import logging`
- `import time`
