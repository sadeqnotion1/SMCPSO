# controllers.smc.algorithms.adaptive.__init__

**Source:** `src\controllers\smc\algorithms\adaptive\__init__.py`

## Module Overview

Adaptive SMC Algorithm Package.

Modular implementation of Adaptive Sliding Mode Control split into focused components:
- Controller: Main orchestration and adaptive control computation
- AdaptationLaw: Online gain adaptation algorithms
- ParameterEstimation: Uncertainty and parameter estimation
- Configuration: Type-safe parameter configuration

This replaces the monolithic 427-line adaptive SMC with focused modules.

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .controller import ModularAdaptiveSMC, AdaptiveSMC`
- `from .adaptation_law import AdaptationLaw, ModifiedAdaptationLaw`
- `from .parameter_estimation import UncertaintyEstimator, ParameterIdentifier, CombinedEstimator`
- `from .config import AdaptiveSMCConfig`
