# Tutorial 02: Controller Comparison & Selection **Level:** Intermediate

**Duration:** 45-60 minutes
**Prerequisites:**
- Completed [Tutorial 01: Your First Simulation](tutorial-01-first-simulation.md)
- Basic understanding of SMC concepts from Getting Started Guide ## Learning Objectives By the end of this tutorial, you will: - [ ] Understand the differences between the 4 core SMC controller types
- [ ] Run comparative simulations and analyze performance tradeoffs
- [ ] Interpret controller-specific metrics (chattering, adaptation, convergence)
- [ ] Select the appropriate controller for specific application requirements
- [ ] Configure controller-specific parameters for optimal performance
- [ ] Understand when to use Classical, Super-Twisting, Adaptive, or Hybrid SMC

---

## Overview: The 4 Core SMC Controllers This framework provides **4 production-ready SMC variants**, each designed for specific control challenges: | Controller | Primary Strength | Best For | Computational Cost |

|------------|------------------|----------|-------------------|
| **Classical SMC** | Simplicity & robustness | Known systems, prototyping | Low |
| **Super-Twisting SMC** | Chattering reduction | High-frequency actuators, smooth control | Medium |
| **Adaptive SMC** | Uncertainty handling | Unknown/varying parameters | Medium-High |
| **Hybrid Adaptive STA** | Best of both worlds | High-performance applications | High | ### Controller Evolution ```
Classical SMC (1970s) ↓ ├─→ Super-Twisting SMC (1990s) ← Addresses chattering ├─→ Adaptive SMC (1980s) ← Addresses uncertainty └─→ Hybrid Adaptive STA (2000s) ← Combines both
``` > **📚 Theory Deep Dive:** For mathematical foundations of these controllers, see:
> - [SMC Theory Guide](../theory/smc-theory.md) - Lyapunov stability, chattering analysis, super-twisting mathematics

---

## Part 1: Controller Characteristics ### 1.1 Classical SMC **Core Principle:** Drive system to sliding surface, then maintain sliding mode **Control Law:**
```

s = k₁·θ₁ + k₂·dθ₁ + λ₁·θ₂ + λ₂·dθ₂ (sliding surface)
u = -K·tanh(s/ε) (control input)
``` **6 Tunable Gains:**
- `k₁, k₂`: First pendulum surface gains
- `λ₁, λ₂`: Second pendulum surface gains
- `K`: Switching gain (robustness)
- `ε`: Boundary layer thickness (chattering reduction) **Strengths:**
✅ Simple to understand and implement
✅ Robust to matched disturbances
✅ Fast response to large errors
✅ Minimal computational overhead **Limitations:**
❌ Chattering (high-frequency oscillations)
❌ Requires accurate model for best performance
❌ Fixed gains may be conservative **Typical Performance (from reference tuning):**
```yaml

Settling Time: 3.2 seconds
Peak Overshoot: 8.5%
ISE: 0.45
Chattering: Moderate (boundary layer dependent)
```

---

### 1.2 Super-Twisting SMC (STA-SMC) **Core Principle:** 2nd-order sliding mode for continuous control without chattering **Control Law:**
```

s = k₁·θ₁ + k₂·dθ₁ + λ₁·θ₂ + λ₂·dθ₂
u = -α·|s|^(1/2)·sign(s) - ∫β·sign(s) dt
``` **6 Tunable Gains:**
- `k₁, k₂, λ₁, λ₂`: Sliding surface (same as classical)
- `α`: First-order super-twisting gain
- `β`: Second-order super-twisting gain **Strengths:**
✅ **Continuous control** (no discontinuous switching)
✅ **Chattering-free** by design
✅ **Finite-time convergence** (faster than asymptotic)
✅ Robust to Lipschitz-continuous disturbances **Limitations:**
❌ More complex gain tuning (α, β must satisfy stability conditions)
❌ Requires relative degree 1 (satisfied for DIP)
❌ Higher computational cost than classical **Typical Performance:**
```yaml

