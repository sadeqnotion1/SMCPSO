# NEXT -- the handoff card

> Exactly one task, run with the audit loop in `brain/MIGRATION_PLAN.md`
> (port -> audit A+B -> prove C -> gate -> accept). ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## -> The one next task (M3): port + AUDIT the UTILS & PRIMITIVES module
We need to migrate and audit `src/utils/` (types, validation, logging, metrics, visualization).
This is a critical prerequisite before we start importing and building the controllers and simulation core.

## Source locations (confirmed in repo)
- Utils code: `SMC-PSO/src/utils/` -> `SMC-PSO-beta/src/utils/`
- Audit focus:
  - Deduplicate vs `core/` and other modules.
  - Verify metric definitions (ISE, IAE, ITAE) are mathematically correct before controllers and optimization modules begin utilizing them.

## Start the next chat with this
> "Read .agents/AGENTS.md + brain (esp. MIGRATION_PLAN.md). Port the utils and primitives from
> SMC-PSO/src/utils/ into SMC-PSO-beta on branch migration/utils, then AUDIT it:
> Lens A (slop) + Lens B (verify metric definitions like ISE, IAE, ITAE). Run the test suites
> and ensure full coverage on utility functions. Show me the file plan + audit findings BEFORE
> marking anything done."

## Definition of done for M3 (the gate)
- All utility functions ported to beta (`src/utils/`).
- **Lens A:** No dead code, no duplicate methods, no placeholder/fake functions.
- **Lens B:** Metric computations (ISE, IAE, ITAE, chattering index) conform to textbook definition and are robust to edge conditions (like time-step scaling).
- **Lens C:** Coverage requirements are met, particularly with safety-critical inputs and metric validators.
- Ledger updated, P0 = 0 / P1 = 0. Then mark M3 [DONE] in STATE.md.

## After M3
M4 controllers base + `src/simulation/` -> M5 controllers + factory.
