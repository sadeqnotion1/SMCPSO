# analysis.performance.control_analysis

**Source:** `src\analysis\performance\control_analysis.py`

## Module Overview Linearisation

and controllability/observability analysis utilities

.

## Advanced Mathematical Theory

### Control System Performance


T(s) = \frac{G(s)C(s)}{1 + G(s)C(s)}
``` Where $G(s)$ is plant, $C(s)$ is controller. ### Frequency Response Analysis **Bode plot analysis:** ```{math}
\begin{align}
\text{Magnitude: } & |G(j\omega)| = \sqrt{\text{Re}^2(G(j\omega)) + \text{Im}^2(G(j\omega))} \\
\text{Phase: } & \angle G(j\omega) = \arctan\left(\frac{\text{Im}(G(j\omega))}{\text{Re}(G(j\omega))}\right)
\end{align}
``` ### Bandwidth and Settling Time **Bandwidth** $\omega_B$: Frequency where $|T(j\omega)| = \frac{1}{\sqrt{2}}|T(0)|$ **Relation to settling time:** ```{math}

t_s \approx \frac{4.6}{\zeta \omega_n} \approx \frac{3}{\omega_B}
``` ### Sensitivity Functions **Sensitivity:** ```{math}
S(s) = \frac{1}{1 + G(s)C(s)}
``` **Complementary sensitivity:** ```{math}

T(s) = \frac{G(s)C(s)}{1 + G(s)C(s)}
``` **Fundamental relation:** ```{math}
S(s) + T(s) = 1
``` ### Performance Bounds **Waterbed effect:** ```{math}

\int_0^\infty \ln|S(j\omega)| d\omega = \pi \sum \text{Re}(p_i)
``` Where $p_i$ are unstable poles of $G(s)C(s)$. ### Rise Time and Overshoot **Second-order approximation:** ```{math}
\begin{align}
t_r &\approx \frac{1.8}{\omega_n} \\
M_p &= e^{-\frac{\pi \zeta}{\sqrt{1-\zeta^2}}} \times 100\%
\end{align}
``` ## Architecture Diagram ```{mermaid}

graph TD A[Closed-Loop System] --> B[Transfer Function] B --> C[Frequency Response] C --> D[Bode Plot] D --> E[Gain Plot] D --> F[Phase Plot] E --> G[Bandwidth] F --> H[Phase Margin] B --> I[Sensitivity Analysis] I --> J[S(s) = 1/(1+GC)] I --> K[T(s) = GC/(1+GC)] J --> L{||S||∞ Check} K --> M{||T||∞ Check} L --> N[Disturbance Rejection] M --> O[Reference Tracking] A --> P[Time Response] P --> Q[Rise Time] P --> R[Settling Time] P --> S[Overshoot] style D fill:#9cf style I fill:#ff9 style N fill:#9f9 style O fill:#9f9
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

This module exposes helper functions to linearise the double inverted
pendulum dynamics at an equilibrium point and to construct the
controllability and observability matrices for a linear time‑invariant
(LTI) system. The Kalman rank criterion states that an LTI system is
controllable if and only if its controllability matrix has full rank
equal to the number of state variables【920100172589331†L79-L84】. An
analogous condition holds for observability. These functions aid in
assessing whether a given linearised model is suitable for state‐space
control or estimation design. ## Complete Source Code ```{literalinclude} ../../../src/analysis/performance/control_analysis.py
:language: python
:linenos:
```

---

## Classes

### `ControlAnalyzer`

Control analysis utilities for linearization and controllability assessment. This class provides a convenient interface to control-theoretic analysis
functions including linearization, controllability, and observability analysis. #### Source Code ```{literalinclude} ../../../src/analysis/performance/control_analysis.py
:language: python
:pyobject: ControlAnalyzer
:linenos:
``` #### Methods (6) ##### `__init__(self)` Initialize the control analyzer. [View full source →](#method-controlanalyzer-__init__) ##### `linearize_dynamics(dyn, x_eq, u_eq)` Linearize nonlinear dynamics around equilibrium point. [View full source →](#method-controlanalyzer-linearize_dynamics) ##### `controllability_matrix(A, B)` Compute controllability matrix for LTI system. [View full source →](#method-controlanalyzer-controllability_matrix) ##### `observability_matrix(A, C)` Compute observability matrix for LTI system. [View full source →](#method-controlanalyzer-observability_matrix) ##### `is_controllable(self, A, B)` Check if system is controllable using rank test. [View full source →](#method-controlanalyzer-is_controllable) ##### `is_observable(self, A, C)` Check if system is observable using rank test. [View full source →](#method-controlanalyzer-is_observable)

---

## Functions

### `linearize_dip(dyn, x_eq, u_eq)`

Linearise the nonlinear dynamics around an equilibrium point. Parameters

dyn : callable A function implementing the continuous‑time dynamics ``f(x, u)``.
x_eq : np.ndarray Equilibrium state vector at which to linearise.
u_eq : float Equilibrium control input. Returns
(A, B) : tuple of np.ndarray Continuous‑time state matrix ``A`` and input matrix ``B`` obtained via numerical differentiation of the dynamics. #### Source Code ```{literalinclude} ../../../src/analysis/performance/control_analysis.py
:language: python
:pyobject: linearize_dip
:linenos:
```

---

### `controllability_matrix(A, B)` Construct the controllability matrix of an LTI system. For an ``n``‑state system described by matrices ``A`` and ``B``, the
controllability matrix is defined as ``[B, AB, A^2B, …, A^{n-1}B]``.
The system is controllable if this matrix has full row rank equal to ``n``【920100172589331†L79-L84】. Parameters
----------
A : np.ndarray State transition matrix of shape ``(n, n)``.
B : np.ndarray Input matrix of shape ``(n, m)``. Returns
np.ndarray The controllability matrix of shape ``(n, n*m)``. #### Source Code ```{literalinclude} ../../../src/analysis/performance/control_analysis.py
:language: python
:pyobject: controllability_matrix
:linenos:
```

---

### `observability_matrix(A, C)` Construct the observability matrix of an LTI system. Given output matrix ``C`` of shape ``(p, n)``

, the observability

matrix is ``[C; CA; CA^2; …; CA^{n-1}]``. The system is observable
when this matrix has full column rank equal to ``n``【920100172589331†L79-L84】. Parameters
----------
A : np.ndarray State transition matrix of shape ``(n, n)``.
C : np.ndarray Output matrix of shape ``(p, n)``. Returns
np.ndarray Observability matrix of shape ``(p*n, n)``. #### Source Code ```{literalinclude} ../../../src/analysis/performance/control_analysis.py
:language: python
:pyobject: observability_matrix
:linenos:
```

---

### `check_controllability_observability(A, B, C)`

Check controllability and observability of an LTI system. Parameters
----------
A : np.ndarray State transition matrix ``(n, n)``.
B : np.ndarray Input matrix ``(n, m)``.
C : np.ndarray Output matrix ``(p, n)``. Returns
-------
(bool, bool) Tuple ``(is_controllable, is_observable)``. ``True`` when the corresponding rank test passes【920100172589331†L79-L84】. #### Source Code ```{literalinclude} ../../../src/analysis/performance/control_analysis.py
:language: python
:pyobject: check_controllability_observability
:linenos:
```

---

## Dependencies This module imports: - `from __future__ import annotations`

- `from typing import Tuple`
- `import numpy as np`
- `from src.controllers.mpc_controller import _numeric_linearize_continuous`