Settling Time: 2.8 seconds (15% faster than classical)
Peak Overshoot: 5.2% (40% reduction)
ISE: 0.32 (30% improvement)
Chattering: Minimal (continuous control)
```

---

### 1.3 Adaptive SMC **Core Principle:** Online gain adaptation to handle model uncertainty **Control Law:**
```

s = k₁·θ₁ + k₂·dθ₁ + λ₁·θ₂ + λ₂·dθ₂
K_adaptive(t) = K₀ + ∫γ·|s| dt (adaptation law)
u = -K_adaptive(t)·tanh(s/ε)
``` **5 Tunable Gains:**
- `k₁, k₂, λ₁, λ₂`: Sliding surface
- `γ`: Adaptation rate (higher = faster but less stable) **Strengths:**
✅ **Handles parameter uncertainty** (mass variations, friction changes)
✅ **Self-tuning** gains reduce conservatism
✅ **Improved efficiency** (lower control effort after adaptation)
✅ Lyapunov-stable adaptation law **Limitations:**
❌ Transient phase during adaptation (~2-3 seconds)
❌ Risk of parameter drift without leakage term
❌ Sensitive to noise (can cause false adaptation) **Typical Performance:**
```yaml

Settling Time: 3.5 seconds (includes adaptation phase)
Peak Overshoot: 6.8%
ISE (steady): 0.28 (38% better after adaptation)
Adaptation: Converges in ~2.5 seconds
Chattering: Low (adaptive gains reduce conservatism)
```

---

### 1.4 Hybrid Adaptive STA-SMC **Core Principle:** Combines super-twisting continuity + adaptive uncertainty handling **Control Law:**
```

s = k₁·θ₁ + k₂·dθ₁ + λ₁·θ₂ + λ₂·dθ₂
α_adaptive(t) = α₀ + ∫γ_α·|s| dt
β_adaptive(t) = β₀ + ∫γ_β·|s| dt
u = -α_adaptive·|s|^(1/2)·sign(s) - ∫β_adaptive·sign(s) dt
``` **4 Base Gains + Adaptation:**
- `k₁, k₂, λ₁, λ₂`: Sliding surface
- `α₀, β₀`: Initial super-twisting gains (auto-computed or manual)
- `γ_α, γ_β`: Adaptation rates (configured, not tuned) **Strengths:**
✅ **Best overall performance** (combines all advantages)
✅ Chattering-free + uncertainty handling
✅ Fast finite-time convergence
✅ Optimal for high-performance applications **Limitations:**
❌ **Highest computational cost** (~30% more than classical)
❌ Most complex to tune (4-8 parameters depending on mode)
❌ Requires careful initialization to avoid transient instability **Typical Performance:**
```yaml

