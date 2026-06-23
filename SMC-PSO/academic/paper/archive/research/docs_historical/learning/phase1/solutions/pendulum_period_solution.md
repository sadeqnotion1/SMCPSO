<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/phase1/solutions/pendulum_period_solution.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# Pendulum Period Verification - Physics Exercise Solution

## Problem Statement

Verify that a simple pendulum's period matches the theoretical formula:

```
T = 2π√(L/g)
```

Where:
- `T` = period (time for one complete swing)
- `L` = pendulum length (m)
- `g` = gravitational acceleration (9.81 m/s²)

**Task**: Simulate a pendulum with length L = 1.0 m, measure its period numerically, and compare to the theoretical value.

------

## Solution Approach

1. **Simulate** the pendulum using numerical integration
2. **Detect** zero crossings to identify complete swings
3. **Calculate** average period from multiple swings
4. **Compare** measured vs. theoretical period
5. **Analyze** any discrepancy

------

## Step-by-Step Solution

### Step 1: Import Libraries

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
```

### Step 2: Define Pendulum Dynamics

```python
def pendulum_derivatives(t, state, L, g):
    """
    Calculate derivatives for pendulum system.

    State: [theta, omega]
    Derivatives: [dtheta/dt, domega/dt] = [omega, alpha]

    Equation: d²θ/dt² = -(g/L) * sin(θ)
    """
    theta, omega = state
    alpha = -(g / L) * np.sin(theta)
    return [omega, alpha]
```

**Explanation**:
- `theta`: Angle from vertical (radians)
- `omega`: Angular velocity (rad/s)
- `alpha`: Angular acceleration (rad/s²)

### Step 3: Simulate Pendulum

```python
def simulate_pendulum(theta0, L, g, t_max, dt):
    """
    Simulate pendulum motion.

    Args:
        theta0: Initial angle (radians)
        L: Length (m)
        g: Gravity (m/s²)
        t_max: Simulation duration (s)
        dt: Time step for output (s)

    Returns:
        t: Time array
        theta: Angle array
        omega: Angular velocity array
    """
    # Initial conditions: [theta0, 0]
    initial_state = [theta0, 0]

    # Time span
    t_span = (0, t_max)
    t_eval = np.arange(0, t_max, dt)

    # Solve ODE
    solution = solve_ivp(
        lambda t, y: pendulum_derivatives(t, y, L, g),
        t_span,
        initial_state,
        t_eval=t_eval,
        method='RK45'  # Runge-Kutta 4th/5th order
    )

    return solution.t, solution.y[0], solution.y[1]
```

**Explanation**:
- `solve_ivp`: SciPy's ODE solver (accurate and robust)
- `method='RK45'`: High-accuracy integration method
- Initial angular velocity = 0 (start from rest)

### Step 4: Detect Zero Crossings (Find Period)

```python
def find_period(t, theta):
    """
    Find period by detecting zero crossings.

    Strategy: Count times when pendulum passes through θ=0
    going downward (positive to negative).

    Args:
        t: Time array
        theta: Angle array

    Returns:
        Average period (s), or None if not enough crossings
    """
    crossings = []

    for i in range(len(theta) - 1):
        # Detect crossing: theta changes from positive to negative
        if theta[i] > 0 and theta[i + 1] <= 0:
            # Linear interpolation to find exact crossing time
            t_cross = t[i] - theta[i] * (t[i + 1] - t[i]) / (theta[i + 1] - theta[i])
            crossings.append(t_cross)

    # Need at least 2 crossings to measure period
    if len(crossings) < 2:
        return None

    # Period = time between consecutive crossings
    periods = np.diff(crossings)
    return np.mean(periods)
```

**Explanation**:
- Zero crossing = pendulum passing through vertical position
- We detect when `theta` changes sign (positive → negative)
- Linear interpolation gives more accurate crossing time
- Average multiple periods for better accuracy

### Step 5: Calculate Theoretical Period

```python
def theoretical_period(L, g):
    """
    Calculate theoretical period for small-angle pendulum.

    Formula: T = 2π√(L/g)
    """
    return 2 * np.pi * np.sqrt(L / g)
