# analysis.__init__

**Source:** `src\analysis\__init__.py`

## Module Overview Professional

analysis framework for control system evaluation and validation

.

## Advanced Mathematical Theory

### Analysis Framework Architecture


\text{Framework} = \text{Performance} \cup \text{Validation} \cup \text{FDI} \cup \text{Visualization}
``` ### Module Dependencies **Dependency graph:** ```{math}
\begin{align}
\text{FDI} &\to \text{Validation} \to \text{Visualization} \\
\text{Performance} &\to \text{Validation} \to \text{Visualization}
\end{align}
``` ### Workflow Integration **Complete analysis pipeline:** ```{math}

\text{Data} \xrightarrow{\text{Performance}} \text{Metrics} \xrightarrow{\text{Validation}} \text{Statistics} \xrightarrow{\text{Viz}} \text{Report}
``` ## Architecture Diagram ```{mermaid}
graph TD A[Analysis Framework] --> B[Performance] A --> C[Validation] A --> D[FDI] A --> E[Visualization] B --> F[Stability] B --> G[Robustness] B --> H[Metrics] C --> I[Statistical Tests] C --> J[Monte Carlo] C --> K[Cross-Validation] D --> L[Residuals] D --> M[Thresholds] E --> N[Analysis Plots] E --> O[Reports] F --> P[Integration Layer] G --> P H --> P I --> P J --> P K --> P L --> P M --> P N --> P O --> P style P fill:#9cf style A fill:#ff9
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
This module provides a analysis framework including:
- Core analysis interfaces and data structures
- Performance metrics and evaluation
- Fault detection and isolation
- Statistical validation and testing
- Monte Carlo analysis
- Cross-validation methods
- Visualization and reporting The framework follows control engineering best practices and provides both
legacy compatibility and modern enhanced capabilities. ## Complete Source Code ```{literalinclude} ../../../src/analysis/__init__.py
:language: python
:linenos:
```

---

## Functions

### `create_performance_analyzer(analyzer_type)`

Create performance analyzer instance. Parameters

analyzer_type : str Type of analyzer ('advanced', 'stability', 'robustness')
**kwargs Additional configuration parameters Returns
PerformanceAnalyzer Configured performance analyzer #### Source Code ```{literalinclude} ../../../src/analysis/__init__.py
:language: python
:pyobject: create_performance_analyzer
:linenos:
```

---

### `create_fault_detector(detector_type)`

Create fault detector instance. Parameters
----------
detector_type : str Type of detector ('enhanced', 'legacy')
**kwargs Additional configuration parameters Returns
FaultDetector Configured fault detector #### Source Code ```{literalinclude} ../../../src/analysis/__init__.py
:language: python
:pyobject: create_fault_detector
:linenos:
```

---

### `create_statistical_validator()`

Create statistical validator instance.

#### Source Code ```

{literalinclude} ../../../src/analysis/__init__.py

:language: python
:pyobject: create_statistical_validator
:linenos:
```

### `create_monte_carlo_analyzer()`

Create Monte Carlo analyzer instance.

#### Source Code ```

{literalinclude} ../../../src/analysis/__init__.py
:language: python
:pyobject: create_monte_carlo_analyzer
:linenos:
```

### `create_visualization_suite()`

Create complete visualization suite.

#### Source Code ```

{literalinclude} ../../../src/analysis/__init__.py

:language: python
:pyobject: create_visualization_suite
:linenos:
```

---

## Dependencies This module imports: - `from .core.interfaces import AnalysisResult, AnalysisStatus, DataProtocol, MetricCalculator, PerformanceAnalyzer, FaultDetector, StatisticalValidator`
- `from .core.data_structures import SimulationData, MetricResult, PerformanceMetrics, FaultDetectionResult, StatisticalTestResult, ConfidenceInterval`
- `from .core.metrics import BaseMetricCalculator, ControlPerformanceMetrics, StabilityMetrics`
- `from .performance.control_metrics import AdvancedControlMetrics, compute_ise, compute_itae, compute_rms_control_effort`
- `from .performance.stability_analysis import StabilityAnalyzer`
- `from .performance.robustness import RobustnessAnalyzer`
- `from .fault_detection.fdi_system import EnhancedFaultDetector, FaultDetectionConfig, FaultType, DetectionMethod, create_enhanced_fault_detector, FDIsystem, FaultDetectionInterface, DynamicsProtocol`
- `from .fault_detection.residual_generators import ResidualGeneratorFactory, ObserverBasedGenerator, KalmanFilterGenerator, ParitySpaceGenerator`
- `from .fault_detection.threshold_adapters import ThresholdAdapterFactory, StatisticalThresholdAdapter, EWMAThresholdAdapter, AdaptiveThresholdManager`
- `from .validation.statistical_tests import StatisticalTestSuite` *... and 7 more*
