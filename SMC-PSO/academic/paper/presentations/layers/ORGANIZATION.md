# Expanded Layer Organization

This document defines a practical structure for keeping the four presentation
layers consistent while allowing each layer to serve a different audience.

## Design Principle

- `L4_research_defense` is the source layer.
- `L3_technical_deep_dive`, `L2_foundations`, and `L1_overview` are derived layers.
- Do not develop independent narratives in lower layers before L4 is stable.

## Common Folder Contract (Each Layer)

```
Lx_*/
  slides/
    sections/
  speaker_notes/
    speaker_scripts/
  figures/
  code_snippets/
  handouts/
  references/
```

Rules:
- Keep filenames numbered where sequence matters (`01_...`, `02_...`).
- Keep section names semantically stable across layers when content is related.
- Keep build helpers (`compile.sh`, `compile.bat`, split scripts) inside `slides/`.

## Current Density by Layer (2026-02-24)

- `L1_overview`: scaffold layer, templates plus README
- `L2_foundations`: scaffold layer, templates plus README
- `L3_technical_deep_dive`: scaffold layer, templates plus README
- `L4_research_defense`: active content layer (full slide sections, scripts, snippets)

Interpretation:
- The current state is healthy for a top-down derivation workflow.
- L1/L2/L3 should be filled by selecting and simplifying from L4, not rebuilt from scratch.

## Recommended Expansion Inside Existing Folders

Without changing top-level names, grow depth in-place:

- `slides/`
  - keep master deck entry points in root
  - keep modular sections under `sections/`
  - optionally add `build/` for generated PDFs and split decks
- `speaker_notes/`
  - keep high-level script entry points in root
  - keep split scripts under `speaker_scripts/`
  - optionally add `qa/` for anticipated committee questions
- `figures/`
  - optionally add `raw/`, `working/`, `final/`
- `code_snippets/`
  - keep numbered teaching path (`01_...` to `NN_...`)
  - optionally add `utils/` for shared helper code
- `handouts/`
  - keep one-page summary template in root
  - optionally add `appendix/` for per-section supplements
- `references/`
  - keep canonical bibliography (`references.bib`)
  - optionally add `reading_list.md` for non-cited background sources

## Promotion Workflow

1. Author complete technical material in `L4_research_defense`.
2. Select only implementation-critical parts for `L3_technical_deep_dive`.
3. Rewrite `L3` into concept-first explanations for `L2_foundations`.
4. Compress `L2` into outcome-first narrative for `L1_overview`.

Quality gate before promotion:
- Every promoted slide must answer a single audience-relevant question.
- Every promoted section should remove at least one layer of technical detail.
- Every lower layer should preserve terminology consistency with L4.

## Cleanup Policy

- Never commit LaTeX build artifacts (`.aux`, `.log`, `.out`, `.toc`, `.nav`, `.snm`).
- Keep placeholder `.gitkeep` files only where a directory is intentionally empty.
- Remove Windows-reserved filename artifacts (for example `nul`) from migrated trees.
