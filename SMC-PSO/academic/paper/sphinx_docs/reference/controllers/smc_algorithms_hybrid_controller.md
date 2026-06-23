# controllers.smc.algorithms.hybrid.controller

**Source:** `src\controllers\smc\algorithms\hybrid\controller.py`

## Module Overview Modular Hybrid SMC Controller

. Implements Hybrid Sliding Mode Control that intelligently switches between


multiple SMC algorithms based on system conditions and performance metrics. Orchestrates:
- Multiple SMC controllers (Classical, Adaptive, Super-Twisting)
- Intelligent switching logic
- Smooth control transitions
- Performance monitoring and learning ## Advanced Mathematical Theory ### Hybrid Adaptive-STA Framework **Unified control law:** ```{math}
u = \begin{cases}
u_{adaptive}, & \text{mode } m = 1 \\
u_{STA}, & \text{mode } m = 2
\end{cases}
``` **Smooth blending:** ```{math}
u = \lambda(t) u_{adaptive} + (1 - \lambda(t)) u_{STA}
``` Where $\lambda \in [0, 1]$ is blend factor. ### Mode Selection Strategy **Adaptive mode** when:

- Uncertainty high
- Need online tuning
- Slow dynamics acceptable **STA mode** when:
- Uncertainty bounded and known
- Fast convergence required
- Chattering critical ### Unified Adaptation Law **Shared gain adaptation:** ```{math}
\dot{K}_{shared} = \gamma |s| - \sigma K_{shared}
``` **Mode-specific scaling:** ```{math}
\begin{align}
K_{adaptive} &= K_{shared} \\
K_{STA,1} &= \beta_1 K_{shared} \\
K_{STA,2} &= \beta_2 K_{shared}
\end{align}
``` ### Best-of-Both-Worlds Performance **Combines:**

1. **Adaptive:** Online uncertainty handling
2. **STA:** Finite-time convergence, low chattering **Achieves:**
- Robustness to unknown disturbances
- Fast transient response
- Minimal steady-state chattering ### Stability Analysis **Switched Lyapunov function:** ```{math}
V_{hybrid} = \begin{cases}
V_{adaptive}, & m = 1 \\
V_{STA}, & m = 2
\end{cases}
``` **Stability condition:** ```{math}
V_{hybrid}(t_k^+) \leq V_{hybrid}(t_k^-), \quad \forall \text{ switch times } t_k
``` Non-increasing Lyapunov function at switches ensures stability. ## Architecture Diagram ```{mermaid}

graph TD A[State x] --> B[Sliding Surface s] B --> C[Adaptive Controller] B --> D[STA Controller] C --> E[u_adaptive] D --> F[u_STA] E --> G[Switching Logic] F --> G G --> H{Mode Selection} H -->|m=1| I[Output: u_adaptive] H -->|m=2| J[Output: u_STA] I --> K[Final Control u] J --> K style G fill:#ff9 style K fill:#9f9
``` ## Usage Examples ### Example 1: Basic Initialization ```python
from src.controllers.smc.algorithms.hybrid import * # Initialize with configuration
config = {'parameter': 'value'}
instance = Component(config)
``` ### Example 2: Performance Tuning ```python
# Adjust parameters for better performance

optimized_params = tune_parameters(instance, target_performance)
``` ### Example 3: Integration with Controller ```python
# Use in complete control loop
controller = create_controller(ctrl_type, config)
result = simulate(controller, duration=5.0)
``` ### Example 4: Edge Case Handling ```python

try: output = instance.compute(state)
except ValueError as e: handle_edge_case(e)
``` ### Example 5: Performance Analysis ```python
# Analyze metrics
metrics = compute_metrics(result)
print(f"ITAE: {metrics.itae:.3f}")
``` ## Architecture Diagram ```{mermaid}

