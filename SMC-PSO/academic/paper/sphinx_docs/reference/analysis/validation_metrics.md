# analysis.validation.metrics

**Source:** `src\analysis\validation\metrics.py`

## Module Overview Statistical

and validation metrics for analysis systems

.

## Advanced Mathematical Theory

### Validation Metrics


\text{MSE} = \frac{1}{n}\sum_{i=1}^n (y_i - \hat{y}_i)^2
``` **Root Mean Squared Error (RMSE):** ```{math}
\text{RMSE} = \sqrt{\text{MSE}}
``` **Mean Absolute Error (MAE):** ```{math}

\text{MAE} = \frac{1}{n}\sum_{i=1}^n |y_i - \hat{y}_i|
``` ### Coefficient of Determination **R-squared:** ```{math}
R^2 = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2} = 1 - \frac{\text{SSE}}{\text{SST}}
``` **Adjusted R-squared:** ```{math}

R_{adj}^2 = 1 - \frac{(1-R^2)(n-1)}{n-p-1}
``` Where $p$ is number of predictors. ### Normalized Metrics **Normalized RMSE:** ```{math}
\text{NRMSE} = \frac{\text{RMSE}}{y_{max} - y_{min}} \times 100\%
``` **Mean Absolute Percentage Error:** ```{math}

\text{MAPE} = \frac{100\%}{n}\sum_{i=1}^n \left|\frac{y_i - \hat{y}_i}{y_i}\right|
``` ### Theil's U Statistic **Inequality coefficient:** ```{math}
U = \frac{\sqrt{\frac{1}{n}\sum(y_i - \hat{y}_i)^2}}{\sqrt{\frac{1}{n}\sum y_i^2} + \sqrt{\frac{1}{n}\sum \hat{y}_i^2}}
``` Range: $U \in [0, 1]$, where 0 is perfect fit. ### Tracking Signal **Cumulative error:** ```{math}

\text{TS} = \frac{\sum_{i=1}^n (y_i - \hat{y}_i)}{\text{MAD}}
``` Where MAD is Mean Absolute Deviation. ### Akaike Information Criterion (AIC) **Model selection criterion:** ```{math}
\text{AIC} = 2p - 2\ln(L)
``` Where $p$ is parameters, $L$ is likelihood. **Corrected AIC (small sample):** ```{math}

\text{AIC}_c = \text{AIC} + \frac{2p(p+1)}{n-p-1}
``` ## Architecture Diagram ```{mermaid}
graph TD A[Predictions ŷ] --> B[Error Computation] C[Actual y] --> B B --> D[MSE: 1/n Σ(y-ŷ)²] B --> E[MAE: 1/n Σ|y-ŷ|] B --> F[MAPE: 100/n Σ|y-ŷ|/y] D --> G[RMSE: √MSE] D --> H[R²: 1-SSE/SST] G --> I{Normalize?} I -->|Yes| J[NRMSE] I -->|No| K[Absolute RMSE] H --> L{Adjust for p?} L -->|Yes| M[Adjusted R²] L -->|No| N[Raw R²] E --> O[Model Selection] F --> O J --> O K --> O M --> O N --> O O --> P[AIC/BIC] P --> Q[Best Model] style B fill:#9cf style O fill:#ff9 style Q fill:#9f9
``` ## Usage Examples ### Example 1: Basic Analysis ```python

from src.analysis import Analyzer # Initialize analyzer
analyzer = Analyzer(config)
result = analyzer.analyze(data)
``` ### Example 2: Statistical Validation ```python
# Compute confidence intervals
from src.analysis.validation import compute_confidence_interval ci = compute_confidence_interval(samples, confidence=0.95)
print(f"95% CI: [{ci.lower:.3f}, {ci.upper:.3f}]")
``` ### Example 3: Performance Metrics ```python
# Compute metrics

