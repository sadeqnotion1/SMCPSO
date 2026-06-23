# Documentation Quality Gates

**Phase 6.5: Enforced Quality Standards**

This document describes the quality gates enforced in the DIP-SMC-PSO project to maintain code quality, documentation completeness, and production readiness.

## Overview

Quality gates are **automated checks** that must pass before code can be merged. They ensure:
- ✅ Consistent code quality and style
- ✅ Complete documentation and type hints
- ✅ Valid internal links
- ✅ Production-ready codebase

## Gate Types

### 🔴 Blocking Gates (MUST PASS)

These gates will **fail CI builds** if not met:

| Gate | Requirement | Impact |
|------|-------------|--------|
| **Docstring Coverage** | ≥95% | Fails build if below threshold |
| **Link Validation** | 0 broken links | Fails build if links broken |
| **Type Hint Coverage** | ≥95% | Fails build if below threshold |

### ⚠️ Advisory Gates (Recommended)

These gates provide **warnings only**:

| Gate | Purpose | Impact |
|------|---------|--------|
| **Markdown Linting** | Style consistency | Warning only |
| **Spell Checking** | Documentation quality | Warning only |

---

## Local Validation

### Quick Check (Pre-Commit Hook)

The pre-commit hook runs automatically before each commit:

```bash
# Runs automatically on: git commit
# Checks:
# - Python syntax
# - Large files (>1MB)
# - Debug statements (pdb, breakpoint)
# - TODO/FIXME markers
# - Ruff linting
```

**Bypass hook (use sparingly):**

```bash
git commit --no-verify
```

## Check

Run full quality validation before pushing:

```bash
# Run all checks
python scripts/validation/run_quality_checks.py

# Run specific check
python scripts/validation/run_quality_checks.py --check docstrings
python scripts/validation/run_quality_checks.py --check types
python scripts/validation/run_quality_checks.py --check links
```

**Available checks:**
- `syntax` - Python syntax validation
- `docstrings` - Docstring coverage (≥95%)
- `types` - Type hint coverage (≥95%)
- `links` - Documentation link validation
- `markdown` - Markdown linting (advisory)
- `spell` - Spell checking (advisory)

## Auto-Fix Common Issues

Automatically fix common quality issues:

```bash
# Dry run (preview changes)
python scripts/validation/fix_common_issues.py --dry-run

# Apply fixes
python scripts/validation/fix_common_issues.py

# Fix specific directory
python scripts/validation/fix_common_issues.py --target src
python scripts/validation/fix_common_issues.py --target docs
```

**What gets fixed:**
- ✓ Trailing whitespace
- ✓ Missing final newlines
- ✓ Import organization (isort)
- ✓ Code formatting (ruff)
- ✓ Auto-fixable linting issues
- ✓ Markdown formatting
- ✓ Common typos

---

## CI/CD Integration

### GitHub Actions Workflow

File: `.github/workflows/docs-quality.yml`

**Triggers:**
- Pull requests to `main`
- Pushes to `main`
- Manual workflow dispatch

**Jobs:**
1. **Markdown Linting** (advisory)
2. **Spell Checking** (advisory)
3. **Docstring Coverage** (blocking, ≥95%)
4. **Link Validation** (blocking, 0 broken)
5. **Type Hint Coverage** (blocking, ≥95%)
6. **Quality Gate Enforcement** (summary)

### Workflow Status

Check your PR for quality gate status:

```
✓ Markdown Linting (advisory)
✓ Spell Checking (advisory)
✓ Docstring Coverage (95.8%) ← BLOCKING
✓ Link Validation (0 broken) ← BLOCKING
✓ Type Hint Coverage (96.2%) ← BLOCKING
```

### Failure Response

If a blocking gate fails:

1. **Check the CI logs** for specific failures
2. **Run local validation** to reproduce:
   ```bash
   python scripts/validation/run_quality_checks.py --check <failed-gate>
   ```
3. **Fix the issues** manually or with auto-fix:
   ```bash
   python scripts/validation/fix_common_issues.py
   ```
4. **Re-run validation** to confirm:
   ```bash
   python scripts/validation/run_quality_checks.py
   ```
5. **Commit and push** the fixes

---

## Quality Standards

### Docstring Coverage (≥95%)

**What counts:**
- All public modules, classes, methods, and functions must have docstrings
- Docstrings must follow NumPy/Google style
- Private methods (`_method`) are excluded
- Magic methods (`__init__`, `__str__`) are excluded

**Check coverage:**

```bash
interrogate src/ \
  --ignore-init-method \
  --ignore-init-module \
  --ignore-magic \
  --ignore-private \
  --ignore-nested-functions \
  --verbose 2
```

