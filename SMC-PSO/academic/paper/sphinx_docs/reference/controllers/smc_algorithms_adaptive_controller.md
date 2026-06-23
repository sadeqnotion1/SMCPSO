# controllers.smc.algorithms.adaptive.controller

**Source:** `src\controllers\smc\algorithms\adaptive\controller.py`

## Module Overview Modular Adaptive SMC Controller

. Implements Adaptive Sliding Mode Control using composed components:


- LinearSlidingSurface: Surface computation
- AdaptationLaw: Online gain adjustment
- UncertaintyEstimator: Disturbance bound estimation
- SwitchingFunction: Smooth chattering reduction Replaces the monolithic 427-line controller with composition of focused modules. ## Advanced Mathematical Theory ### Adaptive SMC Structure **Control law:** ```{math}
u = -\hat{K}(t) \, \text{sat}(s/\epsilon)
``` Where $\hat{K}(t)$ is adapted online. ### Complete Lyapunov Analysis **Augmented Lyapunov function:** ```{math}
V = \frac{1}{2} s^2 + \frac{1}{2\gamma} \tilde{K}^2
``` **Derivative on sliding surface ($s = 0$):** ```{math}

\dot{V} = s \dot{s} + \frac{1}{\gamma} \tilde{K} \dot{K}
``` **With adaptation law** $\dot{K} = \gamma |s| - \sigma K$: ```{math}
\dot{V} = s \dot{s} + \tilde{K} (|s| - \frac{\sigma}{\gamma} K)
``` If $\dot{s} = -\Delta - \hat{K} \text{sign}(s)$, then: ```{math}

s \dot{s} = -s \Delta - \hat{K} |s| = -s \Delta - K^* |s| - \tilde{K} |s|
``` Substituting: ```{math}
\dot{V} \leq -K^* |s| - s \Delta - \frac{\sigma}{\gamma} \tilde{K} K
``` ### Robustness to Parametric Uncertainty **Model with uncertainty:** ```{math}

\dot{s} = f_0(\vec{x}) + \Delta f(\vec{x}, \vec{\theta}) + u
``` **Adaptive control ensures:** ```{math}
\lim_{t \to \infty} |s(t)| \leq \delta_{residual}
``` Where $\delta_{residual}$ depends on $\epsilon_{max}$ (unmodeled dynamics). ### Transient Performance **Overshoot bound:** ```{math}

\max_{t \geq 0} |s(t)| \leq \sqrt{2 V(0)}
``` ### Steady-State Error **Ultimate bound:** ```{math}
|s|_{ss} \leq \frac{\epsilon_{max}}{K_{min} - |\Delta|_{max}}
``` ## Architecture Diagram ```{mermaid}

graph TD A[State x] --> B[Sliding Surface s] B --> C[Adaptation Law: K̇ = γ|s|] C --> D[Gain K_t_] B --> E[Control: u = -K sat_s/ε_] D --> E E --> F[Saturation] F --> G[Control Output u] B --> H[Feedback to Adaptation] H --> C style C fill:#9cf style G fill:#9f9
``` ## Usage Examples ### Example 1: Basic Initialization ```python
from src.controllers.smc.algorithms.adaptive import * # Initialize with configuration
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

graph TD A[State Input] --> B[Sliding Surface] B --> C{Surface Value s} C --> D[Adaptation Law] D --> E[Adaptive Gain K_t_] C --> F[Switching Control] E --> F F --> G[Saturation] G --> H[Control Output u] C --> I[Uncertainty Estimator] I --> D style C fill:#ff9 style D fill:#9cf style E fill:#f9f style G fill:#f99
``` **Data Flow:**
1. State → Sliding Surface Computation
2. Surface Value → Adaptation Law + Switching Control
3. Online Gain Adaptation: K̇ = γ|s| - σ(K - K₀)
4. Adaptive Switching → Saturation → Control Output ## Mathematical Foundation ### Adaptive Sliding Mode Control Adaptive SMC handles system uncertainties through online gain adaptation: ```{math}
\dot{K} = \gamma |s| - \sigma(K - K_0)
``` Where:

- $\gamma > 0$: Adaptation rate
- $\sigma > 0$: Leakage term preventing unbounded growth
- $K_0$: Initial gain estimate ### Stability with Adaptation Modified Lyapunov function: ```{math}
V(s, \tilde{K}) = \frac{1}{2}s^2 + \frac{1}{2\gamma}\tilde{K}^2
``` Where $\tilde{K} = K - K^*$ is the gain error. The derivative becomes: ```{math}
\dot{V} = -K^*|s| - \sigma \tilde{K}^2 \leq 0
``` Ensuring asymptotic stability even with unknown uncertainty bounds. **See:** {doc}`../../../mathematical_foundations/smc_complete_theory` for adaptation law derivation. ## Complete Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/controller.py

:language: python
:linenos:
```

---

## Classes

### `ModularAdaptiveSMC`

