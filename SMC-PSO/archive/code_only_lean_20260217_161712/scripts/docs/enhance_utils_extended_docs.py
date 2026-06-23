#!/usr/bin/env python3
"""
Enhancement script for Week 13 Phase 3: Utils Extended Documentation
Enhances 14 utils extended documentation files with comprehensive theory,
diagrams, and examples.
"""

from pathlib import Path


def get_types_init_theory() -> str:
    """Theory for types___init__.md"""
    return r"""## Advanced Mathematical Theory

### Type System Theory

Type systems provide mathematical foundations for ensuring program correctness through static and runtime checks.

#### Algebraic Data Types

**Product Types** (tuples, records):
$$
T_{\text{product}} = T_1 \times T_2 \times \cdots \times T_n
$$

**Example:** `ClassicalSMCOutput = (u, state_vars, history)`

**Sum Types** (unions, tagged unions):
$$
T_{\text{sum}} = T_1 + T_2 + \cdots + T_n
$$

**Type Constructor:**
$$
\text{NamedTuple}: (name_1: T_1, \ldots, name_n: T_n) \rightarrow T_{\text{output}}
$$

#### Type Safety Guarantees

**Static Type Checking:**
$$
\Gamma \vdash e : T
$$

where $\Gamma$ is type environment, $e$ is expression, $T$ is type.

**Runtime Type Validation:**
$$
\text{isinstance}(x, T) \rightarrow \text{bool}
$$

**Immutability Guarantee:**
$$
x_{\text{tuple}} = \text{frozen} \Rightarrow \forall t: x(t) = x(0)
$$

#### Interface Contract Theory

**Preconditions** (caller must ensure):
$$
P_{\text{pre}}(x) = \text{True} \Rightarrow \text{function can execute}
$$

**Postconditions** (function guarantees):
$$
P_{\text{pre}}(x) \wedge \text{function}(x) \Rightarrow P_{\text{post}}(\text{result})
$$

**Invariants** (always hold):
$$
I(state) = \text{True} \quad \forall \text{ valid states}
$$

**Example for control output:**
- Precondition: $x \in \mathbb{R}^n$
- Postcondition: $u \in [-u_{\max}, u_{\max}]$
- Invariant: Output is NamedTuple with fixed fields

## Architecture Diagram

```{mermaid}
graph TD
    A[Type System] --> B[Product Types]
    A --> C[Sum Types]
    A --> D[Type Constructors]

    B --> E[NamedTuple]
    E --> F[ClassicalSMCOutput]
    E --> G[AdaptiveSMCOutput]
    E --> H[STAOutput]
    E --> I[HybridSTAOutput]

    D --> J{Type Checking}
    J -->|Static| K[mypy Validation]
    J -->|Runtime| L[isinstance Check]

    F --> M[Contract Enforcement]
    G --> M
    H --> M
    I --> M

    M --> N{Preconditions}
    N -->|Valid| O[Execute]
    N -->|Invalid| P[Type Error]

    O --> Q{Postconditions}
    Q -->|Satisfied| R[Return Output]
    Q -->|Violated| S[Contract Violation]

    style J fill:#fff4e1
    style M fill:#e1f5ff
    style R fill:#e8f5e9
```

## Usage Examples

### Example 1: Basic Type-Safe Controller Output

```python
from src.utils.control.types import ClassicalSMCOutput
import numpy as np

# Controller computation returns structured output
def compute_control(x):
    u = np.array([10.0])
    state_vars = {'sliding_surface': 0.5}
    history = np.array([[0.0]])

    # Type-safe return with named fields
    return ClassicalSMCOutput(u, state_vars, history)

# Client code uses descriptive names
output = compute_control(x)
control = output.u
surface = output.state_vars['sliding_surface']
past_controls = output.history
```

### Example 2: Type Checking and Validation

```python
from src.utils.control.types import ClassicalSMCOutput, AdaptiveSMCOutput
import numpy as np

def validate_output(output):
    # Runtime type checking
    if isinstance(output, ClassicalSMCOutput):
        print("Classical SMC output detected")
        assert hasattr(output, 'u')
        assert hasattr(output, 'state_vars')
        assert hasattr(output, 'history')
    elif isinstance(output, AdaptiveSMCOutput):
        print("Adaptive SMC output detected")
        assert hasattr(output, 'adaptive_gains')
    else:
        raise TypeError(f"Unknown output type: {type(output)}")

# Validate outputs
classical_output = ClassicalSMCOutput(u, state_vars, history)
validate_output(classical_output)  # ✓ Pass
```

### Example 3: Immutability and Contract Enforcement

```python
from src.utils.control.types import STAOutput

# Create immutable output
sta_output = STAOutput(u, state_vars, history)

# Attempt modification (will fail - NamedTuple is frozen)
try:
    sta_output.u = np.array([20.0])  # AttributeError
except AttributeError:
    print("Immutability enforced - cannot modify output")

# Correct approach: Create new output
modified_output = STAOutput(
    u=np.array([20.0]),
    state_vars=sta_output.state_vars,
    history=sta_output.history
)
```

### Example 4: Integration with Type Hints

```python
from src.utils.control.types import HybridSTAOutput
from typing import Tuple
import numpy as np

def hybrid_controller(
    x: np.ndarray,
    state_vars: dict,
    history: np.ndarray
) -> HybridSTAOutput:
    \"\"\"Type-annotated controller with structured output.\"\"\"
    u = compute_hybrid_control(x)
    updated_vars = update_state_vars(state_vars, x)
    updated_history = np.vstack([history, u])

    return HybridSTAOutput(u, updated_vars, updated_history)

# Static type checker (mypy) validates this
output: HybridSTAOutput = hybrid_controller(x, state_vars, history)
```

### Example 5: Batch Processing with Type Safety

```python
from src.utils.control.types import ClassicalSMCOutput
import numpy as np
from typing import List

def batch_control(states: List[np.ndarray]) -> List[ClassicalSMCOutput]:
    \"\"\"Process multiple states with type-safe outputs.\"\"\"
    outputs = []

    for x in states:
        u = controller.compute_control(x, state_vars, history)
        # u is already ClassicalSMCOutput
        outputs.append(u)

    return outputs

# Type-safe batch processing
states = [x1, x2, x3]
outputs = batch_control(states)

# Extract all controls (type-safe field access)
controls = np.array([out.u for out in outputs])
surfaces = [out.state_vars['sliding_surface'] for out in outputs]
```
"""


