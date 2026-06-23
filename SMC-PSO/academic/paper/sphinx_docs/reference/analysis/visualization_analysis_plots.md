# analysis.visualization.analysis_plots

**Source:** `src\analysis\visualization\analysis_plots.py`

## Module Overview Analysis

visualization tools for control engineering applications

.

## Advanced Mathematical Theory

### Visualization Theory


S = k \ln(I/I_0)
``` Sensation $S$ proportional to log of intensity $I$. ### Color Theory (CIELAB) **Perceptually uniform color space:** ```{math}
\begin{align}
L^* &= 116f(Y/Y_n) - 16 \\
a^* &= 500[f(X/X_n) - f(Y/Y_n)] \\
b^* &= 200[f(Y/Y_n) - f(Z/Z_n)]
\end{align}
``` Where $f(t) = t^{1/3}$ if $t > (6/29)^3$, else linear. ### Time Series Smoothing **Moving average filter:** ```{math}

y_{smooth}(t) = \frac{1}{2w+1}\sum_{i=-w}^{w} y(t+i)
``` **Exponential smoothing:** ```{math}
s_t = \alpha y_t + (1-\alpha)s_{t-1}
``` ### Phase Portrait Theory **State trajectory:** ```{math}

\vec{x}(t) = [x_1(t), x_2(t)], \quad \text{Plot: } (x_1, x_2)
``` **Vector field:** ```{math}
\vec{v}(x_1, x_2) = [\dot{x}_1(x_1, x_2), \dot{x}_2(x_1, x_2)]
``` ### Nyquist Sampling **Anti-aliasing for plotting:** ```{math}

f_s \geq 2f_{max}
``` **Decimation:** Plot every $M$-th point: ```{math}
y_{plot}[n] = y[Mn]
``` ## Architecture Diagram ```{mermaid}

graph TD A[Analysis Data] --> B{Plot Type} B -->|Time Series| C[Line Plot] B -->|Phase Portrait| D[State Trajectory] B -->|Comparison| E[Multi-Line Plot] C --> F[Smoothing] F --> G[Decimation] D --> H[Vector Field] H --> I[Trajectory Overlay] E --> J[Legend] J --> K[Color Palette] G --> L[Style Application] I --> L K --> L L --> M[Figure Generation] M --> N[Export] style L fill:#9cf style M fill:#ff9 style N fill:#9f9
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

This module provides visualization features for analysis results
including performance plots, comparison charts, and interactive visualizations. ## Complete Source Code ```{literalinclude} ../../../src/analysis/visualization/analysis_plots.py
:language: python
:linenos:
```

---

## Classes

### `AnalysisPlotter`

**Inherits from:** `VisualizationGenerator` Professional analysis plotting framework.

#### Source Code ```

