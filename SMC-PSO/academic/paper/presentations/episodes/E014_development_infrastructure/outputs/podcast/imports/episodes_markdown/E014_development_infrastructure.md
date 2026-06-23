# E014: Development Tools and Workflow

**Hosts**: Dr. Sarah Chen (Control Systems) & Alex Rivera (Software Engineering)

---

## Opening Hook

**Alex**: Question: How long does it take to go from "I have an idea for a new controller" to "I have validated results published in a paper"?

**Sarah**: Without good tooling? 6-12 months of:
- Manually running simulations
- Copy-pasting results into Excel
- Writing LaTeX tables by hand
- Debugging cryptic errors
- Losing track of which experiment was which

**Alex**: With GOOD development infrastructure? **3-4 weeks**!

**Sarah**: The difference? Automation BUYS you time:

**The Magic Button**: One command runs a complete benchmark. Push it. Eight minutes later you get CSV time-series data, JSON statistical summaries, publication-ready PDF figures, and auto-generated LaTeX tables. The manual alternative? Two days of copying, pasting, and formatting.

**Alex**: This episode covers the development infrastructure that makes research FAST:
- **CLI tools**: `simulate.py`, benchmark scripts, analysis utilities
- **Automation**: One-command workflows for reproducible experiments
- **Testing pyramid**: 668 tests ensuring code quality
- **Documentation system**: 985 files with navigation
- **Version control**: Git workflow and recovery tools

**Sarah**: Let's build a development environment that does the heavy lifting FOR you!

---

## Introduction: Development Velocity Matters

**Sarah**: Research is iterative. You need to test ideas FAST:

**Typical Research Iteration**:
```
1. Hypothesis: "Increasing λ1 will reduce overshoot"
2. Implement change (5 minutes)
3. Run experiments (??? - THIS IS THE BOTTLENECK)
4. Analyze results (???)
5. Generate figures for paper (???)
6. Repeat for next hypothesis
```

**Without tooling**: Step 3-5 take **hours to days**
**With tooling**: Step 3-5 take **minutes**

**Alex**: Good tooling BUYS you time. Let's measure the return on investment:

| Task | Manual Approach | Automated Approach | Speedup |
|------|----------------|-------------------|---------|
| Run 1 simulation | 30 sec (GUI clicks) | 2 sec (`python simulate.py`) | 15× |
| Compare 4 controllers | 5 min (run + plot each) | 10 sec (batch script) | 30× |
| PSO optimization | 4 hours (wait) | 5 min (vectorized) | 48× |
| Generate paper figure | 1 hour (Excel→export→edit) | 30 sec (auto script) | 120× |
| Find bug in code | 2 hours (print debugging) | 5 min (pytest pinpoints) | 24× |

**Sarah**: Over a 3-month research project, good tooling BUYS you **200-300 hours**. That's seven weeks of your life back!

### The Development Stack

**Alex**: Our infrastructure has 5 pillars:

**1. Command-Line Interface (CLI)**
- `simulate.py`: Primary simulation driver
- Benchmark scripts: Automated experiments
- Analysis tools: Data processing, plotting

**2. Testing Infrastructure**
- 668 tests (unit, integration, system, UI)
- 100% pass rate, continuous validation

**3. Documentation System**
- 985 files, auto-generated navigation
- Tutorials, API docs, theory guides

**4. Version Control & Recovery**
- Git workflow, checkpoint system
- 30-second project recovery after token limits

**5. Automation Scripts**
- One-command workflows for MT-5, MT-8, LT-7
- Auto-generate LaTeX tables, figures, reports

**Sarah**: Let's explore each pillar!

---

## Pillar 1: Command-Line Interface (CLI)

**Alex**: The CLI is your primary interface to the simulation engine. Let's master `simulate.py`:

### Basic Usage

**Simplest simulation**:
```bash
python simulate.py
# Uses config.yaml defaults:
# - Controller: classical_smc
# - Duration: 10 seconds
# - No plotting
```