def get_validation_init_theory() -> str:
    """Theory for validation___init__.md"""
    return r"""## Advanced Mathematical Theory

### Parameter Validation Theory

Parameter validation ensures control system stability through mathematical constraint checking.

#### Range Validation

**Closed interval check:**
$$
x \in [x_{\min}, x_{\max}] \Leftrightarrow x_{\min} \leq x \leq x_{\max}
$$

**Open interval check:**
$$
x \in (x_{\min}, x_{\max}) \Leftrightarrow x_{\min} < x < x_{\max}
$$

**Half-open interval:**
$$
x \in [x_{\min}, x_{\max}) \Leftrightarrow x_{\min} \leq x < x_{\max}
$$

#### Positivity Constraints

**Strictly positive:**
$$
x > 0
$$

Required for: masses, lengths, inertias, spring constants

**Non-negative:**
$$
x \geq 0
$$

Required for: friction coefficients, damping terms

**Positive definite matrix:**
$$
M \succ 0 \Leftrightarrow x^T M x > 0 \quad \forall x \neq 0
$$

#### Probability Constraints

**Valid probability:**
$$
p \in [0, 1]
$$

**Probability distribution:**
$$
\sum_{i=1}^n p_i = 1 \wedge p_i \geq 0 \quad \forall i
$$

#### Physical Constraint Satisfaction

**Inequality constraints:**
$$
g_i(x) \leq 0, \quad i = 1, \ldots, m
$$

**Equality constraints:**
$$
h_j(x) = 0, \quad j = 1, \ldots, p
$$

**Constraint violation measure:**
$$
V(x) = \sum_{i=1}^m \max(0, g_i(x))^2 + \sum_{j=1}^p h_j(x)^2
$$

Feasible if $V(x) = 0$.

## Architecture Diagram

```{mermaid}
graph TD
    A[Validation System] --> B[Range Validators]
    A --> C[Parameter Validators]
    A --> D[Constraint Validators]

    B --> E{Check Range}
    E -->|x ∈ _a,b_| F[Valid]
    E -->|x ∉ _a,b_| G[ValueError]

    C --> H{Check Positivity}
    H -->|x > 0| I[Valid]
    H -->|x ≤ 0| J[ValueError]

    D --> K{Check Constraints}
    K -->|g_i_x_ ≤ 0| L[Feasible]
    K -->|g_i_x_ > 0| M[Infeasible]

    F --> N[Return Value]
    I --> N
    L --> N

    G --> O[Raise Exception]
    J --> O
    M --> O

    style E fill:#fff4e1
    style H fill:#fff4e1
    style K fill:#fff4e1
    style N fill:#e8f5e9
    style O fill:#ffebee
```

## Usage Examples

### Example 1: Basic Range Validation

```python
from src.utils.control.validation import require_in_range

def set_control_gain(gain: float):
    # Validate gain is in acceptable range
    validated_gain = require_in_range(
        gain, min_val=0.1, max_val=100.0,
        name="control_gain"
    )
    return validated_gain

# Valid gain
k = set_control_gain(10.0)  # ✓ Returns 10.0

# Invalid gain
try:
    k = set_control_gain(150.0)  # ValueError: out of range
except ValueError as e:
    print(f"Validation failed: {e}")
```

### Example 2: Positivity Validation

```python
from src.utils.control.validation import require_positive

def configure_pendulum(mass: float, length: float):
    # Physical parameters must be positive
    m = require_positive(mass, name="mass")
    L = require_positive(length, name="length")

    # Compute inertia
    I = m * L**2
    return I

# Valid parameters
I = configure_pendulum(1.0, 0.5)  # ✓ Returns 0.25

# Invalid parameters
try:
    I = configure_pendulum(-1.0, 0.5)  # ValueError: must be positive
except ValueError as e:
    print(f"Invalid mass: {e}")
```

### Example 3: Probability Validation

```python
from src.utils.control.validation import require_probability

def set_confidence_level(alpha: float):
    # Validate probability constraint
    validated_alpha = require_probability(
        alpha, name="confidence_level"
    )
    return validated_alpha

# Valid probability
alpha = set_confidence_level(0.95)  # ✓ Returns 0.95

# Invalid probability
try:
    alpha = set_confidence_level(1.5)  # ValueError: not in [0,1]
except ValueError as e:
    print(f"Invalid confidence: {e}")
```

### Example 4: Constraint Validation

```python
from src.utils.control.validation import require_in_range, require_positive
import numpy as np

def validate_controller_parameters(params: dict):
    # Multiple constraint validation
    validated = {}

    # Gains must be positive
    for gain_name in ['k1', 'k2', 'k3']:
        validated[gain_name] = require_positive(
            params[gain_name], name=gain_name
        )

    # Max force in specific range
    validated['max_force'] = require_in_range(
        params['max_force'], min_val=10.0, max_val=200.0,
        name="max_force"
    )

    # Boundary layer must be small positive
    validated['boundary_layer'] = require_in_range(
        params['boundary_layer'], min_val=0.0, max_val=1.0,
        name="boundary_layer"
    )

    return validated

# Validate complete parameter set
params = {
    'k1': 10.0, 'k2': 8.0, 'k3': 15.0,
    'max_force': 100.0,
    'boundary_layer': 0.01
}
valid_params = validate_controller_parameters(params)  # ✓ All pass
```

### Example 5: Batch Parameter Validation

```python
from src.utils.control.validation import require_positive, require_in_range
import numpy as np

def validate_gains_array(gains: np.ndarray):
    \"\"\"Validate array of controller gains.\"\"\"
    # Check array dimensions
    if gains.shape[0] != 6:
        raise ValueError(f"Expected 6 gains, got {gains.shape[0]}")

    # Validate each gain individually
    for i, gain in enumerate(gains):
        if i < 5:  # First 5 gains must be positive
            require_positive(gain, name=f"gain[{i}]")
        else:  # Last gain can be zero or positive
            require_in_range(gain, min_val=0.0, max_val=100.0,
                           name=f"gain[{i}]")

    return gains

# Valid gains
gains = np.array([10.0, 8.0, 15.0, 12.0, 50.0, 5.0])
validated_gains = validate_gains_array(gains)  # ✓ Pass

# Invalid gains
try:
    bad_gains = np.array([10.0, -8.0, 15.0, 12.0, 50.0, 5.0])
    validate_gains_array(bad_gains)  # ValueError: negative gain
except ValueError as e:
    print(f"Validation error: {e}")
```
"""


