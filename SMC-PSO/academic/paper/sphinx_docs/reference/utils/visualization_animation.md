# utils.visualization.animation

**Source:** `src\utils\visualization\animation.py`

## Module Overview

Animation utilities for dynamic system visualization.

Provides real-time and recorded animation features for the double
inverted pendulum and control system visualization.

## Complete Source Code

```{literalinclude} ../../../src/utils/visualization/animation.py
:language: python
:linenos:
```



## Classes

### `DIPAnimator`

Animate a controlled double inverted pendulum.

#### Source Code

```{literalinclude} ../../../src/utils/visualization/animation.py
:language: python
:pyobject: DIPAnimator
:linenos:
```

#### Methods (6)

##### `__init__(self, pendulum_model, figsize)`

Initialize the animator with pendulum model.

[View full source →](#method-dipanimator-__init__)

##### `_setup_plot(self)`

Setup the plot appearance and elements.

[View full source →](#method-dipanimator-_setup_plot)

##### `_calculate_positions(self, state)`

Calculate positions of cart and pendulum ends.

[View full source →](#method-dipanimator-_calculate_positions)

##### `animate_frame(self, frame_data)`

Animate a single frame.

[View full source →](#method-dipanimator-animate_frame)

##### `create_animation(self, state_history, control_history, time_history, interval)`

Create animation from simulation data.

[View full source →](#method-dipanimator-create_animation)

##### `save_animation(self, state_history, control_history, time_history, filename, fps)`

Save animation to file.

[View full source →](#method-dipanimator-save_animation)



### `MultiSystemAnimator`

Animate multiple systems or comparison scenarios.

#### Source Code

```{literalinclude} ../../../src/utils/visualization/animation.py
:language: python
:pyobject: MultiSystemAnimator
:linenos:
```

#### Methods (2)

##### `__init__(self, num_systems, figsize)`

Initialize multi-system animator.

[View full source →](#method-multisystemanimator-__init__)

##### `create_comparison_animation(self, systems_data, interval)`

Create comparison animation for multiple systems.

[View full source →](#method-multisystemanimator-create_comparison_animation)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import matplotlib.animation as animation`
- `import matplotlib.pyplot as plt`
- `import numpy as np`
- `from typing import List, Tuple, Optional, Callable`
- `from matplotlib.patches import FancyArrowPatch, Rectangle`


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
