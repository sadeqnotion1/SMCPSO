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
- `src/utils/` (Slices 1-5 [DONE]: types+validation, control.primitives, testing.reproducibility,
  numerical_stability, analysis). Remaining slices [TODO]: infrastructure, monitoring,
  visualization, testing.dev_tools/fault_injection, top-level helpers. Dedupe vs `core/`;
  verify metric defs. NOTE: analysis (slice 5) adds the first SciPy dependency.

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

## [TODO] M7 -- Interfaces / HIL
- `src/interfaces/` (HIL server/client, test automation). Audit latency monitor + safe-stop.

## [TODO] M8 -- Analysis
- `src/analysis/` (statistics, metrics, comparison). Stats-correctness audit.

## [TODO] M9 -- Entry points
- `simulate.py`, `streamlit_app.py`. Every CLI flag / UI control maps to working code; HIL works.

## [TODO] M10 -- Benchmarks (+ decide on integration/, assets/)
- `src/benchmarks/`. Confirm benchmarks measure what they claim; pin baselines.

## [TODO] M11 -- Verification suite & gates
- Full `tests/`; wire `.pytest.ini` / `.coveragerc`; CI runs parity + property tests on push.

---

## Cross-cutting workstreams (run alongside milestones)

### [DONE] W1 -- References authenticity (the Lens B oracle)
- Verify `references/proofs/` + `controllers.bib`/`config.bib` are genuine, not AI-fabricated,
  before using them as the correctness oracle. Closed 2026-06-24 (config.bib web-verified).

### [WIP] W-REFS -- Reference harvest & thesis bibliography  <- NEXT PRIORITY
- Maintain `brain/REFERENCES_LEDGER.md`: a single running bibliography of EVERY reference the
  ported code cites or relies on, captured as we audit each module (thesis-facing).
- W1 only *verified* the existing .bib; W-REFS *accumulates* all references and tracks status
  (VERIFIED / CITED-UNVERIF / CANDIDATE / REMOVED-FAKE).
- **Immediate task:** back-fill all references surfaced up to M3 slice 5, then add a
  "Lens D -- references" step to the per-module audit loop so no future reference is missed.
- See NEXT.md.

> Skipped on purpose (deprecated compat shims): `src/core/`, `src/optimizer/`, `src/deprecated/`.
> Full audit checklists + gate live in `brain/MIGRATION_PLAN.md`.
