# CORRECTION to inertia_validation_proof.md  (W1-4 / W1-5)

Additive companion to the existing proof. States the physics error, the correct bound, and
the resolution actually applied in config + validator.

## The error in the original proof
It claims the genuine COM inertias (~2.65e-3, ~1.15e-3 kg.m^2) "must be scaled up" to
0.0081 / 0.0034 to satisfy `I >= m*d^2`. That bound is wrong for a COM inertia.

Parallel-Axis Theorem:  `I_pivot = I_com + m*d^2`.
So `m*d^2` is a lower bound for the PIVOT inertia, NOT for `I_com`. There is no requirement
that `I_com >= m*d^2`. A COM inertia of 2.65e-3 is fully physical; inflating it to 0.0081
had no physical basis (0.0081 is only ~1.25% above `m*d^2 = 0.008` -- a tell that the number
was reverse-engineered to clear a mis-stated validator bound).

## Correct, grounded values (applied)
The links are modeled as uniform thin rods, so the COM inertia is:
```
I_com = (1/12) * m * L^2
pend1: (1/12)*0.2*0.4^2  = 0.0026667  -> config 0.00265
pend2: (1/12)*0.15*0.3^2 = 0.0011250  -> config 0.00115
```
These match the configured values and the do-mpc DIP benchmark (J = (1/12) m L^2). They feed
`M22 = m1*Lc1^2 + m2*L1^2 + I1` and `M33 = m2*Lc2^2 + I2` correctly (I = I_com there).

## Validator fix (applied -- see APPLY.md step 4)
`validate_inertia_consistency` must bound the COM inertia, not the pivot inertia:
```
# WRONG: min_inertia = mass * com_distance**2     # pivot bound applied to I_com
# RIGHT:
if inertia <= 0: raise ConfigurationError(... 'COM inertia must be positive')
max_inertia = mass * length**2                     # end-rod upper sanity bound
if inertia > max_inertia: raise ConfigurationError(... 'COM inertia above physical max')
```

## Why this does not reopen the dynamics fix
The structure invariants (M symmetric PD, (Mdot-2C) skew-symmetry, energy conservation) hold
for ANY positive inertia. So the corrected M/C/G remain valid; this defect was provenance +
a bad validator bound, now resolved with a real, citable justification.