graph TD A[State Input] --> B[Sliding Surface] B --> C{Surface Value s} A --> D[Model Confidence] D --> E{Switching Logic} C --> F[Equivalent Control] C --> G[Super-Twisting Control] E -->|High Confidence| F E -->|Low Confidence| G F --> H[Transition Filter] G --> H H --> I[Saturation] I --> J[Control Output u] C --> K[Performance Monitor] K --> E style C fill:#ff9 style E fill:#f9f style F fill:#9cf style G fill:#fcf style H fill:#cfc style I fill:#f99
``` **Data Flow:**
1. State → Sliding Surface + Model Confidence
2. Performance Monitoring → Mode Switching Decision
3. High Confidence → Equivalent Control (model-based)
4. Low Confidence → Super-Twisting (robust)
5. Smooth Transition → Final Control Output ## Mathematical Foundation ### Hybrid Adaptive-STA SMC Combines model-based equivalent control with robust adaptive super-twisting: ```{math}
u = u_{eq} + u_{sta}
``` - $u_{eq}$: uses system model when available

- $u_{sta}$: Adaptive super-twisting for robustness ### Mode Switching Logic Intelligent switching between:
1. **Model-based mode**: When model confidence is high
2. **Robust mode**: When uncertainty is detected **See:** {doc}`../../../mathematical_foundations/smc_complete_theory` ## Complete Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/controller.py
:language: python
:linenos:
```

---

## Classes

### `TransitionFilter`

Smoothing filter for control transitions between controllers.

#### Source Code ```

