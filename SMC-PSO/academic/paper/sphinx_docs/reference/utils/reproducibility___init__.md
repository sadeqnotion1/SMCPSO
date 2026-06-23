# utils.reproducibility.__init__

**Source:** `src\utils\reproducibility\__init__.py`

## Module Overview

Reproducibility utilities for control engineering experiments.

This package provides tools for managing random seeds and ensuring
reproducible results across experiments and simulations.

## Complete Source Code

```{literalinclude} ../../../src/utils/reproducibility/__init__.py
:language: python
:linenos:
```



## Functions

### `with_seed(seed)`

Dummy function for backward compatibility.

#### Source Code

```{literalinclude} ../../../src/utils/reproducibility/__init__.py
:language: python
:pyobject: with_seed
:linenos:
```



### `random_seed_context(seed)`

Dummy context manager for backward compatibility.

#### Source Code

```{literalinclude} ../../../src/utils/reproducibility/__init__.py
:language: python
:pyobject: random_seed_context
:linenos:
```



## Dependencies

This module imports:

- `from .seed import set_global_seed, SeedManager, create_rng`


## Advanced Mathematical Theory

### Reproducibility Theory

Scientific reproducibility requires deterministic algorithms and proper random seed management.

#### Pseudo-Random Number Generation

**Linear Congruential Generator (LCG):**
$$
X_{n+1} = (a X_n + c) \mod m
$$

**Mersenne Twister** (period $2^{19937} - 1$):
$$
X_{n+k} = X_n \oplus (X_n \gg u) \oplus ((X_n \ll s) \wedge b)
$$

**Seed determines entire sequence:**
$$
\text{seed} \rightarrow \{X_0, X_1, X_2, \ldots\}
$$

**Reproducibility guarantee:**
$$
\text{seed}_A = \text{seed}_B \Rightarrow \text{sequence}_A = \text{sequence}_B
$$

#### Hash-Based Seeding

**Combine multiple seed sources:**
$$
\text{seed}_{\text{combined}} = \text{hash}(\text{seed}_{\text{base}} \| \text{pid} \| \text{time} \| \text{counter})
$$

**SHA-256 hash truncation:**
$$
\text{seed} = \text{SHA-256}(\text{input}) \mod 2^{32}
$$

#### Statistical Reproducibility

**Mean convergence** (Law of Large Numbers):
$$
\lim_{n \to \infty} \frac{1}{n} \sum_{i=1}^n X_i = \mu
$$

**Distribution convergence** (Central Limit Theorem):
$$
\frac{\bar{X}_n - \mu}{\sigma / \sqrt{n}} \xrightarrow{d} \mathcal{N}(0, 1)
$$

**Monte Carlo reproducibility:**
$$
\text{Same seed} \Rightarrow \text{Same } \{X_i\}_{i=1}^N \Rightarrow \text{Same } \bar{X}_N
$$

#### Entropy Sources

**System entropy:**
$$
E_{\text{system}} = \text{time}() + \text{pid}() + \text{counter}
$$

**User-provided seed:**
$$
E_{\text{user}} = \text{integer in } [0, 2^{32} - 1]
$$

**Combined entropy:**
$$
\text{seed} = \text{combine}(E_{\text{user}}, E_{\text{system}})
$$

## Architecture Diagram

```{mermaid}
graph TD
    A[Reproducibility System] --> B[Seed Management]
    A --> C[PRNG Initialization]
    A --> D[State Capture]

    B --> E{Seed Source}
    E -->|User-Provided| F[Fixed Seed]
    E -->|System-Generated| G[Entropy Pool]

    F --> H[Hash Combination]
    G --> H

    H --> I[Initialize PRNG]
    I --> J[NumPy Generator]
    I --> K[Python random]

    J --> L[Generate Sequence]
    K --> L

    L --> M{Reproducibility Check}
    M -->|Same Seed| N[Same Sequence ✓]
    M -->|Different Seed| O[Different Sequence]

    D --> P[Save State]
    P --> Q[JSON Snapshot]
    Q --> R[Restore State]
    R --> I

    style E fill:#fff4e1
    style M fill:#fff4e1
    style N fill:#e8f5e9
```

