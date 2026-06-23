# AUDIT CARD -- W1 References Authenticity (`references/`)

- Scope: `references/config.bib`, `references/controllers.bib`, `references/proofs/*`, `references/discussed_sources/README.md`
- Auditor: session lead (AI) | Mode: guilty-until-verified | cross-checked against external literature
- Verdict: **PARTIAL -- 3 sources genuine, 1 citation broken/likely fabricated, 1 proof physically incorrect. P1 present.**

## Verified GENUINE
| Ref | Status | Notes |
|-----|--------|-------|
| Moreno & Osorio (2008), "A Lyapunov approach to second-order sliding mode controllers and observers", 47th IEEE CDC, pp. 2856-2861, doi:10.1109/CDC.2008.4739356 | [OK] AUTHENTIC | Real, ~1300 citations. The STA strong-Lyapunov `P`/`Q` proof in stability_validation_proof.md is consistent with this paper. |
| Slotine & Li (1991), "Applied Nonlinear Control", Prentice Hall | [OK] AUTHENTIC | Real foundational text; boundary-layer / sliding-surface usage is correctly attributed. |
| Sandve et al. (2013), "Ten Simple Rules for Reproducible Computational Research", PLOS Comp Biol, doi:10.1371/journal.pcbi.1003285 | [OK] AUTHENTIC | Real; correctly used for provenance-logging rationale. |

## Defects
| ID | Severity | Finding |
|----|----------|---------|
| W1-1 | **P1** | **`Prasad2014` in config.bib is unverifiable / likely fabricated.** Entry: "Modeling and simulation of double inverted pendulum", IJECE vol 4(2), pp 221-235, 2014, doi:10.11591/ijece.v4i2.5694. No such Prasad-Tyagi-Gupta paper could be found. The DOI/title/venue do not resolve to a real article. |
| W1-2 | **P1** | **Dangling citation key.** `inertia_validation_proof.md` and `discussed_sources/README.md` cite `Prasad2012`, but config.bib defines `Prasad2014`. The README even states `Prasad2012` is "configured in config.bib" -- it is not. `\cite{Prasad2012}` would fail to resolve. |
| W1-3 | **P1** | **Wrong-system provenance.** Every genuine Prasad-Tyagi-Gupta paper models a SINGLE inverted pendulum-cart (2012 AMS doi:10.1109/AMS.2012.21; 2014 IJAC doi:10.1007/s11633-014-0818-1; 2011 ICCSCE doi:10.1109/iccsce.2011.6190585). They are cited here as the source of DOUBLE-inverted-pendulum parameters. The DIP parameter set cannot be traced to a verified DIP reference. |
| W1-4 | **P1** | **inertia_validation_proof.md misapplies the Parallel-Axis Theorem.** It claims the genuine COM inertias (I1~2.65e-3, I2~1.15e-3) "must be scaled up" to 0.0081 / 0.0034 to satisfy `I >= m*d^2`. There is NO physics requiring `I_com >= m*d^2`; that bound is for the PIVOT inertia (`I_pivot = I_com + m*d^2`). The config values were reverse-engineered to barely clear a buggy validator (0.0081 is 1.25% above m*d^2=0.008), not taken from the reference. |
| W1-5 | **P1** | **Validator bug (validation.py::validate_inertia_consistency).** `min_inertia = mass*com**2` rejects any genuine COM inertia below `m*d^2` (it would reject the real Prasad I1=2.65e-3). If the config field is COM inertia, this lower bound is wrong; if it is pivot inertia, then `M22=m1*Lc1^2+...+I1` double-counts. The field semantics and the bound are inconsistent. |
| W1-6 | P2 | Metadata drift: 2012 AMS paper pages listed pp.138-143 but ADS bibcode `2012ams..conf...38P` indicates p.38; venue is "Asia Modelling Symposium" (not "Sixth Asia Modelling Symposium" in all records). Cosmetic but fix for citation hygiene. |

## Impact on M2
- The dynamics-structure gate (M symmetric/PD, (Mdot-2C) skew, energy) holds for ANY positive inertia, so the corrected M/C/G are unaffected.
- BUT the M2 DoD requires the model to "match references/proofs/". With W1-1..W1-5 open, the parameter provenance and one proof are not trustworthy. => M2 cannot claim reference parity until these are fixed.

## Required actions
1. Replace `Prasad2014` with a verified citation (see `config.bib.corrected`); fix the `Prasad2012`/`Prasad2014` key mismatch everywhere.
2. Either source the DIP parameters from a real double-inverted-pendulum reference, or relabel them as "adapted from single-IP literature + chosen for this study" (honest provenance).
3. Correct inertia_validation_proof.md (see CORRECTION doc) and fix the validator lower bound (see validation_inertia_fix.md). Decide whether config inertia is COM or pivot, and make code + proof + config consistent.
4. Re-run config validation after the inertia decision; record in ledger.

## Counts: P1 = 5, P2 = 1. Gate (P0=0, P1=0) NOT met for W1.
