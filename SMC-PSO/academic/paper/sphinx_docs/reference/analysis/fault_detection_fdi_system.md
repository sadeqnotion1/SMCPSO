# analysis.fault_detection.fdi_system

**Source:** `src\analysis\fault_detection\fdi_system.py`

## Module Overview Enhanced

fault detection and isolation system

.

## Advanced Mathematical Theory

### Enhanced FDI System Design


\text{Decision} = \text{Fusion}(r_1, r_2, \ldots, r_m)
``` Where $r_i$ from different methods (observer, parity, Kalman). ### Detection Methods **Observer-based:** ```{math}
r_{obs} = \vec{y} - C\hat{\vec{x}}
``` **Parity-based:** ```{math}

r_{par} = W \begin{bmatrix} \vec{y} \\ \vec{u} \end{bmatrix}
``` **Kalman filter:** ```{math}
r_{kf} = \vec{y}_k - C\hat{\vec{x}}_{k|k-1}
``` ### Fault Signature Analysis **Normalized residual:** ```{math}

\bar{r}_i = \frac{r_i - \mu_i}{\sigma_i}
``` **Chi-square test:** ```{math}
\chi^2 = \sum_{i=1}^n \bar{r}_i^2 \sim \chi^2_n
``` Detect fault if $\chi^2 > \chi^2_{n, \alpha}$ (critical value). ### Directional Residual Evaluation **Angle between residuals:** ```{math}

\cos(\theta) = \frac{\vec{r} \cdot \vec{r}_{sig}}{\|\vec{r}\| \|\vec{r}_{sig}\|}
``` Match to known fault signature $\vec{r}_{sig}$. ### Fusion Strategies **Voting:** ```{math}
\text{Fault detected if } \sum_{i=1}^m \mathbb{1}_{|r_i| > \tau_i} \geq k
``` **Bayesian fusion:** ```{math}

P(f | r_1, \ldots, r_m) \propto P(r_1, \ldots, r_m | f) P(f)
``` ### Diagnosis Confidence **Confidence score:** ```{math}
C = \max_i \frac{|\vec{r} \cdot \vec{r}_{sig,i}|}{\|\vec{r}\| \|\vec{r}_{sig,i}\|}
``` ## Architecture Diagram ```{mermaid}

graph TD A[Sensor Data] --> B[Multi-Method FDI] B --> C[Observer-Based] B --> D[Parity-Based] B --> E[Kalman Filter] C --> F[r_obs] D --> G[r_par] E --> H[r_kf] F --> I[Fusion Engine] G --> I H --> I I --> J{Voting/Bayesian} J --> K[Combined Decision] K --> L[Signature Matching] L --> M[Fault Isolation] M --> N[Diagnosis] N --> O[Fault Report] style I fill:#9cf style J fill:#ff9 style O fill:#9f9
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

This module provides a fault detection framework that extends
the basic FDI system with advanced diagnostic features, multiple fault
detection methods, and statistical analysis. ## Complete Source Code ```{literalinclude} ../../../src/analysis/fault_detection/fdi_system.py
:language: python
:linenos:
```

---

## Classes

### `FaultType`

**Inherits from:** `Enum` Enumeration of fault types.

#### Source Code ```

{literalinclude} ../../../src/analysis/fault_detection/fdi_system.py
:language: python
:pyobject: FaultType
:linenos:
```

---

## `DetectionMethod`

**Inherits from:** `Enum` Enumeration of detection methods.

### Source Code ```

{literalinclude} ../../../src/analysis/fault_detection/fdi_system.py

:language: python
:pyobject: DetectionMethod
:linenos:
```

### `FaultDetectionConfig`

Configuration for enhanced fault detection system.

#### Source Code ```

{literalinclude} ../../../src/analysis/fault_detection/fdi_system.py
:language: python
:pyobject: FaultDetectionConfig
:linenos:
```

### `FaultSignature`

Signature for fault identification.

#### Source Code ```

