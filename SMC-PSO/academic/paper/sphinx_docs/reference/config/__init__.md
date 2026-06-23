# config.__init__

**Source:** `src\config\__init__.py`

## Module Overview

Configuration module for the DIP SMC PSO project.

## Complete Source Code

```{literalinclude} ../../../src/config/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .loader import load_config, InvalidConfigurationError, ConfigSchema`
- `from .schemas import PhysicsConfig, PhysicsUncertaintySchema, SimulationConfig, ControllersConfig, ControllerConfig, PermissiveControllerConfig, PSOConfig, PSOBounds, CostFunctionConfig, CostFunctionWeights, CombineWeights, VerificationConfig, SensorsConfig, HILConfig, FDIConfig, StabilityMonitoringConfig, LDRConfig, SaturationConfig, ConditioningConfig, DiagnosticsConfig, StrictModel, set_allow_unknown_config, redact_value`
- `from .logging import configure_provenance_logging, ProvenanceFilter`
- `from .schemas import config`
