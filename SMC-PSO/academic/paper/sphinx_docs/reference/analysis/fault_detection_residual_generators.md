# analysis.fault_detection.residual_generators

**Source:** `src\analysis\fault_detection\residual_generators.py`

## Module Overview

Model-based residual generation for fault detection.



## Advanced Mathematical Theory

### Residual Generation Algorithms

**General form:**

```{math}
\vec{r}(t) = g(\vec{y}(t), \vec{u}(t), \hat{\vec{x}}(t))
```

### Observer-Based Residuals

**Full-order observer:**

```{math}
\begin{align}
\dot{\hat{\vec{x}}} &= A\hat{\vec{x}} + B\vec{u} + L(\vec{y} - C\hat{\vec{x}}) \\
\vec{r} &= \vec{y} - C\hat{\vec{x}}
\end{align}
```

**Error dynamics:**

```{math}
\dot{\vec{e}} = (A - LC)\vec{e} + E\vec{f}
```

Choose $L$ for stable $A - LC$ and fault sensitivity.

### Reduced-Order Observer

**For observable pair $(A, C)$ with $C$ full rank:**

```{math}
\begin{align}
\dot{\vec{z}} &= F\vec{z} + GB\vec{u} + GLC\vec{y} \\
\hat{\vec{x}} &= T^{-1}(\vec{z} + L\vec{y})
\end{align}
```

Dimension: $n - p$ instead of $n$.

### Parity Space Residuals

**Temporal parity equations** (over window $[t-s, t]$):

```{math}
\vec{r} = W \begin{bmatrix} y(t-s) \\ \vdots \\ y(t) \\ u(t-s) \\ \vdots \\ u(t) \end{bmatrix}
```

**Null space:** $W$ chosen so $W^T H = 0$ where $H$ contains system matrices.

### Unknown Input Observer

**For disturbances $\vec{d}$:**

```{math}
\begin{align}
\dot{\vec{x}} &= A\vec{x} + B\vec{u} + E_d\vec{d} + E_f\vec{f} \\
\vec{y} &= C\vec{x}
\end{align}
```

**UIO design:** Decouple disturbance, retain fault sensitivity.

**Conditions:** $\text{rank}(CE_d) = \text{rank}(E_d)$

### Dedicated Residuals

**Dedicated observer scheme (DOS):**

Design $m$ observers, each insensitive to fault $f_i$:

```{math}
r_i = 0 \text{ if fault } f_i, \quad r_i \neq 0 \text{ otherwise}
```

**Generalized observer scheme (GOS):**

Each $r_i$ sensitive only to $f_i$:

```{math}
r_i \neq 0 \text{ iff fault } f_i
```

## Architecture Diagram

```{mermaid}
graph TD
    A[System Model] --> B{Residual Type}

    B -->|Observer| C[Full-Order Observer]
    B -->|Parity| D[Parity Equations]
    B -->|UIO| E[Unknown Input Observer]

    C --> F[State Estimate]
    F --> G[r = y - Cx̂]

    D --> H[Null Space W]
    H --> I[r = W[y; u]]

    E --> J[Disturbance Decoupling]
    J --> K[r_UIO]

    G --> L[Residual Vector]
    I --> L
    K --> L

    L --> M[Sensitivity Analysis]
    M --> N{Fault Sensitive?}
    N -->|Yes| O[Good Residual]
    N -->|No| P[Redesign]

    style M fill:#9cf
    style N fill:#ff9
    style O fill:#9f9
```

## Usage Examples

### Example 1: Basic Initialization

```python
from src.analysis import Component

# Initialize component
component = Component(config)
result = component.process(data)
```

## Example 2: Advanced Configuration

```python
# Configure with custom parameters
config = {
    'threshold': 0.05,
    'method': 'adaptive'
}
component = Component(config)
```

## Example 3: Integration Workflow

```python
# Complete analysis workflow
from src.analysis import analyze

results = analyze(
    data=sensor_data,
    method='enhanced',
    visualization=True
)
```

## Example 4: Fault Detection Example

