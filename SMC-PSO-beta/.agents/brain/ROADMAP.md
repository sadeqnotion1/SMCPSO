# ROADMAP -- migration milestones (audit-driven)

> Dependency-first. Only the **current** milestone is active. Every milestone is gated by
> the audit in `brain/MIGRATION_PLAN.md` (port -> audit -> prove -> gate -> accept).
> A milestone is `[DONE]` only when its Audit Card passes the gate. ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## [DONE] M0 -- Scaffold + brain
- Clean beta scaffold; `.agents/` brain installed; `ai/` merged into `.agents/`.

## [DONE] M1 -- Environment & configuration (Phase 1)
- `requirements.txt`, `setup.py`, `config.yaml`, `src/config/`.
- Re-audit owed: confirm `numpy<2.0` pin (Numba), Pydantic rejects unknown keys, no secrets.

## [DONE] M2 -- Plant dynamics
- Port `src/plant/` (base + full + simplified + low-rank).
- Science gate: `M(q)` symmetric PD; energy-conservation test; equilibria/linearization;
  approximation-error bound for simplified/low-rank.
- Build the shared **parity harness** here (`scripts/parity_check.py` + golden baselines).

## [WIP] M3 -- Utils & primitives  <- ACTIVE
- `src/utils/` (Slices 1, 2 & 3 [DONE]; remaining slices [TODO]). Dedupe vs `core/`; verify metric defs.

## [TODO] M4 -- Controllers base + simulation core
- `src/controllers/base.py`, `src/simulation/`. Integrator + energy/parity on an uncontrolled
  drop test; one full end-to-end sim runs.

## [TODO] M5 -- Controller implementations  (highest scrutiny)
- classical / sta / adaptive / hybrid + `factory.py`.
- Science gate: Lyapunov/reaching per controller; STA gain conditions; adaptive boundedness;
  chattering index; actuator saturation behavior.

## [TODO] M6 -- Optimization
- `src/optimization/` (PSO + objectives + validation). Fitness penalizes instability; bounds
  respected; seed-reproducible; hold-out scenarios.

## [TODO] M7 -- Interfaces / HIL  (was MISSING from old plan)
- `src/interfaces/` (HIL server/client, test automation). Needed before entry points
  (`simulate.py --run-hil`). Audit latency monitor + safe-stop on deadline miss.

## [TODO] M8 -- Analysis  (was MISSING from old plan)
- `src/analysis/` (statistics, metrics, comparison). Stats-correctness audit (CI/t-test
  assumptions, sample size, multiple-comparison correction).

## [TODO] M9 -- Entry points
- `simulate.py`, `streamlit_app.py`. Every CLI flag / UI control maps to working code; HIL works.

## [TODO] M10 -- Benchmarks (+ decide on integration/, assets/)  (was MISSING from old plan)
- `src/benchmarks/`. Confirm benchmarks measure what they claim; pin baselines.

## [TODO] M11 -- Verification suite & gates
- Full `tests/`; wire `.pytest.ini` / `.coveragerc`; CI runs parity + property tests on push.

> Skipped on purpose (deprecated compat shims): `src/core/`, `src/optimizer/`, `src/deprecated/`.
> Full audit checklists + gate live in `brain/MIGRATION_PLAN.md`.
