# Jupyter Notebooks Integration

**Run complete Jupyter notebooks within documentation** - execute cells, interact with widgets, and explore results without leaving the docs.

This page demonstrates all Jupyter integration features available in Phase 4 of the interactive documentation system.

---

## Feature Overview

Phase 4 brings three powerful Jupyter directives:

1. **`jupyter-notebook`**: Embed full notebooks with execution caching
2. **`jupyter-cell`**: Inline code cells for quick demonstrations
3. **`jupyter-widget`**: Interactive controls (sliders, dropdowns, buttons)

All features support:
- **Execution caching** for fast rebuilds
- **Syntax highlighting** with Pygments
- **Error handling** with clear messages
- **Dark mode** styling

---

## 1. Full Notebook Embedding

The `jupyter-notebook` directive embeds complete Jupyter notebooks:

```rst
.. jupyter-notebook::
   :path: docs/tutorials/notebooks/01_getting_started.ipynb
   :execute: auto
   :show-cells: all
```

### Example: Getting Started Notebook

```{eval-rst}
.. jupyter-notebook::
   :path: docs/tutorials/notebooks/01_getting_started.ipynb
   :execute: auto
   :show-cells: 0-5
   :hide-output:
```

**Features:**
- Selective cell display (`:show-cells: 0,2,5-8`)
- Hide input (`:hide-input:`) or output (`:hide-output:`)
- Custom execution timeout (`:timeout: 60`)
- Execution caching with custom keys (`:cache-key: demo-01`)

---

## 2. Inline Code Cells

The `jupyter-cell` directive executes individual code cells:

### Example: Basic Calculation

```{eval-rst}
.. jupyter-cell::
   :kernel: python3
   :cache-key: demo-basic-calc
   :linenos:

   import numpy as np
   from scipy.integrate import odeint

   # Simple pendulum dynamics
   def pendulum(y, t, b, c):
       theta, omega = y
       dydt = [omega, -b*omega - c*np.sin(theta)]
       return dydt

   # Solve ODE
   y0 = [np.pi - 0.1, 0.0]
   t = np.linspace(0, 10, 100)
   sol = odeint(pendulum, y0, t, args=(0.25, 5.0))

   print(f"Pendulum simulation complete!")
   print(f"Final angle: {sol[-1, 0]:.4f} rad")
   print(f"Final velocity: {sol[-1, 1]:.4f} rad/s")
```

### Example: Controller Gain Calculation

```{eval-rst}
.. jupyter-cell::
   :cache-key: demo-gain-calc
   :name: SMC Gain Calculator

   import numpy as np

   # SMC sliding surface coefficients
   c = np.array([10.0, 5.0, 8.0, 3.0])

   # Calculate gain bounds
   eta = 0.1  # Boundary layer thickness
   K_min = np.linalg.norm(c) * eta
   K_max = np.linalg.norm(c) * eta * 10

   print("SMC Gain Bounds:")
   print(f"  Minimum K: {K_min:.3f}")
   print(f"  Maximum K: {K_max:.3f}")
   print(f"  Recommended K: {(K_min + K_max) / 2:.3f}")
```

**Features:**
- Line numbering (`:linenos:`)
- Named cells (`:name: Cell Name`)
- Hide input/output selectively
- Execution caching for fast rebuilds

---

## 3. Interactive Widgets

The `jupyter-widget` directive creates interactive controls:

### Example: Slider Widget

```{eval-rst}
.. jupyter-widget::
   :widget-type: slider
   :label: Controller Gain (K)
   :min: 0
   :max: 100
   :step: 1
   :default: 50
   :callback: updateControllerGain
   :description: Adjust the SMC switching gain to see its effect on control performance
```

### Example: Controller Selector

```{eval-rst}
.. jupyter-widget::
   :widget-type: dropdown
   :label: Controller Type
   :options: classical_smc, sta_smc, adaptive_smc, hybrid_smc
   :default: classical_smc
   :callback: selectController
   :description: Choose which controller to simulate
```

### Example: Simulation Button

```{eval-rst}
.. jupyter-widget::
   :widget-type: button
   :label: Run Simulation
   :callback: runSimulation
   :description: Click to execute the simulation with current parameters
```

### Example: Parameter Checkbox

```{eval-rst}
.. jupyter-widget::
   :widget-type: checkbox
   :label: Enable Chattering Reduction
   :default: true
   :callback: toggleChatteringReduction
```

**Widget Types:**
- **Slider**: Continuous numerical input
- **Dropdown**: Select from predefined options
- **Button**: Trigger actions
- **Checkbox**: Boolean toggle
- **Text**: Free-form text input

---

## 4. Advanced Features

### Execution Caching

All directives support execution caching for fast rebuilds:

```rst
.. jupyter-cell::
   :cache-key: expensive-computation-001

   # This code is cached - rebuilds are instant!
   import numpy as np
   result = np.linalg.eig(np.random.rand(1000, 1000))
```

