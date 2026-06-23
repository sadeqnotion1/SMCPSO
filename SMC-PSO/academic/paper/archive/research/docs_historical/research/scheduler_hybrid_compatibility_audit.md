# Adaptive Gain Scheduler - Hybrid Compatibility Audit

**Date:** November 8, 2025
**Phase:** 1.2 - Scheduler Implementation Review
**File:** `src/controllers/adaptive_gain_scheduler.py`

---

## Executive Summary

The adaptive gain scheduler implements **controller-agnostic** scheduling that treats all SMC variants identically. For Hybrid Adaptive STA SMC, this creates three critical incompatibilities:

1. **State-based vs Surface-based thresholds**: Scheduler uses |θ| while Hybrid uses |s| for adaptation
2. **Uniform gain scaling**: No awareness that c1/c2 affect internal k1/k2 adaptation
3. **Missing dual-layer coordination**: No compensation for k1/k2 slowdown when c1/c2 reduced

**Conclusion:** Scheduler assumes gain independence, violating Hybrid's architectural coupling between external (c1/c2) and internal (k1/k2) layers.

---

## Scheduler Architecture

### Control Flow (lines 235-259)

```python
def compute_control(state, state_vars, history):
    # 1. Compute error magnitude from STATE
    error_mag = compute_error_magnitude(state)  # Uses ||[θ1, θ2]||

    # 2. Schedule gains based on error magnitude
    scheduled_gains = schedule_gains(state)

    # 3. Update base controller gains
    update_controller_gains(scheduled_gains)  # Modifies c1/c2/λ1/λ2

    # 4. Delegate to base controller
    return base_controller.compute_control(state, state_vars, history)
```

**Observation:** Scheduler is **stateless wrapper** - no internal state, no awareness of controller internals beyond gain parameters.

---

## Error Magnitude Computation

### Implementation (lines 127-144)

```python
def compute_error_magnitude(self, state: np.ndarray) -> float:
    if self.config.use_angles_only:
        error = state[1:3]  # [θ1, θ2]
    else:
        error = state  # Full state

    return np.linalg.norm(error)  # L2 norm
```

**Configuration:**
```python
use_angles_only = True  # Default - uses only pendulum angles
```

**Result:** `error_mag = sqrt(θ1² + θ2²)`

### Comparison with Hybrid's Sliding Surface

**Scheduler uses:**
```
error_mag = ||[θ1, θ2]||
```

**Hybrid uses:**
```
s = c1*(θ̇1 + λ1 θ1) + c2*(θ̇2 + λ2 θ2) + cart_term
```

**CRITICAL MISMATCH:**
- Scheduler thresholds: |θ| = 0.1 rad (aggressive) vs 0.2 rad (conservative)
- Hybrid dead zone: |s| = 0.01 (freeze adaptation)
- **Problem:** |θ| and |s| are NOT linearly related!

**Example Scenario:**
```
State: θ1=0.08 rad, θ2=0.03 rad, θ̇1=-0.5 rad/s, θ̇2=0.1 rad/s

Scheduler sees:
  |θ| = sqrt(0.08² + 0.03²) = 0.085 rad < 0.1 rad
  → Uses AGGRESSIVE gains (full c1/c2)

Hybrid computes:
  s = c1*(-0.5 + 12.839*0.08) + c2*(0.1 + 2.750*0.03) + cart
    = c1*0.527 + c2*0.183 + cart
    ≈ 10.149*0.527 + 6.815*0.183 = 6.6 (large!)
  |s| = 6.6 >> 0.01 (NOT in dead zone)
  → k1/k2 adapt normally
```