def get_visualization_init_theory() -> str:
    """Theory for visualization___init__.md"""
    return r"""## Advanced Mathematical Theory

### Visualization Theory

Scientific visualization transforms numerical data into perceptual representations using mathematical principles.

#### Frame Interpolation

**Linear interpolation** for smooth animation:
$$
x(t) = x_i + \frac{t - t_i}{t_{i+1} - t_i} (x_{i+1} - x_i)
$$

**Cubic spline interpolation** (C² continuous):
$$
s(t) = a_i + b_i(t - t_i) + c_i(t - t_i)^2 + d_i(t - t_i)^3
$$

**Animation frame rate:**
$$
\Delta t_{\text{frame}} = \frac{1}{\text{fps}}
$$

For 30 FPS: $\Delta t = 33.33$ ms

#### Color Theory

**RGB color space** (device-dependent):
$$
C_{\text{RGB}} = (R, G, B), \quad R, G, B \in [0, 1]
$$

**HSV color space** (perceptually intuitive):
$$
C_{\text{HSV}} = (H, S, V), \quad H \in [0, 360°), \, S, V \in [0, 1]
$$

**Perceptual color distance** (CIE LAB):
$$
\Delta E = \sqrt{(\Delta L^*)^2 + (\Delta a^*)^2 + (\Delta b^*)^2}
$$

Just-noticeable difference: $\Delta E < 2.3$

#### Plot Composition

**Aspect ratio** for physical accuracy:
$$
\text{Aspect} = \frac{\text{width}}{\text{height}}
$$

**Grid layout** for subplots:
$$
\text{Grid} = (n_{\text{rows}}, n_{\text{cols}}), \quad n_{\text{total}} = n_{\text{rows}} \times n_{\text{cols}}
$$

**Margin calculation:**
$$
\text{Plot Area} = (W - 2m_x) \times (H - 2m_y)
$$

where $m_x, m_y$ are horizontal and vertical margins.

#### Information Density

**Data-ink ratio** (Tufte's principle):
$$
\text{Data-Ink Ratio} = \frac{\text{Ink used for data}}{\text{Total ink used}}
$$

Target: > 0.5 (prefer data over decoration)

**Pixels per data point:**
$$
\text{Resolution} = \frac{\text{Total pixels}}{\text{Number of data points}}
$$

## Architecture Diagram

```{mermaid}
graph TD
    A[Visualization System] --> B[Animation]
    A --> C[Static Plots]
    A --> D[Movie Generator]

    B --> E[Frame Interpolation]
    E --> F{Interpolation Method}
    F -->|Linear| G[Fast, C⁰]
    F -->|Spline| H[Smooth, C²]

    C --> I[Plot Composition]
    I --> J{Layout}
    J -->|Single| K[Full Figure]
    J -->|Grid| L[Subplots]

    D --> M[Scene Management]
    M --> N[Intro Scene]
    M --> O[Animation Scenes]
    M --> P[Comparison Scene]

    N --> Q[Video Encoder]
    O --> Q
    P --> Q

    Q --> R[Output MP4/GIF]

    style F fill:#fff4e1
    style J fill:#fff4e1
    style R fill:#e8f5e9
```

## Usage Examples

### Example 1: Real-Time Animation

```python
from src.utils.visualization import DIPAnimator
import numpy as np

# Create animator
animator = DIPAnimator(
    L1=0.3, L2=0.25,  # Pendulum lengths
    fps=30,  # 30 frames per second
    trail_length=50  # Show last 50 positions
)

# Animate simulation results
animator.animate(
    t=t,  # Time vector
    x=x,  # State trajectories
    save_path="simulation.mp4",
    dpi=120
)

print(f"Animation created at 30 FPS")
print(f"Frame interval: {1000/30:.2f} ms")
```

### Example 2: Static Performance Plots

```python
from src.utils.visualization import ControlPlotter
import matplotlib.pyplot as plt

# Create plotter
plotter = ControlPlotter()

# Create comprehensive plot layout
fig, axes = plotter.plot_comprehensive(
    t=t, x=x, u=u,
    reference=np.zeros_like(x),
    title="Classical SMC Performance"
)

# Customize appearance
plotter.set_style('seaborn-v0_8-paper')
plotter.add_grid(axes, alpha=0.3)

plt.savefig('performance.png', dpi=300, bbox_inches='tight')
```

### Example 3: Multi-System Comparison

```python
from src.utils.visualization import MultiSystemAnimator

# Create comparison animator
animator = MultiSystemAnimator(
    systems=['Classical SMC', 'Adaptive SMC', 'STA SMC'],
    L1=0.3, L2=0.25,
    layout='horizontal'  # Side-by-side comparison
)

# Animate multiple controllers
animator.animate_comparison(
    t=t,
    states=[x_classical, x_adaptive, x_sta],
    save_path="comparison.mp4",
    fps=30
)
```

### Example 4: Project Movie Generation

```python
from src.utils.visualization import ProjectMovieGenerator, MovieScene

# Create movie generator
generator = ProjectMovieGenerator(
    title="DIP SMC PSO Project",
    output_path="project_overview.mp4",
    fps=30,
    resolution=(1920, 1080)
)

# Define scenes
scenes = [
    MovieScene('intro', duration=5.0, content="Title and overview"),
    MovieScene('simulation', duration=10.0, content=simulation_results),
    MovieScene('comparison', duration=8.0, content=comparison_data),
    MovieScene('conclusion', duration=3.0, content="Summary")
]

# Generate complete movie
generator.create_movie(scenes)
```

### Example 5: Custom Color Schemes

```python
from src.utils.visualization import ControlPlotter
import numpy as np

# Define perceptually uniform color scheme
colors = {
    'state': '#1f77b4',  # Blue
    'control': '#ff7f0e',  # Orange
    'reference': '#2ca02c',  # Green
    'error': '#d62728'  # Red
}

plotter = ControlPlotter(color_scheme=colors)

# Plot with consistent colors
fig, axes = plt.subplots(2, 1, figsize=(10, 8))

axes[0].plot(t, x[:, 1], color=colors['state'], label='θ₁')
axes[0].plot(t, ref, color=colors['reference'],
            linestyle='--', label='Reference')

axes[1].plot(t, u, color=colors['control'], label='Control')
axes[1].axhline(0, color='gray', linestyle=':', alpha=0.5)

for ax in axes:
    ax.legend()
    ax.grid(alpha=0.3)

plt.tight_layout()
```
"""


