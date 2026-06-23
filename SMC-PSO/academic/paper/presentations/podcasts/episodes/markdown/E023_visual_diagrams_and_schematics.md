# E023: Visual Diagrams and Schematics

**Part:** Part 4 Professional Practice
**Duration:** 15-20 minutes
**Source:** DIP-SMC-PSO Architecture Documentation

---

## Opening Hook: Sell, Don't Tell

**Sarah:** Today's episode is different. We're not going to describe diagrams—we're going to tell you **why** you need to see them and **where** to find them.

**Alex:** Because here's the truth: describing a flowchart node-by-node over audio is like describing a painting to someone on the phone. "There's a blue box. An arrow goes from the blue box to the green box. The green box has text inside that says..."

**Sarah:** You lose the **gestalt**—the at-a-glance understanding. A diagram shows you everything at once. Audio description is sequential—one piece at a time.

**Alex:** So instead of walking you through every arrow, we're going to tell you **what the diagrams are for**, **why they matter**, and **how to use them**. Then you can go look at them yourself.

**Sarah:** Think of this episode as the **trailer** for the visual documentation. We're selling you on why it's worth your time to open `docs/diagrams/` and explore.

---

## Why Diagrams Matter: Water Through Pipes

**Sarah:** Before we tell you where to find the diagrams, let's talk about **why** they're valuable. What do diagrams show that code can't?

**Alex:** **Flow**. Think of data moving through your system like **water through pipes**. Configuration flows in from `config.yaml`. It gets validated, parsed, split into controller settings and dynamics parameters. Controller settings flow to the factory. The factory instantiates a controller object. State flows from the dynamics model to the controller. Control signals flow back to the dynamics. History flows to the monitoring system.

**Sarah:** **Picture water flowing**. It's not static boxes. It's **movement**—data traveling, transforming, branching, merging.

**Alex:** That's what the control flow diagram shows. You see the **path** data takes from input to output. Where does user configuration enter? Where does it split? Where do control signals get computed? Where do results get logged?

**Sarah:** And you can't get that from reading code alone. Code shows you **what** happens in each function. Diagrams show you **how** the functions connect—the plumbing of the entire system.

---

## Directory Structure: The Top-Level View

**Sarah:** Let us start with the project root. What do you see when you list the directory?

**Alex:** 18 visible items at the root level. Nine core files: `simulate.py`, `streamlit_app.py`, `config.yaml`, `requirements.txt`, `README.md`, `CHANGELOG.md`, `CLAUDE.md`, and two MCP config files -- `package.json` and `package-lock.json`.

**Sarah:** And directories?

**Alex:** Eight core directories. `src/` contains all production code. `tests/` mirrors the source structure with test files. `docs/` holds Sphinx documentation. `benchmarks/` stores performance results. `scripts/` contains automation tools. `envs/` has virtual environment configurations. `optimization_results/` stores PSO tuning outputs. `data/` holds simulation datasets.

**Sarah:** So if I wanted to run a simulation, I would use `simulate.py` at the root. If I wanted the web UI, I would use `streamlit_app.py`. And everything else is hidden behind those eight directories.

**Alex:** Exactly. The root is clean. The complexity is organized behind those directories.

---

## The src/ Directory: Production Code Architecture

**Sarah:** Take me inside `src/`. What is the structure there?

**Alex:** 15 subdirectories. Think of it as four layers. Layer 1 is the core: `core/`, `plant/`, `simulation/`. These are the physics engine, dynamics models, and simulation runner. Everything else depends on these.

**Sarah:** What is in `core/`?

**Alex:** Simulation context, state management, base interfaces. The SimulationContext class lives there -- it is the container that holds time, state, parameters, history. Every simulation starts by creating a context.

**Sarah:** And `plant/`?

**Alex:** Dynamics models. Simplified dynamics for fast prototyping. Full nonlinear dynamics for research. Low-rank approximations for real-time applications. Each model implements the same DynamicsInterface, so the simulation runner does not care which one you use.