{literalinclude} ../../../src/analysis/fault_detection/fdi_system.py

:language: python
:pyobject: FaultSignature
:linenos:
```

### `EnhancedFaultDetector`

**Inherits from:** `FaultDetector` Enhanced fault detection and isolation system.

#### Source Code ```

{literalinclude} ../../../src/analysis/fault_detection/fdi_system.py
:language: python
:pyobject: EnhancedFaultDetector
:linenos:
``` #### Methods (35) ##### `__init__(self, config)` Initialize enhanced fault detector. [View full source →](#method-enhancedfaultdetector-__init__) ##### `detector_type(self)` Type of fault detector. [View full source →](#method-enhancedfaultdetector-detector_type) ##### `detect(self, data)` Detect faults in the system. [View full source →](#method-enhancedfaultdetector-detect) ##### `reset(self)` Reset detector state for new analysis. [View full source →](#method-enhancedfaultdetector-reset) ##### `_perform_residual_based_detection(self, data)` Perform residual-based fault detection. [View full source →](#method-enhancedfaultdetector-_perform_residual_based_detection) ##### `_model_free_residual_detection(self, data)` Model-free residual detection using statistical properties. [View full source →](#method-enhancedfaultdetector-_model_free_residual_detection) ##### `_model_based_residual_detection(self, data, dynamics_model)` Model-based residual detection using dynamics prediction. [View full source →](#method-enhancedfaultdetector-_model_based_residual_detection) ##### `_perform_statistical_detection(self, data)` Perform statistical fault detection. [View full source →](#method-enhancedfaultdetector-_perform_statistical_detection) ##### `_perform_signal_based_detection(self, data)` Perform signal-based fault detection using frequency analysis. [View full source →](#method-enhancedfaultdetector-_perform_signal_based_detection) ##### `_perform_change_point_detection(self, data)` Perform change point detection. [View full source →](#method-enhancedfaultdetector-_perform_change_point_detection) ##### `_perform_fault_classification(self, detection_results)` Classify detected faults. [View full source →](#method-enhancedfaultdetector-_perform_fault_classification) ##### `_assess_fault_severity(self, detection_results)` Assess fault severity. [View full source →](#method-enhancedfaultdetector-_assess_fault_severity) ##### `_perform_fault_isolation(self, data, detection_results)` Perform fault isolation to identify fault location. [View full source →](#method-enhancedfaultdetector-_perform_fault_isolation) ##### `_apply_persistence_filter(self, violations)` Apply persistence filter to reduce false alarms. [View full source →](#method-enhancedfaultdetector-_apply_persistence_filter) ##### `_test_normality(self, data)` Test for normality using Shapiro-Wilk test. [View full source →](#method-enhancedfaultdetector-_test_normality) ##### `_test_stationarity(self, data)` Test for stationarity using simple variance-based test. [View full source →](#method-enhancedfaultdetector-_test_stationarity) ##### `_detect_outliers(self, data)` Detect outliers using statistical methods. [View full source →](#method-enhancedfaultdetector-_detect_outliers) ##### `_detect_change_points_statistical(self, data)` Detect change points using statistical methods. [View full source →](#method-enhancedfaultdetector-_detect_change_points_statistical) ##### `_analyze_frequency_bands(self, freqs, psd)` Analyze power in different frequency bands. [View full source →](#method-enhancedfaultdetector-_analyze_frequency_bands) ##### `_detect_spectral_anomalies(self, freqs, psd)` Detect spectral anomalies. [View full source →](#method-enhancedfaultdetector-_detect_spectral_anomalies) ##### `_analyze_harmonics(self, signal_data, fs)` Analyze harmonic content of signal. [View full source →](#method-enhancedfaultdetector-_analyze_harmonics) ##### `_compute_thd(self, fundamental_magnitude, harmonics)` Compute total harmonic distortion. [View full source →](#method-enhancedfaultdetector-_compute_thd) ##### `_cusum_change_point_detection(self, data)` CUSUM-based change point detection. [View full source →](#method-enhancedfaultdetector-_cusum_change_point_detection) ##### `_variance_change_detection(self, data)` Detect changes in variance. [View full source →](#method-enhancedfaultdetector-_variance_change_detection) ##### `_mean_change_detection(self, data)` Detect changes in mean. [View full source →](#method-enhancedfaultdetector-_mean_change_detection) ##### `_extract_fault_features(self, detection_results)` Extract features for fault classification. [View full source →](#method-enhancedfaultdetector-_extract_fault_features) ##### `_classify_with_signatures(self, features, fault_signatures)` Classify fault using known signatures. [View full source →](#method-enhancedfaultdetector-_classify_with_signatures) ##### `_classify_heuristic(self, features)` Heuristic fault classification based on features. [View full source →](#method-enhancedfaultdetector-_classify_heuristic) ##### `_compute_signature_similarity(self, features1, features2)` Compute similarity between feature sets. [View full source →](#method-enhancedfaultdetector-_compute_signature_similarity) ##### `_compute_statistical_severity(self, statistical_results)` Compute severity based on statistical anomalies. [View full source →](#method-enhancedfaultdetector-_compute_statistical_severity) ##### `_categorize_severity(self, severity_score)` Categorize severity score into levels. [View full source →](#method-enhancedfaultdetector-_categorize_severity) ##### `_compute_state_anomaly_score(self, state_data, detection_results)` Compute anomaly score for a specific state. [View full source →](#method-enhancedfaultdetector-_compute_state_anomaly_score) ##### `_compute_isolation_confidence(self, isolation_results)` Compute confidence in fault isolation. [View full source →](#method-enhancedfaultdetector-_compute_isolation_confidence) ##### `_determine_overall_status(self, results)` Determine overall fault detection status. [View full source →](#method-enhancedfaultdetector-_determine_overall_status) ##### `_generate_diagnostic_summary(self, results)` Generate diagnostic summary. [View full source →](#method-enhancedfaultdetector-_generate_diagnostic_summary)

### `DynamicsProtocol`

**Inherits from:** `TypingProtocol` Protocol defining the expected interface for dynamics models.

#### Source Code ```