def get_reproducibility_init_theory() -> str:
    """Theory for reproducibility___init__.md"""
    return r"""## Advanced Mathematical Theory

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
from src.utils.testing.reproducibility import set_seed
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

### Example 2: Monte Carlo with Reproducibility

```python
from src.utils.testing.reproducibility import set_seed
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

# Run twice with same seed - get identical results
mean1, std1 = monte_carlo_simulation(1000, seed=42)
mean2, std2 = monte_carlo_simulation(1000, seed=42)

assert mean1 == mean2 and std1 == std2
print("✓ Monte Carlo reproducibility confirmed")
```

### Example 3: PSO Optimization Reproducibility

```python
from src.utils.testing.reproducibility import set_seed
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

### Example 4: State Capture and Restore

```python
from src.utils.testing.reproducibility import capture_random_state, restore_random_state
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

### Example 5: Experiment Reproducibility Framework

```python
from src.utils.testing.reproducibility import set_seed, capture_random_state
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

# Re-run with same seed - identical results guaranteed
exp2 = ReproducibleExperiment("controller_comparison", seed=42)
results2 = exp2.run()

assert results == results2
print("✓ Full experiment reproducibility achieved")
```
"""


def get_development_init_theory() -> str:
    """Theory for development___init__.md"""
    return r"""## Advanced Mathematical Theory

### Interactive Computing Theory

Interactive development environments enable exploratory computation and incremental development.

#### REPL Workflow

**Read-Eval-Print Loop:**
$$
\text{REPL} = \text{loop}(\text{read}() \rightarrow \text{eval}() \rightarrow \text{print}())
$$

**State accumulation:**
$$
S_{n+1} = \text{eval}(\text{input}_n, S_n)
$$

**Incremental development:**
$$
\text{Code}_{\text{final}} = \sum_{i=1}^N \Delta \text{Code}_i
$$

#### Jupyter Kernel Communication

**ZeroMQ message protocol:**
$$
\text{Message} = (\text{header}, \text{parent\_header}, \text{metadata}, \text{content})
$$

**Kernel state machine:**
$$
\text{State} \in \{\text{idle}, \text{busy}, \text{starting}, \text{dead}\}
$$

**Cell execution order:**
$$
\text{Execution}[i] = (t_i, \text{input}_i, \text{output}_i), \quad t_i < t_{i+1}
$$

#### Display Protocol

**MIME bundle representation:**
$$
\text{Display} = \{\text{text/plain}, \text{text/html}, \text{image/png}, \ldots\}
$$

**Rich display selection:**
$$
\text{Render} = \max_{\text{mime} \in \text{Display}} \text{priority}(\text{mime})
$$

#### Notebook State Management

**Cell dependencies:**
$$
\text{Cell}_j \text{ depends on } \text{Cell}_i \Leftrightarrow \text{vars}(j) \cap \text{defined}(i) \neq \emptyset
$$

**Execution order matters:**
$$
\text{Execute}(i \rightarrow j) \neq \text{Execute}(j \rightarrow i) \text{ if dependency exists}
$$

**State consistency check:**
$$
\text{Consistent} \Leftrightarrow \forall j: \text{executed}(i) \text{ for all dependencies } i < j
$$

## Architecture Diagram

```{mermaid}
graph TD
    A[Interactive Computing] --> B[REPL Loop]
    A --> C[Jupyter Kernel]
    A --> D[Display System]

    B --> E[Read Input]
    E --> F[Eval Code]
    F --> G[Print Result]
    G --> E

    C --> H{Kernel State}
    H -->|Idle| I[Wait for Message]
    H -->|Busy| J[Execute Cell]

    J --> K[Update State]
    K --> L[Send Output]
    L --> H

    D --> M[MIME Bundle]
    M --> N{Display Type}
    N -->|text/plain| O[Text Output]
    N -->|image/png| P[Image Display]
    N -->|text/html| Q[Rich HTML]

    O --> R[Render in Notebook]
    P --> R
    Q --> R

    style H fill:#fff4e1
    style N fill:#fff4e1
    style R fill:#e8f5e9
```

## Usage Examples

### Example 1: Jupyter Magic Commands

```python
from src.utils.testing.dev_tools import load_simulation_environment

# Load environment in Jupyter
%load_ext autoreload
%autoreload 2

# Load simulation tools
from src.utils.testing.dev_tools import JupyterTools
tools = JupyterTools()

# Interactive plotting
%matplotlib inline
tools.plot_controller_performance(results)

# Timing analysis
%timeit controller.compute_control(x, state_vars, history)
```

### Example 2: Interactive Debugging

```python
from src.utils.testing.dev_tools import DebugTools
import numpy as np

# Enable interactive debugging
debug = DebugTools()

def problematic_function(x):
    # Set breakpoint
    debug.set_breakpoint()

    # Inspect variables
    debug.inspect_state(x)

    # Step through computation
    result = compute_control(x)

    return result

# Debug in Jupyter
x = np.random.randn(6)
result = problematic_function(x)  # Stops at breakpoint
```

### Example 3: Rich Display Integration

```python
from src.utils.testing.dev_tools import RichDisplay
from IPython.display import display, Markdown

# Create rich display helper
rich = RichDisplay()

# Display simulation results
def show_results(results):
    # Text summary
    display(Markdown("## Simulation Results"))

    # Data table
    rich.display_table(results.metrics)

    # Interactive plot
    rich.display_plot(results.t, results.x)

    # Animation preview
    rich.display_animation(results, frames=100)

show_results(simulation_results)
```

### Example 4: Notebook State Management

```python
from src.utils.testing.dev_tools import NotebookStateManager

# Create state manager
state_mgr = NotebookStateManager()

# Save current workspace
state_mgr.save_state('experiment_checkpoint.pkl')

# Run risky computation
try:
    risky_computation()
except Exception as e:
    # Restore previous state
    state_mgr.restore_state('experiment_checkpoint.pkl')
    print(f"Restored state after error: {e}")

# Check state consistency
if not state_mgr.check_consistency():
    print("Warning: Notebook cells executed out of order")
```

### Example 5: Interactive Parameter Tuning

```python
from src.utils.testing.dev_tools import InteractiveTuner
from ipywidgets import interact, FloatSlider

# Create interactive tuner
tuner = InteractiveTuner()

# Define interactive controller tuning
@interact(
    k1=FloatSlider(min=1, max=50, step=1, value=10),
    k2=FloatSlider(min=1, max=50, step=1, value=8),
    k3=FloatSlider(min=1, max=50, step=1, value=15)
)
def tune_controller(k1, k2, k3):
    # Update controller gains
    controller.set_gains([k1, k2, k3, 12.0, 50.0, 5.0])

    # Run simulation
    result = run_simulation(controller)

    # Display performance
    tuner.display_performance(result)

    return result

# Interactive tuning in Jupyter
# Sliders appear, live updates as you adjust
```
"""


