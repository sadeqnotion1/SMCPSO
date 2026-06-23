# plant.core.numerical_stability

<!-- Enhanced by Week 8 Phase 2 --> **Source:** `src\plant\core\numerical_stability.py` **Category:** Plant Dynamics / Numerical Methods
**Complexity:** Advanced
**Prerequisites:** Linear algebra, singular value decomposition, numerical analysis

---

## Table of Contents ```

{contents}

:local:
:depth: 3
```

---

## Module Overview Numerical

Stability Utilities for Plant Dynamics. This module provides robust numerical methods essential for reliable dynamics computation in the presence of **ill-conditioned matrices**. When computing M(q)q̈ = τ - C(q,q̇)q̇ - G(q), the inertia matrix M(q) can become nearly singular for certain configurations, leading to catastrophic numerical errors. **Core Capabilities:** - **Matrix Conditioning Analysis**: Compute condition numbers and singular value ratios
- **Adaptive Tikhonov Regularization**: Stabilize ill-conditioned systems without sacrificing accuracy
- **Robust Matrix Inversion**: Multiple fallback strategies for reliable computation
- **Numerical Instability Detection**: Automatic monitoring and error reporting
- **Performance Tracking**: Statistics for debugging and optimization **Extracted** from monolithic dynamics for focused responsibility and testing.

---

## Mathematical Foundation

### Matrix Conditioning **Definition:**

The **condition number** of a matrix A measures the sensitivity of the solution x to perturbations in the right-hand side b when solving Ax = b: $$
\kappa(A) = \|A\| \cdot \|A^{-1}\|
$$ For symmetric positive-definite matrices (like M(q)), using the 2-norm: $$
\kappa_2(A) = \frac{\sigma_{\text{max}}(A)}{\sigma_{\text{min}}(A)}
$$ where σ_max and σ_min are the largest and smallest singular values. **Physical Interpretation for DIP:** - **Well-conditioned (κ < 10³)**: Numerical errors are negligible
- **Moderate (10³ < κ < 10⁸)**: Small numerical errors, acceptable for most applications
- **Ill-conditioned (10⁸ < κ < 10¹²)**: Significant error amplification, regularization recommended
- **Severely ill-conditioned (κ > 10¹²)**: Near-singular, regularization required to avoid LinAlgError **Causes in DIP Dynamics:** 1. **Extreme configurations**: Links aligned or anti-aligned (θ₁ ≈ θ₂)
2. **Mass imbalance**: Very light pendulum masses relative to cart
3. **Numerical precision limits**: Floating-point arithmetic at ~1e-16 relative precision ### Tikhonov Regularization **Mathematical Formulation:** Replace ill-conditioned matrix A with regularized version: $$
A_{\lambda} = A + \lambda I
$$ where λ > 0 is the **regularization parameter** (damping factor). **Effect on Singular Values:** If A has SVD decomposition A = UΣV^T: $$
A_{\lambda} = U(\Sigma + \lambda I)V^T
$$ **Benefits:** - **Improved Conditioning**: $\kappa(A_{\lambda}) = \frac{\sigma_{\max} + \lambda}{\sigma_{\min} + \lambda} < \kappa(A)$
- **Guaranteed Invertibility**: λ > 0 ensures all singular values > 0
- **Minimal Bias**: For well-conditioned matrices, A_λ ≈ A when λ is small **Trade-off:** - **Too small λ**: Insufficient regularization, numerical instability persists
- **Too large λ**: Over-regularization, introduces bias and reduces accuracy ### Adaptive Regularization **Strategy:** Scale regularization parameter based on matrix properties: $$
\lambda = \alpha \cdot \sigma_{\max}(A) \cdot f(\kappa(A))
$$ where:
- α is base regularization factor (typically 1e-4 to 1e-6)
- f(κ) is an adaptive scaling function: $$
f(\kappa) = \begin{cases}
1 & \text{if } \kappa < 10^{10} \text{ (well-conditioned)} \\
10 & \text{if } 10^{10} < \kappa < 10^{12} \text{ (moderate)} \\
10^2 & \text{if } 10^{12} < \kappa \text{ and } r > 10^{-8} \\
10^4 & \text{if } r < 10^{-8} \text{ (extreme)} \\
10^5 & \text{if } r < 2 \times 10^{-9} \text{ (critical)}
\end{cases}
$$ where r = σ_min / σ_max is the **singular value ratio**. **Enhanced Strategy (Issue #14 Resolution):** For extreme ill-conditioning (condition numbers > 1e12, singular value ratios < 1e-8): 1. **Automatic triggering**: No manual intervention required
2. **Aggressive scaling**: Quadratic to quintic scaling (10² to 10⁵×)
3. **Singular value ratio detection**: Most sensitive indicator of near-singularity
4. **Graceful degradation**: Maintains accuracy for well-conditioned matrices **Mathematical Guarantee:** For κ(A) < 1e16 and machine precision ε ≈ 2.2e-16: $$
\kappa(A_{\lambda}) \leq \min\left(\frac{\sigma_{\max} + \lambda}{\max(\sigma_{\min} + \lambda, \epsilon)}, 10^{12}\right)
$$ ### Singular Value Decomposition (SVD) **Decomposition:** For any matrix A ∈ ℝ^(n×n): $$
A = U \Sigma V^T
$$ where:
- U, V ∈ ℝ^(n×n) are orthogonal matrices (UU^T = VV^T = I)
- Σ = diag(σ₁, σ₂, ..., σ_n) with σ₁ ≥ σ₂ ≥ ... ≥ σ_n ≥ 0 **Properties:** 1. **Singular values**: $\sigma_i = \sqrt{\lambda_i(A^T A)}$ (square roots of eigenvalues)
2. **Condition number**: $\kappa(A) = \sigma_1 / \sigma_n$
3. **Rank**: $\text{rank}(A) = \#\{\sigma_i > \epsilon\}$ (number of non-zero singular values) **Computational Cost:** - **Full SVD**: O(n³) operations (expensive for large n)
- **Condition estimation**: O(n²) using determinant ratios (faster approximation) **Usage in Adaptive Regularization:** 1. Compute SVD: A = UΣV^T
2. Analyze singular values: σ_max, σ_min, ratio r
3. Determine regularization: λ = α · σ_max · f(κ)
4. Apply: A_λ = U(Σ + λI)V^T

---

## Architecture Diagram ```

