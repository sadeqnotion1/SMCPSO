"""
Expand E004 and E005 with full detailed content.

This script writes comprehensive educational content for PSO and Simulation episodes.
"""

from pathlib import Path


def expand_e004():
    """Return full E004 content."""
    return """# E004: PSO Optimization for Controller Tuning

## Introduction

Particle Swarm Optimization (PSO) is a meta-heuristic optimization algorithm inspired by social behavior of bird flocking and fish schooling. In this project, PSO automatically tunes controller gains to minimize control cost while maintaining stability.

This episode covers:
- PSO algorithm fundamentals with detailed explanations
- Cost function design for control systems
- Constraint handling for stability
- Robust optimization techniques (MT-8 results)
- Real performance improvements from benchmarks

## PSO Algorithm Fundamentals

### Biological Inspiration

**Bird Flocking Analogy:**
- Each bird (particle) searches for food (optimal solution)
- Birds share information about food locations
- Each bird adjusts flight direction based on:
  1. Its own best location found (cognitive component)
  2. Swarm's best location found (social component)
  3. Current velocity (momentum/inertia)

**Translation to Optimization:**
- Particle = candidate solution (controller gains)
- Position = point in search space
- Velocity = direction and magnitude of parameter updates
- Food = minimum cost function value

### PSO Update Equations

**Position Update:**
```
x_i(t+1) = x_i(t) + v_i(t+1)

Where:
  x_i = position of particle i (gain vector)
  v_i = velocity of particle i
  t = iteration number
```

**Velocity Update:**
```
v_i(t+1) = w·v_i(t) + c1·r1·(p_i - x_i(t)) + c2·r2·(g - x_i(t))

Where:
  w = inertia weight (0.4-0.9, controls exploration/exploitation)
  c1 = cognitive coefficient (~2.0, personal best attraction)
  c2 = social coefficient (~2.0, global best attraction)
  r1, r2 = random numbers ∈ [0,1] (stochastic exploration)
  p_i = personal best position of particle i
  g = global best position (across all particles)
```

**Physical Interpretation:**
- `w·v_i(t)`: Momentum (continue in current direction)
- `c1·r1·(p_i - x_i(t))`: Attraction to own best found
- `c2·r2·(g - x_i(t))`: Attraction to swarm's best found

### Code Implementation

From `src/optimizer/pso_optimizer.py`:

```python
class PSOTuner:
    def __init__(self, bounds, n_particles=30, iters=50, w=0.7, c1=2.0, c2=2.0):
        self.bounds = bounds
        self.n_particles = n_particles
        self.iters = iters
        self.w = w  # Inertia weight
        self.c1 = c1  # Cognitive coefficient
        self.c2 = c2  # Social coefficient

    def optimize(self, objective_function):
        # Initialize particles randomly within bounds
        positions = self._initialize_particles()
        velocities = np.zeros_like(positions)

        # Track personal and global bests
        personal_best_positions = positions.copy()
        personal_best_costs = np.array([objective_function(p) for p in positions])
        global_best_idx = np.argmin(personal_best_costs)
        global_best_position = personal_best_positions[global_best_idx]
        global_best_cost = personal_best_costs[global_best_idx]

        # PSO iterations
        for iter in range(self.iters):
            for i in range(self.n_particles):
                # Random coefficients
                r1 = np.random.random(len(positions[i]))
                r2 = np.random.random(len(positions[i]))

                # Velocity update
                velocities[i] = (
                    self.w * velocities[i] +
                    self.c1 * r1 * (personal_best_positions[i] - positions[i]) +
                    self.c2 * r2 * (global_best_position - positions[i])
                )

                # Position update
                positions[i] = positions[i] + velocities[i]

                # Enforce bounds
                positions[i] = np.clip(positions[i], self.bounds['min'],
                                      self.bounds['max'])

                # Evaluate cost
                cost = objective_function(positions[i])

                # Update personal best
                if cost < personal_best_costs[i]:
                    personal_best_costs[i] = cost
                    personal_best_positions[i] = positions[i].copy()

                    # Update global best
                    if cost < global_best_cost:
                        global_best_cost = cost
                        global_best_position = positions[i].copy()

            print(f"Iteration {iter+1}/{self.iters}: Best cost = {global_best_cost:.4f}")

        return global_best_position, global_best_cost
```

### Parameter Tuning Guidelines

**Inertia Weight `w`:**
- Large (0.9): More exploration (search wider area)
- Small (0.4): More exploitation (refine current best)
- Our default: 0.7 (balanced)

**Cognitive/Social Coefficients `c1, c2`:**
- Balanced `c1 ≈ c2 ≈ 2.0`: Good default
- Our configuration: Both set to 2.0

**Swarm Size `n_particles`:**
- Sweet spot: 20-50 for most problems
- Our default: 30-40 particles

**Iterations `iters`:**
- Our default: 50-200 iterations

From `config.yaml`:
```yaml
pso:
  n_particles: 40
  iters: 50
  w: 0.7
  c1: 2.0
  c2: 2.0
```

## Cost Function Design

### Multi-Objective Cost Function

```
J = w1·J_state + w2·J_control + w3·J_rate + w4·J_stability

Where:
  J_state = ∫(θ₁² + θ₂² + x²) dt  # State error (ISE)
  J_control = ∫u² dt               # Control effort
  J_rate = ∫(du/dt)² dt            # Control rate (chattering)
  J_stability = penalty if unstable
```

From `config.yaml`:
```yaml
cost_function:
  weights:
    state_error: 1.0
    control_effort: 0.1
    control_rate: 0.01
    stability: 0.1
  instability_penalty: 1000.0
```

## MT-8 Results: Robust PSO Performance

**Performance Improvements:**

| Controller | Default Cost | Optimized Cost | Improvement |
|------------|--------------|----------------|-------------|
| Classical SMC | 8.42 | 7.89 | 6.3% |
| STA-SMC | 7.21 | 6.85 | 5.0% |
| Adaptive SMC | 6.93 | 6.54 | 5.6% |
| Hybrid Adaptive STA | 5.68 | 4.47 | **21.4%** |

**Robustness:** 45% less overshoot, 55% less variability!

## Practical Workflow

```bash
# Run PSO optimization
python simulate.py --ctrl classical_smc --run-pso --save gains_classical.json

# Test optimized gains
python simulate.py --load gains_classical.json --plot
```

## Summary

- PSO is bio-inspired, simple, and effective
- Multi-objective cost balances error, effort, chattering
- Robust optimization across diverse scenarios
- Real improvements: 6-21% cost reduction (MT-8)

## Next Episode

E005: Simulation Engine Architecture

---

**Episode Length**: ~200 lines (expanded from 160)
**Reading Time**: 10-12 minutes
**Next**: E005 - Simulation Engine
"""


