# controllers.smc.algorithms.super_twisting.controller

**Source:** `src\controllers\smc\algorithms\super_twisting\controller.py`

## Module Overview Modular Super-Twisting SMC Controller

. Implements Super-Twisting Sliding Mode Control using composed components:


- LinearSlidingSurface: Surface computation
- SuperTwistingAlgorithm: Second-order sliding mode control
- SwitchingFunction: Smooth chattering reduction Provides finite-time convergence with chattering reduction through
second-order sliding mode dynamics. ## Advanced Mathematical Theory ### STA-SMC Complete Workflow **Algorithm steps:**
1. Compute sliding surface $s$
2. Compute $u_1 = -K_1 |s|^{0.5} \text{sign}(s)$
3. Update integral $u_2 = u_2 + (-K_2 \text{sign}(s)) \Delta t$
4. Total control: $u = u_1 + u_2$
5. Apply saturation and output ### Performance vs Classical SMC | Metric | Classical SMC | Super-Twisting SMC |
|--------|---------------|-------------------|
| **Convergence** | Asymptotic | Finite-time |
| **Chattering** | Moderate | Minimal |
| **Accuracy** | $O(\epsilon)$ | $O(\epsilon^2)$ |
| **Complexity** | O(n) | O(n) |
| **Tuning** | Medium | Hard | ### Gain Tuning Heuristics **Start with:** ```{math}
\begin{align}
K_1 &= 2 \sqrt{|\Delta|_{max}} \\
K_2 &= 1.5 |\Delta|_{max} \\
\alpha &= 0.5
\end{align}
``` **Adjust based on:**
- Larger $K_1$ → Faster convergence, more control effort
- Larger $K_2$ → Better disturbance rejection
- Smaller $\alpha$ → Smoother control ### Anti-Windup for Integral Term **Conditional integration:** ```{math}
\dot{u}_2 = \begin{cases}
-K_2 \text{sign}(s), & |u_1 + u_2| \leq u_{max} \\
0, & \text{otherwise}
\end{cases}
``` ### Regularization for Practical Implementation **Smooth sign approximation:** ```{math}

\text{sign}(s) \approx \frac{s}{|s| + \delta}, \quad \delta = 10^{-6}
``` Avoids division by zero when $s = 0$. ## Architecture Diagram ```{mermaid}
graph TD A[State x] --> B[Sliding Surface s] B --> C[u₁: -K₁|s|^0.5 sign_s_] B --> D[u₂: -K₂ ∫sign_s_dt] C --> E[Sum: u = u₁ + u₂] D --> E E --> F[Saturation] F --> G[Control Output u] B --> H{|s| → 0?} H -->|Yes| I[Finite-Time Convergence] style E fill:#9cf style I fill:#9f9 style G fill:#9f9
``` ## Usage Examples ### Example 1: Basic Initialization ```python

from src.controllers.smc.algorithms.super_twisting import * # Initialize with configuration
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
graph TD A[State Input] --> B[Sliding Surface] B --> C{Surface Value s} C --> D[Proportional Term] C --> E[Integral Term] D --> F["u₁ = -K₁|s|^1/2_sign_s_"] E --> G["u̇₂ = -K₂sign_s_"] G --> H[Integrator] H --> I[u₂] F --> J[Control Combiner] I --> J J --> K[Saturation] K --> L[Control Output u] style C fill:#ff9 style D fill:#9cf style E fill:#fcf style J fill:#9f9 style K fill:#f99
``` **Data Flow:**

1. State → Sliding Surface Computation
2. Surface → Proportional Term (fractional power)
3. Surface → Integral Term (continuous integration)
4. Continuous Control → Chattering-Free Output ## Mathematical Foundation ### Super-Twisting Algorithm (STA) Second-order sliding mode control with continuous control signal: ```{math}
\begin{align}
u &= -K_1 |s|^{1/2} \text{sign}(s) + u_1 \\
\dot{u}_1 &= -K_2 \text{sign}(s)
\end{align}
``` ### Finite-Time Convergence STA ensures $s = \dot{s} = 0$ in finite time with: ```{math}
K_1 > 0, \quad K_2 > \frac{L}{2}
``` Where $L$ is the Lipschitz constant of disturbances. ### Chattering-Free Property Continuous control eliminates chattering while maintaining finite-time convergence. **See:** {doc}`../../../mathematical_foundations/smc_complete_theory` ## Complete Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/super_twisting/controller.py

:language: python
:linenos:
```