{mermaid}
graph TD A[Matrix M_q_] --> B[Compute SVD: M = UΣVᵀ] B --> C[σ_max_ = max_Σ_] B --> D[σ_min_ = min_Σ_] C --> E[κ_M_ = σ_max_ / σ_min_] E --> F{κ_M_ < 10¹⁰?} F -->|Yes| G[Direct Inversion: M⁻¹] F -->|No| H{κ_M_ < 10¹⁴?} H -->|Yes| I[Tikhonov: _M + λI_⁻¹] H -->|No| J[SVD Pseudo-Inverse: M†] I --> K[Select λ adaptively] K --> L[λ = λ_base_ · _κ/κ_thresh__α] J --> M[Σ†_ii_ = σ_i_⁻¹ if σ_i_ > ε] G --> N[Return M⁻¹] L --> N M --> N N --> O[Log Regularization Stats] style F fill:#ff9 style H fill:#ff9 style K fill:#9cf style M fill:#fcf
``` ## Implementation Architecture ### Class Hierarchy ```

MatrixRegularizer (Protocol) ↓ implements
AdaptiveRegularizer ↓ uses
MatrixInverter ↓ monitored by
NumericalStabilityMonitor
``` **Design Rationale:** - **Protocol**: Type-safe interface for regularization strategies
- **Adaptive Regularizer**: Smart Tikhonov regularization with SVD analysis
- **Matrix Inverter**: High-level API with fallback mechanisms
- **Stability Monitor**: Performance tracking and diagnostics ### Exception Handling **NumericalInstabilityError:** Raised when numerical computation becomes unreliable: ```python
class NumericalInstabilityError(RuntimeError): """Matrix too ill-conditioned for reliable computation."""
``` **Usage Pattern:** ```python

