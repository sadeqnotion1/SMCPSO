# controllers.smc.core.gain_validation

**Source:** `src\controllers\smc\core\gain_validation.py`

## Module Overview

Gain Validation for SMC Controllers.

Provides centralized validation logic for SMC controller parameters.
Ensures gains satisfy stability requirements from sliding mode theory.

Mathematical Requirements:
- Surface gains (k1, k2, λ1, λ2) must be positive for Hurwitz stability
- Switching gains (K) must be positive to guarantee reaching condition
- Derivative gains (kd) must be non-negative for damping
- Adaptation gains must satisfy boundedness conditions


## Mathematical Foundation

### Stability Margin Analysis

Gain validation ensures controller **stability margins** meet requirements.

### Hurwitz Criterion Validation

For sliding surface:

```{math}
s = \lambda_1 \dot{\theta}_1 + c_1 \theta_1 + \lambda_2 \dot{\theta}_2 + c_2 \theta_2 = 0
```

**Necessary conditions:**

```{math}
c_i > 0, \quad \lambda_i > 0, \quad i = 1, 2
```

### Lyapunov Stability Margin

**Lyapunov function:**

```{math}
V = \frac{1}{2} s^2
```

**Required condition:**

```{math}
\dot{V} = s \dot{s} \leq -\eta |s|, \quad \eta > 0
```

**Switching gain requirement:**

```{math}
K \geq \frac{\max |\Delta(\vec{x}, t)|}{\eta} + \varepsilon
```

Where:
- $\Delta$: Model uncertainty bound
- $\varepsilon > 0$: Safety margin

**Typical:** $\varepsilon = 0.2 K$ (20% margin)

### Control Authority Validation

**Maximum control force:**

```{math}
|u| \leq u_{max}
```

**Peak force estimate** (worst case):

```{math}
|u|_{peak} \leq |u_{eq}|_{max} + K
```

**Validation criterion:**

```{math}
|u_{eq}|_{max} + K \leq 0.9 u_{max}
```

The 0.9 factor provides 10% safety margin for transients.

### Frequency Domain Validation

**Sliding surface characteristic frequency:**

```{math}
\omega_{n,i} = \sqrt{\frac{c_i}{\lambda_i}}, \quad i = 1, 2
```

**Requirements:**
1. **Below Nyquist:** $\omega_{n,i} < \frac{\omega_s}{5}$ (sampling frequency $\omega_s$)
2. **Above DC:** $\omega_{n,i} > 0.5$ rad/s (avoid drift)
3. **Bandwidth separation:** $\omega_{n,1}$ and $\omega_{n,2}$ differ by factor $< 5$ (avoid mode coupling)

### Gain Bounds

**Physical constraints** limit gains:

| Gain | Lower Bound | Upper Bound | Rationale |
|------|-------------|-------------|-----------|
| $c_1, c_2$ | 0.1 | 100 | Hurwitz + frequency limits |
| $\lambda_1, \lambda_2$ | 0.01 | 50 | Hurwitz + computational precision |
| $K$ (switching) | 1.0 | 500 | Lyapunov + actuator limits |
| $\epsilon$ (boundary) | 0.001 | 0.5 | Chattering vs accuracy trade-off |

### Adaptation Law Validation

For **adaptive SMC**, validate adaptation gains:

```{math}
\dot{K} = \gamma |s|, \quad \gamma > 0
```

**Requirements:**
1. **Rate limit:** $|\dot{K}| \leq \dot{K}_{max}$ (e.g., 100 N/s)
2. **Bounds:** $K_{min} \leq K \leq K_{max}$
3. **Leak term:** Optional $\dot{K} = \gamma |s| - \sigma K$ prevents unbounded growth

**Typical:** $\sigma = 0.01$ (1% leak)

### Robustness Validation

**Uncertainty margin:**

```{math}
\delta_{margin} = \frac{K - |\Delta|_{max}}{K} \times 100\%
```

**Requirement:** $\delta_{margin} \geq 20\%$

### Numerical Conditioning

**Matrix inversion check:** If using equivalent control:

```{math}
\kappa(\mathbf{\Lambda} \mathbf{M}^{-1} \mathbf{B}) < 10^6
```

