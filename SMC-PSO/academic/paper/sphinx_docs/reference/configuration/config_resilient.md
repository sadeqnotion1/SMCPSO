# configuration.config_resilient

**Source:** `src\configuration\config_resilient.py`

## Module Overview

RESILIENT Configuration Management System - SPOF Elimination
This module eliminates the single config file SPOF by implementing:

1. Multiple configuration sources with automatic failover
2. Configuration redundancy and validation
3. Graceful degradation when config files are corrupted
4. Runtime configuration healing and recovery
5. Built-in default configurations for emergency operation

PRODUCTION SAFETY: System can operate even if config.yaml is deleted or corrupted.

## Complete Source Code

```{literalinclude} ../../../src/configuration/config_resilient.py
:language: python
:linenos:
```



## Classes

### `ConfigSource`

**Inherits from:** `Enum`

Configuration source types.

#### Source Code

```{literalinclude} ../../../src/configuration/config_resilient.py
:language: python
:pyobject: ConfigSource
:linenos:
```



### `ConfigState`

**Inherits from:** `Enum`

Configuration system state.

#### Source Code

```{literalinclude} ../../../src/configuration/config_resilient.py
:language: python
:pyobject: ConfigState
:linenos:
```



### `ConfigHealth`

Configuration health status.

#### Source Code

```{literalinclude} ../../../src/configuration/config_resilient.py
:language: python
:pyobject: ConfigHealth
:linenos:
```

#### Methods (1)

##### `update_source_status(self, source, success, error)`

Update status for a configuration source.

[View full source →](#method-confighealth-update_source_status)



### `ResilientConfigManager`

Production-safe configuration manager with SPOF elimination.

Features:
- Multiple configuration sources with automatic failover
- Built-in defaults for emergency operation
- Configuration validation and healing
- Runtime configuration updates
- Thread-safe operations

#### Source Code

```{literalinclude} ../../../src/configuration/config_resilient.py
:language: python
:pyobject: ResilientConfigManager
:linenos:
```

#### Methods (15)

##### `__init__(self, primary_config_path, backup_config_path)`

Initialize resilient configuration manager.

[View full source →](#method-resilientconfigmanager-__init__)

##### `get_config(self, key, default)`

Get configuration value with safe access.

[View full source →](#method-resilientconfigmanager-get_config)

##### `set_config(self, key, value, persist)`

Set configuration value at runtime.

[View full source →](#method-resilientconfigmanager-set_config)

##### `reload_configuration(self)`

Reload configuration from all sources.

[View full source →](#method-resilientconfigmanager-reload_configuration)

##### `get_health_status(self)`

Get configuration health status.

[View full source →](#method-resilientconfigmanager-get_health_status)

##### `validate_configuration(self)`

Validate current configuration and return any issues.

[View full source →](#method-resilientconfigmanager-validate_configuration)

##### `heal_configuration(self)`

Attempt to heal corrupted configuration.

[View full source →](#method-resilientconfigmanager-heal_configuration)

##### `create_config_backup(self)`

Create backup of current configuration.

[View full source →](#method-resilientconfigmanager-create_config_backup)

##### `_load_configuration(self)`

Load configuration from all available sources.

[View full source →](#method-resilientconfigmanager-_load_configuration)

##### `_load_from_file(self, file_path)`

Load configuration from YAML file.

[View full source →](#method-resilientconfigmanager-_load_from_file)

##### `_load_from_environment(self, _)`

Load configuration overrides from environment variables.

[View full source →](#method-resilientconfigmanager-_load_from_environment)

##### `_load_defaults(self, _)`

Load built-in default configuration.

[View full source →](#method-resilientconfigmanager-_load_defaults)

##### `_get_default_config(self)`

Get built-in default configuration (emergency fallback).

[View full source →](#method-resilientconfigmanager-_get_default_config)

##### `_merge_config(self, new_config)`

Merge new configuration with existing, preserving existing values.

[View full source →](#method-resilientconfigmanager-_merge_config)

##### `_save_to_backup(self)`

Save current configuration to backup file.

[View full source →](#method-resilientconfigmanager-_save_to_backup)



## Functions

### `get_config_manager()`

Get configuration manager (creates if not exists).

#### Source Code

```{literalinclude} ../../../src/configuration/config_resilient.py
:language: python
:pyobject: get_config_manager
:linenos:
```



### `set_config_manager(manager)`

Replace configuration manager (eliminates singleton dependency).

#### Source Code

```{literalinclude} ../../../src/configuration/config_resilient.py
:language: python
:pyobject: set_config_manager
:linenos:
```



### `get_config(key, default)`

Get configuration value using resilient manager.

#### Source Code

```{literalinclude} ../../../src/configuration/config_resilient.py
:language: python
:pyobject: get_config
:linenos:
```



### `set_config(key, value, persist)`

Set configuration value using resilient manager.

#### Source Code

```{literalinclude} ../../../src/configuration/config_resilient.py
:language: python
:pyobject: set_config
:linenos:
```



### `reload_config()`

Reload configuration from all sources.

#### Source Code

```{literalinclude} ../../../src/configuration/config_resilient.py
:language: python
:pyobject: reload_config
:linenos:
```



### `get_config_health()`

Get configuration system health.

#### Source Code

```{literalinclude} ../../../src/configuration/config_resilient.py
:language: python
:pyobject: get_config_health
:linenos:
```



## Dependencies

This module imports:

- `import os`
- `import yaml`
- `import json`
- `import copy`
- `import time`
- `import threading`
- `from pathlib import Path`
- `from typing import Dict, Any, List, Optional, Union, Callable`
- `from dataclasses import dataclass, field`
- `from enum import Enum`

*... and 1 more*