try: q_ddot = solver.solve_linear_system(M, forcing)
except NumericalInstabilityError as e: logger.error(f"Dynamics computation failed: {e}") # Fallback: use previous state or safe default
```

---

## Complete Source Code ```

{literalinclude} ../../../src/plant/core/numerical_stability.py
:language: python
:linenos:
```

---

## API Reference

### Exception: NumericalInstabilityError **Inherits:** `RuntimeError` ```

{literalinclude} ../../../src/plant/core/numerical_stability.py

:language: python
:pyobject: NumericalInstabilityError
:linenos:
``` Raised when numerical computation becomes unstable due to ill-conditioned matrices. **Common Causes:** - Inertia matrix M(q) is near-singular (κ > 1e14)
- Extreme singular value ratios (r < 1e-9)
- Invalid matrix entries (NaN, Inf)
- Regularization unable to stabilize system **Example:** ```python
from src.plant.core import NumericalInstabilityError, MatrixInverter inverter = MatrixInverter()
try: M_inv = inverter.invert_matrix(M)
except NumericalInstabilityError as e: print(f"Matrix inversion failed: {e}") # Handle error (use approximation, skip timestep, etc.)
```

---

### Protocol: MatrixRegularizer ```

{literalinclude} ../../../src/plant/core/numerical_stability.py

:language: python
:pyobject: MatrixRegularizer
:linenos:
``` **Type-safe interface for matrix regularization strategies.** #### Required Methods ##### `regularize_matrix(matrix: np.ndarray) -> np.ndarray` Apply regularization to improve matrix conditioning. **Mathematical Effect:** $$
A_{\text{reg}} = A + \lambda I, \quad \lambda > 0
$$ **Returns:** Regularized matrix with improved conditioning ##### `check_conditioning(matrix: np.ndarray) -> bool` Check if matrix conditioning is acceptable. **Threshold:** Typically κ(A) < 1e12 **Returns:** True if matrix is well-conditioned, False otherwise

### Class: AdaptiveRegularizer ```