**Sarah:** So you could swap the physics model without changing anything else.

**Alex:** Correct. That is the value of the interface abstraction.

---

## Layer 2: Controllers and Optimization

**Sarah:** What is Layer 2?

**Alex:** `controllers/` and `optimization/`. These sit on top of the core. Controllers consume state from the simulation context and produce control signals. Optimization tunes controller parameters to minimize cost functions.

**Sarah:** How many controllers?

**Alex:** Seven implementations. Classical SMC, super-twisting, adaptive, hybrid adaptive STA-SMC, swing-up, terminal SMC, integral SMC. Plus an experimental MPC controller. All accessed through a factory pattern -- you request "classical_smc" and the factory instantiates the correct class with validated configuration.

**Sarah:** And the `optimization/` directory?

**Alex:** 48 files, 1.4 megabytes of code. PSO is the primary algorithm. Grid search, random search, Bayesian optimization are staged for future use. The PSO tuner runs swarms of particles across the parameter space, evaluating each candidate by running a full simulation and computing a cost function.

---

## Compatibility Layers: Why Two Optimizer Directories?

**Sarah:** I see `optimizer/` and `optimization/` in the directory listing. Why two?

**Alex:** Backward compatibility. Early code used `from src.optimizer import PSOTuner`. We refactored to a modular architecture under `src.optimization/` but did not want to break existing scripts. So `src/optimizer/` re-exports from `src.optimization/`. It is a shim.

**Sarah:** So if legacy code imports from `optimizer`, it still works.

**Alex:** Correct. This is an intentional architectural pattern. Not a mistake to be fixed. It is similar to Django's migration from `django.conf.urls.defaults` to `django.urls` -- they kept both paths working during the transition period.

**Sarah:** How do you document that this is intentional and not duplication?

**Alex:** We have an architectural standards document that explicitly lists compatibility layers as intentional patterns. There is a comment in `src/optimizer/pso_optimizer.py` that says: "Backward compatibility shim. See src/optimization/ for production code."

---

## Layer 3: Interfaces and Integration

**Sarah:** What is Layer 3?

**Alex:** `interfaces/` and `integration/`. These handle external interactions. The `interfaces/` directory contains the Hardware-In-the-Loop system -- plant server, controller client, test automation framework. The `integration/` directory has Streamlit UI integration, CLI wrappers, and data export utilities.

**Sarah:** So the HIL system lives in `interfaces/`?

**Alex:** Yes. There is a file called `test_automation.py` that is 581 lines and 23 kilobytes. Despite the name, it is not a test file. It is production code -- a framework for writing HIL tests. It exports eight classes: HILTestFramework, TestSuite, TestCase, TestResult, TestMetrics, TestLogger, TestValidator, TestReporter.

**Sarah:** That is confusing naming.

**Alex:** It is. But renaming it would break external tools that import from `src.interfaces.hil.test_automation`. So we document it clearly: this is a framework, not tests. The actual tests live in `tests/test_integration/test_hil/`.

---

## Layer 4: Utilities and Cross-Cutting Concerns

**Sarah:** And Layer 4?

**Alex:** `utils/`. Everything that does not fit in Layers 1-3. Validation, logging, monitoring, visualization, analysis, control primitives like saturation and deadband, reproducibility tools, type definitions.

**Sarah:** Give me examples.

**Alex:** `utils/control/` has saturation.py -- clips control signals to safe limits. `utils/monitoring/` has latency.py -- detects deadline misses in real-time control loops. `utils/validation/` has bounds.py -- ensures parameters are physically plausible. `utils/visualization/` has animation.py -- generates real-time pendulum animations.

**Sarah:** So if I wanted to add logging to my controller, I would import from `utils.logging`.

**Alex:** Correct. And the logging system uses centralized paths defined in `src/utils/logging/paths.py`. Every log file goes to `academic/logs/` with standardized naming: `{purpose}_{YYYYMMDD}_HHMMSS.log`. No logs scattered across the project root.

