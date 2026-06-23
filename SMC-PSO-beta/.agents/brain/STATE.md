# STATE — where we are right now

> Single source of truth. If this disagrees with the real code, the **code wins** —
> tell me and I fix the brain. Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

**Status (one-liner):** Migrating `dip-smc-pso` from `SMC-PSO/` into the clean
`SMC-PSO-beta/` scaffold. Root config + packaging are in place; `src/` packages
are being ported module-by-module. The `.agents/` brain is now installed.

| Part | Status | Notes |
|---|---|---|
| Scaffold & packaging | 🟦 | `config.yaml`, `requirements.txt`, `setup.py`, `src/` present in beta. |
| Config (`config.yaml`) | 🟦 | Ported from source (~22 KB). Validate against beta `src/`. |
| `src/controllers/` (SMC + factory) | ⬜ | Port classical / sta / adaptive / hybrid + `factory.py`. |
| `src/plant/` (models) | ⬜ | simplified / full nonlinear / low-rank dynamics. |
| `src/core/` (sim engine) | ⬜ | `simulation_runner`, `vector_sim`, `safety_guards`. |
| `src/optimization/` (PSO) | ⬜ | algorithms (PSO), objectives (cost), results. |
| `src/analysis/` + `interfaces/` + `utils/` | ⬜ | FDI, validation, viz, HIL, utils. |
| Entry points | ⬜ | `simulate.py` CLI + Streamlit dashboard not yet in beta. |
| Tests (`tests/`) | ⬜ | pytest suite not yet ported. |
| Knowledge graph (`.agents/graph/`) | 🟦 | Seeded from source architecture; refine as beta `src/` lands. |
| Brain (`.agents/brain/`) | ✅ | This system. |

> Legend: ✅ done · 🟦 in progress · ⬜ not started · ⚠️ blocked. Mark the active task **← NEXT**.

## Open decisions / questions waiting on you
- Keep `src/`-layout package (current beta) or move to the `backend/` + entry-points
  shape from the Scaffolding Standard? (See D2.)
- Is `ai/` in beta meant to be folded into `.agents/`, or kept separate?

## Known risks / watch-items
- Source repo has a stray mojibake file (`DProjects...compile.bat`) — do **not** carry it over.
- Numba-accelerated `vector_sim` must keep numeric parity with the source after the port.
- `config.yaml` schema must stay in lockstep with ported `src/` modules.
