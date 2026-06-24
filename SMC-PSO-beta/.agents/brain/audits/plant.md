# AUDIT CARD -- M2 Plant Dynamics (full model first)

- Milestone: M2
- Scope: src/plant/{core,models/full,configurations}, references/, scripts/parity_check.py,
  tests/test_plant/test_full_dynamics_invariants.py
- Convention: q = [x, theta1, theta2]; state = [x, theta1, theta2, x_dot, theta1_dot, theta2_dot];
  ABSOLUTE angles; EOM  M(q) qdd + C(q,qd) qd + G(q) = Q;  G = +dU/dq, U = sum m g L (1 - cos theta).
- Method: PORT (pre-existing) -> AUDIT (Lens A slop, Lens B science) -> PROVE (Lens C run) -> GATE.
- Environment note (decision #5): requirements pin numpy<2.0.0 and numba<0.60.0. The audit sandbox
  had numpy 2.4.6 and NO numba; the pure-Python njit fallback let the code run. Numba-vs-Python
  parity therefore was NOT exercised here and must be run in the pinned env before ACCEPT.

## Counters

- P0 (correctness-breaking): 0 open  (5 source-level P0s were already fixed by the port; re-verified)
- P1 (must fix before accept): 0 open  (F-PLANT-1 resolved)
- P2 (watch): 2 open  (F-PLANT-2, F-PLANT-3)

## Lens A -- AI slop / placeholders / dead code / hallucinated APIs

- [RESOLVED, re-verified] A1: Fabricated gyroscopic term in models/full/physics.py
  (`gyro_coupling = 0.01; C[0,1] += ...; C[1,0] -= ...`). Magic constant, no derivation, asymmetric
  injection that destroys (Mdot-2C) skew-symmetry. The port removed it. Removal is CORRECT.
- [RESOLVED] A2: models/full/dynamics.py imported `src.utils.config_compatibility`
  (AttributeDictionary, ensure_dict_access) -- a module that does not exist in beta yet (M3 scope).
  Port replaced it with duck-typed `to_dict()` decoupling. Good additive fix; no hard dep on unbuilt code.
- [RESOLVED] A3: Dead `_rhs_core` legacy compatibility method removed from FullDIPDynamics.
- [WATCH -> F-PLANT-2, P2] A4: New core/dynamics.py `DIPParams` compat class hardcodes a parallel
  default parameter set (cart_mass=0.5, pend masses 0.2, inertia 0.006, gravity 9.81 ...) that does
  NOT match config.yaml (cart_mass=1.5, I1=0.00265, I2=0.00115). Not on the audited full-model path,
  but a latent drift hazard if any caller relies on these defaults. Flag for M4+; prefer building from config.
- [WATCH -> F-PLANT-3, P2] A5: core/dynamics.py aliases `DIPDynamics = SimplifiedDIPDynamics` and
  re-exports numba rhs/euler/rk4 helpers. Intentional per migration, but "core DIP dynamics" now points
  to the simplified model; downstream consumers (M4 controllers) must not assume full-fidelity here.

## Lens B -- science

- [RESOLVED, PROVEN] B1: Inertia matrix M(q) corrected to textbook absolute-angle form:
  M11=m0+m1+m2; M12=(m1 Lc1+m2 L1)c1; M13=m2 Lc2 c2; M22=m1 Lc1^2+m2 L1^2+I1;
  M23=m2 L1 Lc2 c(t1-t2); M33=m2 Lc2^2+I2. The SOURCE had misplaced/duplicated terms
  (M12 carried an extra +m2 Lc2 c2; M22 absorbed M23/M33 terms; M23 absorbed M33). Corrected form
  is symmetric and PD over 2200 random configurations (0 violations).
- [RESOLVED, PROVEN] B2: Friction removed from the Coriolis matrix. SOURCE put c0,c1,c2 on the C
  diagonal, which corrupts the (Mdot-2C) skew/passivity structure. Port zeros them and reintroduces
  friction as a SEPARATE dissipative term F_friction (viscous + Coulomb) in the forcing vector
  (models/full/physics.py: forcing = u - C@qd - G - F_friction - F_aero - F_disturbance). Friction is
  NOT dropped -- verified present and velocity-opposing. Skew-symmetry holds (residual ~1.8e-10).
- [RESOLVED, PROVEN] B3: Gravity vector sign/structure consistent with G=+dU/dq for the (1-cos)
  potential. Energy conserved under zero input + zero friction to relative drift ~1.6e-14 over 2 s RK4.
- [RESOLVED] B4: validation.py inertia bound fixed. SOURCE applied I_com >= m*d^2 (a PIVOT bound)
  to a COM inertia -- wrong. Port enforces I_com > 0 (hard) and I_com <= m*L^2 (sanity upper).
  Matches inertia_validation_proof_CORRECTION.md and Parallel-Axis reasoning.
- [RESOLVED -> F-PLANT-1, P1] B5: scripts/parity_check.py and tests/test_plant/test_full_dynamics_invariants.py
  hardcode I1=0.0081, I2=0.0034. These are exactly the values the project's own CORRECTION proof brands
  as "reverse-engineered" fabrications; config.yaml and the proof use I1=0.00265, I2=0.00115. The harness
  comment even claims the values come "from config.yaml [physics]" -- they do not. Invariants are
  inertia-agnostic (proven on BOTH sets), so this is not P0, but it undermines the W1 provenance fix and
  the test no longer exercises the shipped parameters. FIXED by setting both to 0.00265 / 0.00115 via the patch.

## Lens C -- proof (executed this session)

Reference module (scripts/parity_check.py gate, physics_matrices_corrected.py):
- A M symmetric-PD: 0,0 violations over 2000 samples -- OK
- B KE == 0.5 qd^T M qd: max err 0.00e+00 -- OK
- C (Mdot-2C) skew: max 8.92e-10 -- OK
- D energy conserved: rel drift 3.61e-13 -- OK

Production FullDIPDynamics (proof_full_invariants.py, run on BOTH inertia sets):
- grounded I=0.00265/0.00115: symPD (0,0); KE err 1.78e-15; skew 1.77e-10; E drift 1.57e-14; equil accel 0.0 -- GATE OK
- hardcoded I=0.0081/0.0034:  symPD (0,0); KE err 1.78e-15; skew 1.77e-10; E drift 2.02e-14; equil accel 0.0 -- GATE OK

Parity vs SOURCE golden trajectories: NOT applicable as a pass criterion. The source M/C/G is the buggy
version (B1/B2/A1); byte-parity against it would re-import the defects. Parity is therefore defined
against the verified-correct reference module, which the gate enforces. Document this in MIGRATION_PLAN.

## Gate decision

- Physics: ACCEPT (corrections verified correct and proven on production code).
- F-PLANT-1 applied successfully. Parity check script passes with "[OK] gate passed".
- References / W1: ACCEPT (citations web-verified; see references_verification.md).
