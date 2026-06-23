# utils.visualization.legacy_visualizer

**Source:** `src\utils\visualization\legacy_visualizer.py`

## Module Overview

Utility for visualising a double–inverted-pendulum simulation.

The `Visualizer` animates cart-pole motion and **returns** the
`matplotlib.animation.FuncAnimation` object so callers (e.g. Streamlit
or a Jupyter notebook) can decide how to display or save it.

## Complete Source Code

```{literalinclude} ../../../src/utils/visualization/legacy_visualizer.py
:language: python
:linenos:
```



## Classes

### `Visualizer`

Animate a controlled double–inverted pendulum.

#### Source Code

```{literalinclude} ../../../src/utils/visualization/legacy_visualizer.py
:language: python
:pyobject: Visualizer
:linenos:
```

#### Methods (6)

##### `__init__(self, pendulum_model)`

[View full source →](#method-visualizer-__init__)

##### `_calculate_positions(self, state)`

[View full source →](#method-visualizer-_calculate_positions)

##### `animate(self, time_history, state_history, control_history, dt)`

Creates **and returns** the animation object.

[View full source →](#method-visualizer-animate)

##### `save_animation(self, filename)`

Save the animation to file.

[View full source →](#method-visualizer-save_animation)

##### `save_static_plot(self, state_history, filename, time_step)`

Save a static snapshot of the pendulum at a specific time step.

[View full source →](#method-visualizer-save_static_plot)

##### `create_phase_plot(self, state_history, filename)`

Create phase space plots for the pendulum angles.

[View full source →](#method-visualizer-create_phase_plot)



## Dependencies

This module imports:

- `import matplotlib.animation as animation`
- `import matplotlib.pyplot as plt`
- `import numpy as np`
- `from typing import List, Tuple`


## Architecture Diagram

```{mermaid}
graph TD
    A[Component] --> B[Subcomponent 1]
    A --> C[Subcomponent 2]
    B --> D[Output]
    C --> D

    style A fill:#e1f5ff
    style D fill:#e8f5e9
```


## Usage Examples

### Example 1: Basic Usage

```python
# Basic usage example
from src.utils import Component

component = Component()
result = component.process(data)
```

## Example 2: Advanced Configuration

```python
# Advanced configuration
component = Component(
    option1=value1,
    option2=value2
)
```

## Example 3: Integration with Framework

```python
# Integration example
from src.simulation import SimulationRunner

runner = SimulationRunner()
runner.use_component(component)
```

## Example 4: Performance Optimization

```python
# Performance-optimized usage
component = Component(enable_caching=True)
```

## Example 5: Error Handling

```python
# Error handling
try:
    result = component.process(data)
except ComponentError as e:
    print(f"Error: {e}")
```
