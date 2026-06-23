# analysis.visualization.diagnostic_plots

**Source:** `src\analysis\visualization\diagnostic_plots.py`

## Module Overview Diagnostic

visualization module for control system analysis

.

## Advanced Mathematical Theory

### Diagnostic Visualization


r_i(t) = y_i(t) - \hat{y}_i(t)
``` **Autocorrelation function:** ```{math}
\rho(\tau) = \frac{E[(r_t - \mu)(r_{t+\tau} - \mu)]}{\sigma^2}
``` Ideal: $\rho(\tau) \approx 0$ for $\tau > 0$ (white noise). ### Multi-Dimensional Visualization **Principal Component Analysis (PCA):** ```{math}

\mathbf{Y} = \mathbf{X}\mathbf{W}
``` Project high-dim data to 2D/3D for visualization. **t-SNE embedding:** ```{math}
p_{j|i} = \frac{\exp(-\|\vec{x}_i - \vec{x}_j\|^2/2\sigma_i^2)}{\sum_k \exp(-\|\vec{x}_i - \vec{x}_k\|^2/2\sigma_i^2)}
``` ### Heatmap Theory **Correlation matrix visualization:** ```{math}

C_{ij} = \frac{\text{cov}(x_i, x_j)}{\sigma_i \sigma_j}
``` **Color mapping:** ```{math}
\text{color}(C_{ij}) = f(C_{ij}), \quad f: [-1, 1] \to \text{colormap}
``` ## Architecture Diagram ```{mermaid}

graph TD A[Diagnostic Data] --> B[Residual Plots] A --> C[Autocorrelation] A --> D[Heatmaps] B --> E[Time Series] E --> F[Threshold Lines] C --> G[ACF Computation] G --> H[Confidence Bands] D --> I[Correlation Matrix] I --> J[Color Mapping] F --> K[Fault Indicators] H --> K J --> K K --> L[Diagnostic Report] style K fill:#9cf style L fill:#9f9
``` ## Usage Examples ### Example 1: Basic Initialization ```python
from src.analysis import Component # Initialize component
component = Component(config)
result = component.process(data)
``` ### Example 2: Advanced Configuration ```python
# Configure with custom parameters

config = { 'threshold': 0.05, 'method': 'adaptive'
}
component = Component(config)
``` ### Example 3: Integration Workflow ```python
# Complete analysis workflow
from src.analysis import analyze results = analyze( data=sensor_data, method='enhanced', visualization=True
)
``` ### Example 4: Fault Detection Example ```python
# FDI system usage

from src.analysis.fault_detection import FDISystem fdi = FDISystem(config)
residual = fdi.generate_residual(y, u)
fault = fdi.detect(residual)
``` ### Example 5: Visualization Example ```python
# Generate analysis plots
from src.analysis.visualization import AnalysisPlotter plotter = AnalysisPlotter(style='professional')
fig = plotter.plot_time_series(data)
fig.savefig('analysis.pdf')
```

This module provides specialized plotting features for control system diagnostics,
including time-domain analysis, frequency-domain analysis, phase portraits,
and control performance visualization. ## Complete Source Code ```{literalinclude} ../../../src/analysis/visualization/diagnostic_plots.py
:language: python
:linenos:
```

---

## Classes

### `DiagnosticPlotter`

Specialized diagnostic plotting for control systems.

#### Source Code ```

{literalinclude} ../../../src/analysis/visualization/diagnostic_plots.py
:language: python
:pyobject: DiagnosticPlotter
:linenos:
``` #### Methods (7) ##### `__init__(self, style, figsize)` Initialize diagnostic plotter with control engineering styling. [View full source →](#method-diagnosticplotter-__init__) ##### `_setup_style(self)` Configure matplotlib style for control engineering plots. [View full source →](#method-diagnosticplotter-_setup_style) ##### `plot_time_response(self, simulation_data, variables, title, save_path)` Plot time-domain response analysis. [View full source →](#method-diagnosticplotter-plot_time_response) ##### `plot_phase_portrait(self, simulation_data, state_pairs, title, save_path)` Create phase portrait plots for nonlinear system analysis. [View full source →](#method-diagnosticplotter-plot_phase_portrait) ##### `plot_frequency_analysis(self, simulation_data, signal_indices, title, save_path)` Perform frequency domain analysis of system signals. [View full source →](#method-diagnosticplotter-plot_frequency_analysis) ##### `plot_control_performance(self, performance_metrics, title, save_path)` Visualize control performance metrics. [View full source →](#method-diagnosticplotter-plot_control_performance) ##### `_estimate_settling_time(self, time, signal, tolerance)` Estimate settling time of a signal. [View full source →](#method-diagnosticplotter-_estimate_settling_time)

---

## Dependencies This module imports: - `import matplotlib.pyplot as plt`

- `import numpy as np`
- `import pandas as pd`
- `from scipy import signal, fft`
- `from typing import Dict, List, Optional, Tuple, Any, Union`
- `import warnings`
- `from ..core.interfaces import DataProtocol`
- `from ..core.data_structures import SimulationData, PerformanceMetrics`
