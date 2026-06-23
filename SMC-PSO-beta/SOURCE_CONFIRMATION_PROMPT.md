# Comprehensive source-confirmation prompt (paste to your CLI AI)

Use this AFTER applying this delivery. It drives your `pdf-fetcher` to fetch real PDFs and
then confirm every reference. ASCII markers only. Windows: use `python`, not `python3`.

---

## PROMPT (copy from here)

```
You are the references-authenticity verifier for SMC-PSO-beta. Follow my Delivery Standard.
Goal: independently CONFIRM or REJECT every reference in references/config.bib and
references/controllers.bib, using real fetched PDFs -- never from memory, never by guessing.
Do NOT mark any milestone done. Do NOT fabricate a citation to make a check pass.

BACKUP FIRST:
  zip -r "../SMC-PSO-beta-backup-$(date +%Y%m%d-%H%M%S).zip" . -x "*.git/*" -x "*__pycache__/*"
  (Windows PowerShell: Compress-Archive -Path * -DestinationPath "..\SMC-PSO-beta-backup.zip")

LOAD THE SKILL: read .agents/skills/paper-context-resolver/SKILL.md and
.agents/skills/ai-research-reproduction/SKILL.md and follow their checklists.

STEP 1 -- automated pass:
  cd pdf-fetcher
  python verify_references.py --manifest references_manifest.json --out reference_verification
  Read reference_verification.md. It checks, per DOI: Crossref resolves, title/year match,
  single-vs-double pendulum, required keywords, parameter vocabulary (via legal Unpaywall PDF).

STEP 2 -- fetch the actual PDFs for the DIP parameter sources and read them:
  python cli.py --doi "10.1016/j.automatica.2006.07.023" --out downloads/Graichen2007.pdf
  python cli.py --doi "10.1109/CCA.2001.973983"          --out downloads/Zhong2001.pdf
  python cli.py --query "Bogdanov Optimal Control Double Inverted Pendulum on a Cart"
  python cli.py --doi "10.1109/CDC.2008.4739356"         --out downloads/Moreno2008.pdf
  python cli.py --doi "10.1371/journal.pcbi.1003285"     --out downloads/Sandve2013.pdf
  # Negative controls (expect failure / single-IP):
  python cli.py --doi "10.11591/ijece.v4i2.5694"         --out downloads/Prasad2014_SUSPECT.pdf
  python cli.py --doi "10.1109/AMS.2012.21"              --out downloads/Prasad2012_single.pdf

STEP 3 -- for EACH downloaded PDF, open it and confirm ALL of:
  (a) Title, author list, year, venue/journal, volume/issue/pages match the .bib entry EXACTLY.
  (b) System type: is it a DOUBLE inverted pendulum ON A CART? (Not single, not rotary/Furuta,
      not a free double pendulum.) Quote the sentence that proves it.
  (c) Physical parameters: does it give explicit cart mass m0, link masses m1/m2, lengths l1/l2,
      COM distances Lc1/Lc2, and link moments of inertia I1/I2? Copy the parameter table/values.
  (d) Model convention: absolute joint angles vs relative; and whether M(q), C(q,qdot), G(q)
      are derived. Confirm the structure matches src/plant/core/physics_matrices.py
      (M22 = m1*Lc1^2 + m2*L1^2 + I1, Christoffel C, G from potential energy).
  (e) Inertia convention: COM inertia (I_com) vs pivot inertia (I_pivot). Confirm our values
      I1=0.00265, I2=0.00115 equal uniform-rod I_com=(1/12) m L^2 for our m,L (show the arithmetic).

STEP 4 -- decide per reference: PASS / REVIEW / FAIL.
  - If a DOI does not resolve, or resolves to a DIFFERENT paper, or the paper is single-IP being
    used as a DIP parameter source: mark FAIL and REMOVE/REPLACE it in config.bib.
  - If you remove a parameter source, find a genuine DIP-on-cart replacement, fetch its PDF,
    confirm (a)-(e), and only then add it. If none can be confirmed, state the parameters are
    study-specific uniform-rod values (cite the uniform-rod derivation) -- do not invent a source.
  - Fix any dangling \cite{...} keys so proofs reference keys that exist in the .bib files.

STEP 5 -- report (do NOT close milestones):
  - Write the per-reference verdict table + quoted evidence to
    .agents/brain/audits/references_authenticity.md.
  - Append dated entries to .agents/brain/AUDIT_LEDGER.md ([OK]/[P1]/[P2] per finding).
  - Update references/README.md so its claims match the .bib files.
  - Per Delivery Standard 5.5: only update brain STATE/NEXT if a task is VERIFIABLY done; otherwise
    report what is still open and ask. Commit + push ONLY verified results with a clear message.
  - Hand back: what changed, file list, exact edits, run+verify steps, and anything unconfirmed.
```

---

## Optional: confirm sources WITHOUT relying on Sci-Hub
`verify_references.py` uses only Crossref + Unpaywall (legal open access). For paywalled PDFs
that Unpaywall cannot serve, prefer the publisher landing page or your institutional access
rather than mirror scraping. The tool will mark those `MANUAL` / metadata-only rather than fail.
