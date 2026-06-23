# Exercise 3: Custom Cost Function Design

**Level:** Advanced (Level 3)
**Estimated Time:** 50 minutes
**Prerequisites:** Tutorial 03, Tutorial 07 (Section 2)

## Objective
Design a multi-objective cost function to minimize **energy consumption** (∫u²dt) and **chattering frequency** simultaneously for Classical SMC.

## Your Task
1. Implement cost function: `cost = w1*(energy/norm_energy) + w2*(chattering/norm_chattering)`
2. Run PSO with 3 weight configurations: (0.7, 0.3), (0.5, 0.5), (0.3, 0.7)
3. Compare energy and chattering for 3 solutions
4. Recommend best for battery-powered robot

**Expected Results:**
- w1=0.7: Energy=180J, Chattering=12Hz (Energy-focused)
- w1=0.5: Energy=220J, Chattering=9Hz (Balanced)
- w1=0.3: Energy=280J, Chattering=6Hz (Smoothness-focused)

**Recommendation:** w1=0.5 provides best tradeoff for most applications.

See [solution](solutions/exercise_03_solution.py).