from src.analysis.performance import compute_all_metrics metrics = compute_all_metrics( time=t, state=x, control=u, reference=r
)
print(f"ISE: {metrics.ise:.2f}, ITAE: {metrics.itae:.2f}")
``` ### Example 4: Batch Analysis ```python
# Analyze multiple trials
results = []
for trial in range(n_trials): result = run_simulation(trial_seed=trial) results.append(analyzer.analyze(result)) # Aggregate statistics
mean_performance = np.mean([r.performance for r in results])
``` ### Example 5: Robustness Analysis ```python
# Parameter sensitivity analysis

from src.analysis.performance import sensitivity_analysis sensitivity = sensitivity_analysis( system=plant, parameters={'mass': (0.8, 1.2), 'length': (0.9, 1.1)}, metric=compute_stability_margin
)
print(f"Most sensitive: {sensitivity.most_sensitive_param}")
```
This module provides metrics computation for validating
control system performance, statistical analysis, and benchmarking. ## Architecture Diagram ```{mermaid}
graph TD A[Simulation Result] --> B[Time Vector t] A --> C[State Trajectory x_t_] A --> D[Control Signal u_t_] B --> E[Control Metrics] C --> E E --> F[ISE] E --> G[ITAE] E --> H[RMS Control] B --> I[Stability Metrics] C --> I I --> J[Overshoot] I --> K[Settling Time] I --> L[Damping Ratio] B --> M[Constraint Metrics] D --> M M --> N[Saturation Severity] M --> O[Violation Count] M --> P[Peak Violation] F --> Q[Metrics Dictionary] G --> Q H --> Q J --> Q K --> Q L --> Q N --> Q O --> Q P --> Q Q --> R[Validation Result] style E fill:#9cf style I fill:#fcf style M fill:#ff9 style Q fill:#f9f style R fill:#9f9
``` **Data Flow:**

1. Extract time, state, control trajectories from simulation
2. **Control Metrics Module**: Compute ISE, ITAE, RMS
3. **Stability Metrics Module**: Compute overshoot, settling time, damping
4. **Constraint Metrics Module**: Compute violations and severity
5. Aggregate all metrics into unified dictionary
6. Return structured validation result **Metric Categories:**
- **Control Performance**: Tracking accuracy, convergence speed
- **Stability Analysis**: Overshoot, damping characteristics
- **Constraint Satisfaction**: Actuator limits, physical constraints ## Mathematical Foundation ### Performance Metric Theory Rigorous performance metrics objective controller comparison and validation against specifications. #### Control Engineering Metrics **Integral of Time-weighted Absolute Error (ITAE)**:
```{math}
ITAE = \int_0^T t |\vec{x}(t)| dt
``` - **Purpose**: Penalizes long settling times

- **Property**: Emphasizes late-time errors more than early errors
- **Interpretation**: Lower ITAE → faster convergence **Overshoot**:
```{math}
OS = \frac{\max(x(t)) - x_{\text{ref}}}{x_{\text{ref}}} \times 100\%
``` **Damping Ratio** (estimated from overshoot):

```{math}
\zeta \approx \frac{-\ln(OS/100)}{\sqrt{\pi^2 + \ln^2(OS/100)}}
``` #### Constraint Violation Analysis **Saturation Severity**:

```{math}
SV = \int_0^T \max(0, |u(t)| - u_{\max}) dt
``` **Violation Frequency**:

```{math}
VF = \frac{1}{T} \sum_{k=0}^{N} \mathbb{1}_{|u_k| > u_{\max}}
``` **Peak Violation**:

```{math}
PV = \max_{t \in [0,T]} (|u(t)| - u_{\max})
``` #### Stability Metrics **Lyapunov Exponent** (numerical estimate):

```{math}
\lambda = \lim_{T \to \infty} \frac{1}{T} \ln \frac{||\delta \vec{x}(T)||}{||\delta \vec{x}(0)||}
``` - $\lambda < 0$: Asymptotically stable

- $\lambda > 0$: Unstable (chaos) **Energy Dissipation Rate**:
```{math}
\dot{E} = \frac{dE}{dt} < 0 \quad \forall t > t_0
``` Required for Lyapunov stability. ### Statistical Properties **Consistency**: Metrics should be monotonic in performance (better control → lower ISE). **Sensitivity**: Sufficient resolution to distinguish controller variants. **Robustness**: Insensitive to numerical noise and discretization. **See:** {doc}`../../../control_theory/performance_specifications` ## Complete Source Code ```{literalinclude} ../../../src/analysis/validation/metrics.py