---

## Control Flow: Simulation Execution Path

**Sarah:** Walk me through a simulation. What happens when you run `python simulate.py --ctrl classical_smc --plot`?

**Alex:** Step 1: Load configuration from `config.yaml`. Pydantic validates every field -- physics parameters, controller gains, simulation settings. If anything is invalid, it fails immediately with a clear error message.

**Sarah:** What gets validated?

**Alex:** Physical plausibility. Mass must be positive. Damping coefficients must be non-negative. Initial angles must be in radians. Simulation timestep must be less than the Nyquist limit for the fastest dynamics. Controller gains must satisfy stability criteria if known.

**Sarah:** Step 2?

**Alex:** Create the dynamics model. Factory pattern: `create_dynamics_model('simplified')` instantiates SimplifiedDIPDynamics. The model loads parameters from the validated config and computes the linearization matrices if needed.

**Sarah:** Step 3?

**Alex:** Create the controller. Another factory: `create_controller('classical_smc', config, gains)` instantiates ClassicalSMCController. The controller initializes sliding surfaces, gain matrices, and internal state.

**Sarah:** Step 4?

**Alex:** Initialize the simulation context. This is the container that holds time, state, control history, and simulation parameters. The context starts at time zero with the initial state from the config.

**Sarah:** Step 5?

**Alex:** Run the simulation loop. For each timestep: compute control signal from current state, apply saturation limits, pass control to dynamics model, compute derivatives, integrate state forward using Runge-Kutta, update context, store history, check termination conditions. Repeat until simulation time ends or the pendulum falls.

**Sarah:** And then?

**Alex:** If `--plot` was specified, generate visualizations. State trajectories, control effort, phase portraits, sliding surface evolution. If `--save` was specified, write results to JSON. If `--run-pso` was specified, repeat the entire process thousands of times with different controller gains, searching for optimal parameters.

---

## Module Dependencies: Who Imports Who?

**Sarah:** Describe the dependency graph. What depends on what?

**Alex:** Bottom layer: `core/`, `plant/`, `utils/types/`. These have no internal dependencies. They are pure -- you can import them without pulling in the rest of the project.

**Sarah:** Next layer?

**Alex:** `controllers/` depends on `core/` and `utils/control/`. Controllers need the simulation context from `core/` and saturation functions from `utils/control/`.

**Sarah:** And optimization?

**Alex:** `optimization/` depends on `controllers/`, `plant/`, `simulation/`, and `utils/validation/`. The PSO tuner needs to instantiate controllers, run simulations, and validate parameter bounds. It is high in the dependency tree.

**Sarah:** What about circular dependencies?

**Alex:** Avoided by design. We use dependency injection. The simulation runner accepts a controller and a dynamics model as arguments. It does not import them directly. The factory pattern is at the top level -- `simulate.py` instantiates everything and wires it together.

**Sarah:** So the core never imports from controllers or optimization.

**Alex:** Correct. Dependencies flow downward only. Core -> Controllers -> Optimization. Never the reverse.

---

## Testing Architecture: Mirroring Source Structure

**Sarah:** How does the `tests/` directory relate to `src/`?

**Alex:** It mirrors the structure exactly. `src/controllers/classical_smc.py` has a corresponding `tests/test_controllers/test_classical_smc.py`. Same subdirectory hierarchy. Same naming convention with "test_" prefix.

**Sarah:** Why mirror instead of grouping tests by type?

**Alex:** Discoverability. If you are editing `src/optimizer/pso_optimizer.py`, you know exactly where the tests are: `tests/test_optimizer/test_pso_optimizer.py`. You do not have to search through a flat `tests/` directory with 200 files.

**Sarah:** What about integration tests?

**Alex:** `tests/test_integration/`. These test interactions between modules. HIL tests, end-to-end simulation tests, multi-controller benchmarks. They live in a separate subdirectory because they do not map to a single source file.

