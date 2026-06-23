[<--Back to Beginner Roadmap](../beginner-roadmap.md)

---

# Phase 3: Hands-On Learning (Week 9-12, ~25 hours)

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
      <span class="phase-badge phase-3">Phase 3</span>
      <span class="breadcrumb-text">Hands-On Learning</span>
    </li>
  </ol>
</nav>
:::

::::

---

**Prerequisites**: Phase 1-2 completion
**Previous Phase**: [Phase 2: Core Concepts](phase-2-core-concepts.md)
**Next Phase**: [Phase 4: Advancing Skills](phase-4-advancing-skills.md)

**Goal**: Run your first simulations, interpret results, compare controllers, and understand how to modify parameters.

## Phase 3 Overview

| Sub-Phase | Topic | Time | Why You Need This |
|-----------|-------|------|-------------------|
| 3.1 | Running Your First Simulation | 8 hours | Get hands-on experience |
| 3.2 | Understanding Simulation Results | 6 hours | Interpret plots and metrics |
| 3.3 | Comparing Controllers | 5 hours | See performance differences |
| 3.4 | Modifying Configuration | 4 hours | Learn to tune parameters |
| 3.5 | Troubleshooting Common Issues | 2 hours | Fix errors independently |

**Total**: ~25 hours over 4 weeks (~6 hours/week)

**Visual Aids**: [View Phase 3 Diagrams -->](phase-3-diagrams.md) (Simulation Workflow, Result Interpretation, Tuning Guide, Analysis)

---

<details>
<summary>3.1 Running Your First Simulation</summary>

## Phase 3.1: Running Your First Simulation (8 hours)

**Goal**: Successfully run your first DIP simulation and see the results.

### What You'll Learn

- How to activate the virtual environment
- Understanding the command-line interface
- Running simulations with different controllers
- Viewing and saving results

### Learning Path

**Step 1: Environment Setup Review (2 hours)**

**Activate Your Virtual Environment** (from Phase 1.3):

::::{tab-set}
:sync-group: os

:::{tab-item} Windows
:sync: win
:selected:

```bash
# Navigate to project directory
cd D:\Projects\dip-smc-pso

# Activate virtual environment (Command Prompt)
venv\Scripts\activate.bat

# OR activate (PowerShell)
venv\Scripts\Activate.ps1

# You should see (venv) at the start of your command prompt
```

:::

:::{tab-item} Mac/Linux
:sync: unix

```bash
# Navigate to project directory
cd ~/projects/dip-smc-pso

# Activate virtual environment
source venv/bin/activate

# You should see (venv) at the start of your command prompt
```

:::

::::

**Verify Installation**:

::::{tab-set}
:sync-group: os

:::{tab-item} Windows
:sync: win
:selected:

```bash
# Check Python version (should be 3.9+)
python --version

# Test imports
python -c "import numpy, scipy, matplotlib; print('OK - All packages installed')"

# If you get errors, reinstall packages
pip install -r requirements.txt
```

:::

:::{tab-item} Mac/Linux
:sync: unix

```bash
# Check Python version (should be 3.9+)
python3 --version

# Test imports
python3 -c "import numpy, scipy, matplotlib; print('OK - All packages installed')"

# If you get errors, reinstall packages
pip3 install -r requirements.txt
```

:::

::::

**Project Structure Review**:

```
dip-smc-pso/
├─ src/                  # Source code
│  ├─ controllers/       # SMC implementations
│  ├─ plant/             # DIP dynamics
│  ├─ optimizer/         # PSO tuner
│  └─ utils/             # Helper functions
├─ simulate.py           # Main entry point (YOU WILL RUN THIS)
├─ config.yaml           # Configuration file
├─ requirements.txt      # Dependencies
└─ docs/                 # Documentation
```

---

**Step 2: Understanding the CLI (3 hours)**

**Help Command**:

```bash
python simulate.py --help
```

