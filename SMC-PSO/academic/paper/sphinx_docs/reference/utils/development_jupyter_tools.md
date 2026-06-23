# utils.development.jupyter_tools

**Source:** `src\utils\development\jupyter_tools.py`

## Module Overview Export

utilities for Jupyter notebooks

. This module provides convenient functions for exporting simulation results,


plots, and data from Jupyter notebooks in various formats. ## Complete Source Code ```{literalinclude} ../../../src/utils/development/jupyter_tools.py
:language: python
:linenos:
```

---

## Classes

### `NotebookExporter`

Utility class for exporting data and plots from Jupyter notebooks. Provides methods to save simulation results, plots, and metadata
in various formats with automatic timestamping and organization. #### Source Code ```{literalinclude} ../../../src/utils/development/jupyter_tools.py
:language: python
:pyobject: NotebookExporter
:linenos:
``` #### Methods (10) ##### `__init__(self, base_dir)` Initialize the exporter. [View full source →](#method-notebookexporter-__init__) ##### `export_simulation_data(self, time, states, controls, metadata, prefix)` Export simulation data in multiple formats. [View full source →](#method-notebookexporter-export_simulation_data) ##### `export_plots(self, figures, names, prefix, formats)` Export matplotlib figures in multiple formats. [View full source →](#method-notebookexporter-export_plots) ##### `export_optimization_results(self, best_params, cost_history, algorithm_info, prefix)` Export PSO or other optimization results. [View full source →](#method-notebookexporter-export_optimization_results) ##### `create_analysis_report(self, time, states, controls, metadata, prefix)` Create a analysis report with statistics and plots. [View full source →](#method-notebookexporter-create_analysis_report) ##### `_calculate_statistics(self, time, states, controls)` Calculate performance statistics. [View full source →](#method-notebookexporter-_calculate_statistics) ##### `_create_state_plot(self, time, states)` Create state time series plot. [View full source →](#method-notebookexporter-_create_state_plot) ##### `_create_control_plot(self, time, controls)` Create control signal plot. [View full source →](#method-notebookexporter-_create_control_plot) ##### `_create_phase_plot(self, states)` Create phase space plot. [View full source →](#method-notebookexporter-_create_phase_plot) ##### `_generate_html_report(self, stats, plot_dir, metadata)` Generate HTML report content. [View full source →](#method-notebookexporter-_generate_html_report)

---

## Functions

### `quick_export_simulation(time, states, controls)`

Quick simulation data export with default settings.

#### Source Code ```

{literalinclude} ../../../src/utils/development/jupyter_tools.py

:language: python
:pyobject: quick_export_simulation
:linenos:
```

### `quick_export_plots()`

Quick plot export with default settings.

#### Source Code ```

{literalinclude} ../../../src/utils/development/jupyter_tools.py
:language: python
:pyobject: quick_export_plots
:linenos:
```

### `quick_analysis_report(time, states, controls)`

Quick analysis report generation.

#### Source Code ```

{literalinclude} ../../../src/utils/development/jupyter_tools.py

:language: python
:pyobject: quick_analysis_report
:linenos:
```

---

## Dependencies This module imports: - `import json`
- `import pickle`
- `import zipfile`
- `from datetime import datetime`
- `from pathlib import Path`
- `from typing import Any, Dict, List, Optional, Union`
- `import matplotlib.pyplot as plt`
- `import numpy as np`
- `import pandas as pd` ## Architecture Diagram ```{mermaid}
graph TD A[Component] --> B[Subcomponent 1] A --> C[Subcomponent 2] B --> D[Output] C --> D style A fill:#e1f5ff style D fill:#e8f5e9
``` ## Usage Examples ### Example 1: Basic Usage ```python
# Basic usage example

from src.utils import Component component = Component()
result = component.process(data)
``` ### Example 2: Advanced Configuration ```python
# Advanced configuration
component = Component( option1=value1, option2=value2
)
``` ### Example 3: Integration with Framework ```python
# Integration example

from src.simulation import SimulationRunner runner = SimulationRunner()
runner.use_component(component)
``` ### Example 4: Performance Optimization ```python
# Performance-optimized usage
component = Component(enable_caching=True)
``` ### Example 5: Error Handling ```python
# Error handling

try: result = component.process(data)
except ComponentError as e: print(f"Error: {e}")
```
