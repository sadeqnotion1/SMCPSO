# analysis.visualization.report_generator

**Source:** `src\analysis\visualization\report_generator.py`

## Module Overview Report

generation module for control system analysis

.

## Advanced Mathematical Theory

### Report Generation Framework


\text{Report} = \text{Template} \oplus \text{Data} \oplus \text{Style}
``` ### LaTeX Generation **Mathematical content:** ```latex
\begin{equation} \vec{r}(t) = \vec{y}(t) - \hat{\vec{y}}(t)
\end{equation}
``` **Automatic figure inclusion:** ```latex

\begin{figure}[htbp] \centering \includegraphics[width=0.8\textwidth]{figure.pdf} \caption{Performance analysis}
\end{figure}
``` ### Markdown Generation **Hierarchical structure:** ```markdown
# Analysis Report
## Performance Metrics
- ISE: 12.34
- ITAE: 56.78
``` **Table generation:** ```{math}

\text{Table}[i,j] = f(\text{data}[i], \text{metric}[j])
``` ### Multi-Format Export **Pandoc conversion:** ```{math}
\text{Markdown} \xrightarrow{\text{pandoc}} \begin{cases}
\text{HTML} \\
\text{PDF} \\
\text{DOCX}
\end{cases}
``` ## Architecture Diagram ```{mermaid}

graph TD A[Analysis Results] --> B[Template Selection] B --> C{Format} C -->|LaTeX| D[LaTeX Template] C -->|Markdown| E[Markdown Template] C -->|HTML| F[HTML Template] D --> G[Math Rendering] E --> H[Simple Formatting] F --> I[Interactive Elements] G --> J[Figure Inclusion] H --> J I --> J J --> K[Content Assembly] K --> L[Style Application] L --> M{Export Format} M -->|PDF| N[PDF Output] M -->|HTML| O[HTML Output] M -->|DOCX| P[Word Output] style K fill:#9cf style L fill:#ff9 style N fill:#9f9 style O fill:#9f9 style P fill:#9f9
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

This module provides automated report generation features that combine
analysis results, visualizations, and statistical summaries into professional reports. ## Complete Source Code ```{literalinclude} ../../../src/analysis/visualization/report_generator.py
:language: python
:linenos:
```

---

## Classes

### `ReportGenerator`

report generation for control system analysis.

#### Source Code ```

{literalinclude} ../../../src/analysis/visualization/report_generator.py
:language: python
:pyobject: ReportGenerator
:linenos:
``` #### Methods (22) ##### `__init__(self, output_dir)` Initialize report generator. [View full source →](#method-reportgenerator-__init__) ##### `generate_full_report(self, simulation_data, performance_metrics, analysis_results, report_name, include_statistical, include_diagnostics)` Generate analysis report. [View full source →](#method-reportgenerator-generate_full_report) ##### `generate_quick_report(self, simulation_data, performance_metrics, report_name)` Generate quick summary report with key plots. [View full source →](#method-reportgenerator-generate_quick_report) ##### `_create_title_page(self, pdf, title, simulation_data)` Create report title page. [View full source →](#method-reportgenerator-_create_title_page) ##### `_create_executive_summary(self, pdf, simulation_data, performance_metrics)` Create executive summary page. [View full source →](#method-reportgenerator-_create_executive_summary) ##### `_add_time_domain_analysis(self, pdf, simulation_data)` Add time domain analysis section. [View full source →](#method-reportgenerator-_add_time_domain_analysis) ##### `_add_performance_analysis(self, pdf, performance_metrics)` Add performance analysis section. [View full source →](#method-reportgenerator-_add_performance_analysis) ##### `_add_diagnostic_analysis(self, pdf, simulation_data)` Add diagnostic analysis section. [View full source →](#method-reportgenerator-_add_diagnostic_analysis) ##### `_add_statistical_analysis(self, pdf, analysis_results)` Add statistical analysis section. [View full source →](#method-reportgenerator-_add_statistical_analysis) ##### `_add_frequency_analysis(self, pdf, simulation_data)` Add frequency domain analysis section. [View full source →](#method-reportgenerator-_add_frequency_analysis) ##### `_add_phase_analysis(self, pdf, simulation_data)` Add phase analysis section. [View full source →](#method-reportgenerator-_add_phase_analysis) ##### `_create_conclusions(self, pdf, simulation_data, performance_metrics)` Create conclusions and recommendations page. [View full source →](#method-reportgenerator-_create_conclusions) ##### `_create_appendix(self, pdf, simulation_data, analysis_results)` Create appendix with raw data summary. [View full source →](#method-reportgenerator-_create_appendix) ##### `_generate_json_report(self, simulation_data, performance_metrics, analysis_results, report_name, timestamp)` Generate JSON report with numerical data. [View full source →](#method-reportgenerator-_generate_json_report) ##### `_generate_summary_text(self, simulation_data, performance_metrics)` Generate executive summary text. [View full source →](#method-reportgenerator-_generate_summary_text) ##### `_generate_key_findings(self, simulation_data, performance_metrics)` Generate key findings text. [View full source →](#method-reportgenerator-_generate_key_findings) ##### `_generate_conclusions_text(self, simulation_data, performance_metrics)` Generate conclusions text. [View full source →](#method-reportgenerator-_generate_conclusions_text) ##### `_generate_recommendations(self, simulation_data, performance_metrics)` Generate recommendations text. [View full source →](#method-reportgenerator-_generate_recommendations) ##### `_generate_data_statistics(self, simulation_data)` Generate data statistics text. [View full source →](#method-reportgenerator-_generate_data_statistics) ##### `_compute_summary_statistics(self, simulation_data)` Compute summary statistics for JSON export. [View full source →](#method-reportgenerator-_compute_summary_statistics) ##### `_serialize_performance_metrics(self, performance_metrics)` Serialize performance metrics for JSON export. [View full source →](#method-reportgenerator-_serialize_performance_metrics) ##### `_serialize_analysis_results(self, analysis_results)` Serialize analysis results for JSON export. [View full source →](#method-reportgenerator-_serialize_analysis_results)

---

## Dependencies This module imports: - `import matplotlib.pyplot as plt`

- `from matplotlib.backends.backend_pdf import PdfPages`
- `import numpy as np`
- `import pandas as pd`
- `from datetime import datetime`
- `from pathlib import Path`
- `from typing import Dict, List, Optional, Any, Union`
- `import json`
- `from ..core.interfaces import AnalysisResult, DataProtocol`
- `from ..core.data_structures import SimulationData, PerformanceMetrics, MetricResult` *... and 3 more*
