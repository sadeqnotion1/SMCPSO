# plant.configurations.unified_config

**Source:** `src\plant\configurations\unified_config.py`

## Module Overview Unified

Configuration System for DIP Models

. Provides a centralized configuration management system that supports


all DIP model types (simplified, full, low-rank) with factory patterns
and automatic configuration selection. ## Complete Source Code ```{literalinclude} ../../../src/plant/configurations/unified_config.py
:language: python
:linenos:
```

---

## Classes

### `DIPModelType`

**Inherits from:** `Enum` Available DIP model types.

#### Source Code ```

{literalinclude} ../../../src/plant/configurations/unified_config.py
:language: python
:pyobject: DIPModelType
:linenos:
```

---

## `ConfigurationFactory`

Factory for creating DIP configurations. Provides centralized creation and management of configurations

for different DIP model types with validation and consistency checking. #### Source Code ```{literalinclude} ../../../src/plant/configurations/unified_config.py
:language: python
:pyobject: ConfigurationFactory
:linenos:
``` #### Methods (10) ##### `register_config(cls, model_type, config_class)` Register a configuration class for a model type. [View full source →](#method-configurationfactory-register_config) ##### `create_config(cls, model_type, config_dict)` Create a configuration for the specified model type. [View full source →](#method-configurationfactory-create_config) ##### `create_default_config(cls, model_type)` Create default configuration for the specified model type. [View full source →](#method-configurationfactory-create_default_config) ##### `create_preset_config(cls, model_type, preset_name)` Create a preset configuration. [View full source →](#method-configurationfactory-create_preset_config) ##### `get_available_presets(cls, model_type)` Get list of available preset names for a model type. [View full source →](#method-configurationfactory-get_available_presets) ##### `compare_configurations(cls, config1, config2)` Compare two configurations and return differences. [View full source →](#method-configurationfactory-compare_configurations) ##### `validate_configuration(cls, config)` validation of a configuration. [View full source →](#method-configurationfactory-validate_configuration) ##### `_lazy_import_config(cls, model_type)` Lazy import configuration classes. [View full source →](#method-configurationfactory-_lazy_import_config) ##### `_import_controller_config(cls)` Import controller configuration class. [View full source →](#method-configurationfactory-_import_controller_config) ##### `_get_preset_configs(cls)` Get preset configuration dictionaries. [View full source →](#method-configurationfactory-_get_preset_configs)

---

### `UnifiedConfiguration`

Unified configuration management for all DIP models. Provides a single interface for configuration management across
different model types with automatic model selection and validation. #### Source Code ```{literalinclude} ../../../src/plant/configurations/unified_config.py
:language: python
:pyobject: UnifiedConfiguration
:linenos:
``` #### Methods (7) ##### `__init__(self, model_type, config)` Initialize unified configuration. [View full source →](#method-unifiedconfiguration-__init__) ##### `validate(self)` Validate the current configuration. [View full source →](#method-unifiedconfiguration-validate) ##### `update(self)` Update configuration parameters. [View full source →](#method-unifiedconfiguration-update) ##### `compare_with(self, other)` Compare with another configuration. [View full source →](#method-unifiedconfiguration-compare_with) ##### `to_dict(self)` Convert to dictionary. [View full source →](#method-unifiedconfiguration-to_dict) ##### `from_dict(cls, config_dict)` Create from dictionary. [View full source →](#method-unifiedconfiguration-from_dict) ##### `get_system_info(self)` Get system information. [View full source →](#method-unifiedconfiguration-get_system_info)

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from typing import Dict, Any, Union, Optional, Type`
- `from enum import Enum`
- `import warnings`
- `from .base_config import BaseDIPConfig, ConfigurationError, ConfigurationWarning`
