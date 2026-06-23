[<--Back to Beginner Roadmap](../beginner-roadmap.md)

---

# Phase 4: Advancing Skills (Week 13-16, ~30 hours)

::::{card}
:class-card: breadcrumb-container

:::{raw} html
<nav aria-label="Learning path breadcrumb" class="breadcrumb-nav">
  <ol class="breadcrumb-list">
    <li class="breadcrumb-item">
      <a href="../beginner-roadmap.html" class="breadcrumb-link">Beginner Roadmap</a>
    </li>
    <li class="breadcrumb-separator" aria-hidden="true">›</li>
    <li class="breadcrumb-item breadcrumb-active" aria-current="page">
      <span class="phase-badge phase-4">Phase 4</span>
      <span class="breadcrumb-text">Advancing Skills</span>
    </li>
  </ol>
</nav>
:::

::::

---

**Prerequisites**: Phase 1-3 completion
**Previous Phase**: [Phase 3: Hands-On Learning](phase-3-hands-on.md)
**Next Phase**: [Phase 5: Mastery Path](phase-5-mastery.md)

**Goal**: Develop advanced Python skills, learn to read source code, and understand the mathematics behind SMC.

## Phase 4 Overview

| Sub-Phase | Topic | Time | Why You Need This |
|-----------|-------|------|-------------------|
| 4.1 | Advanced Python for This Project | 12 hours | Understand code structure |
| 4.2 | Reading Controller Source Code | 8 hours | Learn from implementation |
| 4.3 | Advanced Math for SMC | 10 hours | Grasp theoretical foundation |

**Total**: ~30 hours over 4 weeks (~7-8 hours/week)

---

<details>
<summary>4.1 Advanced Python for This Project</summary>

## Phase 4.1: Advanced Python for This Project (12 hours)

**Goal**: Master Python concepts used in this codebase - classes, inheritance, decorators, type hints, and testing.

### Learning Path

**Step 1: Classes and Objects (4 hours)**

**Why Classes?**

Controllers are implemented as classes to:
- Encapsulate state (gains, parameters)
- Share common interface (all controllers have `compute_control()`)
- Enable polymorphism (swap controllers easily)

**Example: Controller Base Class**

```python
# src/controllers/base.py (simplified)

from abc import ABC, abstractmethod
import numpy as np

class ControllerInterface(ABC):
    """
    Abstract base class for all controllers.
    Defines the interface that all controllers must implement.
    """

    def __init__(self, gains: list, config: dict):
        """
        Initialize controller with gains and configuration.

        Args:
            gains: List of controller gains [k1, k2, ..., kn]
            config: Configuration dictionary
        """
        self.gains = gains
        self.config = config
        self.last_control = 0.0  # Store last control output
        self.history = []        # Store control history

    @abstractmethod
    def compute_control(self, state: np.ndarray, dt: float) -> float:
        """
        Compute control output for given state.

        This method MUST be implemented by all subclasses.

        Args:
            state: System state [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]
            dt: Timestep (seconds)

        Returns:
            Control force F (Newtons)
        """
        pass  # Subclasses provide implementation

    def reset(self):
        """Reset controller state."""
        self.last_control = 0.0
        self.history = []
```

**Key Concepts**:

1. **Abstract Base Class (ABC)**: Template for other classes
2. **@abstractmethod**: Forces subclasses to implement method
3. **`__init__`**: Constructor, runs when object created
4. **Attributes**: `self.gains`, `self.last_control` (object state)
5. **Methods**: Functions that belong to the class

**Try This** (in Python interpreter):

```python
from src.controllers.base import ControllerInterface
# Can't instantiate abstract class
# controller = ControllerInterface(...)  # Error!

# Must use concrete subclass
from src.controllers.classical_smc import ClassicalSMC
controller = ClassicalSMC(gains=[10, 5, 8, 3, 15, 2])
print(type(controller))  # <class 'ClassicalSMC'>
print(isinstance(controller, ControllerInterface))  # True
```

---

**Step 2: Inheritance (3 hours)**

**Why Inheritance?**

All controllers share common functionality (reset, history tracking) but have different control laws.

**Example: Classical SMC Inherits from Base**

