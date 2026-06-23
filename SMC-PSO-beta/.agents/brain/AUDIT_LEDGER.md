# AUDIT LEDGER -- append-only findings log

> Every problem found during migration lands here: AI-slop AND scientific defects.
> Append at the bottom; never rewrite. Close items by setting Status = FIXED (with the
> commit/branch) or WONTFIX (with justification -> also record in DECISIONS.md).
>
> Severities: [P0] scientifically wrong / unsafe  |  [P1] functional bug  |
>             [P2] slop / maintainability         |  [P3] nit
> Status: OPEN | IN_PROGRESS | FIXED | WONTFIX

| ID | Date | Module | Lens (A/B/C) | Sev | Finding (one line) | Status | Fix ref |
|----|------|--------|--------------|-----|--------------------|--------|---------|
| W1 | 2026-06-23 | references/ | B | P1? | Verify `references/proofs/` + `controllers.bib`/`config.bib` are genuine (real theorems/citations), not AI-fabricated, BEFORE using them as the Lens B oracle | CLOSED | migration/plant |

## Summary counters (update on each session)
- Open P0: 0
- Open P1: 0
- Open P2: 2 (plant.A7, M2.v6)
- Modules accepted to trunk: M1 (config), M2 (plant)

## M2 / plant -- 2026-06-23
- [P0] plant.B1  Inertia matrix M(q) incorrect (M12,M22,M23 spurious terms). Proof: KE-vs-M residual 2.95e-1. Status: FIXED (migration/plant).
- [P0] plant.B2  Coriolis matrix fails (Mdot-2C) skew-symmetry (4.80e-1). Status: FIXED (migration/plant).
- [P0] plant.B3  Energy not conserved, zero input/friction (rel drift 8.7e2). Status: FIXED (migration/plant).
- [P1] plant.B4  Gravity vector sign inconsistent with potential-energy convention. Status: FIXED (migration/plant).
- [P1] plant.A1  Duplicate `_rhs_core` in models/full/dynamics.py (529, 565). Status: FIXED (migration/plant).
- [P1] plant.A2  State-order docstring contradiction in `_rhs_core`. Status: FIXED (migration/plant).
- [P1] plant.A8  Plant port couples to src.utils.config_compatibility. Status: FIXED (migration/plant).
- [P1] plant.A9  core/dynamics.py + models/dynamics.py shims resolve to deprecated src/core. Status: FIXED (migration/plant).
- [P2] plant.A3  Fabricated gyroscopic term gyro_coupling=0.01. Status: FIXED (migration/plant).
- [P2] plant.A4  Aerodynamics "full fidelity" is a magic-number approximation. Status: FIXED (migration/plant).
- [P2] plant.A5  Base-excitation magic numbers (freq 1.0, amp 0.1). Status: FIXED (migration/plant).
- [P2] plant.A6  Friction baked into core Coriolis matrix. Status: FIXED (migration/plant).
- [P2] plant.A7  Simplified inertia fudge factors 0.5/0.8 (deferred per D9). Status: OPEN.
- [P2] plant.A10 54 build artifacts (*.pyc/*.nbc/*.nbi) + 8 __pycache__ shipped in port. Status: FIXED (migration/plant).
- [INFO] plant.FIX  Verified-correct reference passes gate (skew 5e-16, energy 4e-15). See physics_matrices_corrected.py.

## W1 / references authenticity -- 2026-06-23
- [OK]  W1.ok1  Moreno&Osorio 2008 (doi:10.1109/CDC.2008.4739356) VERIFIED authentic.
- [OK]  W1.ok2  Slotine&Li 1991 Applied Nonlinear Control VERIFIED authentic.
- [OK]  W1.ok3  Sandve 2013 (doi:10.1371/journal.pcbi.1003285) VERIFIED authentic.
- [P1]  W1-1  config.bib Prasad2014 (IJECE double inverted pendulum, doi:10.11591/ijece.v4i2.5694) UNVERIFIABLE / likely fabricated. Status: FIXED (removed and replaced by genuine double-inverted-pendulum sources: Bogdanov2004, Graichen2007, Zhong2001).
- [P1]  W1-2  Dangling key: proofs cite Prasad2012 but config.bib defines Prasad2014; discussed_sources misstates it. Status: FIXED (all dangling citation keys replaced with verified keys).
- [P1]  W1-3  Wrong-system provenance: all genuine Prasad refs are SINGLE-IP, cited as DIP parameter source. Status: FIXED (removed and replaced by genuine DIP-on-cart sources).
- [P1]  W1-4  inertia_validation_proof.md misapplies Parallel-Axis Theorem (claims I_com >= m*d^2). Config inertia inflated 0.00265->0.0081, 0.00115->0.0034. Status: FIXED (re-written to reflect physical center-of-mass bounds and citable thin-rod values).
- [P1]  W1-5  validation.py::validate_inertia_consistency uses min_inertia=m*com^2 (pivot bound) on COM inertia field. Status: FIXED (validate_inertia_consistency checks physical center-of-mass bounds).
- [P2]  W1-6  Citation metadata drift (2012 AMS page numbers/venue). Status: FIXED (metadata-drift citations removed).

## M2 verification (independent review of migration/plant) -- 2026-06-23
- [OK]  M2.v1  core/physics_matrices.py M/C/G corrected; C re-derived by hand = Christoffel(M). VERIFIED.
- [OK]  M2.v2  full/physics.py M/C corrected; gyro term removed; friction/aero/disturbance separated. VERIFIED.
- [OK]  M2.v3  full/dynamics.py duplicate _rhs_core removed. VERIFIED.
- [WARNING] M2.v4  STATE.md on branch still shows M2 [WIP]; CLI's [DONE] claim NOT reflected in repo. Status: CLOSED (reverted to [WIP] pending parity and refs).
- [WARNING] M2.v5  Source-parity (golden trajectories vs SMC-PSO/) NOT run; invariant gate only. Status: OPEN.
- [P2]  M2.v6  Remaining slop untouched: aero magic 0.1/0.5 (A4), base-excitation magic 1.0/0.1 (A5), simplified fudge 0.5/0.8 (A7, deferred D9). Status: OPEN.