Settling Time: 2.3 seconds (best of all controllers)
Peak Overshoot: 3.9% (lowest)
ISE: 0.25 (45% better than classical)
Adaptation: Converges in ~2.0 seconds
Chattering: None (continuous + adaptive)
```

---

### Controller Comparison #### Performance Comparison Table | Characteristic | Classical SMC | Super-Twisting | Adaptive SMC | Hybrid STA |
|----------------|---------------|----------------|--------------|------------|
| **Control Continuity** | Smoothed (tanh) | Continuous | Smoothed (tanh) | Continuous |
| **Chattering Level** | Moderate | Minimal | Low | None |
| **Settling Time** | 3.2 s | 2.8 s (↓13%) | 3.5 s | 2.3 s (↓28%) |
| **Peak Overshoot** | 8.5% | 5.2% (↓39%) | 6.8% | 3.9% (↓54%) |
| **ISE (Tracking Error)** | 0.45 | 0.32 (↓29%) | 0.28 (↓38%) | 0.25 (↓44%) |
| **Adaptation Phase** | None | None | 2.5 s | 2.0 s |
| **Computational Cost** | Low (baseline) | Medium (+15%) | Medium-High (+20%) | High (+30%) |
| **Number of Gains** | 6 | 6 | 5 | 4 base + adaptation |
| **Tuning Difficulty** | Easy | Medium | Medium | Hard |
| **Parameter Uncertainty** | Fixed gains | Fixed gains | Handles well | Handles best |
| **Robustness** | Good | Very Good | | |
| **Memory Usage** | Low | Low | Medium | Medium-High |
| **Real-Time Suitability** | | Very Good | Good | Good | **Percentage Improvements** (vs Classical SMC):
- **Super-Twisting**: 13% faster settling, 39% less overshoot, 29% lower tracking error
- **Adaptive**: 38% lower steady-state error, self-tuning capability
- **Hybrid**: 28% faster settling, 54% less overshoot, 44% lower error, best overall #### Use Case Matrix | Application Requirement | Recommended Controller | Rationale |
|-------------------------|------------------------|-----------|
| **Rapid prototyping** | Classical SMC | Simple, well-understood, fast tuning |
| **Smooth actuator control** | Super-Twisting or Hybrid | Continuous control, no chattering |
| **Unknown system parameters** | Adaptive or Hybrid | Online gain adaptation |
| **High-performance control** | Hybrid Adaptive STA | Best overall metrics |
| **Low computational resources** | Classical SMC | Minimal CPU/memory overhead |
| **Noise-sensitive environments** | Super-Twisting | Continuous control reduces high-frequency content |
| **Time-varying parameters** | Adaptive or Hybrid | Self-tuning compensates for changes |
| **Research/publication** | Hybrid Adaptive STA | performance (see references) |
| **Industrial deployment** | Super-Twisting | Good balance of performance and complexity |
| **Educational purposes** | Classical SMC | Clear mathematical structure | #### Controller Selection Flowchart ```mermaid
flowchart TD START["🎯 Select SMC Controller"] --> Q1{Is smooth<br/>control required?} Q1 -->|Yes| Q2{Parameter<br/>uncertainty<br/>present?} Q1 -->|No| Q3{Parameter<br/>uncertainty<br/>present?} Q2 -->|Yes| HYBRID["✅ Hybrid Adaptive STA-SMC<br/>🎯 Best overall performance<br/>⚡ Continuous + adaptive<br/>⏱️ Fastest settling<br/>💰 High computational cost"] Q2 -->|No| STA["✅ Super-Twisting SMC<br/>🎯 Chattering-free<br/>⚡ Continuous control<br/>⏱️ Fast convergence<br/>💰 Medium computational cost"] Q3 -->|Yes| ADAPTIVE["✅ Adaptive SMC<br/>🎯 Handles uncertainty<br/>⚡ Self-tuning gains<br/>⏱️ Includes adaptation phase<br/>💰 Medium computational cost"] Q3 -->|No| Q4{Performance<br/>priority?} Q4 -->|High| STA Q4 -->|Moderate| CLASSICAL["✅ Classical SMC<br/>🎯 Simple and robust<br/>⚡ Well-understood<br/>⏱️ Good performance<br/>💰 Low computational cost"] style START fill:#ccccff style CLASSICAL fill:#ccffcc style STA fill:#ffffcc style ADAPTIVE fill:#ffcccc style HYBRID fill:#ccccff
``` **Decision Tree Guidance**: 1. **Start with smooth control requirement**: - Chattering-sensitive applications → Continuous controllers (STA or Hybrid) - Chattering acceptable → Classical or Adaptive 2. **Consider parameter uncertainty**: - High uncertainty → Adaptive controllers (Adaptive or Hybrid) - Well-known system → Fixed-gain controllers (Classical or STA) 3. **Performance vs complexity tradeoff**: - **Best performance**: Hybrid Adaptive STA (highest complexity) - **Best balance**: Super-Twisting (moderate complexity) - **Simplicity priority**: Classical SMC (lowest complexity) **Quick Recommendations**:

- **Not sure?** Start with **Classical SMC** for rapid prototyping
- **Production system?** Use **Super-Twisting** for reliability
- **Research project?** Deploy **Hybrid STA** for best results
- **Uncertain parameters?** Choose **Adaptive** or **Hybrid**

---

## Part 2: Hands-On Comparison ### 2.1 Run All Four Controllers simulate all controllers with the same initial conditions for direct comparison: ```bash

# Classical SMC