```python
# src/controllers/classical_smc.py (simplified)

import numpy as np
from .base import ControllerInterface

class ClassicalSMC(ControllerInterface):
    """
    Classical Sliding Mode Controller implementation.
    Inherits from ControllerInterface.
    """

    def __init__(self, gains: list, boundary_layer: float = 0.1):
        # Call parent class constructor
        super().__init__(gains, config={})

        # Unpack gains
        self.k1, self.k2, self.k3, self.k4, self.k5, self.eta = gains
        self.boundary_layer = boundary_layer

    def compute_control(self, state: np.ndarray, dt: float) -> float:
        """
        Implement classical SMC control law.
        This is the REQUIRED abstract method from parent class.
        """
        # Extract state variables
        x, x_dot, theta1, theta1_dot, theta2, theta2_dot = state

        # Define sliding surface
        s1 = theta1 + self.k1 * theta1_dot
        s2 = theta2 + self.k2 * theta2_dot

        # Compute control law
        u_eq = -(self.k3 * x + self.k4 * x_dot)  # Equivalent control
        u_sw = -self.eta * np.tanh(s1/self.boundary_layer + s2/self.boundary_layer)  # Switching control

        F = u_eq + u_sw  # Total control

        # Saturate (limit force to [-20, 20] N)
        F = np.clip(F, -20.0, 20.0)

        # Store history
        self.last_control = F
        self.history.append(F)

        return F

    # Inherits reset() method from parent - no need to redefine
```

**Source Code Navigation Tree**:

```{mermaid}
:alt: Source code file structure showing organization of controllers, dynamics, optimization, and utility modules
:align: center

%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#9B59B6','primaryTextColor':'#fff','primaryBorderColor':'#8E44AD','lineColor':'#8E44AD','secondaryColor':'#E8DAEF','tertiaryColor':'#fff'}}}%%
graph TD
    A[src/] --> B[controllers/]
    A --> C[core/]
    A --> D[optimizer/]
    A --> E[utils/]

    B --> B1[base.py<br/>Interface]
    B --> B2[classical_smc.py]
    B --> B3[sta_smc.py]
    B --> B4[adaptive_smc.py]
    B --> B5[factory.py]

    C --> C1[dynamics.py]
    C --> C2[simulation_runner.py]

    D --> D1[pso_optimizer.py]

    E --> E1[validation/]
    E --> E2[visualization/]

    style A fill:#9B59B6,stroke:#8E44AD,stroke-width:2px,color:#fff
    style B fill:#E8DAEF,stroke:#8E44AD,stroke-width:2px
    style C fill:#E8DAEF,stroke:#8E44AD,stroke-width:2px
    style D fill:#E8DAEF,stroke:#8E44AD,stroke-width:2px
    style E fill:#E8DAEF,stroke:#8E44AD,stroke-width:2px
```

**Benefits**:
- All controllers have same interface (`compute_control()`)
- Can swap controllers without changing simulation code
- Shared functionality (reset, history) written once

---

**Step 3: Decorators (2 hours)**

**What are Decorators?**

Functions that modify other functions (like "wrappers").

**Example: Timing Decorator**

```python
# src/utils/timing.py (simplified)

import time
from functools import wraps

def timing_decorator(func):
    """
    Decorator that measures function execution time.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)  # Call original function
        end_time = time.time()

        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result

    return wrapper

# Usage
@timing_decorator
def run_simulation():
    # ... simulation code ...
    pass

# Equivalent to:
# run_simulation = timing_decorator(run_simulation)
```

**Validation Decorator**:

```python
def validate_inputs(func):
    """
    Decorator that validates state vector before computing control.
    """
    @wraps(func)
    def wrapper(self, state, dt):
        # Validate state
        if len(state) != 6:
            raise ValueError(f"State must have 6 elements, got {len(state)}")

        if np.any(np.isnan(state)):
            raise ValueError("State contains NaN values")

        # Call original function
        return func(self, state, dt)

    return wrapper

# Usage in controller
class ClassicalSMC(ControllerInterface):
    @validate_inputs  # Function decorated
    def compute_control(self, state, dt):
        # ... implementation ...
        pass
```

**Common Decorators in This Project**:
- `@timing_decorator`: Measure performance
- `@validate_inputs`: Check preconditions
- `@abstractmethod`: Mark method as required in subclass

---

**Step 4: Type Hints (1.5 hours)**

**What are Type Hints?**

Optional annotations that specify expected types (improves readability, enables static analysis).

**Example**:

