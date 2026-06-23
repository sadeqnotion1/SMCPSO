# optimization.integration.pso_factory_bridge

**Source:** `src\optimization\integration\pso_factory_bridge.py`

## Module Overview Advanced PSO-Factory Integration Bridge

.

## Advanced Mathematical Theory

### Controller-PSO Integration


\begin{align}
\min_{\vec{\theta} \in \Theta} \quad & J(\vec{\theta}) \\
\text{where} \quad & J(\vec{\theta}) = \int_0^T L(\vec{x}(t; \vec{\theta}), u(t; \vec{\theta})) \, dt
\end{align}
``` **Mapping:** PSO particles $\vec{x}_i \leftrightarrow$ Controller gains $\vec{\theta}_i$

### Factory Pattern Integration

**Controller creation from PSO particle:**

```python
## example-metadata:
## runnable: false

def particle_to_controller(particle: np.ndarray) -> Controller:
    gains = {
        'k1': particle[0],
        'k2': particle[1],
        ## ...
    }
    return ControllerFactory.create(gains)
``` ### Parameter Mapping Strategies **Direct mapping:** ```{math}

\theta_i = x_i, \quad \theta_i \in [\theta_{min,i}, \theta_{max,i}]
``` **Logarithmic mapping** for wide-range gains: ```{math}
\theta_i = 10^{x_i}, \quad x_i \in [\log_{10}(\theta_{min,i}), \log_{10}(\theta_{max,i})]
``` **Exponential mapping:** ```{math}

\theta_i = \theta_{min,i} + (\theta_{max,i} - \theta_{min,i}) \cdot e^{x_i}
``` ### Fitness Function Design **Weighted multi-objective:** ```{math}
J(\vec{\theta}) = w_1 \text{ITAE}(\vec{\theta}) + w_2 \text{ISE}(\vec{\theta}) + w_3 \text{CHAT}(\vec{\theta}) + w_4 P_{constraint}(\vec{\theta})
``` Where: ```{math}

\begin{align}
\text{ITAE} &= \int_0^T t |e(t)| \, dt \\
\text{ISE} &= \int_0^T e^2(t) \, dt \\
\text{CHAT} &= \int_0^T |\dot{u}(t)| \, dt \\
P_{constraint} &= \sum_j r_j \max(0, |u_{max}| - u_{sat})^2
\end{align}
``` ### Simulation-Based Evaluation **Evaluation pipeline:** 1. Map PSO particle to controller gains
2. Create controller instance via factory
3. Run closed-loop simulation
4. Compute performance metrics
5. Return fitness value **Parallel evaluation** for swarm: ```{math}
\vec{F} = \text{ParallelMap}(\text{EvaluateFitness}, \vec{X})
``` ### Optimization Workflow **Complete PSO-Controller tuning:** ```

1. Define parameter bounds for controller gains
2. Initialize PSO swarm in parameter space
3. For each particle: a. Map to controller gains b. Create controller c. Simulate system d. Compute fitness
4. Update PSO particles
5. Repeat until convergence
6. Return best controller gains
``` ## Architecture Diagram ```{mermaid}
graph TD A[PSO Particle] --> B[Parameter Mapping] B --> C{Mapping Type} C -->|Direct| D[Linear Mapping] C -->|Log| E[Logarithmic Mapping] C -->|Exp| F[Exponential Mapping] D --> G[Controller Gains] E --> G F --> G G --> H[Controller Factory] H --> I[Create Controller] I --> J[Simulate System] J --> K[Compute Metrics] K --> L[ITAE] K --> M[ISE] K --> N[Chattering] L --> O[Weighted Sum] M --> O N --> O O --> P[Fitness Value] P --> Q[PSO Update] style C fill:#ff9 style H fill:#9cf style P fill:#9f9
``` ## Usage Examples ### Example 1: Basic Initialization ```python

from src.optimization.core import * # Initialize with configuration
config = {'parameter': 'value'}
instance = Component(config)
```

### Example 2: Performance Tuning

```python
## Adjust parameters for better performance
optimized_params = tune_parameters(instance, target_performance)
```

### Example 3: Integration with Optimization

```python
## Use in complete optimization loop
optimizer = create_optimizer(opt_type, config)
result = optimize(optimizer, problem, max_iter=100)
```

### Example 4: Edge Case Handling

```python
try:
    output = instance.compute(parameters)
except ValueError as e:
    handle_edge_case(e)
