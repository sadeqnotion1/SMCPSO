# E015: Architectural Standards and Patterns

**Hosts**: Dr. Sarah Chen (Control Systems) & Alex Rivera (Software Engineering)

---

## Opening Hook

**Alex**: You're browsing a codebase and see a file called `simulation_context.py` in THREE different locations. Bug? Duplication? Tech debt?

**Sarah**: Nope! **Intentional architectural pattern** for import path flexibility!

**Alex**: Or you notice 8 different dynamics files (`simplified_dynamics.py`, `full_nonlinear_dynamics.py`, `lowrank_dynamics.py`...). Redundant?

**Sarah**: Nope! **Deliberate model variants** offering accuracy/speed tradeoffs!

**Alex**: This is why architectural standards matter. Without documentation, these patterns look like MISTAKES. With standards, they're FEATURES.

**Sarah**: This episode covers:
- **Architectural invariants**: Patterns you must NEVER "fix"
- **Design patterns**: Factory, strategy, dependency injection
- **Code conventions**: File naming, directory structure, style guides
- **Quality gates**: What gets enforced, what gets flagged

**Alex**: Let's explore the architecture that makes 100,000+ lines of code maintainable!

---

## Introduction: Why Architectural Standards?

**Sarah**: A codebase without standards is like a city without **zoning laws**. Imagine if someone could build a factory next to your house, or open a nightclub in a hospital. Chaos, right?

**Alex**: Same with code. Without standards, you get files like `controller.py`, `Controller_v2.py`, `CONTROLLER_NEW.py`, `my_controller_final_FINAL.py`, and `temp_controller_backup_old_2.py` all living in the same directory. Which one is production code? Which is safe to delete? Nobody knows!

**Sarah**: With standards—with **zoning laws for code**—you get clean organization:
- Controllers live in the Controllers District: `src/controllers/`
- Each has a clear name: `classical_smc.py`, `sta_smc.py`, `adaptive_smc.py`
- No version suffixes, no "final" labels, no confusion

**Alex**: Standards answer four critical questions:
- **WHERE** to put code (directory structure—our zoning laws)
- **HOW** to name things (files, classes, functions)
- **WHAT** patterns to use (factories, not if-else chains)
- **WHEN** to deviate (documented exceptions only)

## Documentation Scale \& Organization

**Documentation Statistics:**

        `docs/NAVIGATION.md` connects all 11 navigation systems \\
        Persona-based entry points, "I Want To..." quick navigation

---

## Documentation Categories

**Organized by Purpose \& Audience:**

    \begin{tabular}{lll}
        \toprule
        **Category** & **Files** & **Audience** \\
        \midrule
        Getting Started & 12 & Beginners \\
        Tutorials & 18 & All levels \\
        Theory \& Algorithms & 45 & Advanced \\
        API Reference & 120 & Developers \\
        Research Workflows & 28 & Researchers \\
        Development Guides & 32 & Contributors \\
        System Architecture & 15 & Advanced developers \\
        AI Workspace & 171 & Claude Code \\
        \bottomrule
    \end{tabular}

        API reference auto-generated from docstrings using Sphinx autodoc \\
        Ensures documentation stays synchronized with code

---

## Navigation Philosophy

**Three Entry Points for Different User Needs:**

        - **Persona-Based Navigation**

            - \textit{"I'm a student learning control theory"}
            - \textit{"I'm a researcher validating algorithms"}
            - \textit{"I'm a developer contributing code"}
            - \textit{"I'm an instructor teaching SMC"}

        - **Intent-Based Navigation ("I Want To...")**

            - \textit{"I want to run my first simulation"}
            - \textit{"I want to tune controller gains"}
            - \textit{"I want to understand the theory"}
            - \textit{"I want to add a new controller"}

        - **Category-Based Navigation**

            - Browse by topic (Theory, Tutorials, API)
            - 43 category index files
            - Visual sitemaps for overview

---

## Design Patterns: Factory Pattern

**Sarah**: Let's start with the Factory pattern - the backbone of our controller creation system.

**Alex**: Think of it like a **vending machine**. You press the button for "Classical SMC" and out comes a Classical SMC controller object. Press "STA-SMC" and you get that instead. The vending machine handles all the complexity of storage, retrieval, and dispensing. You just make a simple request.

**Sarah**: Exactly! **Why Factory?** Because we have 7 controller types and this pattern eliminates massive if-else chains:

