# Interactive Exercises - DIP-SMC-PSO

Welcome to the interactive exercises for the Double Inverted Pendulum SMC-PSO framework. These exercises are designed to reinforce concepts from Tutorials 01-07 and provide hands-on practice with controller analysis, optimization, and robustness testing.

---

## Exercise Index

### Level 2: Intermediate Exercises

**Exercise 1: Disturbance Rejection Testing**
- **Topic:** Test Adaptive SMC under external disturbances
- **Prerequisites:** Tutorial 01, Tutorial 06 (Section 2)
- **Estimated Time:** 30 minutes
- **Skills:** Running simulations, analyzing disturbance rejection, performance metrics
- [Exercise Description](exercise_01_disturbance.md) | [Solution](solutions/exercise_01_solution.py)

**Exercise 2: Model Uncertainty Analysis**
- **Topic:** Test STA SMC under parameter variations
- **Prerequisites:** Tutorial 02, Tutorial 06 (Section 3)
- **Estimated Time:** 40 minutes
- **Skills:** Parameter sweeps, Monte Carlo analysis, statistical confidence intervals
- [Exercise Description](exercise_02_uncertainty.md) | [Solution](solutions/exercise_02_solution.py)

**Exercise 5: Controller Selection for Application**
- **Topic:** Select best controller for high-disturbance environment
- **Prerequisites:** Tutorial 02, Tutorial 06 (Section 5)
- **Estimated Time:** 25 minutes
- **Skills:** Controller comparison, decision trees, application requirements
- [Exercise Description](exercise_05_selection.md) | [Solution](solutions/exercise_05_solution.py)

### Level 3: Advanced Exercises

**Exercise 3: Custom Cost Function Design**
- **Topic:** Design multi-objective cost function minimizing energy and chattering
- **Prerequisites:** Tutorial 03, Tutorial 07 (Section 2)
- **Estimated Time:** 50 minutes
- **Skills:** Multi-objective optimization, weight selection, Pareto frontiers
- [Exercise Description](exercise_03_cost_function.md) | [Solution](solutions/exercise_03_solution.py)

**Exercise 4: PSO Convergence Diagnostics**
- **Topic:** Debug premature convergence in PSO optimization
- **Prerequisites:** Tutorial 03, Tutorial 07 (Section 4)
- **Estimated Time:** 45 minutes
- **Skills:** Convergence analysis, diversity metrics, adaptive inertia
- [Exercise Description](exercise_04_convergence.md) | [Solution](solutions/exercise_04_solution.py)

---

## How to Use These Exercises

### 1. Prerequisites Check
Ensure you've completed the prerequisite tutorials before attempting each exercise. The exercises build on concepts introduced in the tutorials.

### 2. Attempt Before Viewing Solutions
Try to solve each exercise independently before looking at the solution. This reinforces learning and identifies knowledge gaps.

### 3. Run the Code
All solutions are fully executable Python scripts. Run them to see expected outputs:
```bash
# From project root
cd docs/guides/exercises/solutions
python exercise_01_solution.py
```

### 4. Experiment and Modify
After understanding the solution, experiment with:
- Different controller types
- Different parameter values
- Different disturbance magnitudes
- Different optimization objectives

### 5. Compare Your Solution
Compare your approach with the provided solution. There may be multiple valid approaches - the solution shows one recommended method.

---

## Exercise Difficulty Levels

**Level 2 (Intermediate):**
- Requires basic understanding of SMC and simulation framework
- Focuses on running existing tools and interpreting results
- Typical completion time: 25-40 minutes
- Exercises: 1, 2, 5

**Level 3 (Advanced):**
- Requires understanding of optimization theory and advanced SMC
- Involves designing custom functions and debugging complex issues
- Typical completion time: 45-50 minutes
- Exercises: 3, 4

---

## Learning Outcomes

After completing all 5 exercises, you will be able to:

- [ ] Test controllers under realistic disturbances and uncertainties
- [ ] Analyze performance degradation using Monte Carlo methods
- [ ] Design custom multi-objective cost functions for PSO
- [ ] Diagnose and fix PSO convergence issues
- [ ] Select appropriate controllers for specific applications
- [ ] Apply robustness testing best practices to research and industry projects

---

## Additional Resources

**Tutorials:**
- [Tutorial 06: Robustness Analysis](../tutorials/tutorial-06-robustness-analysis.md)
- [Tutorial 07: Multi-Objective PSO](../tutorials/tutorial-07-multi-objective-pso.md)

**Documentation:**
- [API Reference](../../api/index.rst)
- [Theory Documentation](../../theory/index.md)
- [User Guides](../INDEX.md)

**Support:**
- Report issues: [GitHub Issues](https://github.com/theSadeQ/dip-smc-pso/issues)
- Discuss exercises: [GitHub Discussions](https://github.com/theSadeQ/dip-smc-pso/discussions)

---

## Progress Tracking

Mark exercises as complete when you can:
1. Solve independently (without hints)
2. Explain your solution approach
3. Achieve expected results (within ±10% tolerance)

**Your Progress:**
- [ ] Exercise 1: Disturbance Rejection
- [ ] Exercise 2: Model Uncertainty
- [ ] Exercise 3: Custom Cost Function
- [ ] Exercise 4: PSO Convergence Diagnostics
- [ ] Exercise 5: Controller Selection

**Completion Badge:** Complete all 5 exercises to demonstrate proficiency in DIP-SMC-PSO advanced topics.

---

**Last Updated:** November 12, 2025
**Version:** 1.0
**Author:** DIP-SMC-PSO Development Team
**License:** MIT License
