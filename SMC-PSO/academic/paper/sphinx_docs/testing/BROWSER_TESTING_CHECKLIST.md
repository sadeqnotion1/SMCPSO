# Browser Testing Checklist - Collapsible Code Blocks

**Quick Reference:** Use this checklist for rapid browser testing across different environments.

---

## Pre-Test Setup

- [ ] Files verified in `docs/_build/html/_static/`:
  - [ ] `code-collapse.js` (21KB)
  - [ ] `code-collapse.css` (8.9KB)
- [ ] Test page URL: `file:///D:/Projects/main/docs/_build/html/index.html` (or local server)
- [ ] Browser DevTools ready
- [ ] Validation report ready: `docs/testing/code_collapse_validation_report.md`

---

## Quick Smoke Test (5min per browser)

**Run this in each browser for rapid validation:**

1. **Open Page**
   - [ ] Navigate to `docs/_build/html/index.html`
   - [ ] Page loads without errors

2. **Console Check**
   - [ ] Open browser console (F12)
   - [ ] Look for: `[CodeCollapse] ✅ 100% coverage`
   - [ ] No red error messages

3. **Button Presence**
   - [ ] Collapse buttons visible on all code blocks
   - [ ] Gap between copy and collapse buttons = 5-8px (visual check)

4. **Collapse Test**
   - [ ] Click collapse button (▼)
   - [ ] Code hides smoothly (curtain effect)
   - [ ] Message appears: "Code hidden (click ▲ to expand)"

5. **Expand Test**
   - [ ] Click expand button (▲)
   - [ ] Code shows smoothly

6. **Master Controls**
   - [ ] Click "Collapse All" → all code blocks collapse
   - [ ] Click "Expand All" → all code blocks expand

7. **Keyboard Test**
   - [ ] Press Ctrl+Shift+C → all collapse
   - [ ] Press Ctrl+Shift+E → all expand

---

## Chrome Testing

**Version:** _______________

### Functional

- [ ] Buttons present
- [ ] Collapse/expand works
- [ ] Master controls work
- [ ] Keyboard shortcuts work
- [ ] Console shows 100% coverage

### Performance (DevTools → Performance)

- [ ] Record animation
- [ ] FPS ≥ 55: _____
- [ ] No layout shift warnings

### GPU Acceleration (DevTools → Rendering)

- [ ] Enable "Layer borders"
- [ ] Green border on code blocks during animation
- [ ] GPU layers active: Yes / No

**Status:** ✅ Pass / ❌ Fail
**Issues:** _______________

---

## Firefox Testing

**Version:** _______________

### Functional

- [ ] Buttons present
- [ ] Collapse/expand works
- [ ] Master controls work
- [ ] Keyboard shortcuts work
- [ ] Console shows 100% coverage

### Performance

- [ ] Animations smooth
- [ ] FPS check: _____
- [ ] No visible lag

**Note:** Firefox has partial support for `contain: layout` - minor performance differences expected.

**Status:** ✅ Pass / ❌ Fail
**Issues:** _______________

---

## Edge Testing

**Version:** _______________

### Functional

- [ ] Buttons present
- [ ] Collapse/expand works
- [ ] Master controls work
- [ ] Keyboard shortcuts work
- [ ] Console shows 100% coverage

### Performance

- [ ] Animations smooth
- [ ] FPS check: _____

**Status:** ✅ Pass / ❌ Fail
**Issues:** _______________

---

## Safari Testing (Optional - macOS/iOS only)

**Version:** _______________

### Functional

- [ ] Buttons present
- [ ] Collapse/expand works
- [ ] Master controls work
- [ ] Console shows 100% coverage

**Known Limitation:** `contain: layout` has limited support in Safari - may see minor layout shifts.

**Status:** ✅ Pass / ❌ Fail / ⏭️ Skipped
**Issues:** _______________

---

## Mobile Testing

**Device/Emulation:** _______________

### Viewport: 320px (iPhone SE)

- [ ] Buttons visible
- [ ] Gap = 5px (reduced for mobile)
- [ ] Collapse/expand works
- [ ] Touch targets comfortable (min 44x44px)

### Viewport: 375px (iPhone 12/13)

- [ ] Buttons visible
- [ ] Master controls wrap correctly
- [ ] No horizontal scroll

### Viewport: 768px (iPad)

- [ ] Buttons visible
- [ ] Gap = 8px (desktop size)
- [ ] Layout looks good

**Status:** ✅ Pass / ❌ Fail
**Issues:** _______________

---

## Accessibility Quick Check

### Keyboard Navigation

- [ ] Tab to collapse button → visible focus indicator
- [ ] Press Enter → collapse/expand works
- [ ] Ctrl+Shift+C → collapse all
- [ ] Ctrl+Shift+E → expand all

### Reduced Motion (DevTools → Rendering)

- [ ] Enable "Emulate CSS prefers-reduced-motion"
- [ ] Collapse/expand → instant (no animation)

### High Contrast (Windows only)

- [ ] Enable Windows High Contrast
- [ ] Buttons have 3px borders
- [ ] Sufficient color contrast

**Status:** ✅ Pass / ❌ Fail / ⏭️ Skipped
**Issues:** _______________

---

## Edge Cases

### Race Condition Test

- [ ] Hard refresh (Ctrl+Shift+R)
- [ ] Collapse button appears after copy button
- [ ] No console errors

### LocalStorage Disabled

- [ ] Disable LocalStorage (DevTools → Application → Storage)
- [ ] Collapse still works (state not persisted)
- [ ] Console shows warning: `Failed to save code block states`

### Large Code Block

- [ ] Find longest code block
- [ ] Collapse/expand
- [ ] Animation still smooth

### Rapid Clicks

- [ ] Rapidly click collapse button 5x
- [ ] No broken state
- [ ] `.code-collapsing` prevents interaction

**Status:** ✅ Pass / ❌ Fail
**Issues:** _______________

---

## Dark Mode Testing (if available)

- [ ] Toggle dark mode
- [ ] Control bar has darker gradient
- [ ] Buttons visible
- [ ] Collapsed message readable
- [ ] Colors look good

**Status:** ✅ Pass / ❌ Fail / ⏭️ N/A
**Issues:** _______________

---

## Print Preview Testing

- [ ] Open Print Preview (Ctrl+P)
- [ ] All code blocks expanded (even if collapsed on screen)
- [ ] No collapse buttons visible
- [ ] No master controls visible
- [ ] "Code hidden" message not visible

**Status:** ✅ Pass / ❌ Fail
**Issues:** _______________

---

## Summary

| Browser | Version | Status | Issues |
|---------|---------|--------|--------|
| Chrome | _____ | ⏳ | - |
| Firefox | _____ | ⏳ | - |
| Edge | _____ | ⏳ | - |
| Safari | _____ | ⏳ | - |
| Mobile | _____ | ⏳ | - |

**Overall Pass Rate:** _____ / _____ (___%)

**Critical Issues:** [None / List]

**Tester:** _______________
**Date:** _______________

---

## Next Steps

After completing this checklist:
1. Transfer results to `code_collapse_validation_report.md`
2. Address any P0/P1 issues discovered
3. Take screenshots for documentation
4. Mark Phase 5 as complete
5. Proceed to Phase 6 (Documentation & Maintenance) if approved
