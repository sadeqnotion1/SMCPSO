# NEXT — the handoff card

> Exactly one task. Finish it, wrap up, then pick the next from ROADMAP.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## ➡️ The one next task
**Port `src/controllers/` (SMC family + factory) from `SMC-PSO/` into `SMC-PSO-beta/`.**
Bring over classical / super-twisting / adaptive / hybrid-adaptive-STA controllers
and `factory.py`, wired to read gains from beta `config.yaml`.

## Start the next chat with this
> "Read .agents/AGENTS.md and the brain, then port src/controllers/ (classical, sta,
> adaptive, hybrid + factory.py) from SMC-PSO into SMC-PSO-beta. Minimal, anchored,
> additive. Show me the file plan before writing code."

## What to paste / give me at the start
Pull these from the repo (or paste them):
1. `SMC-PSO/src/controllers/factory.py` — the controller factory contract.
2. `SMC-PSO/src/controllers/smc/*` — the four SMC implementations.
3. `SMC-PSO-beta/config.yaml` — the gain/controller config block.

## Decisions I need from you for this task
- Confirm package import root for beta (`src/` flat vs. `src/<pkg>/`).
- Any controllers from source to intentionally drop in beta (e.g. `mpc/`, `specialized/`)?

## Definition of done for this task
- All four SMC controllers + `factory.py` present under beta `src/controllers/`.
- `factory.create(...)` instantiates each controller from `config.yaml` gains.
- A smoke run (one controller, short horizon) executes without import/runtime errors.
- Verified locally; STATE/SESSION_LOG/graph updated on wrap-up.