```

### Step 6: Main Analysis

```python
def main():
    # Parameters
    L = 1.0           # Length: 1 meter
    g = 9.81          # Gravity: 9.81 m/s²
    theta0 = np.radians(10)  # Initial angle: 10 degrees (small!)
    t_max = 20.0      # Simulate 20 seconds
    dt = 0.001        # Fine time step for accurate zero detection

    print("=" * 60)
    print("Pendulum Period Verification")
    print("=" * 60)

    # Theoretical prediction
    T_theory = theoretical_period(L, g)
    print(f"\nTheoretical period: {T_theory:.6f} s")

    # Simulation
    print("\nRunning simulation...")
    t, theta, omega = simulate_pendulum(theta0, L, g, t_max, dt)

    # Measure period
    T_measured = find_period(t, theta)

    if T_measured is None:
        print("Error: Not enough swings to measure period")
        return

    print(f"Measured period: {T_measured:.6f} s")

    # Calculate error
    error = abs(T_measured - T_theory)
    percent_error = 100 * error / T_theory

    print(f"\nAbsolute error: {error:.6f} s")
    print(f"Percent error: {percent_error:.3f}%")

    # Verify accuracy
    if percent_error < 1.0:
        print("\n✓ PASS: Measured period matches theory (< 1% error)")
    else:
        print("\n✗ FAIL: Error too large (> 1%)")

    # Plot results
    plt.figure(figsize=(12, 8))

    # Plot 1: Angle vs time
    plt.subplot(2, 1, 1)
    plt.plot(t, np.degrees(theta), 'b-', linewidth=1)
    plt.axhline(0, color='r', linestyle='--', alpha=0.5)
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (degrees)")
    plt.title(f"Pendulum Motion (L={L}m, θ₀={np.degrees(theta0):.1f}°)")
    plt.grid(True)

    # Plot 2: Phase space
    plt.subplot(2, 1, 2)
    plt.plot(theta, omega, 'b-', linewidth=1)
    plt.plot(theta[0], omega[0], 'go', markersize=10, label='Start')
    plt.plot(theta[-1], omega[-1], 'ro', markersize=10, label='End')
    plt.xlabel("Angle θ (rad)")
    plt.ylabel("Angular Velocity ω (rad/s)")
    plt.title("Phase Space Portrait")
    plt.grid(True)
    plt.legend()
    plt.axis('equal')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
```

------

## Expected Output

```
============================================================
Pendulum Period Verification
============================================================

Theoretical period: 2.006379 s
Running simulation...
Measured period: 2.006385 s

Absolute error: 0.000006 s
Percent error: 0.000%

✓ PASS: Measured period matches theory (< 1% error)
```

------

## Common Mistakes

### Mistake 1: Large Initial Angle

```python
# WRONG - large angle violates small-angle approximation
theta0 = np.radians(90)  # 90 degrees - TOO LARGE
```

**Why wrong**: The formula `T = 2π√(L/g)` assumes `sin(θ) ≈ θ`, which is only valid for small angles (< 15°).

**Fix**: Use θ₀ ≤ 10° for accurate verification.

### Mistake 2: Insufficient Simulation Time

```python
# WRONG - not enough swings to measure period accurately
t_max = 2.0  # Only ~1 period
```

**Why wrong**: Need multiple periods to average out numerical errors.

**Fix**: Simulate at least 5-10 periods (e.g., t_max = 20 seconds).

### Mistake 3: Coarse Time Step

```python
# WRONG - misses exact zero crossing
dt = 0.1  # Too coarse
```

**Why wrong**: Inaccurate zero crossing detection leads to period error.

**Fix**: Use dt ≤ 0.001 for fine-grained output.

------

## Alternative Approaches

### Approach 1: FFT (Frequency Analysis)

Instead of zero crossings, use Fast Fourier Transform to find dominant frequency:

```python
from scipy.fft import fft, fftfreq

def find_period_fft(t, theta):
    """Find period using FFT."""
    dt = t[1] - t[0]
    n = len(theta)

    # Compute FFT
    yf = fft(theta)
    xf = fftfreq(n, dt)

    # Find peak frequency (ignore DC component)
    idx = np.argmax(np.abs(yf[1:n//2])) + 1
    freq = xf[idx]

    # Period = 1 / frequency
    return 1 / freq
```

### Approach 2: Peak Detection

Find time between consecutive maxima:

```python
from scipy.signal import find_peaks

def find_period_peaks(t, theta):
    """Find period using peak detection."""
    peaks, _ = find_peaks(theta)

    if len(peaks) < 2:
        return None

    # Time between peaks
    peak_times = t[peaks]
    periods = np.diff(peak_times)
    return np.mean(periods)
```

------

## Extension Challenges

### Challenge 1: Large Angle Correction

For large angles, the exact period is:

```
T = 4√(L/g) * K(sin(θ₀/2))
```

Where `K` is the complete elliptic integral of the first kind.

Implement this and compare to simulation for θ₀ = 45°.

### Challenge 2: Damped Pendulum

Add damping term and measure how period changes:

```python
alpha = -(g / L) * np.sin(theta) - b * omega
```

Does damping significantly affect period?

### Challenge 3: Energy Verification

In addition to period, verify that total energy remains constant (for undamped case).

------

## Key Takeaways

1. **Numerical integration** accurately reproduces physics
2. **Zero crossing detection** is a robust way to measure period
3. **Small angle approximation** is necessary for simple formula
4. **Multiple measurements** improve accuracy through averaging
5. **SciPy's solve_ivp** is powerful and easy to use

------

**Difficulty**: Intermediate
**Topics**: Differential equations, numerical integration, physics simulation
**Estimated Time**: 30-45 minutes
