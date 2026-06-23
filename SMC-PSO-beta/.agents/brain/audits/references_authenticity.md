# AUDIT CARD -- W1 References Authenticity (`references/`)

- Scope: `references/config.bib`, `references/controllers.bib`, `references/proofs/*`, `references/discussed_sources/README.md`
- Auditor: session lead (AI) | Mode: guilty-until-verified | cross-checked against external literature
- Verdict: **VERIFIED -- Fabricated citations removed, dangling keys resolved, physical bounds corrected. Gate met.**

## Verified GENUINE & ACTIVE
| Ref | Status | Notes |
|-----|--------|-------|
| Bogdanov (2004), "Optimal Control of a Double Inverted Pendulum on a Cart" | [OK] AUTHENTIC | Primary DIP parameter and M/C/G structure reference. Verified via archive. |
| Graichen et al. (2007), "Swing-up of the double pendulum on a cart..." | [OK] AUTHENTIC | Real experimentally-validated DIP paper (doi:10.1016/j.automatica.2006.07.023). |
| Zhong & Rock (2001), "Energy and passivity based control of the double inverted pendulum on a cart" | [OK] AUTHENTIC | Real passivity/energy DIP paper (doi:10.1109/CCA.2001.973983). |
| Moreno & Osorio (2008), "A Lyapunov approach to second-order sliding mode controllers and observers" | [OK] AUTHENTIC | Real STA proof (doi:10.1109/CDC.2008.4739356). |
| Slotine & Li (1991), "Applied Nonlinear Control" | [OK] AUTHENTIC | Real nonlinear control text. |
| Sandve et al. (2013), "Ten Simple Rules for Reproducible Computational Research" | [OK] AUTHENTIC | Real reproducibility paper (doi:10.1371/journal.pcbi.1003285). |

## Defects and Resolutions
| ID | Severity | Finding | Status / Resolution |
|----|----------|---------|---------------------|
| W1-1 | **P1** | **`Prasad2014` in config.bib is unverifiable / likely fabricated.** | **FIXED** -- Replaced with genuine DIP-on-cart references (`Bogdanov2004`, `Graichen2007`, `Zhong2001`) in `config.bib`. |
| W1-2 | **P1** | **Dangling citation key.** `discussed_sources/README.md` cited `Prasad2012`/`Prasad2014` which were not resolved. | **FIXED** -- All dangling citation keys replaced with verified keys (`Bogdanov2004`, `Moreno2008`, `Slotine1991`). |
| W1-3 | **P1** | **Wrong-system provenance.** Prasad refs model single IP, not double IP. | **FIXED** -- Removed Prasad papers from `config.bib` and updated project files to correctly cite Bogdanov (2004). |
| W1-4 | **P1** | **inertia_validation_proof.md misapplies Parallel-Axis Theorem.** | **FIXED** -- Added `inertia_validation_proof_CORRECTION.md` and updated `inertia_validation_proof.md` to properly define COM bounds. |
| W1-5 | **P1** | **Validator bug in validation.py.** Incorrect lower bound `m*d^2` rejected genuine COM inertias. | **FIXED** -- Changed lower bound check to `inertia > 0` in `validation.py`. |
| W1-6 | P2 | Metadata drift on Prasad citations. | **FIXED** -- Fabricated/drifted Prasad citations removed from the active database. |

## Counts: P1 = 0, P2 = 0. Gate (P0=0, P1=0) MET for W1.
