# How-To: Result Analysis

**Type:** Task-Oriented Guide
**Level:** Intermediate
**Prerequisites:** [How-To: Running Simulations](running-simulations.md)



## Overview

This guide shows you how to analyze simulation results, compute statistics, create visualizations, and export data for publication or further processing.

**Common Tasks:**
- Interpret performance metrics
- Compare multiple controllers
- Perform statistical validation
- Create publication-quality plots
- Export data to other tools



## Table of Contents

- [Understanding Metrics](#understanding-metrics)
- [Statistical Analysis](#statistical-analysis)
- [Visualization Recipes](#visualization-recipes)
- [Data Export](#data-export)



## Understanding Metrics

### Core Performance Metrics

The framework computes these metrics automatically for every simulation:

| Metric | Formula | Physical Meaning | Lower is Better |
|--------|---------|------------------|-----------------|
| **ISE** | ∫‖x‖² dt | Total squared tracking error | ✓ |
| **ITAE** | ∫t·‖x‖ dt | Time-weighted error (penalizes slow settling) | ✓ |
| **Settling Time** | t when ‖x‖ < 5% | Time to reach near-equilibrium | ✓ |
| **Overshoot** | max(‖x‖) / setpoint × 100% | Peak deviation | ✓ |
| **Control Effort** | ∫‖u‖ dt | Total energy consumption | ✓ |

### Loading Results

```python
import json
import numpy as np

# Load saved results
with open('results_classical.json') as f:
    data = json.load(f)

# Extract metrics
metrics = data['metrics']
print(f"ISE:              {metrics['ise']:.4f}")
print(f"ITAE:             {metrics['itae']:.4f}")
print(f"Settling Time:    {metrics['settling_time']:.2f} s")
print(f"Peak Overshoot:   {metrics['overshoot']:.2f}%")
print(f"Control Effort:   {metrics['control_effort']:.2f}")

# Extract trajectories
time = np.array(data['time'])
state = np.array(data['state'])
control = np.array(data['control'])

# Separate states
cart_pos = state[:, 0]
cart_vel = state[:, 1]
theta1 = state[:, 2]
dtheta1 = state[:, 3]
theta2 = state[:, 4]
dtheta2 = state[:, 5]
```

## Metric Interpretation

### ISE (Integral Squared Error)

**What it measures:** Total squared deviation from equilibrium

**When to use:**
- Comparing controllers for tracking accuracy
- Quadratic cost in optimal control
- Emphasizes large errors more than small errors

**Typical values:**
- good: ISE < 0.3
- Good: 0.3 ≤ ISE < 0.6
- Acceptable: 0.6 ≤ ISE < 1.0
- Poor: ISE ≥ 1.0

**Example calculation:**
```python
# Manual ISE calculation
def compute_ise(time, state):
    """Compute ISE from state trajectory."""
    dt = time[1] - time[0]  # Assume uniform sampling
    error_norm = np.linalg.norm(state, axis=1)
    ise = np.sum(error_norm**2) * dt
    return ise

ise_manual = compute_ise(time, state)
print(f"ISE (manual): {ise_manual:.4f}")
```

## ITAE (Integral Time-Absolute Error)

**What it measures:** Time-weighted error (penalizes slow convergence)

**When to use:**
- Comparing controllers for convergence speed
- Applications where fast settling is critical
- More realistic than ISE (considers time)

**Typical values:**
- good: ITAE < 0.8
- Good: 0.8 ≤ ITAE < 1.5
- Acceptable: 1.5 ≤ ITAE < 3.0
- Poor: ITAE ≥ 3.0

**Example:**
```python
def compute_itae(time, state):
    """Compute ITAE from state trajectory."""
    dt = time[1] - time[0]
    error_norm = np.linalg.norm(state, axis=1)
    itae = np.sum(time * np.abs(error_norm)) * dt
    return itae

itae_manual = compute_itae(time, state)
print(f"ITAE (manual): {itae_manual:.4f}")
```

### Settling Time

**What it measures:** Time to reach and stay within ±5% of setpoint

**When to use:**
- Real-time control requirements
- Transient response characterization
- Meeting performance specifications

**Typical values:**
- good: < 2.0 s
- Good: 2.0-3.5 s
- Acceptable: 3.5-5.0 s
- Poor: > 5.0 s

#### Control Effort

**What it measures:** Total energy consumed by actuator

**When to use:**
- Energy-constrained systems (battery-powered)
- Actuator wear considerations
- Comparing efficiency across controllers

**Interpretation:**
```python
# Analyze control effort components
control_array = np.array(control)
peak_control = np.max(np.abs(control_array))
mean_control = np.mean(np.abs(control_array))
rms_control = np.sqrt(np.mean(control_array**2))

print(f"Peak Control: {peak_control:.2f} N")
print(f"Mean Control: {mean_control:.2f} N")
print(f"RMS Control:  {rms_control:.2f} N")
```



## Statistical Analysis

### Comparing Two Controllers

```python
import json
import numpy as np
from scipy import stats

# Load results from two controllers
with open('results_classical.json') as f:
    classical = json.load(f)

with open('results_sta.json') as f:
    sta = json.load(f)

# Extract ISE values
ise_classical = classical['metrics']['ise']
ise_sta = sta['metrics']['ise']

# Compute improvement
improvement = (ise_classical - ise_sta) / ise_classical * 100
print(f"ISE Improvement: {improvement:.1f}%")
print(f"Classical SMC: {ise_classical:.4f}")
print(f"STA-SMC:       {ise_sta:.4f}")
```

## Monte Carlo Analysis

```python
# example-metadata:
# runnable: false

# Load multiple trials
n_trials = 50
ise_classical_trials = []
ise_sta_trials = []

for i in range(n_trials):
    with open(f'results_classical_trial_{i}.json') as f:
        ise_classical_trials.append(json.load(f)['metrics']['ise'])

    with open(f'results_sta_trial_{i}.json') as f:
        ise_sta_trials.append(json.load(f)['metrics']['ise'])

# Convert to arrays
ise_classical_trials = np.array(ise_classical_trials)
ise_sta_trials = np.array(ise_sta_trials)

# Compute summary statistics
print("Classical SMC:")
print(f"  Mean ISE: {np.mean(ise_classical_trials):.4f}")
print(f"  Std ISE:  {np.std(ise_classical_trials):.4f}")
print(f"  Min ISE:  {np.min(ise_classical_trials):.4f}")
print(f"  Max ISE:  {np.max(ise_classical_trials):.4f}")

print("\nSTA-SMC:")
print(f"  Mean ISE: {np.mean(ise_sta_trials):.4f}")
print(f"  Std ISE:  {np.std(ise_sta_trials):.4f}")
print(f"  Min ISE:  {np.min(ise_sta_trials):.4f}")
print(f"  Max ISE:  {np.max(ise_sta_trials):.4f}")
```

## Hypothesis Testing

### Welch's t-test (Unequal Variances)

```python
from scipy import stats

# Perform Welch's t-test
t_stat, p_value = stats.ttest_ind(
    ise_classical_trials,
    ise_sta_trials,
    equal_var=False  # Welch's t-test
)

print(f"\nWelch's t-test:")
print(f"  t-statistic: {t_stat:.4f}")
print(f"  p-value:     {p_value:.6f}")

if p_value < 0.05:
    print("  Result: Statistically significant difference (p < 0.05)")
else:
    print("  Result: No statistically significant difference")
```

## Effect Size (Cohen's d)

```python
# example-metadata:
# runnable: false

# Compute Cohen's d (effect size)
mean_diff = np.mean(ise_classical_trials) - np.mean(ise_sta_trials)
pooled_std = np.sqrt(
    (np.std(ise_classical_trials)**2 + np.std(ise_sta_trials)**2) / 2
)
cohens_d = mean_diff / pooled_std

print(f"\nEffect Size (Cohen's d): {cohens_d:.4f}")
print(f"  Interpretation: ", end="")
if abs(cohens_d) < 0.2:
    print("Small effect")
elif abs(cohens_d) < 0.5:
    print("Medium effect")
else:
    print("Large effect")
```

## Confidence Intervals

```python
# example-metadata:
# runnable: false

# 95% Confidence Interval for mean ISE
confidence_level = 0.95
alpha = 1 - confidence_level

# Classical SMC
ci_classical = stats.t.interval(
    confidence_level,
    len(ise_classical_trials) - 1,
    loc=np.mean(ise_classical_trials),
    scale=stats.sem(ise_classical_trials)
)

# STA-SMC
ci_sta = stats.t.interval(
    confidence_level,
    len(ise_sta_trials) - 1,
    loc=np.mean(ise_sta_trials),
    scale=stats.sem(ise_sta_trials)
)

print(f"\n95% Confidence Intervals:")
print(f"  Classical SMC: [{ci_classical[0]:.4f}, {ci_classical[1]:.4f}]")
print(f"  STA-SMC:       [{ci_sta[0]:.4f}, {ci_sta[1]:.4f}]")
```

## Bootstrap Confidence Intervals (Non-Parametric)

```python
from scipy.stats import bootstrap

# Bootstrap confidence interval (more robust, no normality assumption)
def compute_mean(data, axis):
    return np.mean(data, axis=axis)

# Classical SMC bootstrap CI
bootstrap_result_classical = bootstrap(
    (ise_classical_trials,),
    compute_mean,
    n_resamples=10000,
    confidence_level=0.95,
    method='percentile'
)

print(f"\nBootstrap 95% CI (Classical): "
      f"[{bootstrap_result_classical.confidence_interval.low:.4f}, "
      f"{bootstrap_result_classical.confidence_interval.high:.4f}]")
```



## Visualization Recipes

### Basic State Trajectories

```python
import matplotlib.pyplot as plt

# Load data
with open('results_classical.json') as f:
    data = json.load(f)

time = np.array(data['time'])
state = np.array(data['state'])
control = np.array(data['control'])

# Create figure
fig, axes = plt.subplots(3, 1, figsize=(12, 9))

# Pendulum angles
axes[0].plot(time, state[:, 2], 'b-', linewidth=2, label='θ₁ (first pendulum)')
axes[0].plot(time, state[:, 4], 'r-', linewidth=2, label='θ₂ (second pendulum)')
axes[0].axhline(0, color='k', linestyle='--', linewidth=0.5)
axes[0].set_ylabel('Angle (rad)', fontsize=12)
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3)

# Angular velocities
axes[1].plot(time, state[:, 3], 'b-', linewidth=2, label='dθ₁')
axes[1].plot(time, state[:, 5], 'r-', linewidth=2, label='dθ₂')
axes[1].axhline(0, color='k', linestyle='--', linewidth=0.5)
axes[1].set_ylabel('Angular Velocity (rad/s)', fontsize=12)
axes[1].legend(fontsize=10)
axes[1].grid(True, alpha=0.3)

# Control signal
axes[2].plot(time, control, 'g-', linewidth=2)
axes[2].axhline(100, color='r', linestyle='--', label='Max force')
axes[2].axhline(-100, color='r', linestyle='--')
axes[2].set_xlabel('Time (s)', fontsize=12)
axes[2].set_ylabel('Control Force (N)', fontsize=12)
axes[2].legend(fontsize=10)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('state_trajectories.png', dpi=300)
plt.savefig('state_trajectories.pdf')
plt.show()
```

## Comparative Visualization (Multiple Controllers)

```python
# example-metadata:
# runnable: false

controllers = ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
colors = ['blue', 'red', 'green', 'purple']
labels = ['Classical', 'Super-Twisting', 'Adaptive', 'Hybrid']

fig, ax = plt.subplots(figsize=(12, 6))

for ctrl, color, label in zip(controllers, colors, labels):
    with open(f'results_{ctrl}.json') as f:
        data = json.load(f)

    time = np.array(data['time'])
    state = np.array(data['state'])

    # Plot first pendulum angle
    ax.plot(time, state[:, 2], color=color, linewidth=2, label=label)

ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
ax.set_xlabel('Time (s)', fontsize=14)
ax.set_ylabel('θ₁ (rad)', fontsize=14)
ax.set_title('Controller Comparison: First Pendulum Angle', fontsize=16)
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('controller_comparison.png', dpi=300)
plt.show()
```

### Phase Portrait

```python
# example-metadata:
# runnable: false

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# First pendulum phase portrait
axes[0].plot(state[:, 2], state[:, 3], 'b-', linewidth=1.5)
axes[0].plot(state[0, 2], state[0, 3], 'go', markersize=10, label='Start')
axes[0].plot(state[-1, 2], state[-1, 3], 'ro', markersize=10, label='End')
axes[0].set_xlabel('θ₁ (rad)', fontsize=12)
axes[0].set_ylabel('dθ₁ (rad/s)', fontsize=12)
axes[0].set_title('First Pendulum Phase Portrait', fontsize=14)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Second pendulum phase portrait
axes[1].plot(state[:, 4], state[:, 5], 'r-', linewidth=1.5)
axes[1].plot(state[0, 4], state[0, 5], 'go', markersize=10, label='Start')
axes[1].plot(state[-1, 4], state[-1, 5], 'ro', markersize=10, label='End')
axes[1].set_xlabel('θ₂ (rad)', fontsize=12)
axes[1].set_ylabel('dθ₂ (rad/s)', fontsize=12)
axes[1].set_title('Second Pendulum Phase Portrait', fontsize=14)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phase_portraits.png', dpi=300)
plt.show()
```

## Bar Chart (Metrics Comparison)

```python
import pandas as pd

# Load metrics from all controllers
metrics_data = []
for ctrl, label in zip(controllers, labels):
    with open(f'results_{ctrl}.json') as f:
        data = json.load(f)
        metrics_data.append({
            'Controller': label,
            'ISE': data['metrics']['ise'],
            'Settling Time': data['metrics']['settling_time'],
            'Overshoot': data['metrics']['overshoot']
        })

df = pd.DataFrame(metrics_data)

# Create bar chart
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# ISE
axes[0].bar(df['Controller'], df['ISE'], color=colors)
axes[0].set_ylabel('ISE', fontsize=12)
axes[0].set_title('Tracking Accuracy (ISE)', fontsize=14)
axes[0].grid(axis='y', alpha=0.3)

# Settling Time
axes[1].bar(df['Controller'], df['Settling Time'], color=colors)
axes[1].set_ylabel('Time (s)', fontsize=12)
axes[1].set_title('Settling Time', fontsize=14)
axes[1].grid(axis='y', alpha=0.3)

# Overshoot
axes[2].bar(df['Controller'], df['Overshoot'], color=colors)
axes[2].set_ylabel('Overshoot (%)', fontsize=12)
axes[2].set_title('Peak Overshoot', fontsize=14)
axes[2].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('metrics_comparison.png', dpi=300)
plt.show()
```



## Data Export

### Export to CSV

```python
import pandas as pd

# Load data
with open('results_classical.json') as f:
    data = json.load(f)

# Create DataFrame
df = pd.DataFrame({
    'time': data['time'],
    'cart_pos': np.array(data['state'])[:, 0],
    'cart_vel': np.array(data['state'])[:, 1],
    'theta1': np.array(data['state'])[:, 2],
    'dtheta1': np.array(data['state'])[:, 3],
    'theta2': np.array(data['state'])[:, 4],
    'dtheta2': np.array(data['state'])[:, 5],
    'control': data['control']
})

# Save to CSV
df.to_csv('simulation_results.csv', index=False)
print("Exported to simulation_results.csv")
```

## Export to MATLAB

```python
from scipy.io import savemat

# Prepare data for MATLAB
matlab_data = {
    'time': np.array(data['time']),
    'state': np.array(data['state']),
    'control': np.array(data['control']),
    'metrics': {
        'ISE': data['metrics']['ise'],
        'ITAE': data['metrics']['itae'],
        'settling_time': data['metrics']['settling_time']
    }
}

# Save to .mat file
savemat('simulation_results.mat', matlab_data)
print("Exported to simulation_results.mat")
```

## Generate LaTeX Table

```python
# example-metadata:
# runnable: false

# Create metrics table for LaTeX
metrics_table = []
for ctrl, label in zip(controllers, labels):
    with open(f'results_{ctrl}.json') as f:
        metrics = json.load(f)['metrics']
        metrics_table.append([
            label,
            f"{metrics['ise']:.4f}",
            f"{metrics['itae']:.4f}",
            f"{metrics['settling_time']:.2f}",
            f"{metrics['overshoot']:.2f}"
        ])

# Generate LaTeX
latex = r"""\begin{table}[h]
\centering
\caption{Controller Performance Comparison}
\begin{tabular}{lcccc}
\hline
Controller & ISE & ITAE & Settling Time (s) & Overshoot (\%) \\
\hline
"""

for row in metrics_table:
    latex += " & ".join(row) + r" \\" + "\n"

latex += r"""\hline
\end{tabular}
\end{table}"""

print(latex)

# Save to file
with open('metrics_table.tex', 'w') as f:
    f.write(latex)
```



## Next Steps

- [How-To: Optimization Workflows](optimization-workflows.md): Tune gains with PSO
- [How-To: Running Simulations](running-simulations.md): Execute experiments
- [Tutorial 05: Research Workflow](../tutorials/tutorial-05-research-workflow.md): Publication-ready studies
- [User Guide](../user-guide.md): Complete reference



**Last Updated:** October 2025
