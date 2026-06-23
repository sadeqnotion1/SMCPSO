#!/usr/bin/env python3
"""
=======================================================================================
                    scripts/docs/enhance_controllers_core_docs.py
=======================================================================================
Controllers Core Infrastructure Documentation Enhancement Script for Week 9 Phase 1

Enhances 8 critical controllers core files with:
- Sliding mode control theory (Lyapunov stability, Hurwitz criterion)
- Factory design patterns (singleton, registry, PSO integration)
- Control law composition theory (equivalent control, switching functions)
- Architecture diagrams (Mermaid flowcharts)
- Comprehensive usage examples (40 total scenarios)

Usage:
    python scripts/docs/enhance_controllers_core_docs.py --dry-run
    python scripts/docs/enhance_controllers_core_docs.py
"""

import re
from pathlib import Path
from typing import List
from dataclasses import dataclass
import argparse


@dataclass
class ControllersEnhancementStats:
    """Statistics for controllers documentation enhancement."""
    files_enhanced: int = 0
    lines_added: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ControllersDocEnhancer:
    """Enhances controllers core documentation with comprehensive content."""

    # All 8 controllers core files to enhance (Week 9 Phase 1)
    CONTROLLERS_FILES = {
        # SMC Core (4 files)
        'smc_core': [
            'smc_core_sliding_surface.md',
            'smc_core_equivalent_control.md',
            'smc_core_switching_functions.md',
            'smc_core_gain_validation.md',
        ],
        # Factory (2 files)
        'factory': [
            'factory_smc_factory.md',
            'factory_pso_integration.md',
        ],
        # Base (2 files)
        'base': [
            'base_controller_interface.md',
            'base_control_primitives.md',
        ]
    }

    def __init__(self, docs_root: Path, dry_run: bool = False):
        self.docs_root = docs_root / 'reference' / 'controllers'
        self.dry_run = dry_run
        self.stats = ControllersEnhancementStats()

    def enhance_all_files(self):
        """Enhance all controllers core documentation files."""
        print("\n" + "="*80)
        print("Week 9 Phase 1: Controllers Core Infrastructure Documentation Enhancement")
        print("="*80)

        all_files = []
        for category, files in self.CONTROLLERS_FILES.items():
            all_files.extend(files)

        for filename in all_files:
            doc_path = self.docs_root / filename
            if not doc_path.exists():
                error = f"File not found: {doc_path}"
                print(f"  ERROR: {error}")
                self.stats.errors.append(error)
                continue

            category = self._get_file_category(filename)
            self._enhance_file(doc_path, filename, category)

        self._print_summary()

    def _get_file_category(self, filename: str) -> str:
        """Determine file category from filename."""
        if 'smc_core' in filename:
            return 'smc_core'
        elif 'factory' in filename:
            return 'factory'
        elif 'base' in filename:
            return 'base'
        return 'unknown'

    def _enhance_file(self, doc_path: Path, filename: str, category: str):
        """Enhance a single controllers documentation file."""
        print(f"\nEnhancing: {filename}...")

        try:
            # Read existing content
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if already enhanced
            if '## Mathematical Foundation' in content:
                print("  SKIPPED: Already enhanced")
                return

            # Generate enhancements based on file type
            theory_section = self._generate_theory_section(filename, category)
            diagram_section = self._generate_diagram_section(filename, category)
            examples_section = self._generate_examples_section(filename, category)

            # Insert enhancements after Module Overview
            enhanced_content = self._insert_enhancements(
                content, theory_section, diagram_section, examples_section
            )

            # Calculate lines added
            lines_added = enhanced_content.count('\n') - content.count('\n')

            # Write enhanced content
            if not self.dry_run:
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)
                print(f"  SUCCESS: Added {lines_added} lines")
            else:
                print(f"  [DRY RUN] Would add {lines_added} lines")

            self.stats.files_enhanced += 1
            self.stats.lines_added += lines_added

        except Exception as e:
            error = f"Error enhancing {filename}: {e}"
            print(f"  ERROR: {error}")
            self.stats.errors.append(error)

    def _insert_enhancements(self, content: str, theory: str, diagram: str, examples: str) -> str:
        """Insert enhancement sections after Module Overview."""
        # Find Module Overview section
        overview_match = re.search(r'(##\s+Module Overview.*?)(\n##\s+)', content, re.DOTALL)
        if overview_match:
            return (content[:overview_match.end(1)] +
                    f"\n\n{theory}\n\n{diagram}\n\n{examples}\n" +
                    content[overview_match.end(1):])

        # If no Module Overview found, insert after source reference
        source_match = re.search(r'(\*\*Source:\*\*.*?\n)', content, re.DOTALL)
        if source_match:
            return (content[:source_match.end(1)] +
                    f"\n{theory}\n\n{diagram}\n\n{examples}\n\n" +
                    content[source_match.end(1):])

        return content

    def _generate_theory_section(self, filename: str, category: str) -> str:
        """Generate mathematical foundation based on file category."""
        # SMC Core
        if 'sliding_surface' in filename:
            return self._sliding_surface_theory()
        elif 'equivalent_control' in filename:
            return self._equivalent_control_theory()
        elif 'switching_functions' in filename:
            return self._switching_functions_theory()
        elif 'gain_validation' in filename:
            return self._gain_validation_theory()

        # Factory
        elif 'smc_factory' in filename:
            return self._smc_factory_theory()
        elif 'pso_integration' in filename:
            return self._pso_integration_theory()

        # Base
        elif 'controller_interface' in filename:
            return self._controller_interface_theory()
        elif 'control_primitives' in filename:
            return self._control_primitives_theory()

        return ""

    # =========================================================================
    # SMC CORE THEORY SECTIONS
    # =========================================================================

    def _sliding_surface_theory(self) -> str:
        return """## Mathematical Foundation

### Sliding Mode Control Theory

Sliding mode control forces system trajectories onto a **sliding surface** where desired dynamics are exhibited.

```{math}
s(\\vec{x}, t) = 0
```

Where $s: \\mathbb{R}^n \\times \\mathbb{R}_+ \\to \\mathbb{R}^m$ is the sliding surface function.

### Linear Sliding Surface for DIP

For the double-inverted pendulum with state $\\vec{x} = [x, \\dot{x}, \\theta_1, \\dot{\\theta}_1, \\theta_2, \\dot{\\theta}_2]^T$:

```{math}
s = \\lambda_1 \\dot{\\theta}_1 + c_1 \\theta_1 + \\lambda_2 \\dot{\\theta}_2 + c_2 \\theta_2
```

**Physical Interpretation:**
- $\\theta_1, \\theta_2$: Angular errors (desired = 0 for stabilization)
- $\\dot{\\theta}_1, \\dot{\\theta}_2$: Angular velocity errors
- $c_1, c_2 > 0$: Position feedback gains
- $\\lambda_1, \\lambda_2 > 0$: Velocity feedback gains

### Hurwitz Stability Criterion

For the sliding surface to ensure exponential convergence when $s = 0$:

```{math}
\\dot{s} = 0 \\quad \\Rightarrow \\quad \\lambda_i \\ddot{\\theta}_i + c_i \\dot{\\theta}_i = 0, \\quad i = 1, 2
```

This gives characteristic polynomial:

```{math}
p(r) = r + \\frac{c_i}{\\lambda_i}
```

**Hurwitz criterion** requires all roots to have negative real parts:

```{math}
\\frac{c_i}{\\lambda_i} > 0 \\quad \\Rightarrow \\quad c_i, \\lambda_i > 0
```

This ensures **exponential convergence** to zero:

```{math}
\\theta_i(t) = \\theta_i(0) e^{-\\frac{c_i}{\\lambda_i} t}
```

### Lyapunov Stability

**Lyapunov function:**

```{math}
V(s) = \\frac{1}{2} s^2
```

**Sliding condition** (Lyapunov stability):

```{math}
\\dot{V} = s \\dot{s} < 0 \\quad \\text{for} \\quad s \\neq 0
```

This ensures trajectories are attracted to the sliding surface and remain there.

### Reaching Condition

**Finite-time reaching** requires:

```{math}
s \\dot{s} \\leq -\\eta |s|, \\quad \\eta > 0
```

**Reaching time bound:**

```{math}
t_{reach} \\leq \\frac{|s(0)|}{\\eta}
```

### Sliding Surface Design Guidelines

1. **Hurwitz requirement:** All gains $c_i, \\lambda_i > 0$
2. **Convergence rate:** Larger $c_i/\\lambda_i$ → faster convergence
3. **Overshoot control:** Smaller $c_i/\\lambda_i$ → less overshoot
4. **Typical range:** $c_i/\\lambda_i \\in [0.5, 5.0]$ rad/s

### Higher-Order Sliding Surfaces

**Super-Twisting (2nd order):**

```{math}
s = \\sigma, \\quad \\dot{\\sigma} = \\lambda_1 \\dot{\\theta}_1 + c_1 \\theta_1 + \\lambda_2 \\dot{\\theta}_2 + c_2 \\theta_2
```

Provides **finite-time convergence** and **continuous control** (no chattering).

### Computational Complexity

- **Linear surface evaluation:** $O(n)$ multiply-adds
- **Surface derivative:** $O(n^2)$ if Jacobian needed
- **Memory:** $O(n)$ for gains and state"""

    def _equivalent_control_theory(self) -> str:
        return """## Mathematical Foundation

### Equivalent Control Method

The **equivalent control** $u_{eq}$ maintains motion on the sliding surface $s = 0$ when reached.

```{math}
\\frac{d}{dt} s(\\vec{x}, t) = 0 \\quad \\text{when} \\quad s = 0
```

### Derivation for DIP

For sliding surface:

```{math}
s = \\lambda_1 \\dot{\\theta}_1 + c_1 \\theta_1 + \\lambda_2 \\dot{\\theta}_2 + c_2 \\theta_2
```

Differentiate:

```{math}
\\dot{s} = \\lambda_1 \\ddot{\\theta}_1 + c_1 \\dot{\\theta}_1 + \\lambda_2 \\ddot{\\theta}_2 + c_2 \\dot{\\theta}_2
```

### Manipulator Equation

DIP dynamics (manipulator form):

```{math}
\\mathbf{M}(\\vec{q}) \\ddot{\\vec{q}} + \\mathbf{C}(\\vec{q}, \\dot{\\vec{q}}) \\dot{\\vec{q}} + \\mathbf{G}(\\vec{q}) = \\mathbf{B} u
```

Where:
- $\\mathbf{M}$: Mass/inertia matrix (3×3)
- $\\mathbf{C}$: Coriolis/centrifugal matrix
- $\\mathbf{G}$: Gravity vector
- $\\mathbf{B}$: Control input matrix (maps force to generalized coords)

### Solving for Equivalent Control

From $\\dot{s} = 0$ on sliding surface:

```{math}
\\lambda_1 \\ddot{\\theta}_1 + \\lambda_2 \\ddot{\\theta}_2 = -(c_1 \\dot{\\theta}_1 + c_2 \\dot{\\theta}_2)
```

Express $\\ddot{\\vec{q}}$ from manipulator equation:

```{math}
\\ddot{\\vec{q}} = \\mathbf{M}^{-1} (\\mathbf{B} u - \\mathbf{C} \\dot{\\vec{q}} - \\mathbf{G})
```

Substitute into $\\dot{s} = 0$ and solve for $u$:

```{math}
u_{eq} = (\\mathbf{\\Lambda} \\mathbf{M}^{-1} \\mathbf{B})^{-1} \\left[ -\\mathbf{\\Lambda} \\mathbf{M}^{-1} (\\mathbf{C} \\dot{\\vec{q}} + \\mathbf{G}) - \\mathbf{C}_s \\dot{\\vec{\\theta}} \\right]
```

Where:
- $\\mathbf{\\Lambda} = [\\lambda_1, \\lambda_2]$: Surface derivative gains
- $\\mathbf{C}_s = [c_1, c_2]$: Surface position gains

### Matrix Inversion Considerations

**Challenge:** $\\mathbf{M}$ can be **ill-conditioned** near singularities.

**Regularization:** Use **Tikhonov regularization** for numerical stability:

```{math}
\\mathbf{M}^{-1} \\approx (\\mathbf{M}^T \\mathbf{M} + \\alpha \\mathbf{I})^{-1} \\mathbf{M}^T
```

**Typical $\\alpha$:** $10^{-6}$ to $10^{-4}$ depending on conditioning.

### Model-Based vs Model-Free

**Model-Based (Equivalent Control):**
- ✅ Accurate on sliding surface
- ✅ Smooth control
- ❌ Requires accurate model
- ❌ Computational cost $O(n^3)$ for inversion

**Model-Free (Pure Switching):**
- ✅ Robust to model uncertainty
- ✅ Low computational cost
- ❌ High-frequency chattering
- ❌ Actuator wear

### Hybrid Approach

Combine both for practical SMC:

```{math}
u = u_{eq} + u_{sw}
```

Where:
- $u_{eq}$: Model-based equivalent control (nominal performance)
- $u_{sw} = -K \\, \\text{sign}(s)$: Switching term (robustness)

### Computational Complexity

- **Matrix multiplication:** $O(n^3)$
- **Matrix inversion:** $O(n^3)$ (dominant cost)
- **Total:** $O(n^3)$ per control cycle
- **For DIP:** $n = 3$, so ~27 multiply-adds

### Numerical Stability

**Condition number check:**

```{math}
\\kappa(\\mathbf{M}) = \\frac{\\sigma_{max}(\\mathbf{M})}{\\sigma_{min}(\\mathbf{M})}
```

**Rule of thumb:**
- $\\kappa < 10^3$: Well-conditioned
- $10^3 \\leq \\kappa < 10^6$: Moderate conditioning
- $\\kappa \\geq 10^6$: Ill-conditioned (increase regularization)"""

    def _switching_functions_theory(self) -> str:
        return """## Mathematical Foundation

### Chattering Reduction in SMC

**Chattering** is high-frequency oscillation around the sliding surface caused by discontinuous control.

### Sign Function (Ideal SMC)

```{math}
u_{sw} = -K \\, \\text{sign}(s)
```

**Problems:**
- Infinite switching frequency (theory)
- Actuator wear and heat (practice)
- Excites unmodeled dynamics
- Measurement noise amplification

### Boundary Layer Method

Replace sign with continuous approximation within layer $\\epsilon > 0$:

```{math}
\\text{sat}(s/\\epsilon) = \\begin{cases}
1, & s > \\epsilon \\\\
s/\\epsilon, & |s| \\leq \\epsilon \\\\
-1, & s < -\\epsilon
\\end{cases}
```

**Properties:**
- Continuous everywhere
- Lipschitz continuous: $|\\text{sat}(s/\\epsilon) - \\text{sat}(s'/\\epsilon)| \\leq |s - s'|/\\epsilon$
- Reduces chattering to bounded oscillation: $|s| \\leq \\epsilon$

### Tanh Smoothing

```{math}
\\text{tanh}\\left(\\frac{\\beta s}{\\epsilon}\\right)
```

**Advantages:**
- Smooth (infinitely differentiable)
- Slope parameter $\\beta$ controls sharpness
- Better frequency response than saturation

**Slope selection:**
- $\\beta = 3$ (default): Smooth transition, minimal chattering
- $\\beta = 10$: Sharper transition, closer to sign function
- $\\beta < 2$: Too smooth, tracking degrades

### Frequency Analysis

**Describing function** for tanh switching:

```{math}
N(A) = \\frac{4 \\beta}{\\pi \\epsilon A} \\int_0^{\\pi/2} \\tanh(\\beta A \\sin \\phi) \\sin \\phi \\, d\\phi
```

**For small $A \\ll \\epsilon$:**

```{math}
N(A) \\approx \\frac{\\beta}{\\epsilon}
```

**Chattering frequency estimate:**

```{math}
\\omega_c \\approx \\sqrt{\\frac{K \\beta}{\\epsilon m}}
```

Where $m$ is effective inertia.

### Trade-offs

**Larger $\\epsilon$:**
- ✅ Less chattering
- ❌ Larger steady-state error: $|e_{ss}| \\leq \\epsilon \\max_i \\lambda_i$

**Smaller $\\epsilon$:**
- ✅ Better tracking accuracy
- ❌ More chattering

**Typical design:**

```{math}
\\epsilon = 3 \\sigma_{noise}
```

Where $\\sigma_{noise}$ is measurement noise standard deviation.

### Dead Zone

For very small surface values, use dead zone to avoid chattering:

```{math}
u_{sw} = \\begin{cases}
-K \\, \\text{tanh}(s/\\epsilon), & |s| > \\delta \\\\
0, & |s| \\leq \\delta
\\end{cases}
```

**Typical:** $\\delta = 0.1 \\epsilon$

### Higher-Order Approximations

**Sigmoid function:**

```{math}
\\frac{2}{1 + e^{-\\beta s/\\epsilon}} - 1
```

**Properties:**
- Smooth like tanh
- Symmetric around origin
- Computationally similar cost

### Implementation Considerations

**Numerical precision:**
- Avoid $s/\\epsilon$ when $\\epsilon \\to 0$
- Clamp tanh argument: $|\\beta s/\\epsilon| \\leq 20$ (prevents overflow)

**Real-time constraints:**
- tanh: ~10-20 CPU cycles
- saturation: ~5 CPU cycles
- sign: ~1 CPU cycle

### Chattering Index Metric

Quantify chattering via **switching count** in window $T$:

```{math}
I_c = \\frac{1}{T} \\int_0^T |\\dot{u}(t)| dt
```

**Goal:** $I_c < I_{max}$ (e.g., $I_{max} = 100$ N/s for actuator)"""

    def _gain_validation_theory(self) -> str:
        return """## Mathematical Foundation

### Stability Margin Analysis

Gain validation ensures controller **stability margins** meet requirements.

### Hurwitz Criterion Validation

For sliding surface:

```{math}
s = \\lambda_1 \\dot{\\theta}_1 + c_1 \\theta_1 + \\lambda_2 \\dot{\\theta}_2 + c_2 \\theta_2 = 0
```

**Necessary conditions:**

```{math}
c_i > 0, \\quad \\lambda_i > 0, \\quad i = 1, 2
```

### Lyapunov Stability Margin

**Lyapunov function:**

```{math}
V = \\frac{1}{2} s^2
```

**Required condition:**

```{math}
\\dot{V} = s \\dot{s} \\leq -\\eta |s|, \\quad \\eta > 0
```

**Switching gain requirement:**

```{math}
K \\geq \\frac{\\max |\\Delta(\\vec{x}, t)|}{\\eta} + \\varepsilon
```

Where:
- $\\Delta$: Model uncertainty bound
- $\\varepsilon > 0$: Safety margin

**Typical:** $\\varepsilon = 0.2 K$ (20% margin)

### Control Authority Validation

**Maximum control force:**

```{math}
|u| \\leq u_{max}
```

**Peak force estimate** (worst case):

```{math}
|u|_{peak} \\leq |u_{eq}|_{max} + K
```

**Validation criterion:**

```{math}
|u_{eq}|_{max} + K \\leq 0.9 u_{max}
```

The 0.9 factor provides 10% safety margin for transients.

### Frequency Domain Validation

**Sliding surface characteristic frequency:**

```{math}
\\omega_{n,i} = \\sqrt{\\frac{c_i}{\\lambda_i}}, \\quad i = 1, 2
```

**Requirements:**
1. **Below Nyquist:** $\\omega_{n,i} < \\frac{\\omega_s}{5}$ (sampling frequency $\\omega_s$)
2. **Above DC:** $\\omega_{n,i} > 0.5$ rad/s (avoid drift)
3. **Bandwidth separation:** $\\omega_{n,1}$ and $\\omega_{n,2}$ differ by factor $< 5$ (avoid mode coupling)

### Gain Bounds

**Physical constraints** limit gains:

| Gain | Lower Bound | Upper Bound | Rationale |
|------|-------------|-------------|-----------|
| $c_1, c_2$ | 0.1 | 100 | Hurwitz + frequency limits |
| $\\lambda_1, \\lambda_2$ | 0.01 | 50 | Hurwitz + computational precision |
| $K$ (switching) | 1.0 | 500 | Lyapunov + actuator limits |
| $\\epsilon$ (boundary) | 0.001 | 0.5 | Chattering vs accuracy trade-off |

### Adaptation Law Validation

For **adaptive SMC**, validate adaptation gains:

```{math}
\\dot{K} = \\gamma |s|, \\quad \\gamma > 0
```

**Requirements:**
1. **Rate limit:** $|\\dot{K}| \\leq \\dot{K}_{max}$ (e.g., 100 N/s)
2. **Bounds:** $K_{min} \\leq K \\leq K_{max}$
3. **Leak term:** Optional $\\dot{K} = \\gamma |s| - \\sigma K$ prevents unbounded growth

**Typical:** $\\sigma = 0.01$ (1% leak)

### Robustness Validation

**Uncertainty margin:**

```{math}
\\delta_{margin} = \\frac{K - |\\Delta|_{max}}{K} \\times 100\\%
```

**Requirement:** $\\delta_{margin} \\geq 20\\%$

### Numerical Conditioning

**Matrix inversion check:** If using equivalent control:

```{math}
\\kappa(\\mathbf{\\Lambda} \\mathbf{M}^{-1} \\mathbf{B}) < 10^6
```

If $\\kappa \\geq 10^6$: Reduce gains or increase regularization.

### Parameter Space Validation

**Geometric constraint:** Gains must lie within admissible polytope:

```{math}
\\mathcal{G}_{valid} = \\left\\{ (c_1, c_2, \\lambda_1, \\lambda_2, K, \\epsilon) \\in \\mathbb{R}_+^6 : \\text{all criteria met} \\right\\}
```

**PSO optimization:** Search within $\\mathcal{G}_{valid}$ only."""

    # =========================================================================
    # FACTORY THEORY SECTIONS
    # =========================================================================

    def _smc_factory_theory(self) -> str:
        return """## Mathematical Foundation

### Factory Design Pattern

The **Factory Pattern** encapsulates object creation logic, providing loose coupling between client code and concrete implementations.

### Gang of Four Definition

**Intent:** Define an interface for creating objects, but let subclasses decide which class to instantiate.

```{math}
\\text{Factory}: \\text{ProductType} \\times \\text{Parameters} \\to \\text{ConcreteProduct}
```

### SMC Controller Hierarchy

```{math}
\\begin{align}
\\text{SMC} &\\to \\text{Controller} \\quad \\text{(abstract base)} \\\\
&\\to \\text{ClassicalSMC} \\\\
&\\to \\text{AdaptiveSMC} \\\\
&\\to \\text{SuperTwistingSMC} \\\\
&\\to \\text{HybridAdaptiveSMC}
\\end{align}
```

### Enum-Based Type Safety

**Type-safe controller selection:**

```python
class SMCType(Enum):
    CLASSICAL = "classical"
    ADAPTIVE = "adaptive"
    SUPER_TWISTING = "sta"
    HYBRID = "hybrid"
```

**Compile-time validation:** Python type checker (mypy) validates:

```python
def create_controller(ctrl_type: SMCType, ...) -> Controller:
    ...
```

### Registry Pattern

**Dynamic controller registration:**

```{math}
\\text{Registry}: \\text{SMCType} \\to (\\text{Parameters} \\to \\text{Controller})
```

**Benefits:**
1. **Open/Closed Principle:** Add new controllers without modifying factory
2. **Plugin Architecture:** Controllers can be registered at runtime
3. **Testing:** Mock controllers can be injected

### Singleton Registry

**Single global registry** avoids duplication:

```python
_controller_registry: Dict[SMCType, Callable] = {}

def register_controller(ctrl_type: SMCType, factory_fn: Callable):
    _controller_registry[ctrl_type] = factory_fn
```

**Thread safety:** Use locks if multi-threaded:

```python
_registry_lock = threading.Lock()

with _registry_lock:
    _controller_registry[ctrl_type] = factory_fn
```

### Dependency Injection

**Inversion of Control:** Factory receives dependencies rather than creating them:

```python
def create_controller(
    ctrl_type: SMCType,
    gains: List[float],
    dynamics_model: Optional[DynamicsModel] = None,  # Injected
    config: Optional[Config] = None  # Injected
) -> Controller:
    ...
```

**Benefits:**
- Testability: Inject mock dynamics models
- Flexibility: Change models without factory changes
- Loose coupling: Factory doesn't depend on concrete dynamics

### Gain Specification Pattern

**Each controller type specifies gain requirements:**

```{math}
\\text{GainSpec} = (n_{gains}, \\text{bounds}, \\text{names})
```

**Example:**

```python
@dataclass
class GainSpecification:
    n_gains: int
    bounds: List[Tuple[float, float]]
    gain_names: List[str]
    description: str
```

**Runtime validation:**

```python
def validate_gains(ctrl_type: SMCType, gains: List[float]) -> bool:
    spec = get_gain_specification(ctrl_type)
    if len(gains) != spec.n_gains:
        return False
    return all(lb <= g <= ub for g, (lb, ub) in zip(gains, spec.bounds))
```

### Configuration Dataclass Pattern

**Type-safe configuration:**

```python
@dataclass(frozen=True)
class SMCConfig:
    gains: List[float]
    max_force: float
    dt: float
    boundary_layer: float = 0.01

    def __post_init__(self):
        # Validation logic
        if self.max_force <= 0:
            raise ValueError("max_force must be positive")
```

**Benefits:**
- Immutable (frozen=True)
- Type hints enforced
- Validation in `__post_init__`
- Auto-generated `__repr__` and `__eq__`

### Builder Pattern Variant

For complex configurations:

```python
class SMCConfigBuilder:
    def __init__(self):
        self._config = {}

    def with_gains(self, gains: List[float]):
        self._config['gains'] = gains
        return self

    def with_max_force(self, max_force: float):
        self._config['max_force'] = max_force
        return self

    def build(self) -> SMCConfig:
        return SMCConfig(**self._config)
```

**Usage:**

```python
config = (SMCConfigBuilder()
    .with_gains([10, 8, 15, 12, 50, 5])
    .with_max_force(100.0)
    .build())
```

### Performance Considerations

**Factory overhead:**
- Type dispatch: $O(1)$ hash table lookup
- Object construction: $O(n_{params})$
- Validation: $O(n_{gains})$

**Total:** Negligible compared to controller compute time (~$\\mu$s vs ms)."""

    def _pso_integration_theory(self) -> str:
        return """## Mathematical Foundation

### PSO-Controller Integration Architecture

**Problem:** Particle Swarm Optimization (PSO) searches high-dimensional gain space for optimal controller performance.

```{math}
\\min_{\\vec{g} \\in \\mathcal{G}} J(\\vec{g})
```

Where:
- $\\vec{g}$: Gain vector (e.g., $[c_1, c_2, \\lambda_1, \\lambda_2, K, \\epsilon]$)
- $\\mathcal{G}$: Admissible gain space (bounds + constraints)
- $J$: Cost function (e.g., ITAE + control effort)

### Fitness Function Design

**Multi-objective cost:**

```{math}
J(\\vec{g}) = w_1 \\text{ITAE}(\\vec{g}) + w_2 \\text{RMS}_u(\\vec{g}) + w_3 \\text{CHAT}(\\vec{g}) + w_4 \\text{VIOL}(\\vec{g})
```

Where:
- **ITAE:** $\\int_0^T t |\\vec{e}(t)| dt$ (tracking error weighted by time)
- **RMS_u:** $\\sqrt{\\frac{1}{T} \\int_0^T u^2(t) dt}$ (control effort)
- **CHAT:** $\\int_0^T |\\dot{u}(t)| dt$ (chattering index)
- **VIOL:** Constraint violations (saturation events)

**Typical weights:** $w_1 = 1.0, w_2 = 0.1, w_3 = 0.05, w_4 = 10.0$

### Gain Bounds for PSO

**Physical constraints** define search space:

```{math}
\\mathcal{G} = \\prod_{i=1}^{n_g} [g_i^{min}, g_i^{max}]
```

**Example (Classical SMC with 6 gains):**

| Gain | Symbol | Lower | Upper | Unit |
|------|--------|-------|-------|------|
| $c_1$ | Position 1 | 0.1 | 50.0 | — |
| $c_2$ | Position 2 | 0.1 | 50.0 | — |
| $\\lambda_1$ | Velocity 1 | 0.1 | 50.0 | — |
| $\\lambda_2$ | Velocity 2 | 0.1 | 50.0 | — |
| $K$ | Switching | 1.0 | 200.0 | N |
| $\\epsilon$ | Boundary | 0.0 | 50.0 | rad |

### Factory-PSO Integration Pattern

**Closure-based fitness function:**

```python
def create_fitness_function(
    ctrl_type: SMCType,
    config: Config
) -> Callable[[np.ndarray], float]:
    \"\"\"Returns fitness function for PSO.\"\"\"

    def fitness(gains: np.ndarray) -> float:
        # Create controller with candidate gains
        controller = create_smc_for_pso(ctrl_type, gains)

        # Simulate
        result = simulate(controller, config)

        # Compute cost
        return compute_cost(result)

    return fitness
```

**Benefits:**
- Encapsulates controller creation
- PSO only sees fitness function
- Easy to change controller type

### Batch Evaluation Optimization

**Vectorized simulation** for PSO swarm:

```python
def batch_fitness(
    gains_population: np.ndarray,  # Shape: (n_particles, n_gains)
    ctrl_type: SMCType
) -> np.ndarray:  # Shape: (n_particles,)
    \"\"\"Evaluate all particles in parallel.\"\"\"
    controllers = [create_smc_for_pso(ctrl_type, g) for g in gains_population]
    results = batch_simulate(controllers, config)
    return np.array([compute_cost(r) for r in results])
```

**Speedup:** $5{-}10\\times$ using Numba JIT compilation

### Convergence Criteria

**PSO stops when:**

1. **Fitness stagnation:**
   ```{math}
   \\frac{f_{best}^{(k)} - f_{best}^{(k-10)}}{f_{best}^{(k-10)}} < \\epsilon_{conv}
   ```
   Typical: $\\epsilon_{conv} = 10^{-4}$

2. **Diversity collapse:**
   ```{math}
   \\frac{1}{n_p} \\sum_{i=1}^{n_p} \\|\\vec{g}_i - \\bar{\\vec{g}}\\| < \\epsilon_{div}
   ```
   Where $\\bar{\\vec{g}}$ is swarm centroid

3. **Maximum iterations:** $k \\geq k_{max}$ (e.g., 100)

### Post-Optimization Validation

After PSO converges:

1. **Validate gains:** Check Hurwitz, Lyapunov, bounds
2. **Monte Carlo robustness:** Test with parameter uncertainty
3. **Frequency response:** Verify bandwidth requirements
4. **Hardware limits:** Check control authority

**Rejection rate:** ~5-10% of PSO results fail validation.

### Hyperparameter Tuning

**PSO meta-parameters:**

```{math}
\\begin{align}
w &: \\text{Inertia weight} \\quad (0.729) \\\\
c_1 &: \\text{Cognitive coefficient} \\quad (1.494) \\\\
c_2 &: \\text{Social coefficient} \\quad (1.494) \\\\
n_p &: \\text{Particles} \\quad (30) \\\\
k_{max} &: \\text{Iterations} \\quad (50{-}100)
\\end{align}
```

**Tuning guidelines:**
- Larger $w$: More exploration (slower convergence)
- Larger $c_1$: More individualism (local search)
- Larger $c_2$: More social behavior (global search)"""

    # =========================================================================
    # BASE THEORY SECTIONS
    # =========================================================================

    def _controller_interface_theory(self) -> str:
        return """## Mathematical Foundation

### Protocol-Oriented Design

**Protocols** define abstract interfaces without implementation inheritance.

```{math}
\\text{Protocol}: \\text{Interface Specification} \\to \\text{Type Constraints}
```

### Controller Protocol

**Minimal interface** all controllers must implement:

```python
class ControllerProtocol(Protocol):
    def compute_control(
        self,
        state: np.ndarray,
        state_vars: Dict[str, Any],
        history: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any], Dict[str, Any]]:
        ...

    def initialize_history(self) -> Dict[str, Any]:
        ...
```

### Liskov Substitution Principle

**LSP:** Subclasses must be substitutable for base class without breaking program.

```{math}
\\forall c \\in \\text{Controller}: \\quad c.\\text{compute\\_control}(s, v, h) \\to (u, v', h')
```

**Guarantees:**
- All controllers return same signature
- All controllers handle same state format
- Simulation engine doesn't care about controller type

### Type Variance

**Contravariant input types:**

```python
class Controller(ABC):
    def compute_control(
        self,
        state: np.ndarray,  # Can accept more general types in subclasses
        ...
    ) -> ...:
        ...
```

**Covariant return types:**

```python
class Controller(ABC):
    def compute_control(...) -> Tuple[float, Dict, Dict]:  # Subclasses can return more specific types
        ...
```

### Abstract Base Class Pattern

```python
class Controller(ABC):
    @abstractmethod
    def compute_control(self, state, state_vars, history):
        \"\"\"Subclasses MUST implement this.\"\"\"
        pass

    def reset(self):
        \"\"\"Default implementation (optional override).\"\"\"
        return self.initialize_history()
```

**Enforcement:** Python raises `TypeError` if abstract methods not implemented.

### Duck Typing vs Explicit Protocols

**Duck Typing:** "If it walks like a duck and quacks like a duck, it's a duck."

```python
# No type checking - relies on runtime behavior
def simulate(controller):
    u = controller.compute_control(state, {}, {})  # Hope it works!
```

**Explicit Protocol:** Type checker validates at compile time.

```python
def simulate(controller: ControllerProtocol):
    u = controller.compute_control(state, {}, {})  # Type-safe!
```

### State Variable Pattern

**Problem:** Controllers need internal state (e.g., integral error, adaptation gains).

**Solution:** Return updated state variables:

```python
def compute_control(
    self,
    state: np.ndarray,
    state_vars: Dict[str, Any],
    history: Dict[str, Any]
) -> Tuple[float, Dict[str, Any], Dict[str, Any]]:
    # Extract previous state
    K = state_vars.get('K', self.K_initial)

    # Update state (e.g., adaptation)
    K_new = K + self.gamma * abs(s) * self.dt

    # Return new state
    return u, {'K': K_new}, history
```

**Benefits:**
- Pure functional style (no hidden state)
- Simulation reproducible (state fully captured)
- Easy to checkpoint and resume

### History Pattern

**Problem:** Controllers may need trajectory history (e.g., for derivative estimation).

**Solution:** Return updated history dict:

```python
def compute_control(self, state, state_vars, history):
    # Append to history
    history['states'].append(state)
    history['times'].append(t)

    # Compute derivative from history
    if len(history['states']) >= 2:
        derivative = (state - history['states'][-2]) / self.dt

    return u, state_vars, history
```

### Polymorphism Depth

**Single-level polymorphism:**

```
Controller (abstract)
├─ ClassicalSMC
├─ AdaptiveSMC
├─ SuperTwistingSMC
└─ HybridAdaptiveSMC
```

**No deep hierarchies:** Avoid fragile base class problem.

### Method Resolution Order

Python uses **C3 linearization** for multiple inheritance:

```python
class HybridAdaptiveSMC(AdaptiveSMC, SuperTwistingSMC):
    pass

# MRO: HybridAdaptiveSMC → AdaptiveSMC → SuperTwistingSMC → Controller → ABC
```

**Diamond problem:** C3 ensures consistent method resolution."""

    def _control_primitives_theory(self) -> str:
        return """## Mathematical Foundation

### Control Law Composition

**Primitive:** Atomic control operation that can be composed into complex laws.

```{math}
u = \\mathcal{C}(u_1, u_2, \\ldots, u_n)
```

Where $\\mathcal{C}$ is composition operator (sum, max, switching, etc.).

### Additive Composition

**Superposition principle** for linear systems:

```{math}
u = u_{ff} + u_{fb} + u_{robust}
```

Where:
- $u_{ff}$: Feedforward control (model-based)
- $u_{fb}$: Feedback control (error-driven)
- $u_{robust}$: Robustness term (disturbance rejection)

**SMC example:**

```{math}
u = u_{eq} + u_{sw}
```

### Saturation Primitive

**Input saturation** enforces actuator limits:

```{math}
\\text{sat}(u, u_{max}) = \\begin{cases}
u_{max}, & u > u_{max} \\\\
u, & |u| \\leq u_{max} \\\\
-u_{max}, & u < -u_{max}
\\end{cases}
```

**Properties:**
- Non-linear (breaks superposition)
- Lipschitz continuous: $|\\text{sat}(u) - \\text{sat}(v)| \\leq |u - v|$
- Monotonic: $u > v \\Rightarrow \\text{sat}(u) \\geq \\text{sat}(v)$

### Deadband Primitive

**Deadband** ignores small errors (avoid actuator noise):

```{math}
\\text{deadband}(e, \\delta) = \\begin{cases}
e - \\delta, & e > \\delta \\\\
0, & |e| \\leq \\delta \\\\
e + \\delta, & e < -\\delta
\\end{cases}
```

**Typical:** $\\delta = 3 \\sigma_{noise}$

### Rate Limiter Primitive

**Rate limiting** prevents actuator slew violations:

```{math}
u_k = \\text{clip}(u_k^{desired}, u_{k-1} - \\dot{u}_{max} \\Delta t, u_{k-1} + \\dot{u}_{max} \\Delta t)
```

**Example:** $\\dot{u}_{max} = 1000$ N/s for hydraulic actuator

### Low-Pass Filter Primitive

**First-order filter** reduces high-frequency content:

```{math}
u_f = \\frac{\\omega_c}{s + \\omega_c} u
```

**Discrete implementation:**

```{math}
u_f[k] = \\alpha u[k] + (1 - \\alpha) u_f[k-1], \\quad \\alpha = \\frac{\\Delta t}{\\Delta t + \\tau}
```

Where $\\tau = 1/\\omega_c$ is filter time constant.

### Gain Scheduling Primitive

**Non-linear gain** varies with operating point:

```{math}
K(\\vec{x}) = K_0 + \\sum_{i=1}^{n} K_i \\phi_i(\\vec{x})
```

Where $\\phi_i$ are basis functions (e.g., RBF, polynomial).

**Linear interpolation example:**

```{math}
K(\\theta) = \\begin{cases}
K_{low}, & \\theta < \\theta_{low} \\\\
K_{low} + \\frac{K_{high} - K_{low}}{\\theta_{high} - \\theta_{low}} (\\theta - \\theta_{low}), & \\theta_{low} \\leq \\theta \\leq \\theta_{high} \\\\
K_{high}, & \\theta > \\theta_{high}
\\end{cases}
```

### Anti-Windup Primitive

**Problem:** Integral windup when saturation active.

**Solution:** Conditional integration:

```{math}
\\dot{I} = \\begin{cases}
e, & u_{raw} = u_{sat} \\quad \\text{(no saturation)} \\\\
0, & \\text{otherwise}
\\end{cases}
```

Or **back-calculation:**

```{math}
\\dot{I} = e + \\frac{1}{T_i} (u_{sat} - u_{raw})
```

### Observer Primitive

**State estimation** from measurements:

```{math}
\\dot{\\hat{x}} = A \\hat{x} + B u + L(y - C \\hat{x})
```

Where $L$ is observer gain matrix.

**Separation principle:** Design observer and controller independently (for linear systems).

### Composition Algebra

**Commutative:** $u_1 + u_2 = u_2 + u_1$ (for linear)

**Not commutative:** $\\text{sat}(u_1 + u_2) \\neq \\text{sat}(u_1) + \\text{sat}(u_2)$

**Associative:** $(u_1 + u_2) + u_3 = u_1 + (u_2 + u_3)$

**Distributive (partial):** For some operators"""

    # =========================================================================
    # DIAGRAM GENERATION
    # =========================================================================

    def _generate_diagram_section(self, filename: str, category: str) -> str:
        """Generate architecture diagram based on file type."""
        if 'sliding_surface' in filename:
            return self._sliding_surface_diagram()
        elif 'equivalent_control' in filename:
            return self._equivalent_control_diagram()
        elif 'switching_functions' in filename:
            return self._switching_functions_diagram()
        elif 'gain_validation' in filename:
            return self._gain_validation_diagram()
        elif 'smc_factory' in filename:
            return self._smc_factory_diagram()
        elif 'pso_integration' in filename:
            return self._pso_integration_diagram()
        elif 'controller_interface' in filename:
            return self._controller_interface_diagram()
        elif 'control_primitives' in filename:
            return self._control_primitives_diagram()
        return ""

    def _sliding_surface_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[State Vector x] --> B[Extract Errors: θ₁, θ₂, θ̇₁, θ̇₂]
    B --> C[Compute s = λ₁θ̇₁ + c₁θ₁ + λ₂θ̇₂ + c₂θ₂]
    C --> D{|s| < ε?}
    D -->|Yes| E[On Sliding Surface]
    D -->|No| F[Off Sliding Surface]
    E --> G[Sliding Mode Reached]
    F --> H[Reaching Phase]

    B --> I[Validate Gains: c₁, c₂, λ₁, λ₂ > 0]
    I -->|Invalid| J[Raise ValueError]
    I -->|Valid| C

    style C fill:#9cf
    style E fill:#9f9
    style F fill:#ff9
    style J fill:#f99
