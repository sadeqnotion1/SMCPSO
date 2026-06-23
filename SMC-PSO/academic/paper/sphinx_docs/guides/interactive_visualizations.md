# Interactive Visualizations Guide

This guide demonstrates how to embed interactive Chart.js visualizations in DIP_SMC_PSO documentation using custom Sphinx directives.

## Overview

The `chartjs_extension` provides three specialized directives for interactive charts:

1. **`chartjs`** - General-purpose Chart.js directive
2. **`controller-comparison`** - Specialized controller performance comparison
3. **`pso-convergence`** - PSO optimization convergence visualization

## Installation

The Chart.js extension is automatically loaded via `docs/conf.py`. No additional installation required.

## General Chart.js Directive

The `chartjs` directive allows embedding any Chart.js chart type with full configuration control.

### Basic Usage

```rst
.. chartjs::
   :type: line
   :height: 400
   :title: Sample Line Chart

   {
       "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
       "datasets": [{
           "label": "Sales",
           "data": [12, 19, 3, 5, 2],
           "borderColor": "rgb(75, 192, 192)",
           "tension": 0.1
       }]
   }
```

### Live Example: Controller Performance Over Time

```{eval-rst}
.. chartjs::
   :type: line
   :height: 300
   :title: Controller Response Time Comparison
   :responsive:

   {
       "labels": [0, 1, 2, 3, 4, 5],
       "datasets": [
           {
               "label": "Classical SMC",
               "data": [0, 0.5, 0.9, 0.98, 1.0, 1.0],
               "borderColor": "rgba(54, 162, 235, 1)",
               "backgroundColor": "rgba(54, 162, 235, 0.2)",
               "borderWidth": 2,
               "fill": true
           },
           {
               "label": "Adaptive SMC",
               "data": [0, 0.7, 0.95, 0.99, 1.0, 1.0],
               "borderColor": "rgba(255, 99, 132, 1)",
               "backgroundColor": "rgba(255, 99, 132, 0.2)",
               "borderWidth": 2,
               "fill": true
           }
       ]
   }
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `:type:` | string | `line` | Chart type: line, bar, radar, pie, doughnut, polarArea, bubble, scatter |
| `:data:` | path | - | Path to JSON data file (alternative to inline data) |
| `:height:` | int | 400 | Chart height in pixels |
| `:width:` | string | `100%` | Chart width (CSS value) |
| `:title:` | string | - | Chart title |
| `:responsive:` | flag | - | Enable responsive sizing |
| `:animation:` | flag | enabled | Enable chart animations |

## Controller Comparison Directive

Specialized directive for comparing controller performance metrics.

### Usage

```rst
.. controller-comparison::
   :metric: settling_time
   :controllers: classical_smc,adaptive_smc,hybrid_smc,terminal_smc
   :height: 400
```

### Live Example: Settling Time Comparison

```{eval-rst}
.. controller-comparison::
   :metric: settling_time
   :controllers: classical_smc,adaptive_smc,hybrid_smc
   :height: 350
```

### Supported Metrics

- `settling_time` - Settling Time (s)
- `overshoot` - Overshoot (%)
- `steady_state_error` - Steady-State Error
- `rise_time` - Rise Time (s)
- `control_effort` - Control Effort

### Controller Types

- `classical_smc` - Classical Sliding Mode Control
- `adaptive_smc` - Adaptive SMC with gain adaptation
- `hybrid_smc` - Hybrid Adaptive STA-SMC
- `terminal_smc` - Terminal Sliding Mode Control

## PSO Convergence Directive

Visualize PSO optimization convergence behavior.

### Usage

```rst
.. pso-convergence::
   :iterations: 100
   :particles: 30
   :height: 400
```

### Live Example: PSO Optimization Progress

```{eval-rst}
.. pso-convergence::
   :iterations: 50
   :particles: 20
   :height: 350
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `:iterations:` | int | 100 | Number of PSO iterations |
| `:particles:` | int | 30 | Number of particles in swarm |
| `:height:` | int | 400 | Chart height in pixels |

## Advanced Examples

### Multi-Dataset Bar Chart

