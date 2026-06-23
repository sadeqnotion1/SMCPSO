# Educational Content Sync Script

**Location**: `scripts/sync_educational_content.py`
**Purpose**: Sync educational materials from `.project/ai/edu/` to `docs/learning/` for Sphinx documentation build

---

## Usage

### Basic Usage

```bash
# Run sync script
python scripts/sync_educational_content.py
```

**Output**:
```
[INFO] Syncing educational content: .project\ai\edu -> docs\learning
[INFO] Working directory: D:\Projects\main
[INFO] Created docs\learning
[INFO] Found 16 markdown files to sync
[OK] beginner-roadmap.md
[OK] index.md (2 links rewritten)
...
[OK] Sync complete:
     - Files synced: 16
     - Links rewritten: 2
     - Destination: docs\learning
```

### Integration with Sphinx Build

```bash
# Complete documentation build workflow
python scripts/sync_educational_content.py && sphinx-build -M html docs docs/_build -W --keep-going
```

---

## What It Does

1. **Copies Files**: All 16 `.md` files from `.project/ai/edu/` to `docs/learning/`
2. **Preserves Structure**: Maintains exact directory hierarchy (3 levels deep)
3. **Rewrites Links**: Changes `../../docs/` → `../` for new location
4. **Adds Headers**: Injects generation timestamp and source path
5. **Idempotent**: Safe to run multiple times (overwrites cleanly)

---

## Performance

- **Sync Time**: 0.24 seconds (16 files)
- **Build Overhead**: < 1 second
- **Files Processed**: 16 markdown files
- **Link Rewrites**: 2 (in index.md)

---

## Directory Structure

```
.project/ai/edu/                 (SOURCE - canonical version)
├── beginner-roadmap.md
├── index.md
├── README.md
└── phase1/
    ├── *.md (4 files)
    ├── cheatsheets/ (4 files)
    ├── project-templates/ (1 file)
    └── solutions/ (3 files)

docs/learning/                   (DESTINATION - auto-generated)
├── <!-- AUTO-GENERATED HEADER -->
├── beginner-roadmap.md
├── index.md
├── README.md
└── phase1/
    └── (same structure as source)
```

---

## Link Rewriting

### Original Links (in source)
```markdown
[Jump to main docs](../../docs/guides/getting-started.md)
[Jump to tutorials](../../docs/guides/tutorials/)
```

### Rewritten Links (in destination)
```markdown
[Jump to main docs](../guides/getting-started.md)
[Jump to tutorials](../guides/tutorials/)
```

**Pattern**: `../../docs/` → `../`

---

## Generated Header Format

Each synced file gets this header:
```markdown
<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/{relative_path} -->
<!-- Generated: 2025-11-11 12:19:04 -->

(original content follows)
```

---

## When to Run

### Required
- Before building Sphinx documentation
- After modifying any content in `.project/ai/edu/`
- After git checkout (if educational content changed)

### Automatic (Future)
- Pre-commit hook (planned)
- CI/CD pipeline (planned)
- Pre-build Sphinx hook (planned)

---

## Validation

### Quick Validation
```python
python -c "
from pathlib import Path
src = Path('.project/ai/edu')
dest = Path('docs/learning')
print(f'Source: {len(list(src.rglob(\"*.md\")))} files')
print(f'Dest: {len(list(dest.rglob(\"*.md\")))} files')
"
```

### Full Validation
```bash
# Check headers
grep -r "AUTO-GENERATED from .project/ai/edu/" docs/learning/

# Check link rewrites
grep -r "../../docs/" docs/learning/  # Should return nothing

# Verify git ignore
git check-ignore -v docs/learning/
```

---

## Troubleshooting

### Issue: "Source directory not found"
**Cause**: Running from wrong directory
**Solution**: Run from repository root (`D:\Projects\main`)

### Issue: "Permission denied"
**Cause**: docs/learning/ is open in editor or locked
**Solution**: Close all editors, run again

### Issue: Links not rewritten
**Cause**: Regex pattern mismatch
**Solution**: Check source file for unexpected link formats

### Issue: Files missing in destination
**Cause**: Sync script exited early due to error
**Solution**: Check error messages, fix issue, re-run

---

## Maintenance

### Adding New Files
1. Add new `.md` file to `.project/ai/edu/`
2. Run sync script: `python scripts/sync_educational_content.py`
3. No code changes needed (auto-discovers all `.md` files)

### Modifying Link Patterns
Edit `rewrite_links()` function in `scripts/sync_educational_content.py`:
```python
def rewrite_links(content: str, source_file: Path) -> Tuple[str, int]:
    # Pattern 1: ../../docs/ -> ../
    pattern1 = r'\.\./\.\./docs/'
    replacement1 = '../'
    content, count1 = re.subn(pattern1, replacement1, content)

    # Add more patterns here as needed

    return content, count1
```

### Testing Changes
```bash
# Test sync
python scripts/sync_educational_content.py

# Test build
sphinx-build -M html docs docs/_build -W --keep-going

# Verify links
python -m http.server 9000 --directory docs/_build/html
# Open http://localhost:9000 and click links
```

---

## Integration Points

### Git Ignore
`.gitignore` line 95-96:
```gitignore
# Educational materials (auto-generated from .project/ai/edu/)
docs/learning/
```

### Sphinx Configuration
`docs/index.md` line 93:
```markdown
learning/index
```

### Navigation Files
- `docs/guides/INDEX.md` line 7
- `docs/NAVIGATION.md` lines 40, 228, 926
- `docs/NAVIGATION_STATUS_REPORT.md` line 200

All updated to reference `learning/` or `../learning/`

---

## Error Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | Source directory not found |
| 1 | No markdown files found |
| 1 | File sync error |

---

## Future Enhancements

### Planned Features
- [ ] Pre-commit hook integration
- [ ] CI/CD pipeline integration
- [ ] Incremental sync (only changed files)
- [ ] Link validation (check if targets exist)
- [ ] Watch mode (auto-sync on file changes)

### Performance Optimizations
- [ ] Parallel file processing (if > 100 files)
- [ ] Hash-based change detection (skip unchanged files)
- [ ] Async I/O for large files

---

## Related Documentation

- **Source Content**: `.project/ai/edu/README.md`
- **Build System**: `.project/ai/config/documentation_build_system.md`
- **Task Summary**: `SYNC_AUTOMATION_SUMMARY.md`
- **Sphinx Config**: `docs/conf.py`

---

**Last Updated**: 2025-11-11
**Author**: Claude Code - Agent 2
**Status**: Operational