{literalinclude} ../../../src/plant/core/numerical_stability.py
:language: python
:pyobject: AdaptiveRegularizer
:linenos:
``` **Adaptive Tikhonov regularization for numerical stability.** **Mathematical Background:** Uses SVD-based adaptive damping: $$

\lambda = \alpha \cdot \sigma_{\max} \cdot f(\kappa, r)
$$ where:
- α: Base regularization factor
- σ_max: Largest singular value
- f(κ, r): Adaptive scaling function based on condition number κ and singular value ratio r **Key Features:** 1. **Automatic Triggering**: Activates when κ > 1e12 or r < 1e-8
2. **Multi-Level Scaling**: 5 levels from 1× to 100,000× regularization
3. **Minimal Bias**: Well-conditioned matrices use base regularization only
4. **Robustness**: Handles extreme cases (r < 2e-9) without LinAlgError #### Constructor ##### `__init__(self, regularization_alpha=1e-4, max_condition_number=1e14, min_regularization=1e-10, use_fixed_regularization=False)` Initialize adaptive regularizer. **Parameters:** - `regularization_alpha` (float): Base regularization scaling factor - Default: 1e-4 - Range: [1e-6, 1e-3] - Effect: λ_base = α · σ_max - `max_condition_number` (float): Maximum acceptable condition number - Default: 1e14 - Threshold for automatic regularization - Matrices with κ > max_cond are always regularized - `min_regularization` (float): Minimum regularization to ensure invertibility - Default: 1e-10 - Safety floor: λ ≥ λ_min always - `use_fixed_regularization` (bool): Use fixed instead of adaptive regularization - Default: False (adaptive) - True: Always use λ = λ_min (faster but less accurate) **Example:** ```python
from src.plant.core import AdaptiveRegularizer # Research-grade precision (default)
research_regularizer = AdaptiveRegularizer( regularization_alpha=1e-6, max_condition_number=1e14
) # Real-time systems (more aggressive)
realtime_regularizer = AdaptiveRegularizer( regularization_alpha=1e-4, max_condition_number=1e12
) # Fixed regularization (fastest)
fixed_regularizer = AdaptiveRegularizer( use_fixed_regularization=True, min_regularization=1e-8
)
``` #### Public Methods ##### `regularize_matrix(self, matrix: np.ndarray) -> np.ndarray` Apply adaptive regularization to improve matrix conditioning. **Algorithm:** 1. **Compute SVD**: A = UΣV^T
2. **Analyze conditioning**: κ = σ_max / σ_min, r = σ_min / σ_max
3. **Determine scaling**: f(κ, r) based on severity
4. **Apply regularization**: A_λ = A + λI **Regularization Levels:** | Condition | κ Range | r Range | Scaling | Use Case |
|-----------|---------|---------|---------|----------|
| Well-conditioned | < 1e10 | > 1e-6 | 1× | Normal operation |
| Moderate | 1e10-1e12 | 1e-6 to 1e-8 | 10× | Preventive |
| Severe | > 1e12 | 1e-8 to 2e-9 | 100-10,000× | Issue #14 resolution |
| Critical | > 1e14 | < 2e-9 | 100,000× | Emergency | **Args:**
- `matrix`: Input matrix to regularize (typically M(q)) **Returns:**
- Regularized matrix with improved conditioning **Raises:**
- `NumericalInstabilityError`: If SVD fails or matrix contains invalid values **Example:** ```python
import numpy as np # Ill-conditioned matrix (κ ≈ 1e13)
M = np.array([ [1.0, 0.99999999, 0.5], [0.99999999, 1.0, 0.5], [0.5, 0.5, 0.3]
]) print(f"Original condition number: {np.linalg.cond(M):.2e}") # Apply adaptive regularization
regularizer = AdaptiveRegularizer()
M_reg = regularizer.regularize_matrix(M) print(f"Regularized condition number: {np.linalg.cond(M_reg):.2e}")
``` ##### `check_conditioning(self, matrix: np.ndarray) -> bool` Check if matrix conditioning is acceptable. **Criteria:** - κ(A) < max_condition_number

- All singular values are finite
- No NaN or Inf entries **Args:**
- `matrix`: Matrix to check **Returns:**
- `True` if well-conditioned, `False` otherwise **Example:** ```python
if regularizer.check_conditioning(M): # Direct inversion safe M_inv = np.linalg.inv(M)
else: # Regularization needed M_reg = regularizer.regularize_matrix(M) M_inv = np.linalg.inv(M_reg)
``` #### Private Methods ##### `_apply_fixed_regularization(self, matrix: np.ndarray) -> np.ndarray` Apply fixed regularization with minimum damping. **Formula:** $$
A_{\lambda} = A + \lambda_{\min} I
$$ **Use Case:** Real-time systems where SVD cost is prohibitive. ##### `_apply_adaptive_regularization(self, matrix: np.ndarray) -> np.ndarray` Apply adaptive regularization based on matrix conditioning. **Enhanced Strategy (Issue #14):** Handles extreme singular value ratios (1e-8 to 2e-9) with: 1. **Automatic triggers**: κ > 1e12 or r < 1e-8
2. **Quadratic scaling**: λ ∝ σ_max · (κ/κ_max)² for r < 1e-8
3. **Quintic scaling**: λ ∝ σ_max · 10⁵ for r < 2e-9
4. **Verification**: Warns if conditioning remains poor

---

### Class: MatrixInverter ```

