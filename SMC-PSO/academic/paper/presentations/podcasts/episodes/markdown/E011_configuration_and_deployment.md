# E011: Configuration and Deployment

**Part:** Part 2 Infrastructure & Tooling
**Duration:** 15-20 minutes
**Source:** DIP-SMC-PSO Configuration System

---

## Opening Hook

**Sarah:** How do you prevent a user from setting the cart mass to negative five kilograms?

**Alex:** You validate configuration before the simulation runs. Not during. Not after. Before. If the config is invalid, the program refuses to start. No silent failures. No "it worked on my machine." Today we talk about configuration as code -- how `config.yaml` controls everything, how Pydantic ensures type safety, and what it takes to deploy this system.

---

## The Configuration Problem

**Sarah:** Why not just hardcode parameters in the Python files?

**Alex:** Three reasons. First: reproducibility. If your controller gains are scattered across ten Python files, how do you reproduce an experiment? With a single config file, you version it in Git, and the entire simulation is reproducible from that one file. Second: validation. Hardcoded values cannot be validated before runtime. A config file can be parsed, validated, and rejected if invalid. Third: parameter sweeps. If you want to test 100 different gain combinations, you generate 100 config files. No code changes required.

**Sarah:** So configuration is a first-class artifact, not an afterthought.

**Alex:** Exactly. The config file is as important as the code.

---

## config.yaml: The Cockpit Control Panel

**Sarah:** Walk me through the config file. What is in there?

**Alex:** Think of config.yaml as the Cockpit Control Panel for the simulation. Just like a pilot has switches for engines, flaps, landing gear -- each controlling a different system -- we have six main sections. Physics panel: masses, lengths, friction coefficients, gravity. Everything that defines the physical system. Controllers panel: gains, boundary layers, adaptation rates for each of the seven controllers. PSO optimization panel: particle count, iterations, inertia weight, cost function weights. Simulation panel: duration, timestep, initial conditions. Hardware-in-the-loop panel: network settings, timeouts, IP addresses. Monitoring panel: latency thresholds, deadline detection, logging verbosity.

**Sarah:** How big is this control panel?

**Alex:** Approximately 400 lines with extensive comments. Every parameter has an inline comment explaining its purpose, units, and often a citation or issue reference. Think of it as labeled switches with instruction placards. For example: "boundary layer: 0.3 -- Increased from 0.02 for Issue #12 chattering reduction." You know not just WHAT the setting is, but WHY it was changed.

---

## Physics Parameters: Defining the System

**Sarah:** What physics parameters are configurable?

**Alex:** Twelve main parameters defining the physical system. Cart mass, two pendulum masses, two pendulum lengths, center of mass locations, moments of inertia, gravity, and friction coefficients. These define whether you are simulating a lightweight lab prototype or a heavy industrial system.

**Sarah:** What happens if someone sets cart mass to negative five kilograms?

**Alex:** This is where validation becomes critical. Imagine the physics engine trying to simulate negative mass. Newton's second law -- force equals mass times acceleration -- would produce nonsensical results. Negative mass would accelerate TOWARD you when you push it away. The universe does not work this way. So Pydantic validation fails immediately with a clear error: "Field 'cart_mass' expected positive value, received -1.5. Physical masses cannot be negative." The simulation refuses to start. You fix the config, retry. No silent failures. No impossible physics leaking into results.

**Sarah:** What about physically implausible but technically positive values? Like a pendulum with impossibly low inertia?

**Alex:** Additional physics validation catches this. We compute the minimum possible inertia based on mass and length -- basic physics says inertia cannot be below mass times length squared. If the configured inertia is below this, validation fails with: "pendulum1_inertia violates physics constraints. You configured 0.0001, but minimum for a 0.2 kg pendulum at 0.4 meters is 0.008." Again, the simulation refuses to start. We prevent impossible physics at the door, not after you have wasted hours running a simulation that produces meaningless results.

---

## Controller Configuration: Seven Variants

**Sarah:** How are controllers configured?

**Alex:** Each controller has a section under `controllers:`. Example for Classical SMC:

```yaml
controllers:
  classical_smc:
    gains: [23.07, 12.85, 5.51, 3.49, 2.23, 0.15]
    max_force: 150.0
    dt: 0.001
    boundary_layer: 0.3
```

The `gains` array contains controller-specific parameters. For Classical SMC, these are the sliding surface coefficients and switching gains. Each controller interprets the gains differently.

**Sarah:** How does the system know how many gains to expect?

