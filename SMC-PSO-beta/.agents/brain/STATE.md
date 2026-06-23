# STATE — where we are right now

> Single source of truth. If this disagrees with the real code, the **code wins** —
> tell me and I fix the brain. Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

**Status (one-liner):** Migrating `dip-smc-pso` from `SMC-PSO/` into the clean
`SMC-PSO-beta/` scaffold, **dependency-first** (per the folded migration plan).
Environment + config phase is done; `.agents/` brain is installed and the old `ai/`
folder has been merged into it.

## Migration phases (folded from ai/planning/migration_plan.md — dependency-first)

| Phase | Scope | Status |
|---|---|---|
| 1. Environment & config | `requirements.txt`, `setup.py`, `config.yaml`, `src/config/` | ✅ done |
| 2. Plant dynamics | `src/plant/` (base, full nonlinear, simplified, low-rank) | ⬜ next |
| 3. Utils & primitives | `src/utils/` (types, validation, logging, metrics) | ⬜ |
| 4. Controllers base + sim core | `src/controllers/base.py`, `src/simulation/` | ⬜ |
| 5. Controller implementations | classical / sta / adaptive / hybrid + `factory.py` | ⬜ |
| 6. Optimization | `src/optimization/` (PSO algorithms + objectives) | ⬜ |
| 7. Entry points | `simulate.py`, `streamlit_app.py` | ⬜ |
| 8. Verification & tests | `tests/` suite + gates | ⬜ |

> Legend: ✅ done · 🟦 in progress · ⬜ not started · ⚠️ blocked.

## Brain / tooling status
| Part | Status | Notes |
|---|---|---|
| `.agents/` brain | ✅ | This system. |
| Merge of `ai/` -> `.agents/` | ✅ | `ai/AGENTS.md` + `ai/CLAUDE.md` merged into single `AGENTS.md`; `ai/` removed. |
| Knowledge graph | 🟦 | Canonical `src/` layout (`simulation/`, `optimization/`); refine as `src/` lands. |

## Open decisions / questions waiting on you
- Keep `src/`-layout package or move to the `backend/` + entry-points shape from the
  Scaffolding Standard? (See D2.)

## Known risks / watch-items
- Source repo has a stray mojibake file (`DProjects...compile.bat`) — do **not** carry it over.
- Source docs referenced `.ai_workspace/`, `academic/`, the `theSadeQ/dip-smc-pso`
  remote — those don't exist in beta; ignore unless re-created.
- Numba-accelerated batch sim must keep numeric parity with the source after the port.
- Use canonical `src/simulation/` & `src/optimization/`; `src/core/`+`src/optimizer/` are deprecated shims.