Modular Adaptive SMC using composition of focused components. Adaptive SMC law: u = -K(t) * sign(s)
Where K(t) adapts online: K̇ = γ|s| - σK #### Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/controller.py
:language: python
:pyobject: ModularAdaptiveSMC
:linenos:
``` #### Methods (12) ##### `__init__(self, config, dynamics)` Initialize modular adaptive SMC. [View full source →](#method-modularadaptivesmc-__init__) ##### `compute_control(self, state, state_vars, history, dt)` Compute adaptive SMC control law. [View full source →](#method-modularadaptivesmc-compute_control) ##### `_estimate_surface_derivative(self, state, current_surface)` Estimate surface derivative using finite differences. [View full source →](#method-modularadaptivesmc-_estimate_surface_derivative) ##### `_create_control_result(self, u_final, surface_value, surface_derivative, adaptive_gain, uncertainty_bound, switching_output, u_before_sat)` Create structured control result. [View full source →](#method-modularadaptivesmc-_create_control_result) ##### `_create_error_result(self, error_msg)` Create error result with safe defaults. [View full source →](#method-modularadaptivesmc-_create_error_result) ##### `gains(self)` Return controller gains (static configuration gains only). [View full source →](#method-modularadaptivesmc-gains) ##### `get_adaptive_gain(self)` Get current adaptive gain value. [View full source →](#method-modularadaptivesmc-get_adaptive_gain) ##### `reset(self)` Reset controller to initial state (standard interface). [View full source →](#method-modularadaptivesmc-reset) ##### `reset_adaptation(self, initial_gain)` Reset adaptive components to initial state. [View full source →](#method-modularadaptivesmc-reset_adaptation) ##### `get_adaptation_analysis(self)` Get adaptation analysis. [View full source →](#method-modularadaptivesmc-get_adaptation_analysis) ##### `tune_adaptation_parameters(self, gamma, sigma, rate_limit)` Tune adaptation parameters during runtime. [View full source →](#method-modularadaptivesmc-tune_adaptation_parameters) ##### `get_parameters(self)` Get all controller parameters. [View full source →](#method-modularadaptivesmc-get_parameters)

---

## `AdaptiveSMC`

Backward-compatible facade for the modular Adaptive SMC.

### Source Code ```

{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/controller.py

:language: python
:pyobject: AdaptiveSMC
:linenos:
``` #### Methods (7) ##### `__init__(self, gains, dt, max_force)` Initialize Adaptive SMC with legacy interface. [View full source →](#method-adaptivesmc-__init__) ##### `compute_control(self, state, state_vars, history)` Compute control (delegates to modular controller). [View full source →](#method-adaptivesmc-compute_control) ##### `gains(self)` Return controller gains. [View full source →](#method-adaptivesmc-gains) ##### `get_adaptive_gain(self)` Get current adaptive gain. [View full source →](#method-adaptivesmc-get_adaptive_gain) ##### `reset(self)` Reset controller to initial state. [View full source →](#method-adaptivesmc-reset) ##### `reset_adaptation(self)` Reset adaptation state. [View full source →](#method-adaptivesmc-reset_adaptation) ##### `get_parameters(self)` Get controller parameters. [View full source →](#method-adaptivesmc-get_parameters)

---

## Dependencies This module imports: - `from typing import Dict, List, Union, Optional, Any`
- `import numpy as np`
- `import logging`
- `from ...core.sliding_surface import LinearSlidingSurface`
- `from ...core.switching_functions import SwitchingFunction`
- `from .adaptation_law import AdaptationLaw`
- `from .parameter_estimation import UncertaintyEstimator`
- `from .config import AdaptiveSMCConfig` ## Usage Examples ### Basic Instantiation ```python
from src.controllers.smc.algorithms.adaptive import ModularAdaptiveSMC
from src.controllers.smc.algorithms.adaptive.config import AdaptiveSMCConfig # Configure adaptive controller
config = AdaptiveSMCConfig( surface_gains=[10.0, 8.0, 15.0, 12.0], # [k1, k2, λ1, λ2] initial_switching_gain=25.0, # K₀ adaptation_rate=5.0, # γ leakage_term=0.1, # σ max_force=100.0
) controller = ModularAdaptiveSMC(config, dynamics=dynamics)
``` ### Simulation with Online Adaptation ```python

from src.core.simulation_runner import SimulationRunner
from src.plant.models.simplified import SimplifiedDynamics # Create simulation with adaptive controller
dynamics = SimplifiedDynamics()
runner = SimulationRunner(controller, dynamics) # Run with uncertainty
result = runner.run( initial_state=[0.1, 0.05, 0, 0, 0, 0], duration=10.0, dt=0.01
) # Analyze gain adaptation
adaptive_gains = result.history['adaptive_gain']
print(f"Final adapted gain: {adaptive_gains[-1]:.2f}")
``` ### PSO Optimization of Adaptive Parameters ```python
from src.controllers.factory import create_smc_for_pso, SMCType
from src.optimizer.pso_optimizer import PSOTuner # Adaptive SMC has 5 gains: [k1, k2, λ1, λ2, K₀]
bounds = [ (0.1, 50.0), # k1 (0.1, 50.0), # k2 (0.1, 50.0), # λ1 (0.1, 50.0), # λ2 (1.0, 100.0) # K₀
] # Create controller factory
def controller_factory(gains): return create_smc_for_pso(SMCType.ADAPTIVE, gains, max_force=100.0) # Run PSO optimization
tuner = PSOTuner(bounds, controller_factory)
best_gains, best_fitness = tuner.optimize(n_particles=30, iters=100)
``` ### Custom Adaptation Tuning ```python

from src.controllers.smc.algorithms.adaptive.adaptation_law import AdaptationLaw # Experiment with different adaptation strategies
adaptation = AdaptationLaw( gamma=5.0, # Fast adaptation sigma=0.1, # Low leakage K_min=1.0, # Minimum gain bound K_max=200.0 # Maximum gain bound
) # Test adaptation response
for uncertainty in [5.0, 10.0, 20.0]: adapted_gain = adaptation.update(surface=0.1, uncertainty=uncertainty, dt=0.01) print(f"Uncertainty={uncertainty}: K={adapted_gain:.2f}")
``` **See:** {doc}`../../../mathematical_foundations/smc_complete_theory` for adaptation law theory. 
