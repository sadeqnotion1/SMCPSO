# controllers.smc.algorithms.hybrid.__init__

**Source:** `src\controllers\smc\algorithms\hybrid\__init__.py`

## Module Overview

Hybrid SMC Algorithm Package.

Modular implementation of Hybrid Sliding Mode Control that intelligently
switches between multiple SMC algorithms based on system conditions:

- Controller: Main orchestration with intelligent switching
- SwitchingLogic: Decision-making logic for controller selection
- Configuration: Type-safe parameter configuration for hybrid operation

This provides optimal performance by selecting the most appropriate SMC algorithm
for current operating conditions, with smooth transitions and performance monitoring.

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .controller import ModularHybridSMC, HybridSMC`
- `from .switching_logic import HybridSwitchingLogic, SwitchingDecision, ControllerState`
- `from .config import HybridSMCConfig, HybridMode, SwitchingCriterion`
