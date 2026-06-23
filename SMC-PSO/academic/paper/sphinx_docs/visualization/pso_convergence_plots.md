# PSO Convergence Visualization

> **Note:** PSO convergence plotting is covered in multiple guides.

## Quick Links

- **[PSO Optimization Workflow](../guides/workflows/pso-optimization-workflow.md)** - PSO optimization guide with visualization examples
- **[Interactive Visualizations](../guides/interactive_visualizations.md)** - Interactive plotting features
- **[Analysis Plots](../reference/analysis/visualization_analysis_plots.md)** - Analysis visualization API

## Creating PSO Convergence Plots

See the PSO Optimization Workflow guide for complete examples of convergence visualization including:
- Best fitness over iterations
- Swarm diversity plots
- Parameter convergence tracking
- Multi-objective Pareto fronts

Example usage:
```python
# See: guides/workflows/pso-optimization-workflow.md for complete examples
from src.optimization import PSOTuner

tuner = PSOTuner(...)
results = tuner.optimize()

# Convergence plotting examples in the workflow guide
```



**Redirect:** See `guides/workflows/pso-optimization-workflow.md` for PSO visualization