**Opposite Scenario:**
```
State: θ1=0.15 rad, θ2=0.12 rad, θ̇1=0.01 rad/s, θ̇2=-0.02 rad/s

Scheduler sees:
  |θ| = sqrt(0.15² + 0.12²) = 0.192 rad
  → TRANSITION zone (interpolating to conservative)

Hybrid computes:
  s = c1*(0.01 + 12.839*0.15) + c2*(-0.02 + 2.750*0.12) + cart
    = c1*1.936 + c2*0.310 + cart
    ≈ 10.149*1.936 + 6.815*0.310 = 21.8 (very large!)
  |s| = 21.8 >> 0.01
  → k1/k2 should adapt RAPIDLY, but scheduler reduces c1/c2!
```

**Conclusion:** Scheduler and Hybrid use DIFFERENT error metrics, causing mode mismatches.

---

## Gain Scheduling Logic

### Threshold-Based Mode Selection (lines 146-189)

```python
def schedule_gains(self, state):
    error_mag = compute_error_magnitude(state)  # ||θ||

    # Apply hysteresis
    if last_mode == 'aggressive':
        small_thresh = 0.1 + 0.01 = 0.11 rad
    else:
        small_thresh = 0.1 - 0.01 = 0.09 rad

    if last_mode == 'conservative':
        large_thresh = 0.2 - 0.01 = 0.19 rad
    else:
        large_thresh = 0.2 + 0.01 = 0.21 rad

    # Mode selection
    if error_mag < small_thresh:
        return aggressive_gains  # Full c1/c2/λ1/λ2
    elif error_mag > large_thresh:
        return conservative_gains  # c1/c2/λ1/λ2 * 0.5
    else:
        # Linear interpolation
        alpha = (error_mag - small_thresh) / (large_thresh - small_thresh)
        return (1-alpha)*aggressive + alpha*conservative
```

**Observations:**

1. **Hysteresis (±0.01 rad):**
   - Prevents rapid switching between modes
   - BUT: Still allows mode switching every few timesteps if |θ| oscillates near thresholds
   - **Problem for Hybrid:** k1/k2 adaptation is SLOW (gamma1=0.5, gamma2=0.3), expects stable gains over ~1 second

2. **Linear Interpolation:**
   - Smooth transition between aggressive and conservative
   - **Problem for Hybrid:** Gradual gain reduction causes gradual |s| reduction → gradual k1/k2 slowdown
   - No "snap" transition, so Hybrid cannot detect mode change

3. **Uniform Scaling:**
   ```python
   conservative_gains = aggressive_gains * 0.5  # ALL gains scaled equally
   ```
   - c1: 10.149 → 5.075 (50% reduction)
   - λ1: 12.839 → 6.420 (50% reduction)
   - c2: 6.815 → 3.408 (50% reduction)
   - λ2: 2.750 → 1.375 (50% reduction)

   **Problem:** No awareness that c1/λ1 and c2/λ2 have DIFFERENT roles:
   - c1/c2: Surface weights (affect |s| magnitude directly)
   - λ1/λ2: Damping coefficients (affect |s| dynamics indirectly)

   Scaling ALL equally may break tuned c1/λ1 and c2/λ2 ratios.

---

## Controller-Specific Gain Update

### Hybrid Update Path (lines 224-227)

```python
elif controller_type == 'HybridAdaptiveSTASMC':
    # Hybrid: [c1, lambda1, c2, lambda2]
    (self.base_controller.c1, self.base_controller.lambda1,
     self.base_controller.c2, self.base_controller.lambda2) = new_gains
```

**What Gets Modified:**
- ✓ c1, lambda1, c2, lambda2 (external surface coefficients)

**What Does NOT Get Modified:**
- ✗ k1, k2 (internal adaptive gains) - these evolve via Hybrid's adaptation law
- ✗ u_int (STA integral state) - evolves via STA dynamics
- ✗ gamma1, gamma2 (adaptation rates) - fixed parameters
- ✗ taper_eps (self-tapering threshold) - fixed parameter

**Critical Observation:**

Scheduler assumes it's modifying **direct control gains** (like Classical SMC's K, K_d). But for Hybrid, it's modifying **sliding surface topology**, not control authority.