**Without Factory (Bad)**:
```python
def create_controller(ctrl_type, config):
    if ctrl_type == "classical_smc":
        return ClassicalSMC(gains=config.gains, ...)
    elif ctrl_type == "sta_smc":
        return STASMC(gains=config.gains, ...)
    elif ctrl_type == "adaptive_smc":
        return AdaptiveSMC(gains=config.gains, ...)
    # ... 4 more elif blocks
    else:
        raise ValueError(f"Unknown controller: {ctrl_type}")
```

**With Factory (Good)**:
```python
# src/controllers/factory.py
CONTROLLER_REGISTRY = {
    "classical_smc": ClassicalSMC,
    "sta_smc": STASMC,
    "adaptive_smc": AdaptiveSMC,
    "hybrid_adaptive_sta_smc": HybridAdaptiveSTASMC,
    "integral_smc": IntegralSMC,
    "terminal_smc": TerminalSMC,
    "swing_up_smc": SwingUpSMC,
}

def create_controller(ctrl_type: str, config: ControllerConfig):
    """Factory method for controller instantiation."""
    controller_class = CONTROLLER_REGISTRY.get(ctrl_type)
    if controller_class is None:
        available = ", ".join(CONTROLLER_REGISTRY.keys())
        raise ValueError(f"Unknown controller '{ctrl_type}'. Available: {available}")
    return controller_class(gains=config.gains, physics=config.physics)
```

**Sarah**: **Benefits**:
- **Extensibility**: Add new controller → register in dict → done
- **Discoverability**: `CONTROLLER_REGISTRY.keys()` lists all options
- **Type safety**: Single creation point enforces consistent interfaces

**Alex**: Real-world impact: Adding MPC controller took **5 minutes** (not 30 minutes of chasing if-else blocks).

---

## Design Patterns: Strategy Pattern

**Alex**: Strategy pattern lets us swap algorithms at runtime without changing client code.

**Sarah**: **Use case**: Dynamics models with different accuracy/performance tradeoffs.

**Strategy Interface**:
```python
# src/plant/core/dynamics_interface.py
class DynamicsInterface(ABC):
    @abstractmethod
    def compute_derivatives(self, state: np.ndarray, u: float) -> np.ndarray:
        """Compute state derivatives: dx/dt = f(x, u)"""
        pass

    @abstractmethod
    def get_state_dimension(self) -> int:
        """Return state dimension (4 for simplified, 6 for full)"""
        pass
```

**Concrete Strategies**:
```python
# src/plant/models/simplified_dynamics.py
class SimplifiedDynamics(DynamicsInterface):
    """Fast dynamics (no friction, small-angle approximation)"""
    def compute_derivatives(self, state, u):
        # Simplified equations, 2× faster
        return derivatives

# src/plant/models/full_nonlinear_dynamics.py
class FullNonlinearDynamics(DynamicsInterface):
    """Accurate dynamics (friction, exact trig, Coriolis terms)"""
    def compute_derivatives(self, state, u):
        # Full nonlinear equations, more accurate
        return derivatives

# src/plant/models/lowrank_dynamics.py
class LowRankDynamics(DynamicsInterface):
    """Reduced-order dynamics for fast batch optimization"""
    def compute_derivatives(self, state, u):
        # Dimensionality reduction for PSO
        return derivatives
```

**Client Code (Strategy-Agnostic)**:
```python
# src/core/simulation_runner.py
def run_simulation(controller, dynamics: DynamicsInterface, t_span, x0):
    """Works with ANY dynamics strategy"""
    def state_derivative(t, x):
        u = controller.compute_control(x, ...)
        return dynamics.compute_derivatives(x, u)

    solution = solve_ivp(state_derivative, t_span, x0, method='RK45')
    return solution
```

**Alex**: **Why this matters**: Switching from `SimplifiedDynamics` to `FullNonlinearDynamics` requires **zero changes** to simulation code.

**Sarah**: PSO uses `LowRankDynamics` for 50 generations × 30 particles = 1500 simulations. **3× speedup** vs full dynamics!

---

## Design Patterns: Dependency Injection

**Sarah**: Dependency Injection (DI) makes code testable and flexible.

**Alex**: **Bad approach (hard-coded dependencies)**:
```python
class Controller:
    def __init__(self, gains):
        self.monitor = LatencyMonitor(dt=0.01)  # Hard-coded!
        self.dynamics = FullNonlinearDynamics()  # Hard-coded!
```