**Output** (shortened):
```
usage: simulate.py [options]

Options:
  --ctrl CONTROLLER     Controller type: classical_smc, sta_smc, adaptive_smc, etc.
  --plot                Show plots after simulation
  --save FILE           Save results to JSON file
  --run-pso             Run PSO optimization
  --print-config        Print current configuration
  --config FILE         Use custom config file
  -h, --help            Show this help message
```

**Key Options Explained**:

| Option | Purpose | Example |
|--------|---------|---------|
| `--ctrl` | Select controller | `--ctrl classical_smc` |
| `--plot` | Show result plots | `--plot` |
| `--save` | Save results | `--save results.json` |
| `--run-pso` | Optimize gains | `--run-pso` |
| `--config` | Custom config | `--config my_config.yaml` |

**Print Current Configuration**:

```bash
python simulate.py --print-config
```

This shows all parameters from config.yaml (masses, lengths, gains, simulation duration, etc.).

---

**Step 3: Running Your First Simulation (3 hours)**

**Simplest Command**:

```bash
python simulate.py --ctrl classical_smc --plot
```

**What happens**:
1. Script loads config.yaml
2. Creates Classical SMC controller with default gains
3. Creates DIP plant with default parameters
4. Runs simulation for 10 seconds (default)
5. Generates plots
6. Shows plots in new window

**Console Output** (example):

```
[INFO] Starting simulation...
[INFO] Controller: Classical SMC
[INFO] Initial state: [0.0, 0.0, 0.1, 0.0, 0.1, 0.0]  # Small angle disturbance
[INFO] Simulation time: 10.0 seconds
[INFO] Timestep: 0.01 seconds (1000 steps)

Simulating: [====================] 100% (1000/1000) ETA: 0s

[INFO] Simulation complete in 2.3 seconds
[INFO] Performance Metrics:
  - Settling time: 4.2 seconds
  - Max overshoot: 0.03 rad (1.7 degrees)
  - Control effort: 125.4 J
  - Chattering index: 0.42

[INFO] Generating plots...
[OK] Plots displayed. Close plot window to exit.
```

**Understanding the Output**:

- **Initial state**: Starting condition (small disturbance from upright)
- **Settling time**: How long until system stabilizes (smaller is better)
- **Overshoot**: How much it overshoots the target (smaller is better)
- **Control effort**: Energy used (lower is more efficient)
- **Chattering index**: Measure of oscillation (lower is smoother)

**What You See** (6 subplots):

1. **Cart Position vs Time**: Should return to 0
2. **Pendulum 1 Angle vs Time**: Should converge to 0 (upright)
3. **Pendulum 2 Angle vs Time**: Should converge to 0 (upright)
4. **Cart Velocity vs Time**: Should converge to 0
5. **Pendulum Angular Velocities vs Time**: Should converge to 0
6. **Control Input (Force) vs Time**: Shows force applied to cart

**Try This** (hands-on):

Run the simulation and answer:
1. How long does it take for θ1 to reach near-zero? (settling time)
2. Does the cart position return to zero?
3. Is the control force smooth or oscillating?
4. What's the maximum force magnitude?

---

### Self-Assessment: Phase 3.1

**Checklist**:

- ✅ I can activate the virtual environment without errors
- ✅ I can run `python simulate.py --help` and see options
- ✅ I successfully ran my first simulation
- ✅ I see 6 subplots showing system behavior
- ✅ I understand what settling time and overshoot mean

**If all checked**: ✅ Move to Phase 3.2
**If simulation won't run**: ⚠️ Check troubleshooting in Phase 3.5
**If plots don't show**: ⚠️ Check matplotlib backend (use `--save` instead)

</details>

---

<details>
<summary>3.2 Understanding Simulation Results</summary>

## Phase 3.2: Understanding Simulation Results (6 hours)

**Goal**: Deeply understand what each plot shows and what "good" performance looks like.

### Learning Path

**Step 1: State Plots (2 hours)**

**Plot 1: Cart Position (x)**

```
Cart Position vs Time

  0.1 |
  0.0 +----\___________________  <- Returns to origin
 -0.1 |     \
      +--------------------------> Time (s)
      0    2    4    6    8   10
```