```python
# Without type hints (confusing)
def compute_control(self, state, dt):
    pass

# With type hints (clear!)
def compute_control(self, state: np.ndarray, dt: float) -> float:
    """
    Args:
        state: System state vector (6 elements)
        dt: Timestep in seconds

    Returns:
        Control force in Newtons
    """
    pass
```

**Common Types**:

```python
from typing import List, Dict, Optional, Tuple

gains: List[float] = [10.0, 5.0, 8.0]
config: Dict[str, float] = {"mass": 1.0, "length": 0.5}
result: Optional[float] = None  # Can be float or None
position, velocity: Tuple[float, float] = (0.5, 0.1)
```

**Benefits**:
- Self-documenting code
- IDE autocomplete works better
- `mypy` catches type errors before runtime

---

**Step 5: Testing with pytest (1.5 hours)**

**Why Testing?**

Ensure code works correctly, catch regressions, document expected behavior.

**Example Test**:

```python
# tests/test_controllers/test_classical_smc.py

import pytest
import numpy as np
from src.controllers.classical_smc import ClassicalSMC

def test_classical_smc_initialization():
    """Test that controller initializes correctly."""
    gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
    controller = ClassicalSMC(gains)

    assert controller.k1 == 10.0
    assert controller.k2 == 5.0
    assert len(controller.history) == 0

def test_compute_control_returns_float():
    """Test that compute_control returns a number."""
    controller = ClassicalSMC([10, 5, 8, 3, 15, 2])
    state = np.zeros(6)  # Equilibrium state
    dt = 0.01

    F = controller.compute_control(state, dt)

    assert isinstance(F, (float, np.floating))
    assert not np.isnan(F)

def test_control_saturates():
    """Test that control force saturates at limits."""
    controller = ClassicalSMC([100, 50, 80, 30, 150, 20])  # Very high gains
    state = np.array([0.5, 0, 0.5, 0, 0.5, 0])  # Large disturbance
    dt = 0.01

    F = controller.compute_control(state, dt)

    assert -20.0 <= F <= 20.0  # Within saturation limits
```

**Running Tests**:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_controllers/test_classical_smc.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src
```

---

### Self-Assessment: Phase 4.1

**Quiz**:

1. What is an abstract base class?
2. What does inheritance allow us to do?
3. What are decorators used for?
4. What are the benefits of type hints?
5. Why do we write tests?

**Practical Exercise**:

1. Read `src/controllers/base.py` (the actual file)
2. Identify: abstract methods, attributes, concrete methods
3. Explain in your own words what `@abstractmethod` does

**If you can complete quiz and exercise**: ✅ Move to Phase 4.2
**If struggling with classes**: ⚠️ Review Python OOP tutorials online
**If struggling with decorators**: ⚠️ Watch "Python Decorators Explained" videos

**Resources**:
- [Python Classes Tutorial (Real Python, 30 min)](https://realpython.com/python3-object-oriented-programming/)
- [Decorators Explained (YouTube, 15 min)](https://www.youtube.com/results?search_query=python+decorators+explained)
- [Type Hints Crash Course (Article, 20 min)](https://realpython.com/python-type-checking/)

</details>

---

<details>
<summary>4.2 Reading Controller Source Code</summary>

## Phase 4.2: Reading Controller Source Code (8 hours)

**Goal**: Understand controller implementations line by line.

### Learning Path

**Step 1: Navigating the Codebase (2 hours)**

**Directory Structure**:

```
src/controllers/
├─ base.py                      # Abstract interface
├─ classical_smc.py             # Classical SMC (START HERE)
├─ sta_smc.py                   # Super-Twisting
├─ adaptive_smc.py              # Adaptive
├─ hybrid_adaptive_sta_smc.py   # Hybrid
└─ factory.py                   # Controller creation
```

**Reading Order**:
1. `base.py` - Understand interface
2. `classical_smc.py` - Simplest implementation
3. `sta_smc.py` - More complex
4. `factory.py` - How controllers are instantiated

**Open classical_smc.py** (recommended editor: VS Code):

```bash
code src/controllers/classical_smc.py  # VS Code
# Or use any text editor
```

---

**Step 2: Classical SMC Line-by-Line (4 hours)**

**Section 1: Imports and Class Definition**

```python
import numpy as np
from typing import Optional
from .base import ControllerInterface