python simulate.py --ctrl classical_smc --plot --save results_classical.json # Super-Twisting SMC
python simulate.py --ctrl sta_smc --plot --save results_sta.json # Adaptive SMC
python simulate.py --ctrl adaptive_smc --plot --save results_adaptive.json # Hybrid Adaptive STA-SMC
python simulate.py --ctrl hybrid_adaptive_sta_smc --plot --save results_hybrid.json
``` **Expected Execution Time:** ~20 seconds for all 4 simulations

---

## 2.2 Visual Comparison After running all simulations, you should see 4 separate plots. Here's what to look for: #### **State Trajectories** | Metric | Classical | Super-Twisting | Adaptive | Hybrid |
|--------|-----------|----------------|----------|--------|
| θ₁ settling | 3.2s | 2.8s | 3.5s | 2.3s |
| θ₂ settling | 3.5s | 3.0s | 3.8s | 2.5s |
| Oscillations | Moderate | Minimal | Low | Minimal | **Observation Pattern:**
- **Classical:** Fast initial response, some overshoot, moderate oscillations
- **Super-Twisting:** Smooth convergence, minimal overshoot, no high-frequency oscillations
- **Adaptive:** Slower initial response, improves over time as gains adapt
- **Hybrid:** Fastest convergence, smoothest trajectory, best overall #### **Control Signals** | Metric | Classical | Super-Twisting | Adaptive | Hybrid |
|--------|-----------|----------------|----------|--------|
| Chattering | Moderate | **None** | Low | **None** |
| Peak force | 95 N | 88 N | 92 N → 75 N | 82 N |
| Smoothness | Acceptable | **Excellent** | Good | **Excellent** | **Key Insight:** Super-twisting and hybrid controllers produce **continuous control signals** without the high-frequency switching seen in classical SMC.

---

### 2.3 Performance Metrics Comparison Load and compare the saved results: ```python
import json
import numpy as np # Load all results
results = { 'classical': json.load(open('results_classical.json')), 'sta': json.load(open('results_sta.json')), 'adaptive': json.load(open('results_adaptive.json')), 'hybrid': json.load(open('results_hybrid.json'))
} # Compare key metrics
for name, data in results.items(): print(f"\n{name.upper()} SMC:") print(f" ISE: {data['metrics']['ise']:.4f}") print(f" ITAE: {data['metrics']['itae']:.4f}") print(f" Settling Time: {data['metrics']['settling_time']:.2f} s") print(f" Peak Overshoot: {data['metrics']['overshoot']:.2f}%") print(f" Control Effort: {data['metrics']['control_effort']:.2f}")
``` **Expected Output:**

```
CLASSICAL SMC: ISE: 0.4523 ITAE: 1.2341 Settling Time: 3.18 s Peak Overshoot: 8.47% Control Effort: 145.32 STA SMC: ISE: 0.3187 ITAE: 0.9856 Settling Time: 2.79 s Peak Overshoot: 5.21% Control Effort: 128.94 ADAPTIVE SMC: ISE: 0.2834 ITAE: 1.0521 Settling Time: 3.52 s Peak Overshoot: 6.83% Control Effort: 118.67 HYBRID SMC: ISE: 0.2512 ITAE: 0.8234 Settling Time: 2.31 s Peak Overshoot: 3.92% Control Effort: 110.45
```

---

## 2.4 Chattering Analysis **What is Chattering?**

High-frequency oscillations in the control signal caused by imperfect sliding mode realization (discontinuous switching + finite sampling time). **Measure Chattering:**
```python
def compute_chattering_index(u, dt): """Chattering index = average absolute derivative of control signal.""" du_dt = np.diff(u) / dt return np.mean(np.abs(du_dt)) # Compare chattering across controllers
for name, data in results.items(): u = np.array(data['control']) chattering = compute_chattering_index(u, dt=0.01) print(f"{name:15s} chattering index: {chattering:.2f} N/s")
``` **Expected Output:**

```
classical chattering index: 852.34 N/s (high)
sta chattering index: 12.45 N/s (97% reduction!)
adaptive chattering index: 234.56 N/s (moderate)
hybrid chattering index: 8.92 N/s (99% reduction!)
``` **Interpretation:**

- **Classical:** Moderate chattering despite boundary layer (ε=0.01)
- **Super-Twisting:** Near-continuous control (2nd-order sliding mode)
- **Adaptive:** Reduced chattering due to adaptive gain optimization
- **Hybrid:** Best chattering reduction (continuous + adaptive)

---

## Part 3: Controller Selection Framework ### 3.1 Decision Tree Use this flowchart to select the appropriate controller: ```

