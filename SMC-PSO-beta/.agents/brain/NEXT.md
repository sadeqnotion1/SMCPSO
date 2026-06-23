# NEXT — the handoff card

> Exactly one task. Finish it, wrap up, then pick the next from ROADMAP.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## ➡️ The one next task (Migration Phase 2)
**Port `src/plant/` from `SMC-PSO/` into `SMC-PSO-beta/`.**
The DIP dynamics models have no internal project dependencies, so they come first
after config (dependency-first order). Bring over: the shared base/interface, the
full nonlinear model, the simplified model, and the low-rank variant.

## Start the next chat with this
> "Read .agents/AGENTS.md and the brain, then port src/plant/ (base interface + full
> nonlinear + simplified + low-rank dynamics) from SMC-PSO into SMC-PSO-beta. Minimal,
> anchored, additive. Show me the file plan before writing code."

## What to paste / give me at the start
1. `SMC-PSO/src/plant/` tree (base interfaces + model files).
2. The physics block of `SMC-PSO-beta/config.yaml` (masses, lengths, gravity, friction).

## Decisions I need from you for this task
- Confirm the package import root for beta (`src/` flat vs. `src/<pkg>/`).
- Keep all three model fidelities (full / simplified / low-rank), or start with one?

## Definition of done for this task
- `src/plant/` present in beta with base + the chosen model(s).
- A model instantiates from `config.yaml` physics params and returns state derivatives
  for a known input without import/runtime errors.
- Verified locally; STATE/SESSION_LOG/graph updated on wrap-up.

> After plant: Phase 3 = `src/utils/`, then Phase 4 = controllers base + `src/simulation/`,
> then Phase 5 = the SMC controllers + factory. (See ROADMAP.)