class ClassicalSMC(ControllerInterface):
    """
    Classical Sliding Mode Controller.

    Implements the standard SMC control law with:
    - Linear sliding surface
    - Boundary layer to reduce chattering
    - Saturation limits

    Reference: Slotine & Li (1991), "Applied Nonlinear Control"
    """
```

**What this means**:
- Imports NumPy for math operations
- Imports type hints for clarity
- Inherits from `ControllerInterface` (must implement `compute_control()`)
- Docstring explains what this class does

---

**Section 2: Initialization**

```python
def __init__(
    self,
    gains: list[float],
    boundary_layer: float = 0.1,
    saturation_limits: tuple[float, float] = (-20.0, 20.0)
):
    """
    Initialize Classical SMC controller.

    Args:
        gains: [k1, k2, k3, k4, k5, eta]
            k1, k2: Sliding surface coefficients for pendulums
            k3, k4: Equivalent control gains for cart
            k5: Pendulum coupling gain
            eta: Switching control gain
        boundary_layer: Width of boundary layer (reduces chattering)
        saturation_limits: (min_force, max_force) in Newtons
    """
    super().__init__(gains, config={})  # Call parent constructor

    # Unpack gains (validate length)
    if len(gains) != 6:
        raise ValueError(f"Classical SMC requires 6 gains, got {len(gains)}")

    self.k1, self.k2, self.k3, self.k4, self.k5, self.eta = gains

    # Store parameters
    self.boundary_layer = boundary_layer
    self.sat_min, self.sat_max = saturation_limits

    # Initialize internal state
    self.last_control = 0.0
    self.history = []
```

**What this does**:
- Takes gains as input (6 numbers)
- Validates input (must be exactly 6 gains)
- Unpacks gains into meaningful names (k1, k2, ...)
- Stores boundary layer and saturation limits
- Initializes control history

**Try This**:
```python
# Good initialization
controller = ClassicalSMC([10, 5, 8, 3, 15, 2])

# Bad initialization (wrong number of gains)
# controller = ClassicalSMC([10, 5])  # Raises ValueError
```

---

**Section 3: Control Law Implementation**

```python
def compute_control(self, state: np.ndarray, dt: float) -> float:
    """
    Compute control force using classical SMC law.

    Args:
        state: [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]
        dt: Timestep (not used in classical SMC, but required by interface)

    Returns:
        Control force F in Newtons (saturated to limits)
    """
    # 1. Extract state variables
    x = state[0]          # Cart position (m)
    x_dot = state[1]      # Cart velocity (m/s)
    theta1 = state[2]     # Pendulum 1 angle (rad)
    theta1_dot = state[3] # Pendulum 1 angular velocity (rad/s)
    theta2 = state[4]     # Pendulum 2 angle (rad)
    theta2_dot = state[5] # Pendulum 2 angular velocity (rad/s)

    # 2. Define sliding surfaces
    # Sliding surface forces theta + k*theta_dot -> 0
    s1 = theta1 + self.k1 * theta1_dot  # Pendulum 1 sliding variable
    s2 = theta2 + self.k2 * theta2_dot  # Pendulum 2 sliding variable

    # 3. Equivalent control (stabilizes cart position)
    u_eq = -(self.k3 * x + self.k4 * x_dot)

    # 4. Switching control (drives sliding variables to zero)
    # Uses tanh (smooth approximation) instead of sign (discontinuous)
    combined_s = s1 + self.k5 * s2  # Combine sliding surfaces
    u_sw = -self.eta * np.tanh(combined_s / self.boundary_layer)

    # 5. Total control = equivalent + switching
    F = u_eq + u_sw

    # 6. Apply saturation (physical actuator limits)
    F = np.clip(F, self.sat_min, self.sat_max)

    # 7. Store for history/debugging
    self.last_control = F
    self.history.append(F)

    return F
```

**Breaking Down the Math**:

**Sliding Surface** (s1, s2):
- Combines angle and angular velocity
- When s = 0, system is on sliding manifold
- System converges exponentially to equilibrium on manifold

**Equivalent Control** (u_eq):
- Stabilizes cart position
- Linear feedback: proportional to position error and velocity

**Switching Control** (u_sw):
- Drives system toward sliding surface
- High gain (eta) provides robustness
- tanh smooths sign function (reduces chattering)

**Boundary Layer**:
- Region where tanh ≈ linear (not saturated)
- Wider layer --> smoother control, slower convergence
- Narrower layer --> faster convergence, more chattering

**Saturation**:
- Real actuators have force limits
- `np.clip()` enforces [-20, 20] N

---

**Section 4: Helper Methods**

```python
def reset(self):
    """Reset controller state (clear history)."""
    super().reset()  # Call parent reset
    self.last_control = 0.0
    self.history = []

