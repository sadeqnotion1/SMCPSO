# STATE -- where we are right now

> Single source of truth. If this disagrees with the real code, the **code wins** -- tell me
> and I fix the brain. ASCII markers only. Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

**Status (one-liner):** Migrating `dip-smc-pso` from `SMC-PSO/` into the clean `SMC-PSO-beta/`
scaffold, **dependency-first AND audit-driven**: every module is ported, audited for AI-slop
+ scientific correctness, and proven by parity/tests BEFORE it is accepted (see
`brain/MIGRATION_PLAN.md`). Config phase is done; `.agents/` brain installed; `ai/` merged in.

## Migration phases (gated -- a phase is DONE only after its Audit Card passes)

| Milestone | Scope | Status |
|-----------|-------|--------|
| M1 Environment & config | requirements / setup / config.yaml / `src/config/` | [DONE] (re-audit pins owed) |
| M2 Plant dynamics (FULL model first) | `src/plant/models/` full model + parity harness | [DONE] physical consistency verified, W1 refs resolved, parity documented |
| M3 Utils & primitives | `src/utils/` | [WIP] (Slices 1, 2, 3, 4 & 5 accepted) |
| M4 Controllers base + sim core | `src/controllers/base.py`, `src/simulation/` | [TODO] |
| M5 Controller implementations | classical / sta / adaptive / hybrid + factory | [TODO] |
| M6 Optimization | `src/optimization/` | [TODO] |
| M7 Interfaces / HIL | `src/interfaces/` (was missing from old plan) | [TODO] |
| M8 Analysis | `src/analysis/` (was missing) | [TODO] |
| M9 Entry points | `simulate.py`, `streamlit_app.py` | [TODO] |
| M10 Benchmarks (+ integration/assets) | `src/benchmarks/` (was missing) | [TODO] |
| M11 Verification suite & gates | `tests/`, coverage gates, CI | [TODO] |
| -- plant simplified/low-rank | deferred follow-up after M2 (D9) | [TODO] |

## Audit posture (why this plan changed)
- Repo was largely AI-generated -> every ported file is **"guilty until verified."**
- Two lenses on every module: (A) AI-slop/code defects, (B) scientific/math correctness.
- Gate: P0 = 0, P1 = 0, parity passes, coverage met, Audit Card filed. Findings -> `AUDIT_LEDGER.md`.
- Lens B oracle = `references/proofs/` + `references/controllers.bib` + `references/config.bib`,
  but those references are themselves audited for authenticity (ledger W1).

## Open decisions / questions waiting on you
- Confirm package import root (`src/` flat vs `src/<pkg>/`).
- (RESOLVED D9) Plant fidelity: full model first, simplified/low-rank deferred.
- (RESOLVED D10) Reference equations: use repo `references/` (proofs + bib), validate authenticity.

## Known risks / watch-items
- [RESOLVED] W1 (ledger): `references/proofs/` + `.bib` verified genuine.
- Source has duplicated logic: `src/core/` vs `src/simulation/`, `src/optimizer/` vs
  `src/optimization/`, and a nested `src/plant/core/` -- canonical wins; shims dropped.
  Do NOT port the deprecated dirs.
- Source has a stray mojibake file (`DProjects...compile.bat`) -- do NOT carry it over.
- `numpy<2.0` must stay pinned for Numba; verify in M1 re-audit.
- Numba batch path must keep numeric parity with the pure-Python path.