START │ ├─→ Is chattering a critical concern? (high-freq actuators, sensitive equipment) │ │ │ YES → Is system well-modeled? (known parameters, minimal uncertainty) │ │ │ │ │ YES → USE: Super-Twisting SMC │ │ │ │ │ NO → USE: Hybrid Adaptive STA-SMC │ │ │ NO → Is parameter uncertainty significant? (>20% mass variation, unknown friction) │ │ │ YES → Is computational cost a constraint? (embedded system, <100 Hz control) │ │ │ │ │ YES → USE: Adaptive SMC │ │ │ │ │ NO → USE: Hybrid Adaptive STA-SMC │ │ │ NO → Is simplicity/prototyping the priority? │ │ │ YES → USE: Classical SMC │ │ │ NO → USE: Super-Twisting SMC
```

---

### 3.2 Application-Specific Recommendations #### **Research & Benchmarking**
- **Use:** All 4 controllers for analysis
- **Rationale:** Establish baseline (classical) → evaluate improvements (STA, adaptive, hybrid)
- **Configuration:** Identical initial conditions, same performance metrics #### **Industrial Robotics (High-Frequency Actuators)**
- **Use:** Super-Twisting SMC or Hybrid Adaptive STA-SMC
- **Rationale:** Chattering can damage actuators or cause audible noise
- **Configuration:** Conservative gains with safety margins #### **Aerospace/Automotive (Model Uncertainty)**
- **Use:** Adaptive SMC or Hybrid Adaptive STA-SMC
- **Rationale:** Parameter variations (payload, fuel, wear) require adaptation
- **Configuration:** Moderate adaptation rates with parameter bounds #### **Embedded Systems (Limited Computation)**
- **Use:** Classical SMC or Adaptive SMC
- **Rationale:** Lower computational overhead (<100 µs control loop)
- **Configuration:** Optimized gains via PSO for efficiency #### **High-Performance Control (Best Results)**
- **Use:** Hybrid Adaptive STA-SMC
- **Rationale:** Combines all advantages (chattering-free + adaptive + fast)
- **Configuration:** Careful tuning with PSO, monitor adaptation

---

## Part 4: Controller-Specific Configuration ### 4.1 Classical SMC Tuning **Key Parameters:**
```yaml
# config.yaml - controllers.classical_smc

controllers: classical_smc: gains: [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] # [k1, k2, λ1, λ2, K, ε] max_force: 100.0 boundary_layer: 0.01 # Critical for chattering reduction
``` **Tuning Guidelines:**
1. **Surface Gains (k₁, k₂, λ₁, λ₂):** Higher = faster convergence, more aggressive
2. **Switching Gain (K):** Must overcome maximum disturbance + margin
3. **Boundary Layer (ε):** Trade-off between chattering and precision - Small ε (0.001-0.01): Low chattering, precise tracking - Large ε (0.1-1.0): More chattering, wider boundary **Common Issues:**
- **Chattering too high:** Increase `boundary_layer` to 0.05-0.1
- **Slow convergence:** Increase surface gains by 20-50%
- **Overshooting:** Reduce switching gain `K` by 20-30%

---

## 4.2 Super-Twisting SMC Tuning **Key Parameters:**
```yaml
# config.yaml - controllers.sta_smc

controllers: sta_smc: gains: [25.0, 10.0, 15.0, 12.0, 20.0, 15.0] # [k1, k2, λ1, λ2, α, β] max_force: 100.0
``` **Tuning Guidelines:**
1. **Surface Gains (k₁, k₂, λ₁, λ₂):** Same as classical SMC
2. **Super-Twisting Gains (α, β):** Must satisfy stability condition ``` α > L_max (Lipschitz constant of disturbance) β > (5·L_max²) / (4·α) ``` **Stability Condition Check:**
```python
# Example verification