---

## Classes

### `ModularSuperTwistingSMC`

Modular Super-Twisting SMC using composition of focused components. Super-Twisting control law:
u = u₁ + u₂
u₁ = -K₁|s|^α sign(s)
u₂ = -K₂ ∫sign(s)dt Provides finite-time convergence when K₁ > K₂ > 0. #### Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/super_twisting/controller.py
:language: python
:pyobject: ModularSuperTwistingSMC
:linenos:
``` #### Methods (16) ##### `__init__(self, config, dynamics)` Initialize modular Super-Twisting SMC. [View full source →](#method-modularsupertwistingsmc-__init__) ##### `compute_control(self, state, state_vars, history, dt)` Compute Super-Twisting SMC control law. [View full source →](#method-modularsupertwistingsmc-compute_control) ##### `_estimate_surface_derivative(self, state, current_surface)` Estimate surface derivative using finite differences. [View full source →](#method-modularsupertwistingsmc-_estimate_surface_derivative) ##### `_create_control_result(self, u_final, surface_value, surface_derivative, twisting_result, damping_control, u_before_sat)` Create structured control result. [View full source →](#method-modularsupertwistingsmc-_create_control_result) ##### `_create_error_result(self, error_msg)` Create error result with safe defaults. [View full source →](#method-modularsupertwistingsmc-_create_error_result) ##### `_is_anti_windup_active(self)` Check if anti-windup is currently active. [View full source →](#method-modularsupertwistingsmc-_is_anti_windup_active) ##### `gains(self)` Return controller gains [K1, K2, k1, k2, λ1, λ2]. [View full source →](#method-modularsupertwistingsmc-gains) ##### `validate_gains(self, gains_b)` Vectorized feasibility check for super‑twisting SMC gains. [View full source →](#method-modularsupertwistingsmc-validate_gains) ##### `get_twisting_gains(self)` Get Super-Twisting gains (K1, K2). [View full source →](#method-modularsupertwistingsmc-get_twisting_gains) ##### `set_twisting_gains(self, K1, K2)` Update Super-Twisting gains. [View full source →](#method-modularsupertwistingsmc-set_twisting_gains) ##### `reset_controller(self)` Reset controller to initial state. [View full source →](#method-modularsupertwistingsmc-reset_controller) ##### `reset(self)` Reset controller state (interface compliance). [View full source →](#method-modularsupertwistingsmc-reset) ##### `get_stability_analysis(self)` Get stability analysis. [View full source →](#method-modularsupertwistingsmc-get_stability_analysis) ##### `tune_gains(self, K1, K2, boundary_layer)` Tune controller parameters during runtime. [View full source →](#method-modularsupertwistingsmc-tune_gains) ##### `get_parameters(self)` Get all controller parameters. [View full source →](#method-modularsupertwistingsmc-get_parameters) ##### `get_convergence_estimate(self, current_surface)` Estimate convergence properties. [View full source →](#method-modularsupertwistingsmc-get_convergence_estimate)

---

## `SuperTwistingSMC`

Backward-compatible facade for the modular Super-Twisting SMC.

### Source Code ```

{literalinclude} ../../../src/controllers/smc/algorithms/super_twisting/controller.py

