# AGENTS.md — Repo & Graph Orientation

> Entry point. Any AI session reads this FIRST, then follows the boot sequence.
> Operate strictly from these files; never improvise project state. If a brain
> file is missing or stale, fix the brain before touching code.

## Project

- **Name:** SMC-PSO-beta (clean re-scaffold of DIP-SMC-PSO)
- **Repo:** https://github.com/sadeqnotion1/smcpso  (working dir: `SMC-PSO-beta/`)
- **Source of truth being migrated from:** `SMC-PSO/` (the mature `dip-smc-pso`)
- **One-line purpose:** Simulation + PSO gain-tuning framework for sliding-mode
  control (SMC) of a double-inverted pendulum (DIP).
- **Primary stack:** Python 3 · NumPy/Numba · PSO · Streamlit · Matplotlib · pytest · YAML config

## Boot sequence (read in this order)

1. `brain/STATE.md` -> where the migration is right now
2. `brain/NEXT.md` -> the ONE next task + what to hand you
3. `brain/ROADMAP.md` -> the current milestone only
4. `brain/PLAYBOOK.md` -> roles + session loop + protocols
5. `brain/DECISIONS.md` -> skim the latest decisions (the "why")
6. `graph/graph.json` -> query as needed; never dump it in full
7. `skills/index.md` -> discover skills; load one if it matches NEXT.md

## Prompts

- `prompts/start.md` -> the #START kickoff prompt.
- `prompts/wrap-up.md` -> the #WRAP_UP closing prompt.

## Repo layout (high level)

> Keep in sync with the actual tree. Follows the Project Scaffolding Standard:
> minimal root, fewest folders, run files + README + .gitignore at root.

```text
SMC-PSO-beta/
├── src/              # package code (controllers, plant, core, optimization, ...)
├── references/       # papers, theory, citations
├── ai/               # AI/dev configs and notes
├── .agents/          # this brain
├── config.yaml       # main configuration (YAML-validated)
├── requirements.txt
├── setup.py
└── .gitignore
```

## What this project does (1 paragraph)

The system simulates a double-inverted pendulum and stabilizes it with a family
of sliding-mode controllers (classical, super-twisting, adaptive, hybrid
adaptive-STA), built through a type-safe **controller factory**. A simulation
engine (`SimulationRunner`, vectorized/Numba batch sim, safety guards) runs the
plant models (simplified, full nonlinear, low-rank). A **PSO tuner** optimizes
controller gains against multi-objective cost functions, with statistical
analysis and visualization on top. A CLI (`simulate.py`) and a Streamlit
dashboard are the entry points.

## Graph orientation

- `graph/graph.json` maps modules/files/functions and their relationships. Use it
  to answer "what calls what" / "where does X live" without reading the whole tree.
- **Query, don't dump.** Pull only the nodes/edges you need. See `graph/README.md`.
- Regenerate the visual `graph/graph.html` with `python .agents/graph/render_graph.py`.
