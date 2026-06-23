# AUDIT CARD -- M2 Plant Dynamics (full nonlinear model)

- Module under audit: src/plant/ (focus: models/full/, core/physics_matrices.py)
- Source: SMC-PSO/  ->  Target: SMC-PSO-beta/
- Auditor: session lead (AI)  | Mode: guilty-until-verified
- Verdict: **REJECTED -- P0 defects. M2 stays [WIP].**

## Lens A -- slop / fake / dead code
| ID | Severity | Location | Finding |
|----|----------|----------|---------|
| A1 | P1 | models/full/dynamics.py:529 & :565 | `_rhs_core` DEFINED TWICE (identical body); second silently shadows first -- dead/duplicated code. |
| A2 | P1 | models/full/dynamics.py:_rhs_core docstring | State order documented as `[x, dx, theta1, dtheta1, theta2, dtheta2]` but the whole module uses `[x, theta1, theta2, x_dot, theta1_dot, theta2_dot]`. Contradictory contract. |
| A3 | P2 | models/full/physics.py:_compute_full_coriolis_matrix_numba | `gyro_coupling = 0.01` hard-coded fabricated "gyroscopic" term with no physical basis; magic number in code (config-first violation) and it corrupts the dynamics structure. |
| A4 | P2 | models/full/physics.py:_compute_aerodynamic_forces | Hard-coded `0.1`, `0.5` coupling factors + comment admits "simplified transformation - full implementation would require Jacobian matrices". Labeled "Full Fidelity" but is an approximation. |
| A5 | P2 | models/full/physics.py:_compute_disturbance_forces | Hard-coded `excitation_freq=1.0`, `excitation_amplitude=0.1` magic numbers; belong in config. |
| A6 | P2 | core/physics_matrices.py:_compute_coriolis_matrix_numba | Viscous friction (c0,c1,c2) baked INTO the Coriolis matrix (C11=c0, C22=c1-..., C33=c2). Friction is dissipative, not Coriolis; pollutes passivity/energy structure. |
| A7 | P2 | core/physics_matrices.py:SimplifiedDIPPhysicsMatrices | Fudge factors `0.5`, `0.8` in the simplified inertia matrix -- arbitrary, not a principled reduction. (Simplified deferred per D9; logged.) |
| A8 | P1 | models/full/dynamics.py | Hard dependency on `src.utils.config_compatibility` (AttributeDictionary, ensure_dict_access) -- undeclared coupling dragged into the plant port. |
| A9 | P1 | core/dynamics.py, models/dynamics.py | Compat shims `from ...core.dynamics import *` resolve to the DEPRECATED src/core (not plant). Canonical-vs-shim drift (STATE risk confirmed). |
| A10 | P2 | whole tree | 8 `__pycache__` dirs + 54 `*.pyc/*.nbc/*.nbi` build artifacts shipped in the port. Do not migrate. |

## Lens B -- science / math correctness (numerically proven)
| ID | Severity | Finding | Evidence |
|----|----------|---------|----------|
| B1 | **P0** | Inertia matrix M(q) is WRONG: spurious terms in M12, M22, M23. M12 has an extra `+ m2*Lc2*cos(theta2)`; M22 has extra `+ m2*Lc2^2 + I2 + 2*m2*L1*Lc2*cos(t1-t2)`; M23 has extra `+ m2*Lc2^2 + I2`. | TEST B: `max|KE_func - 0.5 q'.M_code.q'| = 2.95e-01` (should be ~0); textbook M matches KE to `3.55e-15`. |
| B2 | **P0** | Coriolis matrix is NOT energy-consistent (fails the passivity property (Mdot-2C) skew-symmetric) and is missing required Christoffel terms. | TEST C: `max|q'(Mdot-2C)q'| = 4.80e-01` (should be ~0). |
| B3 | **P0** | Model does not conserve energy with zero input and zero friction. | TEST D: relative energy drift `= 8.7e+02` (875x) over a 2 s release-from-rest sim. |
| B4 | P1 | Gravity sign inconsistent with the model's own potential energy. PE_func uses `m g L (1-cos theta)` (=> dU/dq = +(...)g sin) but G_code = `-(...)g sin`. G is the negative of dU/dq, so the simulated potential is inverted relative to the energy-analysis function. | derivation + TEST D drift. |
| B5 | P2 | The "gyroscopic" term (A3) has no measurable correct effect; with or without it energy drift is ~875x. Confirms it is fabricated, not physics. | TEST D both rows fail. |

## Corrected reference -- VERIFIED PASSING
A corrected model (textbook absolute-angle M, Christoffel C derived from M, G = +dU/dq)
passes the full gate: see `src/plant/core/physics_matrices_corrected.py` and `proof/verify_fix.py`.
- TEST C skew: `max|q'(Mdot-2C)q'| = 5.13e-16`  [OK]
- TEST D energy: relative drift `= 3.61e-13`  [OK]

## Counts
- P0 = 3  | P1 = 4  | P2 = 5
- Gate: P0=0 AND P1=0 required to pass. **NOT MET.**

## Required actions before M2 [DONE]
1. Replace M, C, G in `core/physics_matrices.py` / `models/full/physics.py` with the verified-correct forms (see corrected module). Move friction out of C into a separate dissipation term.
2. Delete the fabricated gyroscopic term; gate aerodynamic/disturbance models behind config and label them honestly (not "full fidelity" unless Jacobian-correct).
3. Resolve gravity-vs-PE sign convention; document whether theta=0 is up or down and apply consistently.
4. Remove duplicate `_rhs_core`; fix the state-order docstring.
5. Decouple from `src.utils.config_compatibility`; resolve the deprecated src/core shim drift.
6. Strip all build artifacts from the port; capture golden trajectories from SMC-PSO/ and wire `scripts/parity_check.py`.
7. Re-run the gate; safety-critical dynamics to 100% coverage.