def get_gains(self) -> list[float]:
    """Return current gains as list."""
    return [self.k1, self.k2, self.k3, self.k4, self.k5, self.eta]

def set_gains(self, gains: list[float]):
    """Update controller gains."""
    if len(gains) != 6:
        raise ValueError(f"Requires 6 gains, got {len(gains)}")
    self.k1, self.k2, self.k3, self.k4, self.k5, self.eta = gains
```

**What these do**:
- `reset()`: Clear history between simulations
- `get_gains()`: Retrieve current gains (for saving)
- `set_gains()`: Update gains dynamically (for optimization)

---

**Controller Comparison Matrix**:

```{mermaid}
:alt: Controller performance comparison matrix showing trade-offs between classical, super-twisting, adaptive, and hybrid SMC variants
:align: center

%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#9B59B6','primaryTextColor':'#fff','primaryBorderColor':'#8E44AD','lineColor':'#8E44AD','secondaryColor':'#E8DAEF','tertiaryColor':'#fff'}}}%%
graph TD
    A[Controller Types] --> B[Classical SMC]
    A --> C[Super-Twisting STA]
    A --> D[Adaptive SMC]
    A --> E[Hybrid Adaptive STA]

    B --> B1[Speed: Medium<br/>Chattering: Moderate<br/>Complexity: Low]
    C --> C1[Speed: Fast<br/>Chattering: Low<br/>Complexity: Medium]
    D --> D1[Speed: Variable<br/>Chattering: Moderate<br/>Complexity: High]
    E --> E1[Speed: Fast<br/>Chattering: Very Low<br/>Complexity: High]

    style A fill:#9B59B6,stroke:#8E44AD,stroke-width:2px,color:#fff
    style B fill:#E8DAEF,stroke:#8E44AD,stroke-width:2px
    style C fill:#E8DAEF,stroke:#8E44AD,stroke-width:2px
    style D fill:#E8DAEF,stroke:#8E44AD,stroke-width:2px
    style E fill:#10b981,stroke:#059669,stroke-width:3px,color:#fff
    style B1 fill:#FEF3C7,stroke:#F59E0B,stroke-width:2px
    style C1 fill:#D1FAE5,stroke:#10b981,stroke-width:2px
    style D1 fill:#FEF3C7,stroke:#F59E0B,stroke-width:2px
    style E1 fill:#D1FAE5,stroke:#10b981,stroke-width:2px
```

---

### Self-Assessment: Phase 4.2

**Quiz**:

1. What are the 6 gains in Classical SMC and what do they control?
2. What is a sliding surface?
3. Why use `tanh` instead of `sign` function?
4. What does the boundary layer parameter control?
5. Why is saturation necessary?

**Practical Exercise**:

1. Open `src/controllers/classical_smc.py` in your editor
2. Add print statements to `compute_control()`:
   ```python
   print(f"s1 = {s1:.4f}, s2 = {s2:.4f}")
   print(f"u_eq = {u_eq:.4f}, u_sw = {u_sw:.4f}")
   ```
3. Run simulation, observe how s1, s2 evolve
4. Remove prints when done

**If you can complete quiz and exercise**: ✅ Move to Phase 4.3
**If sliding surface confusing**: ⚠️ Review Phase 2.3 (SMC theory)
**If code unclear**: ⚠️ Add more print statements, run with small disturbance

**Resources**:
- [SMC Control Law Explained (Video, 12 min)](https://www.youtube.com/results?search_query=sliding+mode+control+explained)
- [Boundary Layer in SMC (Article)](https://www.sciencedirect.com/topics/engineering/boundary-layer-method)

</details>

---

<details>
<summary>4.3 Advanced Math for SMC</summary>

## Phase 4.3: Advanced Math for SMC (10 hours)

**Goal**: Understand the mathematical foundation - nonlinear dynamics, vector calculus, and Lyapunov stability (conceptual level, not rigorous proofs).

### Learning Path

**Step 1: Full Nonlinear Equations (3 hours)**

**Why Full Equations?**

In Phase 2, we used intuition. Now we see the actual equations.

**Math Concepts Glossary Map**:

```{mermaid}
:alt: Mathematical concepts glossary showing relationships between key equations, derivatives, matrices, and control theory foundations
:align: center