**Alex:** The controller's Pydantic schema. ClassicalSMCConfig expects exactly 6 gains. STASMCConfig expects exactly 6 different gains. AdaptiveSMCConfig expects 5 gains. If you provide the wrong number, validation fails: "classical_smc.gains expected 6 elements, received 5."

**Sarah:** What about the boundary layer parameter?

**Alex:** Controls chattering mitigation. Classical SMC switches control at the sliding surface. If `boundary_layer=0`, you get perfect but chattering control -- the actuator oscillates infinitely fast trying to stay exactly on the surface. If `boundary_layer=0.3`, the controller smooths the switching in a 0.3-radian band around the surface. Less chattering, slightly worse tracking.

---

## PSO Configuration: Optimization Parameters

**Sarah:** The PSO section. What is configured there?

**Alex:** Algorithm parameters for Particle Swarm Optimization. `n_particles: 50` -- how many candidate solutions search the parameter space simultaneously. `n_iterations: 100` -- how many generations the swarm evolves. `inertia_weight: 0.7` -- controls exploration vs exploitation tradeoff. `cognitive_coeff: 2.0` and `social_coeff: 2.0` -- how much particles trust their own best vs the swarm's best. `cost_weights`: relative importance of state error, control effort, settling time, and overshoot in the cost function.

**Sarah:** Give me the cost weights.

**Alex:** `state_error: 1.0`, `control_effort: 0.1`, `settling_time: 0.5`, `overshoot: 0.3`. This says: minimize tracking error most aggressively, care less about control effort, penalize slow settling moderately, penalize overshoot somewhat. Tuning these weights changes the optimization objective -- you get different controllers depending on what you prioritize.

**Sarah:** How do you know what weights to use?

**Alex:** Domain expertise and iteration. If you are designing for an industrial robot, you might weight `control_effort: 0.5` higher because actuators are expensive and wear out. If you are optimizing for academic benchmarks, you might set `state_error: 2.0` to maximize tracking accuracy. There is no universal right answer.

---

## Simulation Settings: Duration and Timestep

**Sarah:** The simulation section. What is there?

**Alex:** `duration: 10.0` seconds -- how long to simulate. `dt: 0.01` seconds -- timestep for numerical integration, corresponding to 100 Hz control rate. `initial_state: [0.0, 0.05, -0.03, 0.0, 0.0, 0.0]` -- starting position: cart at origin, small perturbation in angles. `use_full_dynamics: false` -- whether to use simplified or full nonlinear dynamics.

**Sarah:** Why make dynamics a configuration option?

**Alex:** Performance vs accuracy tradeoff. Simplified dynamics -- linearized around equilibrium -- compute in 5 microseconds. Full nonlinear dynamics with Coriolis and centrifugal effects compute in 50 microseconds. For PSO with 5,000 evaluations, simplified dynamics finish in 3 minutes, full dynamics take 30 minutes. You develop with simplified, validate with full.

**Sarah:** What constraints exist on timestep?

**Alex:** Stability limits. The fastest dynamics -- pendulum natural frequencies -- are around 5 radians per second. Nyquist sampling theorem says you need at least 10 samples per oscillation, so `dt <= 0.1` seconds. In practice, we use `dt=0.01` for 100 Hz, giving a 10x margin. If you set `dt=0.5`, validation warns: "Timestep 0.5s exceeds Nyquist limit for system dynamics. Maximum safe timestep: 0.1s."

---

## Pydantic Validation: The Bouncer at the Door

**Sarah:** Explain how Pydantic validation works.

**Alex:** Think of Pydantic as a Bouncer at the door of a nightclub. You try to enter with your config file. The Bouncer checks your ID -- are you old enough? In our case: are your data types correct? Is cart_mass a number or did you accidentally write "heavy"? Next, the Bouncer checks the dress code -- no sneakers, no tank tops. In our case: are your values within acceptable ranges? Is mass positive? Is length less than 5 meters? If everything checks out, you are allowed in -- the simulation starts. If anything is wrong, you get turned away with a specific reason: "cart_mass must be a float, you provided a string" or "pendulum_length exceeds maximum of 5.0 meters."

**Sarah:** Why is this better than just trying to run the simulation and seeing what breaks?

**Alex:** Fail fast, fail clearly. Without the Bouncer, you would start the simulation, run for 3 minutes, then hit a crash deep in the physics engine with a cryptic error: "cannot multiply string by float." Now you have to debug backwards -- what config value was wrong? With Pydantic, you get rejected at the door with a clear message before wasting any time. The Bouncer knows exactly what is acceptable, checks your ID thoroughly, and tells you precisely what is wrong if you do not meet requirements.

