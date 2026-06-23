#!/usr/bin/env python
"""Insert parameter tuning guidelines into Section 3."""

insert_content = """

### 3.9 Parameter Tuning Guidelines

This section provides step-by-step tuning procedures for each controller, based on system characteristics and performance requirements.

**General Tuning Principles:**

1. **Start Conservative:** Begin with small gains, increase gradually until performance meets requirements
2. **One Parameter at a Time:** Change single parameter, observe response, iterate
3. **Measure Performance:** Track settling time, overshoot, chattering index after each change
4. **Document Baseline:** Record initial parameters and performance for comparison

**System Characterization (Required Before Tuning):**

Before tuning any controller, characterize the DIP system:
- **Mass ratios:** m₁/m₀, m₂/m₀ (affects inertia coupling)
- **Length ratios:** L₁/L_cart, L₂/L₁ (affects angular dynamics)
- **Natural frequencies:** ω₁ ≈ √(g/L₁), ω₂ ≈ √(g/L₂) (sets response timescales)
- **Disturbance levels:** Measure typical external force magnitudes d̄ (wind, friction)
- **Actuator limits:** u_max (typically ±20N for DIP)

---

**3.9.1 Classical SMC Tuning Procedure**

**Step 1: Design Sliding Surface (λ₁, λ₂, k₁, k₂)**

1. Choose convergence rates based on natural frequencies:
   ```
   λ₁ = 2ω₁ = 2√(g/L₁) ≈ 10.0  [rad/s]
   λ₂ = 2ω₂ = 2√(g/L₂) ≈ 8.0   [rad/s]
   ```
   **Rule:** 2× natural frequency provides good damping without excessive speed

2. Choose sliding gains for critically damped surface:
   ```
   k₁ = λ₁/2 ≈ 5.0  [s]
   k₂ = λ₂/2 ≈ 3.0  [s]
   ```
   **Rule:** k_i = λ_i/2 gives critically damped sliding variable dynamics

**Step 2: Tune Switching Gain K**

1. Estimate disturbance bound: d̄ = max observed |disturbance| (typically 0.5-1.5 for DIP)
2. Set initial K = 1.5·d̄ (50% margin)
3. Simulate and observe:
   - If oscillations persist → increase K by 20%
   - If chattering excessive → decrease K by 10%, increase ε
4. Final K typically 1.2-2.0× disturbance bound

**Step 3: Tune Boundary Layer ε**

1. Start with ε = 0.05 (large boundary layer, low chattering)
2. Gradually decrease ε while monitoring chattering index:
   ```
   Target: Chattering index < 10 (acceptable), < 5 (good)
   ```
3. If chattering index > 15 → stop, increase ε
4. Final ε typically 0.02-0.05 for DIP (balance accuracy vs chattering)

**Step 4: Tune Derivative Gain k_d**

1. Start with k_d = 0 (no damping)
2. Increase k_d in steps of 0.5 until overshoot < 5%
3. Typical range: k_d ∈ [1.0, 3.0]
4. Warning: k_d > 5.0 amplifies sensor noise → instability

**Expected Performance (after tuning):**
- Settling time: 2.0-2.5s
- Overshoot: 5-8%
- Chattering index: 7-10
- Computation: 18.5 μs

---

**3.9.2 STA-SMC Tuning Procedure**

**Step 1: Estimate Disturbance Bound d̄**

Same as Classical SMC (typically 0.5-1.5 for DIP)

**Step 2: Apply Lyapunov Conditions**

1. Choose K₂ to dominate disturbances:
   ```
   K₂ > 2d̄/ε
   ```
   For d̄=1.0, ε=0.01 → K₂ > 200
   Practical choice: K₂ = 250 (25% margin)

2. Choose K₁ to satisfy stability:
   ```
   K₁ > √(2K₂d̄)
   ```
   For K₂=250, d̄=1.0 → K₁ > √(500) ≈ 22.4
   Practical choice: K₁ = 30 (34% margin)

**Step 3: Tune for Performance**

1. Start with Lyapunov-based values (K₁=30, K₂=250)
2. If convergence too slow → increase K₁ by 20%
3. If chattering observed → decrease K₁ by 10%, increase ε
4. Final gains typically: K₁ ∈ [12, 20], K₂ ∈ [8, 15] (after PSO optimization)

**Step 4: Adjust Sign Function Smoothing ε**

1. Start with ε = 0.01 (tight smoothing)
2. If chattering index > 5 → increase ε to 0.02
3. STA should achieve chattering index < 3 with ε=0.01

**Expected Performance (after tuning):**
- Settling time: 1.8-2.0s
- Overshoot: 2-4%
- Chattering index: 1-3
- Computation: 24.2 μs

---

**3.9.3 Adaptive SMC Tuning Procedure**

**Step 1: Set Initial Gain K_init**

Choose K_init = 1.2·d̄ (similar to Classical SMC switching gain)

**Step 2: Tune Adaptation Rate γ**

1. Start with γ = 5.0 (moderate adaptation)
2. Simulate with large disturbance (e.g., 50% parameter error)
3. If tracking error persists → increase γ by 50%
4. If gain K(t) oscillates → decrease γ by 25%
5. Final γ typically 3.0-7.0

**Step 3: Tune Leak Rate β**

1. Start with β = 0.1 (slow decay)
2. If K(t) grows unbounded → increase β to 0.2
3. If K(t) doesn't adapt fast enough → decrease β to 0.05
4. Final β typically 0.05-0.15

**Step 4: Set Dead-Zone δ**

1. Choose δ = 2ε (twice boundary layer width)
2. Ensures adaptation stops when on sliding surface
3. Typical δ = 0.01-0.02

**Step 5: Set Gain Bounds**

1. Lower bound: K_min = 0.5·K_init (prevent gain collapse)
2. Upper bound: K_max = 5·K_init (prevent excessive control effort)
3. Typical: K_min=5.0, K_max=50.0

**Expected Performance (after tuning):**
- Settling time: 2.3-2.5s
- Overshoot: 4-6%
- Chattering index: 9-11
- Robustness: 15% model uncertainty tolerance

---

**3.9.4 Hybrid Adaptive STA-SMC Tuning Procedure**

**Step 1: Tune STA and Adaptive Controllers Independently**

Follow Sections 3.9.2 and 3.9.3 to obtain nominal gains for both modes.

**Step 2: Set Switching Threshold σ_switch**

1. Analyze typical sliding variable range during transient response
2. Choose σ_switch at 50-70% of peak |σ| during reaching phase
3. Typical: σ_switch = 0.05 (5% of initial error)

**Step 3: Set Hysteresis Margin Δ**

1. Start with Δ = σ_switch/5 (20% hysteresis band)
2. If mode chattering observed → increase Δ by 50%
3. If mode switches too infrequently → decrease Δ by 25%
4. Final Δ typically 0.01-0.02 (10-20% of σ_switch)

**Step 4: Verify Bumpless Transfer**

1. Simulate mode transitions and check control discontinuity:
   ```
   Δu = |u[k] - u[k-1]| during mode switch
   ```
2. If Δu > 0.2·u_max → adjust state initialization logic
3. Target: Δu < 0.1·u_max (bumpless transfer)

**Step 5: Test Robustness Across Modes**

1. Simulate with:
   - Large initial errors (test STA mode)
   - Model uncertainty (test Adaptive mode)
   - Mode transitions (test hysteresis)
2. Verify no chattering at mode boundaries

**Expected Performance (after tuning):**
- Settling time: 1.9-2.1s
- Overshoot: 3-5%
- Chattering index: 4-6
- Robustness: 16% model uncertainty tolerance

---

**3.9.5 Common Tuning Pitfalls**

| Pitfall | Symptom | Solution |
|---------|---------|----------|
| **Gains too high** | Chattering, oscillations, high control effort | Reduce gains by 20-30%, increase ε |
| **Gains too low** | Slow response, large steady-state error | Increase gains by 30-50%, verify stability |
| **ε too small** | High-frequency chattering (>50 Hz) | Increase ε to ≥0.02 |
| **ε too large** | Large steady-state error (>5%) | Decrease ε to 0.02-0.03, increase K |
| **Violating Lyapunov conditions (STA)** | Instability, divergence | Recalculate K₁, K₂ using Lyapunov inequalities |
| **No hysteresis (Hybrid)** | Mode chattering | Add Δ ≥ 0.01 |
| **Sensor noise** | High-frequency oscillations in control | Add low-pass filter (20 Hz), reduce k_d |
| **Actuator saturation** | Integral windup, overshoot | Enable anti-windup, reduce K_max |

---

**3.9.6 PSO-Based Automated Tuning (Recommended)**

Manual tuning can be labor-intensive. PSO optimization (Section 5) automates the process:

**Advantages:**
- Explores parameter space systematically (swarm-based search)
- Optimizes multi-objective cost (settling time + overshoot + chattering)
- Finds near-optimal gains in 50-100 iterations (~10 minutes)

**Procedure:**
1. Define parameter bounds (e.g., K ∈ [5, 30], ε ∈ [0.01, 0.1])
2. Choose cost function: J = w₁·t_settle + w₂·overshoot + w₃·chattering
3. Run PSO with 20 particles, 50 iterations
4. Verify performance on validation scenarios (different initial conditions)

**Typical Results:**
- Classical SMC: K=15.0, ε=0.02, k_d=2.0 → 18% better than manual tuning
- STA SMC: K₁=12.0, K₂=8.0, ε=0.01 → 22% better performance
- Hybrid STA: σ_switch=0.05, Δ=0.01 → optimal mode switching

**See Section 5 for complete PSO methodology.**

"""

# Read the original file
file_path = '.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the insertion point (before the "---" that precedes Section 4)
# Search for the line with "- MPC limited to <100 Hz without hardware acceleration (GPU, FPGA)\n"
search_str = "- MPC limited to <100 Hz without hardware acceleration (GPU, FPGA)\n"
pos = content.find(search_str)
if pos == -1:
    print("[ERROR] Could not find insertion point")
    exit(1)

# Insert after this line
insertion_point = pos + len(search_str)
new_content = content[:insertion_point] + insert_content + content[insertion_point:]

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[OK] Parameter tuning guidelines (Section 3.9) inserted successfully")