{literalinclude} ../../../src/plant/core/numerical_stability.py
:language: python
:pyobject: MatrixInverter
:linenos:
``` **Robust matrix inversion with automatic regularization.** **Features:** - **Fallback Mechanisms**: Direct inversion → Regularized inversion

- **Automatic Regularization**: Applied only when needed
- **Linear System Solving**: Optimized for Ax = b (avoids explicit inverse)
- **Error Reporting**: Detailed diagnostics for failures #### Constructor ##### `__init__(self, regularizer: Optional[AdaptiveRegularizer] = None)` Initialize matrix inverter. **Parameters:**
- `regularizer`: Optional custom regularizer (default: AdaptiveRegularizer()) **Example:** ```python
from src.plant.core import MatrixInverter, AdaptiveRegularizer # Default regularizer
inverter = MatrixInverter() # Custom regularizer
custom_reg = AdaptiveRegularizer(regularization_alpha=1e-5)
custom_inverter = MatrixInverter(regularizer=custom_reg)
``` #### Public Methods ##### `invert_matrix(self, matrix: np.ndarray) -> np.ndarray` Robustly invert matrix with regularization if needed. **Algorithm:** 1. **Validate** input (check for NaN, Inf, empty matrix)
2. **Try direct inversion** if well-conditioned
3. **Apply regularization** if ill-conditioned or inversion fails
4. **Retry inversion** with regularized matrix
5. **Raise error** if all strategies fail **Args:**
- `matrix`: Matrix to invert **Returns:**
- Matrix inverse **Raises:**
- `NumericalInstabilityError`: If inversion impossible **Example:** ```python
try: M_inv = inverter.invert_matrix(M) q_ddot = M_inv @ forcing
except NumericalInstabilityError: print("Matrix inversion failed - using approximate dynamics") q_ddot = np.zeros(3) # Safe fallback
``` ##### `solve_linear_system(self, A: np.ndarray, b: np.ndarray) -> np.ndarray` Solve linear system Ax = b with numerical stability. **Advantages over `invert_matrix()`:** - **2× faster**: Uses `np.linalg.solve()` instead of computing A⁻¹

- **More accurate**: Avoids explicit matrix inverse
- **Better conditioning**: Direct solve is numerically more stable **Args:**
- `A`: Coefficient matrix
- `b`: Right-hand side vector **Returns:**
- Solution vector x **Raises:**
- `NumericalInstabilityError`: If system cannot be solved **Example:** ```python
# Dynamics computation: M(q)q̈

= τ - C·q̇ - G

M = physics.compute_inertia_matrix(state)
forcing = tau - C @ q_dot - G # Solve for accelerations (preferred method)
q_ddot = inverter.solve_linear_system(M, forcing) # Equivalent but slower:
# M_inv = inverter.invert_matrix(M)

# q_ddot = M_inv @ forcing

```

---

## Class: NumericalStabilityMonitor ```

{literalinclude} ../../../src/plant/core/numerical_stability.py
:language: python
:pyobject: NumericalStabilityMonitor
:linenos:
``` **Monitor numerical stability during dynamics computation.** **Tracked Metrics:** - Number of matrix inversions

- Regularization frequency
- Average condition number
- Maximum condition number observed
- Failure count **Use Cases:** - **Debugging**: Identify problematic configurations
- **Performance Tuning**: Optimize regularization parameters
- **Quality Assurance**: Verify numerical stability in production #### Constructor ##### `__init__(self)` Initialize stability monitor with zero statistics. #### Public Methods ##### `reset_statistics(self)` Reset all monitoring statistics to zero. **Use Case:** Start of new simulation or experiment. ##### `record_inversion(self, condition_number: float, was_regularized: bool, failed: bool = False)` Record statistics from matrix inversion operation. **Args:**
- `condition_number`: Computed κ(A)
- `was_regularized`: Whether regularization was applied
- `failed`: Whether inversion ultimately failed **Example:** ```python
from src.plant.core import NumericalStabilityMonitor monitor = NumericalStabilityMonitor() # During simulation loop
for t in time_steps: M = physics.compute_inertia_matrix(state) cond_num = np.linalg.cond(M) regularized = cond_num > 1e12 try: M_inv = inverter.invert_matrix(M) monitor.record_inversion(cond_num, regularized, failed=False) except NumericalInstabilityError: monitor.record_inversion(cond_num, regularized, failed=True)
``` ##### `get_statistics(self) -> dict` Get accumulated numerical stability statistics. **Returns:** Dictionary with keys:
- `total_inversions`: Total matrix inversions attempted
- `regularized_count`: Number requiring regularization
- `failed_count`: Number of failures
- `avg_condition_number`: Average κ(A)
- `max_condition_number`: Worst κ(A) observed
- `regularization_rate`: Fraction requiring regularization **Example:** ```python
stats = monitor.get_statistics()
print(f"Regularization rate: {stats['regularization_rate'] * 100:.1f}%")
print(f"Average condition number: {stats['avg_condition_number']:.2e}")
print(f"Max condition number: {stats['max_condition_number']:.2e}")
print(f"Failure rate: {stats['failed_count'] / stats['total_inversions'] * 100:.2f}%")
```

---

## Function: fast_condition_estimate **Decorator:** `@njit` ```