**Sarah:** What happens when you load a config?

**Alex:** You call the load config function. Internally, Pydantic validates every field: type correctness, value constraints, required versus optional parameters. If validation passes, you get a validated config object -- the Bouncer let you in. If validation fails, you get a detailed error message -- the Bouncer explains exactly why you were rejected. No simulation runs until your config passes inspection.

---

## Configuration Loading Process

**Sarah:** Walk me through the loading process step by step.

**Alex:** Step 1: Read `config.yaml` from disk using PyYAML. You get a nested dictionary. Step 2: Pass dictionary to Pydantic `Config` model. Pydantic recursively validates all nested sections -- physics, controllers, PSO, simulation, HIL, monitoring. Step 3: Additional physics validation -- check inertia bounds, ensure timestep meets Nyquist criterion. Step 4: Cross-section validation -- if `use_full_dynamics=true`, verify that `include_coriolis_effects` and related flags are consistent. Step 5: If all validations pass, return immutable config object. If any fail, collect all errors and report them together.

**Sarah:** Why collect all errors instead of stopping at the first?

**Alex:** Better developer experience. Imagine fixing one error, re-running, hitting the next error, fixing that, hitting a third. Frustrating. Collecting all errors at once lets you fix them in batch: "cart_mass is negative, pendulum1_inertia violates physics constraints, classical_smc.gains has wrong length (5 expected 6)."

---

## Deployment Scenarios: Three Environments

**Sarah:** You mentioned deployment. What environments does this system support?

**Alex:** Three main scenarios. First: local development. Clone repo, create virtual environment, `pip install -r requirements.txt`, run `python simulate.py`. Everything on one machine, default config, immediate feedback. Second: batch computation. Research cluster or cloud instance running parameter sweeps, Monte Carlo simulations, PSO optimization. Headless execution, no GUI, results saved to files. Third: hardware-in-the-loop. Plant server runs on one machine -- could be a PLC or industrial PC connected to real hardware. Controller client runs on another machine. They communicate over network using ZeroMQ.

**Sarah:** What does deployment to each environment require?

**Alex:** Local dev: Python 3.9+, NumPy, SciPy, Matplotlib, Streamlit for web UI. Install time: 5 minutes. Batch compute: Same dependencies minus Streamlit. Add Numba for JIT acceleration. Headless mode: `python simulate.py --no-gui --save results.json`. HIL: Everything from batch compute, plus ZeroMQ, and specific network configuration -- firewall rules, static IPs, synchronized clocks.

---

## Virtual Environments and Dependencies

**Sarah:** Why virtual environments?

**Alex:** Isolation. Your project depends on NumPy 1.24. Another project depends on NumPy 1.19 with breaking API changes. If you install both globally, one breaks. Virtual environment creates a project-specific Python installation with its own packages. No conflicts.

**Sarah:** How do you create one?

**Alex:** Three commands:

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The `.venv` directory contains an isolated Python environment. Activate it, and `python` and `pip` point to the local installation. Deactivate when done, and you are back to the system Python.

**Sarah:** What is in `requirements.txt`?

**Alex:** 15 main dependencies with pinned versions:

```
numpy==1.24.3
scipy==1.10.1
matplotlib==3.7.1
pydantic==2.0.2
pyyaml==6.0
numba==0.57.0
streamlit==1.23.1
pyswarms==1.3.0
pytest==7.3.1
pytest-cov==4.1.0
hypothesis==6.82.0
pyzmq==25.1.0
# Optional dependencies
cvxpy==1.3.1  # For MPC controller
optuna==3.2.0  # For alternative optimization algorithms
```

Pinned versions ensure reproducibility. If you install today or six months from now, you get identical dependencies.

---

## Configuration Overrides: Command-Line and Environment

**Sarah:** Can you override config values without editing the YAML file?

**Alex:** Yes. Three methods. First: command-line arguments. `python simulate.py --ctrl classical_smc --gains 20,10,5,3,2,0.1` overrides controller and gains. Second: environment variables. `export DIPSMC_PHYSICS_CART_MASS=2.0` overrides cart mass. Third: config file cascading. Load `config.yaml` as base, then `config_local.yaml` if it exists, then apply overrides. This lets you version the base config in Git and keep local tweaks unversioned.

**Sarah:** Why would you use environment variables?

