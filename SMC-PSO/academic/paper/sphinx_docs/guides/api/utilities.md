# Utilities API Guide

**Module:** `src.utils`

**What This API Does:**
This API provides helper functions for common tasks like validating inputs, monitoring performance, plotting results, and analyzing simulations. These utilities save you from writing repetitive code.

**Who This Is For:**
- Developers validating controller implementations
- Researchers analyzing experimental results
- Anyone monitoring real-time control loop performance

**Level:** Intermediate

**Quick Start:**
```python
# Validate controller gains
from src.utils.validation import validate_gains
validate_gains([10, 5, 8, 3, 15, 2])  # Returns True or raises error

# Monitor control loop timing
from src.utils.monitoring import LatencyMonitor
monitor = LatencyMonitor(dt=0.01)
# ... use in control loop
```

---

## Table of Contents

- [Overview](#overview)
- [Validation](#validation)
- [Control Primitives](#control-primitives)
- [Monitoring](#monitoring)
- [Analysis Tools](#analysis-tools)
- [Visualization](#visualization)
- [Integration Patterns](#integration-patterns)



## Overview

The Utilities API provides helper functions and tools for validation, control signal processing, performance monitoring, and result analysis.

**Key Features:**
- ✅ **Validation:** State and parameter bounds checking
- ✅ **Control Primitives:** Saturation, deadzone, sign functions
- ✅ **Monitoring:** Real-time performance tracking
- ✅ **Analysis:** Metrics computation and statistical analysis
- ✅ **Visualization:** Plotting and animation tools

**Related Documentation:**
- [How-To: Testing & Validation](../how-to/testing-validation.md)
- [How-To: Result Analysis](../how-to/result-analysis.md)
- [User Guide: Best Practices](../user-guide.md#best-practices)
- [Technical Reference](../../reference/utils/__init__.md)



## Validation

### State Validation

**Check state vector validity:**
```python
from src.utils.validation import validate_state

state = np.array([0.1, 0.05, 0.2, 0.1, 0.25, 0.15])

# Basic validation
is_valid = validate_state(state)

# With bounds checking
is_valid = validate_state(
    state,
    x_bounds=(-1.0, 1.0),        # Cart position limits
    theta_bounds=(-0.5, 0.5),    # Angle limits (rad)
    velocity_bounds=(-2.0, 2.0)  # Velocity limits
)

if not is_valid:
    print("State violates constraints!")
```

**Check for numerical issues:**
```python
from src.utils.validation import check_numerical_health

state = np.array([0.1, 0.05, 0.2, 0.1, 0.25, 0.15])

health = check_numerical_health(state)

if not health['is_finite']:
    print("State contains NaN or Inf!")
if not health['is_bounded']:
    print("State values unreasonably large!")
```

## Parameter Validation

**Validate physics parameters:**
```python
from src.utils.validation import validate_physics_params

params = config.dip_params

try:
    validate_physics_params(params)
    print("Physics parameters valid")
except ValueError as e:
    print(f"Invalid parameters: {e}")

# Checks:
# - Masses > 0
# - Lengths > 0
# - Friction coefficients ≥ 0
# - Gravity ≈ 9.81 m/s²
# - Inertias > 0
```

**Validate controller gains:**
```python
from src.utils.validation import validate_controller_gains

gains = [10, 8, 15, 12, 50, 5]
controller_type = 'classical_smc'

is_valid = validate_controller_gains(gains, controller_type)

# Checks:
# - Correct number of gains
# - All gains positive (where required)
# - Gains within reasonable bounds
```

## Input Sanitization

```python
from src.utils.validation import sanitize_input

# Clean and validate user input
user_input = "  10.5, 8.0, 15.2, 12.1, 50.0, 5.5  "
gains = sanitize_input(user_input, expected_length=6)

# Returns: [10.5, 8.0, 15.2, 12.1, 50.0, 5.5]
```



## Control Primitives

### Saturation

**Apply control saturation:**
```python
from src.utils.control import saturate

control = 150.0
max_force = 100.0

# Hard saturation
saturated = saturate(control, max_force)
# Returns: 100.0

# Symmetric saturation
saturated = saturate(control, -max_force, max_force)

# Soft saturation (smooth)
from src.utils.control import soft_saturate

soft_sat = soft_saturate(control, max_force, smoothness=0.1)
# Smooth transition near limits
```

## Deadzone

**Apply deadzone to reduce noise:**
```python
from src.utils.control import apply_deadzone

control = 2.5
deadzone_threshold = 5.0

# Linear deadzone
output = apply_deadzone(control, deadzone_threshold)
# Returns: 0.0 (below threshold)

control = 7.5
output = apply_deadzone(control, deadzone_threshold)
# Returns: 2.5 (7.5 - 5.0)

# Smooth deadzone
from src.utils.control import smooth_deadzone

output = smooth_deadzone(control, deadzone_threshold, smoothness=0.5)
```

## Sign Functions

**Smooth sign function:**
```python
from src.utils.control import smooth_sign

s = 0.5  # Sliding surface value
epsilon = 0.01  # Boundary layer

# Standard sign (discontinuous)
sign_output = np.sign(s)  # Returns: 1.0

# Smooth sign (continuous)
smooth_output = smooth_sign(s, epsilon)
# Returns: tanh(s/epsilon)

# Linear approximation in boundary layer
from src.utils.control import linear_sign

linear_output = linear_sign(s, epsilon)
# Returns: s/epsilon if |s| < epsilon, else sign(s)
```

## Filtering

**Low-pass filter for control smoothing:**
```python
from src.utils.control import LowPassFilter

# Create filter
lpf = LowPassFilter(cutoff_freq=10.0, dt=0.01)

# Filter control signal
controls = []
for i in range(len(control_sequence)):
    filtered = lpf.update(control_sequence[i])
    controls.append(filtered)

# Reset filter
lpf.reset()
```

**Moving average filter:**
```python
from src.utils.control import MovingAverageFilter

maf = MovingAverageFilter(window_size=10)

for control in control_sequence:
    smoothed = maf.update(control)
```



## Monitoring

### Performance Monitoring

**Real-time performance tracking:**
```python
from src.utils.monitoring import PerformanceMonitor

monitor = PerformanceMonitor(dt=0.01)

# Start monitoring
monitor.start()

# During simulation
for t, state, control in simulation_loop:
    monitor.update(t, state, control)

    # Check metrics
    if monitor.get_current_ise() > 100:
        print("Warning: High ISE detected")

# Get final statistics
stats = monitor.get_statistics()
print(f"ISE: {stats['ise']:.4f}")
print(f"Max theta: {stats['max_theta']:.3f} rad")
print(f"Settling time: {stats['settling_time']:.2f} s")
```

## Resource Monitoring

**Monitor memory usage:**
```python
from src.utils.monitoring import MemoryMonitor

mem_monitor = MemoryMonitor(threshold_mb=500)

# Check memory periodically
while running:
    if alert := mem_monitor.check():
        print(alert)  # "Alert: 550MB > 500MB"
        # Clean up
        history = controller.initialize_history()
        import gc
        gc.collect()
```

### Latency Monitoring

**Track control loop timing:**
```python
from src.utils.monitoring import LatencyMonitor

latency_monitor = LatencyMonitor(dt=0.01, deadline=0.01)

for timestep in range(n_steps):
    start = latency_monitor.start()

    # Compute control
    control = controller.compute_control(state, state_vars, history)

    # Check if deadline met
    missed = latency_monitor.end(start)
    if missed:
        print(f"Deadline miss at step {timestep}")

# Get statistics
stats = latency_monitor.get_stats()
print(f"Average latency: {stats['avg_latency']:.4f} s")
print(f"Deadline misses: {stats['miss_count']}/{n_steps}")
```

## Saturation Monitoring

**Track control saturation events:**
```python
from src.utils.monitoring import SaturationMonitor

sat_monitor = SaturationMonitor(max_force=100.0)

for control in control_sequence:
    sat_monitor.update(control)

# Get saturation statistics
stats = sat_monitor.get_statistics()
print(f"Saturation percentage: {stats['saturation_percentage']:.1f}%")
print(f"Total saturated steps: {stats['saturated_count']}")
```



## Analysis Tools

### Metrics Computation

**Compute standard control metrics:**
```python
from src.utils.analysis import compute_metrics

result = {
    't': t,
    'state': state_trajectory,
    'control': control_sequence
}

metrics = compute_metrics(result)

print(f"ISE: {metrics['ise']:.4f}")
print(f"ITAE: {metrics['itae']:.4f}")
print(f"RMS Control: {metrics['rms_control']:.4f}")
print(f"Settling Time: {metrics['settling_time']:.2f} s")
```

**Custom metric computation:**
```python
from src.utils.analysis import (
    compute_ise, compute_itae, compute_overshoot,
    compute_settling_time, compute_control_effort
)

# Individual metrics
ise = compute_ise(t, state[:, 2:4])  # ISE for θ₁, θ₂
itae = compute_itae(t, state[:, 2:4])
overshoot = compute_overshoot(state[:, 2])  # First pendulum
settling = compute_settling_time(t, state[:, 2], threshold=0.02)
energy = compute_control_effort(t, control)
```

## Statistical Analysis

**Confidence intervals:**
```python
from src.utils.analysis import compute_confidence_interval

# Monte Carlo results
ise_values = [result['metrics']['ise'] for result in monte_carlo_results]

mean, ci_lower, ci_upper = compute_confidence_interval(
    ise_values,
    confidence=0.95
)

print(f"ISE: {mean:.4f} [{ci_lower:.4f}, {ci_upper:.4f}] (95% CI)")
```

**Hypothesis testing:**
```python
from src.utils.analysis import compare_controllers_statistical

# Compare two controller results
controller_a_results = monte_carlo_results_a
controller_b_results = monte_carlo_results_b

comparison = compare_controllers_statistical(
    controller_a_results,
    controller_b_results,
    metric='ise'
)

print(f"t-statistic: {comparison['t_statistic']:.4f}")
print(f"p-value: {comparison['p_value']:.4f}")

if comparison['p_value'] < 0.05:
    print("Statistically significant difference")
```

## Performance Profiling

**Profile simulation performance:**
```python
from src.utils.analysis import profile_simulation

def run_simulation():
    return runner.run(controller)

profile = profile_simulation(run_simulation, n_runs=100)

print(f"Average time: {profile['mean_time']:.4f} s")
print(f"Std dev: {profile['std_time']:.4f} s")
print(f"Min time: {profile['min_time']:.4f} s")
print(f"Max time: {profile['max_time']:.4f} s")
```



## Visualization

### Plotting Results

**Standard result plots:**
```python
from src.utils.visualization import plot_results

# Plot state trajectories and control
fig, axes = plot_results(result, show=True)

# Customize plots
fig, axes = plot_results(
    result,
    plot_types=['state', 'control', 'phase'],
    figsize=(15, 10),
    show=False
)
plt.savefig('simulation_results.png', dpi=300)
```

**Individual plot functions:**
```python
from src.utils.visualization import (
    plot_state_trajectory,
    plot_control_signal,
    plot_phase_portrait,
    plot_sliding_surface
)

# State trajectory
fig1 = plot_state_trajectory(result['t'], result['state'])

# Control signal
fig2 = plot_control_signal(result['t'], result['control'], max_force=100)

# Phase portrait
fig3 = plot_phase_portrait(
    result['state'][:, 2],  # theta1
    result['state'][:, 3]   # dtheta1
)

# Sliding surface
if 'sliding_surface' in result:
    fig4 = plot_sliding_surface(result['t'], result['sliding_surface'])
```

## Animation

**Create animation of pendulum motion:**
```python
from src.utils.visualization import DIPAnimator

animator = DIPAnimator(config.dip_params)

# Create animation
anim = animator.animate(
    result['t'],
    result['state'],
    save_path='simulation.mp4',
    fps=30
)
```

## Comparison Plots

**Compare multiple controllers:**
```python
from src.utils.visualization import plot_controller_comparison

results_dict = {
    'Classical SMC': result_classical,
    'STA-SMC': result_sta,
    'Adaptive SMC': result_adaptive
}

fig = plot_controller_comparison(
    results_dict,
    metrics=['ise', 'settling_time', 'control_effort']
)
plt.savefig('controller_comparison.png')
```



## Integration Patterns

### Pattern 1: Validation Pipeline

```python
from src.utils.validation import (
    validate_physics_params,
    validate_controller_gains,
    validate_state
)

# Validate configuration
try:
    validate_physics_params(config.dip_params)
    validate_controller_gains(gains, controller_type)
    validate_state(initial_state)
    print("✅ All validation passed")
except ValueError as e:
    print(f"❌ Validation failed: {e}")
    sys.exit(1)

# Proceed with simulation
result = runner.run(controller)
```

## Pattern 2: Monitoring & Analysis Pipeline

```python
from src.utils.monitoring import PerformanceMonitor
from src.utils.analysis import compute_metrics
from src.utils.visualization import plot_results

# Run with monitoring
monitor = PerformanceMonitor(dt=0.01)
monitor.start()

result = runner.run(controller)

# Analyze
metrics = compute_metrics(result)
monitor_stats = monitor.get_statistics()

# Visualize
plot_results(result, show=True)

# Report
print(f"Performance Metrics:")
print(f"  ISE: {metrics['ise']:.4f}")
print(f"  Settling Time: {metrics['settling_time']:.2f} s")
print(f"  Saturation: {monitor_stats['saturation_percentage']:.1f}%")
```

## Pattern 3: Statistical Validation

```python
from src.utils.analysis import (
    compute_confidence_interval,
    compare_controllers_statistical
)

# Run Monte Carlo
n_trials = 100
results = []

for i in range(n_trials):
    ic = np.random.normal(ic_mean, ic_std)
    result = runner.run(controller, initial_state=ic)
    results.append(result)

# Compute statistics
ise_values = [r['metrics']['ise'] for r in results]
mean_ise, ci_lower, ci_upper = compute_confidence_interval(ise_values)

print(f"ISE: {mean_ise:.4f} [{ci_lower:.4f}, {ci_upper:.4f}]")

# Compare with baseline
if baseline_results:
    comparison = compare_controllers_statistical(results, baseline_results)
    print(f"Improvement: {comparison['improvement_percent']:.1f}%")
    print(f"p-value: {comparison['p_value']:.4f}")
```



## Next Steps

- **Learn validation:** [How-To: Testing & Validation](../how-to/testing-validation.md)
- **Analyze results:** [How-To: Result Analysis](../how-to/result-analysis.md)
- **Best practices:** [User Guide: Best Practices](../user-guide.md#best-practices)
- **Technical details:** [Utils Technical Reference](../../reference/utils/__init__.md)



**Last Updated:** October 2025