**Problems**:
- Can't test without real `LatencyMonitor` (slow, non-deterministic)
- Can't swap dynamics models
- Can't disable monitoring in production

**Good approach (DI)**:
```python
class Controller:
    def __init__(self, gains, monitor: Optional[LatencyMonitor] = None,
                 dynamics: Optional[DynamicsInterface] = None):
        self.gains = gains
        self.monitor = monitor  # Injected dependency
        self.dynamics = dynamics  # Injected dependency

    def compute_control(self, state, ...):
        if self.monitor:
            start = self.monitor.start()

        u = self._compute_control_law(state)

        if self.monitor:
            self.monitor.end(start)

        return u
```

**Sarah**: Now we can inject **mock objects** for testing:
```python
# tests/test_controllers/test_classical_smc.py
def test_controller_without_monitoring():
    controller = ClassicalSMC(gains=[...], monitor=None)  # No monitoring overhead
    u = controller.compute_control(state, ...)
    assert -100 <= u <= 100

def test_controller_with_mock_dynamics():
    mock_dynamics = MockDynamics(return_value=np.zeros(4))
    controller = ClassicalSMC(gains=[...], dynamics=mock_dynamics)
    # Test controller in isolation
```

**Alex**: Production uses real dependencies, tests use mocks. **Best of both worlds!**

---

## Critical Architectural Patterns

**Alex**: Now the patterns that look like **bugs** but are actually **features**.

**Sarah**: These are **architectural invariants** - NEVER "fix" them!

### Pattern 1: Compatibility Layers

**File duplication you'll see**:
```
src/optimizer/           # Legacy path (backward compatibility)
src/optimization/        # New canonical path
```

**Why both exist**:
- External tools use `from src.optimizer import PSOTuner`
- New code uses `from src.optimization import PSOTuner`
- Both work via re-export: `src/optimizer/__init__.py` imports from `src/optimization/`

**Alex**: **NEVER delete** `src/optimizer/` - it's a compatibility shim, not duplication!

### Pattern 2: Re-export Chains

**File appears in 3 locations**:
```
src/core/simulation_context.py               # Canonical implementation
src/simulation_context.py                     # Root-level re-export
tests/simulation_context.py                   # Test-level re-export
```

**Why 3 copies**:
```python
# Import flexibility for different contexts
from src.core.simulation_context import SimulationContext  # Explicit
from src.simulation_context import SimulationContext       # Convenient
from simulation_context import SimulationContext           # Test-local
```

**Sarah**: This is **intentional import path flexibility**, not tech debt!

### Pattern 3: Model Variants

**Sarah**: You'll find **eight different dynamics files** in the models directory. Duplication?

**Alex**: Nope! Each serves a different purpose. Think of them as **different tools for different jobs**:

**Sarah**: We have the **Simplified Dynamics**—fast and easy to understand, perfect for tutorials. Uses small-angle approximations, runs twice as fast as the full model.

**Alex**: Then the **Full Nonlinear Dynamics**—accurate with exact trigonometry, friction, Coriolis terms. This is production-grade validation.

**Sarah**: The **Low-Rank Dynamics** is optimized for PSO. Reduced-order model that runs three times faster. When you're running 1,500 simulations for optimization, that speed matters!

**Alex**: Plus we have specialized research variants: **Friction-Only**, **Coriolis-Only**, **Linearized**, **Stochastic** with noise injection, and **Hybrid** with mode-switching. Each tests a specific hypothesis.

**Sarah**: The key insight? These are **deliberate accuracy-speed tradeoffs**, not redundant code. NEVER consolidate them into one file—you'd lose the ability to choose the right tool for the job!

### Pattern 4: Framework Files in Unexpected Places

**Alex**: You'll see this file and think "Should this be in tests/?"
```
src/interfaces/hil/test_automation.py
```

**Sarah**: NOPE! This is a **testing framework** (production code), not a **test file** (pytest code).

**Distinction**:
- **Test files** (`tests/test_*.py`): Use pytest, imported by pytest runner
- **Testing frameworks** (`src/**/test_*.py`): Provide infrastructure, imported by production code

