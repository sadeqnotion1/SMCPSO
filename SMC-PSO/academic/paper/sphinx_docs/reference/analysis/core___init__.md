# analysis.core.__init__

**Source:** `src\analysis\core\__init__.py`

## Module Overview

Core analysis framework components.

This module provides the foundational interfaces, data structures, and
metric computation features for the analysis framework.

## Complete Source Code

```{literalinclude} ../../../src/analysis/core/__init__.py
:language: python
:linenos:
```



## Dependencies

This module imports:

- `from .interfaces import AnalysisStatus, AnalysisResult, DataProtocol, MetricCalculator, PerformanceAnalyzer, FaultDetector, StatisticalValidator, VisualizationGenerator, ReportGenerator, AnalyzerFactory, AnalysisConfiguration, AnalysisPipeline, AnalysisSession`
- `from .data_structures import SimulationData, MetricResult, PerformanceMetrics, FaultDetectionResult, StatisticalTestResult, ConfidenceInterval, ComparisonResult, AnalysisConfiguration, create_simulation_data_from_arrays, create_analysis_result`
- `from .metrics import BaseMetricCalculator, ControlPerformanceMetrics, StabilityMetrics, RobustnessMetrics, create_comprehensive_metrics`
