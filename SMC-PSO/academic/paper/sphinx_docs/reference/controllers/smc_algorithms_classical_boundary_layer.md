# controllers.smc.algorithms.classical.boundary_layer

**Source:** `src\controllers\smc\algorithms\classical\boundary_layer.py`

## Module Overview Boundary

Layer Implementation for Classical SMC

. Implements boundary layer method for chattering reduction in sliding mode control.


Extracted from the original monolithic controller to provide focused, reusable
boundary layer logic. Mathematical Background:
- Boundary layer thickness ε controls trade-off between chattering and tracking error
- Adaptive boundary layer: ε_eff = ε + α|ṡ| adapts to surface motion
- Switching function approximates sign(s) with continuous function within ±ε ## Advanced Mathematical Theory ### Boundary Layer Design The boundary layer thickness $\epsilon$ controls the trade-off between chattering and tracking accuracy. ### Optimal Boundary Layer Width **Noise-based selection:** ```{math}
\epsilon_{opt} = 3 \sigma_{noise} \sqrt{1 + \frac{\omega_c^2}{\omega_n^2}}
``` Where:
- $\sigma_{noise}$: Measurement noise standard deviation
- $\omega_c$: Chattering frequency
- $\omega_n$: Natural frequency of sliding surface ### Steady-State Error Bound Within boundary layer, steady-state error is bounded: ```{math}
|e_{ss}| \leq \epsilon \max_i \{\lambda_i\}
``` ### Adaptive Boundary Layer **Time-varying thickness:** ```{math}

\epsilon_{eff}(t) = \epsilon_0 + \alpha |\dot{s}(t)|
``` Adapts to surface velocity - thicker when $|\dot{s}|$ large. ### Chattering Frequency Analysis **Describing function approximation:** ```{math}
\omega_c \approx \sqrt{\frac{K \beta}{\epsilon m_{eff}}}
``` Where $m_{eff}$ is effective system inertia. ### Switching Function Comparison | Method | Smoothness | Chattering | Complexity |

|--------|-----------|-----------|------------|
| sign | C⁰ | High | O(1) |
| saturation | C⁰ | Medium | O(1) |
| tanh | C^∞ | Low | O(10) | ### Performance Metrics **Chattering index:** ```{math}
I_c = \frac{1}{T} \int_0^T |\dot{u}(t)| dt
``` Target: $I_c < I_{max}$ (e.g., 100 N/s for hydraulic actuators) ## Architecture Diagram ```{mermaid}
graph TD A[Sliding Surface s] --> B{|s| vs ε} B -->|s > ε| C[Linear Region: u = K] B -->|s < -ε| D[Linear Region: u = -K] B -->|-ε ≤ s ≤ ε| E[Boundary Layer] E --> F{Switching Method} F -->|saturation| G[sat_s/ε_] F -->|tanh| H[tanh_βs/ε_] G --> I[Control Output u_sw] H --> I style E fill:#ff9 style I fill:#9f9
``` ## Usage Examples ### Example 1: Basic Initialization ```python

from src.controllers.smc.algorithms.classical import * # Initialize with configuration
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
``` ## Complete Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/classical/boundary_layer.py
:language: python
:linenos:
```

---

## Classes

### `BoundaryLayer`

Boundary layer implementation for chattering reduction. Provides continuous approximation to discontinuous switching within

a thin layer around the sliding surface. #### Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/classical/boundary_layer.py
:language: python
:pyobject: BoundaryLayer
:linenos:
``` #### Methods (11) ##### `__init__(self, thickness, slope, switch_method)` Initialize boundary layer. [View full source →](#method-boundarylayer-__init__) ##### `get_effective_thickness(self, surface_derivative)` Compute effective boundary layer thickness. [View full source →](#method-boundarylayer-get_effective_thickness) ##### `apply_to_surface(self, surface_value, surface_derivative)` Apply boundary layer switching to surface value. [View full source →](#method-boundarylayer-apply_to_surface) ##### `compute_switching_control(self, surface_value, switching_gain, surface_derivative)` Compute switching control component. [View full source →](#method-boundarylayer-compute_switching_control) ##### `is_in_boundary_layer(self, surface_value, surface_derivative)` Check if system is within boundary layer. [View full source →](#method-boundarylayer-is_in_boundary_layer) ##### `get_chattering_index(self, control_history, dt)` Compute chattering index from control signal history using FFT-based spectral analysis. [View full source →](#method-boundarylayer-get_chattering_index) ##### `update_thickness(self, new_thickness)` Update base boundary layer thickness. [View full source →](#method-boundarylayer-update_thickness) ##### `update_slope(self, new_slope)` Update adaptive slope coefficient. [View full source →](#method-boundarylayer-update_slope) ##### `get_parameters(self)` Get boundary layer parameters. [View full source →](#method-boundarylayer-get_parameters) ##### `analyze_performance(self, surface_history, control_history, dt, state_history)` Analyze boundary layer performance with metrics. [View full source →](#method-boundarylayer-analyze_performance) ##### `_estimate_convergence_time(self, surface_history, dt, tolerance)` Estimate time to converge to boundary layer. [View full source →](#method-boundarylayer-_estimate_convergence_time)

---

## Dependencies This module imports: - `from typing import Union, Callable, Optional`
- `import numpy as np`
- `from ...core.switching_functions import SwitchingFunction`