**Example**:
```python
# src/interfaces/hil/test_automation.py (Framework - belongs in src/)
class HILTestFramework:
    """Framework for automating HIL experiments"""
    def run_test_sequence(self, scenarios): ...
    def validate_results(self, results): ...

# tests/test_hil/test_plant_server.py (Test - belongs in tests/)
def test_plant_server_timeout():
    """Pytest test using the framework"""
    framework = HILTestFramework()
    result = framework.run_test_sequence([...])
    assert result.success
```

---

## Directory Structure Rules

**Sarah**: Where to put code? Think of it like **city zoning districts**. Each directory is a zone with specific rules:

### Rule 1: src/ = Production Code (The Business District)

**Alex**: The `src` directory is your **Business District**—this is where the real work happens. Production code that ships to users lives here.

**Sarah**: How do you know if code belongs in `src`? Ask yourself: Does it meet **any** of these criteria?
- Is it exported in an `__init__.py` file?
- Does production code import and use it?
- Is it framework or infrastructure code?
- Does it provide reusable functionality?

**Alex**: If you answer **yes** to even one question, it goes in `src`.

**Sarah**: Examples: `classical_smc.py` in the controllers directory? Yes—exported and imported by `simulate.py`. The validation utilities? Yes—provide reusable state validation for all controllers. Even `test_automation.py` in the HIL interfaces? Yes—it's a framework, not a test file!

### Rule 2: scripts/ = Development Tools (The Workshop District)

**Alex**: The `scripts` directory is your **Workshop District**—tools and utilities for developers, not end users.

**Sarah**: Code goes in `scripts` only if **all three** of these are true:
- It's executed directly, never imported
- It's a development or automation tool
- It's not part of production runtime

**Alex**: Think of it as the backstage area. Users never see it. Developers use it constantly.

**Sarah**: Examples: `run_mt5.py` runs benchmarks—you execute it directly, it's an automation tool, production code never calls it. The doc quality checker `detect_ai_patterns.py`? Same deal. The coverage runner? Definitely a workshop tool!

### Rule 3: tests/ = Pytest Tests (The Quality Assurance District)

**Alex**: The `tests` directory is your **QA District**—where code goes to prove it works.

**Sarah**: Code belongs in `tests` only if **all three** are true:
- Filename matches `test_*.py` or `*_test.py`
- It uses pytest imports
- It contains test functions starting with `test_`

**Alex**: Simple rule: If pytest runs it, it lives in `tests`. If production code imports it, it lives in `src`. **Never mix the two!**

---

## Code Style Conventions

**Alex**: Naming rules that prevent the chaos we saw earlier—remember `my_controller_final_FINAL.py`?

### File Naming

**Sarah**: For Python modules, use **snake_case** and be descriptive: `classical_smc.py`, `pso_optimizer.py`, `latency_monitor.py`. Clear, consistent, readable.

**Alex**: What **not** to do? No PascalCase for files—that's for classes inside the files. No hyphens—they break Python imports. No version suffixes like `_v2` or `_FINAL`—that's what Git is for!

**Sarah**: For configuration files, lowercase is standard: `config.yaml`, `pytest.ini`. Tool-specific configs can use hyphens: `.pre-commit-config.yaml`. But never capitalize the first letter, and never add backup suffixes. Use version control, not filename hacks!

### Class Naming

**Alex**: Classes use **PascalCase**—capitalize every word: `ClassicalSMC`, `LatencyMonitor`, `PSOTuner`.

**Sarah**: Keep acronyms fully uppercase: `SMC` not `Smc`, `PSO` not `Pso`. No underscores—`Classical_SMC` is wrong. No snake_case—classes aren't variables!

### Function Naming

**Alex**: Functions use **snake_case** with a verb-noun structure: `compute_control`, `validate_state_bounds`, `run_pso_optimization`. The verb tells you what it **does**, the noun tells you what it **operates on**.

**Sarah**: Never use PascalCase or camelCase for functions. And always include the verb—`control(state)` is vague. Does it compute control? Validate control? Apply control? Be explicit: `compute_control(state)`.

### Variable Naming

**Sarah**: Variables also use **snake_case** and should be descriptive: `state_dimension`, `max_iterations`. Avoid abbreviations like `state_dim` unless it's universally understood.

**Alex**: Exception: mathematical variables can be short. `dt` for timestep? Fine—everyone knows that. `t` for time? Sure. But `sd` for state dimension? Too cryptic. Spell it out!

---

## Quality Gates (Enforce Strictly)

**Sarah**: These are the HARD LIMITS enforced by CI:

### Gate 1: Test Pass Rate
```
MANDATORY: 100% tests passing
Current: 668/668 passing [OK]
Action if failing: ALL work stops until fixed
```

### Gate 2: Critical Issues
```
MANDATORY: 0 critical issues
Examples: Security vulnerabilities, data corruption, safety violations
Action if found: Immediate rollback + root cause analysis
```

### Gate 3: Coverage Thresholds
```
REQUIRED:
- Overall: ≥85%
- Critical components (controllers, dynamics): ≥95%
- Safety-critical (saturation, bounds checking): 100%

Current: 87% overall [OK]
Action if failing: No merge to main
```

### Gate 4: Root Directory Cleanliness
```
REQUIRED: ≤19 visible items in project root
Current: 14 items [OK]
Threshold: 19 items (red flag at 20+)
Action if exceeded: Cleanup sprint required
```

### Gate 5: Documentation Build
```
MANDATORY: Sphinx docs build without warnings
Command: sphinx-build -M html docs docs/_build -W --keep-going
Action if failing: Fix warnings before merge
```

### Gate 6: Code Style
```
REQUIRED: Black + isort + flake8 pass
Command: pre-commit run --all-files
Action if failing: Auto-fix or manual correction
```

### Gate 7: Type Checking
```
REQUIRED: mypy passes on critical modules
Threshold: 0 errors in src/controllers/, src/core/, src/plant/
Action if failing: Add type hints or use # type: ignore with justification
```

### Gate 8: Filename Validation
```
MANDATORY: No malformed filenames
Forbidden:
- Windows device names (nul, con, prn, aux, com1-9, lpt1-9)
- Braces/spaces ({dir}/, my folder/)
- Unicode on Windows (emoji in filenames)
Action if found: Rename via git mv immediately
```

**Alex**: **Why so strict?** Because catching issues at commit time is 100× cheaper than catching them in production!

---

## Quality Audit Results (CA-02)

**Sarah**: Here's proof the standards work - results from our comprehensive audit:

### Coverage Analysis
```
Component                    Coverage    Status
--------------------------------------------
Controllers (critical)       98.7%       [OK]
Dynamics models (critical)   96.2%       [OK]
Simulation core (critical)   95.8%       [OK]
Optimization (important)     91.4%       [OK]
Utils (important)            88.3%       [OK]
HIL (important)              87.9%       [OK]
--------------------------------------------
Overall                      87.1%       [OK] (≥85% required)
```

### Test Pyramid
```
Unit tests:        542 (81%)     [OK] (target: 70-80%)
Integration tests:  98 (15%)     [OK] (target: 15-20%)
System tests:       28 (4%)      [OK] (target: 5-10%)
--------------------------------------------
Total:             668 (100%)    [OK]
```

### Architectural Compliance
```
Gate                          Status
----------------------------------------
Dependency injection usage    100%  [OK]
Factory pattern compliance    100%  [OK]
Strategy pattern usage         95%  [OK]
Proper directory placement     98%  [OK]
Naming convention adherence    97%  [OK]
```

**Alex**: **5% strategy gap** comes from experimental MPC controller (still hardcodes some dynamics). Tracked in technical debt register.

---

## Architectural Decision Records (ADRs)

**Sarah**: Major design decisions are documented as ADRs:

**Example: ADR-003 - Factory Pattern for Controllers**
```markdown
# ADR-003: Factory Pattern for Controller Instantiation

**Status**: Accepted (Oct 2025)

**Context**: Adding new controllers required modifying 5+ files (simulate.py,
streamlit_app.py, tests, benchmarks, docs). High coupling, error-prone.

**Decision**: Implement factory pattern with registry dictionary.

**Consequences**:
- Positive: Adding controller = single dict entry, extensible, testable
- Negative: Indirection (registry lookup), less obvious from IDE
- Mitigation: Registry is well-documented, IDE autocomplete works via type hints

**Alternatives Considered**:
- If-else chain: Rejected (not extensible)
- Plugin system: Rejected (too complex for 7 controllers)
- Abstract factory: Rejected (overkill, no controller families)
```

**Alex**: ADRs answer "Why did we do it this way?" when reviewing code 6 months later.

---

## Common Anti-Patterns (Avoid These)

**Alex**: Patterns that seem reasonable but violate our standards. Let me tell you a cautionary tale:

### Anti-Pattern 1: God Objects—The Monster That Ate the Codebase

