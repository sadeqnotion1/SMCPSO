# analysis.core.interfaces

**Source:** `src\analysis\core\interfaces.py`

## Module Overview Core

interfaces for the analysis framework

.

## Advanced Mathematical Theory

### Interface Design Principles

### Abstract Base Classes

```python
# example-metadata:
# runnable: false

class Analyzer(Protocol):
    def analyze(self, data: Data) -> Result:
        ...
``` **Subtype relation:** ```{math}
\text{ConcreteAnalyzer} <: \text{Analyzer}
``` ### Dependency Inversion **High-level modules depend on abstractions:** ```{math}

\text{Controller} \to \text{IController} \leftarrow \text{ConcreteController}
``` ### Interface Segregation **Minimize interface size:** ```{math}
|\text{Interface}| = \min \{|I| : I \text{ satisfies requirements}\}
``` ### Type Variance **Covariance (return types):** ```{math}

S <: T \implies F[S] <: F[T]
``` **Contravariance (parameter types):** ```{math}
S <: T \implies F[T] <: F[S]
``` ### Design by Contract **Precondition:** $P: \text{State} \to \text{Bool}$

**Postcondition:** $Q: \text{State} \times \text{Result} \to \text{Bool}$ **Hoare triple:** ```{math}
\{P\} \, \text{method}() \, \{Q\}
``` ### Adapter Pattern **Interface adaptation:** ```{math}
\text{Adapter}: \text{SourceInterface} \to \text{TargetInterface}
``` ### Factory Method **Object creation abstraction:** ```{math}

\text{create}(\text{type}: T) \to \text{Instance}_T
``` ## Architecture Diagram ```{mermaid}
graph TD A[Abstract Interface] --> B[Protocol Definition] B --> C[Method Signatures] B --> D[Type Contracts] C --> E[Concrete Impl 1] C --> F[Concrete Impl 2] C --> G[Concrete Impl N] E --> H[Dependency Injection] F --> H G --> H H --> I[Client Code] D --> J[Runtime Validation] J --> K{Type Check} K -->|Pass| L[Execute] K -->|Fail| M[Type Error] A --> N[Adapter Pattern] N --> O[Legacy Interface] O --> P[Adapt to New] I --> Q[Factory Method] Q --> R[Create Instance] style B fill:#9cf style H fill:#ff9 style L fill:#9f9 style M fill:#f99
```

## Usage Examples

### Example 1: Basic Analysis

```python
from src.analysis import Analyzer

## Initialize analyzer
analyzer = Analyzer(config)
result = analyzer.analyze(data)
```

### Example 2: Statistical Validation

```python
## Compute confidence intervals
from src.analysis.validation import compute_confidence_interval
ci = compute_confidence_interval(samples, confidence=0.95)
print(f"95% CI: [{ci.lower:.3f}, {ci.upper:.3f}]")
```

### Example 3: Performance Metrics

```python
## Compute metrics
from src.analysis.performance import compute_all_metrics
metrics = compute_all_metrics(
    time=t,
    state=x,
    control=u,
    reference=r
)
print(f"ISE: {metrics.ise:.2f}, ITAE: {metrics.itae:.2f}")
```

### Example 4: Batch Analysis

```python
## Analyze multiple trials
results = []
for trial in range(n_trials):
    result = run_simulation(trial_seed=trial)
    results.append(analyzer.analyze(result))

## Aggregate statistics
mean_performance = np.mean([r.performance for r in results])
```

### Example 5: Robustness Analysis

```python
## Parameter sensitivity analysis
from src.analysis.performance import sensitivity_analysis
sensitivity = sensitivity_analysis(
    system=plant,
    parameters={'mass': (0.8, 1.2), 'length': (0.9, 1.1)},
    metric=compute_stability_margin
)
print(f"Most sensitive: {sensitivity.most_sensitive_param}")
```
This module defines abstract base classes and protocols that establish
the contract for analysis components, ensuring consistency and extensibility
across the framework. ## Complete Source Code ```{literalinclude} ../../../src/analysis/core/interfaces.py
:language: python
:linenos:
```

## Classes

### `AnalysisStatus`

**Inherits from:** `Enum` Status of analysis operations.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py

:language: python
:pyobject: AnalysisStatus
:linenos:
```

### `AnalysisResult`

Base class for analysis results.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py
:language: python
:pyobject: AnalysisResult
:linenos:
``` #### Methods (3) ##### `is_success(self)` Check if analysis was successful. [View full source →](#method-analysisresult-is_success) ##### `has_warnings(self)` Check if analysis has warnings. [View full source →](#method-analysisresult-has_warnings) ##### `has_errors(self)` Check if analysis has errors. [View full source →](#method-analysisresult-has_errors)

### `DataProtocol`

**Inherits from:** `Protocol` Protocol for simulation data.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py

:language: python
:pyobject: DataProtocol
:linenos:
``` #### Methods (2) ##### `get_time_range(self)` Get time range of the data. [View full source →](#method-dataprotocol-get_time_range) ##### `get_sampling_rate(self)` Get average sampling rate. [View full source →](#method-dataprotocol-get_sampling_rate)

### `MetricCalculator`