If $\kappa \geq 10^6$: Reduce gains or increase regularization.

### Parameter Space Validation

**Geometric constraint:** Gains must lie within admissible polytope:

```{math}
\mathcal{G}_{valid} = \left\{ (c_1, c_2, \lambda_1, \lambda_2, K, \epsilon) \in \mathbb{R}_+^6 : \text{all criteria met} \right\}
```

**PSO optimization:** Search within $\mathcal{G}_{valid}$ only.

## Architecture Diagram

```{mermaid}
graph TD
    A[Input Gains] --> B{Hurwitz Check}
    B -->|c₁,c₂,λ₁,λ₂ > 0?| C[Frequency Analysis]
    B -->|No| X[Reject: Unstable]

    C --> D{ω_n < ω_s/5?}
    D -->|No| Y[Reject: Aliasing Risk]
    D -->|Yes| E[Control Authority Check]

    E --> F{|u_eq|_max + K ≤ 0.9u_max?}
    F -->|No| Z[Reject: Saturation Risk]
    F -->|Yes| G[Robustness Margin]

    G --> H{_K - |Δ|_max_/K ≥ 20%?}
    H -->|No| W[Reject: Insufficient Margin]
    H -->|Yes| I[Accept Gains]

    style X fill:#f99
    style Y fill:#f99
    style Z fill:#f99
    style W fill:#f99
    style I fill:#9f9
```

## Usage Examples

### Example 1: Hurwitz Criterion Validation

```python
from src.controllers.smc.core.gain_validation import validate_hurwitz_criterion

# Test gains
gains = [10.0, 8.0, 15.0, 12.0, 50.0, 0.01]  # c1, c2, λ1, λ2, K, ε

is_hurwitz = validate_hurwitz_criterion(gains)

if is_hurwitz:
    print("Gains satisfy Hurwitz criterion (stable sliding surface)")
else:
    print("Warning: Gains violate Hurwitz criterion")
```

## Example 2: Control Authority Check

```python
from src.controllers.smc.core.gain_validation import check_control_authority

# Controller parameters
c1, c2, lambda1, lambda2, K, epsilon = gains
u_max = 100.0  # Maximum actuator force (N)

# Estimate peak equivalent control (worst case)
u_eq_max = 80.0  # From dynamics analysis

# Check if total

control fits within limits
u_total_max = u_eq_max + K
margin = u_max - u_total_max

print(f"u_eq_max: {u_eq_max:.1f} N")
print(f"K:        {K:.1f} N")
print(f"u_total:  {u_total_max:.1f} N")
print(f"u_max:    {u_max:.1f} N")
print(f"Margin:   {margin:.1f} N ({100*margin/u_max:.1f}%)")

if margin < 0.1 * u_max:
    print("Warning: Insufficient control authority margin")
```

## Example 3: Frequency Bounds Validation

```python
# example-metadata:
# runnable: false

# Compute natural frequencies
omega_n1 = np.sqrt(c1 / lambda1)
omega_n2 = np.sqrt(c2 / lambda2)

# Sampling frequency (Hz)
f_s = 100  # Hz
omega_s = 2 * np.pi * f_s  # rad/s

# Check Nyquist criterion
if omega_n1 < omega_s / 5 and omega_n2 < omega_s / 5:
    print(f"✓ Frequencies safe: ω_n1={omega_n1:.2f}, ω_n2={omega_n2:.2f} rad/s")
else:
    print(f"✗ Aliasing risk: ω_n1={omega_n1:.2f}, ω_n2={omega_n2:.2f} rad/s")

# Check lower bound (avoid drift)
if omega_n1 > 0.5 and omega_n2 > 0.5:
    print("✓ Frequencies above DC drift threshold")
else:
    print("✗ Frequencies too low, drift risk")
```

## Example 4: Robustness Margin

