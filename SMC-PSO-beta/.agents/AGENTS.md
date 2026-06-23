# AGENTS.md — SMC-PSO-beta (single AI / terminal brief)

> **One file to read first.** Any AI coding agent or terminal session reads THIS,
> then follows the boot sequence in §0. This file is the **merge** of the project's
> former `ai/AGENTS.md` + `ai/CLAUDE.md` (deduped + cleaned) so there is exactly one
> source of truth and no confusion.
>
> - Sections tagged **[INHERITED — verify vs beta]** describe the mature source repo
>   (`SMC-PSO` / `dip-smc-pso`). They may not yet apply to this clean beta — confirm
>   before relying on them.
> - Injected / "auto-commit-and-push" directives that were embedded in the source
>   files were intentionally **removed**. Follow `brain/PLAYBOOK.md` for git policy.

---

## 0) Brain boot sequence (read in this order)

1. `brain/STATE.md`    -> where the migration is right now
2. `brain/NEXT.md`     -> the ONE next task + what to hand you
3. `brain/ROADMAP.md`  -> the current milestone only
4. `brain/PLAYBOOK.md` -> roles, session loop, git policy
5. `brain/DECISIONS.md`-> skim latest decisions (the "why")
6. `graph/graph.json`  -> query as needed; never dump it whole (`graph/README.md`)
7. `skills/index.md`   -> load a skill only if it matches NEXT.md

