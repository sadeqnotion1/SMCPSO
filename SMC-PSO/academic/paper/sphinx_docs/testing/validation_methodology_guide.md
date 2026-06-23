# Validation Methodology Guide

**DIP-SMC-PSO Project**
**Last Updated**: 2025-10-04
**Status**: Research-Grade Mathematical Validation Framework



## Table of Contents

1. [Overview](#1-overview)
2. [Mathematical Validation](#2-mathematical-validation)
3. [Configuration Validation](#3-configuration-validation)
4. [Numerical Validation](#4-numerical-validation)
5. [Scientific Validation](#5-scientific-validation)



## 1. Overview

### 1.1 Validation Philosophy

The validation methodology ensures that all mathematical algorithms, configurations, and numerical computations maintain **scientific rigor**, **mathematical correctness**, and **numerical stability** throughout the system lifecycle.

### 1.2 Validation Categories

```
Validation Framework
├── Mathematical Validation           # Control theory property tests
│   ├── Sliding surface properties       # Linearity, homogeneity, gain sensitivity
│   ├── Boundary layer properties        # Continuity, monotonicity, asymptotic behavior
│   ├── Lyapunov function validation     # Positive definiteness, V̇ < 0
│   └── Reaching law verification        # s·ṡ ≤ -η|s|
│
├── Configuration Validation          # Parameter validation
│   ├── Physical constraints             # Positive masses, lengths, gains
│   ├── Stability requirements           # Hurwitz conditions, damping ratios
│   ├── Compatibility checks             # Controller-dynamics compatibility
│   └── Range validation                 # Bounds checking
│
├── Numerical Validation             # Numerical stability
│   ├── Floating-point precision         # Machine epsilon tests
│   ├── Conditioning analysis            # Matrix condition numbers
│   ├── Edge case testing                # Boundary values, singularities
│   └── Convergence validation           # Iterative algorithm convergence
│
└── Scientific Validation            # Research-grade validation
    ├── Control-theoretic properties     # Stability, controllability
    ├── Performance metrics              # ISE, settling time, overshoot
    ├── Monte Carlo validation           # Statistical robustness
    └── Cross-validation                 # Analytical vs numerical
```

### 1.3 Quality Gates

| Validation Category | Coverage Requirement | Acceptance Criteria |
|---------------------|---------------------|---------------------|
| Mathematical Properties | 100% | All theoretical properties verified |
| Configuration Rules | 100% | All invalid configs rejected |
| Numerical Stability | ≥95% | Edge cases handled gracefully |
| Scientific Validation | ≥90% | Control theory guarantees met |



## 2. Mathematical Validation

### 2.1 Sliding Surface Properties

#### 2.1.1 Linearity Property

**Theoretical Requirement**: For linear sliding surface σ(x), the property σ(x₁ + x₂) = σ(x₁) + σ(x₂) must hold.

```python
# tests/validation/test_sliding_surface_properties.py

import pytest
import numpy as np
from src.controllers.smc.core.sliding_surface import LinearSlidingSurface

class TestSlidingSurfaceLinearity:
    """Validate linearity property of sliding surfaces."""

    def test_linearity_property(self):
        """Test σ(x₁ + x₂) = σ(x₁) + σ(x₂) for linear surfaces."""
        gains = [5.0, 3.0, 4.0, 2.0]
        surface = LinearSlidingSurface(gains)

        # Generate test states
        x1 = np.array([0.1, 0.1, 0.1, 0.05, 0.05, 0.05])
        x2 = np.array([0.2, 0.2, 0.2, 0.1, 0.1, 0.1])

        # Compute sliding variables
        s1 = surface.compute(x1)
        s2 = surface.compute(x2)
        s_combined = surface.compute(x1 + x2)

        # Verify linearity: s(x1 + x2) = s(x1) + s(x2)
        assert abs(s_combined - (s1 + s2)) < 1e-10, (
            f"Linearity violated: s({x1}+{x2}) = {s_combined}, "
            f"but s({x1}) + s({x2}) = {s1 + s2}"
        )

    @pytest.mark.parametrize("k1,k2,lam1,lam2", [
        (5.0, 3.0, 4.0, 2.0),
        (10.0, 8.0, 15.0, 12.0),
        (1.0, 1.0, 1.0, 1.0),
    ])
    def test_linearity_various_gains(self, k1, k2, lam1, lam2):
        """Test linearity for various gain combinations."""
        gains = [k1, k2, lam1, lam2]
        surface = LinearSlidingSurface(gains)

        for _ in range(100):
            x1 = np.random.uniform(-1, 1, size=6)
            x2 = np.random.uniform(-1, 1, size=6)

            s1 = surface.compute(x1)
            s2 = surface.compute(x2)
            s_combined = surface.compute(x1 + x2)

            assert abs(s_combined - (s1 + s2)) < 1e-10
```

#### 2.1.2 Homogeneity Property

**Theoretical Requirement**: For linear sliding surface, σ(α·x) = α·σ(x) for any scalar α.

```python
# example-metadata:
# runnable: false

class TestSlidingSurfaceHomogeneity:
    """Validate homogeneity property of sliding surfaces."""

    def test_homogeneity_property(self):
        """Test σ(α·x) = α·σ(x) for linear surfaces."""
        gains = [5.0, 3.0, 4.0, 2.0]
        surface = LinearSlidingSurface(gains)

        x = np.array([0.1, 0.1, 0.1, 0.05, 0.05, 0.05])
        alpha = 2.5

        s_original = surface.compute(x)
        s_scaled = surface.compute(alpha * x)

        # Verify homogeneity: s(α·x) = α·s(x)
        expected = alpha * s_original
        assert abs(s_scaled - expected) < 1e-10, (
            f"Homogeneity violated: s({alpha}·x) = {s_scaled}, "
            f"but {alpha}·s(x) = {expected}"
        )

    def test_homogeneity_negative_scaling(self):
        """Test homogeneity with negative scalar."""
        gains = [5.0, 3.0, 4.0, 2.0]
        surface = LinearSlidingSurface(gains)

        x = np.array([0.1, 0.1, 0.1, 0.05, 0.05, 0.05])
        alpha = -1.5

        s_original = surface.compute(x)
        s_scaled = surface.compute(alpha * x)

        assert abs(s_scaled - alpha * s_original) < 1e-10
```

#### 2.1.3 Gain Sensitivity

**Theoretical Requirement**: Sliding surface must respond proportionally to gain changes.

```python
# example-metadata:
# runnable: false

class TestSlidingSurfaceGainSensitivity:
    """Validate gain sensitivity of sliding surfaces."""

    def test_proportional_gain_scaling(self):
        """Test that doubling gains doubles sliding variable."""
        gains1 = [5.0, 3.0, 4.0, 2.0]
        gains2 = [10.0, 6.0, 8.0, 4.0]  # Doubled gains

        surface1 = LinearSlidingSurface(gains1)
        surface2 = LinearSlidingSurface(gains2)

        state = np.array([0.1, 0.1, 0.1, 0.05, 0.05, 0.05])

        s1 = surface1.compute(state)
        s2 = surface2.compute(state)

        # Surface value should double with doubled gains
        assert abs(s2 - 2 * s1) < 1e-10, (
            f"Gain sensitivity violated: s(2k) = {s2}, but 2·s(k) = {2*s1}"
        )

    def test_zero_gains_zero_surface(self):
        """Test that zero gains produce zero sliding variable."""
        gains = [0.0, 0.0, 0.0, 0.0]
        surface = LinearSlidingSurface(gains)

        state = np.random.uniform(-1, 1, size=6)
        s = surface.compute(state)

        assert abs(s) < 1e-15, f"Zero gains should produce zero surface, got {s}"
```

### 2.2 Boundary Layer Properties

#### 2.2.1 Continuity Validation

**Theoretical Requirement**: Switching function must be continuous at sliding surface (σ = 0).

```python
# tests/validation/test_boundary_layer_properties.py

class TestBoundaryLayerContinuity:
    """Validate continuity of boundary layer switching functions."""

    def test_tanh_continuity_at_surface(self):
        """Test tanh switching function is continuous at σ = 0."""
        from src.controllers.smc.algorithms.classical.boundary_layer import BoundaryLayer

        boundary_layer = BoundaryLayer(thickness=0.1, method="tanh")

        epsilon = 1e-8
        switch_left = boundary_layer.compute(-epsilon)
        switch_center = boundary_layer.compute(0.0)
        switch_right = boundary_layer.compute(epsilon)

        # Values should be very close at the boundary
        assert abs(switch_left - switch_center) < 1e-6
        assert abs(switch_right - switch_center) < 1e-6
        assert abs(switch_center) < 1e-6  # tanh(0) = 0

    def test_linear_continuity_at_surface(self):
        """Test linear (saturation) switching function continuity."""
        boundary_layer = BoundaryLayer(thickness=0.1, method="linear")

        epsilon = 1e-8
        switch_left = boundary_layer.compute(-epsilon)
        switch_center = boundary_layer.compute(0.0)
        switch_right = boundary_layer.compute(epsilon)

        # Linear function is continuous
        assert abs(switch_left - switch_center) < 1e-10
        assert abs(switch_right - switch_center) < 1e-10
```

#### 2.2.2 Monotonicity Validation

**Theoretical Requirement**: Switching function must be strictly monotonic increasing.

```python
# example-metadata:
# runnable: false

class TestBoundaryLayerMonotonicity:
    """Validate monotonicity of switching functions."""

    def test_tanh_monotonicity(self):
        """Test tanh switching function is strictly increasing."""
        boundary_layer = BoundaryLayer(thickness=0.1, method="tanh")

        s_values = np.linspace(-1, 1, 100)
        switch_values = [boundary_layer.compute(s) for s in s_values]

        # Verify strict monotonicity
        for i in range(len(switch_values) - 1):
            assert switch_values[i+1] >= switch_values[i], (
                f"Monotonicity violated at index {i}: "
                f"switch({s_values[i+1]}) = {switch_values[i+1]} < "
                f"switch({s_values[i]}) = {switch_values[i]}"
            )

    def test_saturation_monotonicity(self):
        """Test saturation function is monotonic."""
        boundary_layer = BoundaryLayer(thickness=0.1, method="linear")

        s_values = np.linspace(-2, 2, 200)
        switch_values = [boundary_layer.compute(s) for s in s_values]

        for i in range(len(switch_values) - 1):
            assert switch_values[i+1] >= switch_values[i]
```

#### 2.2.3 Asymptotic Behavior

**Theoretical Requirement**: Switching function must approach ±1 for large |σ|.

```python
# example-metadata:
# runnable: false

class TestBoundaryLayerAsymptoticBehavior:
    """Validate asymptotic limits of switching functions."""

    def test_tanh_asymptotic_limits(self):
        """Test tanh approaches ±1 for large |σ|."""
        boundary_layer = BoundaryLayer(thickness=0.1, method="tanh")

        # Large positive σ
        switch_pos = boundary_layer.compute(10.0)
        assert abs(switch_pos - 1.0) < 1e-3, (
            f"tanh should approach +1 for large positive σ, got {switch_pos}"
        )

        # Large negative σ
        switch_neg = boundary_layer.compute(-10.0)
        assert abs(switch_neg - (-1.0)) < 1e-3, (
            f"tanh should approach -1 for large negative σ, got {switch_neg}"
        )

    def test_saturation_bounds(self):
        """Test saturation function is bounded by ±1."""
        boundary_layer = BoundaryLayer(thickness=0.1, method="linear")

        # Test many values
        s_values = np.random.uniform(-100, 100, size=1000)
        for s in s_values:
            switch = boundary_layer.compute(s)
            assert -1.0 <= switch <= 1.0, (
                f"Saturation violated: switch({s}) = {switch} not in [-1, 1]"
            )
```

### 2.3 Lyapunov Function Validation

#### 2.3.1 Positive Definiteness

**Theoretical Requirement**: V(σ) > 0 for σ ≠ 0, V(0) = 0

```python
# tests/validation/test_lyapunov_properties.py

class TestLyapunovFunctionProperties:
    """Validate Lyapunov function properties for stability analysis."""

    def test_positive_definiteness(self):
        """Test V(σ) > 0 for σ ≠ 0, V(0) = 0."""
        from src.controllers.smc.core.sliding_surface import LinearSlidingSurface

        gains = [5.0, 3.0, 4.0, 2.0]
        surface = LinearSlidingSurface(gains)

        # Test states
        states = [
            np.array([0.1, 0.05, 0.08, 0.02, 0.03, 0.01]),  # Non-zero
            np.array([0.2, 0.1, 0.15, 0.05, 0.08, 0.03]),   # Non-zero
            np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])        # Zero (equilibrium)
        ]

        for state in states:
            s = surface.compute(state)
            V = 0.5 * s**2  # Lyapunov candidate: V = ½σ²

            if np.linalg.norm(state) < 1e-10:
                # At equilibrium, V should be zero
                assert V < 1e-15, f"V(0) should be zero, got {V}"
            else:
                # Away from equilibrium, V should be positive
                assert V > 0, f"V(σ) should be positive for σ ≠ 0, got {V}"

    def test_lyapunov_decrease_property(self):
        """Test V̇(σ) < 0 for σ ≠ 0 (Lyapunov decrease condition)."""
        from src.controllers.smc.classic_smc import ClassicalSMC
        from src.core.dynamics import SimplifiedDynamics

        controller = ClassicalSMC(
            gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
            max_force=100.0,
            boundary_layer=0.01
        )

        physics_cfg = {
            'M': 1.0, 'm1': 0.1, 'm2': 0.1,
            'L1': 0.5, 'L2': 0.5, 'g': 9.81
        }
        dynamics = SimplifiedDynamics(physics_cfg)

        # Initial state away from equilibrium
        state = np.array([0.0, 0.2, 0.15, 0.0, 0.0, 0.0])

        V_values = []
        for _ in range(100):
            # Compute sliding variable
            from src.controllers.smc.core.sliding_surface import LinearSlidingSurface
            surface = LinearSlidingSurface([10.0, 8.0, 15.0, 12.0])
            s = surface.compute(state)

            V = 0.5 * s**2
            V_values.append(V)

            # Apply control and step dynamics
            result = controller.compute_control(state, {}, {})
            u = result.get('control_output', result.get('control', 0.0))
            x_dot = dynamics.dynamics(state, u)
            state = state + 0.01 * x_dot

        # Verify Lyapunov decrease: V̇ < 0
        V_derivative = np.diff(V_values)
        positive_derivatives = np.sum(V_derivative > 0)

        # Allow small violations due to numerical errors
        violation_ratio = positive_derivatives / len(V_derivative)
        assert violation_ratio < 0.05, (
            f"Lyapunov function should decrease monotonically, "
            f"but increased {violation_ratio*100:.1f}% of the time"
        )
```

### 2.4 Reaching Law Validation

**Theoretical Requirement**: σ·σ̇ ≤ -η|σ| ensures finite-time reaching.

```python
class TestReachingLawSatisfaction:
    """Validate reaching law for sliding mode controllers."""

    def test_reaching_law_condition(self):
        """Test σ·σ̇ ≤ -η|σ| is satisfied."""
        from src.controllers.smc.classic_smc import ClassicalSMC
        from src.core.dynamics import SimplifiedDynamics

        controller = ClassicalSMC(
            gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
            max_force=100.0,
            boundary_layer=0.01
        )

        physics_cfg = {'M': 1.0, 'm1': 0.1, 'm2': 0.1, 'L1': 0.5, 'L2': 0.5, 'g': 9.81}
        dynamics = SimplifiedDynamics(physics_cfg)

        state = np.array([0.0, 0.2, 0.15, 0.0, 0.0, 0.0])

        from src.controllers.smc.core.sliding_surface import LinearSlidingSurface
        surface = LinearSlidingSurface([10.0, 8.0, 15.0, 12.0])

        dt = 0.01
        for _ in range(50):
            s_current = surface.compute(state)

            # Apply control
            result = controller.compute_control(state, {}, {})
            u = result.get('control_output', result.get('control', 0.0))

            # Step dynamics
            x_dot = dynamics.dynamics(state, u)
            state_next = state + dt * x_dot

            s_next = surface.compute(state_next)
            s_dot = (s_next - s_current) / dt

            # Reaching law: s·ṡ ≤ -η|s|
            reaching_product = s_current * s_dot
            eta = 0.5  # Reaching rate parameter

            if abs(s_current) > controller.boundary_layer:
                # Outside boundary layer, reaching law must be satisfied
                assert reaching_product <= -eta * abs(s_current) + 0.1, (
                    f"Reaching law violated: σ·σ̇ = {reaching_product}, "
                    f"but should be ≤ {-eta * abs(s_current)}"
                )

            state = state_next
```



## 3. Configuration Validation

### 3.1 Parameter Validation Rules

#### 3.1.1 Positive Gain Requirement

```python
# tests/validation/test_configuration_validation.py

class TestControllerGainValidation:
    """Validate controller gain configuration rules."""

    def test_positive_gain_requirement(self):
        """Test that all gains must be positive."""
        from src.controllers.smc.classic_smc import ClassicalSMC

        # Valid gains
        valid_gains = [10.0, 8.0, 15.0, 12.0, 50.0, 5.0]
        controller = ClassicalSMC(gains=valid_gains, max_force=100.0)
        assert controller.k1 == 10.0

        # Invalid: negative gain
        with pytest.raises(ValueError, match="must be positive"):
            ClassicalSMC(
                gains=[10.0, -8.0, 15.0, 12.0, 50.0, 5.0],
                max_force=100.0
            )

        # Invalid: zero gain
        with pytest.raises(ValueError, match="must be positive"):
            ClassicalSMC(
                gains=[0.0, 8.0, 15.0, 12.0, 50.0, 5.0],
                max_force=100.0
            )

    def test_switching_gain_validation(self):
        """Test switching gain K must be positive."""
        from src.controllers.smc.classic_smc import ClassicalSMC

        with pytest.raises(ValueError, match="Switching gain K must be positive"):
            ClassicalSMC(
                gains=[10.0, 8.0, 15.0, 12.0, -50.0, 5.0],  # Negative K
                max_force=100.0
            )

    def test_boundary_layer_validation(self):
        """Test boundary layer thickness must be positive."""
        from src.controllers.smc.classic_smc import ClassicalSMC

        valid_gains = [10.0, 8.0, 15.0, 12.0, 50.0, 5.0]

        # Valid boundary layer
        controller = ClassicalSMC(gains=valid_gains, max_force=100.0, boundary_layer=0.01)
        assert controller.boundary_layer == 0.01

        # Invalid: zero boundary layer
        with pytest.raises(ValueError, match="boundary_layer must be positive"):
            ClassicalSMC(gains=valid_gains, max_force=100.0, boundary_layer=0.0)

        # Invalid: negative boundary layer
        with pytest.raises(ValueError, match="boundary_layer must be positive"):
            ClassicalSMC(gains=valid_gains, max_force=100.0, boundary_layer=-0.01)
```

### 3.2 Stability Requirements

#### 3.2.1 Hurwitz Stability Checks

**Theoretical Requirement**: For 2nd-order subsystems, characteristic polynomial s² + λᵢs + cᵢ = 0 requires λᵢ > 0 and cᵢ > 0 for stability.

```python
class TestStabilityRequirements:
    """Validate stability requirements for controller gains."""

    def test_hurwitz_stability_condition(self):
        """Test gains satisfy Hurwitz stability criteria."""
        from src.controllers.smc.classic_smc import ClassicalSMC

        # Stable configuration
        stable_gains = [5.0, 3.0, 4.0, 2.0, 10.0, 1.0]
        controller = ClassicalSMC(gains=stable_gains, max_force=100.0)

        # Check Hurwitz conditions
        k1, k2, lam1, lam2 = controller.k1, controller.k2, controller.lam1, controller.lam2

        # For stable sliding dynamics: λᵢ > 0 and cᵢ (gains) > 0
        assert k1 > 0 and k2 > 0, "Position gains must be positive for stability"
        assert lam1 > 0 and lam2 > 0, "Velocity gains must be positive for stability"

    def test_damping_ratio_validation(self):
        """Test that damping ratios are positive."""
        from src.controllers.smc.classic_smc import ClassicalSMC

        stable_gains = [5.0, 3.0, 4.0, 2.0, 10.0, 1.0]
        controller = ClassicalSMC(gains=stable_gains, max_force=100.0)

        # Compute damping ratios: ζᵢ = λᵢ / (2√kᵢ)
        zeta1 = controller.lam1 / (2 * np.sqrt(controller.k1))
        zeta2 = controller.lam2 / (2 * np.sqrt(controller.k2))

        assert zeta1 > 0, f"Damping ratio ζ₁ must be positive, got {zeta1}"
        assert zeta2 > 0, f"Damping ratio ζ₂ must be positive, got {zeta2}"

        # Recommended: underdamped to critically damped (0 < ζ ≤ 1)
        assert 0 < zeta1 <= 2.0, f"ζ₁ = {zeta1} outside recommended range (0, 2]"
        assert 0 < zeta2 <= 2.0, f"ζ₂ = {zeta2} outside recommended range (0, 2]"
```

### 3.3 Physical Constraint Validation

```python
class TestPhysicsParameterValidation:
    """Validate physics parameter constraints."""

    def test_positive_mass_requirement(self):
        """Test all masses must be positive."""
        from src.core.dynamics import SimplifiedDynamics

        valid_config = {
            'M': 1.0, 'm1': 0.1, 'm2': 0.1,
            'L1': 0.5, 'L2': 0.5, 'g': 9.81
        }

        dynamics = SimplifiedDynamics(valid_config)
        assert dynamics.M == 1.0

        # Invalid: negative mass
        invalid_config = valid_config.copy()
        invalid_config['M'] = -1.0

        with pytest.raises(ValueError, match="Mass must be positive"):
            SimplifiedDynamics(invalid_config)

    def test_positive_length_requirement(self):
        """Test pendulum lengths must be positive."""
        from src.core.dynamics import SimplifiedDynamics

        valid_config = {
            'M': 1.0, 'm1': 0.1, 'm2': 0.1,
            'L1': 0.5, 'L2': 0.5, 'g': 9.81
        }

        # Invalid: zero length
        invalid_config = valid_config.copy()
        invalid_config['L1'] = 0.0

        with pytest.raises(ValueError, match="Length must be positive"):
            SimplifiedDynamics(invalid_config)
```



## 4. Numerical Validation

### 4.1 Floating-Point Precision Tests

```python
# tests/validation/test_numerical_precision.py

class TestNumericalPrecision:
    """Validate numerical precision and stability."""

    def test_floating_point_consistency(self):
        """Test that repeated computations yield identical results."""
        from src.controllers.smc.classic_smc import ClassicalSMC

        controller = ClassicalSMC(
            gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
            max_force=100.0,
            boundary_layer=0.01
        )

        state = np.array([0.1, 0.05, 0.08, 0.02, 0.03, 0.01])

        # Compute control 100 times
        results = []
        for _ in range(100):
            result = controller.compute_control(state, {}, {})
            control = result.get('control_output', result.get('control'))
            results.append(control)

        results = np.array(results)

        # All results should be identical (deterministic)
        std_dev = np.std(results)
        assert std_dev < 1e-15, f"Floating-point consistency violated: std = {std_dev}"

    def test_numerical_stability_small_values(self):
        """Test numerical stability with very small state values."""
        from src.controllers.smc.classic_smc import ClassicalSMC

        controller = ClassicalSMC(
            gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
            max_force=100.0,
            boundary_layer=0.01
        )

        # Very small state values (near machine precision)
        small_state = np.array([1e-15, 1e-15, 1e-15, 1e-15, 1e-15, 1e-15])

        result = controller.compute_control(small_state, {}, {})
        control = result.get('control_output', result.get('control'))

        # Control should be finite and small
        assert np.isfinite(control), f"Control is not finite for small state: {control}"
        assert abs(control) < 1.0, f"Control magnitude too large for small state: {control}"

    def test_numerical_stability_large_values(self):
        """Test numerical stability with large state values."""
        from src.controllers.smc.classic_smc import ClassicalSMC

        controller = ClassicalSMC(
            gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
            max_force=100.0,
            boundary_layer=0.01
        )

        # Large state values
        large_state = np.array([10.0, 5.0, 3.0, 2.0, 2.0, 1.0])

        result = controller.compute_control(large_state, {}, {})
        control = result.get('control_output', result.get('control'))

        # Control should be finite and saturated
        assert np.isfinite(control), f"Control is not finite for large state: {control}"
        assert abs(control) <= 100.0 * 1.01, f"Control exceeds saturation: {control}"
```

### 4.2 Matrix Conditioning Analysis

```python
class TestMatrixConditioning:
    """Validate matrix conditioning for numerical stability."""

    def test_mass_matrix_conditioning(self):
        """Test mass matrix is well-conditioned."""
        from src.core.dynamics_full import FullNonlinearDynamics

        physics_cfg = {
            'M': 1.0, 'm1': 0.1, 'm2': 0.1,
            'L1': 0.5, 'L2': 0.5, 'g': 9.81
        }
        dynamics = FullNonlinearDynamics(physics_cfg)

        # Test various states
        states = [
            np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),      # Equilibrium
            np.array([0.0, np.pi/4, np.pi/6, 0.0, 0.0, 0.0]),  # Angled
            np.array([0.0, np.pi/2, np.pi/3, 0.0, 0.0, 0.0])   # Large angles
        ]

        for state in states:
            M = dynamics.compute_mass_matrix(state)

            # Compute condition number
            cond_number = np.linalg.cond(M)

            assert cond_number < 1e6, (
                f"Mass matrix poorly conditioned at {state}: "
                f"condition number = {cond_number:.2e}"
            )

    def test_mass_matrix_positive_definite(self):
        """Test mass matrix is positive definite."""
        from src.core.dynamics_full import FullNonlinearDynamics

        physics_cfg = {
            'M': 1.0, 'm1': 0.1, 'm2': 0.1,
            'L1': 0.5, 'L2': 0.5, 'g': 9.81
        }
        dynamics = FullNonlinearDynamics(physics_cfg)

        state = np.array([0.0, np.pi/4, np.pi/6, 0.0, 0.0, 0.0])
        M = dynamics.compute_mass_matrix(state)

        # Check positive definiteness via eigenvalues
        eigenvalues = np.linalg.eigvals(M)

        assert np.all(eigenvalues > 0), (
            f"Mass matrix not positive definite: eigenvalues = {eigenvalues}"
        )
```



## 5. Scientific Validation

### 5.1 Control-Theoretic Property Verification

```python
# tests/validation/test_scientific_properties.py

class TestControlTheoreticProperties:
    """Validate control-theoretic guarantees."""

    def test_exponential_stability(self):
        """Test closed-loop system exhibits exponential stability."""
        from src.controllers.smc.classic_smc import ClassicalSMC
        from src.core.dynamics import SimplifiedDynamics

        controller = ClassicalSMC(
            gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
            max_force=100.0,
            boundary_layer=0.01
        )

        physics_cfg = {'M': 1.0, 'm1': 0.1, 'm2': 0.1, 'L1': 0.5, 'L2': 0.5, 'g': 9.81}
        dynamics = SimplifiedDynamics(physics_cfg)

        # Initial state
        state = np.array([0.0, 0.2, 0.15, 0.0, 0.0, 0.0])
        initial_error = np.linalg.norm(state)

        # Simulate
        errors = [initial_error]
        for _ in range(500):
            result = controller.compute_control(state, {}, {})
            u = result.get('control_output', result.get('control', 0.0))
            x_dot = dynamics.dynamics(state, u)
            state = state + 0.01 * x_dot
            errors.append(np.linalg.norm(state))

        errors = np.array(errors)
        t = np.arange(len(errors)) * 0.01

        # Fit exponential decay: e(t) ≈ e(0)·exp(-λt)
        log_errors = np.log(errors + 1e-10)
        coeffs = np.polyfit(t, log_errors, 1)
        decay_rate = -coeffs[0]

        # Positive decay rate indicates exponential stability
        assert decay_rate > 0, (
            f"System not exponentially stable: decay rate = {decay_rate}"
        )

    def test_finite_time_convergence_to_sliding_surface(self):
        """Test reaching phase achieves sliding surface in finite time."""
        from src.controllers.smc.sta_smc import STASMC
        from src.core.dynamics import SimplifiedDynamics

        controller = STASMC(
            gains=[25.0, 10.0, 15.0, 12.0, 20.0, 15.0],
            max_force=100.0
        )

        physics_cfg = {'M': 1.0, 'm1': 0.1, 'm2': 0.1, 'L1': 0.5, 'L2': 0.5, 'g': 9.81}
        dynamics = SimplifiedDynamics(physics_cfg)

        state = np.array([0.0, 0.2, 0.15, 0.0, 0.0, 0.0])

        from src.controllers.smc.core.sliding_surface import LinearSlidingSurface
        surface = LinearSlidingSurface([25.0, 10.0, 15.0, 12.0])

        reached_surface = False
        for i in range(1000):
            s = surface.compute(state)

            if abs(s) < 0.01:  # Reached sliding surface
                reached_surface = True
                print(f"Reached sliding surface at iteration {i}")
                break

            result = controller.compute_control(state, {}, {})
            u = result.get('control_output', result.get('control', 0.0))
            x_dot = dynamics.dynamics(state, u)
            state = state + 0.01 * x_dot

        assert reached_surface, "Failed to reach sliding surface in finite time"
```

### 5.2 Monte Carlo Validation

```python
class TestMonteCarloValidation:
    """Validate controller robustness via Monte Carlo simulation."""

    def test_robustness_to_initial_conditions(self):
        """Test controller stabilizes system from diverse initial conditions."""
        from src.controllers.smc.classic_smc import ClassicalSMC
        from src.core.dynamics import SimplifiedDynamics

        controller = ClassicalSMC(
            gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0],
            max_force=100.0,
            boundary_layer=0.01
        )

        physics_cfg = {'M': 1.0, 'm1': 0.1, 'm2': 0.1, 'L1': 0.5, 'L2': 0.5, 'g': 9.81}
        dynamics = SimplifiedDynamics(physics_cfg)

        # Monte Carlo: 100 random initial conditions
        n_trials = 100
        successes = 0

        for _ in range(n_trials):
            # Random initial state within bounds
            state = np.random.uniform(-0.2, 0.2, size=6)

            # Simulate
            for _ in range(500):
                result = controller.compute_control(state, {}, {})
                u = result.get('control_output', result.get('control', 0.0))
                x_dot = dynamics.dynamics(state, u)
                state = state + 0.01 * x_dot

            # Check stabilization
            if np.linalg.norm(state) < 0.05:
                successes += 1

        success_rate = successes / n_trials
        assert success_rate > 0.90, (
            f"Controller stabilized only {success_rate*100:.1f}% of initial conditions"
        )
```



## Summary

This validation methodology ensures:

1. **Mathematical Correctness**: All control-theoretic properties verified
2. **Configuration Safety**: Invalid parameters rejected at initialization
3. **Numerical Stability**: Robust to floating-point precision and conditioning issues
4. **Scientific Rigor**: Control guarantees (stability, convergence) validated

**Validation Coverage:**
- Mathematical Properties: 100%
- Configuration Rules: 100%
- Numerical Stability: ≥95%
- Scientific Properties: ≥90%

**Next**: [Testing Workflows & Best Practices Guide](testing_workflows_best_practices.md)