**Sarah**: What's a God Object?

**Alex**: A class that does **everything**. It starts innocently: "I'll just add one more method..." Six months later, you have a 500-line monster that computes control, logs telemetry, plots results, saves to databases, and sends email reports. Changing **anything** risks breaking **everything**.

**Sarah**: We encountered this early in development. The original controller class had 12 responsibilities. Testing was impossible—to test the control logic, you needed a database connection, a plotting library, and an SMTP server. Ridiculous!

```python
# BAD: The God Object Monster
class Controller:
    def compute_control(self, state): ...
    def log_telemetry(self, state): ...
    def plot_results(self, results): ...
    def save_to_database(self, results): ...
    def send_email_report(self, results): ...
    def validate_inputs(self, state): ...
    def check_safety_limits(self, u): ...
    # 500 lines of tangled logic later...
```

**Alex**: The fix? **Single Responsibility Principle**. Each class does **one thing** and does it well:

```python
# GOOD: Clean separation of concerns
class Controller:
    def compute_control(self, state): ...  # Only control logic

class TelemetryLogger:
    def log(self, state): ...  # Only logging

class ResultsVisualizer:
    def plot(self, results): ...  # Only plotting
```

**Sarah**: After refactoring, testing became trivial. Mock the logger, test the controller in isolation. **God Objects are the enemy of maintainability.**

### Anti-Pattern 2: Magic Numbers
```python
# BAD: Unexplained constants
def compute_control(error):
    return 10.5 * error + 3.2 * integral + 0.8 * derivative
```

**Fix: Named Constants**
```python
# GOOD: Self-documenting
KP = 10.5  # Proportional gain (tuned via PSO)
KI = 3.2   # Integral gain
KD = 0.8   # Derivative gain

def compute_control(error):
    return KP * error + KI * integral + KD * derivative
```

### Anti-Pattern 3: Mutable Default Arguments
```python
# BAD: Mutable default (shared across calls!)
def add_state(state, history=[]):
    history.append(state)
    return history
```

**Fix: None Default + Initialize Inside**
```python
# GOOD: Fresh list each call
def add_state(state, history=None):
    if history is None:
        history = []
    history.append(state)
    return history
```

---

## Summary: Architectural Lessons

**Sarah**: So what makes this architecture successful? After 100,000 lines of code, what did we learn?

**Alex**: **Three core principles that saved our sanity**:

**1. Intentional Patterns Over Clever Code**

Think **vending machines** (Factory pattern), not if-else chains. Think **interchangeable tools** (Strategy pattern), not inheritance hell. Think **dependency injection**, not hard-coded nightmares. Simple, proven patterns beat clever hacks.

**2. Standards Prevent Chaos—Zoning Laws for Code**

Eight quality gates enforced at commit time. Directory zoning: Business District (`src/`), Workshop (`scripts/`), QA (`tests/`). Naming conventions: no `final_v2_REALLY_FINAL.py`, no God Objects, no magic numbers. Standards are your safety net.

**3. Document the Why, Not Just the What**

ADRs explain **why** we chose Factory over plugin systems. CLAUDE.md captures **why** eight dynamics files exist. Comments explain **why** the pattern looks weird. Future you will thank present you.

**Sarah**: **The proof it works**—key metrics:
- 87.1% test coverage—meets the 85% gate
- 668 tests, 100% passing—zero failures tolerated
- 14 visible root items—well under the 19-item chaos threshold
- 0 critical issues—quality gates holding strong
- 50× productivity gain—automation turns 2 days into 8 minutes

**Alex**: The architecture isn't perfect. But it's **maintainable**—you can understand it in 30 minutes. It's **extensible**—adding a controller takes 5 minutes, not 5 hours. And it's **documented**—the "why" survives team turnover.

**Sarah**: And that's what matters when you're managing 100,000+ lines of code across token limits and month-long gaps!

**Alex**: Remember: **Standards beat cleverness. Every. Single. Time.** The Factory pattern is boring. The directory rules are strict. The naming conventions feel pedantic. But six months from now, when you return to this code? You'll thank yourself for being boring, strict, and pedantic.

---

## Resources

- **Repository:** https://github.com/theSadeQ/dip-smc-pso.git
- **Documentation:** `docs/` directory
- **Getting Started:** `docs/guides/getting-started.md`

---

*Educational podcast episode generated from comprehensive presentation materials*