**Sarah:** And benchmarks?

**Alex:** `tests/test_benchmarks/`. Performance tests using pytest-benchmark. Microbenchmarks for critical algorithms like Numba-accelerated dynamics. Macrobenchmarks for full simulation runs. Regression tests that ensure performance does not degrade.

---

## Configuration Flow: YAML to Runtime

**Sarah:** Explain how configuration works. You mentioned `config.yaml` earlier.

**Alex:** The config file is the single source of truth. It has six main sections: physics_params, controller_config, pso_config, simulation_settings, hil_config, and monitoring_config.

**Sarah:** What is in physics_params?

**Alex:** Masses, lengths, damping coefficients, gravitational acceleration, moment of inertia. Everything that defines the physical system. When you load the config, Pydantic parses the YAML and validates each field against the schema.

**Sarah:** What happens if validation fails?

**Alex:** You get a detailed error message. "Field 'mass_cart' expected float > 0, received -1.5. Physical masses cannot be negative." The simulation does not start. You fix the config and try again.

**Sarah:** And after validation?

**Alex:** The config object is passed to the dynamics model constructor. The model extracts the parameters it needs and computes derived quantities -- linearization matrices, natural frequencies, damping ratios. The controller constructor receives controller_config and extracts gains, boundary layer thickness, adaptation rates.

**Sarah:** So the config file is read once at startup, validated, and then passed to every component that needs parameters.

**Alex:** Correct. No global state. No hardcoded parameters. Everything is explicit and validated.

---

## Documentation Structure: Sphinx and Guides

**Sarah:** The `docs/` directory. What is in there?

**Alex:** Sphinx documentation system. The source files are markdown and reStructuredText. Sphinx builds them into HTML with automatic API reference generation, cross-references, search, and navigation.

**Sarah:** What categories?

**Alex:** Four main sections. Guides: getting started, tutorials, how-to guides, troubleshooting. Theory: control theory background, SMC fundamentals, PSO optimization, Lyapunov stability. API Reference: auto-generated from docstrings, every public class and function documented. Research: paper drafts, benchmark reports, experimental results.

**Sarah:** How do you keep the docs in sync with the code?

**Alex:** Three mechanisms. First, API reference is auto-generated from docstrings using Sphinx autodoc. If the code changes, the docs rebuild automatically. Second, we have validation scripts that check for broken cross-references and missing docstrings. Third, every pull request requires documentation updates for any API changes.

**Sarah:** What about the learning paths?

**Alex:** Five paths. Path 0 is for complete beginners -- 125 to 150 hours of prerequisite material on Python, physics, math, control theory. Path 1 is quick start -- get a simulation running in 1 to 2 hours. Paths 2 through 4 are advanced -- custom controllers, research workflows, production deployment.

---

## System Context Diagram: External Boundaries

**Sarah:** If I drew a box around the DIP-SMC-PSO system, what would be outside the box? What are the external interfaces?

**Alex:** Four main boundaries. First: the command line. You invoke `simulate.py` with arguments, it runs, it outputs results to the terminal or files. That is the CLI interface.

**Sarah:** Second?

**Alex:** The web UI. You start Streamlit with `streamlit run streamlit_app.py`. It launches a local web server on port 8501. You open your browser, you interact with sliders and buttons, you visualize results in real time. The Streamlit app imports the same controllers and simulation engine as the CLI -- it is just a different front end.

**Sarah:** Third?

**Alex:** Hardware-In-the-Loop. The plant server runs on one machine, the controller client runs on another. They communicate over TCP using ZeroMQ. The controller sends control signals, the plant returns state measurements. This simulates distributed control systems or tests controllers against real hardware.

**Sarah:** And fourth?

**Alex:** Data export. You can save simulation results to JSON, CSV, or HDF5. External tools like MATLAB, Julia, or R can load those files for post-processing, visualization, or comparison with other controllers.

