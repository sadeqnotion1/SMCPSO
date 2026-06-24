# W1 reference authenticity verification (closes W1 'fabricated citation' risk)

W1 (AUDIT_LEDGER, opened 2026-06-23, references/, Lens B): verify the discussed-source citations
are genuine, not fabricated. config.bib marked entries `[CONFIRM]`. Results below (web-verified):

| Citation | Claim in config.bib | External verification | Verdict |
| :--- | :--- | :--- | :--- |
| Bogdanov2004 | OGI/OHSU Tech Report CSE-04-006, "Optimal Control of a Double Inverted Pendulum on a Cart", no DOI | Confirmed by independent reference lists (MDPI Information 2022; AUTh thesis) and Semantic Scholar; report is the standard DIPC M/C/G source | GENUINE |
| Graichen2007 | Automatica 43(1):63-71, 2007, doi 10.1016/j.automatica.2006.07.023, "often miscited as 2005" | ScienceDirect + Kybernetika ref list confirm vol 43(1):63-71 and the DOI; a TU-Wien paper indeed miscites it as 2005 -> the bib's warning is itself correct | GENUINE |
| Zhong2001 | IEEE CCA 2001, arnumber/DOI 973983, "Energy and passivity based control of the DIP on a cart" | IEEE Xplore arnumber 973983 + ADS 2001cca..conf..157W confirm authors Zhong & Rock, title, venue | GENUINE |
| Moreno2008 | 47th IEEE CDC 2008, pp 2856-2861, doi 10.1109/CDC.2008.4739356 | ADS 2008cdc..conf..796M + Semantic Scholar confirm authors/title/venue/year | GENUINE |
| Slotine1991 | Applied Nonlinear Control, Prentice Hall, 1991 | Standard textbook, marked VERIFIED already | GENUINE |
| Sandve2013 | PLOS Comp Biol 9(10):e1003285, doi 10.1371/journal.pcbi.1003285 | Marked VERIFIED already | GENUINE |
| Prasad20xx (REMOVED) | Removed as DIP-parameter provenance; genuine Prasad-Tyagi-Gupta papers model a SINGLE inverted pendulum | Confirmed: Prasad/Tyagi/Gupta 2014 (IJAC, doi 10.1007/s11633-014-0818-1) and 2012 (AMS) are NONLINEAR/SINGLE inverted pendulum, not DIP-on-cart | REMOVAL JUSTIFIED |

Note on the deleted entry: the bib removed a "Prasad2014" with `doi:10.11591/ijece.v4i2.5694` (IJECE).
The authentic Prasad 2014 paper is in IJAC (doi 10.1007/s11633-014-0818-1), not IJECE, and is a single
inverted pendulum -- so the removed IJECE/DOI entry was indeed mis-stated/fabricated provenance. Correct to drop.

## Inertia provenance (W1-4 / W1-5)

The configured I1=0.00265, I2=0.00115 are the uniform thin-rod values I_com=(1/12) m L^2:
  pend1: (1/12)*0.2*0.4^2 = 0.0026667  (config 0.00265, <1% off)
  pend2: (1/12)*0.15*0.3^2 = 0.0011250 (config 0.00115, <3.3% off)
This is an honest, citable justification (uniform rods; do-mpc DIP convention), independent of any
paywalled PDF. The two large excluded PDFs (Khalil2002; Nonlinear Systems 3rd ed) are general
nonlinear-systems textbooks in undiscussed_sources/ and are NOT provenance for any plant parameter,
so their absence from the archive does not block the M2 plant audit.

## Recommendation

Flip the config.bib `[CONFIRM]` markers to verified for Bogdanov2004, Graichen2007, Zhong2001
(Moreno2008/Slotine1991/Sandve2013 already verified). W1 can be moved to RESOLVED once
verify_references.py is run against references_manifest.json in the pinned env.