{literalinclude} ../../../src/analysis/fault_detection/fdi_system.py

:language: python
:pyobject: DynamicsProtocol
:linenos:
``` #### Methods (1) ##### `step(self, state, u, dt)` Advance the system dynamics by one timestep. [View full source →](#method-dynamicsprotocol-step)

### `FDIsystem`

Legacy fault detection and isolation system for backward compatibility. This is the original FDI system that provides basic fault detection
capabilities. For new applications, consider using EnhancedFaultDetector
which provides more advanced features and better integration with the
analysis framework. #### Source Code ```{literalinclude} ../../../src/analysis/fault_detection/fdi_system.py
:language: python
:pyobject: FDIsystem
:linenos:
``` #### Methods (1) ##### `check(self, t, meas, u, dt, dynamics_model)` Check for a fault at the current time step. [View full source →](#method-fdisystem-check)

---

## Functions

### `create_enhanced_fault_detector(config)`

Factory function to create enhanced fault detector. Parameters

config : Dict[str, Any], optional Configuration parameters Returns
-------
EnhancedFaultDetector Configured enhanced fault detector #### Source Code ```{literalinclude} ../../../src/analysis/fault_detection/fdi_system.py
:language: python
:pyobject: create_enhanced_fault_detector
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `from typing import Dict, List, Optional, Tuple, Any, Union, Callable`
- `import numpy as np`
- `from scipy import signal, stats`
- `import warnings`
- `from dataclasses import dataclass, field`
- `from enum import Enum`
- `from datetime import datetime`
- `from ..core.interfaces import FaultDetector, AnalysisResult, AnalysisStatus, DataProtocol`
- `from ..core.data_structures import FaultDetectionResult, StatisticalTestResult, ConfidenceInterval` *... and 2 more*
