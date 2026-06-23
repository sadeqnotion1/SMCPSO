# Exercise 1: Disturbance Rejection Testing

**Level:** Intermediate (Level 2)
**Estimated Time:** 30 minutes
**Prerequisites:** Tutorial 01, Tutorial 06 (Section 2)

---

## Objective

Test the **Adaptive SMC** controller under a 50N horizontal step disturbance applied at t=2.0s for 0.5 seconds. Analyze the disturbance rejection capability and performance degradation.

---

## Background

Real-world control systems must handle unexpected disturbances such as:
- External forces (wind, collisions, pushing)
- Load changes (picking up/dropping objects)
- Environmental perturbations (terrain bumps for mobile robots)

A robust controller should:
1. **Reject disturbances quickly** (return to equilibrium within 2-5 seconds)
2. **Minimize performance degradation** (settling time increase <20%)
3. **Maintain stability** (no divergence or oscillations)

---

## Your Task

Write a Python script that:

1. **Runs nominal simulation** (no disturbance) with Adaptive SMC
2. **Runs disturbed simulation** with 50N horizontal force at t=2.0s for 0.5s
3. **Computes performance metrics:**
   - Settling time (nominal vs disturbed)
   - Overshoot (nominal vs disturbed)
   - Control effort (nominal vs disturbed)
   - Rejection time (time to return within 5% of equilibrium after disturbance)
4. **Plots comparison:**
   - Theta1 vs time (nominal vs disturbed)
   - Cart position vs time
   - Control input vs time
   - Shade disturbance period (orange)

---

## Expected Results

**Nominal Case (No Disturbance):**
- Settling time: ~3.5s
- Max overshoot: ~8 degrees
- Control effort: ~250 J

**Disturbed Case (50N Step):**
- Settling time: ~4.0s (+14%, GOOD)
- Max overshoot: ~10 degrees (+25%, ACCEPTABLE)
- Control effort: ~280 J (+12%, EXCELLENT)
- Rejection time: ~0.6s (EXCELLENT)

**Performance Assessment:**
- Adaptive SMC should show EXCELLENT disturbance rejection
- Degradation <15% for all metrics
- Rejection time <1.0s

---

## Hints

1. **Apply disturbance:**
   ```python
   def step_disturbance(t, state, magnitude=50.0, start=2.0, duration=0.5):
       if start <= t < (start + duration):
           return np.array([magnitude, 0, 0, 0, 0, 0])
       return np.zeros(6)
   ```

2. **Compute rejection time:**
   - Find time when |theta1| drops below 5% of max deviation after disturbance
   - Rejection time = t_within_threshold - t_disturbance_end

3. **Plotting:**
   - Use `axvspan(start, end, alpha=0.2, color='orange')` to shade disturbance period

---

## Success Criteria

Your solution is correct if:
- [x] Nominal simulation converges (settling time < 5s)
- [x] Disturbed simulation converges (no divergence)
- [x] Performance degradation <20% for settling time
- [x] Rejection time <1.0s
- [x] Plot shows clear disturbance rejection behavior

---

## Solution

See [exercise_01_solution.py](solutions/exercise_01_solution.py) for complete solution.

**Key Concepts Reinforced:**
- Disturbance injection into dynamics
- Performance metric computation
- Comparative analysis (nominal vs disturbed)
- Robustness quantification

---

## Extension Challenges

1. **Vary disturbance magnitude:** Test 25N, 50N, 75N, 100N - plot rejection time vs magnitude
2. **Test other controllers:** Compare Classical SMC, STA, Adaptive, Hybrid
3. **Impulse disturbance:** Change duration to 0.05s (50ms) - analyze response
4. **Torque disturbance:** Apply 5 Nm torque to link 1 instead of force to cart

---

**Difficulty:** 2/5
**Time:** 30 minutes
**Status:** Ready
