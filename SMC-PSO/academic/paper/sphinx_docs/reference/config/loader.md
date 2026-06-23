# config.loader

**Source:** `src\config\loader.py`

## Module Overview

Configuration loading and validation logic.

## Complete Source Code

```{literalinclude} ../../../src/config/loader.py
:language: python
:linenos:
```



## Classes

### `InvalidConfigurationError`

**Inherits from:** `Exception`

Raised when configuration validation fails with aggregated error messages.

#### Source Code

```{literalinclude} ../../../src/config/loader.py
:language: python
:pyobject: InvalidConfigurationError
:linenos:
```



### `FileSettingsSource`

**Inherits from:** `PydanticBaseSettingsSource`

Custom settings source for loading from YAML or JSON files.

#### Source Code

```{literalinclude} ../../../src/config/loader.py
:language: python
:pyobject: FileSettingsSource
:linenos:
```

#### Methods (4)

##### `__init__(self, settings_cls, file_path)`

[View full source →](#method-filesettingssource-__init__)

##### `_read_file(self, file_path)`

Read configuration from YAML or JSON file.

[View full source →](#method-filesettingssource-_read_file)

##### `get_field_value(self, field, field_name)`

Return (value, field_name, found) for a single field. We use __call__ to load all.

[View full source →](#method-filesettingssource-get_field_value)

##### `__call__(self)`

Return mapping of settings from file source.

[View full source →](#method-filesettingssource-__call__)



### `ConfigSchema`

**Inherits from:** `BaseSettings`

#### Source Code

```{literalinclude} ../../../src/config/loader.py
:language: python
:pyobject: ConfigSchema
:linenos:
```

#### Methods (1)

##### `settings_customise_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings)`

Precedence (highest to lowest): ENV > .env > FILE > defaults

[View full source →](#method-configschema-settings_customise_sources)



## Functions

### `load_config(path)`

Load, parse, and validate configuration with precedence:
  1) Environment variables (C04__ prefix)
  2) .env file (if present)
  3) YAML/JSON file at `path` (if present)
  4) Model defaults

Parameters
----------
path : str | Path
    Path to YAML or JSON configuration file (optional).
allow_unknown : bool
    If True, unknown keys in controller configs will be accepted and collected.

Raises
------
InvalidConfigurationError
    When validation fails. Aggregates error messages with dot-paths.

#### Source Code

```{literalinclude} ../../../src/config/loader.py
:language: python
:pyobject: load_config
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import json`
- `import logging`
- `import os`
- `from pathlib import Path`
- `from typing import Any, Dict, List, Tuple, Type`
- `import yaml`
- `from pydantic.fields import FieldInfo`
- `from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict`
- `from dotenv import load_dotenv`

*... and 2 more*
