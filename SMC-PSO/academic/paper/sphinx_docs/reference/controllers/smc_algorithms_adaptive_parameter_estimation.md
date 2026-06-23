# controllers.smc.algorithms.adaptive.parameter_estimation

**Source:** `src\controllers\smc\algorithms\adaptive\parameter_estimation.py`

## Module Overview Parameter

and Uncertainty Estimation for Adaptive SMC

. Implements online estimation of system uncertainties and disturbance bounds


to improve adaptive gain selection and overall controller performance. Mathematical Background:
- Uncertainty bound estimation: η̂ = max{|disturbance|, model_error}
- Sliding mode observer: estimate unknown dynamics components
- Recursive least squares: parameter identification ## Advanced Mathematical Theory ### Uncertainty Parametrization **Model uncertainty:** ```{math}
\Delta(\vec{x}, t) = \vec{\phi}^T(\vec{x}) \vec{\theta} + \epsilon(t)
``` Where:
- $\vec{\phi}$: Known regressor (basis functions)
- $\vec{\theta}$: Unknown parameter vector
- $\epsilon$: Bounded residual ($|\epsilon| \leq \epsilon_{max}$) ### Recursive Least Squares (RLS) **Update law:** ```{math}
\begin{align}
\hat{\vec{\theta}}(k+1) &= \hat{\vec{\theta}}(k) + \mathbf{P}(k) \vec{\phi}(k) [y(k) - \vec{\phi}^T(k) \hat{\vec{\theta}}(k)] \\
\mathbf{P}(k+1) &= \mathbf{P}(k) - \frac{\mathbf{P}(k) \vec{\phi}(k) \vec{\phi}^T(k) \mathbf{P}(k)}{1 + \vec{\phi}^T(k) \mathbf{P}(k) \vec{\phi}(k)}
\end{align}
``` ### Persistent Excitation For parameter convergence, regressor must be **persistently exciting**: ```{math}

\alpha_1 \mathbf{I} \leq \int_t^{t+T} \vec{\phi}(\tau) \vec{\phi}^T(\tau) d\tau \leq \alpha_2 \mathbf{I}
``` For all $t \geq 0$ and some $T > 0$, $\alpha_2 > \alpha_1 > 0$. ### Gradient Estimation **Steepest descent:** ```{math}
\dot{\hat{\vec{\theta}}} = -\Gamma \vec{\phi}(\vec{x}) e
``` Where $e = y - \vec{\phi}^T \hat{\vec{\theta}}$ is prediction error. ### Lyapunov-Based Estimation **Candidate function:** ```{math}

V = \frac{1}{2} e^2 + \frac{1}{2} \tilde{\vec{\theta}}^T \Gamma^{-1} \tilde{\vec{\theta}}
``` **Derivative:** ```{math}
\dot{V} = e \dot{e} + \tilde{\vec{\theta}}^T \Gamma^{-1} \dot{\tilde{\vec{\theta}}}
``` Choosing $\dot{\hat{\vec{\theta}}} = \Gamma \vec{\phi} e$ yields $\dot{V} \leq 0$. ### Projection Algorithm **Constrained estimation:** ```{math}

\dot{\hat{\vec{\theta}}} = \text{Proj}(\hat{\vec{\theta}}, \Gamma \vec{\phi} e)
``` Ensures $\hat{\vec{\theta}} \in \Theta$ (admissible parameter set). ## Architecture Diagram ```{mermaid}
graph TD A[Measurement y] --> B[Prediction Error: e = y - φᵀθ̂] B --> C[Gradient: ∇θ = Γφe] C --> D[Update: θ̂_k+1_ = θ̂_k_ + Γφe] D --> E{Projection} E -->|In bounds| F[θ̂ ∈ Θ] E -->|Out bounds| G[Project to Θ] G --> F F --> H[Estimated Parameters θ̂] style B fill:#ff9 style H fill:#9f9
``` ## Usage Examples ### Example 1: Basic Initialization ```python

from src.controllers.smc.algorithms.adaptive import * # Initialize with configuration
config = {'parameter': 'value'}
instance = Component(config)
``` ### Example 2: Performance Tuning ```python
# Adjust parameters for better performance
optimized_params = tune_parameters(instance, target_performance)
``` ### Example 3: Integration with Controller ```python
# Use in complete control loop