**With controller selection**:
```bash
python simulate.py --ctrl sta_smc
python simulate.py --ctrl adaptive_smc
python simulate.py --ctrl hybrid_adaptive_sta_smc
```

**With visualization**:
```bash
python simulate.py --ctrl classical_smc --plot
# Opens matplotlib window with time-series plots
```

**Custom duration**:
```bash
python simulate.py --duration 20 --plot
# Simulate for 20 seconds instead of default 10s
```

### Advanced Features

**PSO optimization**:
```bash
python simulate.py --ctrl classical_smc --run-pso --save gains_classical.json
# Runs PSO optimization (~5 minutes)
# Saves optimized gains to JSON file
```

**Load saved gains**:
```bash
python simulate.py --load gains_classical.json --plot
# Uses optimized gains from PSO
```

**HIL mode**:
```bash
python simulate.py --run-hil --duration 10
# Starts plant server for hardware-in-the-loop testing
```

**Custom config**:
```bash
python simulate.py --config my_custom_config.yaml --plot
# Override default config.yaml
```

### Combining Options

**Sarah**: You can chain options for complex workflows:

```bash
# Optimize gains, save, test, and plot in one command
python simulate.py \
    --ctrl adaptive_smc \
    --run-pso \
    --save gains_adaptive.json \
    --plot

# Then test on multiple scenarios
python simulate.py \
    --load gains_adaptive.json \
    --config scenarios/high_mass.yaml \
    --plot
```

---

## Pillar 2: Automation Scripts

**Alex**: For research, you run 100s of simulations. Automation scripts make this ONE command:

### MT-5 Comprehensive Benchmark

**The Magic Button for Research**:

One script. One command. It runs 7 controllers across 12 scenarios with 50 random seeds—that's 4,200 simulations. It generates CSV files with raw time-series data, computes statistical summaries with confidence intervals, creates publication-ready PDF figures, and generates LaTeX tables for your paper. Total time? Eight minutes. A week's work compressed into the time it takes to make coffee.

**Output structure**:
```
MT5_comprehensive_benchmark/
├── raw_data/
│   ├── classical_smc_nominal_seed42.csv
│   ├── sta_smc_nominal_seed42.csv
│   └── ... (4,200 CSV files)
├── summaries/
│   └── statistical_summary.json
├── figures/
│   ├── figure1_overshoot_comparison.pdf
│   ├── figure2_settling_time.pdf
│   └── figure3_control_effort.pdf
└── latex/
    └── results_table.tex
```

**Sarah**: This is the Magic Button in action. Manual approach: two days. Automated: eight minutes. You just bought yourself 15 hours and 52 minutes.

### MT-8 Disturbance Rejection

**Purpose**: Test robustness to external forces—impulse kicks, step changes, sinusoidal waves.

One command tests 3 controllers against 3 disturbance types with 30 random seeds. That's 270 simulations validating robustness, with disturbance rejection plots generated automatically. Time: three minutes.

### PSO Batch Optimization

**Purpose**: Optimize all 7 controllers and validate consistency.

One command runs PSO ten times per controller with different random seeds. It saves the best gains from each run and compares consistency across seeds—critical for MT-7 validation. Total time: 45 minutes. The manual alternative? Four days of babysitting optimization runs.

**Alex**: These are your Magic Buttons. They automate the entire experimental pipeline and buy you weeks of time!

---

## Pillar 3: Testing Infrastructure

**Sarah**: 668 tests ensure nothing breaks. Let's tour the test pyramid:

### Level 1: Unit Tests (Fast, Isolated)

**Purpose**: Test individual functions/classes