```python
# FDI system usage
from src.analysis.fault_detection import FDISystem

fdi = FDISystem(config)
residual = fdi.generate_residual(y, u)
fault = fdi.detect(residual)
```

## Example 5: Visualization Example

```python
# Generate analysis plots
from src.analysis.visualization import AnalysisPlotter

plotter = AnalysisPlotter(style='professional')
fig = plotter.plot_time_series(data)
fig.savefig('analysis.pdf')
```

This module provides various residual generation methods for fault detection
including observer-based, parity-based, and parameter estimation approaches.

## Complete Source Code

```{literalinclude} ../../../src/analysis/fault_detection/residual_generators.py
:language: python
:linenos:
```



## Classes

### `SystemModel`

**Inherits from:** `Protocol`

Protocol for system models used in residual generation.

#### Source Code

```{literalinclude} ../../../src/analysis/fault_detection/residual_generators.py
:language: python
:pyobject: SystemModel
:linenos:
```

#### Methods (2)

##### `predict(self, state, control, dt)`

Predict next state given current state and control.

[View full source →](#method-systemmodel-predict)

##### `observe(self, state)`

Compute output from state.

[View full source →](#method-systemmodel-observe)



### `ResidualGeneratorConfig`

Configuration for residual generators.

#### Source Code

```{literalinclude} ../../../src/analysis/fault_detection/residual_generators.py
:language: python
:pyobject: ResidualGeneratorConfig
:linenos:
```



### `ResidualGenerator`

**Inherits from:** `ABC`

Abstract base class for residual generators.

#### Source Code

```{literalinclude} ../../../src/analysis/fault_detection/residual_generators.py
:language: python
:pyobject: ResidualGenerator
:linenos:
```

#### Methods (2)

##### `generate_residual(self, data, system_model)`

Generate residual from data and system model.

[View full source →](#method-residualgenerator-generate_residual)

##### `reset(self)`

Reset generator state.

[View full source →](#method-residualgenerator-reset)



### `ObserverBasedGenerator`

**Inherits from:** `ResidualGenerator`

Observer-based residual generator using Luenberger observers.

#### Source Code

```{literalinclude} ../../../src/analysis/fault_detection/residual_generators.py
:language: python
:pyobject: ObserverBasedGenerator
:linenos:
```

#### Methods (4)

##### `__init__(self, config, A, C)`

Initialize observer-based generator.

[View full source →](#method-observerbasedgenerator-__init__)

##### `_design_observer(self)`

Design observer gain matrix.

[View full source →](#method-observerbasedgenerator-_design_observer)

##### `generate_residual(self, data, system_model)`

Generate observer-based residual.

[View full source →](#method-observerbasedgenerator-generate_residual)

##### `reset(self)`

Reset observer state.

[View full source →](#method-observerbasedgenerator-reset)



### `KalmanFilterGenerator`

**Inherits from:** `ResidualGenerator`

Kalman filter-based residual generator.

#### Source Code

```{literalinclude} ../../../src/analysis/fault_detection/residual_generators.py
:language: python
:pyobject: KalmanFilterGenerator
:linenos:
```

#### Methods (3)

##### `__init__(self, config, A, B, C, D)`

Initialize Kalman filter generator.

[View full source →](#method-kalmanfiltergenerator-__init__)

##### `generate_residual(self, data, system_model)`

Generate Kalman filter innovation residual.

[View full source →](#method-kalmanfiltergenerator-generate_residual)

##### `reset(self)`

Reset Kalman filter state.

[View full source →](#method-kalmanfiltergenerator-reset)



### `ParitySpaceGenerator`

**Inherits from:** `ResidualGenerator`

Parity space-based residual generator.

#### Source Code

```{literalinclude} ../../../src/analysis/fault_detection/residual_generators.py
:language: python
:pyobject: ParitySpaceGenerator
:linenos:
```

#### Methods (4)

##### `__init__(self, config, A, B, C)`

Initialize parity space generator.

[View full source →](#method-parityspacegenerator-__init__)

##### `_compute_parity_matrices(self)`

Compute parity space matrices.

[View full source →](#method-parityspacegenerator-_compute_parity_matrices)

##### `generate_residual(self, data, system_model)`

Generate parity space residual.

[View full source →](#method-parityspacegenerator-generate_residual)

##### `reset(self)`

Reset parity space generator state.

[View full source →](#method-parityspacegenerator-reset)



### `ParameterEstimationGenerator`

**Inherits from:** `ResidualGenerator`

Parameter estimation-based residual generator.

#### Source Code

```{literalinclude} ../../../src/analysis/fault_detection/residual_generators.py
:language: python
:pyobject: ParameterEstimationGenerator
:linenos:
```

#### Methods (4)

##### `__init__(self, config, nominal_parameters)`

Initialize parameter estimation generator.

[View full source →](#method-parameterestimationgenerator-__init__)

##### `generate_residual(self, data, system_model)`

Generate parameter estimation residual.

[View full source →](#method-parameterestimationgenerator-generate_residual)

##### `_estimate_parameters(self, states, controls, times)`

Estimate parameters from data window.

[View full source →](#method-parameterestimationgenerator-_estimate_parameters)

##### `reset(self)`

Reset parameter estimation state.

[View full source →](#method-parameterestimationgenerator-reset)



### `AdaptiveResidualGenerator`

**Inherits from:** `ResidualGenerator`

Adaptive residual generator that combines multiple methods.

#### Source Code

```{literalinclude} ../../../src/analysis/fault_detection/residual_generators.py
:language: python
:pyobject: AdaptiveResidualGenerator
:linenos:
```

#### Methods (4)

##### `__init__(self, generators, weights)`

Initialize adaptive generator.

[View full source →](#method-adaptiveresidualgenerator-__init__)

##### `generate_residual(self, data, system_model)`

Generate adaptive residual by combining multiple methods.

[View full source →](#method-adaptiveresidualgenerator-generate_residual)

##### `_combine_residuals(self, residuals)`

Combine residuals from multiple generators.

[View full source →](#method-adaptiveresidualgenerator-_combine_residuals)

##### `reset(self)`

Reset all generators.

[View full source →](#method-adaptiveresidualgenerator-reset)



### `ResidualGeneratorFactory`

Factory class for creating residual generators.

This class provides a unified interface for creating different types of
residual generators used in fault detection systems.

#### Source Code

```{literalinclude} ../../../src/analysis/fault_detection/residual_generators.py
:language: python
:pyobject: ResidualGeneratorFactory
:linenos:
```

#### Methods (4)

##### `create_generator(method, config)`

Create a residual generator of the specified type.

[View full source →](#method-residualgeneratorfactory-create_generator)

##### `get_available_methods()`

Get list of available residual generation methods.

[View full source →](#method-residualgeneratorfactory-get_available_methods)

##### `create_default_observer(cls, A, C)`

Create observer-based generator with default configuration.

[View full source →](#method-residualgeneratorfactory-create_default_observer)

##### `create_default_kalman(cls, A, B, C, D)`

Create Kalman filter generator with default configuration.

[View full source →](#method-residualgeneratorfactory-create_default_kalman)



## Functions

### `create_residual_generator(method, config)`

Factory function to create residual generators.

Parameters
----------
method : str
    Type of generator ('observer', 'kalman', 'parity', 'parameter_estimation', 'adaptive')
config : ResidualGeneratorConfig, optional
    Configuration parameters
**kwargs
    Additional parameters specific to each method

Returns
-------
ResidualGenerator
    Configured residual generator

#### Source Code

```{literalinclude} ../../../src/analysis/fault_detection/residual_generators.py
:language: python
:pyobject: create_residual_generator
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `from typing import Dict, List, Optional, Tuple, Any, Protocol, Callable`
- `import numpy as np`
- `from scipy import linalg, signal`
- `import warnings`
- `from dataclasses import dataclass, field`
- `from abc import ABC, abstractmethod`
- `from ..core.interfaces import DataProtocol`