**Analogy:**
- **Classical SMC:** Scheduler adjusts "steering wheel sensitivity" → immediate effect on control
- **Hybrid SMC:** Scheduler adjusts "road curvature" → indirect effect via k1/k2 adaptation

---

## Comparison with Other Controllers

### Classical SMC (lines 206-210)

```python
if controller_type == 'ClassicalSMC':
    # [k1, k2, lam1, lam2, K, kd]
    (self.base_controller.k1, self.base_controller.k2,
     self.base_controller.lam1, self.base_controller.lam2,
     self.base_controller.K, self.base_controller.kd) = new_gains
```

**Why it works:**
- K, kd: Direct control gains (affect control output immediately)
- k1, k2, lam1, lam2: Sliding surface coefficients (similar to Hybrid's c1/c2/λ1/λ2)
- **No internal adaptation** - gains directly control chattering

**Result:** Chattering reduction 28-40% (MT-8 Enhancement #3)

---

### STA SMC (lines 212-216)

```python
elif controller_type in ['STASMC', 'SuperTwistingSMC']:
    # [K1, K2, k1, k2, lam1, lam2]
    (self.base_controller.K1, self.base_controller.K2,
     self.base_controller.k1, self.base_controller.k2,
     self.base_controller.lam1, self.base_controller.lam2) = new_gains
```

**Why it doesn't work (0% change):**
- STA already uses continuous approximation (tanh) → minimal chattering
- K1, K2 are FIXED gains (no adaptation) but designed for chattering suppression
- Reducing K1/K2 doesn't further reduce chattering (already near optimal)

**Result:** 0% chattering change (MT-8 Enhancement #3)

---

### Adaptive SMC (lines 218-222)

```python
elif controller_type == 'AdaptiveSMC':
    # [k1, k2, k3, k4, k5]
    (self.base_controller.k1, self.base_controller.k2,
     self.base_controller.k3, self.base_controller.k4,
     self.base_controller.k5) = new_gains
```

**Why it has mixed results:**
- k1, k2: Base sliding surface gains
- k3, k4, k5: Internal adaptive gains (similar to Hybrid's k1/k2!)
- **Interference:** External scheduling of k3/k4/k5 may conflict with internal adaptation

**Result:** Mixed (-7.7% to +2.8%) - NOT recommended (MT-8 Enhancement #3)

---

## Missing Hybrid-Specific Logic

### What Scheduler Should Do (But Doesn't)

**1. Use Sliding Surface Magnitude:**
```python
# Current (WRONG for Hybrid)
error_mag = ||[θ1, θ2]||

# Should use (aligned with Hybrid's adaptation)
s = compute_sliding_surface(state, c1, λ1, c2, λ2)
error_mag = |s|
```

**2. Adjust Adaptation Rates:**
```python
# Current (WRONG - only modifies c1/c2)
scheduled_gains = aggressive_gains * conservative_scale

# Should also boost internal adaptation to compensate
if switching_to_conservative:
    # Increase gamma1/gamma2 to counteract slower |s| growth
    gamma1_boost = 1.0 / conservative_scale  # 2.0x
    gamma2_boost = 1.0 / conservative_scale  # 2.0x
```

**3. Controller-Aware Gain Relationships:**
```python
# Current (WRONG - uniform scaling)
c1_sched = c1_agg * 0.5
λ1_sched = λ1_agg * 0.5
c2_sched = c2_agg * 0.5
λ2_sched = λ2_agg * 0.5

# Should preserve c1/λ1 and c2/λ2 ratios
c1_sched = c1_agg * 0.5
λ1_sched = λ1_agg * 0.7  # Less aggressive reduction for damping
c2_sched = c2_agg * 0.5
λ2_sched = λ2_agg * 0.7
```

**4. Slower Switching for Hybrid:**
```python
# Current (WRONG - same hysteresis for all controllers)
hysteresis_width = 0.01 rad

# Should use controller-specific hysteresis
if controller_type == 'HybridAdaptiveSTASMC':
    hysteresis_width = 0.05 rad  # 5x slower switching
    # Hybrid's k1/k2 adaptation is slow (gamma1=0.5), needs stable gains
```

---

## Quantitative Impact Analysis

### Assumption Violations

**Scheduler Assumption 1:** "Reducing gains by 50% reduces chattering by ~30-50%"

**Reality for Hybrid:**
- Reducing c1/c2 by 50% → reduces |s| by ~50%
- Reducing |s| by 50% → reduces k1_dot by ~67% (superlinear, from Phase 1.1 proof)
- Slower k1/k2 growth → INCREASES chattering (insufficient control authority)

**Violation:** Scheduler assumption is **OPPOSITE** of Hybrid's behavior.

---

**Scheduler Assumption 2:** "All gains can be scaled uniformly"

**Reality for Hybrid:**
- c1/λ1 ratio determines pendulum 1 surface dynamics
- c2/λ2 ratio determines pendulum 2 surface dynamics
- PSO tuned these ratios to [10.149/12.839] = 0.79 and [6.815/2.750] = 2.48
- Uniform scaling preserves ratios BUT changes absolute magnitude of |s|

**Violation:** Scheduler preserves ratios but breaks |s| magnitude, which k1/k2 depend on.

---

**Scheduler Assumption 3:** "State magnitude |θ| correlates with chattering risk"

**Reality for Hybrid:**
- Chattering originates from sign(s) switching, not |θ| magnitude
- |s| dynamics depend on θ, θ̇, and cart position x
- |θ| may be large while |s| is small (well-damped system)
- |θ| may be small while |s| is large (high velocity case)

**Violation:** Scheduler uses wrong error metric for Hybrid.

---

## Timing Analysis

### Scheduler Update Frequency

**Every timestep (dt = 0.01s = 100 Hz):**
1. Compute |θ| from state
2. Determine gain mode (aggressive/conservative/transition)
3. Update c1/c2/λ1/λ2
4. Hybrid computes s with NEW c1/c2/λ1/λ2
5. Hybrid updates k1/k2 based on NEW |s|

**Problem:** Scheduler can switch modes FASTER than Hybrid adapts.

**Example Timeline:**
```
t=0.00s: |θ|=0.09 rad → aggressive (c1=10.149)
t=0.01s: |θ|=0.11 rad → transition (c1=8.5)  [SWITCHED!]
t=0.02s: |θ|=0.13 rad → transition (c1=7.5)
t=0.03s: |θ|=0.10 rad → transition (c1=8.0)  [SWITCHED BACK!]
...
Meanwhile:
t=0.00s: k1=20.0
t=0.01s: k1=20.05  (slow growth, gamma1=0.5)
t=0.02s: k1=20.08
t=0.03s: k1=20.10  (adapts over ~1 second)
```

**Conclusion:** Scheduler switches 10-100x faster than k1/k2 can adapt, creating instability.

---

## Code Audit Findings

### 1. No Hybrid-Specific Branches

**Current Code:**
```python
def schedule_gains(self, state):
    # Generic for all controllers
    error_mag = self.compute_error_magnitude(state)
    # ... same logic for Classical, STA, Adaptive, Hybrid
```

**Missing:**
```python
def schedule_gains(self, state):
    controller_type = type(self.base_controller).__name__

    if controller_type == 'HybridAdaptiveSTASMC':
        # Use |s| instead of |θ|
        error_mag = self._compute_hybrid_sliding_surface(state)
    else:
        error_mag = self.compute_error_magnitude(state)
    # ...
```

---

### 2. No Awareness of Internal State

**Current:**
- Scheduler is **stateless wrapper**
- No access to k1, k2, u_int values
- Cannot detect if Hybrid is in dead zone, saturated, or adapting normally

**Should Have:**
```python
def schedule_gains(self, state):
    # Query Hybrid internal state
    k1_current = self.base_controller.k1 (or from state_vars)
    k2_current = self.base_controller.k2

    # Adjust scheduling based on adaptation progress
    if k1_current < 0.5 * k1_max:
        # Still building up control authority - use aggressive gains
        return self.aggressive_gains
    elif k1_current > 0.9 * k1_max:
        # Near saturation - reduce gains to prevent runaway
        return self.conservative_gains
```

---

### 3. No Compensation Mechanism

**Current:**
- Scheduler reduces c1/c2/λ1/λ2 by 50%
- k1/k2 adaptation slows by 67% (superlinear)
- **No compensation** for this slowdown

**Should Have:**
```python
def update_controller_gains(self, new_gains):
    if controller_type == 'HybridAdaptiveSTASMC':
        # Update surface coefficients
        (self.base_controller.c1, self.base_controller.lambda1,
         self.base_controller.c2, self.base_controller.lambda2) = new_gains

        # COMPENSATE: Boost adaptation rates to counteract |s| reduction
        reduction_factor = new_gains[0] / self.aggressive_gains[0]  # c1 ratio
        if reduction_factor < 1.0:
            # Conservative mode - boost gamma1/gamma2
            self.base_controller.gamma1 *= (1.0 / reduction_factor)
            self.base_controller.gamma2 *= (1.0 / reduction_factor)
```

---

## Conclusion

The adaptive gain scheduler implements a **one-size-fits-all** approach that:

1. ✓ Works well for Classical SMC (28-40% chattering reduction)
2. ⚪ Has no effect on STA SMC (already optimal, 0% change)
3. ⚠️ Has mixed results for Adaptive SMC (conflicts with internal adaptation)
4. ❌ **FAILS catastrophically for Hybrid SMC (+217% chattering increase)**

**Root Causes of Hybrid Incompatibility:**

| Issue | Scheduler Behavior | Hybrid Requirement | Consequence |
|-------|-------------------|-------------------|-------------|
| Error Metric | Uses \|θ\| | Uses \|s\| | Mode mismatch |
| Gain Independence | Assumes independent | c1/c2 affect k1/k2 | Feedback interference |
| Update Frequency | 100 Hz (every dt) | ~1 Hz (slow adaptation) | Instability |
| Uniform Scaling | All gains * 0.5 | Preserve c/λ ratios | Broken dynamics |
| Stateless Design | No internal state access | Needs k1/k2 values | Cannot compensate |

**Recommendation:** Hybrid controller requires **architecture-aware scheduling** with:
- Sliding surface-based thresholds (|s| not |θ|)
- Dynamic adaptation rate compensation
- Slower switching (0.05 rad hysteresis vs 0.01 rad)
- Selective gain scheduling (test c1/c2 vs λ1/λ2 separately in Phase 3)

---

## Next Steps

- **Phase 1.3:** Mine MT-8 data to correlate IC magnitude with chattering degradation
- **Phase 2.1:** Test gain interference hypothesis (manual 50% c1/c2 scaling)
- **Phase 3:** Test selective scheduling (c1/c2 only, λ1/λ2 only)
- **Phase 4:** Develop HybridGainScheduler with |s|-based thresholds

---

## References

- `src/controllers/adaptive_gain_scheduler.py`: Complete implementation (281 lines)
- `src/controllers/smc/hybrid_adaptive_sta_smc.py`: Lines 400-443 (sliding surface computation)
- `.artifacts/research/experiments/mt8_disturbances/MT8_ADAPTIVE_SCHEDULING_SUMMARY.md`: Lines 119-149 (Hybrid results)
- `docs/research/hybrid_gain_coordination_analysis.md`: Phase 1.1 architecture analysis

---

**Document Version:** 1.0
**Date:** November 8, 2025
**Status:** Phase 1.2 COMPLETE
