# Step 1: Extract Source Materials for Chapter 8 - Simulation Setup

**Time**: 1.5 hours
**Output**: Organized notes for Chapter 8
**Goal**: Extract simulation parameters, initial conditions, disturbances, metrics, and hardware specs

---

## OBJECTIVE

Chapter 8 describes the experimental setup: initial conditions, disturbance scenarios, performance metrics, and computational hardware specifications.

---

## SOURCE MATERIALS TO READ (1.5 hours)

### Primary Sources

1. **Configuration File** (30 min)
   - `D:\Projects\main\config.yaml` (complete file)
   - Extract:
     * Initial conditions (x₀, θ₁₀, θ₂₀)
     * Time parameters (t_final, dt)
     * Physics parameters (masses, lengths, friction)
     * Controller parameters for each controller

2. **Simulation Parameters** (20 min)
   - `src\core\simulation_runner.py` (integration settings)
   - Note: RK4 step size, max simulation time
   - Check for adaptive time stepping (if any)

3. **Disturbance Scenarios** (20 min)
   - `scripts\mt8_robust_pso.py` (MT-8 disturbance definitions)
   - Step disturbance: 10N @ t=2s
   - Impulse disturbance: 30N pulse @ t=2s, duration 0.1s
   - Check for other disturbance types in benchmarks

4. **Performance Metrics** (20 min)
   - `src\utils\analysis\` (metric calculation functions)
   - Settling time, overshoot, steady-state error
   - Control effort, chattering index
   - Check: `benchmarks\comprehensive_benchmark.csv` for metric definitions

5. **Hardware Specifications** (10 min)
   - Check system info from project documentation
   - CPU, RAM, Python version, NumPy version
   - Note: Typical PSO runtime, simulation time

---

## EXTRACTION TASKS

### Task 1: Extract Initial Conditions (15 min)

**From** `config.yaml`:

**Create file**: `thesis\notes\chapter08_initial_conditions.txt`

```
INITIAL CONDITIONS FOR CHAPTER 8

Standard Initial Condition (used in all baseline tests):
- Cart position: x₀ = 0.1 m
- Pendulum 1 angle: θ₁₀ = 0.05 rad (2.86°)
- Pendulum 2 angle: θ₂₀ = 0.03 rad (1.72°)
- Cart velocity: ẋ₀ = 0 m/s
- Pendulum 1 angular velocity: θ̇₁₀ = 0 rad/s
- Pendulum 2 angular velocity: θ̇₂₀ = 0 rad/s

Robustness Test Initial Conditions (LT-6):
- IC1 (small): [0.05, 0.03, 0.02, 0, 0, 0]
- IC2 (medium): [0.1, 0.05, 0.03, 0, 0, 0] (standard)
- IC3 (large): [0.2, 0.1, 0.08, 0, 0, 0]
- IC4 (extreme): [0.3, 0.15, 0.12, 0, 0, 0]

Monte Carlo Initial Conditions (if used):
- Random perturbations: ±10% around standard IC
- Number of trials: 100
- Seed: 42 (reproducibility)
```

### Task 2: Extract Disturbance Scenarios (15 min)

**From** `scripts\mt8_robust_pso.py` and MT-8 reports:

**Create file**: `thesis\notes\chapter08_disturbances.txt`

```
DISTURBANCE SCENARIOS FOR CHAPTER 8

Nominal Scenario (Baseline):
- No external disturbances
- Used for: Initial controller comparison, PSO optimization

Step Disturbance:
- Type: Constant force applied to cart
- Magnitude: 10 N
- Application time: t = 2.0 s
- Duration: Until end of simulation (3.0 s)
- Purpose: Test steady-state disturbance rejection

Impulse Disturbance:
- Type: Short-duration pulse
- Magnitude: 30 N
- Application time: t = 2.0 s
- Duration: 0.1 s (100 ms)
- Purpose: Test transient disturbance rejection

Combined Disturbance (if used):
- Both step and impulse applied simultaneously
- Application time: t = 2.0 s