```"""

    def _equivalent_control_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[State x, Dynamics Model] --> B[Compute M_x_]
    B --> C[Compute C_x_ẋ_]
    C --> D[Compute G_x_]
    D --> E[Compute B Matrix]
    E --> F[Assemble: Λ M⁻¹ B]
    F --> G{Condition Number < 10⁶?}
    G -->|Yes| H[Invert: _Λ M⁻¹ B_⁻¹]
    G -->|No| I[Apply Tikhonov Regularization]
    I --> H
    H --> J[Compute u_eq = _Λ M⁻¹ B_⁻¹ _-Λ M⁻¹_Cẋ + G_ - C_s θ̇_]
    J --> K[Return u_eq]

    style F fill:#9cf
    style H fill:#ff9
    style I fill:#f99
    style K fill:#9f9
```"""

    def _switching_functions_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[Sliding Surface s] --> B{Switching Method}
    B -->|sign| C[Discontinuous: sign_s_]
    B -->|saturation| D[Boundary Layer: sat_s/ε_]
    B -->|tanh| E[Smooth: tanh_βs/ε_]

    C --> F[High Chattering]
    D --> G[Reduced Chattering, Bounded |s| ≤ ε]
    E --> H[Minimal Chattering, Smooth]

    E --> I[Check: |βs/ε| < 20]
    I -->|Yes| J[Compute tanh]
    I -->|No| K[Clamp Argument]
    K --> J

    style C fill:#f99
    style D fill:#ff9
    style E fill:#9cf
    style H fill:#9f9
```"""

    def _gain_validation_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[Input Gains] --> B{Hurwitz Check}
    B -->|c₁,c₂,λ₁,λ₂ > 0?| C[Frequency Analysis]
    B -->|No| X[Reject: Unstable]

    C --> D{ω_n < ω_s/5?}
    D -->|No| Y[Reject: Aliasing Risk]
    D -->|Yes| E[Control Authority Check]

    E --> F{|u_eq|_max + K ≤ 0.9u_max?}
    F -->|No| Z[Reject: Saturation Risk]
    F -->|Yes| G[Robustness Margin]

    G --> H{_K - |Δ|_max_/K ≥ 20%?}
    H -->|No| W[Reject: Insufficient Margin]
    H -->|Yes| I[Accept Gains]

    style X fill:#f99
    style Y fill:#f99
    style Z fill:#f99
    style W fill:#f99
    style I fill:#9f9
