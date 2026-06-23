# controllers.smc.algorithms.hybrid.switching_logic

**Source:** `src\controllers\smc\algorithms\hybrid\switching_logic.py`

## Module Overview Hybrid

Switching Logic for Multi-Controller SMC

. Implements intelligent switching between multiple SMC controllers based on:


- System performance metrics
- Operating conditions
- Predictive analysis
- Learning algorithms Mathematical Background:
- Switching functions prevent controller chattering
- Hysteresis bands ensure stable transitions
- Performance indices guide optimal controller selection ## Advanced Mathematical Theory ### Multi-Mode Controller Selection **Performance index for mode $m$:** ```{math}
J_m(t) = w_1 \text{ITAE}_m + w_2 \text{CHAT}_m + w_3 \text{ROBUST}_m
``` **Optimal mode:** ```{math}
m^*(t) = \arg\min_m J_m(t)
``` ### Hysteresis Switching **Switching rule with hysteresis:** ```{math}

\text{Switch from } m_1 \to m_2 \text{ only if } J_{m_2} < (1 - h) J_{m_1}
``` Where $h \in (0, 1)$ is hysteresis band (typically 0.1-0.2). **Prevents:** Rapid mode oscillation (chattering in mode space). ### Dwell Time Constraint **Minimum time in each mode:** ```{math}
t_{switch}^{k+1} - t_{switch}^k \geq T_{dwell}
``` **Ensures:** Stability during transients. ### Predictive Switching **Future performance estimate:** ```{math}

\hat{J}_m(t + \tau) = J_m(t) + \tau \dot{J}_m(t)
``` Switch based on predicted performance. ### Mode Transition Stability **Common Lyapunov function:** $V(\vec{x})$ decreases across all modes: ```{math}
\dot{V}_m(\vec{x}) < 0, \quad \forall m \in \mathcal{M}
``` **Guarantees:** Stability during arbitrary switching. ### Performance Metrics **Tracking error:** ```{math}

\text{ITAE}_m = \int_0^t \tau |e_m(\tau)| d\tau
``` **Chattering:** ```{math}
\text{CHAT}_m = \int_0^t |\dot{u}_m(\tau)| d\tau
``` **Robustness:** ```{math}

\text{ROBUST}_m = K_m - |\Delta|_{max}
``` ## Architecture Diagram ```{mermaid}
graph TD A[Performance Metrics] --> B[Compute J_adaptive] A --> C[Compute J_STA] B --> D{J_adaptive < _1-h_ J_STA?} C --> D D -->|Yes| E[Select Adaptive Mode] D -->|No| F{J_STA < _1-h_ J_adaptive?} F -->|Yes| G[Select STA Mode] F -->|No| H[Keep Current Mode] E --> I[Controller Selection] G --> I H --> I style D fill:#ff9 style I fill:#9f9
``` ## Usage Examples ### Example 1: Basic Initialization ```python

from src.controllers.smc.algorithms.hybrid import * # Initialize with configuration
config = {'parameter': 'value'}
instance = Component(config)
```

### Example 2: Performance Tuning

```python
## Adjust parameters for better performance
optimized_params = tune_parameters(instance, target_performance)
```

### Example 3: Integration with Controller

```python
## Use in complete control loop
controller = create_controller(ctrl_type, config)
result = simulate(controller, duration=5.0)
```

### Example 4: Edge Case Handling

```python
try:
    output = instance.compute(state)
except ValueError as e:
    handle_edge_case(e)
```

### Example 5: Performance Analysis

```python
## Analyze metrics
metrics = compute_metrics(result)
print(f"ITAE: {metrics.itae:.3f}")
``` ## Complete Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/switching_logic.py
:language: python
:linenos:
```

## Classes

### `ControllerState`

**Inherits from:** `Enum` Current active controller state.

#### Source Code ```

{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/switching_logic.py

:language: python
:pyobject: ControllerState
:linenos:
```

### `SwitchingDecision`

Represents a switching decision with reasoning.

#### Source Code ```

{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/switching_logic.py
:language: python
:pyobject: SwitchingDecision
:linenos:
``` #### Methods (1) ##### `__init__(self, target_controller, reason, confidence, metrics)` [View full source →](#method-switchingdecision-__init__)

### `HybridSwitchingLogic`

Intelligent switching logic for hybrid SMC controllers. Manages controller selection based on system performance,

operating conditions, and learned preferences. #### Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/switching_logic.py
:language: python
:pyobject: HybridSwitchingLogic
:linenos:
``` #### Methods (16) ##### `__init__(self, config)` Initialize hybrid switching logic. [View full source →](#method-hybridswitchinglogic-__init__) ##### `evaluate_switching(self, system_state, control_results, current_time)` Evaluate whether to switch controllers. [View full source →](#method-hybridswitchinglogic-evaluate_switching) ##### `execute_switch(self, decision, current_time)` Execute a switching decision. [View full source →](#method-hybridswitchinglogic-execute_switch) ##### `get_current_controller(self)` Get name of currently active controller. [View full source →](#method-hybridswitchinglogic-get_current_controller) ##### `_update_performance_metrics(self, control_results, system_state)` Update performance metrics for all controllers. [View full source →](#method-hybridswitchinglogic-_update_performance_metrics) ##### `_evaluate_surface_magnitude_switching(self, control_results)` Evaluate switching based on sliding surface magnitude. [View full source →](#method-hybridswitchinglogic-_evaluate_surface_magnitude_switching) ##### `_evaluate_control_effort_switching(self, control_results)` Evaluate switching based on control effort. [View full source →](#method-hybridswitchinglogic-_evaluate_control_effort_switching) ##### `_evaluate_tracking_error_switching(self, system_state)` Evaluate switching based on tracking error. [View full source →](#method-hybridswitchinglogic-_evaluate_tracking_error_switching) ##### `_evaluate_adaptation_rate_switching(self, control_results)` Evaluate switching based on adaptation rate (for adaptive controllers). [View full source →](#method-hybridswitchinglogic-_evaluate_adaptation_rate_switching) ##### `_evaluate_performance_index_switching(self, control_results)` Evaluate switching based on performance index. [View full source →](#method-hybridswitchinglogic-_evaluate_performance_index_switching) ##### `_evaluate_time_based_switching(self, current_time)` Evaluate switching based on time (round-robin or scheduled switching). [View full source →](#method-hybridswitchinglogic-_evaluate_time_based_switching) ##### `_check_hysteresis_condition(self, decision)` Check if switching decision passes hysteresis condition. [View full source →](#method-hybridswitchinglogic-_check_hysteresis_condition) ##### `_apply_predictive_analysis(self, decision, system_state)` Apply predictive analysis to switching decision. [View full source →](#method-hybridswitchinglogic-_apply_predictive_analysis) ##### `_update_learned_thresholds(self, decision, control_results)` Update learned switching thresholds based on decision outcomes. [View full source →](#method-hybridswitchinglogic-_update_learned_thresholds) ##### `get_switching_analysis(self)` Get analysis of switching behavior. [View full source →](#method-hybridswitchinglogic-get_switching_analysis) ##### `_compute_switching_statistics(self)` Compute statistics about switching behavior. [View full source →](#method-hybridswitchinglogic-_compute_switching_statistics)

## Dependencies This module imports: - `from typing import Dict, List, Optional, Any, Tuple`
- `import numpy as np`
- `from collections import deque`
- `from enum import Enum`
- `from .config import HybridSMCConfig, SwitchingCriterion`
