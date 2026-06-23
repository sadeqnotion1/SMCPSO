# Step 3: Write Section 7.2 - System Architecture

**Time**: 1.5 hours
**Output**: 3 pages (Section 7.2 of Chapter 7)
**Source**: Design patterns notes from Step 1

---

## OBJECTIVE

Write a 3-page section describing the overall system architecture, module organization, design patterns, and interfaces.

---

## SOURCE MATERIALS TO READ FIRST (15 min)

### Primary Sources
1. **Read**: `thesis\notes\chapter07_design_patterns.txt` (from Step 1)
2. **Read**: `D:\Projects\main\src\controllers\factory.py`
3. **Read**: `D:\Projects\main\src\controllers\base.py` (if exists)
4. **Read**: `D:\Projects\main\src\core\simulation_context.py`

---

## EXACT PROMPT TO USE

### Copy This Into Your AI Assistant:

```
Write Section 7.2 - System Architecture (3 pages) for Chapter 7 (Implementation) of a Master's thesis on "Sliding Mode Control of Double-Inverted Pendulum with Particle Swarm Optimization."

Context:
- This is Section 7.2 of Chapter 7
- Audience: Software engineers and control researchers
- Format: LaTeX, IEEE citation style
- Tone: Technical, precise, engineering documentation style

Structure (3 pages total):

**Page 1: Module Organization**

Subsection: Package Structure
- Describe top-level organization:
  * src/controllers/: 7 controller implementations + factory
  * src/core/: Simulation engine, context, vectorized simulators
  * src/plant/: 3 dynamics models + base interfaces
  * src/optimizer/: PSO tuner implementation
  * src/utils/: Validation, control primitives, monitoring, visualization
  * src/hil/: Hardware-in-the-loop plant server and controller client

- Dependency hierarchy:
  * Core depends on: NumPy, SciPy (numerical computation)
  * Controllers depend on: Core, Plant (interfaces)
  * Optimizer depends on: Controllers, Core, Plant (full stack)
  * Utils are independent (no internal dependencies)
  * HIL depends on: Controllers, Core, Plant

- Design principle: "Layered architecture with clear separation of concerns"

Include Figure 7.1: Architecture diagram (box-and-arrow diagram showing modules and dependencies)

**Page 2: Design Patterns**

Subsection: Factory Pattern for Controller Creation
- Problem: Need to instantiate different controllers from configuration
- Solution: Factory function in controllers/factory.py
- Code snippet:
```python
def create_controller(name, config, gains):
    if name == 'classical_smc':
        return ClassicalSMC(config, gains)
    elif name == 'sta_smc':
        return STASMC(config, gains)
    # ... other controllers
    else:
        raise ValueError(f"Unknown controller: {name}")
```

Subsection: Strategy Pattern for Controller Interface
- Problem: Need uniform interface for different control algorithms
- Solution: Abstract base class BaseController
- Code snippet:
```python
class BaseController(ABC):
    @abstractmethod
    def compute_control(self, state, last_control, history):
        \"\"\"Compute control output given current state.\"\"\"
        pass

    def cleanup(self):
        \"\"\"Release resources (weakref pattern).\"\"\"
        pass
```

Subsection: Context Pattern for Simulation
- Problem: Need to encapsulate controller + dynamics + parameters
- Solution: SimulationContext class
- Benefits: Unified interface, easier batch simulation, cleaner code

**Page 3: Key Interfaces**

Subsection: Controller Interface
- Required methods: compute_control(), reset(), cleanup()
- Input: state (6D vector: [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂])
- Output: control force u
- History tracking: Optional for adaptive controllers

Subsection: Dynamics Interface
- Required methods: step(state, control, dt) → next_state
- Input: current state, control, time step
- Output: next state (after one integration step)
- Models: SimplifiedDynamics, FullDynamics, LowRankDynamics

Subsection: Configuration Interface
- Pydantic models for validation
- Hierarchical structure (root config → controller configs → PSO config)
- Type checking at runtime
- Default value handling

Summary paragraph:
"These design patterns and interfaces enable extensibility while maintaining type safety and performance. New controllers can be added by implementing the BaseController interface and registering with the factory. The layered architecture isolates numerical computation (core) from control logic (controllers) and optimization (optimizer), facilitating independent testing and validation."

Citation Requirements:
- Cite design patterns book cite:Gamma1994
- Cite Python type hints cite:PEP484
- Cite Pydantic cite:Colvin2023

Code Formatting:
- Use \texttt{} for inline code
- Use lstlisting environment for code blocks
- Include line numbers for longer snippets

Quality Checks:
- NO conversational language
- YES precise technical terminology
- Include actual code snippets (not pseudocode)
- Reference Figure 7.1 in text

Length: Exactly 3 pages when compiled in LaTeX (12pt font, 1-inch margins)
```

---

## WHAT TO DO WITH THE OUTPUT

### 1. Create Architecture Diagram (20 min)

**Method 1: Using draw.io or similar**:
- Create 6 boxes: Controllers, Core, Plant, Optimizer, Utils, HIL
- Add arrows showing dependencies
- Save as PDF: `thesis\figures\chapter07\architecture_diagram.pdf`

