# Global Reference Database & Proofs Manifest

This directory serves as the centralized repository for academic references, mathematical proofs, and literature PDFs in the Double-Inverted Pendulum (DIP) controller framework.

---

## 1. Directory Structure

```
references/
  ├── config.bib              # BibTeX database for configuration references
  ├── controllers.bib         # BibTeX database for controller stability references
  │
  ├── discussed_sources/      # Reference details for sources discussed during configuration tuning
  │   └── README.md           # Manifest & retrieval links (Prasad 2012, Moreno 2008, Slotine 1991)
  │
  ├── undiscussed_sources/    # Migrated PDFs from the original repository (not discussed in this session)
  │   ├── articles/           # Technical control theory and optimization papers
  │   ├── books/              # Nonlinear control textbooks
  │   ├── manuals/            # Mechanical and electrical hardware manuals
  │   ├── proceedings/        # Swarm intelligence conference articles
  │   └── manually_downloaded/ # Additional reference documents
  │
  └── proofs/                 # Derivations and physical consistency proofs
      ├── inertia_validation_proof.md  # Parallel Axis Theorem & point-mass limits
      └── stability_validation_proof.md # Geometric, thermodynamic, and STA Lyapunov proofs
```

---

## 2. Organization Policy

*   **centralized location:** All academic literature and mathematical proofs are kept globally under `/references` at the root of the repository instead of being nested under development folders.
*   **discussed vs. undiscussed division:** 
    *   `discussed_sources/` lists the details and retrieval links of the benchmark papers that govern the exact numerical parameters configured in `config.yaml`.
    *   `undiscussed_sources/` archives all general reference PDFs copied from the stable repository's original database that did not require modification or active discussion during Phase 1.
*   **proof validation:** Every physical constraint or stability bound checked by the validation script in [validation.py](file:///E:/University/SMC-PSO-beta/src/plant/configurations/validation.py) corresponds to a formal mathematical derivation in `proofs/`.