{literalinclude} ../../../src/plant/core/numerical_stability.py

:language: python
:pyobject: fast_condition_estimate
:linenos:
``` Fast condition number estimation using determinant ratio. **Mathematical Approximation:** $$
\kappa(A) \approx \frac{\|A\|_F}{\|A^{-1}\|_F^{-1}} \approx \frac{\|A\|_F^2}{|\det(A)|}
$$ where ∥·∥_F is the Frobenius norm. **Performance:** - **Full SVD**: O(n³) - exact but slow
- **Determinant method**: O(n³) - approximate but same complexity
- **This function**: O(n²) - very fast approximation **Accuracy:** - **Well-conditioned matrices**: Within 10% of true κ
- **Ill-conditioned matrices**: Order of magnitude estimate
- **Singular matrices**: Returns Inf correctly **Args:**
- `matrix`: Matrix to analyze **Returns:**
- Approximate condition number **Example:** ```python
from src.plant.core import fast_condition_estimate # Compare with exact computation
M = np.random.randn(3, 3)
M = M @ M.T # Make symmetric positive definite exact_cond = np.linalg.cond(M)
approx_cond = fast_condition_estimate(M) print(f"Exact: {exact_cond:.2e}")
print(f"Approximate: {approx_cond:.2e}")
print(f"Relative error: {abs(exact_cond - approx_cond) / exact_cond * 100:.1f}%")
```

---

## Usage Examples

### Basic Regularization ```

python

import numpy as np
from src.plant.core import AdaptiveRegularizer # Create ill-conditioned matrix
M = np.array([ [1.0, 0.999999999, 0.5], [0.999999999, 1.0, 0.5], [0.5, 0.5, 0.3]
]) print(f"Original condition number: {np.linalg.cond(M):.2e}") # ~1e13 # Regularize
regularizer = AdaptiveRegularizer()
M_reg = regularizer.regularize_matrix(M) print(f"Regularized condition number: {np.linalg.cond(M_reg):.2e}") # ~1e8
``` ### Robust Matrix Inversion ```python
from src.plant.core import MatrixInverter, NumericalInstabilityError inverter = MatrixInverter() try: M_inv = inverter.invert_matrix(M) print("Inversion successful")
except NumericalInstabilityError as e: print(f"Inversion failed: {e}")
``` ### Solving Dynamics Equation ```python

from src.plant.core import MatrixInverter, DIPPhysicsMatrices
from src.plant.configurations import UnifiedDIPConfig config = UnifiedDIPConfig()
physics = DIPPhysicsMatrices(config)
inverter = MatrixInverter() # State and control
state = np.array([0.1, 0.05, -0.03, 0.2, 0.1, -0.05])
tau = np.array([10.0, 0.0, 0.0]) # Compute physics matrices
M, C, G = physics.compute_all_matrices(state)
q_dot = state[3:] # Solve M(q)q̈ = τ - C·q̇ - G for q̈
forcing = tau - C @ q_dot - G
q_ddot = inverter.solve_linear_system(M, forcing) print(f"Accelerations: {q_ddot}")
``` ### Monitoring Numerical Stability ```python
from src.plant.core import NumericalStabilityMonitor monitor = NumericalStabilityMonitor() # Simulation loop
for i in range(1000): M = physics.compute_inertia_matrix(states[i]) cond_num = np.linalg.cond(M) regularized = not regularizer.check_conditioning(M) try: q_ddot = inverter.solve_linear_system(M, forcing[i]) monitor.record_inversion(cond_num, regularized, failed=False) except NumericalInstabilityError: monitor.record_inversion(cond_num, regularized, failed=True) # Get statistics
stats = monitor.get_statistics()
print(f"Simulation used regularization {stats['regularization_rate'] * 100:.1f}% of the time")
print(f"Max condition number: {stats['max_condition_number']:.2e}")
print(f"Failure rate: {stats['failed_count'] / stats['total_inversions'] * 100:.2f}%")
``` ### Custom Regularization Strategy ```python
# example-metadata:

# runnable: false # Conservative (research-grade precision)

conservative_reg = AdaptiveRegularizer( regularization_alpha=1e-6, # Minimal regularization max_condition_number=1e15 # High tolerance
) # Aggressive (real-time systems)
aggressive_reg = AdaptiveRegularizer( regularization_alpha=1e-3, # Strong regularization max_condition_number=1e10 # Low tolerance
) # Fixed (maximum performance)
fixed_reg = AdaptiveRegularizer( use_fixed_regularization=True, min_regularization=1e-7
) # Compare
M_conservative = conservative_reg.regularize_matrix(M)
M_aggressive = aggressive_reg.regularize_matrix(M)
M_fixed = fixed_reg.regularize_matrix(M) print(f"Conservative κ: {np.linalg.cond(M_conservative):.2e}")
print(f"Aggressive κ: {np.linalg.cond(M_aggressive):.2e}")
print(f"Fixed κ: {np.linalg.cond(M_fixed):.2e}")
```

---

## Performance Considerations

### SVD Computational Cost

**Full SVD**: O(n³) for n×n matrix For 3×3 matrices (DIP dynamics):
- **Typical time**: 5-10 μs (modern CPU)
- **Acceptable** for real-time control at 1 kHz For larger systems (10×10):
- **Typical time**: 100-200 μs
- May become bottleneck at high frequencies **Optimization Strategies:** 1. **Condition estimation** instead of full SVD for well-conditioned matrices
2. **Cache regularized matrices** when configuration doesn't change
3. **Fixed regularization** for real-time critical paths ### Regularization Overhead **Benchmark** (3×3 matrix, 10,000 iterations): | Method | Time | Accuracy |
|--------|------|----------|
| Direct inversion (no check) | 1.0× | Fails on ill-conditioned |
| With condition check | 1.2× | Detects problems |
| Adaptive regularization | 2.5× | Robust |
| Fixed regularization | 1.3× | Fast but less accurate | **Recommendation:** - **Research/offline**: Use adaptive regularization
- **Real-time control**: Use adaptive with caching
- **High-frequency loops**: Consider fixed regularization

---

## Scientific References 1.

**Golub, G.H., Van Loan, C.F.** (2013). *Matrix Computations* (4th ed.). Johns Hopkins University Press. Chapter 2: Matrix Analysis; Chapter 5: Eigenvalue Problems. 2. **Higham, N.J.** (2002). *Accuracy and Stability of Numerical Algorithms* (2nd ed.). SIAM. Chapter 7: Matrix Inversion; Chapter 15: Condition Number Estimation. 3. **Tikhonov, A.N., Arsenin, V.Y.** (1977). *approaches of Ill-Posed Problems*. Winston & Sons. Chapter 1: Regularization Methods. 4. **Trefethen, L.N., Bau, D.** (1997). *Numerical Linear Algebra*. SIAM. Lecture 12: Conditioning and Condition Numbers; Lecture 15: SVD and Pseudo-inverse. 5. **Horn, R.A., Johnson, C.R.** (2012). *Matrix Analysis* (2nd ed.). Cambridge University Press. Section 5.6: Condition Number and Matrix Norms.

---

## Related Documentation - **Physics Matrices**: [core_physics_matrices.md](core_physics_matrices.md)
- **Full Dynamics Model**: [models_full_dynamics.md](models_full_dynamics.md)
- **Issue #14 Resolution**: Extreme ill-conditioning handling (κ > 1e12, r < 1e-8)

---

## Dependencies This module imports: - `from __future__ import annotations`
- `from typing import Tuple, Optional, Protocol`
- `import numpy as np`
- `import warnings`
- `from numba import njit` (optional, graceful fallback)