```{eval-rst}
.. chartjs::
   :type: bar
   :height: 350
   :title: Controller Performance Metrics
   :responsive:

   {
       "labels": ["Settling Time", "Overshoot", "Control Effort"],
       "datasets": [
           {
               "label": "Classical SMC",
               "data": [2.5, 15, 80],
               "backgroundColor": "rgba(54, 162, 235, 0.7)"
           },
           {
               "label": "Adaptive SMC",
               "data": [1.8, 8, 65],
               "backgroundColor": "rgba(255, 99, 132, 0.7)"
           },
           {
               "label": "Hybrid SMC",
               "data": [1.2, 5, 55],
               "backgroundColor": "rgba(75, 192, 192, 0.7)"
           }
       ]
   }
```

### Radar Chart: Controller features

```{eval-rst}
.. chartjs::
   :type: radar
   :height: 400
   :title: Controller Capability Profile
   :responsive:

   {
       "labels": ["Stability", "Robustness", "Speed", "Precision", "Efficiency"],
       "datasets": [
           {
               "label": "Classical SMC",
               "data": [7, 8, 6, 7, 9],
               "borderColor": "rgba(54, 162, 235, 1)",
               "backgroundColor": "rgba(54, 162, 235, 0.2)",
               "borderWidth": 2
           },
           {
               "label": "Hybrid Adaptive STA-SMC",
               "data": [9, 9, 8, 9, 7],
               "borderColor": "rgba(75, 192, 192, 1)",
               "backgroundColor": "rgba(75, 192, 192, 0.2)",
               "borderWidth": 2
           }
       ]
   }
```

## Loading Data from Files

For large datasets or reusable data, use the `:data:` option:

**File: `docs/_data/performance_data.json`**
```json
{
    "labels": ["0s", "1s", "2s", "3s", "4s", "5s"],
    "datasets": [{
        "label": "Position Error",
        "data": [1.0, 0.5, 0.2, 0.05, 0.01, 0.0],
        "borderColor": "rgb(75, 192, 192)"
    }]
}
```

**Usage in documentation:**
```rst
.. chartjs::
   :type: line
   :data: _data/performance_data.json
   :title: Position Error Convergence
```

## Integration with Simulation Results

The directives can be integrated with actual simulation data by updating the Chart.js configuration to load from simulation output files:

```python
# In simulation script
import json

results = run_simulation(controller, duration=5.0)
chart_data = {
    "labels": results['time'].tolist(),
    "datasets": [{
        "label": "Theta1",
        "data": results['theta1'].tolist()
    }]
}

with open('docs/_data/sim_results.json', 'w') as f:
    json.dump(chart_data, f)
```

Then reference in documentation:
```rst
.. chartjs::
   :type: line
   :data: _data/sim_results.json
   :title: Simulation Results: Theta1 vs Time
```

## Styling and Customization

Charts inherit Furo theme colors automatically. For custom styling, extend the Chart.js configuration:

```rst
.. chartjs::
   :type: line
   :height: 300

   {
       "data": {
           "labels": [1, 2, 3],
           "datasets": [{"data": [10, 20, 30]}]
       },
       "options": {
           "plugins": {
               "legend": {
                   "position": "bottom",
                   "labels": {
                       "font": {
                           "size": 14,
                           "family": "'Helvetica Neue', sans-serif"
                       }
                   }
               }
           },
           "scales": {
               "y": {
                   "title": {
                       "display": true,
                       "text": "Custom Y Label"
                   }
               }
           }
       }
   }
```

## Best Practices

1. **Keep JSON readable**: Use proper indentation in inline data
2. **Use external files for large datasets**: Improves doc maintainability
3. **Set appropriate heights**: 300-400px for most charts
4. **Enable responsive mode**: Better mobile experience
5. **Provide context**: Add explanatory text before/after charts
6. **Use semantic colors**: Match controller types to consistent colors
7. **Test rendering**: Build docs locally to verify chart display

## Troubleshooting

### Chart Not Displaying

- Verify JSON syntax is valid (use online validator)
- Check browser console for JavaScript errors
- Ensure Chart.js CDN is loading (check network tab)

### Data Not Updating

- Clear browser cache
- Rebuild documentation: `cd docs && make clean && make html`
- Verify data file path is correct (relative to docs/)

### Performance Issues

- Limit data points to <1000 for responsive performance
- Disable animations for large datasets: remove `:animation:` flag
- Use aggregated data for overview charts

## References

- [Chart.js Official Documentation](https://www.chartjs.org/docs/latest/)
- [Sphinx Custom Directives Guide](https://www.sphinx-doc.org/en/master/development/tutorials/helloworld.html)
- [DIP_SMC_PSO Controller Documentation](../reference/controllers/index.md)
- [PSO Optimization Workflow](workflows/pso-optimization-workflow.md)
