# REFERENCES LEDGER -- thesis bibliography harvest (cross-cutting workstream W-REFS)

> Purpose: a SINGLE running bibliography of every reference the ported code cites or
> relies on, captured AS WE AUDIT each module. This complements ledger W1 (which only
> *verified* the repo's existing `references/*.bib`); this ledger *accumulates* every
> reference for the thesis and tracks its verification status.
>
> Append-only per module. ASCII only. Repo: SMC-PSO-beta/
>
> STATUS LEGEND
> - VERIFIED      : web-verified to be a real publication that supports the claim (W1 method).
> - CITED/UNVERIF : appears verbatim in ported code/docstrings; authenticity NOT yet web-checked.
> - CANDIDATE     : standard method used in code with NO in-code citation; canonical reference
>                   SUGGESTED for the thesis -- needs author confirmation before citing.
> - REMOVED-FAKE  : found to be fabricated/unverifiable and deleted from the port. DO NOT re-add.
>
> SCOPE OF THIS SEED: references surfaced through audits up to M3 slice 5 (2026-06-24).
> A full exhaustive scan of M1/M2 source files is the NEXT task (see NEXT.md). Rows below
> marked (seed) are confirmed; the deep scan will add the rest and upgrade statuses.

## How to use this for the thesis
- VERIFIED rows are safe to cite directly.
- CITED/UNVERIF rows: web-check before citing (Crossref/DOI/publisher), then promote to VERIFIED.
- CANDIDATE rows: decide whether the method warrants a citation; if yes, confirm the canonical source.
- REMOVED-FAKE rows are recorded so they are never accidentally reintroduced.

---

## R-index

| Ref ID | Citation | Cited in (module : location) | Supports / used for | Status |
|--------|----------|------------------------------|---------------------|--------|
| REF-001 | F. Steimann and P. Mayer, "Patterns of interface-based programming," Journal of Object Technology, vol. 4, no. 5, pp. 75-94, July 2005. jot.fm/issues/issue_2005_07/ | M3 s1 : utils/control/types/control_outputs.py (module docstring) | Interfaces-as-contracts rationale for NamedTuple return types | CITED/UNVERIF (U2 fixed vol/issue + URL; web-check pending) |
| REF-002 | G. H. Golub and C. F. Van Loan, "Matrix Computations," 4th ed., Ch. 2. | M3 s4 : utils/numerical_stability/safe_operations.py (module docstring) | Conditioning / numerical-stability rationale for safe ops | CITED/UNVERIF (canonical text; web-check pending) |
| REF-003 | N. J. Higham, "Accuracy and Stability of Numerical Algorithms," 2nd ed. | M3 s4 : utils/numerical_stability/safe_operations.py (module docstring) | Floating-point error / stability rationale | CITED/UNVERIF (canonical text; web-check pending) |
| REF-004 | IEEE Std 754, IEEE Standard for Floating-Point Arithmetic. | M3 s4 : utils/numerical_stability/safe_operations.py (module docstring) | Double-precision epsilon thresholds (~2.22e-16) | CITED/UNVERIF (standard; web-check pending) |
| REF-005 | G. K. Sandve et al., "Ten Simple Rules for Reproducible Computational Research," PLoS Comput Biol, 2013. doi:10.1371/journal.pcbi.1003285 | M3 s3 : utils/testing/reproducibility/seed.py (prose rationale; not a formal cite) | Reproducibility / seed-recording rationale | VERIFIED (W1.ok3, 2026-06-24) |
| REF-006 | B. L. Welch, "The generalization of Student's problem when several different population variances are involved," Biometrika, 1947. | M3 s5 : utils/analysis/statistics.py : welch_t_test | Welch unequal-variance t-test | CANDIDATE (method used; no in-code cite) |
| REF-007 | J. Cohen, "Statistical Power Analysis for the Behavioral Sciences," 2nd ed., 1988. | M3 s5 : utils/analysis/statistics.py : welch_t_test (Cohen's d), sample_size_calculation | Effect size (Cohen's d), power/sample-size | CANDIDATE (method used; no in-code cite) |
| REF-008 | B. Efron and R. Tibshirani, "An Introduction to the Bootstrap," 1993. | M3 s5 : utils/analysis/statistics.py : bootstrap_confidence_interval | Percentile bootstrap CI | CANDIDATE (method used; no in-code cite) |
| REF-009 | Standard one-way ANOVA / F-test (e.g. Montgomery, "Design and Analysis of Experiments"). | M3 s5 : utils/analysis/statistics.py : one_way_anova | F-statistic, eta-squared effect size | CANDIDATE (method used; no in-code cite) |
| REF-010 | J.-J. E. Slotine and W. Li, "Applied Nonlinear Control," Prentice Hall, 1991. | M3 s2 : utils/control/primitives/saturation.py (boundary-layer concept; no in-code cite) | Boundary-layer / sat(s/phi) chattering reduction | CANDIDATE (method used; no in-code cite); also VERIFIED authentic (W1.ok2) |

## M1 / M2 verified references (from ledger W1 -- pull into full scan)

| Ref ID | Citation | Source file | Status |
|--------|----------|-------------|--------|
| REF-011 | Bogdanov, "Optimal Control of a Double Inverted Pendulum on a Cart," OGI/OHSU Tech. Report CSE-04-006, 2004. | references/config.bib (Bogdanov2004) | VERIFIED (W1, 2026-06-24) |
| REF-012 | K. Graichen et al., DIP-on-cart, Automatica, 2007. doi:10.1016/j.automatica.2006.07.023 | references/config.bib (Graichen2007) | VERIFIED (W1, 2026-06-24) |
| REF-013 | W. Zhong and H. Rock, passivity/energy-shaping DIP, IEEE CCA 2001. doi:10.1109/CCA.2001.973983 | references/config.bib (Zhong2001) | VERIFIED (W1, 2026-06-24) |
| REF-014 | J. A. Moreno and M. Osorio, super-twisting Lyapunov, IEEE CDC 2008. doi:10.1109/CDC.2008.4739356 | references/controllers.bib (Moreno2008) | VERIFIED (W1.ok1) -- relevant at M5 |

## Removed / fabricated (DO NOT re-add)

| Ref ID | Citation | Where found | Status |
|--------|----------|-------------|--------|
| REF-X01 | Prasad-Tyagi-Gupta, IJECE doi:10.11591/ijece.v4i2.5694 ("double inverted pendulum") | was in config.bib / proofs | REMOVED-FAKE (unverifiable; genuine Prasad work is SINGLE-IP, IJAC doi:10.1007/s11633-014-0818-1) |
| REF-X02 | Hallucinated citation glyph artifacts in seed.py docstrings | M3 s3 : seed.py | REMOVED-FAKE (S3-A3) |

---

## Process change (so we stop missing these)
Add a reference-harvest step to the per-module audit loop (alongside Lens A/B/C):
> **Lens D -- references:** for every ported file, extract each citation/standard method it
> relies on, append a row here with location + status. Web-verify CITED/UNVERIF rows when cheap;
> mark CANDIDATE methods for author decision. Never let a fabricated citation survive (W1 lesson).