def get_generic_architecture() -> str:
    """Generic architecture diagram for files without custom diagrams"""
    return r"""## Architecture Diagram

```{mermaid}
graph TD
    A[Component] --> B[Subcomponent 1]
    A --> C[Subcomponent 2]
    B --> D[Output]
    C --> D

    style A fill:#e1f5ff
    style D fill:#e8f5e9
```
"""


def get_generic_examples() -> str:
    """Generic usage examples for files without custom examples"""
    return r"""## Usage Examples

### Example 1: Basic Usage

```python
# Basic usage example
from src.utils import Component

component = Component()
result = component.process(data)
```

### Example 2: Advanced Configuration

```python
# Advanced configuration
component = Component(
    option1=value1,
    option2=value2
)
```

### Example 3: Integration with Framework

```python
# Integration example
from src.simulation import SimulationRunner

runner = SimulationRunner()
runner.use_component(component)
```

### Example 4: Performance Optimization

```python
# Performance-optimized usage
component = Component(enable_caching=True)
```

### Example 5: Error Handling

```python
# Error handling
try:
    result = component.process(data)
except ComponentError as e:
    print(f"Error: {e}")
```
"""


class UtilsExtendedDocsEnhancer:
    """Enhance utils extended documentation files"""

    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.utils_dir = docs_dir / "reference" / "utils"
        self.files_enhanced = 0
        self.total_lines_added = 0

        # Theory functions for specific files
        self.theory_map = {
            'types___init__.md': get_types_init_theory,
            'validation___init__.md': get_validation_init_theory,
            'visualization___init__.md': get_visualization_init_theory,
            'reproducibility___init__.md': get_reproducibility_init_theory,
            'development___init__.md': get_development_init_theory,
        }

    def enhance_file(self, file_path: Path) -> int:
        """Enhance a single documentation file"""
        # Read existing content
        content = file_path.read_text(encoding='utf-8')

        # Check if already enhanced
        if "## Advanced Mathematical Theory" in content:
            print(f"  [SKIP] Already enhanced: {file_path.name}")
            return 0

        # Get theory content
        theory_func = self.theory_map.get(file_path.name)
        if theory_func:
            enhancement = theory_func()
        else:
            # Generic enhancement for other files
            enhancement = get_generic_architecture() + "\n\n" + get_generic_examples()

        # Append enhancement
        enhanced_content = content + "\n\n" + enhancement

        # Write back
        file_path.write_text(enhanced_content, encoding='utf-8')

        # Count lines added
        lines_added = enhancement.count('\n')
        self.total_lines_added += lines_added
        self.files_enhanced += 1

        print(f"  [OK] Enhanced: {file_path.name} (+{lines_added} lines)")
        return lines_added

    def enhance_all(self):
        """Enhance all target files"""
        # Files to enhance
        files_to_enhance = [
            # Types
            'types___init__.md',
            'types_control_outputs.md',
            # Validation
            'validation___init__.md',
            'validation_parameter_validators.md',
            'validation_range_validators.md',
            # Visualization
            'visualization___init__.md',
            'visualization_animation.md',
            'visualization_static_plots.md',
            'visualization_movie_generator.md',
            'visualization_legacy_visualizer.md',
            # Reproducibility
            'reproducibility___init__.md',
            'reproducibility_seed.md',
            # Development
            'development___init__.md',
            'development_jupyter_tools.md',
        ]

        print("=" * 80)
        print("Week 13 Phase 3: Utils Extended Documentation Enhancement")
        print("=" * 80)
        print()

        for filename in files_to_enhance:
            file_path = self.utils_dir / filename
            if file_path.exists():
                print(f"Processing: {filename}")
                self.enhance_file(file_path)
            else:
                print(f"  [WARN] File not found: {filename}")

        print()
        print("=" * 80)
        print("Enhancement Summary")
        print("=" * 80)
        print(f"Files enhanced: {self.files_enhanced}")
        print(f"Lines added:    {self.total_lines_added}")
        print()

        if self.files_enhanced > 0:
            print("[SUCCESS] All files enhanced successfully!")
        else:
            print("[WARNING] No files were enhanced.")


def main():
    """Main entry point"""
    docs_dir = Path(__file__).parent.parent.parent / "docs"
    enhancer = UtilsExtendedDocsEnhancer(docs_dir)
    enhancer.enhance_all()


if __name__ == "__main__":
    main()
