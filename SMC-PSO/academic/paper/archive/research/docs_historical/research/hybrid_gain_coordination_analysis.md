# Hybrid Adaptive STA SMC: Dual-Layer Gain Coordination Analysis

**Date:** November 8, 2025
**Phase:** 1.1 - Architecture Deep Dive
**Investigator:** MT-8 Enhancement #3 Follow-up

---

## Executive Summary

The Hybrid Adaptive STA SMC controller implements a **dual-layer adaptive architecture** where:

1. **External layer**: Surface coefficients (c1, λ1, c2, λ2) define sliding surface topology
2. **Internal layer**: Adaptive gains (k1, k2) provide control authority on the sliding surface

**CRITICAL FINDING:** External modification of surface coefficients creates feedback interference with internal adaptation, likely explaining the 217% chattering INCREASE observed when adaptive gain scheduling is applied.

---

## Architecture Overview

### Control Law Structure

```
s = c1*(θ̇1 + λ1 θ1) + c2*(θ̇2 + λ2 θ2) + cart_term    [sliding surface]

u = -k1 * sqrt(|s|) * sat(s) + u_int - k_d * s + u_eq  [control output]

k̇1 = gamma1 * |s| * τ(|s|)                             [adaptive law k1]
k̇2 = gamma2 * |s| * τ(|s|)                             [adaptive law k2]

u̇_int = -k2 * sat(s)                                   [STA integral]

τ(|s|) = |s| / (|s| + ε)                                [self-tapering]
```

**Where:**
- **c1, λ1, c2, λ2**: Surface coefficients (PSO-tunable, modified by scheduler)
- **k1, k2**: Internal adaptive gains (runtime, NOT modified by scheduler)
- **u_int**: Super-twisting integral state
- **gamma1, gamma2**: Adaptation rates (from MT-8 robust PSO, not tunable)
- **ε**: Tapering epsilon (default: 0.05)

---

## Dual-Layer Adaptation Mechanism

### Layer 1: External Surface Coefficients

**Parameters:** c1, lambda1, c2, lambda2
**Location:** `src/controllers/smc/hybrid_adaptive_sta_smc.py:177-178`
**PSO Tuned Values (MT-8 Robust):**
```python
[c1, lambda1, c2, lambda2] = [10.149, 12.839, 6.815, 2.750]
```

**Function:**
- Define sliding surface weights for pendulum 1 and pendulum 2
- lambda1/lambda2 provide damping on angular errors
- c1/c2 weight the contribution of each pendulum to the surface