**What it shows**:
- Initial position: x = 0 (cart at center)
- Controller may move cart left/right to balance pendulums
- Final position: Should return to x ≈ 0 (±0.01 m tolerance)

**Good performance**: Small excursion, smooth return to zero

**Poor performance**: Large oscillations, doesn't settle, or drifts away

---

**Plot 2 & 3: Pendulum Angles (θ1, θ2)**

```
Pendulum 1 Angle vs Time

  0.15|    *
  0.10|   * \
  0.05|  *   \___/\__________  <- Converges to upright
  0.00|             \________
 -0.05|
      +--------------------------> Time (s)
      0    2    4    6    8   10
```

**What it shows**:
- Initial: θ1 = 0.1 rad (5.7 degrees off vertical)
- Controller works to bring both pendulums to θ = 0 (upright)
- Transient: May overshoot, oscillate before settling
- Final: θ1, θ2 ≈ 0 (±0.01 rad)

**Key observations**:
- **Settling time**: When does |θ| stay below 0.01 rad?
- **Overshoot**: Maximum deviation from target
- **Oscillations**: Does it ring back and forth?

**Good performance**: Fast settling, minimal overshoot, smooth convergence

---

**Plot 4 & 5: Velocities (ẋ, θ̇1, θ̇2)**

**What it shows**:
- How fast the cart and pendulums are moving
- Should all converge to zero (system at rest)
- Velocity spikes indicate rapid movements

**Typical behavior**:
- Initial velocities: 0 (system starts at rest)
- Transient: Large velocities as controller stabilizes
- Final: All velocities --> 0

**Good performance**: Velocities decay smoothly to zero

---

**Step 2: Control Input Plot (2 hours)**

**Plot 6: Control Force (F)**

```
Control Input (Force) vs Time

  20 |  /\  /\              <- High-frequency switching (chattering)
  10 | /  \/  \____
   0 |/         \___________  <- Settles to zero
 -10 |
 -20 |
     +--------------------------> Time (s)
     0    2    4    6    8   10
```

**What it shows**:
- Horizontal force applied to cart (Newtons)
- Limited to [-20, 20] N (saturation limits)
- Sign indicates direction (+ right, - left)

**Chattering**:
- Rapid oscillations in control signal
- Caused by ideal SMC sign function
- Reduced by boundary layer (tanh instead of sign)

**What to look for**:
- **Magnitude**: Is force within limits? (saturated = bad)
- **Smoothness**: Is it smooth or oscillating rapidly?
- **Settling**: Does force --> 0 as system stabilizes?

**Good control**:
- Moderate initial force (not saturated)
- Smooth transitions (low chattering)
- Settles to zero with system

---

**Step 3: Performance Metrics (2 hours)**

**Metric 1: Settling Time**

**Definition**: Time until system stays within ±1% of target

**Calculation**:
```python
settling_time = first time t where |θ1(t)| < 0.01 and |θ2(t)| < 0.01 for all t' > t
```

**Typical values**:
- Classical SMC: 4-6 seconds
- STA-SMC: 3-5 seconds
- Adaptive/Hybrid: 2-4 seconds

**What it means**:
- How quickly the controller stabilizes the system
- Lower is better (faster response)
- Very low settling time may indicate aggressive control (high chattering)

---

**Metric 2: Overshoot**

**Definition**: Maximum deviation from target during transient

**Calculation**:
```python
overshoot_theta1 = max(|θ1(t)|) - |θ1(0)|  # How much beyond initial disturbance
```

**Typical values**:
- Good: < 0.05 rad (< 3 degrees)
- Moderate: 0.05-0.1 rad
- Poor: > 0.1 rad (significant overshoot)

**What it means**:
- How much the system "overshoots" the target while stabilizing
- Lower is better (less oscillation)
- High overshoot can cause instability

---

**Metric 3: Control Effort**

**Definition**: Total energy used by controller

**Calculation**:
```python
control_effort = integral of F²(t) dt  # Joules
```

**Typical values**:
- Efficient: 50-100 J
- Moderate: 100-200 J
- High: > 200 J

**What it means**:
- Energy consumption
- Lower is better (more efficient)
- Tradeoff: Fast settling often requires high effort

