# analysis.validation.cross_validation

**Source:** `src\analysis\validation\cross_validation.py`

## Module Overview Cross-validation

methods for analysis validation and model selection

.

## Advanced Mathematical Theory

### Cross-Validation


2. For fold $i$: Train on $D \setminus D_i$, test on $D_i$
3. Compute error: $\text{CV}(k) = \frac{1}{k}\sum_{i=1}^k \text{Err}_i$ **Leave-One-Out (LOO):** ```{math}
\text{CV}_{LOO} = \frac{1}{n}\sum_{i=1}^n (y_i - \hat{y}_{-i})^2
``` Where $\hat{y}_{-i}$ is prediction without sample $i$. ### Bias-Variance Tradeoff **Prediction error decomposition:** ```{math}
\text{Err}(x) = \text{Bias}^2 + \text{Variance} + \sigma^2
``` **Bias:** ```{math}

\text{Bias}(\hat{f}(x)) = E[\hat{f}(x)] - f(x)
``` **Variance:** ```{math}
\text{Variance}(\hat{f}(x)) = E[(\hat{f}(x) - E[\hat{f}(x)])^2]
``` ### Stratified Cross-Validation **Preserve class proportions:** ```{math}

\frac{n_c^{(i)}}{|D_i|} \approx \frac{n_c}{n} \quad \forall c, i
``` Where $n_c^{(i)}$ is count of class $c$ in fold $i$. ### Time Series Cross-Validation **Forward chaining:** ```{math}
\begin{align}
\text{Fold 1: } & \text{Train}(1:m), \text{Test}(m+1) \\
\text{Fold 2: } & \text{Train}(1:m+1), \text{Test}(m+2) \\
& \vdots \\
\text{Fold } k: & \text{Train}(1:m+k-1), \text{Test}(m+k)
\end{align}
``` ### AIC and BIC **Akaike Information Criterion:** ```{math}

\text{AIC} = -2\ln(L) + 2p
``` **Bayesian Information Criterion:** ```{math}
\text{BIC} = -2\ln(L) + p\ln(n)
``` Where $L$ is likelihood, $p$ is parameters, $n$ is samples. ### Generalized Cross-Validation **GCV score:** ```{math}

\text{GCV}(\lambda) = \frac{\|y - \hat{y}^{(\lambda)}\|^2}{(1 - \text{tr}(S^{(\lambda)})/n)^2}
``` Where $S^{(\lambda)}$ is smoother matrix. ## Architecture Diagram ```{mermaid}
graph TD A[Dataset D] --> B[Split into k Folds] B --> C[Fold 1] B --> D[Fold 2] B --> E[...] B --> F[Fold k] C --> G[Iteration 1] D --> H[Iteration 2] F --> I[Iteration k] G --> J[Train: D \ D₁] J --> K[Test: D₁] K --> L[Error₁] H --> M[Train: D \ D₂] M --> N[Test: D₂] N --> O[Error₂] I --> P[Train: D \ Dₖ] P --> Q[Test: Dₖ] Q --> R[Errorₖ] L --> S[CV = 1/k Σ Errorᵢ] O --> S R --> S S --> T{Select Model} T --> U[Min CV Error] style B fill:#9cf style S fill:#ff9 style U fill:#9f9
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
This module provides cross-validation techniques for validating
analysis methods, selecting models, and assessing generalization performance
in control engineering applications. ## Complete Source Code ```{literalinclude} ../../../src/analysis/validation/cross_validation.py
:language: python
:linenos:
```

---

## Classes

### `KFold`

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/cross_validation.py

:language: python
:pyobject: KFold
:linenos:
``` #### Methods (2) ##### `__init__(self, n_splits, shuffle, random_state)` [View full source →](#method-kfold-__init__) ##### `split(self, X)` [View full source →](#method-kfold-split)

### `StratifiedKFold`

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/cross_validation.py
:language: python
:pyobject: StratifiedKFold
:linenos:
``` #### Methods (2) ##### `__init__(self, n_splits, shuffle, random_state)` [View full source →](#method-stratifiedkfold-__init__) ##### `split(self, X, y)` [View full source →](#method-stratifiedkfold-split)

### `TimeSeriesSplit`

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/cross_validation.py

:language: python
:pyobject: TimeSeriesSplit
:linenos:
``` #### Methods (2) ##### `__init__(self, n_splits)` [View full source →](#method-timeseriessplit-__init__) ##### `split(self, X)` [View full source →](#method-timeseriessplit-split)

### `LeaveOneOut`

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/cross_validation.py
:language: python
:pyobject: LeaveOneOut
:linenos:
``` #### Methods (1) ##### `split(self, X)` [View full source →](#method-leaveoneout-split)

### `CrossValidationConfig`

Configuration for cross-validation methods.

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/cross_validation.py

:language: python
:pyobject: CrossValidationConfig
:linenos:
```

### `CrossValidator`