alpha = 20.0
beta = 15.0
L_max = 10.0 # Estimated maximum disturbance gradient assert alpha > L_max, "α must exceed disturbance Lipschitz constant"
assert beta > (5 * L_max**2) / (4 * alpha), "β violates stability condition"
``` **Common Issues:**
- **Oscillations persist:** Increase α (try +50%)
- **Slow convergence:** Increase β proportionally (β/α² ratio)
- **Instability:** Verify α, β stability conditions

---

## 4.3 Adaptive SMC Tuning **Key Parameters:**
```yaml
# config.yaml - controllers.adaptive_smc

controllers: adaptive_smc: gains: [10.0, 8.0, 15.0, 12.0, 0.5] # [k1, k2, λ1, λ2, γ] max_force: 100.0 initial_gain: 10.0 # K₀ starting value adaptation_rate: 0.5 # γ (higher = faster adaptation) leak_rate: 0.01 # Prevents parameter drift
``` **Tuning Guidelines:**
1. **Adaptation Rate (γ):** Trade-off between speed and stability - Low γ (0.1-0.5): Slow, stable adaptation - High γ (1.0-5.0): Fast, potentially oscillatory
2. **Leak Rate:** Prevents unbounded growth (typically 0.01-0.1)
3. **Initial Gain (K₀):** Conservative estimate of required control **Monitoring Adaptation:**
```python
# Track adaptive gain evolution

adapted_gains = data['state_vars']['adaptive_gain']
import matplotlib.pyplot as plt plt.plot(data['time'], adapted_gains)
plt.xlabel('Time (s)')
plt.ylabel('Adaptive Gain K(t)')
plt.title('Gain Adaptation Trajectory')
plt.grid()
plt.show()
``` **Common Issues:**
- **Parameter drift:** Increase `leak_rate` to 0.05-0.1
- **Slow adaptation:** Increase `adaptation_rate` by 2x
- **Noisy adaptation:** Reduce `adaptation_rate` by 50%, add filtering

---

## 4.4 Hybrid Adaptive STA-SMC Tuning **Key Parameters:**
```yaml
# config.yaml - controllers.hybrid_adaptive_sta_smc

controllers: hybrid_adaptive_sta_smc: gains: [15.0, 12.0, 18.0, 15.0] # [k1, k2, λ1, λ2] only max_force: 100.0 initial_alpha: 20.0 # α₀ (auto-computed if omitted) initial_beta: 15.0 # β₀ (auto-computed if omitted) adaptation_alpha: 0.3 # γ_α adaptation_beta: 0.2 # γ_β
``` **Tuning Guidelines:**
1. **Surface Gains:** Same as classical/STA
2. **Auto-Computation:** If `initial_alpha` omitted, uses model-based formula
3. **Adaptation Rates:** Typically 50-70% of adaptive SMC rates (more conservative) **Advanced: Auto-Tuning Mode**
```yaml
# Let controller auto-compute α₀, β₀ from model