**Sarah:** So the system has four external interfaces: CLI, web UI, HIL network protocol, and data export formats.

**Alex:** Correct. And each interface is independent. You can use the CLI without the web UI. You can run HIL without data export. The core simulation engine does not know which interface invoked it.

---

## Class Hierarchy: Controllers and Dynamics

**Sarah:** Describe the class hierarchy for controllers.

**Alex:** Base class: BaseController. This is an abstract class with a single method: `compute_control(state, last_control, history)`. It takes the current state, the previous control signal, and the simulation history, and it returns the new control signal.

**Sarah:** And the subclasses?

**Alex:** Seven concrete controllers. ClassicalSMCController, SuperTwistingSMCController, AdaptiveSMCController, HybridAdaptiveSTASMCController, SwingUpController, TerminalSMCController, IntegralSMCController. Each implements `compute_control` with its own algorithm. They all share the same interface, so the simulation runner treats them uniformly.

**Sarah:** What about dynamics models?

**Alex:** Similar hierarchy. Base class: DynamicsInterface with a method `compute_derivatives(state, control)`. Subclasses: SimplifiedDIPDynamics, FullDIPDynamics, LowRankDIPDynamics. Each computes `d(state)/dt` using different physics approximations.

**Sarah:** So you could write a new controller or dynamics model by subclassing the base and implementing one method.

**Alex:** Exactly. That is the extension point. You do not modify existing code. You add a new file, subclass the base, implement the required method, register it with the factory, and it integrates seamlessly.

---

## Re-export Chains: Import Path Flexibility

**Sarah:** You mentioned earlier that `simulation_context.py` exists in three locations. Explain that pattern.

**Alex:** Canonical source: `src/simulation/core/simulation_context.py`. This is the real implementation -- 203 lines. Secondary shim: `src/simulation/context/simulation_context.py` -- 116 lines. It imports from the canonical source and re-exports. Compatibility layer: `src/core/simulation_context.py` -- 13 lines. It imports from the secondary shim and re-exports.

**Sarah:** Why the chain?

**Alex:** Different import paths for different use cases. Legacy code uses `from src.core import SimulationContext`. New code uses `from src.simulation.core import SimulationContext`. Intermediate code uses `from src.simulation.context import SimulationContext`. All three paths work. No broken imports.

**Sarah:** That sounds like technical debt.

**Alex:** It is. But it is documented technical debt. We explicitly marked this as an intentional compatibility pattern in the architectural standards. If we ever do a major version bump, we will consolidate to a single path. Until then, backward compatibility is more valuable than purity.

---

## Workspace Organization: Hidden Directories

**Sarah:** You mentioned hidden directories earlier. What is the purpose of those?

**Alex:** Keep the root clean. Development tools, build artifacts, caches, logs -- anything that is not core to the project goes in a dot-prefixed directory. Examples: `.ai_workspace/` for AI tooling configs, `.cache/` for pytest and hypothesis caches, `academic/` for research artifacts that are visible but separate from production code.

**Sarah:** Why `academic/` instead of `.academic/`?

**Alex:** Because we want it visible in the repository. It contains the research paper, thesis drafts, experiment data, and logs. These are valuable outputs, not ephemeral build artifacts. But they are organizationally separate from the production codebase.

**Sarah:** So the rule is: core files and directories at the root, dev tools and ephemeral data in hidden directories, research outputs in visible but separate directories.

**Alex:** Correct. The goal is that when you clone the repository and list the root, you see 18 items and immediately understand what this project is: a simulation system with controllers, tests, docs, benchmarks, and scripts.

---

## The Value of Visual Thinking for Verbal Description

**Sarah:** We have described the entire architecture verbally. But if you were explaining this to a new contributor, would you not just draw a diagram?

**Alex:** Absolutely. Diagrams are efficient. But the exercise of verbal description is valuable because it forces you to identify what is essential. When you draw a diagram, you include everything. When you describe verbally, you prioritize. You say: "The core is the simulation engine. Controllers sit on top. Optimization tunes the controllers. Utilities provide cross-cutting services." That hierarchy emerges from the verbal explanation.

