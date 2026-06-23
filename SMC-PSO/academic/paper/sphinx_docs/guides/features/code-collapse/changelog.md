# Changelog - Collapsible Code Blocks Feature

**What This Document Is:**
This changelog tracks all changes to the collapsible code blocks feature. You can see what was added, what changed, and what's planned for future versions.

**Who Should Read This:**
- Developers maintaining the feature
- Users wanting to know what's new
- Anyone tracking feature evolution over time

**Format:**
This changelog follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format, which organizes changes into clear categories (Added, Changed, Fixed, etc.).

**Quick Navigation:**
- [Latest Release (1.0.0)](#100---2025-10-12) - Current stable version
- [Planned Features](#unreleased) - What's coming next
- [Migration Guide](#migration-guide) - How to upgrade

---

## Introduction

The collapsible code blocks feature was developed in 6 phases from October 2025. It allows users to collapse and expand code examples in the documentation, making pages easier to navigate and read.

**Key Benefits:**
- Cleaner documentation pages (less scrolling)
- User control over what code to view
- Fast performance (60 FPS animations)
- Works on all modern browsers

**Development History:**
Started as a simple button spacing fix (Phase 1), evolved into a comprehensive feature with accessibility, performance optimization, and full browser support (Phases 2-6).

---

## [1.0.0] - 2025-10-12

### Added

- Collapsible code blocks with smooth curtain animations
- Master controls ("Collapse All" / "Expand All") at top of pages
- Keyboard shortcuts (Ctrl+Shift+C / Ctrl+Shift+E)
- State persistence via LocalStorage across page reloads
- 100% selector coverage system with debug logging
- Full accessibility support (ARIA, keyboard navigation, reduced motion)
- Mobile responsive design (touch-friendly buttons, adaptive spacing)
- Print-friendly behavior (all blocks expanded when printing)
- Dark mode support with themed colors
- GPU-accelerated animations (60 FPS target)

### Implementation Phases

1. **Phase 1:** Button spacing fix (40px → 5-8px gap)
2. **Phase 2:** Architectural fix (true button siblings, wait-and-retry pattern)
3. **Phase 3:** 100% selector coverage + comprehensive debug logging
4. **Phase 4:** GPU-accelerated smooth animations (Material Design easing, double RAF)
5. **Phase 5:** Testing & validation (35+ test cases across 7 categories)
6. **Phase 6:** Documentation & maintenance (this release)

### Performance Metrics

- **FPS:** 58-60 during collapse/expand animations
- **CLS:** <0.05 (Cumulative Layout Shift, well below 0.1 target)
- **Memory:** <100KB total (JS + CSS + localStorage state)
- **Coverage:** 100% (all code blocks matched, math blocks excluded)
- **Button Gap:** 8px desktop, 5px mobile

### Browser Support

- Chrome 90+ (full support with all GPU features)
- Firefox 88+ (full support, partial CSS containment)
- Edge 90+ (full support with all GPU features)
- Safari 14+ (core features work, limited CSS containment)

### Files Added

- `docs/_static/code-collapse.js` (21KB)
- `docs/_static/code-collapse.css` (8.9KB)
- `docs/guides/features/code-collapse/user-guide.md`
- `docs/guides/features/code-collapse/integration-guide.md`
- `docs/guides/features/code-collapse/configuration-reference.md`
- `docs/guides/features/code-collapse/troubleshooting.md`
- `docs/guides/features/code-collapse/technical-reference.md`
- `docs/guides/features/code-collapse/maintenance-guide.md`
- `docs/guides/features/code-collapse/changelog.md`
- `docs/testing/code_collapse_validation_report.md`
- `docs/testing/BROWSER_TESTING_CHECKLIST.md`
- `docs/testing/TESTING_PROCEDURES.md`
- `docs/testing/PHASE5_SETUP_COMPLETE.md`

### Configuration Changes

**How to Enable:**
Add these lines to your Sphinx `conf.py` file:

```python
# In conf.py
html_css_files = [
    'code-collapse.css',  # Add to your existing list
]

html_js_files = [
    'code-collapse.js',   # Add to your existing list
]
```

**Configuration Details:**
- Added `'code-collapse.css'` to `html_css_files` in `conf.py` (line 204)
- Added `'code-collapse.js'` to `html_js_files` in `conf.py` (line 213)

### Technical Details

- **Selectors:** 6 comprehensive patterns for 100% code block coverage
- **Exclusions:** Math blocks (amsmath, math, nohighlight), very short blocks (<10 chars)
- **Animation:** Double `requestAnimationFrame` pattern with Material Design easing
- **GPU Hints:** `contain: layout`, `transform: translateZ(0)`, `will-change`, `backface-visibility`
- **Accessibility:** ARIA labels/states, keyboard focus indicators, reduced motion support
- **State Management:** LocalStorage with graceful degradation

---

## [Unreleased]

### Planned Enhancements (Phase 7+)

- [ ] Automated browser testing framework (Playwright/Cypress)
- [ ] Visual regression testing suite
- [ ] Configurable animation themes (presets: minimal, standard, bouncy)
- [ ] Bulk state management UI (collapse all across sessions)
- [ ] Analytics tracking (optional collapse/expand event tracking)
- [ ] Lazy loading optimization for very large pages (1000+ code blocks)
- [ ] Theme customization API for developers
- [ ] Code block preview on hover when collapsed
- [ ] Collapse groups (collapse related code blocks together)

### Under Consideration

- [ ] Minified versions (code-collapse.min.js, code-collapse.min.css)
- [ ] CDN hosting option
- [ ] npm package for easy installation
- [ ] Integration with sphinx-tabs extension

---

## Version History

### Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- **MAJOR:** Breaking changes (require code updates)
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes (no API changes)

### Release Process

1. Update this changelog
2. Update version in documentation
3. Run Phase 5 test suite
4. Rebuild documentation
5. Tag release in Git
6. Deploy to production

---

## Migration Guide

### From No Code Collapse Feature

- No migration needed
- Feature activates automatically on next build
- Users can immediately start collapsing code blocks

### Future Version Migrations

- Will be documented here as needed
- Breaking changes will include migration instructions

---

## How to Use This Changelog

**Finding What You Need:**
- **Looking for new features?** Check the [Added] sections in each version
- **Upgrading?** See the [Migration Guide](#migration-guide) section
- **Planning ahead?** Review [Unreleased](#unreleased) for upcoming features

**Legend:**
- **Added** - New features that didn't exist before
- **Changed** - Modifications to existing functionality
- **Deprecated** - Features that still work but will be removed soon
- **Removed** - Features that no longer work
- **Fixed** - Bug fixes and corrections
- **Security** - Security-related improvements

---

## Related Documentation

- [User Guide](user-guide.md) - How to use collapsible code blocks
- [Configuration Reference](configuration-reference.md) - All customization options
- [Integration Guide](integration-guide.md) - Adding to your Sphinx docs
- [Technical Reference](technical-reference.md) - Implementation details
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

---

**Maintained by:** DIP_SMC_PSO Documentation Team
**Last Updated:** 2025-11-10
**Version:** 1.0.0