**Method 2: Using LaTeX TikZ**:
```latex
\begin{figure}[ht]
\centering
\begin{tikzpicture}[
  module/.style={rectangle, draw, minimum width=2cm, minimum height=1cm},
  arrow/.style={->, >=stealth, thick}
]
\node[module] (utils) at (0,0) {Utils};
\node[module] (core) at (3,0) {Core};
\node[module] (plant) at (6,0) {Plant};
\node[module] (controllers) at (3,2) {Controllers};
\node[module] (optimizer) at (6,2) {Optimizer};
\node[module] (hil) at (0,2) {HIL};

\draw[arrow] (controllers) -- (core);
\draw[arrow] (controllers) -- (plant);
\draw[arrow] (optimizer) -- (controllers);
\draw[arrow] (optimizer) -- (core);
\draw[arrow] (hil) -- (controllers);
\end{tikzpicture}
\caption{System architecture showing module dependencies. Arrows indicate compile-time dependencies.}
\label{fig:impl:architecture}
\end{figure}
```

### 2. Review and Edit (15 min)

Check for:
- [ ] **Code snippets**: Verify against actual source files
- [ ] **Design patterns**: Accurate description (Factory, Strategy, Context)
- [ ] **Module names**: Match actual directory structure
- [ ] **Figure reference**: Text mentions "Figure 7.1"

### 3. Format as LaTeX (15 min)

Append to: `D:\Projects\main\thesis\chapters\chapter07_implementation.tex`

```latex
\section{System Architecture}
\label{sec:impl:architecture}

[PASTE AI OUTPUT HERE]

% Add figure
\input{figures/chapter07/architecture_diagram.tex}
```

### 4. Test Compile (5 min)

```bash
cd thesis
pdflatex main.tex
```

Verify:
- [ ] Figure 7.1 appears
- [ ] Code snippets formatted correctly
- [ ] No compilation errors

---

## VALIDATION CHECKLIST

Before moving to Step 4:

### Content Quality
- [ ] All 6 modules described (Controllers, Core, Plant, Optimizer, Utils, HIL)
- [ ] 3 design patterns explained (Factory, Strategy, Context)
- [ ] 3 interfaces documented (Controller, Dynamics, Configuration)
- [ ] Dependency hierarchy clear

### Code Accuracy
- [ ] Code snippets match actual source files
- [ ] Function signatures correct (parameter names, types)
- [ ] Import statements valid

### Visual Elements
- [ ] Figure 7.1 created (architecture diagram)
- [ ] Figure referenced in text
- [ ] Diagram shows all 6 modules and dependencies

### Citations
- [ ] Design patterns cited (Gamma et al.)
- [ ] Python PEP 484 cited (type hints)
- [ ] Pydantic cited (validation)

### Page Count
- [ ] Output is 2.8-3.2 pages (target: 3 pages)

---

## EXPECTED OUTPUT SAMPLE

Here's what the Factory Pattern subsection might look like:

```latex
\subsection{Factory Pattern for Controller Creation}

The controller instantiation process employs the Factory design pattern \cite{Gamma1994} to decouple client code from concrete controller classes. The \texttt{create\_controller()} function in \texttt{src/controllers/factory.py} accepts a controller name string and returns the appropriate instance:

\begin{lstlisting}[language=Python, caption={Factory function for controller creation}, label={lst:impl:factory}]
def create_controller(name: str, config: dict, gains: List[float]):
    if name == 'classical_smc':
        return ClassicalSMC(config, gains)
    elif name == 'sta_smc':
        return STASMC(config, gains)
    # Additional controllers...
    else:
        raise ValueError(f"Unknown controller: {name}")
\end{lstlisting}

This pattern enables configuration-driven controller selection, allowing users to specify the desired algorithm in \texttt{config.yaml} without modifying code. New controllers can be added by implementing the \texttt{BaseController} interface (Section 7.2.3) and extending the factory function.
```

---

## COMMON ISSUES

**Issue**: Code snippets don't compile in LaTeX
- **Fix**: Add to preamble.tex:
```latex
\usepackage{listings}
\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  captionpos=b
}
```

**Issue**: Architecture diagram too complex
- **Fix**: Simplify to show only module-level dependencies
- **Omit**: Internal class relationships (save for Appendix)

**Issue**: Design patterns explanation too abstract
- **Fix**: Always include code snippet showing actual implementation
- **Link**: "This pattern solves the problem of..."

---

## TIME CHECK

- Reading sources: 15 min
- Running prompt: 5 min
- Creating diagram: 20 min
- Reviewing output: 15 min
- Formatting LaTeX: 15 min
- Test compile: 5 min
- **Total**: ~1.5 hours

---

## NEXT STEP

Once Section 7.2 is complete:
**Proceed to**: `step_04_section_7_3_simulation_engine.md`

This will write Section 7.3 - Simulation Engine (3 pages, 1.5 hours)

---

**[OK] Ready to write? Follow the prompt and create Section 7.2!**
