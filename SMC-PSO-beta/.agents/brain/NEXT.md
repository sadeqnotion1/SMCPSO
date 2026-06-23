# NEXT -- the handoff card

> Exactly one task, run with the audit loop in `brain/MIGRATION_PLAN.md`
> (port -> audit A+B -> prove C -> gate -> accept). ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## -> The one next task (M2): port + AUDIT the FULL plant model, build the parity harness
Owner decision (D9): do the **full nonlinear model first**; simplified + low-rank are deferred
to a later pass. DIP dynamics have no internal deps, so they go first, and this is where we
stand up the shared **parity harness** every later module reuses.

## Source locations (confirmed in repo)
- Plant code: `SMC-PSO/src/plant/` -> `models/` (the model classes), `core/` (shared dynamics),
  `parameters/`, `configurations/`, `__init__.py`. Port the **full model** path first.
- Reference math (the Lens B oracle): `SMC-PSO-beta/references/proofs/` (stability proofs),
  `references/controllers.bib`, `references/config.bib`, plus `references/README.md`.
  **Audit these too** -- since the repo is AI-generated, verify the proofs/citations are real
  before trusting them (see MIGRATION_PLAN section 6b).

## Start the next chat with this
> "Read .agents/AGENTS.md + brain (esp. MIGRATION_PLAN.md). Port ONLY the full nonlinear plant
> model from SMC-PSO/src/plant/ into SMC-PSO-beta on branch migration/plant, then AUDIT it:
> Lens A (slop) + Lens B (dynamics correctness, cross-checked against references/proofs +
> controllers.bib/config.bib -- and validate those references are genuine). Build
> scripts/parity_check.py with golden baselines. Show me the file plan + audit findings BEFORE
> marking anything done."

## What to give me at the start
1. The full-model files under `SMC-PSO/src/plant/models/` (+ `core/`, `parameters/`).
2. The physics block of `SMC-PSO-beta/config.yaml` (masses, lengths, gravity, friction).
3. Nothing else needed for the reference -- it is in `references/proofs/` + the `.bib` files.

## Definition of done for M2 (the gate)
- Full nonlinear plant model ported to beta (`src/plant/`), simplified/low-rank stubbed/deferred.
- **Lens A:** no fake/placeholder code, no hallucinated APIs, no dead code; findings logged.
- **Lens B:** `M(q)` symmetric positive-definite; **energy conserved** (zero input + zero
  friction) within integrator tolerance; equilibria + linearized eigenvalues correct; code
  matches the equations in `references/proofs/`; the proofs/citations themselves validated.
- **Lens C:** real tests + property tests (M PD, energy bounded); parity harness passes;
  safety-critical dynamics at 100% coverage.
- Audit Card filed (`brain/templates/AUDIT_CARD.md` -> `brain/audits/plant.md`), ledger updated,
  P0 = 0 / P1 = 0. Then mark M2 [DONE] in STATE.md and ROADMAP.md.

## After M2
M3 `src/utils/` -> M4 controllers base + `src/simulation/` -> M5 controllers + factory.
Then revisit plant simplified/low-rank models. (See ROADMAP.)
