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
| W1 | 2026-06-23 | references/ | B | P1? | Verify `references/proofs/` + `controllers.bib`/`config.bib` are genuine (real theorems/citations), not AI-fabricated, BEFORE using them as the Lens B oracle | OPEN | M2 |

## Summary counters (update on each session)
- Open P0: 0
- Open P1: 0 (W1 is a pending verification, not yet confirmed a defect)
- Open P2: 1 (plant.A7 deferred)
- Modules accepted to trunk: M1 (config)

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

## W1 cross-check (references authenticity)
- Pending: validate references/proofs/, controllers.bib, config.bib are genuine before citing M(q)/C/G as "matches reference". Not yet done (read-only env).