---

**Metric 4: Chattering Index**

**Definition**: Measure of high-frequency oscillations

**Calculation**:
```python
chattering = std(diff(F)) / mean(|F|)  # Relative variation
```

**Typical values**:
- Low chattering: < 0.3 (smooth)
- Moderate: 0.3-0.6
- High chattering: > 0.6 (very oscillatory)

**What it means**:
- Smoothness of control signal
- Lower is better (less wear on actuators)
- STA-SMC designed to reduce chattering

---

### Self-Assessment: Phase 3.2

**Quiz**:

1. What does the cart position plot show?
2. What does "settling time" mean?
3. What is chattering and why is it undesirable?
4. Which metric measures energy efficiency?
5. What should all velocities converge to?

**Practical Exercise**:

Sketch (on paper) what a "good" pendulum angle plot looks like vs a "poor" one with high overshoot.

**If you can complete quiz and sketch**: ✅ Move to Phase 3.3
**If struggling with plots**: ⚠️ Review Step 1, run more simulations
**If struggling with metrics**: ⚠️ Review Step 3, compare controller outputs

</details>

---

<details>
<summary>3.3 Comparing Controllers</summary>

## Phase 3.3: Comparing Controllers (5 hours)

**Goal**: Run simulations with different SMC variants and compare their performance.

### Learning Path

**Step 1: Running Multiple Controllers (2 hours)**

**Controller Options**:

| Command | Controller | Key Feature |
|---------|------------|-------------|
| `--ctrl classical_smc` | Classical SMC | Baseline, simple |
| `--ctrl sta_smc` | Super-Twisting | Reduced chattering |
| `--ctrl adaptive_smc` | Adaptive SMC | Learns optimal gains |
| `--ctrl hybrid_adaptive_sta_smc` | Hybrid | Best of both |

**Run Each Controller**:

```bash
# Classical
python simulate.py --ctrl classical_smc --plot --save classical_results.json

# Super-Twisting
python simulate.py --ctrl sta_smc --plot --save sta_results.json

# Adaptive
python simulate.py --ctrl adaptive_smc --plot --save adaptive_results.json

# Hybrid
python simulate.py --ctrl hybrid_adaptive_sta_smc --plot --save hybrid_results.json
```

**What to observe**:
- Do all controllers stabilize the system?
- Which settles fastest?
- Which has smoothest control?
- Which uses least energy?

---

**Step 2: Side-by-Side Comparison (2 hours)**

**Create Comparison Table** (from saved results):

| Metric | Classical | STA | Adaptive | Hybrid |
|--------|-----------|-----|----------|--------|
| Settling Time (s) | 4.2 | 3.5 | 3.8 | 2.9 |
| Max Overshoot (rad) | 0.03 | 0.02 | 0.04 | 0.02 |
| Control Effort (J) | 125 | 110 | 95 | 105 |
| Chattering Index | 0.42 | 0.25 | 0.38 | 0.20 |

**Analysis**:

**Classical SMC**:
- Pros: Simple, reliable baseline
- Cons: Moderate chattering, slower settling
- Use when: Simplicity is priority

**Super-Twisting (STA)**:
- Pros: Low chattering, smooth control
- Cons: Slightly slower than hybrid
- Use when: Smoothness is critical

**Adaptive SMC**:
- Pros: Low control effort (learns efficient gains)
- Cons: Moderate overshoot, slower convergence initially
- Use when: Energy efficiency matters

**Hybrid Adaptive STA**:
- Pros: Best overall (fast + smooth + efficient)
- Cons: More complex, harder to tune manually
- Use when: Maximum performance needed

---

**Step 3: Understanding Tradeoffs (1 hour)**

**The Fundamental Tradeoff**:

```
                Fast Settling
                     ^
                     |
     Hybrid    STA   |
       *       *     |
                     |     * Classical
                     |
    Adaptive *       |
                     |
    <----------------+----------------->
    Low Chattering         High Chattering
```

**No controller is "best" at everything**:
- Fast settling often --> Higher chattering
- Low chattering often --> Slower settling
- Low energy often --> Longer settling