:language: python
:linenos:
```

---

## Functions

### `compute_basic_metrics(data)`

Compute basic statistical metrics for data analysis. Args: data: Input data array Returns: Dictionary containing basic statistical metrics

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/metrics.py
:language: python
:pyobject: compute_basic_metrics
:linenos:
```

---

## `compute_performance_metrics(reference, actual)`

Compute performance metrics comparing actual vs reference data. Args: reference: Reference/target data actual: Actual measured data Returns: Dictionary containing performance metrics

### Source Code ```

{literalinclude} ../../../src/analysis/validation/metrics.py

:language: python
:pyobject: compute_performance_metrics
:linenos:
```

### `compute_control_metrics(control_signals, time_vector)`

Compute control-specific performance metrics. Args: control_signals: Control input signals over time time_vector: Optional time vector for time-based metrics Returns: Dictionary containing control metrics

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/metrics.py
:language: python
:pyobject: compute_control_metrics
:linenos:
```

### `compute_stability_metrics(states, reference_state)`

Compute stability-related metrics for state trajectories. Args: states: State trajectory matrix (time x state_dim) reference_state: Optional reference state for deviation metrics Returns: Dictionary containing stability metrics

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/metrics.py

:language: python
:pyobject: compute_stability_metrics
:linenos:
```

### `compute_frequency_metrics(signal, sampling_rate, frequency_bands)`

Compute frequency domain metrics for signal analysis. Args: signal: Input signal sampling_rate: Sampling rate in Hz frequency_bands: Optional list of (low, high) frequency bands Returns: Dictionary containing frequency domain metrics

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/metrics.py
:language: python
:pyobject: compute_frequency_metrics
:linenos:
```

### `compute_statistical_significance(data1, data2, test_type)`

Compute statistical significance between two data sets. Args: data1: First data set data2: Second data set test_type: Type of statistical test ('ttest', 'mannwhitney', 'ks') Returns: Dictionary containing test statistics and p-value

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/metrics.py

:language: python
:pyobject: compute_statistical_significance
:linenos:
```

### `compute_robustness_metrics(nominal_performance, perturbed_performances, metric_names)`

Compute robustness metrics comparing nominal vs perturbed performance. Args: nominal_performance: Performance metrics for nominal conditions perturbed_performances: List of performance metrics under perturbations metric_names: Optional list of metric names to analyze Returns: Dictionary of robustness metrics for each performance metric

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/metrics.py
:language: python
:pyobject: compute_robustness_metrics
:linenos:
```

### `compute_comprehensive_metrics(states, controls, time_vector, reference_states, reference_controls)`

Compute metrics for control system analysis. Args: states: State trajectory matrix controls: Control signal vector time_vector: Time vector reference_states: Optional reference state trajectory reference_controls: Optional reference control signals Returns: Dictionary containing metrics

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/metrics.py