## Usage Examples

### Example 1: Basic Seed Setting

```python
from src.utils.reproducibility import set_seed
import numpy as np

# Set global seed for reproducibility
set_seed(42)

# Generate random numbers
random_values_1 = np.random.randn(10)

# Reset seed - get same sequence
set_seed(42)
random_values_2 = np.random.randn(10)

# Verify reproducibility
assert np.allclose(random_values_1, random_values_2)
print("✓ Reproducibility verified")
```

## Example 2: Monte Carlo with Reproducibility

```python
from src.utils.reproducibility import set_seed
import numpy as np

def monte_carlo_simulation(n_trials: int, seed: int):
    # Set seed for reproducible Monte Carlo
    set_seed(seed)

    results = []
    for i in range(n_trials):
        # Simulate with random initial conditions
        x0 = np.random.randn(6) * 0.1
        result = run_simulation(x0)
        results.append(result)

    return np.mean(results), np.std(results)

# Run twice with

same seed - get identical results
mean1, std1 = monte_carlo_simulation(1000, seed=42)
mean2, std2 = monte_carlo_simulation(1000, seed=42)

assert mean1 == mean2 and std1 == std2
print("✓ Monte Carlo reproducibility confirmed")
```

## Example 3: PSO Optimization Reproducibility

```python
from src.utils.reproducibility import set_seed
from src.optimizer import PSOTuner

def reproducible_pso_tuning(seed: int):
    # Set seed before PSO initialization
    set_seed(seed)

    # Create PSO tuner
    tuner = PSOTuner(
        n_particles=30,
        iters=100,
        bounds=[(0.1, 50.0)] * 6
    )

    # Optimize (deterministic with fixed seed)
    best_gains, best_fitness = tuner.optimize(fitness_function)

    return best_gains

# Verify PSO reproducibility
gains_run1 = reproducible_pso_tuning(seed=123)
gains_run2 = reproducible_pso_tuning(seed=123)

assert np.allclose(gains_run1, gains_run2)
print("✓ PSO optimization is reproducible")
```

## Example 4: State Capture and Restore

```python
from src.utils.reproducibility import capture_random_state, restore_random_state
import numpy as np

# Generate some random numbers
set_seed(42)
values_before = np.random.randn(5)

# Capture current RNG state
state = capture_random_state()

# Generate more numbers (changes state)
np.random.randn(100)

# Restore previous state
restore_random_state(state)

# Continue from captured state
values_after = np.random.randn(5)

# Should match continuation from before
print("State restoration allows sequence continuation")
```

## Example 5: Experiment Reproducibility Framework

```python
from src.utils.reproducibility import set_seed, capture_random_state
import json
from pathlib import Path

class ReproducibleExperiment:
    def __init__(self, name: str, seed: int):
        self.name = name
        self.seed = seed
        set_seed(seed)
        self.initial_state = capture_random_state()

    def run(self):
        # Restore initial state for clean run
        restore_random_state(self.initial_state)

        # Run experiment
        results = self.execute_experiment()

        # Save results with metadata
        self.save_results(results)

        return results

    def save_results(self, results):
        metadata = {
            'experiment': self.name,
            'seed': self.seed,
            'results': results
        }

        Path('results').mkdir(exist_ok=True)
        with open(f'results/{self.name}_seed{self.seed}.json', 'w') as f:
            json.dump(metadata, f, indent=2)

# Run reproducible experiment
exp = ReproducibleExperiment("controller_comparison", seed=42)
results = exp.run()

# Re-run with same

seed - identical results guaranteed
exp2 = ReproducibleExperiment("controller_comparison", seed=42)
results2 = exp2.run()

assert results == results2
print("✓ Full experiment reproducibility achieved")
```
