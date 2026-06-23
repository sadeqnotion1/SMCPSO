# Multi-Layer Presentation Organization

This directory organizes the same project story at four levels of depth.
Use `L4_research_defense` as the technical source of truth, then derive
`L3_technical_deep_dive`, `L2_foundations`, and `L1_overview`.

## Levels

1. `L1_overview`
   Audience: non-technical or mixed audience
   Goal: project story, value, key outcomes
2. `L2_foundations`
   Audience: learners and new contributors
   Goal: core concepts and system basics
3. `L3_technical_deep_dive`
   Audience: technical team and engineering reviewers
   Goal: architecture, implementation, and evaluation details
4. `L4_research_defense`
   Audience: thesis committee and research conference reviewers
   Goal: full technical rigor, methods, and evidence

## Current Snapshot (2026-02-24)

- `L1_overview`: 10 files, mostly starter templates
- `L2_foundations`: 10 files, mostly starter templates
- `L3_technical_deep_dive`: 10 files, mostly starter templates
- `L4_research_defense`: 70 files, primary content layer

This means the repo is already organized as an intentional funnel:
detail concentrates in L4, then gets distilled for lower-depth audiences.

## Standard Subfolders Per Level

- `slides/`: deck sources, modular sections, and build scripts
- `speaker_notes/`: script variants, timing notes, and Q&A prep
- `figures/`: diagrams, plots, and visual assets
- `code_snippets/`: short code examples used in teaching or defense
- `handouts/`: one-page summaries and appendix packets
- `references/`: level-specific citations and reading lists

## Expanded Organization Guide

For a detailed contract (naming, folder depth, ownership, and promotion flow),
see:

- `ORGANIZATION.md`
- `LEVEL_MAPPING.md`

## Suggested Use

1. Build and validate complete content in `L4_research_defense`.
2. Derive `L3_technical_deep_dive` by pruning proofs and dense appendices.
3. Derive `L2_foundations` by simplifying language and examples.
4. Derive `L1_overview` by keeping only motivation, contributions, and outcomes.