%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#9B59B6','primaryTextColor':'#fff','primaryBorderColor':'#8E44AD','lineColor':'#8E44AD','secondaryColor':'#E8DAEF','tertiaryColor':'#fff'}}}%%
mindmap
  root((Math for SMC))
    Lagrangian Mechanics
      Kinetic Energy T
      Potential Energy V
      L = T - V
      Euler-Lagrange Equations
    Linear Algebra
      Mass Matrix M θ
      State Vector x θ ẋ θ̇
      Matrix Inversion
      Jacobian
    Calculus
      Time Derivatives ẋ ẍ
      Partial Derivatives ∂f/∂x
      Chain Rule
      Gradient ∇V
    Control Theory
      Sliding Surface s
      Lyapunov Function V
      Stability Analysis
      Finite-Time Convergence
```

**Lagrangian Mechanics** (conceptual):

The DIP is a mechanical system. Its motion is governed by:
1. **Kinetic Energy** (T): Energy of motion
2. **Potential Energy** (V): Energy of position (gravity)
3. **Lagrangian**: L = T - V
4. **Euler-Lagrange Equations**: Derive equations of motion from L

**Equations of Motion** (simplified notation):

```
M(θ) * q̈ + C(θ, θ̇) * θ̇ + G(θ) = B * F

Where:
- q = [x, theta1, theta2]          # Generalized coordinates
- M(θ) = Mass matrix (3x3, depends on angles)
- C(θ, θ̇) = Coriolis/centrifugal terms
- G(θ) = Gravity terms
- B = Input matrix (which DOF F affects)
- F = Control force
```

**Mass Matrix** (conceptual):

```
M(θ) = [
    M + m1 + m2,     m1*L1*cos(θ1) + m2*L*cos(θ1),     m2*L2*cos(θ2)
    m1*L1*cos(θ1),   (m1+m2)*L1²,                      m2*L1*L2*cos(θ1-θ2)
    m2*L2*cos(θ2),   m2*L1*L2*cos(θ1-θ2),              m2*L2²
]
```

**Key Insights**:
- Matrix depends on θ (nonlinear!)
- Coupling between DOF (off-diagonal terms)
- Must be inverted to solve for accelerations

**You DON'T need to derive these**. Key takeaway:
- Equations are complex, nonlinear, coupled
- Numerical solver (ODE integrator) handles them
- Controller doesn't need full model (SMC is robust!)

---

**Step 2: Vector Calculus Basics (3 hours)**

**Why Vector Calculus?**

SMC theory uses derivatives of vector-valued functions.

**Gradients**:

```python
# Scalar function of vector
V(x) = x² + y²  # Energy-like function

# Gradient (vector of partial derivatives)
∇V = [∂V/∂x, ∂V/∂y] = [2x, 2y]
```

**Interpretation**: Gradient points in direction of steepest increase.

**Jacobian Matrix**:

```python
# Vector function of vector
f(q) = [f1(q), f2(q), f3(q)]

# Jacobian (matrix of partial derivatives)
J = [
    [∂f1/∂q1, ∂f1/∂q2, ∂f1/∂q3],
    [∂f2/∂q1, ∂f2/∂q2, ∂f2/∂q3],
    [∂f3/∂q1, ∂f3/∂q2, ∂f3/∂q3],
]
```

**Use in Control**: Linearization around equilibrium

**Time Derivatives of Vectors**:

```python
# State vector
x(t) = [x1(t), x2(t), x3(t)]

# Time derivative
ẋ(t) = [ẋ1(t), ẋ2(t), ẋ3(t)] = dx/dt
```

**Chain Rule** (multivariable):

```
dV/dt = ∇V · ẋ  # Dot product
```

**Example**:

```python
V(x, y) = x² + y²
x(t) = cos(t), y(t) = sin(t)

∇V = [2x, 2y] = [2cos(t), 2sin(t)]
ẋ = [-sin(t), cos(t)]