**Inherits from:** `StatisticalValidator` cross-validation framework.

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/cross_validation.py
:language: python
:pyobject: CrossValidator
:linenos:
``` #### Methods (23) ##### `__init__(self, config)` Initialize cross-validator. [View full source →](#method-crossvalidator-__init__) ##### `validation_methods(self)` List of validation methods supported. [View full source →](#method-crossvalidator-validation_methods) ##### `validate(self, data)` Perform cross-validation analysis. [View full source →](#method-crossvalidator-validate) ##### `_preprocess_data(self, data)` Preprocess data for cross-validation. [View full source →](#method-crossvalidator-_preprocess_data) ##### `_create_lagged_features(self, data, n_lags)` Create lagged features from time series data. [View full source →](#method-crossvalidator-_create_lagged_features) ##### `_get_cv_splitter(self, X, y)` Get cross-validation splitter based on configuration. [View full source →](#method-crossvalidator-_get_cv_splitter) ##### `_perform_k_fold_validation(self, X, y, models, prediction_function)` Perform k-fold cross-validation. [View full source →](#method-crossvalidator-_perform_k_fold_validation) ##### `_perform_time_series_validation(self, X, y, models, prediction_function)` Perform time series cross-validation. [View full source →](#method-crossvalidator-_perform_time_series_validation) ##### `_perform_monte_carlo_validation(self, X, y, models, prediction_function)` Perform Monte Carlo cross-validation. [View full source →](#method-crossvalidator-_perform_monte_carlo_validation) ##### `_perform_nested_validation(self, X, y, models)` Perform nested cross-validation for unbiased performance estimation. [View full source →](#method-crossvalidator-_perform_nested_validation) ##### `_perform_model_comparison(self, X, y, models)` Perform statistical comparison between models. [View full source →](#method-crossvalidator-_perform_model_comparison) ##### `_perform_bias_variance_analysis(self, X, y, models, prediction_function)` Perform bias-variance decomposition analysis. [View full source →](#method-crossvalidator-_perform_bias_variance_analysis) ##### `_perform_learning_curve_analysis(self, X, y, models, prediction_function)` Perform learning curve analysis. [View full source →](#method-crossvalidator-_perform_learning_curve_analysis) ##### `_validate_single_model(self, X, y, model, cv_splitter)` Validate a single model using cross-validation. [View full source →](#method-crossvalidator-_validate_single_model) ##### `_validate_prediction_function(self, X, y, prediction_function, cv_splitter)` Validate a prediction function using cross-validation. [View full source →](#method-crossvalidator-_validate_prediction_function) ##### `_evaluate_model_on_split(self, model, X_train, y_train, X_test, y_test)` Evaluate model on a single train-test split. [View full source →](#method-crossvalidator-_evaluate_model_on_split) ##### `_evaluate_function_on_split(self, prediction_function, X_train, y_train, X_test, y_test)` Evaluate prediction function on a single train-test split. [View full source →](#method-crossvalidator-_evaluate_function_on_split) ##### `_train_and_predict(self, model, X_train, y_train, X_test)` Train model and make predictions. [View full source →](#method-crossvalidator-_train_and_predict) ##### `_compute_score(self, y_true, y_pred)` Compute score for predictions. [View full source →](#method-crossvalidator-_compute_score) ##### `_compute_overall_metrics(self, y_true, y_pred)` Compute overall metrics across all folds. [View full source →](#method-crossvalidator-_compute_overall_metrics) ##### `_compute_confidence_interval(self, scores)` Compute confidence interval for scores. [View full source →](#method-crossvalidator-_compute_confidence_interval) ##### `_analyze_learning_curve_convergence(self, train_sizes, test_scores)` Analyze convergence of learning curves. [View full source →](#method-crossvalidator-_analyze_learning_curve_convergence) ##### `_generate_validation_summary(self, results)` Generate overall validation summary. [View full source →](#method-crossvalidator-_generate_validation_summary)

---

## Functions

### `mean_squared_error(y_true, y_pred)`

Compute mean squared error.

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/cross_validation.py

:language: python
:pyobject: mean_squared_error
:linenos:
```

### `mean_absolute_error(y_true, y_pred)`

Compute mean absolute error.

#### Source Code ```

{literalinclude} ../../../src/analysis/validation/cross_validation.py
:language: python
:pyobject: mean_absolute_error
:linenos:
```

### `create_cross_validator(config)`

Factory function to create cross-validator. Parameters

config : Dict[str, Any], optional Configuration parameters Returns
-------
CrossValidator Configured cross-validator #### Source Code ```{literalinclude} ../../../src/analysis/validation/cross_validation.py
:language: python
:pyobject: create_cross_validator
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`
- `from typing import Dict, List, Optional, Tuple, Any, Union, Callable`
- `import numpy as np`
- `from scipy import stats`
- `import warnings`
- `from dataclasses import dataclass, field`
- `import itertools`
- `from ..core.interfaces import StatisticalValidator, AnalysisResult, AnalysisStatus, DataProtocol`
- `from ..core.data_structures import StatisticalTestResult, ConfidenceInterval`
