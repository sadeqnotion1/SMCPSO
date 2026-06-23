# Presentations Workspace Organization

This document defines the directory contract for
`academic/paper/presentations`.

## Purpose

Keep presentation-related assets separated by output channel and lifecycle so
content can evolve without mixing source files, generated artifacts, and
derived formats.

## Top-Level Map

- `slides/`
  - Canonical LaTeX slide deck sources and modular sections.
  - Primary technical slide authoring workspace.
- `speaker/`
  - Canonical LaTeX speaker scripts tied to slide sections.
- `episodes/`
  - Episode-first hub with one folder per episode (`E###_slug`).
  - Canonical cross-channel package point for per-episode work.
- `layers/`
  - Audience-depth variants (`L1` through `L4`).
  - Use `layers/L4_research_defense` as source for derived layer versions.
- `podcasts/`
  - Episode-generation pipeline and produced episode assets.
- `beautiful_ai/`
  - Beautiful.ai-adapted slide content and guide material.
- `code_snippets/`
  - Shared executable example snippets used across channels.
- `figures/`
  - Shared visual assets referenced by decks and scripts.

## Source-of-Truth Flow

1. Author and validate technical depth in `slides/` and `speaker/`.
2. Package episode units under `episodes/` (source, assets, outputs, metadata).
3. Mirror or migrate stable technical content into `layers/L4_research_defense`.
4. Derive `L3`, `L2`, and `L1` from `L4` by simplification.
5. Derive platform outputs (`beautiful_ai/`, `podcasts/`) from stabilized episode/layer content.

## Hygiene Rules

- Do not commit LaTeX intermediate artifacts (`.aux`, `.log`, `.out`, `.toc`, `.nav`, `.snm`, and related build files).
- Keep generated outputs inside designated output folders only.
- Do not keep Windows reserved-name files (for example `nul`) in the tree.
- Use `.gitkeep` only for intentionally empty folders.

## Pre-Commit Audit

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\audit_presentation_hygiene.ps1 -FailOnFindings
```

The script reports artifact and reserved-name findings and exits with code `1`
if `-FailOnFindings` is set and issues are detected.

For cleanup:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_presentation_artifacts.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_presentation_artifacts.ps1 -Apply
powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_presentation_artifacts.ps1 -Apply -IncludeReservedNames
```

For bulk episode packaging:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\migrate_all_episodes.ps1
```

## Related Guides

- `layers/ORGANIZATION.md` for the multi-depth layer contract.
- `episodes/README.md` for episode folder contract and index usage.
- `EPISODE_TRACEABILITY_MAP.md` and `EPISODE_TRACEABILITY_MAP.csv` for
  source-to-episode traceability.
- `podcasts/README.md` for episode production workflow.
- `beautiful_ai/PRESENTATION_GUIDE.md` for platform adaptation workflow.