**Example** (`tests/test_controllers/test_classical_smc.py`):
```python
def test_classical_smc_sliding_surface():
    """Verify sliding surface computation."""
    controller = ClassicalSMC(gains=[10, 5, 8, 3, 15, 2])

    # Test state: θ₁=0.1, θ̇₁=0.2, θ₂=0.05, θ̇₂=0.1, x=0, ẋ=0
    state = np.array([0.1, 0.2, 0.05, 0.1, 0.0, 0.0])

    # Manually compute expected sliding surfaces
    lambda1, lambda2 = 10, 5
    s1_expected = 0.2 + lambda1 * 0.1  # θ̇₁ + λ₁·θ₁
    s2_expected = 0.1 + lambda2 * 0.05  # θ̇₂ + λ₂·θ₂

    # Get actual from controller (private method exposed for testing)
    s = controller._compute_sliding_surfaces(state)

    assert np.isclose(s[0], s1_expected), f"s1 mismatch: {s[0]} != {s1_expected}"
    assert np.isclose(s[1], s2_expected), f"s2 mismatch: {s[1]} != {s2_expected}"
```

**Run unit tests**:
```bash
pytest tests/test_controllers/ -v
# 234 tests in ~1 second
```

### Level 2: Integration Tests (Component Interaction)

**Purpose**: Test how modules work together

**Example** (`tests/test_integration/test_factory.py`):
```python
def test_factory_creates_valid_controller():
    """Verify factory pattern loads config and creates working controller."""
    config = load_config("config.yaml")

    # Factory creates controller from config
    controller = create_controller(config.controller.type, config.controller.params)

    # Test it's usable
    state = np.random.rand(6)
    u = controller.compute_control(state)

    assert isinstance(u, float), "Control must be scalar"
    assert -100 < u < 100, "Control must be reasonable magnitude"
```

**Run integration tests**:
```bash
pytest tests/test_integration/ -v
# 125 tests in ~5 seconds
```

### Level 3: System Tests (End-to-End)

**Purpose**: Test complete workflows

**Example** (`tests/test_system/test_pso_optimization.py`):
```python
def test_pso_optimization_improves_cost():
    """Verify PSO reduces cost function."""
    # Default gains (hand-tuned)
    controller_default = ClassicalSMC(gains=[10, 5, 8, 3, 15, 2])
    cost_default = run_simulation_and_compute_cost(controller_default)

    # Run PSO
    tuner = PSOTuner(controller_type="classical_smc", config=config)
    best_gains, cost_optimized = tuner.optimize(max_iter=20, n_particles=15)

    # Verify improvement
    improvement = (cost_default - cost_optimized) / cost_default
    assert improvement > 0.03, f"PSO should improve cost by >3%, got {improvement:.2%}"
```

**Run system tests**:
```bash
pytest tests/test_system/ -v
# 98 tests in ~2 minutes
```

### Level 4: UI Tests (Browser Automation)

**Purpose**: Test Streamlit web interface

**Example** (`tests/test_ui/test_streamlit_basic.py`):
```python
from playwright.sync_api import Page

def test_streamlit_loads_without_error(page: Page):
    """Verify Streamlit app starts successfully."""
    page.goto("http://localhost:8501")

    # Check title renders
    assert "DIP-SMC-PSO" in page.title()

    # Check controller dropdown exists
    dropdown = page.locator("select#controller-select")
    assert dropdown.is_visible()
```

**Run UI tests**:
```bash
# Start Streamlit server first
streamlit run streamlit_app.py &

# Run Playwright tests
pytest tests/test_ui/ --headed
# 17 tests in ~30 seconds
```

**Alex**: Total test coverage: **668 tests, 100% passing!**

---

## Pillar 4: Documentation System

**Sarah**: 985 files is overwhelming - how do you navigate? The documentation system!

### Structure

```
docs/
├── index.md                    # Main entry point (Sphinx)
├── guides/
│   ├── INDEX.md                # Guide directory
│   ├── getting-started.md      # Tutorial 01
│   ├── controller-tuning.md    # Tutorial 02
│   └── research-workflow.md    # Tutorial 05
├── theory/
│   ├── sliding-mode-control.md
│   ├── pso-optimization.md
│   └── lyapunov-stability.md
├── api/
│   ├── controllers.md          # Auto-generated from docstrings
│   ├── plant.md
│   └── utils.md
└── NAVIGATION.md               # Master navigation hub (11 systems)
```

**Navigation Tools**:

1. **NAVIGATION.md**: Master hub connecting all 11 navigation systems
   - "I Want To..." quick navigation (6 intent categories)
   - Persona-based entry points (4 user types)
   - Complete category index directory (43 indexes)

2. **Search functionality**: Full-text search across all 985 files

3. **Cross-references**: Every doc links to related content

**Alex**: Example navigation path:
```
User wants to tune a controller:
  → NAVIGATION.md ("I want to tune...")
  → guides/controller-tuning.md (Tutorial 02)
  → theory/pso-optimization.md (deep dive)
  → api/pso_optimizer.md (code reference)
```

### Building Documentation

```bash
# Build Sphinx HTML docs
sphinx-build -M html docs docs/_build

# Serve locally
python -m http.server 9000 --directory docs/_build/html

# Open in browser: http://localhost:9000
```

**Sarah**: Documentation build system auto-rebuilds on file changes (see `.ai_workspace/guides/documentation_build_system.md`)!

---

## Pillar 5: Version Control & Recovery

**Alex**: Git workflow + checkpoint system for resilience:

### Git Workflow

**Daily workflow**:
```bash
# Check status
git status

# Create feature branch
git checkout -b feature/new-controller

# Make changes, commit
git add src/controllers/new_controller.py
git commit -m "feat(controllers): Add new PID+SMC hybrid controller

- Implements PID outer loop + SMC inner loop
- Passes unit tests (15/15)
- Benchmarked: 12% better settling time vs Classical SMC

[AI] Generated with Claude Code"

# Push to remote
git push origin feature/new-controller

# Create PR (using gh CLI)
gh pr create --title "Add PID+SMC Hybrid Controller" --body "$(cat <<EOF
## Summary
New hybrid controller combining PID outer loop with SMC inner loop

## Test Plan
- [x] Unit tests (15/15 passing)
- [x] Integration test with full dynamics
- [x] Benchmark vs Classical SMC (12% improvement)

🤖 Generated with Claude Code
EOF
)"
```

### Recovery System (30-Second Project Recovery)

**Problem**: Token limit hit, or returning after 3 months - how to resume?

**Solution**: `/recover` command

```bash
# One command recovery
bash .ai_workspace/tools/recovery/recover_project.sh

# Output:
# ══════════════════════════════════════════════════
# Project Recovery
# ══════════════════════════════════════════════════
# Phase: Maintenance/Publication
# Completed: Phase 3 (UI), Phase 4 (Production), Phase 5 (Research)
# Current focus: Paper submission (LT-7)
#
# Recent commits:
#   927826c feat(podcasts): Expand E006-E007
#   da97a6c feat(podcasts): Expand E004-E005
#
# Roadmap progress: 50/50 tasks (100%)
# Agent checkpoints: 3 incomplete tasks detected
#
# Next actions:
#   1. Review .ai_workspace/planning/CURRENT_STATUS.md
#   2. Check academic/paper/experiments/ for latest results
#   3. Resume from last checkpoint: LT-7 final submission
# ══════════════════════════════════════════════════
```

**Sarah**: This script analyzes:
- Git history
- Project state files
- Roadmap progress
- Agent checkpoints

And gives you context to resume immediately!

---

## Real-World Impact: Development Velocity

**Alex**: Let's measure the ROI of good tooling:

### Case Study: MT-5 Comprehensive Benchmark

**Without tooling (manual)**:
```
Day 1: Run ClassicalSMC on 12 scenarios manually
       - Open GUI, set parameters, run, save CSV
       - 12 scenarios × 5 min each = 60 min

Day 2: Run STASMC, AdaptiveSMC (same process)
       - 2 controllers × 60 min = 120 min

Days 3-5: Run remaining 4 controllers
          - 240 min total

Day 6: Copy data to Excel, create plots
       - 4 hours

Day 7: Generate LaTeX tables by hand
       - 3 hours

Total: 7 days, ~20 hours of manual work
```

**With tooling (automated)**:

Push the Magic Button. Wait 8 minutes. Done.

**Speedup**: **150×** (20 hours → 8 minutes). You just bought yourself 19 hours and 52 minutes.