**Inherits from:** `ABC` Abstract base class for metric calculators.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py
:language: python
:pyobject: MetricCalculator
:linenos:
``` #### Methods (3) ##### `compute(self, data)` Compute metrics from simulation data. [View full source →](#method-metriccalculator-compute) ##### `supported_metrics(self)` List of metrics supported by this calculator. [View full source →](#method-metriccalculator-supported_metrics) ##### `validate_data(self, data)` Validate input data for metric calculation. [View full source →](#method-metriccalculator-validate_data)

### `PerformanceAnalyzer`

**Inherits from:** `ABC` Abstract base class for performance analyzers.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py

:language: python
:pyobject: PerformanceAnalyzer
:linenos:
``` #### Methods (3) ##### `analyze(self, data)` Perform performance analysis. [View full source →](#method-performanceanalyzer-analyze) ##### `analyzer_name(self)` Name of the analyzer. [View full source →](#method-performanceanalyzer-analyzer_name) ##### `required_data_fields(self)` List of required data fields for analysis. [View full source →](#method-performanceanalyzer-required_data_fields)

### `FaultDetector`

**Inherits from:** `ABC` Abstract base class for fault detection systems.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py
:language: python
:pyobject: FaultDetector
:linenos:
``` #### Methods (3) ##### `detect(self, data)` Detect faults in the system. [View full source →](#method-faultdetector-detect) ##### `reset(self)` Reset detector state for new analysis. [View full source →](#method-faultdetector-reset) ##### `detector_type(self)` Type of fault detector. [View full source →](#method-faultdetector-detector_type)

### `StatisticalValidator`

**Inherits from:** `ABC` Abstract base class for statistical validation.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py

:language: python
:pyobject: StatisticalValidator
:linenos:
``` #### Methods (2) ##### `validate(self, data)` Perform statistical validation. [View full source →](#method-statisticalvalidator-validate) ##### `validation_methods(self)` List of validation methods supported. [View full source →](#method-statisticalvalidator-validation_methods)

### `VisualizationGenerator`

**Inherits from:** `ABC` Abstract base class for visualization generators.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py
:language: python
:pyobject: VisualizationGenerator
:linenos:
``` #### Methods (2) ##### `generate(self, analysis_result)` Generate visualization from analysis results. [View full source →](#method-visualizationgenerator-generate) ##### `supported_formats(self)` List of supported output formats. [View full source →](#method-visualizationgenerator-supported_formats)

### `ReportGenerator`

**Inherits from:** `ABC` Abstract base class for report generators.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py

:language: python
:pyobject: ReportGenerator
:linenos:
``` #### Methods (2) ##### `generate_report(self, analysis_results)` Generate analysis report. [View full source →](#method-reportgenerator-generate_report) ##### `report_formats(self)` List of supported report formats. [View full source →](#method-reportgenerator-report_formats)

### `AnalyzerFactory`

**Inherits from:** `Protocol` Protocol for analyzer factories.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py
:language: python
:pyobject: AnalyzerFactory
:linenos:
``` #### Methods (4) ##### `create_metric_calculator(self, calculator_type)` Create a metric calculator of specified type. [View full source →](#method-analyzerfactory-create_metric_calculator) ##### `create_performance_analyzer(self, analyzer_type)` Create a performance analyzer of specified type. [View full source →](#method-analyzerfactory-create_performance_analyzer) ##### `create_fault_detector(self, detector_type)` Create a fault detector of specified type. [View full source →](#method-analyzerfactory-create_fault_detector) ##### `create_statistical_validator(self, validator_type)` Create a statistical validator of specified type. [View full source →](#method-analyzerfactory-create_statistical_validator)

### `AnalysisConfiguration`

**Inherits from:** `Protocol` Protocol for analysis configuration.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py

:language: python
:pyobject: AnalysisConfiguration
:linenos:
``` #### Methods (1) ##### `validate(self)` Validate configuration parameters. [View full source →](#method-analysisconfiguration-validate)

### `AnalysisPipeline`

**Inherits from:** `ABC` Abstract base class for analysis pipelines.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py
:language: python
:pyobject: AnalysisPipeline
:linenos:
``` #### Methods (4) ##### `add_analyzer(self, analyzer)` Add an analyzer to the pipeline. [View full source →](#method-analysispipeline-add_analyzer) ##### `run_pipeline(self, data)` Run the complete analysis pipeline. [View full source →](#method-analysispipeline-run_pipeline) ##### `get_summary(self)` Get summary of pipeline results. [View full source →](#method-analysispipeline-get_summary) ##### `pipeline_name(self)` Name of the analysis pipeline. [View full source →](#method-analysispipeline-pipeline_name)

### `AnalysisSession`

**Inherits from:** `ABC` Abstract base class for analysis sessions.

#### Source Code ```

{literalinclude} ../../../src/analysis/core/interfaces.py

:language: python
:pyobject: AnalysisSession
:linenos:
``` #### Methods (5) ##### `__enter__(self)` Enter analysis session context. [View full source →](#method-analysissession-__enter__) ##### `__exit__(self, exc_type, exc_val, exc_tb)` Exit analysis session context. [View full source →](#method-analysissession-__exit__) ##### `add_data(self, name, data)` Add data to the session. [View full source →](#method-analysissession-add_data) ##### `run_analysis(self, analysis_type)` Run analysis on session data. [View full source →](#method-analysissession-run_analysis) ##### `export_results(self, format)` Export session results. [View full source →](#method-analysissession-export_results)

## Dependencies This module imports: - `from __future__ import annotations`
- `from abc import ABC, abstractmethod`
- `from typing import Any, Dict, List, Optional, Protocol, Union, Tuple`
- `from dataclasses import dataclass`
- `from enum import Enum`
- `import numpy as np`