**Alex:** Cloud deployments. Docker containers, Kubernetes pods -- you inject configuration through environment variables. The container image is immutable, but behavior changes based on env vars set by the orchestration system.

**Sarah:** Example?

**Alex:** Kubernetes deployment:

```yaml
env:
  - name: DIPSMC_PSO_N_PARTICLES
    value: "100"
  - name: DIPSMC_PSO_N_ITERATIONS
    value: "200"
  - name: DIPSMC_SIMULATION_DURATION
    value: "20.0"
```

Same container runs different experiments based on env vars.

---

## Hardware-In-the-Loop Configuration

**Sarah:** The HIL section. What is configured there?

**Alex:** Network and protocol settings. `plant_host: "192.168.1.100"`, `plant_port: 5555` -- where the plant server listens. `controller_host: "192.168.1.101"`, `controller_port: 5556` -- where the controller client connects. `protocol: "tcp"` or `"udp"` -- ZeroMQ transport. `timeout_ms: 100` -- how long to wait for messages before declaring failure. `enable_logging: true` -- whether to log every control cycle for post-mortem analysis.

**Sarah:** Why separate plant and controller?

**Alex:** Mimics real distributed control systems. Industrial plants have sensors and actuators connected to a PLC. The controller runs on a separate computer -- could be in a control room, could be a cloud server. They communicate over Ethernet or fieldbus. HIL simulates this by running plant dynamics on one machine, controller on another.

**Sarah:** What if the network is unreliable?

**Alex:** Timeout and retry logic. If a control signal does not arrive within 100 milliseconds, the plant uses the last valid control signal and increments a missed-deadline counter. After 10 consecutive misses, the plant declares controller failure and enters safe mode -- applies zero force and logs the failure.

---

## Production Considerations: Thread Safety and Memory

**Sarah:** What does production deployment require beyond basic setup?

**Alex:** Four main concerns. First: thread safety. If multiple threads run simulations in parallel, controllers must not share mutable state. We use weakref patterns and explicit cleanup methods. Second: memory management. Controllers must not leak memory during long-running optimizations. We validate with 10,000 consecutive simulations -- memory growth must be zero. Third: numerical stability. Dynamics models must detect singularities and NaN propagation. If the inertia matrix is near-singular, switch to a regularized inverse. Fourth: logging and monitoring. Production systems need structured logs with timestamps, simulation IDs, and performance metrics.

**Sarah:** Is this system production-ready?

**Alex:** No. Production readiness score is 23.9 out of 100. It is research-ready -- single-threaded and multi-threaded operation validated, controllers functional and tested, documentation complete. But production requires: fault injection testing, PLC integration, formal safety certification, real-time OS deployment, hardware validation. That is 200 to 300 additional hours of work -- a different project with different goals.

---

## Configuration as Code: Versioning and Auditing

**Sarah:** You mentioned versioning config files in Git. Why is that important?

**Alex:** Reproducibility and auditing. Every experiment has a corresponding config file committed to Git. You can reproduce any result by checking out the commit, loading the config, running the simulation. You know exactly what parameters were used. For academic papers, this is critical -- reviewers can verify your claims by running your exact configuration.

**Sarah:** Give me an example workflow.

**Alex:** You run an experiment: `python simulate.py --config experiments/exp_001_classical_smc.yaml --save results/exp_001.json`. You commit both files:

```bash
git add experiments/exp_001_classical_smc.yaml results/exp_001.json
git commit -m "Experiment 001: Classical SMC with optimized gains"
```

Six months later, a reviewer asks: "How did you get that settling time?" You check out the commit, re-run with the exact config, verify the result matches. Reproducibility.

---

## Configuration Validation Scripts

**Sarah:** Can you validate a config file without running a simulation?

**Alex:** Yes. `python scripts/validate_config.py config.yaml`. This loads the config, runs all Pydantic validations, runs physics constraints checks, and reports any errors. Useful for CI/CD -- you validate config changes in pull requests before merging.

**Sarah:** What does the validation script check beyond Pydantic?

**Alex:** Domain-specific constraints. Physics plausibility: masses positive, lengths reasonable, inertias within bounds. Controller stability: gains must satisfy Lyapunov-based stability criteria if known. PSO feasibility: particle count and iterations must allow meaningful exploration of the search space. Simulation sanity: duration must be long enough for the system to settle, timestep must satisfy Nyquist criterion.

---

## Default Configuration and Minimal Config

**Sarah:** Do you provide a default config for new users?

