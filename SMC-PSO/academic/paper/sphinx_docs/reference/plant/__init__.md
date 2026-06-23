# plant.__init__

**Source:** `src\plant\__init__.py`

## Module Overview Plant

Dynamics and Physical Models for the Double Inverted Pendulum System

. This package provides a modular architecture for DIP dynamics with three implementations: Modular Architecture:


- Simplified DIP: High-performance simplified dynamics
- Full DIP: High-fidelity complete dynamics
- Low-rank DIP: Reduced-order approximations
- Core components: Shared physics computation, validation, stability
- Configurations: Unified type-safe parameter management The modular architecture provides:
- Clear separation of concerns
- validation and error handling
- Numerical stability features
- Performance optimizations
- Type safety and documentation
- Unified configuration system with factory patterns ## Complete Source Code ```{literalinclude} ../../../src/plant/__init__.py
:language: python
:linenos:
```

---

## Dependencies This module imports: - `from .models.simplified import SimplifiedDIPConfig, SimplifiedPhysicsComputer, SimplifiedDIPDynamics`
- `from .models.full import FullDIPConfig, FullFidelityPhysicsComputer, FullDIPDynamics`
- `from .models.lowrank import LowRankDIPConfig, LowRankPhysicsComputer, LowRankDIPDynamics`
- `from .models.base import DynamicsModel, DynamicsResult, IntegrationMethod, BaseDynamicsModel, LinearDynamicsModel`
- `from .core import DIPPhysicsMatrices, SimplifiedDIPPhysicsMatrices, NumericalInstabilityError, AdaptiveRegularizer, MatrixInverter, NumericalStabilityMonitor, StateValidationError, DIPStateValidator, MinimalStateValidator`
- `from .configurations import BasePhysicsConfig, BaseDIPConfig, ConfigurationFactory, UnifiedConfiguration, DIPModelType, ConfigurationError, ConfigurationWarning, PhysicsParameterValidator, validate_physics_parameters`
