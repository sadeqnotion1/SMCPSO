# Step 4: Write Section 7.3 - Simulation Engine

**Time**: 1.5 hours
**Output**: 3 pages (Section 7.3 of Chapter 7)
**Source**: simulation_runner.py, vector_sim.py

---

## OBJECTIVE

Write a 3-page section describing the numerical integration method (RK4), batch simulation with Numba, and simulation context management.

---

## SOURCE MATERIALS TO READ FIRST (15 min)

### Primary Sources
1. **Read**: `D:\Projects\main\src\core\simulation_runner.py` (main simulation loop)
2. **Read**: `D:\Projects\main\src\core\vector_sim.py` (batch simulation)
3. **Read**: `D:\Projects\main\src\core\simulation_context.py` (context management)

---

## EXACT PROMPT TO USE

```
Write Section 7.3 - Simulation Engine (3 pages) for Chapter 7 (Implementation) of a Master's thesis on "Sliding Mode Control of Double-Inverted Pendulum with Particle Swarm Optimization."

Context:
- This is Section 7.3 of Chapter 7
- Audience: Control engineers and numerical methods specialists
- Format: LaTeX, IEEE citation style
- Tone: Technical, emphasize numerical accuracy and performance

Structure (3 pages total):

**Page 1: Numerical Integration**

Subsection: Fourth-Order Runge-Kutta Method
- Explain RK4 choice: Balance accuracy vs computational cost
- Mathematical formulation:
  * $k_1 = f(t, \vect{x})$
  * $k_2 = f(t + \Delta t/2, \vect{x} + k_1 \Delta t/2)$
  * $k_3 = f(t + \Delta t/2, \vect{x} + k_2 \Delta t/2)$
  * $k_4 = f(t + \Delta t, \vect{x} + k_3 \Delta t)$
  * $\vect{x}_{n+1} = \vect{x}_n + \frac{\Delta t}{6}(k_1 + 2k_2 + 2k_3 + k_4)$
- Time step selection: $\Delta t = 0.001$ seconds (1 kHz sampling)
- Error analysis: RK4 provides $\mathcal{O}(\Delta t^4)$ local truncation error
- Stability: Von Neumann stability analysis for this system

Code snippet (Python implementation of RK4):
```python
def rk4_step(dynamics, state, control, dt):
    k1 = dynamics.step(state, control, 0)
    k2 = dynamics.step(state + k1*dt/2, control, dt/2)
    k3 = dynamics.step(state + k2*dt/2, control, dt/2)
    k4 = dynamics.step(state + k3*dt, control, dt)
    return state + (k1 + 2*k2 + 2*k3 + k4) * dt / 6
```

**Page 2: Batch Simulation with Numba**

Subsection: Performance Optimization
- Challenge: PSO requires evaluating 1,500 simulations (30 particles × 50 iterations)
- Solution: Numba JIT compilation for CPU acceleration
- Speedup: ~50x compared to pure Python (benchmark on typical workstation)

Subsection: Vectorization Strategy
- Parallelize across initial conditions, not time steps (avoid race conditions)
- Batch size: 30 simulations in parallel (one PSO generation)
- Memory layout: Contiguous arrays for cache efficiency

Code snippet (Numba-accelerated batch simulation):
```python
@numba.jit(nopython=True, parallel=True)
def run_batch_simulation(initial_states, gains, params):
    n_sims = initial_states.shape[0]
    results = np.zeros((n_sims, n_timesteps, 6))
    for i in numba.prange(n_sims):
        results[i] = simulate_single(initial_states[i], gains, params)
    return results
```

Performance table:
| Method | Time (1 sim) | Time (1500 sims) | Speedup |
|--------|--------------|------------------|---------|
| Pure Python | 2.3 s | 3,450 s (57.5 min) | 1x |
| NumPy vectorized | 0.8 s | 1,200 s (20 min) | 2.9x |
| Numba JIT | 0.046 s | 69 s (1.15 min) | 50x |

**Page 3: Simulation Context Management**

Subsection: SimulationContext Class
- Purpose: Encapsulate controller + dynamics + parameters in single object
- Benefits:
  * Cleaner API (one object instead of passing 5+ arguments)
  * Easier serialization for checkpointing
  * Facilitates batch simulation

Code snippet:
```python
class SimulationContext:
    def __init__(self, controller, dynamics, sim_params):
        self.controller = controller
        self.dynamics = dynamics
        self.dt = sim_params['dt']
        self.t_final = sim_params['t_final']
        self.n_steps = int(self.t_final / self.dt)

    def run(self, initial_state):
        states = np.zeros((self.n_steps, 6))
        states[0] = initial_state
        for i in range(1, self.n_steps):
            u = self.controller.compute_control(states[i-1])
            states[i] = rk4_step(self.dynamics, states[i-1], u, self.dt)
        return states
```

Subsection: Deterministic Execution
- Global seed control: `np.random.seed(42)` in config
- RNG state serialization for reproducibility
- Hash verification for configuration changes

Summary: "The simulation engine achieves 50x speedup via Numba while maintaining numerical accuracy (RK4 integration) and reproducibility (deterministic seeding)."

Citation Requirements:
- Cite RK4 method cite:Press2007
- Cite Numba cite:Lam2015
- Cite numerical stability cite:Hairer1993

Quality Checks:
- Include performance benchmarks (table with timing data)
- Explain WHY RK4 chosen (not just WHAT it is)
- Quantify speedup (50x)

Length: 3 pages
```

---

## WHAT TO DO WITH THE OUTPUT

### 1. Verify Performance Numbers (20 min)

**Run benchmark**:
```bash
cd D:\Projects\main
python -m pytest tests/test_benchmarks/ --benchmark-only
```

**Update table** with actual measurements.

### 2. Test RK4 Code Snippet (10 min)

**Verify** the RK4 implementation matches `simulation_runner.py`.

### 3. Format as LaTeX (15 min)

```latex
\section{Simulation Engine}
\label{sec:impl:simulation}

[PASTE AI OUTPUT HERE]
```

### 4. Add Performance Table (10 min)

```latex
\begin{table}[ht]
\centering
\caption{Simulation performance comparison}
\label{tab:impl:performance}
\begin{tabular}{lccc}
\toprule
Method & Time (1 sim) & Time (1500 sims) & Speedup \\
\midrule
Pure Python & 2.3 s & 3,450 s & 1.0× \\
NumPy vectorized & 0.8 s & 1,200 s & 2.9× \\
Numba JIT & 0.046 s & 69 s & 50× \\
\bottomrule
\end{tabular}
\end{table}
```

---

## VALIDATION CHECKLIST

### Content Quality
- [ ] RK4 mathematical formulation complete
- [ ] Time step justified ($\Delta t = 0.001$ s)
- [ ] Numba speedup quantified (50x)
- [ ] Performance table included
- [ ] Simulation context explained

### Code Accuracy
- [ ] RK4 code snippet matches implementation
- [ ] Numba decorator syntax correct
- [ ] SimulationContext API accurate

### Mathematical Rigor
- [ ] Big-O notation for error: $\mathcal{O}(\Delta t^4)$
- [ ] Stability analysis mentioned
- [ ] Numerical precision discussed

---

## TIME CHECK
- Reading sources: 15 min
- Running prompt: 5 min
- Verifying benchmarks: 20 min
- Formatting LaTeX: 15 min
- Test compile: 5 min
- **Total**: ~1.5 hours

---

## NEXT STEP

**Proceed to**: `step_05_section_7_4_controller_modules.md`

---

**[OK] Ready? Create Section 7.3!**