dV/dt = ∇V · ẋ = 2cos(t)*(-sin(t)) + 2sin(t)*cos(t) = 0  # Energy conserved!
```

---

**Step 3: Lyapunov Stability (Conceptual) (4 hours)**

**What is Lyapunov Stability?**

A method to prove a system converges to equilibrium WITHOUT solving differential equations.

**Analogy**: Imagine a ball rolling in a bowl.
- Bowl = Lyapunov function V(x)
- Ball's position = system state x
- Gravity pulls ball down --> V decreases
- Bottom of bowl = equilibrium (V minimum)
- Ball eventually rests at bottom --> stable

**Formal Definition** (simplified):

A Lyapunov function V(x) is:
1. **Positive Definite**: V(x) > 0 for all x ≠ 0, V(0) = 0
2. **Decreasing**: V̇(x) < 0 along system trajectories

If such V exists, system is stable!

**Example: Pendulum Energy**

```python
# Simple pendulum (no control)
θ̈ + sin(θ) = 0

# Lyapunov function (total energy)
V(θ, θ̇) = (1/2) * θ̇² + (1 - cos(θ))

# Time derivative
V̇ = θ̇ * θ̈ + sin(θ) * θ̇
  = θ̇ * (-sin(θ)) + sin(θ) * θ̇
  = 0  # Energy conserved (no damping)

# Conclusion: System is stable but not asymptotically stable
# (ball rolls forever, doesn't settle)
```

**With Damping**:

```python
θ̈ + b*θ̇ + sin(θ) = 0  # Added damping b*θ̇

V̇ = θ̇ * θ̈ + sin(θ) * θ̇
  = θ̇ * (-b*θ̇ - sin(θ)) + sin(θ) * θ̇
  = -b * θ̇²  # Negative! (energy dissipates)

# Conclusion: System is asymptotically stable (ball settles to bottom)
```

**SMC Lyapunov Function**:

For sliding mode control:

```python
# Sliding variable
s = θ + k * θ̇

# Lyapunov function
V = (1/2) * s²  # "Distance" from sliding surface

# Control law designed such that:
V̇ = s * ṡ < 0  # System approaches surface
```

**Reaching Condition**: System reaches sliding surface in finite time.

**Sliding Condition**: Once on surface, system stays there.

**Convergence**: On sliding surface, system converges to equilibrium.

---

**Phase Portraits and State Space** (visualization, no equations):

**Phase Portrait**: Plot of trajectories in state space.

```
   θ̇ (angular velocity)
    ^
    |     ●------>        <-- Trajectories
    |    /
    |   /
    |  ●------>
    | /
    +--------------------> θ (angle)
    |
    |    Equilibrium (θ=0, θ̇=0) is at origin
```

**Sliding Surface** (in phase space):

```
   θ̇
    ^
    |     ╱ Sliding surface: s = θ + k*θ̇ = 0
    |    ╱   (line in 2D, plane in higher dimensions)
    |   ╱
    |  ╱  <--Trajectories converge to this line
    | ╱
    +╱─────────────────> θ
   ╱ |
```

**Key Insight**: SMC drives system TO the sliding surface, THEN slides along it to equilibrium.

---

**Differential Equation Solvers** (how simulation works):

**SciPy odeint**:

```python
from scipy.integrate import odeint

# Define system dynamics
def dip_dynamics(state, t, controller):
    """
    Compute state derivatives.

    Args:
        state: [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]
        t: Current time
        controller: Controller object

    Returns:
        derivatives: [x_dot, x_ddot, theta1_dot, theta1_ddot, theta2_dot, theta2_ddot]
    """
    # Compute control force
    F = controller.compute_control(state, dt=0.01)

    # Compute accelerations (using M, C, G matrices - hidden complexity)
    x_ddot = f1(state, F)
    theta1_ddot = f2(state, F)
    theta2_ddot = f3(state, F)

    return [state[1], x_ddot, state[3], theta1_ddot, state[5], theta2_ddot]

