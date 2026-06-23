# Boundary Layer Mathematical Derivations

## Theoretical Foundation of Boundary Layer Approximation

### 1. Mathematical Motivation

The classical sliding mode control law employs a discontinuous sign function:

```latex
u = u_{eq} - K \cdot \text{sign}(\sigma)
```

However, this discontinuous control leads to **chattering** - high-frequency oscillations around the sliding surface. The boundary layer method provides a continuous approximation to mitigate this issue.

### 2. Boundary Layer Definition

#### 2.1 Linear Saturation Function

The linear saturation function provides a piecewise-linear approximation:

```latex
\text{sat}\left(\frac{\sigma}{\epsilon}\right) = \begin{cases}
\frac{\sigma}{\epsilon}, & \text{if } |\sigma| \leq \epsilon \\
\text{sign}(\sigma), & \text{if } |\sigma| > \epsilon
\end{cases}
```

**Mathematical Properties:**
- **Continuity**: The function is continuous everywhere
- **Boundedness**: Output is bounded in [-1, 1]
- **Lipschitz**: Locally Lipschitz with constant 1/ε

#### 2.2 Hyperbolic Tangent Approximation

The hyperbolic tangent provides a smooth approximation:

```latex
\text{sat}(\sigma/\epsilon) = \tanh(\sigma/\epsilon)
```

**Advantages over linear saturation:**
- **Smooth**: Infinitely differentiable
- **Better approximation**: Closer to ideal sign function shape
- **Preserved control authority**: Non-zero slope at origin

### 3. Mathematical Analysis of Boundary Layer Effects

#### 3.1 Steady-State Error Analysis

Inside the boundary layer (|σ| ≤ ε), the control law becomes:

```latex
u = u_{eq} - K \cdot \frac{\sigma}{\epsilon}
```

The closed-loop dynamics in the boundary layer:

```latex
\dot{\sigma} = L(M^{-1}(u_{eq} - K\frac{\sigma}{\epsilon}) - M^{-1}(C\dot{q} + G))
```

**Equilibrium condition** (σ̇ = 0):
```latex
\sigma_{ss} = \frac{\epsilon \cdot \text{disturbance}}{K}
```

**Key insight**: Steady-state error is proportional to ε and inversely proportional to K.

#### 3.2 Chattering Analysis

**Without boundary layer**: Switching frequency → ∞ as sampling rate increases

**With boundary layer**: Switching frequency is bounded by:
```latex
f_{switch} \leq \frac{1}{2\epsilon} \cdot \max|\dot{\sigma}|
```

### 4. Adaptive Boundary Layer Theory

#### 4.1 State-Dependent Boundary Layer

To balance chattering reduction and tracking accuracy:

```latex
\epsilon(t) = \epsilon_0 + \epsilon_1 \|\sigma(t)\|
```

where:
- `ε₀ > 0`: minimum boundary layer thickness
- `ε₁ ≥ 0`: scaling parameter

**Mathematical justification:**
- Large errors: Larger ε reduces chattering
- Small errors: Smaller ε improves accuracy

#### 4.2 Convergence Analysis with Adaptive Layer

Consider the Lyapunov function:
```latex
V = \frac{1}{2}\sigma^2
```

Time derivative:
```latex
\dot{V} = \sigma \dot{\sigma} = \sigma \left(L M^{-1}(u_{eq} - K \text{sat}(\sigma/\epsilon(\sigma))) + d\right)
```

For the adaptive boundary layer:
```latex
\dot{V} \leq -\eta |\sigma| + \delta \epsilon_0
```

where η > 0 depends on the control gains and δ bounds the disturbance effects.

### 5. Hysteresis Implementation

#### 5.1 Mathematical Definition

Hysteresis introduces a dead-band to further reduce chattering:

```latex
\text{sat}_{hyst}(\sigma, \epsilon) = \begin{cases}
0, & \text{if } |\sigma| < \rho \epsilon_0 \\
\text{sat}(\sigma/\epsilon), & \text{if } |\sigma| \geq \rho \epsilon_0
\end{cases}
```

where `0 ≤ ρ ≤ 1` is the hysteresis ratio.

#### 5.2 Stability Analysis with Hysteresis

The dead-band modifies the convergence analysis:

```latex
\dot{V} = \begin{cases}
\sigma \cdot d, & \text{if } |\sigma| < \rho \epsilon_0 \\
\sigma(\text{control term} + d), & \text{if } |\sigma| \geq \rho \epsilon_0
\end{cases}
```

**Ultimate boundedness**: The system converges to the set `|σ| ≤ ρε₀ + δ/η`.

### 6. Numerical Implementation Considerations

#### 6.1 Computational Stability

**Potential numerical issues:**
1. **Division by zero**: When ε = 0
2. **Overflow**: For very small ε and large σ
3. **Underflow**: For very large ε and small σ

**Solutions:**
```latex
\epsilon_{safe} = \max(\epsilon, \epsilon_{min})
```

where `εₘᵢₙ` is a small positive constant (e.g., 1e-6).

#### 6.2 Real-Time Implementation

**Computational complexity:**
- Linear saturation: O(1) - simple conditional
- Hyperbolic tangent: O(1) - hardware-optimized function

**Memory requirements:**
- Stateless for constant boundary layer
- Single float for adaptive boundary layer state