{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/controller.py
:language: python
:pyobject: TransitionFilter
:linenos:
``` #### Methods (3) ##### `__init__(self, time_constant)` Initialize transition filter. [View full source →](#method-transitionfilter-__init__) ##### `filter(self, new_input, dt)` Apply exponential smoothing filter. [View full source →](#method-transitionfilter-filter) ##### `reset(self, initial_value)` Reset filter state. [View full source →](#method-transitionfilter-reset)

---

## `ModularHybridSMC`

Modular Hybrid SMC using intelligent switching between multiple controllers. Provides optimal performance by selecting the most appropriate SMC algorithm

based on current system conditions and performance metrics. #### Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/controller.py
:language: python
:pyobject: ModularHybridSMC
:linenos:
``` #### Methods (20) ##### `__init__(self, config, dynamics)` Initialize modular hybrid SMC. [View full source →](#method-modularhybridsmc-__init__) ##### `_initialize_controllers(self)` Initialize individual SMC controllers based on hybrid mode. [View full source →](#method-modularhybridsmc-_initialize_controllers) ##### `current_mode(self)` Get current hybrid mode for test compatibility. [View full source →](#method-modularhybridsmc-current_mode) ##### `current_mode(self, mode)` Set current hybrid mode for test compatibility. [View full source →](#method-modularhybridsmc-current_mode) ##### `compute_control(self, state, state_vars, history, dt)` Compute hybrid SMC control law. [View full source →](#method-modularhybridsmc-compute_control) ##### `_create_hybrid_result(self, u_final, active_controller, active_result, all_results, switching_decision, switched, state)` Create hybrid control result. [View full source →](#method-modularhybridsmc-_create_hybrid_result) ##### `_extract_controller_specific_info(self, controller_name, result)` Extract controller-specific information for logging. [View full source →](#method-modularhybridsmc-_extract_controller_specific_info) ##### `_compute_tracking_error(self, state)` Compute tracking error from system state. [View full source →](#method-modularhybridsmc-_compute_tracking_error) ##### `_create_error_result(self, error_msg)` Create error result with safe defaults. [View full source →](#method-modularhybridsmc-_create_error_result) ##### `gains(self)` Return hybrid controller surface gains [k1, k2, λ1, λ2]. [View full source →](#method-modularhybridsmc-gains) ##### `validate_gains(self, gains_b)` Vectorized feasibility check for hybrid SMC gains. [View full source →](#method-modularhybridsmc-validate_gains) ##### `get_active_controller_name(self)` Get name of currently active controller. [View full source →](#method-modularhybridsmc-get_active_controller_name) ##### `get_active_controller(self)` Get currently active controller object. [View full source →](#method-modularhybridsmc-get_active_controller) ##### `reset(self)` Reset controller to initial state (standard interface). [View full source →](#method-modularhybridsmc-reset) ##### `reset_all_controllers(self)` Reset all individual controllers to initial state. [View full source →](#method-modularhybridsmc-reset_all_controllers) ##### `force_switch_to_controller(self, controller_name)` Force switch to specific controller. [View full source →](#method-modularhybridsmc-force_switch_to_controller) ##### `get_comprehensive_analysis(self)` Get analysis of hybrid system performance. [View full source →](#method-modularhybridsmc-get_comprehensive_analysis) ##### `_analyze_controller_performance(self)` Analyze relative performance of different controllers. [View full source →](#method-modularhybridsmc-_analyze_controller_performance) ##### `tune_switching_parameters(self)` Tune switching parameters during runtime. [View full source →](#method-modularhybridsmc-tune_switching_parameters) ##### `get_parameters(self)` Get all hybrid system parameters. [View full source →](#method-modularhybridsmc-get_parameters)

---

### `HybridSMC`

Backward-compatible facade for the modular Hybrid SMC.

#### Source Code ```

{literalinclude} ../../../src/controllers/smc/algorithms/hybrid/controller.py
:language: python
:pyobject: HybridSMC
:linenos:
``` #### Methods (6) ##### `__init__(self, hybrid_mode, controller_configs, dt, max_force)` Initialize Hybrid SMC with legacy interface. [View full source →](#method-hybridsmc-__init__) ##### `compute_control(self, state, state_vars, history)` Compute control (delegates to modular controller). [View full source →](#method-hybridsmc-compute_control) ##### `gains(self)` Return controller gains. [View full source →](#method-hybridsmc-gains) ##### `get_active_controller_name(self)` Get active controller name. [View full source →](#method-hybridsmc-get_active_controller_name) ##### `reset_all_controllers(self)` Reset all controllers. [View full source →](#method-hybridsmc-reset_all_controllers) ##### `get_parameters(self)` Get controller parameters. [View full source →](#method-hybridsmc-get_parameters)

---

## Dependencies This module imports: - `from typing import Dict, List, Union, Optional, Any`

- `import numpy as np`
- `import logging`
- `from ..classical.controller import ModularClassicalSMC`
- `from ..adaptive.controller import ModularAdaptiveSMC`
- `from ..super_twisting.controller import ModularSuperTwistingSMC`
- `from .switching_logic import HybridSwitchingLogic, ControllerState`
- `from .config import HybridSMCConfig` ## Usage Examples ### Basic Instantiation ```python
from src.controllers.smc.algorithms.hybrid import ModularHybridSMC
from src.controllers.smc.algorithms.hybrid.config import HybridSMCConfig # Configure hybrid controller
config = HybridSMCConfig( surface_gains=[15.0, 12.0, 18.0, 15.0], proportional_gain=25.0, integral_gain=18.0, derivative_gain=6.0, max_force=100.0, switching_threshold=0.05 # Mode switching sensitivity
) controller = ModularHybridSMC(config, dynamics_model=dynamics)
``` ### Mode Switching Demonstration ```python
from src.core.simulation_runner import SimulationRunner
from src.plant.models.simplified import SimplifiedDynamics dynamics = SimplifiedDynamics()
runner = SimulationRunner(controller, dynamics) result = runner.run( initial_state=[0.2, 0.15, 0, 0, 0, 0], # Large disturbance duration=15.0, dt=0.01
) # Analyze mode switching history
mode_history = result.controller_history['active_mode']
switches = np.diff(mode_history).nonzero()[0]
print(f"Mode switches: {len(switches)} times")
``` ### PSO Optimization with Hybrid Strategy ```python

from src.controllers.factory import create_smc_for_pso, SMCType # Hybrid SMC has 4 gains (surface only, internal switching)
bounds = [ (1.0, 50.0), # k1 (1.0, 50.0), # k2 (1.0, 50.0), # λ1 (1.0, 50.0), # λ2
] def controller_factory(gains): return create_smc_for_pso(SMCType.HYBRID, gains, max_force=100.0) # Optimize for robustness
tuner = PSOTuner(bounds, controller_factory, metric='robustness_index')
best_gains, best_robustness = tuner.optimize(n_particles=35, iters=120)
``` ### Comparing All SMC Variants ```python
from src.controllers.factory import create_all_smc_controllers gains_dict = { "classical": [10, 8, 15, 12, 50, 5], "adaptive": [10, 8, 15, 12, 25], "sta": [25, 10, 15, 12, 20, 15], "hybrid": [15, 12, 18, 15]
} controllers = create_all_smc_controllers(gains_dict, max_force=100.0) # Benchmark all controllers
from src.benchmarks import run_comprehensive_comparison
comparison = run_comprehensive_comparison( controllers=controllers, scenarios='standard', metrics='all'
) comparison.generate_report('controller_comparison.pdf')
``` **See:** {doc}`../../../mathematical_foundations/smc_complete_theory` for hybrid control theory. 
