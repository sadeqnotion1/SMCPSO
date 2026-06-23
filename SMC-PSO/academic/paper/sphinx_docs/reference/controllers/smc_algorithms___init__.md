# controllers.smc.algorithms.__init__

**Source:** `src\controllers\smc\algorithms\__init__.py`

## Module Overview SMC Algorithms Package

. collection of Sliding Mode Control algorithms implemented


with modular architecture for clarity and best practices: - Classical SMC: Traditional sliding mode control with boundary layer
- Adaptive SMC: Online gain adaptation for unknown uncertainties
- Super-Twisting SMC: Second-order sliding mode for finite-time convergence
- Hybrid SMC: Intelligent switching between multiple SMC algorithms Each algorithm is split into focused components following single-responsibility principle. ## Complete Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/__init__.py
:language: python
:linenos:
```

---

## Dependencies This module imports: - `from .classical import ClassicalSMC, ModularClassicalSMC, ClassicalSMCConfig`
- `from .adaptive import AdaptiveSMC, ModularAdaptiveSMC, AdaptiveSMCConfig, AdaptationLaw, ModifiedAdaptationLaw, UncertaintyEstimator, ParameterIdentifier, CombinedEstimator`
- `from .super_twisting import SuperTwistingSMC, ModularSuperTwistingSMC, SuperTwistingSMCConfig, SuperTwistingAlgorithm`
- `from .hybrid import HybridSMC, ModularHybridSMC, HybridSMCConfig, HybridSwitchingLogic, SwitchingDecision, ControllerState, HybridMode, SwitchingCriterion`