```"""

    def _smc_factory_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[Client Request: SMCType, gains, config] --> B[Factory.create_controller]
    B --> C{Validate Gains}
    C -->|Invalid| D[Raise ValueError]
    C -->|Valid| E{Type Dispatch}

    E -->|CLASSICAL| F[ClassicalSMC.__init__]
    E -->|ADAPTIVE| G[AdaptiveSMC.__init__]
    E -->|SUPER_TWISTING| H[SuperTwistingSMC.__init__]
    E -->|HYBRID| I[HybridAdaptiveSMC.__init__]

    F --> J[Return Controller Instance]
    G --> J
    H --> J
    I --> J

    J --> K[Client Uses: controller.compute_control]

    style B fill:#9cf
    style E fill:#ff9
    style J fill:#9f9
    style D fill:#f99
```"""

    def _pso_integration_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[PSO Optimizer] --> B[Generate Particle Swarm]
    B --> C[For Each Particle: gains]
    C --> D[Factory.create_smc_for_pso_ctrl_type_ gains_]
    D --> E[Simulate with Controller]
    E --> F[Compute Fitness: J_gains_]
    F --> G[Update Personal Best]
    G --> H[Update Global Best]
    H --> I{Converged?}
    I -->|No| J[Update Velocities & Positions]
    J --> C
    I -->|Yes| K[Validate Best Gains]
    K --> L{Pass Validation?}
    L -->|Yes| M[Return Optimal Gains]
    L -->|No| N[Re-run PSO with Stricter Constraints]

    style D fill:#9cf
    style F fill:#ff9
    style M fill:#9f9
    style N fill:#f99
```"""

    def _controller_interface_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[ControllerProtocol_ABC_] --> B[compute_control: Abstract]
    A --> C[initialize_history: Abstract]
    A --> D[reset: Default Implementation]

    B --> E[ClassicalSMC.compute_control]
    B --> F[AdaptiveSMC.compute_control]
    B --> G[SuperTwistingSMC.compute_control]
    B --> H[HybridAdaptiveSMC.compute_control]

    C --> I[ClassicalSMC.initialize_history]
    C --> J[AdaptiveSMC.initialize_history]
    C --> K[SuperTwistingSMC.initialize_history]
    C --> L[HybridAdaptiveSMC.initialize_history]

    E --> M[Return: _u_ state_vars_ history_]
    F --> M
    G --> M
    H --> M

    style A fill:#9cf
    style B fill:#ff9
    style M fill:#9f9