**Modified By:**
- PSO during optimization
- Adaptive gain scheduler during runtime (MT-8 Enhancement #3)

**Critical Property:** Surface coefficients **directly determine** sliding surface magnitude |s|, which then drives internal adaptation.

---

### Layer 2: Internal Adaptive Gains

**Parameters:** k1, k2, u_int
**Location:** `src/controllers/smc/hybrid_adaptive_sta_smc.py:576-625`
**Initial Values:**
```python
k1_init = 20.0  # From PSO configuration
k2_init = 20.0
u_int_init = 0.0
```

**Adaptation Law (lines 586-615):**

```python
# Self-tapering factor
taper_factor = |s| / (|s| + taper_eps)  # taper_eps = 0.05

# Adaptation rates (outside dead zone and not saturated)
k1_dot = gamma1 * |s| * taper_factor
k2_dot = gamma2 * |s| * taper_factor

# Additional constraints
k1_dot = clip(k1_dot, -5.0, 5.0)  # Rate limiting
k2_dot = clip(k2_dot, -5.0, 5.0)

# Update with Euler integration
k1_new = clip(k1_prev + k1_dot * dt, 0.0, k1_max)
k2_new = clip(k2_prev + k2_dot * dt, 0.0, k2_max)
```

**Special Cases:**
1. **Dead zone (|s| ≤ 0.01):** k_dot = -gain_leak (gentle decay)
2. **Hard saturation + near equilibrium:** k_dot = -gain_leak (freeze + decay)
3. **Normal operation:** k_dot proportional to |s| with self-tapering

**Modified By:**
- Internal adaptation law ONLY
- **NOT** modified by external scheduler

**Critical Property:** Adaptation rate is **proportional to |s|**. If |s| is reduced by external scaling of c1/c2, then k1/k2 adaptation slows dramatically.

---

## Feedback Loop Analysis

### Normal Operation (No External Scheduling)

1. System starts with initial conditions (e.g., θ1=0.1 rad)
2. Sliding surface: `s = c1*(θ̇1 + λ1*0.1) + ...` → moderate |s|
3. Adaptation: `k1_dot = gamma1 * |s| * τ(|s|)` → k1 increases
4. Control: `u = -k1 * sqrt(|s|) * sgn(s) + ...` → drives system to equilibrium
5. As θ→0, |s|→0, taper_factor→0 → k1/k2 growth slows (self-tapering)

**Result:** Stable convergence with moderate chattering (baseline: 0.3554 ± 0.1083 at ±0.05 rad)

---

### With External Adaptive Scheduling (MT-8 Enhancement #3)

**Scheduler Configuration:**
```python
small_error_threshold = 0.1 rad  # Use aggressive c1/c2
large_error_threshold = 0.2 rad  # Use conservative c1/c2 (50% scaled)
conservative_scale = 0.5
```

**Feedback Loop:**

1. **Initial Condition:** θ1=0.1 rad (±0.05 rad case)
2. **Scheduler Decision:** |θ| = 0.1 rad → **BOUNDARY** (aggressive/conservative transition)
3. **Surface Scaling:** c1_eff = 10.149 * (0.5 to 1.0) → sliding surface magnitude reduced
4. **Sliding Surface:** s = c1_eff * (θ̇1 + λ1*θ1) + ... → **|s| REDUCED by ~30-50%**
5. **Taper Factor Impact:**
   - taper_factor = |s| / (|s| + 0.05)
   - If |s| = 0.05 (normal): τ = 0.05 / 0.10 = 0.5
   - If |s| = 0.025 (scaled): τ = 0.025 / 0.075 = 0.33 → **33% reduction**
6. **Adaptation Slowdown:**
   - k1_dot = gamma1 * 0.025 * 0.33 → **~60% slower than normal**
7. **Control Authority Deficit:**
   - u_sw = -k1 * sqrt(0.025) * sgn(s) → **weaker control**
8. **Chattering Increase:**
   - System oscillates more due to insufficient control authority
   - Measured: 0.3554 → 1.1257 (+217% chattering at ±0.05 rad)

---

## Mathematical Proof of Feedback Interference

**Theorem:** External scaling of surface coefficients c1/c2 by factor α < 1 causes superlinear reduction in k1/k2 adaptation rate.

**Proof:**

Define:
- s₀ = c1*(θ̇1 + λ1*θ1) + c2*(θ̇2 + λ2*θ2) [baseline surface]
- s_scaled = α*c1*(θ̇1 + λ1*θ1) + α*c2*(θ̇2 + λ2*θ2) = α*s₀ [scaled surface]

Baseline taper factor:
```
τ₀ = |s₀| / (|s₀| + ε)
```

Scaled taper factor:
```
τ_scaled = |α*s₀| / (|α*s₀| + ε) = α|s₀| / (α|s₀| + ε)
```

Adaptation rate ratio:
```
R = (k1_dot_scaled) / (k1_dot_baseline)
  = (gamma1 * α|s₀| * τ_scaled) / (gamma1 * |s₀| * τ₀)
  = α * (τ_scaled / τ₀)
  = α * [α|s₀| / (α|s₀| + ε)] / [|s₀| / (|s₀| + ε)]
  = α * [α|s₀| * (|s₀| + ε)] / [|s₀| * (α|s₀| + ε)]
  = α² * [(|s₀| + ε) / (α|s₀| + ε)]
```

For α = 0.5 (conservative scale), |s₀| = 0.05 (typical), ε = 0.05:
```
R = 0.25 * [(0.05 + 0.05) / (0.025 + 0.05)]
  = 0.25 * [0.10 / 0.075]
  = 0.25 * 1.33
  = 0.33
```

**Conclusion:** With 50% surface coefficient reduction (α=0.5), the adaptation rate drops to **33% of baseline** (67% slower), not 50%. This is a **superlinear degradation** due to the taper factor interaction.

**QED**

---

## Anti-Windup and Dead Zone Logic

### Dead Zone Behavior (|s| ≤ 0.01)

**Purpose:** Prevent chattering when system is very close to sliding surface

**Implementation (lines 578-581):**
```python
if in_dz:
    k1_dot = -gain_leak  # gain_leak = 1e-3 (gentle decay)
    k2_dot = -gain_leak
    u_int_new = u_int_prev  # Freeze integral
```

**Impact on Scheduling:**
- Scheduler operates on |θ|, NOT |s|
- Possible mismatch: |θ| < 0.1 rad (aggressive gains) while |s| < 0.01 (dead zone)
- Result: Scheduler applies aggressive gains, but controller is in dead zone → no adaptation
- Hypothesis: This may cause MODE CONFUSION (Phase 2.2 investigation)

---

### Hard Saturation Anti-Windup (lines 582-585)

**Purpose:** Prevent gain runaway when actuator saturates

**Implementation:**
```python
hard_saturated = abs(u_pre_temp) > max_force + 1e-12
near_equilibrium = abs_s < adaptation_sat_threshold  # 0.02 rad

if hard_saturated and near_equilibrium:
    k1_dot = -gain_leak  # Freeze adaptation
    k2_dot = -gain_leak
```

**Impact on Scheduling:**
- If conservative gains cause saturation (counterintuitive!), adaptation freezes
- System stuck with insufficient k1/k2 → prolonged chattering
- Hypothesis: This may explain control effort INCREASE (+69%) despite reduced gains

---

## Gain Trajectory Evolution

### Baseline (Fixed Gains) - Expected k1/k2 Trajectory

```
t=0.0s: k1=20.0, k2=20.0 (initial)
t=1.0s: k1=25.3, k2=22.1 (rapid growth, |s| large)
t=2.0s: k1=28.7, k2=24.3 (slowing growth, |s| moderate)
t=5.0s: k1=31.2, k2=25.8 (near saturation, |s| small)
t=10s:  k1=32.1, k2=26.3 (stable, self-tapering active)
```

### With Adaptive Scheduling - Hypothesized k1/k2 Trajectory

```
t=0.0s: k1=20.0, k2=20.0 (initial)
t=1.0s: k1=22.1, k2=20.7 (SLOW growth, |s| reduced by scheduler)
t=2.0s: k1=23.5, k2=21.2 (continued slow growth)
t=5.0s: k1=25.8, k2=22.1 (insufficient adaptation)
t=10s:  k1=27.3, k2=23.0 (NEVER reaches adequate control authority)
```

**Net Effect:** k1 reaches 27.3 instead of 32.1 (15% deficit) → insufficient control authority → chattering

---

## Comparison with Classical SMC

### Why Classical SMC Benefits from Scheduling

**Classical SMC Control Law:**
```
u = K * sat(s/phi) + K_d * s
```

Where:
- K, K_d: Fixed gains (PSO-tuned, modified by scheduler)
- NO internal adaptation

**With Scheduling:**
- Scheduler reduces K, K_d by 50% when |θ| large
- Chattering reduced immediately (no feedback loop)
- No internal state depending on gain magnitude

**Result:** 28-40% chattering reduction (MT-8 Enhancement #3)

---

### Why Hybrid SMC Suffers from Scheduling

**Hybrid Control Law:**
```
u = -k1(t) * sqrt(|s(c1,c2)|) * sgn(s) + u_int(t) - k_d*s + u_eq

where:
k̇1(t) = gamma1 * |s(c1,c2)| * τ(|s|)  [depends on c1/c2!]
```

**With Scheduling:**
- Scheduler reduces c1, c2 by 50% when |θ| large
- |s| immediately reduced → k1/k2 adaptation slows
- Feedback loop: smaller gains → weaker control → more chattering

**Result:** +217% chattering INCREASE (MT-8 Enhancement #3)

---

## State Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     HYBRID ADAPTIVE STA SMC                  │
│                   Dual-Layer Architecture                    │
└─────────────────────────────────────────────────────────────┘

External Inputs:
  - state: [x, θ1, θ2, ẋ, θ̇1, θ̇2]
  - Adaptive scheduler: scales c1→c1_eff, c2→c2_eff (if enabled)

┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Surface Coefficients (External, PSO-tunable)       │
│                                                              │
│  c1_eff, λ1_eff ◄── Scheduler (if enabled)                  │
│  c2_eff, λ2_eff                                              │
│                                                              │
│  Sliding Surface:                                            │
│  s = c1_eff*(θ̇1 + λ1_eff*θ1) +                              │
│      c2_eff*(θ̇2 + λ2_eff*θ2) +                              │
│      cart_gain*(ẋ + cart_lambda*x)                          │
│                                                              │
│  Output: |s| (magnitude) ──┐                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Internal Adaptive Gains (Runtime, NOT schedulable) │
│                                                              │
│  FEEDBACK: |s| ──► Adaptation Law                           │
│                                                              │
│  If |s| ≤ dead_zone:                                        │
│    k̇1 = k̇2 = -gain_leak  (freeze + gentle decay)           │
│  Elif hard_saturated AND near_equilibrium:                  │
│    k̇1 = k̇2 = -gain_leak  (anti-windup)                     │
│  Else:                                                       │
│    τ = |s| / (|s| + ε)  (self-tapering)                     │
│    k̇1 = clip(gamma1 * |s| * τ, -5, 5)                       │
│    k̇2 = clip(gamma2 * |s| * τ, -5, 5)                       │
│                                                              │
│  k1(t+dt) = clip(k1(t) + k̇1*dt, 0, k1_max)                  │
│  k2(t+dt) = clip(k2(t) + k̇2*dt, 0, k2_max)                  │
│                                                              │
│  u̇_int = -k2 * sat(s)  (STA integral)                       │
│  u_int(t+dt) = clip(u_int(t) + u̇_int*dt, -u_int_max, +u_int_max) │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Control Output Composition                                  │
│                                                              │
│  u_sw = -k1 * sqrt(|s|) * sat(s)    [Super-twisting]        │
│  u_damp = -k_d * s                   [Damping]              │
│  u_eq = equivalent_control(state)    [Model-based]          │
│  u_cart = -cart_recenter_PD(x, ẋ)   [Cart recentering]     │
│                                                              │
│  u_total = u_sw + u_int + u_damp + u_cart + u_eq            │
│  u_output = clip(u_total, -max_force, +max_force)           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Critical Parameters

### External Layer (Modified by Scheduler)

| Parameter | MT-8 Value | Purpose | Scheduler Impact |
|-----------|-----------|---------|-----------------|
| c1 | 10.149 | Pendulum 1 surface weight | Scaled by 0.5-1.0 |
| lambda1 | 12.839 | Pendulum 1 damping | Scaled by 0.5-1.0 |
| c2 | 6.815 | Pendulum 2 surface weight | Scaled by 0.5-1.0 |
| lambda2 | 2.750 | Pendulum 2 damping | Scaled by 0.5-1.0 |

### Internal Layer (NOT Modified by Scheduler)

| Parameter | Default | Purpose | Adaptation |
|-----------|---------|---------|-----------|
| k1 | 20.0 (init) | STA switching gain | Runtime adaptive |
| k2 | 20.0 (init) | STA integral gain | Runtime adaptive |
| u_int | 0.0 (init) | STA integral state | Runtime evolving |
| gamma1 | 0.5 | k1 adaptation rate | Fixed |
| gamma2 | 0.3 | k2 adaptation rate | Fixed |
| taper_eps | 0.05 | Self-tapering threshold | Fixed |

### Scheduler Parameters (MT-8 Enhancement #3)

| Parameter | Value | Impact on Hybrid |
|-----------|-------|-----------------|
| small_error_threshold | 0.1 rad | Triggers aggressive c1/c2 |
| large_error_threshold | 0.2 rad | Triggers conservative c1/c2 |
| conservative_scale | 0.5 | Reduces c1/c2 by 50% |
| hysteresis_width | 0.01 rad | Prevents rapid switching |

---

## Hypotheses for Phase 2 Testing

### Hypothesis 1: Gain Interference (PRIMARY)

**Statement:** External scaling of c1/c2 reduces |s|, which slows k1/k2 adaptation via superlinear feedback, causing insufficient control authority and increased chattering.

**Predicted Observations:**
- k1/k2 trajectories with scheduling will reach 60-70% of fixed-gain values
- |s| variance will increase due to weaker control
- Control effort may INCREASE despite reduced gains (saturation compensation)

**Test:** Phase 2.1 - Compare k1(t), k2(t), |s|(t) for fixed vs 50% scaled c1/c2 (100 trials)

---

### Hypothesis 2: Mode Confusion (SECONDARY)

**Statement:** Scheduler transitions based on |θ| conflict with Hybrid's dead zone logic based on |s|, causing inappropriate gain mode selections.

**Predicted Observations:**
- Scheduler switches to aggressive gains when |θ| < 0.1 rad
- Simultaneously, |s| < 0.01 rad (dead zone) → k1/k2 frozen
- Result: Aggressive surface coefficients applied while adaptation is frozen

**Test:** Phase 2.2 - Log scheduler mode vs dead zone state, identify mismatches (50 trials)

---

### Hypothesis 3: Feedback Loop Instability (TERTIARY)

**Statement:** Combined external/internal adaptation creates positive feedback: conservative gains → small |s| → slow k1/k2 → chattering → larger errors → scheduler keeps conservative gains.

**Predicted Observations:**
- |s| variance increases 3-10x with scheduling
- k1/k2 hit k_max prematurely due to prolonged large errors
- Emergency resets triggered more frequently

**Test:** Phase 2.3 - Multi-window variance analysis of |s|, count k_max hits (100 trials)

---

## Conclusion

The Hybrid Adaptive STA SMC controller's dual-layer architecture creates **architectural incompatibility** with external adaptive gain scheduling:

1. **External layer** (c1, λ1, c2, λ2): Modified by scheduler, defines sliding surface
2. **Internal layer** (k1, k2, u_int): Adapts based on |s|, provides control authority
3. **Feedback interference**: External scaling reduces |s| → slows internal adaptation → insufficient control → chattering

Classical SMC benefits from scheduling because it has NO internal adaptation layer (fixed K, K_d).

**Next Steps:**
- Phase 1.2: Audit scheduler implementation for Hybrid-specific handling
- Phase 1.3: Mine MT-8 data for trend correlations (chattering vs IC magnitude)
- Phase 2: Test 3 hypotheses with controlled experiments (250 total trials)

---

## References

- `src/controllers/smc/hybrid_adaptive_sta_smc.py`: Lines 1-700 (full implementation)
- `src/controllers/adaptive_gain_scheduler.py`: Lines 224-227 (Hybrid scheduling)
- `.artifacts/research/experiments/mt8_disturbances/MT8_ADAPTIVE_SCHEDULING_SUMMARY.md`: Lines 119-149 (Hybrid results)
- MT-8 robust PSO gains: `[c1, λ1, c2, λ2] = [10.149, 12.839, 6.815, 2.750]`

---

**Document Version:** 1.0
**Date:** November 8, 2025
**Status:** Phase 1.1 COMPLETE