**Fix:**
- Add missing docstrings to public functions/classes
- Ensure docstrings include:
  - Brief description
  - Parameters (with types)
  - Returns (with type)
  - Raises (if applicable)
  - Examples (recommended)

**Example:**
```python
def compute_control(self, state: np.ndarray) -> float:
    """
    Compute control force for current state.

    Parameters
    ----------
    state : np.ndarray
        Current system state [x, dx, θ1, dθ1, θ2, dθ2]

    Returns
    -------
    float
        Control force in Newtons

    Raises
    ------
    ValueError
        If state dimension is invalid
    """
    ...
```

### Type Hint Coverage (≥95%)

**What counts:**
- All function/method signatures must have type hints
- Function return types must be annotated
- Type hints must be accurate and meaningful

**Check coverage:**

```bash
python scripts/validation/run_quality_checks.py --check types
```

**Fix:**
- Add type hints to function parameters and returns
- Import required types from `typing` module
- Use appropriate generic types (List, Dict, Optional, etc.)

**Example:**

```python
from typing import List, Optional, Tuple

def optimize_gains(
    controller: str,
    bounds: List[Tuple[float, float]],
    iterations: int = 100,
    seed: Optional[int] = None
) -> Tuple[np.ndarray, float]:
    """..."""
    ...
```

### Link Validation (0 broken)

**What counts:**
- All internal documentation links must be valid
- Cross-references between documentation files
- Links to source code files

**Check links:**

```bash
python scripts/documentation/analyze_cross_references.py
pytest tests/test_documentation/test_cross_references.py -v
```

**Fix:**
- Update moved/renamed file references
- Fix typos in file paths
- Remove references to deleted files
- Use relative paths consistently

---

## Best Practices

### Before Committing

```bash
# 1. Run auto-fix
python scripts/validation/fix_common_issues.py

# 2. Run quality checks
python scripts/validation/run_quality_checks.py

# 3. Commit if all checks pass
git commit -m "Your commit message"
```

## Before Pushing

```bash
# Run validation
python scripts/validation/run_quality_checks.py

# If passed, push
git push origin <branch>
```

## When Adding New Code

1. **Write docstrings** for all public functions/classes
2. **Add type hints** to all function signatures
3. **Update documentation** if adding new features
4. **Run validation** before committing

### When Modifying Documentation

1. **Check links** after moving/renaming files
2. **Run spell check** for new documentation
3. **Validate markdown** formatting
4. **Re-run link validation** before pushing

---

## Troubleshooting

### "Docstring coverage below 95%"

**Diagnosis:**

```bash
interrogate src/ --verbose 2 | grep "Missing"
```

**Solution:**

Add docstrings to the listed functions/classes.

### "Broken links detected"

**Diagnosis:**

```bash
cat .test_artifacts/cross_references/broken_links.json
```

**Solution:**

Fix or remove the broken links listed in the JSON file.

### "Type hint coverage below 95%"

**Diagnosis:**

```bash
find src -name "*.py" -exec grep -L "from typing import\|: .*->" {} \;
```

**Solution:**

Add type hints to the listed files.

### "Pre-commit hook fails"

**Quick fix:**

```bash
# Fix common issues
python scripts/validation/fix_common_issues.py

# Re-run commit
git commit
```

**Bypass (use sparingly):**
```bash
git commit --no-verify
```

---

## FAQ

**Q: Can I bypass quality gates?**

A: Pre-commit hooks can be bypassed with `--no-verify`, but CI gates cannot be bypassed without admin approval.

**Q: How long do quality checks take?**

A: Local validation: ~30 seconds. CI validation: ~2-3 minutes.

**Q: What happens if I ignore advisory gates?**

A: Advisory gates (markdown linting, spell checking) won't block merges but should be addressed for code quality.

**Q: Can I add custom quality checks?**

A: Yes! Add new checks to `scripts/validation/run_quality_checks.py` and update `.github/workflows/docs-quality.yml`.

**Q: Why are quality gates enforced?**

A: To maintain consistent code quality, complete documentation, and production readiness across the project.

---

## Implementation Timeline

- **Phase 6.1-6.2:** Cross-reference integration, code example validation
- **Phase 6.3:** Interactive documentation enhancement (Chart.js, dashboards)
- **Phase 6.4:** Documentation build automation
- **Phase 6.5:** ✅ **Quality gates enforcement** (this phase)
- **Phase 6.6:** Changelog & version documentation
- **Phase 6.7:** Final cleanup

---

## References

- [Documentation Quality Workflow](../../.github/workflows/docs-quality.yml)
- [Quality Check Script](../../scripts/validation/run_quality_checks.py)
- [Auto-Fix Script](../../scripts/validation/fix_common_issues.py)
- [Pre-Commit Hook](../../.git/hooks/pre-commit)

---

**Last Updated:** Phase 6.5 (2025-10-08)
**Maintained By:** Development Team