```python
# example-metadata:
# runnable: false

# Model uncertainty bound
Delta_max = 20.0  # N (maximum disturbance/uncertainty)

# Compute robustness margin
margin_percent = 100 * (K - Delta_max) / K

print(f"Switching gain K:      {K:.1f} N")
print(f"Uncertainty Δ_max:     {Delta_max:.1f} N")
print(f"Robustness margin:     {margin_percent:.1f}%")

if margin_percent < 20:
    print("Warning: Insufficient robustness margin (< 20%)")
    K_recommended = Delta_max / 0.8  # 20% margin
    print(f"Recommended K:         {K_recommended:.1f} N")
```

## Example 5: Complete Validation Suite

```python
from src.controllers.smc.core.gain_validation import validate_all_criteria

# Validation configuration
validation_config = {
    'u_max': 100.0,         # Actuator limit (N)
    'omega_s': 2*np.pi*100, # Sampling frequency (rad/s)
    'Delta_max': 20.0,      # Uncertainty bound (N)
    'u_eq_max': 80.0,       # Peak equivalent control (N)
}

# Run all validation checks
results = validate_all_criteria(gains, validation_config)

print("\nValidation Results:")
print("=" * 50)
for criterion, passed in results.items():
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{criterion:30s}: {status}")

if all(results.values()):
    print("\n✓ All validation criteria passed")
else:
    print("\n✗ Some validation criteria failed")
```

## Complete Source Code

```{literalinclude} ../../../src/controllers/smc/core/gain_validation.py
:language: python
:linenos:
```



## Classes

### `SMCControllerType`

**Inherits from:** `Enum`

SMC controller types with different gain requirements.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/gain_validation.py
:language: python
:pyobject: SMCControllerType
:linenos:
```



### `GainBounds`

Bounds for SMC controller gains.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/gain_validation.py
:language: python
:pyobject: GainBounds
:linenos:
```

#### Methods (1)

##### `validate(self, value)`

Check if value is within bounds.

[View full source →](#method-gainbounds-validate)



### `SMCGainValidator`

Centralized gain validation for all SMC controller types.

Provides type-specific validation rules based on SMC theory requirements.

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/gain_validation.py
:language: python
:pyobject: SMCGainValidator
:linenos:
```

#### Methods (6)

##### `__init__(self)`

Initialize gain validator with standard bounds.

[View full source →](#method-smcgainvalidator-__init__)

##### `_initialize_standard_bounds(self)`

Initialize standard gain bounds for each controller type.

[View full source →](#method-smcgainvalidator-_initialize_standard_bounds)

##### `validate_gains(self, gains, controller_type)`

Validate gains for specific SMC controller type.

[View full source →](#method-smcgainvalidator-validate_gains)

##### `validate_stability_conditions(self, gains, controller_type)`

Validate SMC-specific stability conditions.

[View full source →](#method-smcgainvalidator-validate_stability_conditions)

##### `get_recommended_ranges(self, controller_type)`

Get recommended gain ranges for controller type.

[View full source →](#method-smcgainvalidator-get_recommended_ranges)

##### `update_bounds(self, controller_type, gain_name, min_val, max_val)`

Update gain bounds for specific controller and gain.

[View full source →](#method-smcgainvalidator-update_bounds)



## Functions

### `validate_smc_gains(gains, controller_type)`

Quick validation of SMC gains.

Args:
    gains: Gain values
    controller_type: Type of SMC controller

Returns:
    True if gains are valid, False otherwise

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/gain_validation.py
:language: python
:pyobject: validate_smc_gains
:linenos:
```



### `check_stability_conditions(gains, controller_type)`

Quick check of SMC stability conditions.

Args:
    gains: Gain values
    controller_type: Type of SMC controller

Returns:
    True if stability conditions are satisfied, False otherwise

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/gain_validation.py
:language: python
:pyobject: check_stability_conditions
:linenos:
```



### `get_gain_bounds_for_controller(controller_type)`

Get gain bounds for specific controller type.

Args:
    controller_type: Type of SMC controller

Returns:
    Dictionary of gain bounds

#### Source Code

```{literalinclude} ../../../src/controllers/smc/core/gain_validation.py
:language: python
:pyobject: get_gain_bounds_for_controller
:linenos:
```



## Dependencies

This module imports:

- `from typing import List, Union, Dict, Optional, Sequence`
- `import numpy as np`
- `from dataclasses import dataclass`
- `from enum import Enum`
