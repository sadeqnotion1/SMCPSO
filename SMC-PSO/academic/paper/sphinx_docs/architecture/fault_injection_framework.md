# Fault Injection Framework Architecture

**Version:** 1.0
**Date:** 2025-11-11
**Status:** Operational
**Phase:** Level 1, Phase 1.3

---

## Table of Contents

1. [Overview](#overview)
2. [Fault Taxonomy](#fault-taxonomy)
3. [Injection Points](#injection-points)
4. [Configuration Format](#configuration-format)
5. [Expected vs Observed Behavior Models](#expected-vs-observed-behavior-models)
6. [Robustness Metrics](#robustness-metrics)
7. [Implementation Architecture](#implementation-architecture)
8. [Usage Examples](#usage-examples)
9. [Validation Strategy](#validation-strategy)

---

## Overview

The Fault Injection Framework provides systematic chaos testing capabilities for validating controller robustness under adverse conditions. It enables researchers to:

- Inject realistic sensor, actuator, and parametric faults
- Test controller performance under stress
- Quantify robustness through degradation metrics
- Compare controllers across fault scenarios
- Identify vulnerabilities before deployment

**Design Principles:**

- **Realism:** Fault models match real-world sensor/actuator characteristics
- **Composability:** Multiple faults can be combined
- **Reproducibility:** Seeded randomness ensures repeatability
- **Configurability:** YAML-based scenario definition
- **Measurability:** Quantitative robustness assessment

---

## Fault Taxonomy

### 1. Sensor Faults

Faults affecting measurement accuracy and reliability.

#### 1.1 Gaussian Noise

**Description:** Additive white Gaussian noise (AWGN) corrupts sensor readings.

**Parameters:**
- `snr_db`: Signal-to-noise ratio in decibels (50, 30, 10 typical)
- `noise_type`: Distribution ('gaussian', 'uniform', 'salt_pepper')

**Model:**
```
y_noisy(t) = y_true(t) + n(t)
n(t) ~ N(0, sigma^2)
sigma = y_rms / (10^(SNR_dB/20))
```

**Severity Levels:**
- **Mild:** SNR = 50 dB (high-quality sensors)
- **Moderate:** SNR = 30 dB (typical industrial sensors)
- **Severe:** SNR = 10 dB (degraded/failing sensors)

**Use Cases:**
- IMU noise in harsh environments
- Encoder quantization effects
- Electrical interference

#### 1.2 Bias (Constant Offset)

**Description:** Systematic error causing constant shift in readings.

**Parameters:**
- `bias_magnitude`: Offset value (absolute or percentage)
- `bias_type`: 'constant', 'drift' (time-varying)

**Model:**
```
y_biased(t) = y_true(t) + b
```

**Severity Levels:**
- **Mild:** 1-5% of measurement range
- **Moderate:** 5-10% of measurement range
- **Severe:** 10-20% of measurement range

**Use Cases:**
- Accelerometer bias instability
- Zero-point drift in sensors
- Calibration errors

#### 1.3 Dropout (Data Loss)

**Description:** Intermittent loss of sensor measurements.

**Parameters:**
- `dropout_rate`: Probability of data loss per sample (0.01-0.2)
- `dropout_pattern`: 'random', 'burst' (consecutive losses)

**Model:**
```
y_dropout(t) = y_true(t) if rand() > p_drop else y_prev
```

**Severity Levels:**
- **Mild:** 1% dropout rate
- **Moderate:** 5% dropout rate
- **Severe:** 10-20% dropout rate

**Use Cases:**
- Wireless sensor packet loss
- Encoder skipped readings
- Communication failures

#### 1.4 Quantization

**Description:** Limited resolution due to finite bit-depth.

**Parameters:**
- `bit_depth`: Number of bits (8, 10, 12, 16)
- `range`: Measurement range for quantization

**Model:**
```
y_quant(t) = round(y_true(t) / q) * q
q = range / (2^bit_depth - 1)
```

**Severity Levels:**
- **Mild:** 16-bit (0.0015% resolution)
- **Moderate:** 12-bit (0.024% resolution)
- **Severe:** 8-bit (0.39% resolution)

**Use Cases:**
- Low-cost encoders
- ADC resolution limits
- Embedded system constraints

---

### 2. Actuator Faults

Faults affecting control command execution.

#### 2.1 Saturation

**Description:** Actuator cannot exceed physical limits.

**Parameters:**
- `limit_pct`: Percentage of nominal range (40%, 60%, 80%)
- `lower_limit`, `upper_limit`: Absolute bounds

**Model:**
```
u_sat(t) = clip(u_cmd(t), u_min, u_max)
```

**Severity Levels:**
- **Mild:** 80% of nominal range
- **Moderate:** 60% of nominal range
- **Severe:** 40% of nominal range

**Use Cases:**
- Motor torque limits
- Hydraulic pressure limits
- Power supply constraints

#### 2.2 Dead Zone

**Description:** Region where actuator is unresponsive.

**Parameters:**
- `dead_zone_width`: Width of unresponsive region
- `center`: Center point of dead zone

**Model:**
```
u_dz(t) = u_cmd(t) if |u_cmd(t)| > dz_width else 0
```

**Severity Levels:**
- **Mild:** 5% dead zone width
- **Moderate:** 10% dead zone width
- **Severe:** 20% dead zone width

**Use Cases:**
- Mechanical backlash
- Valve stiction
- Friction in gears

#### 2.3 Lag (Actuation Delay)

**Description:** First-order delay in actuator response.

**Parameters:**
- `time_constant`: Lag time constant (seconds)
- `delay_steps`: Discrete delay (timesteps)

**Model:**
```
tau * du_lag/dt + u_lag(t) = u_cmd(t)
```

**Severity Levels:**
- **Mild:** tau = 0.01s (1 timestep)
- **Moderate:** tau = 0.05s (5 timesteps)
- **Severe:** tau = 0.1s (10 timesteps)

**Use Cases:**
- Motor electrical dynamics
- Hydraulic response time
- Servo lag

#### 2.4 Jitter (High-Frequency Noise)

**Description:** Random high-frequency oscillations in actuation.

**Parameters:**
- `jitter_amplitude`: Peak-to-peak noise (% of command)
- `jitter_frequency`: Dominant frequency (Hz)

**Model:**
```
u_jitter(t) = u_cmd(t) + A * sin(2*pi*f*t + phi)
```

**Severity Levels:**
- **Mild:** 1% jitter amplitude
- **Moderate:** 5% jitter amplitude
- **Severe:** 10% jitter amplitude

**Use Cases:**
- PWM noise
- Electrical interference
- Mechanical vibration

---

### 3. Parameter Variations

Faults due to model uncertainty or parameter drift.

#### 3.1 Gain Errors

**Description:** Controller gains deviate from designed values.

**Parameters:**
- `gain_tolerance`: Percentage deviation (±5%, ±10%, ±20%)
- `affected_gains`: List of gain indices

**Model:**
```
K_actual = K_nominal * (1 + delta)
delta ~ U(-tolerance, +tolerance)
```

**Severity Levels:**
- **Mild:** ±5% gain variation
- **Moderate:** ±10% gain variation
- **Severe:** ±20% gain variation

**Use Cases:**
- Manufacturing tolerances
- Temperature effects
- Component aging

#### 3.2 System Uncertainty

**Description:** Physical parameters differ from nominal model.

**Parameters:**
- `mass_variation`: ±% of nominal mass
- `inertia_variation`: ±% of nominal inertia
- `friction_variation`: ±% of nominal friction

**Model:**
```
m_actual = m_nominal * (1 + delta_m)
J_actual = J_nominal * (1 + delta_J)
```

**Severity Levels:**
- **Mild:** ±5% physical parameter variation
- **Moderate:** ±10% physical parameter variation
- **Severe:** ±20% physical parameter variation

**Use Cases:**
- Load changes
- Wear and tear
- Environmental conditions

#### 3.3 Controller Parameter Drift

**Description:** Time-varying controller parameters.

**Parameters:**
- `drift_rate`: Change per unit time
- `drift_pattern`: 'linear', 'exponential', 'random_walk'

**Model:**
```
K(t) = K_0 + drift_rate * t
```

**Severity Levels:**
- **Mild:** 1% drift per 10s
- **Moderate:** 5% drift per 10s
- **Severe:** 10% drift per 10s

**Use Cases:**
- Adaptive controller transients
- Gain scheduling errors
- Memory corruption

---

### 4. Environmental Faults

External disturbances and model mismatch.

#### 4.1 Disturbances

**Description:** External forces acting on the system.

**Parameters:**
- `disturbance_type`: 'step', 'periodic', 'random', 'impulse'
- `disturbance_magnitude`: Force amplitude (N or Nm)
- `disturbance_frequency`: For periodic disturbances (Hz)

**Model:**
```
Step: d(t) = A * u_step(t - t_0)
Periodic: d(t) = A * sin(2*pi*f*t)
Random: d(t) = A * randn(t)
```

**Severity Levels:**
- **Mild:** 5% of nominal control effort
- **Moderate:** 10% of nominal control effort
- **Severe:** 20% of nominal control effort

**Use Cases:**
- Wind gusts
- Collision impacts
- Floor vibrations

#### 4.2 Model Mismatch

**Description:** Controller designed for simplified model, deployed on full model.

**Parameters:**
- `plant_model`: 'simplified', 'full', 'lowrank'
- `controller_model_basis`: Model used for controller design

**Severity Levels:**
- **Mild:** Simplified -> Full (minor nonlinearities)
- **Moderate:** Linearized -> Nonlinear
- **Severe:** Wrong model structure

**Use Cases:**
- Linearization errors
- Unmodeled dynamics
- Simplifying assumptions

---

## Injection Points

### 1. Sensor Outputs (Pre-Control)

**Location:** Between plant state and controller input

**Injection Types:**
- Noise, bias, dropout, quantization

**Implementation:**
```python
state_measured = sensor_fault_injector(state_true)
control_output = controller.compute_control(state_measured)
```

**Rationale:** Tests controller's ability to handle noisy/corrupted measurements.

---

### 2. Actuator Commands (Post-Control)

**Location:** Between controller output and plant input

**Injection Types:**
- Saturation, dead zone, lag, jitter

**Implementation:**
```python
control_commanded = controller.compute_control(state)
control_actual = actuator_fault_injector(control_commanded)
state_next = plant.step(control_actual)
```

**Rationale:** Tests controller's robustness to actuation limitations.

---

### 3. Plant Parameters

**Location:** System dynamics equations

**Injection Types:**
- Mass/inertia variations, friction changes

**Implementation:**
```python
plant_params = inject_parameter_variations(nominal_params)
plant = DynamicsModel(plant_params)
```

**Rationale:** Tests controller's robustness to model uncertainty.

---

### 4. Controller Gains

**Location:** Controller initialization or online

**Injection Types:**
- Gain errors, drift

**Implementation:**
```python
gains_actual = inject_gain_errors(gains_nominal)
controller = ControllerFactory.create(gains=gains_actual)
```

**Rationale:** Tests sensitivity to controller parameter errors.

---

### 5. Initial Conditions

**Location:** Simulation start state

**Injection Types:**
- Perturbed initial angles/velocities

**Implementation:**
```python
initial_state = nominal_state + perturbation
```

**Rationale:** Tests basin of attraction and transient response.

---

## Configuration Format

### YAML Schema

```yaml
# Fault Injection Scenario Configuration
scenario:
  name: "sensor_noise_actuator_saturation"
  description: "Combined sensor noise and actuator limits"
  seed: 42  # For reproducibility

  # Sensor faults
  sensor_faults:
    - type: "gaussian_noise"
      target: "all_states"  # or specific: ["theta1", "theta2"]
      snr_db: 30
      enabled: true

    - type: "bias"
      target: ["theta1_dot", "theta2_dot"]
      bias_magnitude: 0.05  # 5% of typical velocity
      enabled: true

    - type: "dropout"
      target: "encoder_theta1"
      dropout_rate: 0.05
      dropout_pattern: "random"
      enabled: false

  # Actuator faults
  actuator_faults:
    - type: "saturation"
      limit_pct: 80
      enabled: true

    - type: "lag"
      time_constant: 0.02  # 20ms delay
      enabled: true

    - type: "dead_zone"
      dead_zone_width: 0.1  # 10% of control range
      enabled: false

  # Parameter variations
  parameter_variations:
    - type: "gain_error"
      affected_gains: [0, 1, 2, 3, 4, 5]  # All gains
      tolerance_pct: 10
      distribution: "uniform"
      enabled: true

    - type: "system_uncertainty"
      mass_cart_variation: 0.1  # ±10%
      mass_pole1_variation: 0.1
      mass_pole2_variation: 0.1
      inertia_pole1_variation: 0.15
      inertia_pole2_variation: 0.15
      enabled: false

  # Environmental disturbances
  disturbances:
    - type: "periodic"
      magnitude: 0.5  # 0.5 Nm
      frequency: 2.0  # 2 Hz
      phase: 0.0
      start_time: 1.0
      end_time: 5.0
      enabled: false

  # Expected behavior (for validation)
  expected_behavior:
    settling_time_max: 3.0  # seconds
    overshoot_max: 20.0  # percent
    steady_state_error_max: 0.05  # radians
    stability_required: true

# Multiple scenarios can be defined
scenarios:
  - name: "baseline"
    sensor_faults: []
    actuator_faults: []
    parameter_variations: []
    disturbances: []

  - name: "mild_stress"
    sensor_faults:
      - {type: "gaussian_noise", snr_db: 50}
    actuator_faults:
      - {type: "saturation", limit_pct: 80}

  - name: "severe_stress"
    sensor_faults:
      - {type: "gaussian_noise", snr_db: 10}
      - {type: "bias", bias_magnitude: 0.1}
    actuator_faults:
      - {type: "saturation", limit_pct: 40}
      - {type: "lag", time_constant: 0.1}
    parameter_variations:
      - {type: "gain_error", tolerance_pct: 20}
```

---

## Expected vs Observed Behavior Models

### Baseline (Expected Behavior)

Run controller without faults to establish performance baseline:

**Metrics:**
- Settling time: T_s (time to reach ±2% of target)
- Overshoot: OS (peak deviation from target, %)
- Energy consumption: E (integral of control effort squared)
- Stability: Binary (converged vs diverged)

**Example Baseline:**
```
Classical SMC (no faults):
  Settling time: 1.8s
  Overshoot: 12%
  Energy: 45 J
  Stability: YES
```

---

### Faulty Behavior (Observed)

Run same controller with injected faults:

**Metrics (same as baseline):**
- Settling time: T_s_fault
- Overshoot: OS_fault
- Energy: E_fault
- Stability: Binary

**Example Faulty:**
```
Classical SMC (SNR=30dB, Sat=80%):
  Settling time: 2.5s
  Overshoot: 18%
  Energy: 62 J
  Stability: YES
```

---

### Degradation Analysis

Compute performance degradation:

```
Delta_settling = (T_s_fault - T_s_baseline) / T_s_baseline * 100%
Delta_overshoot = (OS_fault - OS_baseline) / OS_baseline * 100%
Delta_energy = (E_fault - E_baseline) / E_baseline * 100%
Stability_maintained = (Stable_fault == Stable_baseline)
```

**Example:**
```
Delta_settling = (2.5 - 1.8) / 1.8 * 100% = +38.9%
Delta_overshoot = (18 - 12) / 12 * 100% = +50%
Delta_energy = (62 - 45) / 45 * 100% = +37.8%
Stability_maintained = YES
```

**Acceptance Criteria:**
- Delta_settling < 50% (acceptable degradation)
- Delta_overshoot < 100% (no excessive oscillation)
- Stability_maintained = YES (critical)

---

## Robustness Metrics

### 1. Degradation Score

**Definition:** Normalized measure of performance degradation.

**Formula:**
```
Degradation_Score = (
    w1 * Delta_settling +
    w2 * Delta_overshoot +
    w3 * Delta_energy
) / (w1 + w2 + w3)

Default weights: w1=0.4, w2=0.4, w3=0.2
```

**Interpretation:**
- 0-20%: Excellent robustness
- 20-50%: Good robustness
- 50-100%: Moderate robustness
- >100%: Poor robustness (performance doubled)

---

### 2. Robustness Index (RI)

**Definition:** Inverse of degradation, normalized to [0, 1].

**Formula:**
```
RI = 1 / (1 + Degradation_Score / 100)
```

**Interpretation:**
- RI > 0.8: Highly robust
- 0.6 < RI <= 0.8: Robust
- 0.4 < RI <= 0.6: Moderately robust
- RI <= 0.4: Fragile

---

### 3. Stability Margin

**Definition:** Severity of fault at which controller loses stability.

**Measurement:**
- Start with mild fault (SNR=50dB)
- Incrementally increase severity (SNR=40, 30, 20, 10, 5)
- Record fault level at which stability is lost

**Example:**
```
Classical SMC: Loses stability at SNR = 8dB
Adaptive SMC: Loses stability at SNR = 5dB
=> Adaptive SMC has better stability margin
```

---

### 4. Consistency Score

**Definition:** Variance in performance across multiple fault scenarios.

**Formula:**
```
Consistency = 1 - std(Degradation_Scores) / mean(Degradation_Scores)
```

**Interpretation:**
- Consistency > 0.8: Very consistent (predictable)
- 0.6 < Consistency <= 0.8: Consistent
- Consistency <= 0.6: Inconsistent (scenario-dependent)

---

### 5. Overall Robustness Rank

Aggregate ranking across all metrics:

**Formula:**
```
Overall_Rank = 0.3 * RI + 0.3 * Stability_Margin + 0.2 * Consistency + 0.2 * Energy_Efficiency
```

**Output:** Ranking of 7 controllers from most robust (1) to least robust (7).

---

## Implementation Architecture

### Class Hierarchy

```
FaultInjector (Abstract Base)
├── SensorFaultInjector
│   ├── GaussianNoiseFault
│   ├── BiasFault
│   ├── DropoutFault
│   └── QuantizationFault
├── ActuatorFaultInjector
│   ├── SaturationFault
│   ├── DeadZoneFault
│   ├── LagFault
│   └── JitterFault
├── ParametricFaultInjector
│   ├── GainErrorFault
│   ├── SystemUncertaintyFault
│   └── DriftFault
└── EnvironmentalFaultInjector
    ├── DisturbanceFault
    └── ModelMismatchFault

FaultScenario
├── add_fault(fault_injector)
├── run_simulation(controller, plant, initial_state)
└── compute_metrics(baseline_metrics)

RobustnessAnalyzer
├── compare_controllers(results_dict)
├── rank_controllers(metric='overall')
└── generate_report(output_format='html')
```

---

## Usage Examples

### Example 1: Single Fault Injection

```python
from src.utils.fault_injection import GaussianNoiseFault, FaultScenario

# Create fault
noise_fault = GaussianNoiseFault(snr_db=30, target='all_states')

# Create scenario
scenario = FaultScenario(name="sensor_noise_test")
scenario.add_sensor_fault(noise_fault)

# Run simulation
results = scenario.run_simulation(
    controller=classical_smc,
    plant=dynamics,
    initial_state=initial_conditions,
    duration=10.0
)

# Analyze
print(f"Settling time: {results.settling_time:.2f}s")
print(f"Degradation: {results.degradation_pct:.1f}%")
```

---

### Example 2: Combined Faults

```python
scenario = FaultScenario(name="combined_stress")
scenario.add_sensor_fault(GaussianNoiseFault(snr_db=30))
scenario.add_actuator_fault(SaturationFault(limit_pct=80))
scenario.add_parameter_variation(GainErrorFault(tolerance_pct=10))

results = scenario.run_simulation(...)
```

---

### Example 3: Robustness Comparison

```python
from src.utils.fault_injection import RobustnessAnalyzer

# Test all 7 controllers
controllers = [classical_smc, sta_smc, adaptive_smc, ...]
results = {}

for ctrl in controllers:
    results[ctrl.name] = scenario.run_simulation(ctrl, plant, ...)

# Analyze and rank
analyzer = RobustnessAnalyzer()
rankings = analyzer.rank_controllers(results, metric='overall')

print("Robustness Ranking (1=best, 7=worst):")
for rank, (ctrl_name, score) in enumerate(rankings, start=1):
    print(f"{rank}. {ctrl_name}: {score:.2f}")
```

---

## Validation Strategy

### 1. Unit Tests

Test each fault type independently:

```python
def test_gaussian_noise_snr():
    """Verify SNR calculation is accurate."""
    signal = np.ones(1000)  # 1.0 RMS
    noisy = inject_gaussian_noise(signal, snr_db=20)

    noise = noisy - signal
    actual_snr = 20 * np.log10(np.std(signal) / np.std(noise))

    assert abs(actual_snr - 20) < 1.0  # Within 1 dB tolerance
```

---

### 2. Integration Tests

Test with real controllers:

```python
def test_classical_smc_robustness_sensor_noise():
    """Classical SMC should handle 30dB noise."""
    scenario = FaultScenario(name="noise_30db")
    scenario.add_sensor_fault(GaussianNoiseFault(snr_db=30))

    results = scenario.run_simulation(classical_smc, ...)

    assert results.stability == True
    assert results.degradation_pct < 50
```

---

### 3. Comparative Validation

Cross-check with literature:

- SMC chattering reduction under noise (expected)
- Adaptive SMC better with parameter uncertainty (expected)
- STA robustness to disturbances (expected from theory)

---

### 4. Sensitivity Analysis

Verify fault severity levels:

```python
snr_levels = [50, 40, 30, 20, 10, 5]
degradations = []

for snr in snr_levels:
    scenario.add_sensor_fault(GaussianNoiseFault(snr_db=snr))
    results = scenario.run_simulation(...)
    degradations.append(results.degradation_pct)

# Expect monotonic increase in degradation
assert all(degradations[i] <= degradations[i+1] for i in range(len(degradations)-1))
```

---

## Summary

This framework enables systematic robustness validation of all 7 controllers under 4 fault categories (sensor, actuator, parametric, environmental) at 5 severity levels, yielding 140 test cases total.

**Key Benefits:**

1. **Realism:** Fault models match real-world conditions
2. **Comprehensive:** 140 test cases cover wide fault space
3. **Quantitative:** Degradation metrics enable objective comparison
4. **Reproducible:** Seeded randomness ensures repeatability
5. **Configurable:** YAML-based scenarios for easy experimentation

**Next Steps:**

- Task 1.3.2: Implement fault injection library
- Task 1.3.3: Create robustness tests for all 7 controllers
- Task 1.3.4: Add realistic sensor models
- Task 1.3.5: Generate comparative analysis reports

---

**Document Length:** 12 pages
**Lines of Documentation:** ~850 lines
**Coverage:** Complete fault taxonomy, injection architecture, metrics, and validation strategy
