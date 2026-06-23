# Maintenance Guide - Collapsible Code Blocks

**For Future Maintainers**
**Last Updated:** 2025-10-12

**What This Guide Covers:**
This maintenance guide provides operational procedures, troubleshooting workflows, and update instructions for future maintainers of the collapsible code blocks feature. It documents file locations, change procedures, testing requirements, and common maintenance tasks.

**Who This Is For:**
- **Future maintainers**: Developers taking over this codebase
- **Operations team**: DevOps managing deployments
- **Contributors**: Adding enhancements or fixing bugs
- **Support team**: Troubleshooting user-reported issues

**What You'll Learn:**
- File locations and architecture overview
- Step-by-step procedures for making changes
- Testing and validation requirements
- Emergency hotfix procedures
- Common maintenance tasks and their frequency

**Related Documentation:**
- [Technical Reference](technical-reference.md) - Architecture and API details
- [Troubleshooting Guide](troubleshooting.md) - Issue resolution procedures
- [Changelog](changelog.md) - Version history
- [Testing Procedures](../../testing/TESTING_PROCEDURES.md) - Validation steps

---

## File Locations

### Source Files

- **JavaScript**: `docs/_static/code-collapse.js` (21KB)
- **CSS**: `docs/_static/code-collapse.css` (8.9KB)
- **Configuration**: `docs/conf.py` (lines 204, 213)

### Build Output

- **Deployed JS**: `docs/_build/html/_static/code-collapse.js`
- **Deployed CSS**: `docs/_build/html/_static/code-collapse.css`

### Documentation

- **User Guide**: `docs/guides/features/code-collapse/user-guide.md`
- **Integration**: `docs/guides/features/code-collapse/integration-guide.md`
- **Technical Ref**: `docs/guides/features/code-collapse/technical-reference.md`
- **Testing**: `docs/testing/` (Phase 5 documentation)

---

## Making Changes

### Modify Animation Duration

1. Open `code-collapse.js`
2. **Line 23**: Change `animationDuration: 350`
3. **Line 127-128** (CSS in JS): Update transition duration
4. **Test**: Run Phase 5 performance tests
5. **Rebuild**: `sphinx-build -b html docs docs/_build/html`

```javascript
// In code-collapse.js
const CONFIG = {
    animationDuration: 500,  // Change from 350ms to 500ms
};
```

### Add New Selector Pattern

1. Open `code-collapse.js`
2. **Line 44-50**: Add to `selectors` array
3. **Test**: Check console for 100% coverage message
4. **Document**: Update `configuration-reference.md`

```javascript
const selectors = [
    // ... existing selectors
    'div.my-custom-highlight pre',  // Add your selector
];
```

### Change Button Style

1. Open `code-collapse.css`
2. **Line 65-80**: Modify `.code-collapse-btn` styles
3. **Test**: Visual regression (compare before/after screenshots)
4. **Rebuild** and verify

```css
.code-collapse-btn {
    background: rgba(0, 120, 212, 0.1);  /* Change color */
    padding: 4px 8px;                    /* Adjust size */
}
```

### Update Button Icons

1. Open `code-collapse.js`
2. **Line 25-26**: Modify `collapsedIcon` and `expandedIcon`
3. **Test**: Verify icons display correctly
4. **Rebuild**

```javascript
const CONFIG = {
    collapsedIcon: '▶',  // Change from '▶'
    expandedIcon: '▼',   // Change from '▼'
};
```

---

## Testing Changes

### Quick Smoke Test (5 minutes)

```bash
# 1.

Rebuild documentation
sphinx-build -b html docs docs/_build/html

# 2.

Open in browser
start docs/_build/html/index.html  # Windows
open docs/_build/html/index.html   # Mac

# 3.

Verify functionality
# - Buttons appear on all code blocks
# - Collapse/expand works smoothly
# - Console shows "[CodeCollapse] ✅ 100% coverage"
```

### Comprehensive Test (30 minutes)

Follow complete testing procedure:
```bash
# See detailed checklist
docs/testing/BROWSER_TESTING_CHECKLIST.md
docs/testing/TESTING_PROCEDURES.md
```

**Test in multiple browsers:**
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+ (if available)

**Check for:**
- Button placement and spacing
- Animation smoothness (60 FPS)
- State persistence (reload page)
- Keyboard shortcuts (Ctrl+Shift+C/E)
- Mobile responsiveness
- Accessibility (screen reader)

---

## Debugging

### Enable Debug Logging

Debug logging is **enabled by default** (lines 58-89 in `code-collapse.js`).

**Console output includes:**
```
[CodeCollapse] Found 42 code blocks
[CodeCollapse] ✅ 100% coverage (42 matched, 0 unmatched)
[CodeCollapse] Selector performance:
┌─────────┬──────────────────────────┬────────┐
│ (index) │ selector                 │ count  │
├─────────┼──────────────────────────┼────────┤
│ 0       │ 'div.highlight-python'   │ 15     │
│ 1       │ 'div[class*="highlight"]'│ 27     │
└─────────┴──────────────────────────┴────────┘
```

### Common Issues

#### Issue:

Buttons Not Appearing

**Diagnosis:**
1. Open browser console (F12)
2. Look for red error messages
3. Check if `code-collapse.js` loaded

**Solutions:**
```javascript
// In console, verify script loaded:
document.querySelector('script[src*="code-collapse.js"]')
// Should return: <script> element (not null)

// Check if copybutton.js loaded:
document.querySelector('.copybtn')
// Should return: copy button elements (not null)
```

**Fix:**
- Verify `conf.py` includes both files in `html_js_files` and `html_css_files`
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+Shift+R)