# Solve ODE
t = np.linspace(0, 10, 1000)  # Time points
state0 = [0, 0, 0.1, 0, 0.1, 0]  # Initial condition
states = odeint(dip_dynamics, state0, t, args=(controller,))
```

**What odeint does**:
1. Start at initial state
2. Compute derivatives using `dip_dynamics()`
3. Take small timestep: state_new ≈ state_old + derivatives * dt
4. Repeat for all timesteps

**Methods**: Runge-Kutta (RK45), Adams, etc. (odeint chooses automatically)

---

### Self-Assessment: Phase 4.3

**Quiz**:

1. What is the Lagrangian and what does it represent?
2. What is a gradient vector?
3. What are the two conditions for a Lyapunov function?
4. What does a phase portrait show?
5. What does odeint do?

**Conceptual Understanding**:

Can you explain (in your own words, no equations):
1. Why DIP equations are "nonlinear"?
2. How Lyapunov functions prove stability without solving equations?
3. What a sliding surface represents geometrically?

**If you can answer conceptually**: 🎉 **Phase 4 COMPLETE!**
**If math too abstract**: ⚠️ Focus on conceptual understanding, skip derivations
**If want deeper math**: ✅ Read Slotine & Li textbook (graduate level)

**Resources**:
- [Lyapunov Stability Intuition (Video, 10 min)](https://www.youtube.com/results?search_query=lyapunov+stability+explained)
- [Phase Portraits (Interactive)](https://www.geogebra.org/m/KPqq8KBQ)
- [Scipy odeint Tutorial (Article, 15 min)](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.odeint.html)

</details>

---


## Learning Resources

```{grid} 1 2 3
:gutter: 2

```{grid-item-card} YouTube: Advanced Python & Math
:link: https://www.youtube.com/results?search_query=python+oop+advanced+lyapunov+stability
:link-type: url
:text-align: center

Watch tutorials on OOP, decorators, and Lyapunov theory
[View -->]

```

```{grid-item-card} Article: Source Code Reading Guide
:link: https://realpython.com/python3-object-oriented-programming/
:link-type: url
:text-align: center

Read about reading and understanding complex code
[Read -->]

```

```{grid-item-card} Interactive Quiz
:link: #self-assessment-phase-43
:link-type: url
:text-align: center

Test your advanced skills from Phase 4
[Take Quiz -->]

```

```{grid-item-card} 📖 PSO Algorithm Explained
:link: https://www.geeksforgeeks.org/machine-learning/particle-swarm-optimization-pso-an-overview/
:link-type: url
:class-card: resource-card resource-article
:shadow: md
:text-align: center

Comprehensive PSO overview with algorithm fundamentals, swarm intelligence, and Python implementation examples.
📊 *Estimated Time:* 40 min | 🎯 *Level:* Advanced
[Read -->]

```

```{grid-item-card} 📖 Chattering Reduction Techniques
:link: https://www.mdpi.com/2504-446X/7/7/420
:link-type: url
:class-card: resource-card resource-article
:shadow: md
:text-align: center

Open-access MDPI paper on chattering reduction using reinforcement learning for SMC. Practical engineering focus.
📊 *Estimated Time:* 50 min | 🎯 *Level:* Technical
[Read -->]

```

```{grid-item-card} 🛠️ Matplotlib Best Practices
:link: https://matplotlib.org/
:link-type: url
:class-card: resource-card resource-tool
:shadow: md
:text-align: center

Official Matplotlib documentation with examples gallery, user guide, and API docs for data visualization.
📊 *Estimated Time:* Reference | 🎯 *Level:* Reference
[Browse -->]

```

```{grid-item-card} 🧪 Streamlit UI Tutorial
:link: https://docs.streamlit.io/get-started/tutorials/create-an-app
:link-type: url
:class-card: resource-card resource-interactive
:shadow: md
:text-align: center

Official Streamlit tutorial building interactive NYC Uber app. Covers caching, widgets, and deployment.
📊 *Estimated Time:* 60 min | 🎯 *Level:* Beginner
[Try It -->]

```
```

---
**CONGRATULATIONS!** 🎉

You've completed **Phase 4: Advancing Skills** (~30 hours)!

You now understand:
✅ Advanced Python concepts (classes, inheritance, decorators)
✅ How to read and understand controller source code
✅ Mathematical foundations (Lagrangian, Lyapunov, phase space)

**Skills Gained**:
- Code reading and comprehension
- Object-oriented programming mastery
- Mathematical intuition for control theory
- Ability to modify and extend controllers

**Next**: [Phase 5: Mastery Path](phase-5-mastery.md) - transition to advanced tutorials and research

---

**Navigation:**
- <--[Phase 3: Hands-On Learning](phase-3-hands-on.md)
- **Next**: [Phase 5: Mastery Path](phase-5-mastery.md) -->
- [<--Back to Beginner Roadmap](../beginner-roadmap.md)

---

## Navigation

[<--Phase 3: Hands-On Learning](phase-3-hands-on.md) | [Back to Roadmap](../beginner-roadmap.md) | [Phase 5: Mastery Path -->](phase-5-mastery.md)