**Sarah:** And if the verbal explanation is confusing, that tells you something about the architecture.

**Alex:** Exactly. If you cannot explain it clearly, the architecture is probably too complex. The best architectures are simple enough to describe in a few sentences. The details matter, but the high-level structure should be obvious.

**Sarah:** So the verbal description is a design tool, not just a documentation exercise.

**Alex:** Correct. If you are designing a new system, try describing it out loud before you write any code. If the description is convoluted, the code will be worse. If the description is clear, you have a good chance of building something maintainable.

---

## Key Takeaways

**Sarah:** Let us recap the architecture we described today.

**Alex:** The project root has 18 visible items: 9 core files and 8 core directories. Everything else is hidden behind dot-prefixed directories or organized under `academic/`.

**Sarah:** The `src/` directory has four layers: core, controllers/optimization, interfaces/integration, and utilities. Dependencies flow downward only -- no circular imports.

**Alex:** The `tests/` directory mirrors `src/` exactly. Every source file has a corresponding test file. Integration tests and benchmarks live in separate subdirectories.

**Sarah:** Configuration flows from `config.yaml` through Pydantic validation to runtime objects. No global state, no hardcoded parameters.

**Alex:** The system has four external interfaces: CLI, web UI, HIL network protocol, and data export formats. Each is independent.

**Sarah:** Controllers and dynamics models use abstract base classes. You extend by subclassing and implementing one method. The factory pattern handles instantiation.

**Alex:** Compatibility layers and re-export chains provide import path flexibility. These are intentional patterns, not mistakes.

**Sarah:** Documentation lives in `docs/` and is built with Sphinx. API reference is auto-generated. Five learning paths guide users from beginners to advanced.

**Alex:** Verbal description forces you to prioritize and clarify. If you cannot explain your architecture without a diagram, you do not understand it deeply enough.

---

## Pronunciation Guide

For listeners unfamiliar with technical terms used in this episode:

- **Pydantic**: A Python library for data validation. Pronounced "pie-DAN-tik."
- **YAML**: A configuration file format. Pronounced "YAM-ul" (rhymes with "camel").
- **Sphinx**: A documentation generator. Pronounced "SFINKS" (like the mythical creature).
- **ZeroMQ**: A messaging library. Pronounced "zero M-Q."
- **Numba**: A Python compiler for numerical code. Pronounced "NUM-buh."
- **reStructuredText**: A markup language. Often abbreviated as "reST." Pronounced "rest" or "R-S-T."
- **Pytest**: A testing framework. Pronounced "pie-test."

---

## What's Next

**Sarah:** Next episode, Episode 24, we cover lessons learned and best practices. The mistakes we made, the patterns we discovered, and the advice we would give to someone starting a similar project.

**Alex:** The things you only learn by building something real and living with the consequences.

**Sarah:** Episode 24. Coming soon.

---

## Pause and Reflect

Architecture is communication. When you organize code into directories, name modules, define interfaces, and draw boundaries, you are communicating intent to future readers. A well-structured codebase tells a story: "This is the core. These are the extensions. These are the tools. These are the tests." A poorly structured codebase is a pile of files with no narrative. The goal of architectural thinking is not to draw perfect diagrams. It is to make the system understandable. And if you can explain it without pictures, you have succeeded.

---

## Resources

- **Repository:** https://github.com/theSadeQ/dip-smc-pso.git
- **Architecture standards:** `.ai_workspace/guides/architectural_standards.md`
- **Workspace organization:** `.ai_workspace/guides/workspace_organization.md`
- **Documentation build system:** `.ai_workspace/guides/documentation_build_system.md`
- **Getting Started Guide:** `docs/guides/getting-started.md`

---

*Educational podcast episode -- describing system architecture verbally for control systems research software*