**Choosing a Controller**:

Ask yourself:
1. Is speed critical? --> Hybrid
2. Is smoothness critical? --> STA
3. Is energy limited? --> Adaptive
4. Is simplicity needed? --> Classical

---

### Self-Assessment: Phase 3.3

**Quiz**:

1. Which controller has the lowest chattering?
2. Which controller settles fastest?
3. What is the tradeoff between fast settling and low chattering?
4. When would you choose Adaptive SMC over STA?
5. Why is Hybrid often the best overall?

**Practical Exercise**:

Run all 4 controllers and create your own comparison table. Verify your results match the trends described.

**If you can complete quiz and exercise**: ✅ Move to Phase 3.4
**If controllers won't run**: ⚠️ Check controller names (case-sensitive)
**If results seem wrong**: ⚠️ Check initial conditions are same for all runs

</details>

---

<details>
<summary>3.4 Modifying Configuration</summary>

## Phase 3.4: Modifying Configuration (4 hours)

**Goal**: Learn to edit config.yaml and understand how parameters affect performance.

### Learning Path

**Step 1: Understanding config.yaml (1.5 hours)**

**Open config.yaml** (in text editor):

```yaml
# DIP System Parameters
plant:
  cart_mass: 1.0          # kg
  pendulum1_mass: 0.1     # kg
  pendulum1_length: 0.5   # m
  pendulum2_mass: 0.1     # kg
  pendulum2_length: 0.5   # m
  gravity: 9.81           # m/s²
  friction: 0.01          # damping coefficient

# Classical SMC Gains
controllers:
  classical_smc:
    gains: [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]  # [k1, k2, k3, k4, k5, eta]
    boundary_layer: 0.1                       # Reduce chattering

  sta_smc:
    gains: [12.0, 6.0, 10.0, 4.0, 18.0]      # Different gain structure
    alpha: 0.5                                # STA parameter

# Simulation Settings
simulation:
  duration: 10.0          # seconds
  timestep: 0.01          # seconds (100 Hz)
  initial_disturbance:    # Starting condition
    theta1: 0.1           # rad
    theta2: 0.1           # rad

# PSO Optimization
pso:
  num_particles: 30
  num_iterations: 50
  bounds: [[1, 20], ...]  # Gain bounds
```

**Key Sections**:
1. **plant**: Physical parameters (masses, lengths)
2. **controllers**: Gain values for each controller
3. **simulation**: Time settings, initial conditions
4. **pso**: Optimization settings

---

**Step 2: Changing Plant Parameters (1 hour)**

**Experiment 1: Heavier Pendulums**

Modify `config.yaml`:
```yaml
plant:
  pendulum1_mass: 0.2  # Double the mass (was 0.1)
  pendulum2_mass: 0.2
```

Run:
```bash
python simulate.py --ctrl classical_smc --plot
```

**Expected Result**:
- Harder to control (heavier pendulums have more inertia)
- Settling time increases
- Control effort increases

**Why?** Heavier masses require more force to accelerate.

---

**Experiment 2: Longer Pendulums**

Modify:
```yaml
plant:
  pendulum1_length: 0.75  # 50% longer (was 0.5)
  pendulum2_length: 0.75
```

Run again.

**Expected Result**:
- Even harder to control (longer = more unstable)
- Large overshoot possible
- May not stabilize with default gains

**Why?** Longer pendulums fall faster, require faster response.

---

**Step 3: Changing Controller Gains (1.5 hours)**

**Experiment 3: Increase Gains (More Aggressive)**

Modify:
```yaml
controllers:
  classical_smc:
    gains: [20.0, 10.0, 16.0, 6.0, 30.0, 4.0]  # Double all gains
```

Run:
```bash
python simulate.py --ctrl classical_smc --plot
```

**Expected Result**:
- Faster settling time
- Higher chattering
- More aggressive control

**Why?** Higher gains --> Stronger control response --> Faster but noisier.

---

**Experiment 4: Decrease Gains (More Conservative)**

