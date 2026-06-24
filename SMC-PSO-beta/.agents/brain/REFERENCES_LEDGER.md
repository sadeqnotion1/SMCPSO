# REFERENCES LEDGER -- thesis bibliography harvest (cross-cutting workstream W-REFS)

> Purpose: a SINGLE running bibliography of every reference the ported code cites or
> relies on, captured as we audit each module. Complements ledger W1 (which only *verified*
> the repo's existing `references/*.bib`); this ledger *accumulates* every reference for the
> thesis and tracks its verification status.
>
> Append-only per module. ASCII only. Repo: SMC-PSO-beta/
>
> STATUS LEGEND
> - VERIFIED      : web-verified to be a real publication that supports the claim (DOI/ISBN below).
> - VERIFIED-STD  : a real published standard (IEEE/ISO etc.).
> - PRINCIPLE     : a named textbook physical/mathematical law relied on in a proof (not a paper).
> - CANDIDATE     : standard method used in code with NO in-code citation; canonical reference
>                   SUGGESTED for the thesis -- confirm before citing.
> - REMOVED-FAKE  : found fabricated/unverifiable and deleted from the port. DO NOT re-add.
>
> SCAN STATUS: FULL back-fill complete 2026-06-24 for M1 (config), M2 (plant + references/),
> and M3 slices 1-5. One open gap (uncatalogued PDFs) recorded at the bottom.

## How to use this for the thesis
- VERIFIED / VERIFIED-STD rows are safe to cite directly (bibliographic details below).
- CANDIDATE rows: the code uses the method but does not cite it; add the suggested citation if you
  want the thesis to attribute it.
- PRINCIPLE rows: name the law in-text; cite any standard mechanics/thermodynamics text.
- REMOVED-FAKE rows are recorded so they are never reintroduced.

---

## R-index

| Ref ID | Citation | Cited in (module : location) | Supports / used for | Status |
|--------|----------|------------------------------|---------------------|--------|
| REF-001 | F. Steimann and P. Mayer, "Patterns of interface-based programming," Journal of Object Technology, vol. 4, no. 5, pp. 75-94, July 2005. doi:10.5381/jot.2005.4.5.a1 | M3 s1 : utils/control/types/control_outputs.py (docstring) | Interfaces-as-contracts rationale for NamedTuple return types | VERIFIED (2026-06-24; DOI confirmed; matches U2 vol/issue fix) |
| REF-002 | G. H. Golub and C. F. Van Loan, "Matrix Computations," 4th ed., Johns Hopkins Univ. Press, 2013. ISBN 978-1-4214-0794-4 | M3 s4 : utils/numerical_stability/safe_operations.py (docstring) | Conditioning / numerical-stability rationale | VERIFIED (2026-06-24; JHU Press 4th ed) |
| REF-003 | N. J. Higham, "Accuracy and Stability of Numerical Algorithms," 2nd ed., SIAM, 2002. ISBN 0-89871-521-0 | M3 s4 : utils/numerical_stability/safe_operations.py (docstring) | Floating-point error / stability rationale | VERIFIED (2026-06-24; SIAM 2nd ed) |
| REF-004 | IEEE Std 754, IEEE Standard for Floating-Point Arithmetic. | M3 s4 : utils/numerical_stability/safe_operations.py (docstring) | Double-precision epsilon thresholds (~2.22e-16) | VERIFIED-STD |
| REF-005 | G. K. Sandve et al., "Ten Simple Rules for Reproducible Computational Research," PLOS Comput. Biol., 9(10):e1003285, 2013. doi:10.1371/journal.pcbi.1003285 | M3 s3 : utils/testing/reproducibility/seed.py (prose); references/config.bib (Sandve2013) | Reproducibility / seed-recording rationale | VERIFIED (W1.ok3) |
| REF-006 | B. L. Welch, "The generalization of 'Student's' problem when several different population variances are involved," Biometrika, 34(1-2):28-35, 1947. doi:10.1093/biomet/34.1-2.28 | M3 s5 : utils/analysis/statistics.py : welch_t_test | Welch unequal-variance t-test | VERIFIED (2026-06-24; canonical source -- method uncited in code) |
| REF-007 | J. Cohen, "Statistical Power Analysis for the Behavioral Sciences," 2nd ed., Lawrence Erlbaum, 1988. ISBN 0-8058-0283-5 | M3 s5 : statistics.py : welch_t_test (Cohen's d), sample_size_calculation | Effect size (Cohen's d), power / sample size | VERIFIED (2026-06-24; canonical source -- method uncited in code) |
| REF-008 | B. Efron and R. J. Tibshirani, "An Introduction to the Bootstrap," Chapman & Hall, 1993. | M3 s5 : statistics.py : bootstrap_confidence_interval | Percentile bootstrap CI | CANDIDATE (method uncited in code) |
| REF-009 | D. C. Montgomery, "Design and Analysis of Experiments" (one-way ANOVA / F-test). | M3 s5 : statistics.py : one_way_anova | F-statistic, eta-squared effect size | CANDIDATE (method uncited in code) |
| REF-010 | J.-J. E. Slotine and W. Li, "Applied Nonlinear Control," Prentice Hall, 1991. ISBN 0130408905 | M3 s2 : utils/control/primitives/saturation.py (boundary-layer concept, uncited); references/config.bib (Slotine1991); proofs (sec 5) | Boundary-layer sat(s/phi) chattering reduction | VERIFIED (W1; authentic) |
| REF-011 | A. Bogdanov, "Optimal Control of a Double Inverted Pendulum on a Cart," OGI/OHSU Tech. Report CSE-04-006, 2004. | references/config.bib (Bogdanov2004); proofs/inertia_validation_proof.md sec 3 | DIP-on-cart M(q)/C/G structure + benchmark params | VERIFIED (W1, 2026-06-24) |
| REF-012 | K. Graichen, M. Treuer, M. Zeitz, "Swing-up of the double pendulum on a cart...," Automatica, 43(1):63-71, 2007. doi:10.1016/j.automatica.2006.07.023 | references/config.bib (Graichen2007); proofs/inertia sec 3 | Experimentally-validated DIP-on-cart | VERIFIED (W1, 2026-06-24) |
| REF-013 | W. Zhong and H. Rock, "Energy and passivity based control of the double inverted pendulum on a cart," IEEE CCA, 2001. doi:10.1109/CCA.2001.973983 | references/config.bib (Zhong2001) | Passivity/energy-shaping; (Mdot-2C) skew-symmetry | VERIFIED (W1, 2026-06-24) |
| REF-014 | J. A. Moreno and M. Osorio, "A Lyapunov approach to second-order sliding mode controllers and observers," 47th IEEE CDC, pp. 2856-2861, 2008. doi:10.1109/CDC.2008.4739356 | references/controllers.bib (Moreno2008); proofs/stability sec 4 (STA K1>K2>0) | Super-twisting strict Lyapunov stability | VERIFIED (W1.ok1) -- governs M5 STA gains |

## Physical principles relied on in proofs (name in-text; cite a standard text)

| Ref ID | Principle | Relied on in | Status |
|--------|-----------|--------------|--------|
| REF-015 | Parallel Axis Theorem (Steiner): I_pivot = I_com + m d^2; uniform-rod I_com = (1/12) m L^2 | proofs/inertia_validation_proof.md (inertia bounds) | PRINCIPLE |
| REF-016 | Second Law of Thermodynamics / Clausius inequality (entropy generation >= 0) | proofs/stability_validation_proof.md sec 2 (viscous friction b >= 0) | PRINCIPLE |
| REF-017 | do-mpc double-inverted-pendulum benchmark (software), J = (1/12) m L^2 formulation | references/config.bib provenance note | CANDIDATE (software benchmark) |

## Removed / fabricated (DO NOT re-add)

| Ref ID | Citation | Where found | Status |
|--------|----------|-------------|--------|
| REF-X01 | Prasad-Tyagi-Gupta, IJECE doi:10.11591/ijece.v4i2.5694 ("double inverted pendulum") | was in config.bib / proofs | REMOVED-FAKE (unverifiable; genuine Prasad work is SINGLE-IP, IJAC doi:10.1007/s11633-014-0818-1) |
| REF-X02 | Hallucinated citation glyph artifacts in seed.py docstrings | M3 s3 : seed.py | REMOVED-FAKE (S3-A3) |

## Scan coverage (2026-06-24)

- **M1 config**: `config.yaml` header carries only INTERNAL provenance (Issue #2 / Issue #18 / MT-8
  reports, docs/*.md, artifacts/*.json) -- no academic citations. Nothing to add to the bibliography.
- **M2 plant**: academic citations are centralized in `references/` (not inline in `src/plant/**`).
  All `.bib` keys cited by the proofs resolve (Bogdanov2004, Graichen2007, Moreno2008, Slotine1991) --
  **no dangling citation keys**. Proofs additionally invoke the named principles REF-015/REF-016.
- **M3 slices 1-5**: all in-code citations captured (REF-001..010).
- **W1 cross-check**: the 6 catalogued `.bib` refs are all web-verified genuine; the fabricated
  Prasad ref stays removed.

## Open gap (NOT a fabricated-ref issue -- a cataloguing gap)

- **GAP-1**: `references/undiscussed_sources/` holds migrated PDFs (articles/ books/ manuals/
  proceedings/ manually_downloaded/) that are NOT keyed in any `.bib` and not yet catalogued here.
  Directory listing is not available from this tooling, so enumerate locally
  (`E:\University\SMC-PSO-beta\references\undiscussed_sources\`) and add any thesis-relevant PDF as a
  ledger row (with status) when its module is reached. Most are expected to belong to M5 (controllers)
  / M6 (PSO / swarm proceedings) and can be catalogued then.

## Process change (so we stop missing these)
Add a reference-harvest step to the per-module audit loop (alongside Lens A/B/C):
> **Lens D -- references:** for every ported file, extract each citation/standard method/principle it
> relies on, append a row here with location + status. Web-verify where cheap; mark CANDIDATE methods
> for author decision. Never let a fabricated citation survive (W1 lesson).