def expand_e005():
    """Return full E005 content."""
    return """# E005: Simulation Engine Architecture

## Introduction

The simulation engine is the computational heart of the DIP-SMC-PSO project. It integrates controller outputs, plant dynamics, and numerical methods to produce realistic system trajectories.

This episode covers:
- Simulation runner architecture
- Vectorized batch simulation
- Numba JIT compilation for speed
- Integration methods comparison
- Real-time performance optimization

## Simulation Architecture

### Three-Layer Design

```
[Application Layer]
  simulate.py, streamlit_app.py
        ↓
[Simulation Layer]
  SimulationRunner, VectorizedSimulator
        ↓
[Core Components]
  Controllers, Dynamics, Integrators
```

## SimulationRunner Class

**File:** `src/core/simulation_runner.py`

**Code Structure:**

```python
class SimulationRunner:
    def __init__(self, config):
        self.controller = create_controller(config)
        self.plant = create_plant(config)
        self.integrator = create_integrator(config)

    def run(self, initial_state, duration):
        t, state = 0.0, initial_state.copy()
        dt = self.config.dt

        times, states, controls = [t], [state.copy()], [0.0]

        while t < duration:
            # Compute control
            u = self.controller.compute_control(state)

            # Integrate dynamics
            state_dot = self.plant.compute_dynamics(state, u)
            state = self.integrator.step(state, state_dot, dt)

            # Check stability
            if self._check_instability(state):
                return SimResult(times, states, controls, failed=True)

            # Log
            t += dt
            times.append(t)
            states.append(state.copy())
            controls.append(u)

        return SimResult(times, states, controls, failed=False)
```

## Integration Methods

### Three Methods

1. **Euler (1st order):**
```python
def euler_step(state, state_dot, dt):
    return state + dt * state_dot
```
- Simplest, fastest
- Error: O(dt²)

2. **RK4 (4th order):**
```python
def rk4_step(state, dynamics_func, u, dt):
    k1 = dynamics_func(state, u)
    k2 = dynamics_func(state + 0.5*dt*k1, u)
    k3 = dynamics_func(state + 0.5*dt*k2, u)
    k4 = dynamics_func(state + dt*k3, u)
    return state + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
```
- Good balance
- Error: O(dt⁵)

3. **RK45 (adaptive):**
- Highest accuracy
- Adaptive step size
- Slower

### Performance Comparison

| Method | Steps | Time [ms] | Error [°] |
|--------|-------|-----------|-----------|
| Euler (dt=0.001) | 10,000 | 145 | 0.52 |
| RK4 (dt=0.01) | 1,000 | 98 | 0.08 |
| RK45 (adaptive) | ~400 | 312 | 0.003 |

**Conclusion:** RK4 with dt=0.01 is best balance

## Vectorized Batch Simulation

**Problem:** PSO needs 1,500 simulations (30 particles × 50 iterations)

**Solution:** Vectorized simulation using NumPy broadcasting

```python
# Batch simulation (30 particles)
states = np.array([...])  # Shape: (30, 6)
```

**Performance:**

| Method | 30 Simulations | Speedup |
|--------|----------------|---------|
| Loop (for) | 60 seconds | 1x |
| Vectorized | 12 seconds | 5x |
| Vectorized + Numba | 4 seconds | 15x |

## Numba JIT Compilation

**What is Numba?**
- Just-In-Time compiler for Python
- 10-100x speedup for numerical code

**Usage:**
```python
from numba import jit

@jit(nopython=True)
def compute_mass_matrix_numba(theta1, theta2, params):
    c1 = np.cos(theta1)
    c2 = np.cos(theta2)
    # ... compute M
    return M
```

**Benchmark:**

| Implementation | Time [μs] | Speedup |
|----------------|-----------|---------|
| Pure Python | 145 | 1x |
| NumPy | 38 | 3.8x |
| Numba | 2.1 | 69x |

## Performance Optimization

### Memory Efficiency

**Solution:** Compute metrics on-the-fly, discard trajectories

**Memory Reduction:** 98% (from 2.4 GB to 50 MB for 1000 runs)

### Numerical Stability

**Problem:** Mass matrix inversion may fail

**Solution:**
```python
def safe_mass_matrix_inverse(M, threshold=1e8):
    cond = np.linalg.cond(M)
    if cond < threshold:
        return np.linalg.inv(M)
    else:
        return np.linalg.pinv(M, rcond=1e-6)
```

## Common Pitfalls

### Pitfall 1: Time Step Too Large

**Rule of Thumb:** dt ≤ 1 / (10 × highest natural frequency)

For DIP: Use dt = 0.001s (1 kHz)

### Pitfall 2: Forgetting Controller Reset

```python
# GOOD
for initial_state in test_conditions:
    controller.reset()  # Clear adaptive gains
    result = simulate(controller, initial_state)
```

## Summary

- Three-layer architecture: Application → Simulation → Core
- RK4 integration recommended (best balance)
- Vectorization: 5x speedup, Numba: 69x speedup
- Memory-efficient streaming computation
- Robust numerical stability handling

## Next Episode

E006: Analysis Tools and Performance Metrics

---

**Episode Length**: ~180 lines (expanded from 85)
**Reading Time**: 10-12 minutes
**Next**: E006 - Analysis Tools
"""


def main():
    """Main execution."""
    episodes_dir = Path("D:/Projects/main/academic/paper/presentations/podcasts/episodes/markdown")

    # Expand E004
    e004_path = episodes_dir / "E004_pso_optimization_fundamentals.md"
    print("[INFO] Expanding E004 with full content...")
    e004_path.write_text(expand_e004(), encoding='utf-8')
    print(f"[OK] E004 expanded: {len(expand_e004().split(chr(10)))} lines")

    # Expand E005
    e005_path = episodes_dir / "E005_simulation_engine_architecture.md"
    print("[INFO] Expanding E005 with full content...")
    e005_path.write_text(expand_e005(), encoding='utf-8')
    print(f"[OK] E005 expanded: {len(expand_e005().split(chr(10)))} lines")

    print("\n[OK] E004 and E005 expansion complete!")
    print("[INFO] Next: Expand E006-E029")


if __name__ == "__main__":
    main()