**Alex:** Yes. `config.yaml` at the project root is the reference configuration. It has validated parameters, extensive comments, and known-good controller gains from PSO optimization. New users can run `python simulate.py` with no arguments and get a working simulation.

**Sarah:** What about a minimal config for advanced users?

**Alex:** You can omit parameters with sensible defaults. Minimal config:

```yaml
physics:
  cart_mass: 1.5
  pendulum1_mass: 0.2
  pendulum2_mass: 0.15
  pendulum1_length: 0.4
  pendulum2_length: 0.3

controllers:
  classical_smc:
    gains: [23.07, 12.85, 5.51, 3.49, 2.23, 0.15]

simulation:
  duration: 10.0
  dt: 0.01
```

Everything else -- gravity, friction, boundary layers, PSO settings -- uses defaults from the Pydantic schema.

---

## Key Takeaways

**Sarah:** Let us recap configuration and deployment.

**Alex:** config.yaml is the Cockpit Control Panel -- six main sections controlling physics, controllers, PSO, simulation, HIL, and monitoring. Approximately 400 lines with inline comments and citations explaining each switch and setting.

**Sarah:** Pydantic acts as the Bouncer at the door -- checks your ID (data types) and dress code (value constraints). Negative masses, wrong gain counts, physics violations all caught before simulation starts. Fail fast, fail clearly.

**Alex:** Physics validation includes domain-specific checks: inertia bounds, Nyquist timestep limits, stability criteria for controller gains.

**Sarah:** Three deployment scenarios: local dev (5-minute setup), batch compute (headless, cloud-ready), hardware-in-the-loop (distributed, network-based).

**Alex:** Virtual environments provide dependency isolation. `requirements.txt` pins 15 dependencies with exact versions for reproducibility.

**Sarah:** Configuration overrides via command-line arguments, environment variables, or cascading config files. Supports Docker and Kubernetes deployments.

**Alex:** Production considerations: thread safety with weakref patterns, memory leak validation over 10,000 simulations, numerical stability checks, structured logging.

**Sarah:** Configuration as code enables versioning in Git, reproducible experiments, and audit trails for academic papers.

**Alex:** Validation scripts check config files in CI/CD without running simulations. Domain-specific constraints beyond Pydantic type checking.

---

## Pronunciation Guide

For listeners unfamiliar with technical terms used in this episode:

- **Pydantic**: A Python data validation library. Pronounced "pie-DAN-tik."
- **YAML**: A configuration file format. Pronounced "YAM-ul" (rhymes with "camel").
- **PyYAML**: Python YAML parser. Pronounced "pie-YAM-ul."
- **Nyquist**: Sampling theorem named after Harry Nyquist. Pronounced "NYE-kwist" (like "night" + "twist").
- **ZeroMQ**: A messaging library. Pronounced "zero M-Q."
- **HIL**: Hardware-In-the-Loop. Say each letter: "H-I-L."
- **Kubernetes**: Container orchestration system. Pronounced "koo-ber-NET-eez" (often shortened to "K8s").

---

## What's Next

**Sarah:** Next episode, Episode 12, we cover testing strategy and quality assurance. How 4,563 tests validate 105,000 lines of code, why critical modules require 100% coverage, and how property-based testing catches edge cases.

**Alex:** Testing is not about proving correctness. It is about documenting how things fail.

**Sarah:** Episode 12. Coming soon.

---

## Pause and Reflect

Configuration is a design decision. When you hardcode a parameter, you are saying: "This value will never need to change." When you make it configurable, you are saying: "Different contexts require different values." The trick is knowing which is which. Over-configuration leads to complexity -- 500 knobs on the Cockpit Control Panel with no guidance on which matter. Under-configuration leads to inflexibility -- you hardcode a timestep that works on your laptop but violates Nyquist on real hardware. Good configuration finds the balance: expose what needs to vary, hide what can be safely defaulted. And validate everything with a strict Bouncer at the door. The cost of rejecting an invalid config at load time is zero seconds. The cost of discovering the error after a 3-hour PSO optimization run is three lost hours. Fail fast, fail clearly, fail before wasting time.

---

## Resources

- **Repository:** https://github.com/theSadeQ/dip-smc-pso.git
- **Configuration File:** `config.yaml` (400 lines, extensively commented)
- **Configuration Module:** `src/config.py` (Pydantic schemas and validation)
- **Requirements File:** `requirements.txt` (15 pinned dependencies)
- **Validation Script:** `scripts/validate_config.py`

---

*Educational podcast episode -- configuring and deploying control systems research software*
