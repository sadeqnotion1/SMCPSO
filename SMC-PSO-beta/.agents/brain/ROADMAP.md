# ROADMAP — migration milestones

> Dependency-first order, folded from `ai/planning/migration_plan.md`. Only the
> **current** milestone is active. Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## ✅ M0 — Scaffold + brain
- Clean beta scaffold; `.agents/` brain installed; `ai/` merged into `.agents/`.

## ✅ M1 — Environment & configuration (Phase 1)
- `requirements.txt`, `setup.py`, `config.yaml`, `src/config/` (Pydantic schema + loader).

## 🟦 M2 — Plant dynamics (Phase 2) — ACTIVE
- Port `src/plant/`: base interface, full nonlinear, simplified, low-rank. ← you are here

## ⬜ M3 — Utils & math primitives (Phase 3)
- Port `src/utils/`: types, validation, control primitives, monitoring, metrics.

## ⬜ M4 — Controllers base + simulation core (Phase 4)
- Port `src/controllers/base.py` and `src/simulation/` (integrators, context, orchestrator).
- One end-to-end simulation runs in beta.

## ⬜ M5 — Controller implementations (Phase 5)
- Port classical / sta / adaptive / hybrid + `src/controllers/factory.py`.
- Controllers instantiate from `config.yaml`.

## ⬜ M6 — Optimization (Phase 6)
- Port `src/optimization/` (PSO algorithms + objectives). A PSO run yields tuned gains.

## ⬜ M7 — Entry points (Phase 7)
- Add `simulate.py` CLI and `streamlit_app.py` dashboard.

## ⬜ M8 — Verification & tests (Phase 8)
- Port `tests/` (pytest) green in beta; confirm numeric parity vs. source; refresh graph.

### Per-file migration checklist (apply to every port)
1. Copy file/dir from `SMC-PSO/` to the matching path in `SMC-PSO-beta/`.
2. Run syntax checks + linting.
3. Validate imports (adjust relative imports if package structure shifts).
4. Mark the phase item done in STATE.md.