### 7. Boundary Layer Design Guidelines

#### 7.1 Selection Criteria

**Trade-off considerations:**
1. **Chattering vs. accuracy**: Smaller ε → better tracking, more chattering
2. **Disturbance rejection**: ε should be proportional to expected disturbance magnitude
3. **Control authority**: ε should not exceed actuator saturation limits

**Recommended design process:**
```latex
\epsilon_0 = \alpha \cdot \frac{\text{expected disturbance}}{K}
```

where α ∈ [0.1, 1.0] is a design parameter.

#### 7.2 Tuning Guidelines

**Initial values:**
- Start with ε₀ = 0.01 for normalized systems
- Set ε₁ = 0 initially (constant boundary layer)
- Hysteresis ratio ρ = 0.1 (10% of boundary layer)

**Iterative tuning:**
1. Increase K to improve disturbance rejection
2. Decrease ε₀ to improve tracking accuracy
3. Add adaptive scaling (ε₁ > 0) if needed
4. Adjust hysteresis ratio for chattering control

### 8. Mathematical Validation Requirements

#### 8.1 Property Verification

**Continuity test:**
```python
def test_boundary_layer_continuity():
    eps = 0.01
    sigma_test = np.linspace(-2*eps, 2*eps, 1000)
    sat_values = [saturate(s, eps, method="linear") for s in sigma_test]

    # Check for discontinuities
    diffs = np.diff(sat_values)
    max_jump = np.max(np.abs(diffs))
    assert max_jump < threshold  # Should be small for continuity
```

**Boundary conditions:**
```python
def test_boundary_conditions():
    eps = 0.01

    # At boundary points
    assert abs(saturate(eps, eps, "linear") - 1.0) < 1e-10
    assert abs(saturate(-eps, eps, "linear") + 1.0) < 1e-10

    # Inside boundary layer (linear region)
    sigma_inside = 0.5 * eps
    expected = sigma_inside / eps
    assert abs(saturate(sigma_inside, eps, "linear") - expected) < 1e-10
```

#### 8.2 Convergence Verification

**Lyapunov decrease test:**
```python
def test_lyapunov_decrease():
    # Verify that V̇ < 0 outside the ultimate bound
    sigma = np.linspace(-1, 1, 100)
    for s in sigma:
        if abs(s) > ultimate_bound:
            V_dot = compute_lyapunov_derivative(s)
            assert V_dot < 0
```

### 9. Implementation Examples

#### 9.1 Classical SMC with Adaptive Boundary Layer

```python
def compute_boundary_layer(sigma, epsilon0, epsilon1):
    """Compute adaptive boundary layer thickness."""
    return epsilon0 + epsilon1 * abs(sigma)

def saturate_adaptive(sigma, epsilon0, epsilon1, method="tanh"):
    """Saturation with adaptive boundary layer."""
    eps_adaptive = compute_boundary_layer(sigma, epsilon0, epsilon1)
    return saturate(sigma, eps_adaptive, method)
```

#### 9.2 Hysteresis Implementation

```python
def saturate_with_hysteresis(sigma, epsilon0, hysteresis_ratio, method="tanh"):
    """Saturation function with hysteresis dead-band."""
    dead_band = hysteresis_ratio * epsilon0

    if abs(sigma) < dead_band:
        return 0.0
    else:
        return saturate(sigma, epsilon0, method)
```

### 10. Performance Metrics

#### 10.1 Chattering Quantification

**Switching frequency metric:**
```latex
f_{avg} = \frac{1}{T} \sum_{k=1}^{N-1} \frac{|\text{sign}(u_{k+1}) - \text{sign}(u_k)|}{2\Delta t}
```

**Control effort metric:**
```latex
J_{effort} = \int_0^T |u(t)| dt
```

#### 10.2 Tracking Performance

**Steady-state error bound:**
```latex
e_{ss} \leq \frac{\epsilon_0 \cdot d_{max}}{K_{min}}
```

**Convergence time estimate:**
```latex
t_{conv} \approx \frac{\ln(\sigma_0/\epsilon_0)}{\lambda_{min}}
```

where λₘᵢₙ is the smallest eigenvalue of the closed-loop system matrix.

## Implementation Status in Codebase

### Current Implementation Analysis

Based on the codebase review:

1. **Classical SMC** (`classic_smc.py`):
   - ✅ Implements adaptive boundary layer: `ε = ε₀ + ε₁||σ||`
   - ✅ Supports both "tanh" and "linear" saturation methods
   - ✅ Includes hysteresis with configurable ratio
   - ✅ Proper validation of ε > 0

2. **Super-Twisting SMC** (`sta_smc.py`):
   - ✅ Uses boundary layer for sign function approximation
   - ✅ Implements both "tanh" and "linear" methods
   - ✅ Validates boundary layer positivity
   - ⚠️ Could benefit from adaptive boundary layer option

3. **Common Implementation Issues Found**:
   - **Mathematical correctness**: All boundary layer computations are mathematically sound
   - **Numerical stability**: Proper validation prevents division by zero
   - **Performance**: Numba acceleration for critical paths

### Recommendations for Enhancement

1. **Add adaptive boundary layer to STA-SMC**
2. **Implement boundary layer performance metrics**
3. **Add mathematical property tests as shown above**
4. **Consider state-dependent hysteresis for advanced applications**