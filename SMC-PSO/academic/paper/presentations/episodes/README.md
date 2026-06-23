# Episode-First Organization

This directory organizes presentation content by episode (`E###`) instead of by
channel (`podcasts`, `beautiful_ai`, and so on).

## Directory Contract

Each episode follows:

```
E###_slug/
  source/
    scripts/
    notes/
  assets/
    figures/
    code/
  outputs/
    podcast/
      markdown/
      pdf/
    beautiful_ai/
    pdf/
  qa/
  metadata.yaml
```

Rules:
- Keep editable source in `source/`.
- Keep generated artifacts and platform exports in `outputs/`.
- Keep review and acceptance notes in `qa/`.
- Keep one metadata file per episode (`metadata.yaml`).

## Index

Use `INDEX.csv` as the global tracking table for status, language coverage, and
last-update date.

## Full Migration Command

From `academic/paper/presentations`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\migrate_all_episodes.ps1
```

This scans `podcasts/` and `beautiful_ai/`, groups files by detected episode
ID (`E###` and `EP###`), and copies them into the episode-first hub.

## Migration Status

Full episode migration completed on `2026-02-24`:
- `E001` through `E116`
- `EP001` through `EP012`