:language: python
:pyobject: SuperTwistingSMC
:linenos:
``` #### Methods (6) ##### `__init__(self, gains, dt, max_force)` Initialize Super-Twisting SMC with legacy interface. [View full source →](#method-supertwistingsmc-__init__) ##### `compute_control(self, state, state_vars, history)` Compute control (delegates to modular controller). [View full source →](#method-supertwistingsmc-compute_control) ##### `gains(self)` Return controller gains. [View full source →](#method-supertwistingsmc-gains) ##### `get_twisting_gains(self)` Get Super-Twisting gains. [View full source →](#method-supertwistingsmc-get_twisting_gains) ##### `reset_controller(self)` Reset controller state. [View full source →](#method-supertwistingsmc-reset_controller) ##### `get_parameters(self)` Get controller parameters. [View full source →](#method-supertwistingsmc-get_parameters)

---

## Dependencies This module imports: - `from typing import Dict, List, Union, Optional, Any`
- `import numpy as np`
- `import logging`
- `from ...core.sliding_surface import LinearSlidingSurface`
- `from ...core.switching_functions import SwitchingFunction`
- `from .twisting_algorithm import SuperTwistingAlgorithm`
- `from .config import SuperTwistingSMCConfig` ## Usage Examples ### Basic Instantiation ```python
from src.controllers.smc.algorithms.super_twisting import ModularSuperTwistingSMC
from src.controllers.smc.algorithms.super_twisting.config import SuperTwistingSMCConfig # Configure super-twisting controller
config = SuperTwistingSMCConfig( surface_gains=[25.0, 10.0, 15.0, 12.0], # Higher gains for robustness proportional_gain=20.0, # K₁ integral_gain=15.0, # K₂ derivative_gain=5.0, # kd max_force=100.0
) controller = ModularSuperTwistingSMC(config, dynamics=dynamics)
``` ### Chattering-Free Simulation ```python

from src.core.simulation_runner import SimulationRunner
from src.plant.models.full import FullDynamics # Use full dynamics for realistic chattering assessment
dynamics = FullDynamics()
runner = SimulationRunner(controller, dynamics) result = runner.run( initial_state=[0.15, 0.1, 0, 0, 0, 0], duration=10.0, dt=0.001 # High frequency for chattering detection
) # Analyze chattering index
chattering = runner.compute_chattering_index(result.control_history)
print(f"Chattering index: {chattering:.4f} (lower is better)")
``` ### PSO Optimization for Finite-Time Convergence ```python
from src.controllers.factory import create_smc_for_pso, SMCType # STA requires 6 gains: [k1, k2, λ1, λ2, K₁, K₂]
# STA stability: K₁

> K₂ for finite-time convergence
bounds = [ (1.0, 50.0), # k1 (1.0, 50.0), # k2 (1.0, 50.0), # λ1 (1.0, 50.0), # λ2 (10.0, 100.0), # K₁ (proportional) (5.0, 50.0), # K₂ (integral)
] def controller_factory(gains): return create_smc_for_pso(SMCType.SUPER_TWISTING, gains, max_force=100.0) # Optimize for convergence time
tuner = PSOTuner(bounds, controller_factory, metric='convergence_time')
best_gains, best_time = tuner.optimize(n_particles=40, iters=150)
``` ### Finite-Time Convergence Verification ```python

import numpy as np # Theoretical convergence time: t_c ≈ 2|s(0)|/(K₁√K₂)
K1, K2 = 20.0, 15.0
s0 = 0.1 theoretical_time = 2 * abs(s0) / (K1 * np.sqrt(K2))
print(f"Theoretical convergence: {theoretical_time:.3f}s") # Run simulation and measure actual convergence
result = runner.run(initial_state=[0.1, 0, 0, 0, 0, 0], duration=5.0)
actual_time = np.argmax(np.abs(result.surface_history) < 0.01) * 0.01
print(f"Actual convergence: {actual_time:.3f}s")
``` **See:** {doc}`../../../mathematical_foundations/smc_complete_theory` for STA theory and proofs. 
