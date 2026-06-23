# Documentation Versioning Guide

This guide explains how versioned documentation is managed for the DIP-SMC-PSO project.



## Overview

Documentation versioning ensures users can access docs for:
- **Latest (main):** Development version
- **Stable:** Latest release
- **v1.0.x, v1.1.x:** Specific release versions



## Version Strategy

### Version Tags

Documentation versions correspond to git tags:

```bash
# Create release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Version Naming

| Version | Description | URL |
|---------|-------------|-----|
| `latest` | Development (main branch) | `/en/latest/` |
| `stable` | Latest release | `/en/stable/` |
| `v1.0` | Version 1.0.x series | `/en/v1.0/` |
| `v1.1` | Version 1.1.x series | `/en/v1.1/` |



## ReadTheDocs Configuration

### Automatic Builds

ReadTheDocs automatically builds documentation when:
1. **Push to main:** Updates `latest` version
2. **New tag created:** Builds version-specific docs
3. **PR opened:** Builds preview (if enabled)

### Version Activation

1. Go to ReadTheDocs project settings
2. Navigate to **Versions**
3. Activate desired versions (e.g., v1.0, stable)
4. Set default version (typically `stable`)



## Sphinx Version Configuration

### In `docs/conf.py`

```python
# Version information
import subprocess

# Get version from git tags
try:
    version = subprocess.check_output(
        ['git', 'describe', '--tags', '--abbrev=0'],
        stderr=subprocess.DEVNULL
    ).decode('utf-8').strip()
    release = version
except:
    version = '1.0.0'
    release = '1.0.0'

# Version selector
html_context = {
    'display_github': True,
    'github_user': 'theSadeQ',
    'github_repo': 'dip-smc-pso',
    'github_version': 'main',
    'conf_py_path': '/docs/',
    'versions': [
        ('latest', '/en/latest/'),
        ('stable', '/en/stable/'),
        ('v1.0', '/en/v1.0/'),
    ]
}
```



## Version Selector in Documentation

### HTML Theme Integration

The version selector appears in the navigation bar, allowing users to switch between versions.

**Furo theme (current):**
```python
html_theme_options = {
    'source_repository': 'https://github.com/theSadeQ/dip-smc-pso/',
    'source_branch': 'main',
    'source_directory': 'docs/',
}
```



## Release Workflow

### Creating a New Release

1. **Update version in code:**
   ```bash
   # Update version in setup.py, __init__.py, etc.
   ```

2. **Update CHANGELOG.md:**
   ```bash
   git add CHANGELOG.md
   git commit -m "Update changelog for v1.1.0"
   ```

3. **Create release tag:**
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```

4. **ReadTheDocs auto-builds:** Version `v1.1` automatically created

5. **Activate on ReadTheDocs:**
   - Go to ReadTheDocs dashboard
   - Activate `v1.1` version
   - Optionally set as default



## Version Management Best Practices

### Documentation Branches

- **main:** Latest development docs
- **stable:** Synced with latest release tag
- **v1.0-docs:** Branch for v1.0.x doc fixes

### Backporting Doc Fixes

```bash
# Fix docs on main
git checkout main
# ... make fixes ...
git commit -m "Fix typo in tutorial"

# Backport to v1.0 docs
git checkout v1.0-docs
git cherry-pick <commit-hash>
git push origin v1.0-docs
```

## Deprecation Warnings

Add version warnings for deprecated features:

```rst
.. deprecated:: 1.1.0
   This feature is deprecated. Use :func:`new_feature` instead.
```



## Troubleshooting

### Version Not Showing

**Problem:** New version tag created but not appearing on ReadTheDocs.

**Solution:**
1. Check ReadTheDocs build logs
2. Activate version in ReadTheDocs settings
3. Trigger manual build if needed

### Version Selector Not Working

**Problem:** Users can't switch versions.

**Solution:**
1. Verify `html_context['versions']` in `conf.py`
2. Check theme supports version switching
3. Clear ReadTheDocs build cache

### Old Version Still Showing

**Problem:** Latest changes not reflected in docs.

**Solution:**
1. Check which version is set as default
2. Clear browser cache
3. Rebuild on ReadTheDocs



## Automation

### GitHub Actions Integration

Documentation versions are automatically managed via:

**.github/workflows/docs-build.yml:**
- Builds on every push to main (→ `latest`)
- Builds on every new tag (→ versioned docs)

**.github/workflows/release.yml (future):**
```yaml
- name: Update stable docs
  if: startsWith(github.ref, 'refs/tags/v')
  run: |
    # Tag also triggers stable rebuild
    git tag -f stable
    git push -f origin stable
```



## Documentation Version Support Policy

| Version | Support Status | Updates |
|---------|----------------|---------|
| **latest** | Development | Continuous |
| **stable** | Supported | Bug fixes |
| **v1.1** | Supported | Critical fixes only |
| **v1.0** | Maintenance | Security fixes only |
| **<v1.0** | Unsupported | None |



## User-Facing Version Information

### In Documentation Footer

Each page displays:
- Current version (e.g., "v1.1.0")
- Last updated date
- Link to latest version

### Version Banners

For old versions, display warning banner:

```rst
.. note::
   You are viewing documentation for version 1.0.
   See the `latest documentation <https://dip-smc-pso.readthedocs.io/en/latest/>`_
   for the most up-to-date information.
```



## ReadTheDocs Dashboard

**Project URL:** https://readthedocs.org/projects/dip-smc-pso/

**Key Settings:**
- **Default version:** stable
- **Active versions:** latest, stable, v1.1, v1.0
- **Build settings:** Python 3.12, Ubuntu 22.04
- **Webhooks:** Enabled for auto-builds



## Testing Version Switching

### Local Testing

Build multiple versions locally:

```bash
# Build current version
cd docs
sphinx-build -b html . _build/html

# Build with version tag
git checkout v1.0.0
sphinx-build -b html . _build/html-v1.0

# Build latest
git checkout main
sphinx-build -b html . _build/html-latest
```

## Preview URLs

- Latest: https://dip-smc-pso.readthedocs.io/en/latest/
- Stable: https://dip-smc-pso.readthedocs.io/en/stable/
- v1.0: https://dip-smc-pso.readthedocs.io/en/v1.0/



## Future Enhancements

1. **Version comparison tool:** Show differences between versions
2. **Archived versions:** Keep all historical versions accessible
3. **Version-specific search:** Search within specific version only
4. **Automated changelog generation:** From git commits
5. **Version deprecation notices:** Automatic warnings for old versions



**Last Updated:** 2025-10-07
**Maintained By:** Documentation Team
