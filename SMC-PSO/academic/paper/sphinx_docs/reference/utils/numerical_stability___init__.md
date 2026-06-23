# utils.numerical_stability.__init__

**Source:** `src\utils\numerical_stability\__init__.py`

## Module Overview Numerical

stability utilities for robust mathematical operations

. This module provides safe mathematical operations that protect against:


- Division by zero and near-zero denominators
- Negative arguments to sqrt and log
- Numerical overflow/underflow
- Catastrophic cancellation All operations use configurable epsilon thresholds tuned for control system
stability and optimization algorithm convergence. Example: >>> from src.utils.numerical_stability import safe_divide, safe_sqrt >>> result = safe_divide(1.0, 1e-15) # Protected division >>> root = safe_sqrt(-0.001) # Safe sqrt with negative protection ## Complete Source Code ```{literalinclude} ../../../src/utils/numerical_stability/__init__.py
:language: python
:linenos:
```

---

## Dependencies This module imports: - `from src.utils.numerical_stability.safe_operations import safe_divide, safe_reciprocal, safe_sqrt, safe_log, safe_exp, safe_power, safe_norm, safe_normalize, EPSILON_DIV, EPSILON_SQRT, EPSILON_LOG, EPSILON_EXP, is_safe_denominator, clip_to_safe_range`

## Advanced Mathematical Theory

### Numerical Stability for

Robust Computation Numerical stability utilities protect against common numerical errors in control systems and optimization algorithms.

#### Division by Zero Protection **Safe division:**
$$
\text{safe\_div}(a, b, \epsilon) = \frac{a}{\max(|b|, \epsilon)} \cdot \text{sign}(b)
$$ where $\epsilon = 10^{-10}$ (default, configurable). **Reciprocal:**
$$
\text{safe\_reciprocal}(x, \epsilon) = \frac{1}{\max(|x|, \epsilon)} \cdot \text{sign}(x)
$$ #### Square Root Protection **Safe square root:**
$$
\text{safe\_sqrt}(x) = \begin{cases}
\sqrt{x} & \text{if } x \geq 0 \\
\sqrt{|x|} & \text{if allow\_negative} \\
0 & \text{otherwise}
\end{cases}
$$ **Normalized safe sqrt:**
$$
\text{safe\_sqrt}(x, \epsilon) = \sqrt{\max(x, \epsilon)}
$$ #### Logarithm and Exponential Protection **Safe logarithm:**
$$
\text{safe\_log}(x, \epsilon) = \log(\max(x, \epsilon))
$$ Default: $\epsilon_{\log} = 10^{-10}$ **Safe exponential:**
$$
\text{safe\_exp}(x) = \exp(\text{clip}(x, -\text{MAX\_EXP}, \text{MAX\_EXP}))
$$ where $\text{MAX\_EXP} = 700$ to prevent overflow. #### Matrix Conditioning **Condition number:**
$$
\kappa(A) = \|A\| \cdot \|A^{-1}\|
$$ **Ill-conditioned detection:**
$$
\text{Ill-conditioned} = (\kappa(A) > 10^{12})
$$ **Regularization:**
$$
A_{\text{reg}} = A + \epsilon I
$$ where $\epsilon$ is chosen to bring $\kappa(A_{\text{reg}}) \approx 10^6$. ### Numerical Error Analysis **Machine epsilon:**
$$
\epsilon_{\text{machine}} \approx 2.22 \times 10^{-16} \quad \text{(double precision)}
$$ **Relative error:**
$$
\text{RelError} = \frac{|x_{\text{computed}} - x_{\text{exact}}|}{|x_{\text{exact}}|}
$$ **Acceptable tolerance:**
$$
\text{RelError} < 10^{-6} \quad \text{(typical for control systems)}
$$ ## Architecture Diagram \`\`\`{mermaid}
graph TD A[Input Value] --> B{Operation Type} B -->|Division| C[Check Denominator] B -->|Sqrt| D[Check Non-negative] B -->|Log| E[Check Positive] B -->|Exp| F[Check Range] C --> G{|b| < ε?} G -->|Yes| H[Use ε instead] G -->|No| I[Normal Division] D --> J{x < 0?} J -->|Yes| K[Use |x| or 0] J -->|No| L[Normal Sqrt] E --> M{x < ε?} M -->|Yes| N[Use ε instead] M -->|No| O[Normal Log] F --> P{|x| > MAX?} P -->|Yes| Q[Clip to ±MAX] P -->|No| R[Normal Exp] H --> S[Protected Result] I --> S K --> S L --> S N --> S O --> S Q --> S R --> S style G fill:#fff4e1 style J fill:#fff4e1 style M fill:#fff4e1 style P fill:#fff4e1 style S fill:#e8f5e9
\`\`\` ## Usage Examples ### Example 1: Safe Division \`\`\`python
from src.utils.numerical_stability import safe_divide # Protect against divide-by-zero
a = 1.0
b = 1e-15 # Near-zero denominator result = safe_divide(a, b, epsilon=1e-10)
print(f"Safe division: {a}/{b} = {result}")
# Uses epsilon instead

of b, returns bounded result # Vector safe division
numerators = np.array([1.0, 2.0, 3.0])
denominators = np.array([0.5, 1e-16, 2.0]) results = safe_divide(numerators, denominators)
print(f"Vector safe division: {results}")
\`\`\` ### Example 2: Safe Square Root for Negative Values \`\`\`python
from src.utils.numerical_stability import safe_sqrt # Handle numerical noise causing negative sqrt arguments
x = -0.001 # Small negative due to numerical error # Option 1: Use absolute value
result1 = safe_sqrt(x, allow_negative=True)
print(f"Safe sqrt (abs): {result1}") # sqrt(0.001) # Option 2: Clamp to zero
result2 = safe_sqrt(x, allow_negative=False)
print(f"Safe sqrt (clamp): {result2}") # 0.0 # Application: Lyapunov function
def lyapunov_analysis(x): V = x.T @ P @ x # May be slightly negative due to numerics # Safe sqrt for norm V_norm = safe_sqrt(V, allow_negative=True) return V_norm
\`\`\` ### Example 3: Safe Log and Exp for Optimization \`\`\`python
from src.utils.numerical_stability import safe_log, safe_exp # PSO optimization with safe operations
def compute_fitness_safe(params): """Fitness function with numerical protection.""" # Ensure positive before log cost = compute_cost(params) log_cost = safe_log(cost, epsilon=1e-10) # Prevent exp overflow penalty = compute_penalty(params) exp_penalty = safe_exp(penalty) # Clipped to prevent overflow fitness = log_cost + exp_penalty return fitness # Example values
cost = 1e-15 # Very small cost
penalty = 1000 # Large penalty fitness = compute_fitness_safe({'k1': 10, 'k2': 5})
print(f"Safe fitness: {fitness}") # No overflow or log(0) error
\`\`\` ### Example 4: Matrix Conditioning and Regularization \`\`\`python
from src.utils.numerical_stability import ( compute_condition_number, adaptive_regularization
)
import numpy as np # Check matrix conditioning
A = np.array([[1, 1], [1, 1.0001]]) # Near-singular kappa = compute_condition_number(A)
print(f"Condition number: {kappa:.2e}") if kappa > 1e12: print("Matrix is ill-conditioned, applying regularization...") # Adaptive regularization A_reg, epsilon_used = adaptive_regularization( A, target_condition=1e6 ) kappa_reg = compute_condition_number(A_reg) print(f"Regularized condition number: {kappa_reg:.2e}") print(f"Epsilon used: {epsilon_used:.2e}")
\`\`\` ### Example 5: Numerical Safety Pipeline \`\`\`python
from src.utils.numerical_stability import ( safe_divide, safe_sqrt, safe_log, safe_normalize
) def compute_control_with_safety(x, controller_gains): """Control computation with numerical safety.""" # Safe normalization x_norm = safe_normalize(x, epsilon=1e-10) # Safe division in gain computation adaptive_gain = safe_divide(controller_gains['base'], x_norm) # Safe sqrt for lyapunov-based gain V = x.T @ P @ x lyap_gain = safe_sqrt(V, allow_negative=True) # Safe log for barrier function barrier = safe_log(distance_to_constraint, epsilon=1e-10) # Combine safely u = adaptive_gain * x + lyap_gain * barrier_direction return u # Use in simulation
for k in range(1000): u = compute_control_with_safety(x, gains) x = integrator.integrate(dynamics, x, u, t) # No numerical errors even at boundaries
\`\`\` ## Architecture Diagram \`\`\`{mermaid}
graph TD A[Component] --> B[Subcomponent 1] A --> C[Subcomponent 2] B --> D[Output] C --> D style A fill:#e1f5ff style D fill:#e8f5e9
\`\`\` ## Usage Examples ### Example 1: Basic Usage \`\`\`python
from src.utils.numerical_stability import Component component = Component()
result = component.process(data)
\`\`\` ### Example 2: Advanced Configuration \`\`\`python
component = Component( option1=value1, option2=value2
)
\`\`\` ### Example 3: Integration with Simulation \`\`\`python
# Integration example
for k in range(num_steps): result = component.process(x) x = update(x, result)
\`\`\` ### Example 4: Performance Optimization \`\`\`python
component = Component(enable_caching=True)
\`\`\` ### Example 5: Error Handling \`\`\`python
try: result = component.process(data)
except ComponentError as e: print(f"Error: {e}")
\`\`\` 