:language: python
:pyobject: compute_comprehensive_metrics
:linenos:
```

---

## Dependencies This module imports: - `from typing import Dict, List, Tuple, Any, Optional, Union`
- `import numpy as np`
- `from scipy import stats`
- `import warnings` ## Usage Examples ### Compute All Metrics for a Simulation ```python
from src.benchmarks.metrics import compute_all_metrics
from src.simulation.engines.simulation_runner import run_simulation
from src.controllers.factory import create_smc_for_pso, SMCType
from src.plant.models.simplified import SimplifiedDynamics # Run simulation
controller = create_smc_for_pso(SMCType.CLASSICAL, [10, 8, 15, 12, 50, 5])
dynamics = SimplifiedDynamics() result = run_simulation( controller=controller, dynamics_model=dynamics, initial_state=[0.1, 0.05, 0, 0, 0, 0], sim_time=10.0, dt=0.01
) # Compute metrics
metrics = compute_all_metrics( t=result.time, x=result.states, u=result.control, max_force=100.0, include_advanced=True
) # Access metrics
print("Control Performance:")
print(f" ISE: {metrics['ise']:.4f}")
print(f" ITAE: {metrics['itae']:.4f}")
print(f" RMS Control: {metrics['rms_control']:.4f}") print("
Stability Analysis:")
print(f" Settling Time: {metrics['settling_time']:.3f}s")
print(f" Overshoot: {metrics['overshoot']:.2f}%")
print(f" Damping Ratio: {metrics['damping_ratio']:.3f}") print("
Constraint Violations:")
print(f" Saturation Count: {metrics['saturation_count']}")
print(f" Saturation Severity: {metrics['saturation_severity']:.4f}")
``` ### Individual Metric Computation ```python

from src.benchmarks.metrics.control_metrics import compute_ise, compute_itae
from src.benchmarks.metrics.stability_metrics import compute_overshoot, compute_settling_time
from src.benchmarks.metrics.constraint_metrics import count_control_violations # Control metrics
ise = compute_ise(result.time, result.states)
itae = compute_itae(result.time, result.states) # Stability metrics
overshoot = compute_overshoot(result.states[:, 0]) # First angle
settling_time = compute_settling_time(result.time, result.states, threshold=0.02) # Constraint violations
violations, severity, peak = count_control_violations(result.control, max_force=100.0) print(f"ISE: {ise:.4f}, ITAE: {itae:.4f}")
print(f"Overshoot: {overshoot:.2f}%, Settling: {settling_time:.3f}s")
print(f"Violations: {violations}, Severity: {severity:.4f}, Peak: {peak:.2f}")
``` ### Custom Metric: Chattering Index ```python
import numpy as np def compute_chattering_index(u, dt): """Quantify control chattering.""" # Total variation of control signal tv = np.sum(np.abs(np.diff(u))) * dt return tv chattering = compute_chattering_index(result.control, dt=0.01)
print(f"Chattering Index: {chattering:.4f}") # Compare chattering across controllers
controllers = { 'Classical': create_smc_for_pso(SMCType.CLASSICAL, [10, 8, 15, 12, 50, 5]), 'STA': create_smc_for_pso(SMCType.SUPER_TWISTING, [25, 10, 15, 12, 20, 15]),
} chattering_results = {}
for name, ctrl in controllers.items(): result = run_simulation(ctrl, dynamics, [0.1, 0.05, 0, 0, 0, 0], 10.0, 0.01) chattering_results[name] = compute_chattering_index(result.control, 0.01) for name, ci in chattering_results.items(): print(f"{name} Chattering: {ci:.4f}")
``` ### Energy-Based Metrics ```python
# example-metadata:

# runnable: false #

Track energy conservation (for unforced natural dynamics)

def compute_energy_drift(result, dynamics): """Measure energy drift as validation check.""" energies = [dynamics.compute_total_energy(x) for x in result.states] initial_energy = energies[0] drift = np.abs(np.array(energies) - initial_energy) / initial_energy * 100 max_drift = np.max(drift) mean_drift = np.mean(drift) return {'max_drift_%': max_drift, 'mean_drift_%': mean_drift} energy_metrics = compute_energy_drift(result, dynamics)
print(f"Energy drift: {energy_metrics['max_drift_%']:.3f}% (max), " f"{energy_metrics['mean_drift_%']:.3f}% (mean)")
``` ### Batch Metric Computation for Trials ```python
from src.benchmarks.metrics import compute_all_metrics # Compute metrics for multiple trials
trials_results = [] # List of simulation results from multiple runs metrics_collection = []
for result in trials_results: metrics = compute_all_metrics(result.time, result.states, result.control, 100.0) metrics_collection.append(metrics) # Aggregate statistics
import pandas as pd
df = pd.DataFrame(metrics_collection) print("Metric Statistics Across Trials:")
print(df[['ise', 'settling_time', 'overshoot', 'rms_control']].describe())
``` **See:** {doc}`../../../performance_metrics/metric_definitions` 
