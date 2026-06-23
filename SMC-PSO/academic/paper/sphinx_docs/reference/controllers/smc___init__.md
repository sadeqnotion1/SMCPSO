# controllers.smc.__init__

**Source:** `src\controllers\smc\__init__.py`

## Module Overview

Sliding Mode Controllers for the double inverted pendulum system.

This package provides both legacy monolithic controllers and new modular implementations:

Legacy Controllers (for backward compatibility):
- ClassicalSMC (from classic_smc.py)
- AdaptiveSMC (from adaptive_smc.py)
- SuperTwistingSMC (from sta_smc.py)
- HybridAdaptiveSTASMC (from hybrid_adaptive_sta_smc.py)

New Modular Controllers (recommended for new development):
- All controllers from algorithms package with focused, single-responsibility modules
- Improved maintainability, testing, and extensibility
- Type-safe configurations with mathematical validation

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .classic_smc import ClassicalSMC as LegacyClassicalSMC`
- `from .adaptive_smc import AdaptiveSMC as LegacyAdaptiveSMC`
- `from .sta_smc import SuperTwistingSMC as LegacySuperTwistingSMC`
- `from .hybrid_adaptive_sta_smc import HybridAdaptiveSTASMC`
- `from .algorithms import ClassicalSMC, ModularClassicalSMC, ClassicalSMCConfig, AdaptiveSMC, ModularAdaptiveSMC, AdaptiveSMCConfig, AdaptationLaw, ModifiedAdaptationLaw, UncertaintyEstimator, ParameterIdentifier, CombinedEstimator, SuperTwistingSMC, ModularSuperTwistingSMC, SuperTwistingSMCConfig, SuperTwistingAlgorithm, HybridSMC, ModularHybridSMC, HybridSMCConfig, HybridSwitchingLogic, SwitchingDecision, ControllerState, HybridMode, SwitchingCriterion`
- `from .core import SlidingSurface, LinearSlidingSurface, SwitchingFunction, EquivalentControl, validate_smc_gains, SMCGainValidator`