controller = create_controller(ctrl_type, config)
result = simulate(controller, duration=5.0)
``` ### Example 4: Edge Case Handling ```python
try: output = instance.compute(state)
except ValueError as e: handle_edge_case(e)
``` ### Example 5: Performance Analysis ```python
# Analyze metrics

metrics = compute_metrics(result)
print(f"ITAE: {metrics.itae:.3f}")
``` ## Complete Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/parameter_estimation.py
:language: python
:linenos:
```

---

## Classes

### `UncertaintyEstimator`

Online uncertainty estimation for adaptive SMC. Estimates bounds on system uncertainties and disturbances

to improve adaptive gain selection. #### Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/parameter_estimation.py
:language: python
:pyobject: UncertaintyEstimator
:linenos:
``` #### Methods (8) ##### `__init__(self, window_size, forgetting_factor, initial_estimate, estimation_gain)` Initialize uncertainty estimator. [View full source →](#method-uncertaintyestimator-__init__) ##### `update_estimate(self, surface_value, surface_derivative, control_input, dt)` Update uncertainty estimate based on sliding surface behavior. [View full source →](#method-uncertaintyestimator-update_estimate) ##### `_compute_uncertainty_indicator(self, s, s_dot, u)` Compute uncertainty indicator from surface behavior. [View full source →](#method-uncertaintyestimator-_compute_uncertainty_indicator) ##### `get_uncertainty_bound(self)` Get current uncertainty bound estimate. [View full source →](#method-uncertaintyestimator-get_uncertainty_bound) ##### `get_confidence_interval(self, confidence)` Get confidence interval for uncertainty estimate. [View full source →](#method-uncertaintyestimator-get_confidence_interval) ##### `analyze_estimation_quality(self)` Analyze quality of uncertainty estimation. [View full source →](#method-uncertaintyestimator-analyze_estimation_quality) ##### `update_estimates(self, surface_value, adaptation_rate, dt)` Compatibility method for tests - maps to update_estimate with surface derivative. [View full source →](#method-uncertaintyestimator-update_estimates) ##### `current_estimates(self)` Current uncertainty estimates for test compatibility. [View full source →](#method-uncertaintyestimator-current_estimates)

### `ParameterIdentifier`

Online parameter identification using recursive least squares. Identifies unknown system parameters to improve model accuracy
and reduce uncertainty bounds. #### Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/parameter_estimation.py
:language: python
:pyobject: ParameterIdentifier
:linenos:
``` #### Methods (6) ##### `__init__(self, n_parameters, forgetting_factor, initial_covariance)` Initialize parameter identifier. [View full source →](#method-parameteridentifier-__init__) ##### `update_parameters(self, regressor, measurement)` Update parameter estimates using RLS algorithm. [View full source →](#method-parameteridentifier-update_parameters) ##### `get_parameter_estimates(self)` Get current parameter estimates. [View full source →](#method-parameteridentifier-get_parameter_estimates) ##### `get_parameter_covariance(self)` Get parameter covariance matrix. [View full source →](#method-parameteridentifier-get_parameter_covariance) ##### `get_parameter_confidence(self, confidence)` Get confidence intervals for parameters. [View full source →](#method-parameteridentifier-get_parameter_confidence) ##### `reset_identifier(self, initial_covariance)` Reset parameter identifier state. [View full source →](#method-parameteridentifier-reset_identifier)

### `CombinedEstimator`

Combined uncertainty estimation and parameter identification. Integrates uncertainty estimation with parameter identification

for improved adaptive SMC performance. #### Source Code ```{literalinclude} ../../../src/controllers/smc/algorithms/adaptive/parameter_estimation.py
:language: python
:pyobject: CombinedEstimator
:linenos:
``` #### Methods (4) ##### `__init__(self, n_parameters)` Initialize combined estimator. [View full source →](#method-combinedestimator-__init__) ##### `update_estimates(self, surface_value, surface_derivative, control_input, regressor, measurement, dt)` Update both uncertainty and parameter estimates. [View full source →](#method-combinedestimator-update_estimates) ##### `set_estimation_active(self, active)` Enable/disable online estimation. [View full source →](#method-combinedestimator-set_estimation_active) ##### `get_combined_analysis(self)` Get analysis of estimation performance. [View full source →](#method-combinedestimator-get_combined_analysis)

---

## Dependencies This module imports: - `from typing import List, Optional, Union, Dict, Any`
- `import numpy as np`
- `from collections import deque`