Modify:
```yaml
controllers:
  classical_smc:
    gains: [5.0, 2.5, 4.0, 1.5, 7.5, 1.0]  # Half all gains
```

Run again.

**Expected Result**:
- Slower settling (or may not stabilize)
- Lower chattering
- System may oscillate longer

**Why?** Lower gains --> Weaker control response --> Slower, smoother.

---

**Step 4: Changing Simulation Settings (1 hour)**

**Experiment 5: Larger Initial Disturbance**

Modify:
```yaml
simulation:
  initial_disturbance:
    theta1: 0.3  # Larger disturbance (was 0.1)
    theta2: 0.3
```

Run:
```bash
python simulate.py --ctrl classical_smc --plot
```

**Expected Result**:
- Harder initial condition
- Longer settling time
- May reveal controller limitations

**Why?** Larger disturbances require more control effort.

---

**Experiment 6: Change Simulation Duration**

Modify:
```yaml
simulation:
  duration: 15.0  # Longer simulation (was 10.0)
```

**Use Case**: Verify system stays stable after settling.

---

**IMPORTANT: Reset config.yaml**

After experiments, restore default values:
```bash
git checkout config.yaml  # If using git
# Or manually restore original values
```

---

### Self-Assessment: Phase 3.4

**Quiz**:

1. What happens when you double pendulum masses?
2. What happens when you double controller gains?
3. Which parameter controls simulation length?
4. How do you increase initial disturbance?
5. Why is it important to reset config.yaml after experiments?

**Practical Exercise**:

1. Modify one plant parameter, run simulation
2. Observe how performance changes
3. Explain why (in your own words)

**If you can complete quiz and exercise**: ✅ Move to Phase 3.5
**If YAML syntax errors**: ⚠️ Check indentation (use spaces, not tabs)
**If simulation fails after changes**: ⚠️ Reset config.yaml and try again

</details>

---

<details>
<summary>3.5 Troubleshooting Common Issues</summary>

## Phase 3.5: Troubleshooting Common Issues (2 hours)

**Goal**: Fix common errors independently.

### Common Errors & Solutions

**Error 1: ModuleNotFoundError**

```
ModuleNotFoundError: No module named 'numpy'
```

**Cause**: Virtual environment not activated or packages not installed

**Solution**:
```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Reinstall packages
pip install -r requirements.txt
```

---

**Error 2: YAML Syntax Error**

```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Cause**: Incorrect indentation or syntax in config.yaml

**Solution**:
- Use spaces, NOT tabs (YAML requirement)
- Check colons have space after: `key: value` not `key:value`
- Use online YAML validator: https://www.yamllint.com/

---

**Error 3: Simulation Diverges (NaN values)**

```
RuntimeError: Simulation diverged (NaN values detected)
```

**Cause**: Gains too low, system unstable, or extreme initial conditions

**Solution**:
1. Reset config.yaml to defaults
2. Reduce initial disturbance
3. Increase controller gains slightly
4. Check physical parameters are reasonable

---

**Error 4: Plots Don't Show**

**Cause**: Matplotlib backend issue (headless environment) or plots closing immediately

**Solution**:
```bash
# Save instead of displaying
python simulate.py --ctrl classical_smc --save results.json

# Or change matplotlib backend
export MPLBACKEND=TkAgg  # Linux/macOS
set MPLBACKEND=TkAgg     # Windows
```

---

**Error 5: Controller Not Found**

```
ValueError: Unknown controller type: 'classical'
```

**Cause**: Wrong controller name (case-sensitive)

**Solution**:
- Use exact name: `classical_smc` not `classical`
- Run `python simulate.py --help` to see valid names

---

### Getting Help

**Resources**:

1. **Documentation**: `docs/guides/getting-started.md`
2. **GitHub Discussions**: Ask questions, search existing issues
3. **Stack Overflow**: Tag with `[python] [control-systems]`
4. **Re-read This Roadmap**: Phase 1-2 cover fundamentals

**Before Asking for Help**:
1. Read error message carefully
2. Check you're in correct directory
3. Verify virtual environment activated
4. Try resetting config.yaml
5. Search for error message online

---

### Self-Assessment: Phase 3.5

**Checklist**:

- ✅ I know how to activate virtual environment
- ✅ I can fix YAML syntax errors
- ✅ I know what to do if simulation diverges
- ✅ I can troubleshoot import errors
- ✅ I know where to get help

**If all checked**: 🎉 **Phase 3 COMPLETE!**
**If stuck on errors**: ⚠️ Review solutions above, ask for help

</details>

---


## Learning Resources

```{grid} 1 2 3
:gutter: 2

