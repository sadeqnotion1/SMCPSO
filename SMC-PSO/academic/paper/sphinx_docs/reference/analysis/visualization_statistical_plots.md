# analysis.visualization.statistical_plots

**Source:** `src\analysis\visualization\statistical_plots.py`

## Module Overview Statistical

visualization module for control system analysis

.

## Advanced Mathematical Theory

### Statistical Visualization


\begin{align}
Q_1 &= \text{25th percentile} \\
Q_2 &= \text{median (50th)} \\
Q_3 &= \text{75th percentile} \\
\text{IQR} &= Q_3 - Q_1 \\
\text{Whiskers} &= [Q_1 - 1.5\cdot\text{IQR}, Q_3 + 1.5\cdot\text{IQR}]
\end{align}
``` ### Violin Plot **Kernel density estimate:** ```{math}
\hat{f}(x) = \frac{1}{nh}\sum_{i=1}^n K\left(\frac{x - x_i}{h}\right)
``` Where $K$ is kernel (e.g., Gaussian), $h$ is bandwidth. **Bandwidth selection (Silverman's rule):** ```{math}

h = 0.9 \min\left(\sigma, \frac{\text{IQR}}{1.34}\right) n^{-1/5}
``` ### Histogram Theory **Bin width selection (Freedman-Diaconis):** ```{math}
w = 2 \frac{\text{IQR}}{n^{1/3}}
``` **Number of bins:** ```{math}

k = \left\lceil \frac{\max(x) - \min(x)}{w} \right\rceil
``` ### Q-Q Plot **Quantile-Quantile plot:** ```{math}
\text{Plot: } (F^{-1}(p_i), x_{(i)})
``` Where $F^{-1}$ is theoretical quantile function, $x_{(i)}$ are ordered data. ## Architecture Diagram ```{mermaid}

graph TD A[Statistical Data] --> B{Plot Type} B -->|Box Plot| C[Quartiles] B -->|Violin| D[KDE] B -->|Histogram| E[Binning] B -->|Q-Q| F[Quantiles] C --> G[Whiskers] G --> H[Outliers] D --> I[Bandwidth Selection] I --> J[Density Curve] E --> K[Bin Width] K --> L[Frequency Count] F --> M[Theoretical Quantiles] M --> N[Comparison Line] H --> O[Statistical Plot] J --> O L --> O N --> O style I fill:#9cf style K fill:#ff9 style O fill:#9f9
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

This module provides specialized plotting features for statistical analysis
of control system data, including distribution analysis, hypothesis test results,
and Monte Carlo simulation visualizations. ## Complete Source Code ```{literalinclude} ../../../src/analysis/visualization/statistical_plots.py
:language: python
:linenos:
```

---

## Classes

### `StatisticalPlotter`

Advanced statistical plotting for control system analysis.

#### Source Code ```

{literalinclude} ../../../src/analysis/visualization/statistical_plots.py
:language: python
:pyobject: StatisticalPlotter
:linenos:
``` #### Methods (7) ##### `__init__(self, style, figsize)` Initialize statistical plotter with scientific styling. [View full source →](#method-statisticalplotter-__init__) ##### `_setup_style(self)` Configure matplotlib style for scientific plots. [View full source →](#method-statisticalplotter-_setup_style) ##### `plot_distribution_analysis(self, data, title, theoretical_dist, save_path)` Create distribution analysis plot. [View full source →](#method-statisticalplotter-plot_distribution_analysis) ##### `plot_hypothesis_test_results(self, test_results, title, save_path)` Visualize hypothesis test results. [View full source →](#method-statisticalplotter-plot_hypothesis_test_results) ##### `plot_monte_carlo_results(self, simulation_results, confidence_levels, title, save_path)` Visualize Monte Carlo simulation results. [View full source →](#method-statisticalplotter-plot_monte_carlo_results) ##### `plot_correlation_matrix(self, data, labels, method, title, save_path)` Create correlation matrix heatmap. [View full source →](#method-statisticalplotter-plot_correlation_matrix) ##### `plot_convergence_analysis(self, convergence_data, title, save_path)` Plot convergence behavior of iterative algorithms. [View full source →](#method-statisticalplotter-plot_convergence_analysis)

---

## Dependencies This module imports: - `import matplotlib.pyplot as plt`

- `import matplotlib.patches as patches`
- `import numpy as np`
- `import pandas as pd`
- `from scipy import stats`
- `from typing import Dict, List, Optional, Tuple, Any, Union`
- `import warnings`
- `from ..core.interfaces import DataProtocol`
- `from ..core.data_structures import MetricResult`