controllers: hybrid_adaptive_sta_smc: gains: [15.0, 12.0, 18.0, 15.0] # Omit initial_alpha, initial_beta for auto-computation
``` **Common Issues:**
- **Transient instability:** Reduce adaptation rates by 50%
- **Slow initial response:** Manually set `initial_alpha` = 25-30
- **Complex tuning:** Use PSO optimization (recommended)

---

## Part 5: Practical Experiments ### Experiment 1: Chattering Sensitivity **Objective:** Quantify chattering reduction across controllers ```bash
# Run classical SMC with different boundary layers
python simulate.py --ctrl classical_smc --override "boundary_layer=0.001" --save bl_0.001.json
python simulate.py --ctrl classical_smc --override "boundary_layer=0.01" --save bl_0.01.json
python simulate.py --ctrl classical_smc --override "boundary_layer=0.1" --save bl_0.1.json # Compare with STA-SMC (inherently chattering-free)
python simulate.py --ctrl sta_smc --save sta_baseline.json
``` **Analysis:**

```python
# example-metadata:
# runnable: false boundary_layers = [0.001, 0.01, 0.1]
chattering_indices = [] for bl in boundary_layers: data = json.load(open(f'bl_{bl}.json')) u = np.array(data['control']) chattering = compute_chattering_index(u, dt=0.01) chattering_indices.append(chattering) # Plot results
plt.plot(boundary_layers, chattering_indices, 'o-', label='Classical SMC')
plt.axhline(sta_chattering, color='red', linestyle='--', label='STA-SMC')
plt.xlabel('Boundary Layer ε')
plt.ylabel('Chattering Index (N/s)')
plt.xscale('log')
plt.legend()
plt.grid()
plt.show()
```

---

## Experiment 2: Robustness to Parameter Uncertainty **Objective:** Test adaptive controllers under mass variations ```bash

# Baseline: nominal mass