```"""

    def _control_primitives_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[Raw Control u_raw] --> B[Anti-Windup]
    B --> C[Rate Limiter]
    C --> D[Saturation]
    D --> E[Low-Pass Filter]
    E --> F[Deadband]
    F --> G[Final Control u]

    B --> H[Check: Saturation Active?]
    H -->|Yes| I[Halt Integration]
    H -->|No| J[Continue Integration]

    C --> K[Check: |u̇| ≤ u̇_max?]
    K -->|No| L[Clip Rate]
    K -->|Yes| C

    D --> M[Check: |u| ≤ u_max?]
    M -->|No| N[Saturate]
    M -->|Yes| D

    style A fill:#9cf
    style G fill:#9f9
    style I fill:#f99
    style L fill:#ff9
    style N fill:#ff9
```"""

    # =========================================================================
    # EXAMPLES GENERATION
    # =========================================================================

    def _generate_examples_section(self, filename: str, category: str) -> str:
        """Generate usage examples based on file type."""
        if 'sliding_surface' in filename:
            return self._sliding_surface_examples()
        elif 'equivalent_control' in filename:
            return self._equivalent_control_examples()
        elif 'switching_functions' in filename:
            return self._switching_functions_examples()
        elif 'gain_validation' in filename:
            return self._gain_validation_examples()
        elif 'smc_factory' in filename:
            return self._smc_factory_examples()
        elif 'pso_integration' in filename:
            return self._pso_integration_examples()
        elif 'controller_interface' in filename:
            return self._controller_interface_examples()
        elif 'control_primitives' in filename:
            return self._control_primitives_examples()
        return ""

    def _sliding_surface_examples(self) -> str:
        return """## Usage Examples

