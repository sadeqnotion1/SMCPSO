# Exercise 5: Controller Selection for Application

**Level:** Intermediate (Level 2)
**Estimated Time:** 25 minutes
**Prerequisites:** Tutorial 02, Tutorial 06 (Section 5)

## Objective
Select the best controller for a mobile robot operating in a high-disturbance environment (frequent collisions, variable payload).

## Your Task
1. Review controller robustness rankings from Tutorial 06
2. Analyze application requirements:
   - High disturbances (±50N forces)
   - Moderate uncertainty (±15% payload variation)
   - Energy constraint (battery-powered)
   - Smoothness preferred (passenger comfort)
3. Justify controller selection using decision tree
4. Write 1-paragraph recommendation

**Expected Selection:**
- **Hybrid Adaptive STA** or **Adaptive SMC**
- Rationale: Best disturbance rejection + uncertainty handling
- Energy acceptable (not critical constraint)
- Smoothness good (STA reduces chattering)

**Decision Tree:**
```
High Disturbances? YES → Moderate Uncertainty? YES → Energy Critical? NO → Select: Hybrid/Adaptive
```

See [solution](solutions/exercise_05_solution.py).