python simulate.py --ctrl adaptive_smc --save nominal_mass.json # Perturbed: +30% cart mass
python simulate.py --ctrl adaptive_smc --override "dip_params.m0=1.3" --save high_mass.json # Perturbed: -20% cart mass
python simulate.py --ctrl adaptive_smc --override "dip_params.m0=0.8" --save low_mass.json # Compare with classical SMC (non-adaptive)
python simulate.py --ctrl classical_smc --override "dip_params.m0=1.3" --save classical_high_mass.json
``` **Analysis:**
- **Adaptive SMC:** Should maintain similar performance across mass variations
- **Classical SMC:** Performance degrades with parameter mismatch

---

## Experiment 3: Convergence Speed Comparison **Objective:** Measure settling time for all controllers ```bash
# Large initial disturbance: θ₁ = 0.3 rad, θ₂ = 0.4 rad
for ctrl in classical_smc sta_smc adaptive_smc hybrid_adaptive_sta_smc; do python simulate.py --ctrl $ctrl \ --override "simulation.initial_conditions=[0, 0, 0.3, 0, 0.4, 0]" \ --save "${ctrl}_large_disturbance.json"
done
``` **Expected Ranking (fastest to slowest):**

1. Hybrid Adaptive STA-SMC (~2.3s)
2. Super-Twisting SMC (~2.8s)
3. Classical SMC (~3.2s)
4. Adaptive SMC (~3.5s, includes adaptation phase)

---

## Part 6: Controller Selection Checklist Before selecting a controller, answer these questions: **System Characteristics:**

- [ ] Are system parameters well-known? (±10% accuracy)
- [ ] Is the model high-fidelity? (nonlinear dynamics captured)
- [ ] Are there significant disturbances? (>5% of control authority)
- [ ] Does the system exhibit parameter drift? (wear, temperature, loading) **Performance Requirements:**
- [ ] Is chattering acceptable? (actuator tolerance, noise constraints)
- [ ] What is the required settling time? (<2s, <5s, <10s)
- [ ] Are there overshoot constraints? (<5%, <10%, no limit)
- [ ] Is control effort limited? (energy, actuator saturation) **Implementation Constraints:**
- [ ] What is the control loop frequency? (<100 Hz, <1 kHz, >1 kHz)
- [ ] Is computational cost a factor? (embedded, real-time OS, desktop)
- [ ] Is tuning effort acceptable? (quick prototype, PSO optimization, manual)
- [ ] Are specialized tools available? (PSO, HIL testbed, simulation only) **Based on answers, use decision tree in Section 3.1**

---

## Troubleshooting ### Issue: All Controllers Perform Poorly **Symptoms:** Long settling times (>10s), high overshoot (>20%), instability **Diagnosis:**

1. **Check physics parameters:** ```bash python simulate.py --print-config | grep dip_params ``` Verify masses, lengths, inertias are reasonable 2. **Verify initial conditions:** ```bash python simulate.py --print-config | grep initial_conditions ``` Ensure angles are small (<0.5 rad) for linear region 3. **Validate gain bounds:** ```python from controllers import get_gain_bounds_for_pso, SMCType bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL) print("Recommended gain bounds:", bounds) ``` **Solution:** Use PSO to auto-tune gains (Tutorial 03)

---

### Issue: Adaptive Controller Not Adapting **Symptoms:** Adaptive gain remains constant, performance identical to classical **Diagnosis:**

```python
# Check if adaptation is occurring
data = json.load(open('results_adaptive.json'))
gain_trajectory = data['state_vars']['adaptive_gain'] if np.std(gain_trajectory) < 0.1: print("WARNING: Adaptation not occurring") print(f"Final gain: {gain_trajectory[-1]:.2f}") print(f"Initial gain: {gain_trajectory[0]:.2f}")
``` **Common Causes:**

- Adaptation rate too low (`γ < 0.1`)
- Leak rate too high (`leak_rate > 0.5`)
- System already well-controlled (no adaptation needed) **Solution:** Increase `adaptation_rate` to 0.5-1.0, reduce `leak_rate` to 0.01-0.05

---

## Issue: Hybrid Controller Unstable **Symptoms:** Oscillations grow, system diverges **Diagnosis:**

- Verify STA stability conditions (Section 4.2)
- Check adaptation rates (should be <0.5 for hybrid)
- Monitor initial transient (first 0.5 seconds) **Solution:**
1. Use auto-computation for `initial_alpha`, `initial_beta`
2. Reduce adaptation rates by 50%
3. Increase `max_force` if saturation occurs

---

## Practice Exercises ### Exercise 1: Controller Ranking Run all 4 controllers with the same initial condition `[0, 0, 0.2, 0, 0.3, 0]`. Rank them by:

1. Settling time (fastest to slowest)
2. Peak overshoot (lowest to highest)
3. Control effort (lowest to highest)
4. Chattering (lowest to highest) **Expected Learning:** Understanding performance tradeoffs

---

### Exercise 2: Boundary Layer Sweep For classical SMC, sweep `boundary_layer` from 0.001 to 0.5 (logarithmic spacing). Plot:

- Chattering index vs. boundary layer
- Steady-state error vs. boundary layer **Expected Learning:** Precision-chattering tradeoff in classical SMC

---

### Exercise 3: Robustness Test Simulate all controllers with:

- Nominal mass (`m0 = 1.0`)
- Heavy cart (`m0 = 1.5`)
- Light cart (`m0 = 0.6`) Which controllers maintain performance? Why? **Expected Learning:** Adaptive advantages under parameter uncertainty

---

## Summary **Controller Comparison Matrix:** | Aspect | Classical | Super-Twisting | Adaptive | Hybrid |

|--------|-----------|----------------|----------|--------|
| **Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Chattering** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Robustness** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Convergence** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Computation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Tunability** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | **Key Takeaways:**
- **Classical SMC:** Best starting point for learning and prototyping
- **Super-Twisting SMC:** Best for chattering-sensitive applications
- **Adaptive SMC:** Best for uncertain/varying systems
- **Hybrid Adaptive STA-SMC:** Best overall performance (if computational cost acceptable)

---

## Next Steps **Next Tutorial:** [Tutorial 03: PSO Optimization](tutorial-03-pso-optimization.md) - Automatically tune controller gains **Related Guides:**

- [Controllers API](../api/controllers.md): Technical reference for all 4 controller types
- [Optimization Workflows How-To](../how-to/optimization-workflows.md): Advanced PSO tuning strategies **Theory & Foundations:**
- [SMC Theory Guide](../theory/smc-theory.md): Deep mathematical foundations - Lyapunov stability proofs - Chattering analysis and boundary layers - Super-twisting algorithm mathematics - Practical design guidelines **Advanced Topics:**
- [Tutorial 04: Custom Controllers](tutorial-04-custom-controller.md): Implement your own SMC variant
- [Tutorial 05: Research Workflows](tutorial-05-research-workflow.md): Publication-ready comparative studies **Congratulations!** You now understand the strengths and tradeoffs of all 4 core SMC controllers and can select the appropriate one for your application.