**Cache Benefits:**
- **Fast rebuilds**: Cached cells execute instantly
- **Consistent results**: Same output across builds
- **Smart invalidation**: Cache updates when code changes

### Error Handling

Cells can continue execution on errors:

```rst
.. jupyter-notebook::
   :path: docs/tutorials/notebooks/experimental.ipynb
   :allow-errors:
```

### Selective Display

Show only specific cells from notebooks:

```rst
.. jupyter-notebook::
   :path: docs/tutorials/notebooks/tutorial.ipynb
   :show-cells: 0,2,5-8,12
   :hide-input:
```

**Use Cases:**
- Show only results (`:hide-input:`)
- Display code without outputs (`:hide-output:`)
- Focus on specific sections (`:show-cells:`)

---

## 5. Integration Examples

### Tutorial Integration

Combine notebooks with narrative documentation:

```rst
First, let's set up the controller:

.. jupyter-cell::
   :cache-key: tutorial-setup

   from src.controllers.factory import create_controller
   controller = create_controller('classical_smc')

Now adjust the gain:

.. jupyter-widget::
   :widget-type: slider
   :label: Gain
   :min: 0
   :max: 100

Run the simulation:

.. jupyter-widget::
   :widget-type: button
   :label: Simulate
```

### API Documentation

Execute examples inline:

```rst
## ControllerFactory.create_controller()

Example usage:

.. jupyter-cell::

   from src.controllers.factory import create_controller
   ctrl = create_controller('sta_smc', gains=[10, 5, 8])
   print(f"Controller created: {ctrl.__class__.__name__}")
```

---

## Technical Details

### Execution Environment

- **Kernel**: Python 3.12 with Jupyter
- **Packages**: Full project environment (NumPy, SciPy, Matplotlib, etc.)
- **Isolation**: Each cell executes in persistent kernel
- **Timeout**: 30 seconds per cell (configurable)

### Cache System

```python
# Cache stored in docs/_build/html/_jupyter_cache/
cache = {
    'cell-hash': {
        'status': 'success',
        'stdout': 'Output text',
        'execution_count': 1,
    }
}
```

**Cache Invalidation:**
- Code content changes
- Kernel version changes
- Manual cache clear

### Performance

| Operation | Time |
|-----------|------|
| First execution | 1-5 seconds |
| Cached execution | <10ms |
| Full notebook | 5-30 seconds |
| Widget interaction | Instant |

---

## Best Practices

### When to Use Each Directive

**Use `jupyter-notebook` for:**
- Complete tutorial workflows
- Multi-step analyses
- Reproducible research

**Use `jupyter-cell` for:**
- Quick code demonstrations
- API examples
- Inline calculations

**Use `jupyter-widget` for:**
- Parameter exploration
- Interactive tutorials
- User experiments

### Performance Tips

1. **Use caching**: Always provide `:cache-key:` for expensive cells
2. **Limit cell output**: Avoid printing large arrays
3. **Hide unnecessary**: Use `:hide-input:` or `:hide-output:` when appropriate
4. **Timeout wisely**: Set realistic `:timeout:` values

### Accessibility

- All widgets have keyboard navigation
- Screen reader compatible labels
- High contrast styling
- Mobile-responsive layout

---

## Comparison with Other Features

| Feature | Phase 2: Pyodide | Phase 3: Plotly | Phase 4: Jupyter |
|---------|------------------|-----------------|------------------|
| **Execution** | Browser (WASM) | N/A (pre-rendered) | Server (build time) |
| **Performance** | 50-70% native | Instant | 100% native |
| **Packages** | Limited | N/A | Full environment |
| **Caching** | Browser LocalStorage | N/A | Pickle on disk |
| **Widgets** | Limited | Interactive charts | Full ipywidgets |

---

## Examples Gallery

Explore these pages using Jupyter integration:

1. **[Tutorial 01: First Simulation](../tutorials/tutorial-01-first-simulation.md)** - Interactive setup
2. **[Controller Comparison](../tutorials/tutorial-02-controller-comparison.md)** - Side-by-side execution
3. **[PSO Optimization](../tutorials/tutorial-03-pso-optimization.md)** - Live optimization

---

## Troubleshooting

### Notebook not found

**Error:** `jupyter-notebook: Notebook not found: path/to/notebook.ipynb`

**Solution:** Check path is relative to `docs/` directory or use absolute path.

### Execution timeout

**Error:** Cell execution exceeded 30 seconds

**Solution:** Increase timeout with `:timeout: 60` or simplify computation.

### Cache stale

**Problem:** Changes not reflected in output

**Solution:** Clear cache directory: `rm -rf docs/_build/html/_jupyter_cache/`

---

## Next Steps

- **[Create Custom Notebooks](../../tutorials/tutorial-04-custom-controller.md)**
- **[Widget Development Guide](../../api/widgets-api.md)** (Coming soon)
- **[Jupyter Best Practices](../../guides/jupyter-best-practices.md)** (Coming soon)

---

**[AI] Generated with Claude Code**
**Phase 4**: Jupyter Notebooks Integration