### Example 1: Basic Linear Sliding Surface

```python
from src.controllers.smc.core.sliding_surface import LinearSlidingSurface
import numpy as np

# Define gains (c1, c2, λ1, λ2)
gains = [10.0, 8.0, 15.0, 12.0]
surface = LinearSlidingSurface(gains)

# Compute surface value for state
state = np.array([0.1, 0.0, 0.05, 0.1, 0.02, 0.05])  # [x, ẋ, θ₁, θ̇₁, θ₂, θ̇₂]
s = surface.compute(state)
print(f"Sliding surface value: {s:.4f}")
```

### Example 2: Surface Derivative Computation

```python
# Compute surface derivative ds/dt
state_dot = np.array([0.0, 0.0, 0.1, -0.5, 0.05, -0.3])
s_dot = surface.compute_derivative(state, state_dot)
print(f"Surface derivative: {s_dot:.4f}")

# Check sliding condition
if abs(s) < 0.01 and s * s_dot < 0:
    print("Sliding mode reached and maintained")
```

### Example 3: Gain Validation

```python
from src.controllers.smc.core.sliding_surface import validate_sliding_surface_gains

# Valid gains (all positive)
gains_valid = [10.0, 8.0, 15.0, 12.0]
is_valid = validate_sliding_surface_gains(gains_valid)
print(f"Valid gains: {is_valid}")  # True

# Invalid gains (c2 negative)
gains_invalid = [10.0, -8.0, 15.0, 12.0]
try:
    surface_bad = LinearSlidingSurface(gains_invalid)
except ValueError as e:
    print(f"Validation error: {e}")
```