{literalinclude} ../../../src/analysis/visualization/analysis_plots.py
:language: python
:pyobject: AnalysisPlotter
:linenos:
``` #### Methods (42) ##### `__init__(self, style, figsize, dpi, color_palette)` Initialize analysis plotter. [View full source →](#method-analysisplotter-__init__) ##### `_setup_style(self)` Setup matplotlib style for professional plots. [View full source →](#method-analysisplotter-_setup_style) ##### `supported_formats(self)` List of supported output formats. [View full source →](#method-analysisplotter-supported_formats) ##### `generate(self, analysis_result)` Generate visualization from analysis results. [View full source →](#method-analysisplotter-generate) ##### `create_summary_plot(self, analysis_result, output_path)` Create summary plot. [View full source →](#method-analysisplotter-create_summary_plot) ##### `create_performance_comparison(self, analysis_result, output_path)` Create performance comparison visualization. [View full source →](#method-analysisplotter-create_performance_comparison) ##### `create_time_series_plot(self, analysis_result, output_path)` Create time series analysis plot. [View full source →](#method-analysisplotter-create_time_series_plot) ##### `create_distribution_plot(self, analysis_result, output_path)` Create distribution analysis plot. [View full source →](#method-analysisplotter-create_distribution_plot) ##### `create_correlation_matrix(self, analysis_result, output_path)` Create correlation matrix visualization. [View full source →](#method-analysisplotter-create_correlation_matrix) ##### `create_control_performance_plot(self, analysis_result, output_path)` Create control-specific performance visualization. [View full source →](#method-analysisplotter-create_control_performance_plot) ##### `_plot_key_metrics(self, ax, data)` Plot key metrics as bar chart. [View full source →](#method-analysisplotter-_plot_key_metrics) ##### `_plot_performance_trends(self, ax, data)` Plot performance trends over time or iterations. [View full source →](#method-analysisplotter-_plot_performance_trends) ##### `_plot_distribution_overview(self, ax, data)` Plot distribution overview. [View full source →](#method-analysisplotter-_plot_distribution_overview) ##### `_plot_quality_indicators(self, ax, data)` Plot quality indicators as gauge-style visualization. [View full source →](#method-analysisplotter-_plot_quality_indicators) ##### `_plot_metric_comparison(self, ax, data)` Plot metric comparison between methods. [View full source →](#method-analysisplotter-_plot_metric_comparison) ##### `_plot_statistical_significance(self, ax, data)` Plot statistical significance results. [View full source →](#method-analysisplotter-_plot_statistical_significance) ##### `_plot_effect_sizes(self, ax, data)` Plot effect sizes. [View full source →](#method-analysisplotter-_plot_effect_sizes) ##### `_plot_time_series_data(self, ax, data)` Plot time series data. [View full source →](#method-analysisplotter-_plot_time_series_data) ##### `_plot_residuals_analysis(self, ax, data)` Plot residuals analysis. [View full source →](#method-analysisplotter-_plot_residuals_analysis) ##### `_plot_frequency_analysis(self, ax, data)` Plot frequency domain analysis. [View full source →](#method-analysisplotter-_plot_frequency_analysis) ##### `_plot_histogram_with_fit(self, ax, data)` Plot histogram with distribution fit. [View full source →](#method-analysisplotter-_plot_histogram_with_fit) ##### `_plot_qq_plot(self, ax, data)` Plot Q-Q plot for normality assessment. [View full source →](#method-analysisplotter-_plot_qq_plot) ##### `_plot_box_plot_analysis(self, ax, data)` Plot box plot with outlier analysis. [View full source →](#method-analysisplotter-_plot_box_plot_analysis) ##### `_plot_density_comparison(self, ax, data)` Plot probability density comparison. [View full source →](#method-analysisplotter-_plot_density_comparison) ##### `_plot_correlation_heatmap(self, ax, data)` Plot correlation heatmap. [View full source →](#method-analysisplotter-_plot_correlation_heatmap) ##### `_plot_correlation_network(self, ax, data)` Plot correlation network diagram. [View full source →](#method-analysisplotter-_plot_correlation_network) ##### `_plot_step_response_analysis(self, ax, data)` Plot step response analysis. [View full source →](#method-analysisplotter-_plot_step_response_analysis) ##### `_plot_frequency_response(self, ax, data)` Plot frequency response. [View full source →](#method-analysisplotter-_plot_frequency_response) ##### `_plot_stability_margins(self, ax, data)` Plot stability margins. [View full source →](#method-analysisplotter-_plot_stability_margins) ##### `_plot_control_effort_analysis(self, ax, data)` Plot control effort analysis. [View full source →](#method-analysisplotter-_plot_control_effort_analysis) ##### `_plot_robustness_analysis(self, ax, data)` Plot robustness analysis. [View full source →](#method-analysisplotter-_plot_robustness_analysis) ##### `_plot_performance_radar(self, ax, data)` Plot performance radar chart. [View full source →](#method-analysisplotter-_plot_performance_radar) ##### `_extract_metrics_from_data(self, data)` Extract metrics from analysis data. [View full source →](#method-analysisplotter-_extract_metrics_from_data) ##### `_extract_time_series_from_data(self, data)` Extract time series data. [View full source →](#method-analysisplotter-_extract_time_series_from_data) ##### `_extract_distribution_data(self, data)` Extract data for distribution analysis. [View full source →](#method-analysisplotter-_extract_distribution_data) ##### `_extract_quality_metrics(self, data)` Extract quality metrics. [View full source →](#method-analysisplotter-_extract_quality_metrics) ##### `_extract_comparison_data(self, data)` Extract comparison data between methods. [View full source →](#method-analysisplotter-_extract_comparison_data) ##### `_extract_significance_data(self, data)` Extract statistical significance data. [View full source →](#method-analysisplotter-_extract_significance_data) ##### `_extract_effect_size_data(self, data)` Extract effect size data. [View full source →](#method-analysisplotter-_extract_effect_size_data) ##### `_extract_residuals_data(self, data)` Extract residuals data. [View full source →](#method-analysisplotter-_extract_residuals_data) ##### `_extract_frequency_data(self, data)` Extract frequency domain data. [View full source →](#method-analysisplotter-_extract_frequency_data) ##### `_extract_correlation_data(self, data)` Extract correlation matrix data. [View full source →](#method-analysisplotter-_extract_correlation_data)

---

## Functions

### `create_analysis_plotter(style)`

Factory function to create analysis plotter. Parameters

style : str, optional Plot style
**kwargs Additional configuration parameters Returns
-------
AnalysisPlotter Configured analysis plotter #### Source Code ```{literalinclude} ../../../src/analysis/visualization/analysis_plots.py
:language: python
:pyobject: create_analysis_plotter
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `from typing import Dict, List, Optional, Tuple, Any, Union`
- `import numpy as np`
- `import matplotlib.pyplot as plt`
- `import matplotlib.patches as patches`
- `from matplotlib.patches import Ellipse`
- `from scipy import stats`
- `import warnings`
- `from pathlib import Path`
- `from ..core.interfaces import VisualizationGenerator, AnalysisResult` *... and 1 more*