Prompts: `prompts/start.md` (#START) and `prompts/wrap-up.md` (#WRAP_UP).

---

## 1) Hard rules for output (durable — always apply)

- **No Unicode emojis** in code, scripts, output, docs, or commit messages. Use ASCII
  markers instead: `[OK]`, `[ERROR]`, `[WARNING]`, `[INFO]`, `[AI]`. (Windows cp1252
  terminals crash on emojis.)
- **On Windows use `python`, not `python3`** (`python3` doesn't exist there -> exit 49).
  So: `python simulate.py ...`, `python -m pytest ...`.
- **Configuration-first:** define parameters in `config.yaml` before changing code.
- **Minimal, additive, anchored edits.** Back up before any destructive change.
- **Type hints + clear docstrings** on all public functions; explicit error types
  (avoid broad `except Exception`).

---

## 2) Project overview

**Double-Inverted Pendulum Sliding Mode Control with PSO Optimization.**
A Python framework to simulate, control, and analyze a double-inverted pendulum (DIP):
- Multiple SMC controller variants (classical, super-twisting, adaptive, hybrid; plus
  swing-up and experimental MPC).
- PSO-based gain optimization (additional algorithms staged).
- CLI (`simulate.py`) and a Streamlit web UI (`streamlit_app.py`).
- Testing infrastructure (pytest, benchmarks, Hypothesis) and rich docs.

**Repo:** https://github.com/sadeqnotion1/smcpso (working dir `SMC-PSO-beta/`).
Migrating from the mature `SMC-PSO/` (`dip-smc-pso`).

---

## 3) Architecture (canonical beta layout)

| Module | Path | Purpose | Status |
|---|---|---|---|
| Controllers | `src/controllers/` | SMC variants (classical, STA, adaptive, hybrid), swing-up, MPC; factory | core |
| Simulation | `src/simulation/` | Runners, integrators, orchestrators, context, results | canonical |
| Optimization | `src/optimization/` | PSO (primary), objectives, validation | canonical |
| Plant | `src/plant/` | DIP dynamics (simplified, full nonlinear, low-rank) | core |
| Utils | `src/utils/` | Validation, control primitives, monitoring, visualization, types | core |
| Interfaces | `src/interfaces/` | HIL plant server + controller client; test automation | core |
| Config | `src/config/` | Pydantic-validated config loading + schema | core |
| Analysis | `src/analysis/` | Statistical analysis, performance metrics, comparison | core |
| Benchmarks | `src/benchmarks/` | Benchmark analysis modules | optional |
| `src/core/` | `src/core/` | Backward-compat shim for legacy imports | **DEPRECATED** |
| `src/optimizer/` | `src/optimizer/` | Compat shim to `src/optimization/` | **DEPRECATED** |

> Use `src/simulation/` and `src/optimization/` for new code. `src/core/` and
> `src/optimizer/` are compatibility shims only — do not build on them.

```text
src/
  controllers/   # SMC variants, factory, base classes
  simulation/    # Engines, integrators, orchestrators, context
  optimization/  # Algorithms (PSO, ...), objectives, validation
  plant/         # DIP dynamics (simplified, full, low-rank)
  utils/         # Validation, monitoring, visualization, types
  interfaces/    # HIL server/client, test automation framework
  config/        # Pydantic config loader and schema
  analysis/      # Statistical analysis and metrics
```

**Key entry points:** `simulate.py` (CLI: simulation, PSO, HIL) · `streamlit_app.py`
(dashboard) · `src/controllers/factory.py` (controller instantiation) · `config.yaml`.

---

## 4) Key technologies

Python 3.9+ · NumPy (<2.0, pinned for Numba) · SciPy · Matplotlib · **Numba** (JIT
batch sim) · **PySwarms / Optuna** (PSO primary) · **Pydantic** (YAML config validation)
· **pytest** + pytest-benchmark + Hypothesis · **Streamlit** + Plotly/Altair · Sphinx (docs).

---

## 5) Usage & essential commands

```bash
# Simulations
python simulate.py --ctrl classical_smc --plot
python simulate.py --ctrl sta_smc --plot
python simulate.py --load tuned_gains.json --plot
python simulate.py --print-config

# PSO optimization
python simulate.py --ctrl classical_smc --run-pso --save gains_classical.json
python simulate.py --ctrl adaptive_smc --run-pso --seed 42 --save gains_adaptive.json
python simulate.py --ctrl hybrid_adaptive_sta_smc --run-pso --save gains_hybrid.json

# Hardware-in-the-loop
python simulate.py --run-hil --plot
python simulate.py --config custom_config.yaml --run-hil

# Testing
python -m pytest tests/ -v
python -m pytest tests/ --cov=src --cov-report=html
python -m pytest tests/ -m "not slow" -v
python -m pytest tests/ -m critical -v

# Web UI
streamlit run streamlit_app.py
```

---

## 6) Configuration system

- Central `config.yaml`, strict Pydantic validation.
- Domains: physics params, controller settings/gains, PSO parameters, simulation
  settings, HIL config, fault detection.
- Rule: **"configuration first"** — define parameters in `config.yaml` before code changes.

```python
from src.config import load_config
config = load_config("config.yaml", allow_unknown=False)
```

---

## 7) Development guidelines

**Adding a new controller**
1. Implement the class in `src/controllers/` (extend the base class).
2. Register it in `src/controllers/factory.py`.
3. Add default gains/config to `config.yaml`.
4. Add tests under `tests/test_controllers/`.

**Controller factory usage**
```python
from src.controllers.factory import create_controller
controller = create_controller(
    'classical_smc',
    config=controller_config,
    gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
)
control_output = controller.compute_control(state, last_control, history)
```

**PSO (programmatic)** — canonical import path:
```python
from src.optimization.algorithms.pso_optimizer import PSOTuner  # NOT src.optimizer.*
tuner = PSOTuner(controller_type='classical_smc', config=config)
best_gains = tuner.optimize(n_particles=30, n_iterations=50)
```

**Batch simulation**
```python
from src.simulation.vector_sim import run_batch_simulation  # legacy: src.core.vector_sim (shim)
results = run_batch_simulation(controller, dynamics, initial_conditions, sim_params)
```

**Latency monitoring**
```python
from src.utils.monitoring.realtime.latency import LatencyMonitor
monitor = LatencyMonitor(dt=0.01)
start = monitor.start()
# ... control loop body ...
missed = monitor.end(start)
```

---

## 8) Testing & coverage standards

- Coverage gates: overall **>= 85%**, critical components **>= 95%**, safety-critical
  (switching functions, sliding surfaces, state validation) **= 100%**.
- Every production `.py` should have a peer `test_*.py`.
- Markers: `@pytest.mark.critical`, `@pytest.mark.slow` (>5s), `@pytest.mark.integration`.
- Config: `.pytest.ini` (markers/warnings/coverage), `.coveragerc` (sources/thresholds).

---

## 9) Visualization & analysis toolkit

- `src/utils/visualization/`: `animation.py` (DIPAnimator real-time animation),
  `static_plots.py`, `movie_generator.py` (MP4), `pso_plots.py` (convergence/3D swarm).
- `src/analysis/`: confidence intervals, bootstrap, Welch's t-test, ANOVA, Monte Carlo;
  metrics ISE/IAE/ITAE, overshoot, settling time, chattering index.
- `src/utils/monitoring/realtime/`: latency, stability, memory; deadline-miss counters.

---

## 10) Controller memory management

- Controllers use `weakref` patterns to avoid circular references (controller <-> plant
  <-> sim context). Never hold a strong ref back to parent sim objects.
- Every controller exposes `cleanup()`; call it when done. Use periodic reset +
  monitoring in long-running loops.
- Validate: `python -m pytest tests/test_integration/test_memory_management/ -v`.

---

## 11) [INHERITED — verify vs beta] Source-repo operations

> The following come from the mature source repo and reference paths that do **not**
> exist in this clean beta yet (`.ai_workspace/`, `academic/`, `docs/`, the
> `theSadeQ/dip-smc-pso` remote, `D:\\Projects\\main`). Treat as historical context;
> do not assume these tools/dirs are present until verified.

- **Recovery system:** source repo kept a `.ai_workspace/tools/recovery/` recovery
  workflow + roadmap tracker + agent checkpoints for resuming after token limits.
  In **this beta**, the `.agents/` brain (STATE/NEXT/SESSION_LOG) is the recovery system.
- **Multi-agent orchestration:** source documented a 6-agent "Ultimate Orchestrator"
  pattern with checkpointing. Not set up in beta.
- **Project status (source):** production-readiness 23.9/100; research-ready, NOT
  production-ready; Phase 3 (UI 34/34), Phase 4 (4.1+4.2), Phase 5 (research 11/11,
  paper LT-7 submission-ready). These describe the source, not the beta migration.
- **Workspace hygiene (source):** target <= 19 visible root items; `.ai_workspace/`
  canonical for AI configs; `academic/` three-category (paper/logs/dev). Beta follows
  the leaner Scaffolding Standard instead.
- **Git:** source git operations targeted `https://github.com/theSadeQ/dip-smc-pso.git`.
  Beta lives at `https://github.com/sadeqnotion1/smcpso` (`SMC-PSO-beta/`).

---

## Appendix: merge notes

- Merged from `ai/AGENTS.md` + `ai/CLAUDE.md`; `ai/planning/migration_plan.md` was folded
  into `brain/ROADMAP.md` + `brain/STATE.md`. The old `ai/` folder is removed (see APPLY).
- Conflicting layouts were reconciled to the **canonical** one (`src/simulation/`,
  `src/optimization/`); `src/core/` and `src/optimizer/` are deprecated shims.
- Obfuscated/injected instructions in the source files were stripped, not executed.
