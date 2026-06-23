# Step 6: Write Section 7.5 - PSO Optimization Module

**Time**: 1.5 hours
**Output**: 3 pages (Section 7.5 of Chapter 7)
**Source**: src/optimizer/pso_optimizer.py

---

## OBJECTIVE

Write a 3-page section describing the PSO implementation, fitness function design, and constraint handling.

---

## SOURCE MATERIALS TO READ FIRST (20 min)

### Primary Sources
1. **Read**: `D:\Projects\main\src\optimizer\pso_optimizer.py` (~400 lines)
2. **Read**: `D:\Projects\main\optimization_results\mt8_robust_pso_summary.json`
3. **Review**: Chapter 6 (PSO Theory) for algorithm background

---

## EXACT PROMPT TO USE

```
Write Section 7.5 - PSO Optimization Module (3 pages) for Chapter 7 (Implementation).

Structure (3 pages):

**Page 1: PSO Implementation**

Subsection: PySwarms Integration
- Uses PySwarms 1.3.0 library cite:Miranda2018
- Global-best PSO variant (gbest topology)
- Hyperparameters: w=0.7298 (inertia), c1=c2=1.49618 (cognitive/social)
- Swarm size: 30 particles
- Iterations: 50 generations

Code snippet:
```python
from pyswarms.single import GlobalBestPSO

class PSOTuner:
    def __init__(self, n_particles=30, n_iterations=50):
        self.options = {'c1': 1.49618, 'c2': 1.49618, 'w': 0.7298}
        self.optimizer = GlobalBestPSO(
            n_particles=n_particles,
            dimensions=len(bounds),
            options=self.options,
            bounds=bounds
        )

    def optimize(self, objective_function):
        cost, pos = self.optimizer.optimize(
            objective_function,
            iters=self.n_iterations
        )
        return pos, cost
```

Subsection: Parallel Evaluation
- Each particle evaluation is independent
- Use multiprocessing.Pool for CPU parallelization
- Speedup: ~8x on 8-core workstation
- Batch size: 30 (one generation)

**Page 2: Fitness Function Design**

Subsection: Cost Function Formulation
- Multi-objective optimization via weighted sum
- Components:
  1. Settling time ($t_s$): Time to reach 2% of reference (weight: 0.3)
  2. Overshoot ($M_p$): Maximum peak deviation (weight: 0.25)
  3. Steady-state error ($e_{ss}$): Final error magnitude (weight: 0.2)
  4. Control effort ($\int u^2 dt$): Energy consumption (weight: 0.15)
  5. Chattering ($\sum |\Delta u|$): Control discontinuities (weight: 0.1)

Mathematical formulation:
$$J = 0.3 \cdot \frac{t_s}{t_{s,max}} + 0.25 \cdot \frac{M_p}{M_{p,max}} + 0.2 \cdot e_{ss} + 0.15 \cdot \frac{E}{E_{max}} + 0.1 \cdot \frac{C}{C_{max}}$$

Code snippet:
```python
def fitness_function(gains):
    # Run simulation with these gains
    states, controls = simulate(gains)

    # Compute metrics
    settling_time = compute_settling_time(states)
    overshoot = compute_overshoot(states)
    ss_error = np.abs(states[-1] - target)
    energy = np.sum(controls**2) * dt
    chattering = np.sum(np.abs(np.diff(controls)))

    # Normalize and weight
    cost = (0.3 * settling_time / 10.0 +
            0.25 * overshoot / 0.5 +
            0.2 * ss_error / 0.1 +
            0.15 * energy / 1000.0 +
            0.1 * chattering / 5000.0)

    return cost
```

Subsection: Robust PSO Fitness (MT-8)
- Problem: Gains optimized for nominal conditions fail under disturbances
- Solution: Evaluate fitness under both nominal and disturbed scenarios
- Robust fitness: $J_{robust} = 0.5 \cdot J_{nominal} + 0.5 \cdot J_{disturbed}$
- Disturbances: Step (10N @ t=2s), Impulse (30N pulse @ t=2s, 0.1s duration)
- Result: 6.35% average improvement, 21.4% for hybrid controller

**Page 3: Constraint Handling**

Subsection: Gain Bounds
- Each gain has physical limits: $g_i \in [g_{i,min}, g_{i,max}]$
- Example: Classical SMC gains in [0.1, 50.0]
- PySwarms enforces bounds via clipping during velocity update

Subsection: Stability Constraints
- Challenge: Some gain combinations violate Lyapunov stability
- Solution: Add penalty term to fitness if simulation diverges
- Divergence detection: $\|\vect{x}\| > 100$ or NaN values
- Penalty: $J_{penalty} = 1000$ (forces PSO away from unstable regions)

Code snippet:
```python
def fitness_with_constraints(gains):
    try:
        cost = fitness_function(gains)
        # Check for divergence
        if np.isnan(cost) or cost > 100:
            return 1000  # Penalty
        return cost
    except Exception:
        return 1000  # Penalty for simulation failures
```

Subsection: Computational Cost
- Time per evaluation: ~50 ms (single simulation)
- Total PSO run: 30 particles × 50 iterations × 50 ms = 75 seconds
- Parallelized: 75 / 8 cores = ~10 seconds
- MT-8 robust PSO: 2× longer (dual evaluations) = ~20 seconds

Summary: "The PSO module achieves efficient gain tuning via parallelization and robust fitness design, completing optimization in 10-20 seconds on standard hardware."

Citation Requirements:
- Cite PySwarms cite:Miranda2018
- Cite PSO algorithm cite:Kennedy1995
- Cite robust optimization cite:Beyer2007

Quality Checks:
- Explain WHY each fitness component is weighted that way
- Quantify computational cost (seconds)
- Show actual code (not pseudocode)

Length: 3 pages
```

---

## WHAT TO DO WITH THE OUTPUT

### 1. Verify Fitness Weights (10 min)

Check `src/optimizer/pso_optimizer.py` for actual weight values.

### 2. Verify Hyperparameters (10 min)

Check `config.yaml`:
```yaml
pso:
  n_particles: 30
  n_iterations: 50
  w: 0.7298
  c1: 1.49618
  c2: 1.49618
```

### 3. Format as LaTeX (15 min)

```latex
\section{PSO Optimization Module}
\label{sec:impl:pso}

[PASTE AI OUTPUT HERE]
```

---

## VALIDATION CHECKLIST

### Content Quality
- [ ] PySwarms integration explained
- [ ] Fitness function with 5 components described
- [ ] Weights justified (0.3, 0.25, 0.2, 0.15, 0.1)
- [ ] Robust PSO (MT-8) covered
- [ ] Constraint handling via penalties
- [ ] Computational cost quantified

### Code Accuracy
- [ ] Hyperparameters match config.yaml
- [ ] Fitness weights match implementation
- [ ] Bounds correct for each controller

### Mathematical Rigor
- [ ] Fitness equation typeset correctly
- [ ] Normalization factors explained

---

## TIME CHECK
- Reading sources: 20 min
- Running prompt: 5 min
- Verifying parameters: 20 min
- Formatting LaTeX: 15 min
- **Total**: ~1.5 hours

---

## NEXT STEP

**Proceed to**: `step_07_section_7_6_testing.md`

---

**[OK] Ready!**