```

### Example 5: Performance Analysis

```python
## Analyze metrics
metrics = compute_metrics(result)
print(f"Best fitness: {metrics.best_fitness:.3f}")
```
This module provides robust integration between PSO optimization and the controller factory
pattern, addressing fitness evaluation issues, parameter validation, and convergence diagnostics. ## Complete Source Code ```{literalinclude} ../../../src/optimization/integration/pso_factory_bridge.py
:language: python
:linenos:
```

## Classes

### `ControllerType`

**Inherits from:** `Enum` Controller types for PSO optimization.

#### Source Code ```

{literalinclude} ../../../src/optimization/integration/pso_factory_bridge.py

:language: python
:pyobject: ControllerType
:linenos:
```

### `PSOFactoryConfig`

Configuration for PSO-Factory integration.

#### Source Code ```

{literalinclude} ../../../src/optimization/integration/pso_factory_bridge.py
:language: python
:pyobject: PSOFactoryConfig
:linenos:
```

### `EnhancedPSOFactory`

Enhanced PSO-Factory integration with advanced optimization capabilities.

#### Source Code ```

{literalinclude} ../../../src/optimization/integration/pso_factory_bridge.py

:language: python
:pyobject: EnhancedPSOFactory
:linenos:
``` #### Methods (11) ##### `__init__(self, config, global_config_path)` Initialize enhanced PSO factory. [View full source →](#method-enhancedpsofactory-__init__) ##### `_get_controller_specifications(self)` Get controller-specific optimization specifications. [View full source →](#method-enhancedpsofactory-_get_controller_specifications) ##### `_get_default_gains(self, smc_type)` Get robust default gains for controller type. [View full source →](#method-enhancedpsofactory-_get_default_gains) ##### `create_enhanced_controller_factory(self)` Create an enhanced controller factory with robust error handling. [View full source →](#method-enhancedpsofactory-create_enhanced_controller_factory) ##### `create_enhanced_fitness_function(self, controller_factory)` Create enhanced fitness function with proper simulation execution. [View full source →](#method-enhancedpsofactory-create_enhanced_fitness_function) ##### `_evaluate_controller_performance(self, controller, gains)` Evaluate controller performance across multiple scenarios. [View full source →](#method-enhancedpsofactory-_evaluate_controller_performance) ##### `_simulate_scenario(self, controller, scenario)` Simulate a specific control scenario and compute cost. [View full source →](#method-enhancedpsofactory-_simulate_scenario) ##### `optimize_controller(self)` Run enhanced PSO optimization with monitoring. [View full source →](#method-enhancedpsofactory-optimize_controller) ##### `_analyze_optimization_performance(self, pso_result)` Analyze PSO optimization performance and convergence. [View full source →](#method-enhancedpsofactory-_analyze_optimization_performance) ##### `_validate_optimized_controller(self, controller, gains)` Validate the optimized controller performance. [View full source →](#method-enhancedpsofactory-_validate_optimized_controller) ##### `get_optimization_diagnostics(self)` Get optimization diagnostics. [View full source →](#method-enhancedpsofactory-get_optimization_diagnostics)

## Functions

### `create_optimized_controller_factory(controller_type, optimization_config)`

Create an optimized controller factory using PSO with results.

#### Source Code ```

{literalinclude} ../../../src/optimization/integration/pso_factory_bridge.py
:language: python
:pyobject: create_optimized_controller_factory
:linenos:
```

### `optimize_classical_smc()`

Optimize Classical SMC controller using PSO.

#### Source Code ```

{literalinclude} ../../../src/optimization/integration/pso_factory_bridge.py

:language: python
:pyobject: optimize_classical_smc
:linenos:
```

### `optimize_adaptive_smc()`

Optimize Adaptive SMC controller using PSO.

#### Source Code ```

{literalinclude} ../../../src/optimization/integration/pso_factory_bridge.py
:language: python
:pyobject: optimize_adaptive_smc
:linenos:
```

### `optimize_sta_smc()`

Optimize Super-Twisting SMC controller using PSO.

#### Source Code ```

{literalinclude} ../../../src/optimization/integration/pso_factory_bridge.py

:language: python
:pyobject: optimize_sta_smc
:linenos:
```

## Dependencies This module imports: - `import numpy as np`
- `import logging`
- `from typing import Any, Callable, Dict, List, Optional, Tuple, Union`
- `from dataclasses import dataclass`
- `from enum import Enum`
- `from src.controllers.factory import SMCType, SMCFactory, create_smc_for_pso, get_gain_bounds_for_pso, validate_smc_gains, get_expected_gain_count`
- `from src.optimization.algorithms.pso_optimizer import PSOTuner`
- `from src.config import load_config`
- `from src.plant.configurations import ConfigurationFactory`
