# Episode Traceability Map

This map links canonical authoring sources (`slides/` and `speaker/`) to
episode-number packaging in `episodes/`.

## Why This Exists

- `slides/`, `speaker/`, and `layers/` stay canonical for authoring.
- `episodes/` is the delivery/package index by episode ID.
- This file keeps numbering traceable without forcing all sources into episode
  folders.

## Main Track (`E001`-`E116`)

- Part I (`slides/sections/part1_foundations/*`) -> `E001-E020`
- Part II (`slides/sections/part2_infrastructure/*`) -> `E021-E044`
- Part III (`slides/sections/part3_advanced/*`) -> `E045-E068`
- Part IV (`slides/sections/part4_professional/*`) -> `E069-E096`
- Appendix (`slides/sections/appendix/*`) -> `E097-E116`

Speaker scripts follow the same ranges:

- `speaker/speaker_scripts/part1_foundations.tex` -> `E001-E020`
- `speaker/speaker_scripts/part2_infrastructure.tex` -> `E021-E044`
- `speaker/speaker_scripts/part3_advanced.tex` -> `E045-E068`
- `speaker/speaker_scripts/part4_professional.tex` -> `E069-E096`
- `speaker/speaker_scripts/appendix.tex` -> `E097-E116`

## Specialized Track (`EP001`-`EP012`)

`podcasts/episodes/specialized_advisor_report_complete/tex/01_*.tex` through
`12_*.tex` map to `EP001` through `EP012`.

## Machine-Readable Version

Use `EPISODE_TRACEABILITY_MAP.csv` for tooling and scripts.

## Note

The production-plan naming for Part IV episode blocks and current slide
filenames are not perfectly aligned (for example Section 23/24 naming). The
numeric episode ranges are preserved as the source of truth.