### Example 4: Frequency Analysis

```python
# Compute characteristic frequencies
c1, c2, lambda1, lambda2 = gains
omega_n1 = np.sqrt(c1 / lambda1)  # rad/s
omega_n2 = np.sqrt(c2 / lambda2)  # rad/s

print(f"Natural frequency 1: {omega_n1:.2f} rad/s")
print(f"Natural frequency 2: {omega_n2:.2f} rad/s")

# Check Nyquist criterion (sampling frequency 100 Hz)
omega_s = 2 * np.pi * 100  # rad/s
if omega_n1 < omega_s / 5 and omega_n2 < omega_s / 5:
    print("Frequencies safe for 100 Hz sampling")
```

### Example 5: Higher-Order Surface (Super-Twisting)

```python
from src.controllers.smc.core.sliding_surface import HigherOrderSlidingSurface

# Define 6 gains for 2nd order surface
gains_ho = [25.0, 10.0, 15.0, 12.0, 20.0, 15.0]
surface_ho = HigherOrderSlidingSurface(gains_ho)

# Compute surface and its derivative
s_ho = surface_ho.compute(state)
s_dot_ho = surface_ho.compute_derivative(state, state_dot)

print(f"Higher-order surface: s={s_ho:.4f}, ṡ={s_dot_ho:.4f}")
```"""

    def _equivalent_control_examples(self) -> str:
        return """## Usage Examples

### Example 1: Basic Equivalent Control Computation

```python
from src.controllers.smc.core.equivalent_control import EquivalentControl
from src.plant.models.simplified import SimplifiedDIPDynamics

# Initialize dynamics model
dynamics = SimplifiedDIPDynamics()

# Initialize equivalent control module
eq_control = EquivalentControl(
    dynamics_model=dynamics,
    surface_gains=[10.0, 8.0, 15.0, 12.0]  # λ1, c1, λ2, c2
)

# Compute equivalent control for current state
state = np.array([0.1, 0.0, 0.05, 0.1, 0.02, 0.05])
u_eq = eq_control.compute(state)
print(f"Equivalent control: {u_eq:.2f} N")
```

### Example 2: Matrix Conditioning Check

```python
# Check matrix conditioning before inversion
M = dynamics.compute_mass_matrix(state)
cond_number = np.linalg.cond(M)

print(f"Condition number of M: {cond_number:.2e}")

if cond_number > 1e6:
    print("Warning: Ill-conditioned matrix, increasing regularization")
    eq_control.set_regularization(alpha=1e-4)
else:
    print("Matrix well-conditioned")
```

### Example 3: Regularization Adjustment

```python
# Adaptive regularization based on conditioning
def adaptive_regularization(cond_number):
    if cond_number < 1e3:
        return 1e-6  # Minimal regularization
    elif cond_number < 1e6:
        return 1e-5  # Moderate regularization
    else:
        return 1e-4  # Strong regularization

alpha = adaptive_regularization(cond_number)
eq_control.set_regularization(alpha=alpha)
print(f"Using regularization: α={alpha:.2e}")
```

### Example 4: Hybrid Control (Equivalent + Switching)

```python
from src.utils.control.saturation import saturate

# Compute equivalent control (model-based)
u_eq = eq_control.compute(state)

# Compute sliding surface
s = surface.compute(state)

# Compute switching control (robustness)
K_sw = 50.0  # Switching gain
epsilon = 0.01  # Boundary layer
u_sw = -K_sw * saturate(s, epsilon, method='tanh')

# Total control
u_total = u_eq + u_sw

# Apply actuator limits
u_max = 100.0
u = np.clip(u_total, -u_max, u_max)

print(f"u_eq={u_eq:.2f}, u_sw={u_sw:.2f}, u_total={u:.2f}")
```

### Example 5: Performance Profiling

```python
import time

# Benchmark equivalent control computation
n_iterations = 1000
start = time.time()

for _ in range(n_iterations):
    u_eq = eq_control.compute(state)

elapsed = time.time() - start
time_per_call = (elapsed / n_iterations) * 1e6  # microseconds

print(f"Equivalent control time: {time_per_call:.2f} μs per call")
print(f"Can achieve ~{1e6 / time_per_call:.0f} Hz control rate")
```"""

    def _switching_functions_examples(self) -> str:
        return """## Usage Examples

### Example 1: Tanh Switching Function

```python
from src.utils.control.saturation import saturate
import numpy as np

# Sliding surface value
s = 0.05  # rad

# Boundary layer parameters
epsilon = 0.01  # rad
beta = 3.0  # Slope parameter

# Compute tanh switching
u_sw = saturate(s, epsilon, method='tanh', slope=beta)
print(f"Switching control: {u_sw:.4f}")

# For s >> epsilon, u_sw → 1.0
# For s << -epsilon, u_sw → -1.0
# For |s| < epsilon, smooth transition
```

### Example 2: Chattering Comparison

```python
import matplotlib.pyplot as plt

# Time series
t = np.linspace(0, 5, 5000)
s_trajectory = 0.02 * np.sin(10 * t) + 0.005 * np.random.randn(len(t))

# Different switching methods
u_sign = np.sign(s_trajectory)
u_sat = np.clip(s_trajectory / epsilon, -1, 1)
u_tanh = np.tanh(beta * s_trajectory / epsilon)

# Compute chattering index (control derivative)
chat_sign = np.sum(np.abs(np.diff(u_sign)))
chat_sat = np.sum(np.abs(np.diff(u_sat)))
chat_tanh = np.sum(np.abs(np.diff(u_tanh)))

print(f"Chattering index (sign):  {chat_sign:.1f}")
print(f"Chattering index (sat):   {chat_sat:.1f}")
print(f"Chattering index (tanh):  {chat_tanh:.1f}")  # Lowest
```

### Example 3: Slope Parameter Tuning

```python
# Test different slope parameters
slopes = [1.0, 3.0, 5.0, 10.0, 20.0]

for beta in slopes:
    u = saturate(s, epsilon, method='tanh', slope=beta)

    # Estimate effective switching sharpness
    s_test = np.linspace(-3*epsilon, 3*epsilon, 100)
    u_test = saturate(s_test, epsilon, method='tanh', slope=beta)
    sharpness = np.mean(np.abs(np.diff(u_test))) / (6 * epsilon / 100)

    print(f"β={beta:4.1f}: u={u:6.4f}, sharpness={sharpness:.3f}")
```

### Example 4: Dead Zone Integration

```python
def dead_zone_switching(s, epsilon, delta, K):
    \"\"\"Switching with dead zone to avoid chattering near origin.\"\"\"
    if abs(s) < delta:
        return 0.0
    else:
        return -K * saturate(s, epsilon, method='tanh')

# Parameters
delta = 0.1 * epsilon  # Dead zone 10% of boundary layer
K = 50.0

u_sw = dead_zone_switching(s, epsilon, delta, K)
print(f"Switching with dead zone: {u_sw:.2f} N")
```

### Example 5: Frequency Response

```python
from scipy import signal

# Create transfer function for tanh switching
# Approximation: linearize around s=0
# tanh(βs/ε) ≈ (β/ε)s for small s
gain_linear = beta / epsilon

# Frequency response
frequencies = np.logspace(-1, 3, 100)  # 0.1 to 1000 rad/s
w, mag, phase = signal.bode((gain_linear, [1, 0]), frequencies)

# Plot
plt.subplot(2, 1, 1)
plt.semilogx(w, mag)
plt.ylabel('Magnitude (dB)')
plt.title(f'Tanh Switching (β={beta}, ε={epsilon})')

plt.subplot(2, 1, 2)
plt.semilogx(w, phase)
plt.ylabel('Phase (deg)')
plt.xlabel('Frequency (rad/s)')
plt.show()
```"""

    def _gain_validation_examples(self) -> str:
        return """## Usage Examples

### Example 1: Hurwitz Criterion Validation