Parameter Uncertainty (LT-6):
- Mass variations: ±20% (m_cart, m1, m2)
- Length variations: ±10% (L1, L2)
- Friction variations: ±30% (b_cart, b1, b2)
- Purpose: Test robustness to model uncertainty
```

### Task 3: Extract Performance Metrics (20 min)

**From** `src\utils\analysis\` and benchmark files:

**Create file**: `thesis\notes\chapter08_metrics.txt`

```
PERFORMANCE METRICS FOR CHAPTER 8

Primary Metrics:
1. Settling Time (t_s)
   - Definition: Time to reach and stay within 2% of reference (zero)
   - Units: seconds
   - Threshold: |θ₁| < 0.02 rad AND |θ₂| < 0.02 rad AND |x| < 0.02 m
   - Typical values: 2-8 seconds

2. Maximum Overshoot (M_p)
   - Definition: Maximum peak deviation from reference
   - Units: radians (for angles), meters (for position)
   - Calculation: max(|θ₁(t)|, |θ₂(t)|, |x(t)|) for t ∈ [0, t_s]
   - Typical values: 0.05-0.20 rad

3. Steady-State Error (e_ss)
   - Definition: Final error magnitude at t = t_final
   - Units: Euclidean norm of state vector
   - Calculation: ||x(t_final)||₂
   - Typical values: <0.01 (converged), >0.1 (diverged)

Secondary Metrics:
4. Control Effort (E)
   - Definition: Integral of squared control signal
   - Formula: E = ∫₀^T u²(t) dt ≈ Σᵢ uᵢ² Δt
   - Units: N²·s
   - Purpose: Energy consumption

5. Chattering Index (C)
   - Definition: Sum of absolute control changes
   - Formula: C = Σᵢ |uᵢ - uᵢ₋₁|
   - Units: N
   - Purpose: Quantify high-frequency switching

6. Convergence Rate (λ)
   - Definition: Exponential decay rate (if applicable)
   - Fit: ||x(t)|| ≈ ||x₀|| e^(-λt)
   - Units: 1/s
   - Purpose: Characterize transient response
```

### Task 4: Extract Hardware Specifications (10 min)

**Create file**: `thesis\notes\chapter08_hardware.txt`

```
HARDWARE SPECIFICATIONS FOR CHAPTER 8

Development Workstation:
- CPU: [Extract from system - e.g., Intel Core i7-11700K @ 3.6 GHz]
- Cores/Threads: 8 cores / 16 threads
- RAM: [Extract - e.g., 32 GB DDR4-3200]
- OS: Windows 11 (or specify from CLAUDE.md: win32)

Software Environment:
- Python: 3.9+ (from requirements.txt)
- NumPy: 1.24+
- SciPy: 1.10+
- Numba: 0.56+ (JIT compilation)
- PySwarms: 1.3.0

Computational Performance:
- Single simulation time: ~50 ms (5 seconds simulated, 1 kHz sampling)
- PSO optimization time: ~10-20 seconds (30 particles × 50 iterations, parallelized)
- Batch simulation: 50x speedup via Numba (from Chapter 7)

Reproducibility:
- Global seed: 42 (from config.yaml)
- Deterministic: Yes (all RNG seeded)
- Version control: Git commit hash recorded in results
```

---

## VALIDATION CHECKLIST

### Source Files Read
- [ ] config.yaml completely reviewed
- [ ] Disturbance definitions extracted (MT-8 reports)
- [ ] Performance metrics documented
- [ ] Hardware specs gathered

### Extraction Completed
- [ ] Initial conditions file created
- [ ] Disturbances file created
- [ ] Metrics file created
- [ ] Hardware file created

### Understanding Achieved
- [ ] Can explain all 6 performance metrics
- [ ] Can describe 4 disturbance scenarios
- [ ] Can list all initial condition variants

---

## TIME CHECK
- config.yaml review: 30 min
- Simulation parameters: 20 min
- Disturbance scenarios: 20 min
- Performance metrics: 20 min
- Hardware specs: 10 min
- File creation: 10 min
- **Total**: ~1.5 hours

---

## NEXT STEP

**Proceed to**: `step_02_section_8_1_intro.md`

---

**[OK] Ready to extract!**