```{grid-item-card} YouTube: Simulation & Analysis
:link: https://www.youtube.com/results?search_query=python+simulation+control+systems
:link-type: url
:text-align: center

Watch tutorials on running simulations and analyzing results
[View -->]

```

```{grid-item-card} Article: Controller Comparison Methods
:link: https://www.mathworks.com/help/control/
:link-type: url
:text-align: center

Read about comparing controller performance metrics
[Read -->]

```

```{grid-item-card} Interactive Quiz
:link: #self-assessment-phase-35
:link-type: url
:text-align: center

Test your hands-on simulation skills from Phase 3
[Take Quiz -->]

```

```{grid-item-card} 📖 Sliding Mode Control Overview
:link: https://www.researchgate.net/publication/36218899_A_QUICK_INTRODUCTION_TO_SLIDING_MODE_CONTROL_AND_ITS_APPLICATIONS
:link-type: url
:class-card: resource-card resource-article
:shadow: md
:text-align: center

Quick introduction to SMC theory covering first and second-order SMC with chattering solutions. Free access.
📊 *Estimated Time:* 60 min | 🎯 *Level:* Intermediate
[Read -->]

```

```{grid-item-card} 🎥 Lyapunov Stability Theory - Stanford
:link: https://stanford.edu/class/ee363/lectures/lyap.pdf
:link-type: url
:class-card: resource-card resource-video
:shadow: md
:text-align: center

Stanford University lecture notes on basic Lyapunov theory. Mathematical foundation for control stability.
📊 *Estimated Time:* 45 min | 🎯 *Level:* Technical
[View -->]

```

```{grid-item-card} 📚 SciPy Control Systems Documentation
:link: https://docs.scipy.org/doc/scipy/reference/integrate.html
:link-type: url
:class-card: resource-card resource-docs
:shadow: md
:text-align: center

Official SciPy documentation for ODE solvers and integration. Complete API reference with examples.
📊 *Estimated Time:* Reference | 🎯 *Level:* Reference
[Browse -->]

```

```{grid-item-card} 🧪 Pendulum Simulation Demo
:link: https://www.myphysicslab.com/pendulum/inverted-double-pendulum-en.html
:link-type: url
:class-card: resource-card resource-interactive
:shadow: md
:text-align: center

Interactive double inverted pendulum simulation. Adjust parameters, drag pendulum, visualize dynamics.
📊 *Estimated Time:* 30 min | 🎯 *Level:* Hands-on
[Try It -->]

```
```

---
**CONGRATULATIONS!** 🎉

You've completed **Phase 3: Hands-On Learning** (~25 hours)!

You now can:
✅ Run simulations with different controllers
✅ Interpret result plots and performance metrics
✅ Compare controller performance
✅ Modify configuration files
✅ Troubleshoot common errors

**Skills Gained**:
- Command-line proficiency
- Data interpretation
- Parameter tuning intuition
- Independent problem-solving

**Next**: [Phase 4: Advancing Skills](phase-4-advancing-skills.md) - deeper Python, reading code, understanding math

---

**Navigation:**
- <--[Phase 2: Core Concepts](phase-2-core-concepts.md)
- **Next**: [Phase 4: Advancing Skills](phase-4-advancing-skills.md) -->
- [<--Back to Beginner Roadmap](../beginner-roadmap.md)

---

## Navigation

[<--Phase 2: Core Concepts](phase-2-core-concepts.md) | [Back to Roadmap](../beginner-roadmap.md) | [Phase 4: Advancing Skills -->](phase-4-advancing-skills.md)