```python
from src.controllers.smc.core.gain_validation import validate_hurwitz_criterion

# Test gains
gains = [10.0, 8.0, 15.0, 12.0, 50.0, 0.01]  # c1, c2, λ1, λ2, K, ε

is_hurwitz = validate_hurwitz_criterion(gains)

if is_hurwitz:
    print("Gains satisfy Hurwitz criterion (stable sliding surface)")
else:
    print("Warning: Gains violate Hurwitz criterion")
```

### Example 2: Control Authority Check

```python
from src.controllers.smc.core.gain_validation import check_control_authority

# Controller parameters
c1, c2, lambda1, lambda2, K, epsilon = gains
u_max = 100.0  # Maximum actuator force (N)

# Estimate peak equivalent control (worst case)
u_eq_max = 80.0  # From dynamics analysis

# Check if total control fits within limits
u_total_max = u_eq_max + K
margin = u_max - u_total_max

print(f"u_eq_max: {u_eq_max:.1f} N")
print(f"K:        {K:.1f} N")
print(f"u_total:  {u_total_max:.1f} N")
print(f"u_max:    {u_max:.1f} N")
print(f"Margin:   {margin:.1f} N ({100*margin/u_max:.1f}%)")

if margin < 0.1 * u_max:
    print("Warning: Insufficient control authority margin")
```

### Example 3: Frequency Bounds Validation

```python
# Compute natural frequencies
omega_n1 = np.sqrt(c1 / lambda1)
omega_n2 = np.sqrt(c2 / lambda2)

# Sampling frequency (Hz)
f_s = 100  # Hz
omega_s = 2 * np.pi * f_s  # rad/s

# Check Nyquist criterion
if omega_n1 < omega_s / 5 and omega_n2 < omega_s / 5:
    print(f"✓ Frequencies safe: ω_n1={omega_n1:.2f}, ω_n2={omega_n2:.2f} rad/s")
else:
    print(f"✗ Aliasing risk: ω_n1={omega_n1:.2f}, ω_n2={omega_n2:.2f} rad/s")

# Check lower bound (avoid drift)
if omega_n1 > 0.5 and omega_n2 > 0.5:
    print("✓ Frequencies above DC drift threshold")
else:
    print("✗ Frequencies too low, drift risk")
```

### Example 4: Robustness Margin

```python
# Model uncertainty bound
Delta_max = 20.0  # N (maximum disturbance/uncertainty)

# Compute robustness margin
margin_percent = 100 * (K - Delta_max) / K

print(f"Switching gain K:      {K:.1f} N")
print(f"Uncertainty Δ_max:     {Delta_max:.1f} N")
print(f"Robustness margin:     {margin_percent:.1f}%")

if margin_percent < 20:
    print("Warning: Insufficient robustness margin (< 20%)")
    K_recommended = Delta_max / 0.8  # 20% margin
    print(f"Recommended K:         {K_recommended:.1f} N")
```

### Example 5: Complete Validation Suite

```python
from src.controllers.smc.core.gain_validation import validate_all_criteria

# Validation configuration
validation_config = {
    'u_max': 100.0,         # Actuator limit (N)
    'omega_s': 2*np.pi*100, # Sampling frequency (rad/s)
    'Delta_max': 20.0,      # Uncertainty bound (N)
    'u_eq_max': 80.0,       # Peak equivalent control (N)
}

# Run all validation checks
results = validate_all_criteria(gains, validation_config)

print("\\nValidation Results:")
print("=" * 50)
for criterion, passed in results.items():
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{criterion:30s}: {status}")

if all(results.values()):
    print("\\n✓ All validation criteria passed")
else:
    print("\\n✗ Some validation criteria failed")
```"""

    def _smc_factory_examples(self) -> str:
        return """## Usage Examples

### Example 1: Basic Controller Creation

```python
from src.controllers.factory import SMCType, create_controller

# Create classical SMC controller
controller = create_controller(
    ctrl_type=SMCType.CLASSICAL,
    gains=[10.0, 8.0, 15.0, 12.0, 50.0, 0.01],
    max_force=100.0,
    dt=0.01
)

# Use controller
state = np.array([0.1, 0.0, 0.05, 0.1, 0.02, 0.05])
u, state_vars, history = controller.compute_control(state, {}, {})
print(f"Control output: {u:.2f} N")
```

### Example 2: Type-Safe Factory Usage

```python
from src.controllers.factory import SMCFactory, SMCConfig

# Create configuration dataclass
config = SMCConfig(
    gains=[10.0, 8.0, 15.0, 12.0, 50.0, 0.01],
    max_force=100.0,
    dt=0.01,
    boundary_layer=0.01
)

# Factory ensures type safety
controller = SMCFactory.create_controller(SMCType.CLASSICAL, config)

# mypy validates this at compile time!
```

### Example 3: Gain Specification Query

```python
from src.controllers.factory import SMCFactory, SMCType

# Get gain requirements for each controller type
for ctrl_type in SMCType:
    spec = SMCFactory.get_gain_specification(ctrl_type)
    print(f"\\n{ctrl_type.value}:")
    print(f"  Number of gains: {spec.n_gains}")
    print(f"  Gain names:      {spec.gain_names}")
    print(f"  Bounds:          {spec.bounds}")
```

### Example 4: Dynamic Controller Registry

```python
from src.controllers.factory.core.registry import ControllerRegistry

# View registered controllers
registry = ControllerRegistry()
registered_types = registry.list_controllers()

print("Registered Controllers:")
for ctrl_type in registered_types:
    factory_fn = registry.get_factory(ctrl_type)
    print(f"  {ctrl_type.value}: {factory_fn.__name__}")

# Register custom controller (plugin architecture)
def create_custom_smc(config):
    return CustomSMC(**config)

registry.register(SMCType.CUSTOM, create_custom_smc)
```

### Example 5: Batch Controller Creation

```python
from src.controllers.factory import create_all_smc_controllers

# Gains for each controller type
gains_dict = {
    "classical": [10, 8, 15, 12, 50, 0.01],
    "adaptive": [10, 8, 15, 12, 0.5],
    "sta": [25, 10, 15, 12, 20, 15],
    "hybrid": [15, 12, 18, 15]
}

# Create all controllers for comparison
controllers = create_all_smc_controllers(
    gains_dict,
    max_force=100.0,
    dt=0.01
)

# Simulate each controller
results = {}
for ctrl_name, controller in controllers.items():
    result = simulate(controller, duration=5.0)
    results[ctrl_name] = result
    print(f"{ctrl_name}: ITAE={result.itae:.3f}")
```"""

    def _pso_integration_examples(self) -> str:
        return """## Usage Examples

### Example 1: Basic PSO-Controller Integration

```python
from src.controllers.factory import create_smc_for_pso, SMCType, get_gain_bounds_for_pso
from src.optimizer.pso_optimizer import PSOTuner

# Get parameter bounds for Classical SMC
bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)

# Define fitness function
def fitness_function(gains):
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)
    result = simulate(controller, duration=5.0)
    return result.itae + 0.1 * result.rms_control

# Initialize PSO
pso = PSOTuner(
    n_particles=30,
    bounds=bounds,
    fitness_function=fitness_function
)

# Optimize
best_gains, best_fitness = pso.optimize(max_iterations=50)
print(f"Optimal gains: {best_gains}")
print(f"Best fitness:  {best_fitness:.4f}")
```

### Example 2: Multi-Objective Optimization

```python
# Multi-objective cost function
def multi_objective_fitness(gains):
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)
    result = simulate(controller, duration=5.0)

    # Weighted sum of objectives
    w_itae = 1.0     # Tracking error
    w_control = 0.1  # Control effort
    w_chat = 0.05    # Chattering
    w_viol = 10.0    # Constraint violations

    cost = (w_itae * result.itae +
            w_control * result.rms_control +
            w_chat * result.chattering_index +
            w_viol * result.violation_count)

    return cost

pso = PSOTuner(
    n_particles=30,
    bounds=bounds,
    fitness_function=multi_objective_fitness
)

best_gains, best_cost = pso.optimize(max_iterations=100)
```

### Example 3: Convergence Monitoring

```python
# PSO with convergence callback
def convergence_callback(iteration, best_fitness, diversity):
    print(f"Iteration {iteration:3d}: "
          f"Fitness={best_fitness:.4f}, "
          f"Diversity={diversity:.4f}")

    # Early stopping if fitness stagnant
    if iteration > 20:
        fitness_history = pso.get_fitness_history()
        improvement = abs(fitness_history[-1] - fitness_history[-10]) / fitness_history[-10]
        if improvement < 1e-4:
            print("Early stopping: convergence detected")
            return True  # Stop optimization
    return False

pso = PSOTuner(
    n_particles=30,
    bounds=bounds,
    fitness_function=fitness_function,
    convergence_callback=convergence_callback
)

best_gains, _ = pso.optimize(max_iterations=200)
```

### Example 4: Constraint Handling

```python
# Fitness with constraint penalties
def constrained_fitness(gains):
    # Create controller
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains)

    # Validate gains first (cheap check)
    from src.controllers.smc.core.gain_validation import validate_all_criteria

    validation_config = {
        'u_max': 100.0,
        'omega_s': 2*np.pi*100,
        'Delta_max': 20.0,
        'u_eq_max': 80.0,
    }

    results = validate_all_criteria(gains, validation_config)

    # Heavy penalty for invalid gains
    if not all(results.values()):
        return 1e6  # Return worst fitness

    # Simulate only if gains valid
    result = simulate(controller, duration=5.0)
    return result.itae

pso = PSOTuner(n_particles=30, bounds=bounds, fitness_function=constrained_fitness)
best_gains, _ = pso.optimize(max_iterations=100)
```

### Example 5: Batch Fitness Evaluation (Parallel)