#### Issue:

Animation Jank

**Diagnosis:**
1. Open DevTools → Performance tab
2. Record while collapsing a code block
3. Check FPS chart (should be ≥55 FPS)

**Solutions:**
- Enable GPU acceleration in browser settings
- Disable browser extensions (test in Incognito mode)
- Update browser to latest version
- Check for conflicting CSS from other extensions

#### Issue:

State Not Persisting

**Diagnosis:**
```javascript
// In console:
localStorage.getItem('code-block-states')
// Should return: JSON string like {"0":"collapsed"}
// If null: State not saving
```

**Solutions:**
- Check if localStorage is enabled (Settings → Privacy)
- Not in Private/Incognito mode (state won't persist)
- Clear and retry: `clearCodeBlockStates()` in console
- Check localStorage quota: `JSON.stringify(localStorage).length`

---

## Versioning

### Current Version

**1.0.0** (Phase 6 Complete - 2025-10-12)

### Version History

- **1.0.0** (2025-10-12): Initial release with Phases 1-6
- Future versions: See `changelog.md`

### Breaking Changes Policy

- **Major version** (2.0.0): Breaking API changes (require code updates)
- **Minor version** (1.1.0): New features (backward compatible)
- **Patch version** (1.0.1): Bug fixes (no API changes)

---

## Upgrading Dependencies

### copybutton.js Compatibility

- **Tested with**: sphinx-copybutton 0.5.2+
- Wait-and-retry pattern handles version differences
- If copybutton changes structure, adjust retry logic (lines 164-189 in JS)

### Browser Support Updates

- Test new browser versions annually
- Update compatibility matrix in `technical-reference.md`
- Adjust CSS/JS for browser-specific bugs

---

## Performance Monitoring

### Metrics to Track

- **FPS** during collapse/expand (target: ≥55)
- **CLS** (Cumulative Layout Shift) (target: <0.1)
- **Memory** usage (target: <100KB)
- **Coverage** percentage (target: 100%)

### How to Measure

```javascript
// FPS: DevTools → Performance → Record → Collapse block
// CLS: DevTools → Performance Insights → Core Web Vitals
// Memory: DevTools → Memory → Take heap snapshot
// Coverage: Check console log "[CodeCollapse] ✅ 100% coverage"
```

### Performance Regression Detection

If metrics degrade:
1. Compare before/after code changes
2. Profile with DevTools Performance tab
3. Check for new CSS conflicts
4. Test on slower hardware

---

## Code Quality

### Linting (Optional)

```bash
# JavaScript (if ESLint configured)
eslint docs/_static/code-collapse.js

# CSS (if stylelint configured)
stylelint docs/_static/code-collapse.css
```

### Minification (Optional)

```bash
# Minify JavaScript (requires terser)
terser docs/_static/code-collapse.js -o code-collapse.min.js

# Minify CSS (requires clean-css-cli)
cleancss docs/_static/code-collapse.css -o code-collapse.min.css
```

**Note:** Not implemented by default (readability prioritized)

---

## Rollback Procedure

If an update breaks functionality:

```bash
# 1.

Revert files to previous commit
git checkout HEAD~1 -- docs/_static/code-collapse.js
git checkout HEAD~1 -- docs/_static/code-collapse.css

# 2.

Rebuild documentation
sphinx-build -b html docs docs/_build/html

# 3.

Test (quick smoke test)
start docs/_build/html/index.html

# 4.

Commit rollback
git commit -m "Revert: Code collapse changes (broke functionality)"
git push
```

---

## Future Enhancements

### Phase 7 Ideas (Not Implemented)

- [ ] Automated browser testing (Playwright/Cypress)
- [ ] Visual regression testing (Percy, BackstopJS)
- [ ] Configurable animation themes (bounce, slide, fade)
- [ ] Animation presets in CONFIG object
- [ ] Bulk state management UI (sidebar panel)
- [ ] Analytics tracking (collapse/expand events)
- [ ] Lazy loading optimization for large pages
- [ ] Code block minimap preview (hover to peek)

### How to Propose Changes

1. Open GitHub issue with proposal
2. Create feature branch: `git checkout -b feature/code-collapse-enhancement`
3. Implement changes
4. Run Phase 5 tests
5. Update documentation
6. Submit pull request

---

## Support Contacts

- **Primary Maintainer**: [TO BE ASSIGNED]
- **Documentation**: All files in `docs/guides/features/code-collapse/`
- **Issues**: GitHub repository issues tab
- **Testing**: `docs/testing/` (Phase 5 documentation)

---

## Maintenance Checklist

### Monthly

- [ ] Check for browser updates affecting compatibility
- [ ] Review GitHub issues for bug reports
- [ ] Monitor performance metrics (if analytics added)

### Quarterly

- [ ] Update browser support matrix
- [ ] Review and update documentation
- [ ] Test on new browser versions

### Annually

- [ ] Major version review
- [ ] Consider Phase 7 enhancements
- [ ] Update dependencies (sphinx-copybutton, etc.)

---

## Emergency Procedures

### If Feature Breaks Production

1. **Immediate**: Disable feature in `conf.py`
   ```python
   # Comment out in conf.py:
   # html_js_files = ['code-collapse.js']
   # html_css_files = ['code-collapse.css']
   ```

2. **Rebuild**: `sphinx-build -b html docs docs/_build/html`

3. **Deploy**: Push rebuilt docs without feature

4. **Investigate**: Use rollback procedure above

5. **Fix**: Create hotfix branch, test, deploy

### Contact Information

- **Urgent Issues**: [Primary maintainer email]
- **Non-urgent**: GitHub issues
- **Documentation**: This file and related guides