### Annual Productivity Gains

**Alex**: For a typical research project with 10 major experiments:

| Task | Manual (hrs) | Automated (min) | Saved per experiment |
|------|--------------|----------------|---------------------|
| Benchmark | 20 | 8 | 19.9 hrs |
| PSO optimization | 4 | 5 | 3.9 hrs |
| Generate figures | 4 | 0.5 | 3.99 hrs |
| LaTeX tables | 3 | 0.1 | 2.99 hrs |
| **Total** | **31 hrs** | **13.6 min** | **30.87 hrs** |

**Annual savings** (10 experiments): **~310 hours** = **7.75 work weeks**!

**Sarah**: You just BOUGHT yourself two months by investing one week in tooling. That's the power of the Magic Button!

---

## Educational Infrastructure Context

**Alex**: The development tools also power the educational system:

## Educational System Overview

**Mission:** Democratize access to advanced control theory

        44 episodes covering Phases 1-4, ~40 hours audio content \\
        Convert written materials to commute-friendly learning format

---

## Beginner Roadmap: Path 0

**Target:** Zero prerequisites (no coding/control theory background)

    **Duration:** 125-150 hours over 4-6 months

    **Phase Breakdown:**
    
        - **Computing Fundamentals (30 hrs)**
        
            - Terminal/command line basics
            - Git version control
            - Package management (pip, conda)

        - **Python Programming (40 hrs)**
        
            - Variables, functions, classes
            - NumPy/SciPy fundamentals
            - Matplotlib visualization

        - **Physics \& Mathematics (35 hrs)**
        
            - Classical mechanics (pendulum dynamics)
            - Linear algebra (matrices, eigenvalues)
            - Differential equations (ODEs)

        - **Control Theory (20 hrs)**
        
            - PID control introduction
            - State-space representation
            - Lyapunov stability basics

---

## Tutorial System Architecture

**Progressive Learning Structure:**

    \begin{tabular}{lll}
        \toprule
        **Tutorial** & **Topic** & **Duration** \\
        \midrule
        Tutorial 01 & Getting Started & 1-2 hrs \\
        & CLI basics, first simulation & \\
        \midrule
        Tutorial 02 & Controller Comparison & 3-4 hrs \\
        & All 7 controllers, PSO tuning & \\
        \midrule
        Tutorial 03 & Advanced Features & 4-5 hrs \\
        & Batch simulation, monitoring & \\
        \midrule
        Tutorial 04 & Web Interface & 2-3 hrs \\
        & Streamlit dashboard, real-time plots & \\
        \midrule
        Tutorial 05 & Research Workflow & 5-8 hrs \\
        & Reproducible experiments, paper figures & \\
        \bottomrule
    \end{tabular}

        Every tutorial includes runnable code, expected outputs, troubleshooting tips

---

## NotebookLM Podcast Series

**Innovation:** Convert documentation to podcast-style audio

    **Series Statistics:**
    
        - **44 episodes** covering Phases 1-4
        - **~40 hours** total audio content
        - **125 hours** equivalent learning material
        - TTS optimization for commute/exercise listening

    **Episode Structure:**
    
        - **Phase 1:** Foundations (Python, Git, Physics) -- 12 episodes
        - **Phase 2:** Control Theory (SMC, PSO) -- 10 episodes
        - **Phase 3:** Implementation (Controllers, Simulation) -- 14 episodes
        - **Phase 4:** Advanced Topics (HIL, Monitoring, Research) -- 8 episodes

        Episode templates, TTS optimization checklist, phase-specific examples \\
        \textit{See:} `.ai\_workspace/guides/notebooklm\_guide.md`

---

## Learning Path Integration

**Seamless Progression Across Paths:**

    [Visual diagram - see PDF]

---

## Resources

- **Repository:** https://github.com/theSadeQ/dip-smc-pso.git
- **Documentation:** `docs/` directory
- **Getting Started:** `docs/guides/getting-started.md`

---

*Educational podcast episode generated from comprehensive presentation materials*