```python
from joblib import Parallel, delayed

# Parallel fitness evaluation
def batch_fitness(gains_population):
    \"\"\"Evaluate all particles in parallel.\"\"\"

    def eval_single(gains):
        controller = create_smc_for_pso(SMCType.CLASSICAL, gains)
        result = simulate(controller, duration=5.0)
        return result.itae

    # Parallel execution (8 cores)
    fitness_values = Parallel(n_jobs=8)(
        delayed(eval_single)(gains) for gains in gains_population
    )

    return np.array(fitness_values)

# PSO with batch evaluation
pso = PSOTuner(
    n_particles=30,
    bounds=bounds,
    fitness_function=batch_fitness,  # Pass batch function
    batch_mode=True
)

best_gains, _ = pso.optimize(max_iterations=50)
print(f"Speedup: ~8x using parallel evaluation")
```"""

    def _controller_interface_examples(self) -> str:
        return """## Usage Examples

### Example 1: Basic Controller Protocol Usage

```python
from src.controllers.base.controller_interface import ControllerProtocol
import numpy as np

def simulate(controller: ControllerProtocol, duration: float):
    \"\"\"Simulate with any controller implementing the protocol.\"\"\"

    # Initialize
    state_vars = {}
    history = controller.initialize_history()

    # Simulation loop
    state = np.array([0.1, 0.0, 0.05, 0.1, 0.02, 0.05])

    for t in np.arange(0, duration, 0.01):
        u, state_vars, history = controller.compute_control(
            state, state_vars, history
        )
        # ... integrate dynamics

    return history

# Works with ANY controller implementing ControllerProtocol
from src.controllers import ClassicalSMC, AdaptiveSMC

classical = ClassicalSMC(gains=[10, 8, 15, 12, 50, 0.01])
adaptive = AdaptiveSMC(gains=[10, 8, 15, 12, 0.5])

result_classical = simulate(classical, duration=5.0)
result_adaptive = simulate(adaptive, duration=5.0)
```

### Example 2: Duck Typing vs Explicit Protocol

```python
# Duck typing (no type checking)
def simulate_duck(controller):  # No type hint
    u = controller.compute_control(state, {}, {})  # Hope it works!
    return u

# Explicit protocol (type-safe)
def simulate_protocol(controller: ControllerProtocol):
    u, _, _ = controller.compute_control(state, {}, {})  # mypy validates!
    return u

# mypy catches errors at compile time:
# simulate_protocol(None)  # Error: None doesn't implement ControllerProtocol
# simulate_protocol("foo")  # Error: str doesn't implement ControllerProtocol
```

### Example 3: Liskov Substitution Principle

```python
# Base class behavior
from src.controllers.base import Controller

def reset_controller(controller: Controller):
    \"\"\"Works with any Controller subclass.\"\"\"
    history = controller.reset()
    return history

# Works for all subclasses
classical = ClassicalSMC(gains=[10, 8, 15, 12, 50, 0.01])
adaptive = AdaptiveSMC(gains=[10, 8, 15, 12, 0.5])

history_classical = reset_controller(classical)  # Works
history_adaptive = reset_controller(adaptive)    # Works

# Substitutability guaranteed by LSP
```

### Example 4: State Variable Pattern

```python
# Controller with internal state (e.g., adaptation)
class AdaptiveController(Controller):
    def compute_control(self, state, state_vars, history):
        # Extract previous state
        K = state_vars.get('K', self.K_initial)
        integral = state_vars.get('integral', 0.0)

        # Compute control
        s = self.compute_sliding_surface(state)
        K_new = K + self.gamma * abs(s) * self.dt
        integral_new = integral + s * self.dt

        u = -K_new * np.tanh(s / self.epsilon)

        # Return updated state
        return u, {'K': K_new, 'integral': integral_new}, history

# State is fully captured in state_vars
state_vars = {}
for i in range(100):
    u, state_vars, history = controller.compute_control(state, state_vars, history)
    # state_vars contains full controller state for reproducibility
```

### Example 5: Custom Controller Implementation

```python
from src.controllers.base.controller_interface import Controller
from abc import ABC

class MyCustomSMC(Controller):
    \"\"\"Custom SMC implementation.\"\"\"

    def __init__(self, gains, max_force):
        self.gains = gains
        self.max_force = max_force

    def compute_control(self, state, state_vars, history):
        # Custom control law
        theta1, theta2 = state[2], state[4]
        theta1_dot, theta2_dot = state[3], state[5]

        # Custom sliding surface
        s = self.gains[0] * theta1 + self.gains[1] * theta1_dot

        # Custom switching law
        u = -self.gains[2] * np.sign(s)
        u = np.clip(u, -self.max_force, self.max_force)

        return u, state_vars, history

    def initialize_history(self):
        return {'states': [], 'times': []}

# Use custom controller with existing simulation infrastructure
custom_controller = MyCustomSMC(gains=[10.0, 5.0, 50.0], max_force=100.0)
result = simulate(custom_controller, duration=5.0)  # Works!
```"""

    def _control_primitives_examples(self) -> str:
        return """## Usage Examples

### Example 1: Saturation Primitive

```python
from src.controllers.base.control_primitives import saturate

# Apply saturation to control signal
u_raw = 150.0  # Exceeds actuator limit
u_max = 100.0

u = saturate(u_raw, u_max)
print(f"Saturated control: {u:.1f} N")  # 100.0 N

# Vectorized saturation
u_raw_array = np.array([150.0, 50.0, -120.0, 30.0])
u_array = saturate(u_raw_array, u_max)
print(f"Saturated controls: {u_array}")  # [100, 50, -100, 30]
```

### Example 2: Rate Limiter

```python
from src.controllers.base.control_primitives import rate_limit

# Current and previous control
u_current = 80.0
u_previous = 40.0
dt = 0.01  # Time step
u_dot_max = 1000.0  # N/s

# Apply rate limiting
u_limited = rate_limit(u_current, u_previous, u_dot_max, dt)

# Maximum allowed change: 1000 * 0.01 = 10 N
# Requested change: 80 - 40 = 40 N
# Limited change: 10 N
print(f"Rate-limited control: {u_limited:.1f} N")  # 50.0 N
```

### Example 3: Anti-Windup

```python
from src.controllers.base.control_primitives import anti_windup_back_calculation

# PID-like controller with integral term
integral = 5.0  # Accumulated integral error
u_raw = 150.0   # Requested control
u_max = 100.0

# Saturated control
u_sat = saturate(u_raw, u_max)  # 100.0 N

# Back-calculation anti-windup
T_i = 1.0  # Integration time constant
integral_correction = (u_sat - u_raw) / T_i  # Negative (reduces integral)

integral_new = integral + integral_correction * dt
print(f"Integral before: {integral:.3f}")
print(f"Integral after:  {integral_new:.3f}")  # Reduced
```

### Example 4: Low-Pass Filter

```python
from src.controllers.base.control_primitives import low_pass_filter

# Noisy control signal
u_noisy = 50.0 + 5.0 * np.random.randn()

# Filter parameters
omega_c = 20.0  # Cutoff frequency (rad/s)
dt = 0.01
tau = 1.0 / omega_c  # Time constant

# Apply filter
u_filtered_prev = 48.0  # Previous filtered value
u_filtered = low_pass_filter(u_noisy, u_filtered_prev, tau, dt)

print(f"Noisy control:    {u_noisy:.2f} N")
print(f"Filtered control: {u_filtered:.2f} N")
```

### Example 5: Complete Control Pipeline

```python
from src.controllers.base.control_primitives import (
    saturate, rate_limit, low_pass_filter, deadband
)

# Control pipeline
class ControlPipeline:
    def __init__(self, u_max, u_dot_max, tau_filter, deadband_threshold):
        self.u_max = u_max
        self.u_dot_max = u_dot_max
        self.tau = tau_filter
        self.deadband = deadband_threshold
        self.u_prev = 0.0
        self.u_filtered_prev = 0.0

    def process(self, u_raw, dt):
        # 1. Deadband (ignore small errors)
        u1 = deadband(u_raw, self.deadband)

        # 2. Rate limiting (prevent slew violations)
        u2 = rate_limit(u1, self.u_prev, self.u_dot_max, dt)

        # 3. Saturation (enforce actuator limits)
        u3 = saturate(u2, self.u_max)

        # 4. Low-pass filter (reduce high-frequency content)
        u4 = low_pass_filter(u3, self.u_filtered_prev, self.tau, dt)

        # Update history
        self.u_prev = u3  # Before filtering for rate limiting
        self.u_filtered_prev = u4

        return u4

# Usage
pipeline = ControlPipeline(
    u_max=100.0,
    u_dot_max=1000.0,
    tau_filter=0.05,
    deadband_threshold=0.5
)

u_raw = -75.0  # Raw controller output
u_final = pipeline.process(u_raw, dt=0.01)
print(f"Final control: {u_final:.2f} N")
```"""

    def _print_summary(self):
        """Print enhancement summary statistics."""
        print("\n" + "="*80)
        print("ENHANCEMENT SUMMARY")
        print("="*80)
        print(f"Files enhanced: {self.stats.files_enhanced}")
        print(f"Lines added:    {self.stats.lines_added}")

        if self.stats.errors:
            print(f"\nErrors: {len(self.stats.errors)}")
            for error in self.stats.errors:
                print(f"  - {error}")
        else:
            print("\nAll files enhanced successfully!")

        print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description="Enhance controllers core documentation for Week 9 Phase 1"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be done without making changes"
    )
    args = parser.parse_args()

    # Project root is 2 levels up from this script
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    docs_root = project_root / 'docs'

    enhancer = ControllersDocEnhancer(docs_root, dry_run=args.dry_run)
    enhancer.enhance_all_files()


if __name__ == '__main__':
    main()
