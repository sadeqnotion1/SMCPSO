# Collapsible Code Blocks - Integration Guide

**For Sphinx Project Developers**
**Last Updated:** 2025-10-12

**What This Covers:**
This guide shows you how to add collapsible code blocks to your Sphinx documentation. You'll learn how to install the feature, customize it for your theme, and troubleshoot common issues.

**Who This Is For:**
- Sphinx documentation maintainers
- Technical writers working with code-heavy docs
- Developers integrating UI features into Sphinx sites

**What You'll Learn:**
- 5-minute installation process (copy files + edit conf.py)
- Theme compatibility and customization options
- Integration with sphinx-copybutton and other extensions

**Quick Example:**
```python
# Just add two lines to conf.py
html_css_files = ['code-collapse.css']
html_js_files = ['code-collapse.js']
# Rebuild docs - done!
```

---

## Quick Start (5 Minutes)

### Prerequisites

- Sphinx 4.0+
- Python 3.7+
- sphinx-copybutton extension (recommended but optional)

### Installation

#### Step 1: Copy Files

```bash
# From this project's docs/_static/ directory
cp code-collapse.js your-project/docs/_static/
cp code-collapse.css your-project/docs/_static/
```

#### Step 2:

Update conf.py

```python
# Add to html_css_files list
html_css_files = [
    'code-collapse.css',
]

# Add to html_js_files list
html_js_files = [
    'code-collapse.js',
]
```

#### Step 3:

Rebuild Documentation

```bash
cd your-project/docs
sphinx-build -b html . _build/html
```

#### Step 4: Verify

Open `_build/html/index.html` in a browser:
- Check console (F12) for: `[CodeCollapse] ✅ 100% coverage`
- Verify collapse buttons appear on code blocks
- Test collapse/expand functionality

**Done!** If you see the success message, the feature is working.

---

## Compatibility

### Tested Themes

- ✅ **Furo** (fully tested, recommended)
- ✅ **Read the Docs** (compatible)
- ✅ **Alabaster** (compatible)
- ⚠️ **Custom themes** (may need CSS adjustments)

### Required Extensions

- **sphinx-copybutton** (recommended) - Buttons positioned relative to copy button
- Without it: Collapse buttons still appear, just positioned differently

### Compatible Extensions

- ✅ sphinx-design
- ✅ myst-parser
- ✅ sphinxcontrib.mermaid
- ✅ sphinx.ext.autodoc
- ⚠️ Custom JavaScript extensions (test for conflicts)

---

## Customization

### Change Animation Duration

**Edit:** `code-collapse.js` (line 23)

```javascript
const CONFIG = {
    animationDuration: 500, // Change from 350 to 500ms
    // ...
};
```

**Rebuild:** `sphinx-build -b html . _build/html`

### Change Button Icons

**Edit:** `code-collapse.js` (lines 25-26)

```javascript
const CONFIG = {
    expandedIcon: '➖',  // Unicode character
    collapsedIcon: '➕',
    // ...
};
```

Find Unicode icons: https://unicode-table.com/

### Change Button Styling

**Edit:** `code-collapse.css` (line 65-80)

```css
.code-collapse-btn {
    opacity: 0.5;  /* Change from 0.3 */
    color: #0066cc;  /* Add color */
    /* ... */
}
```

### Change Master Control Colors

**Edit:** `code-collapse.css` (line 10-21)

```css
.code-controls-master {
    background: linear-gradient(135deg, #your-color-1, #your-color-2);
    border: 2px solid #your-border-color;
    /* ... */
}
```

---

## Advanced Configuration

### Add Custom Code Block Selector

If your documentation uses custom code block classes:

**Edit:** `code-collapse.js` (lines 44-50)

```javascript
const selectors = [
    'div.notranslate[class*="highlight-"]',
    'div[class*="highlight-"]:not(.nohighlight)',
    'div.doctest',
    'div.literal-block',
    'div.code-block',
    'pre.literal-block',
    'div.my-custom-code-class',  // Add your selector here
];
```

### Change LocalStorage Key

To avoid conflicts with other JavaScript on your site:

**Edit:** `code-collapse.js` (line 22)

```javascript
const CONFIG = {
    storageKey: 'my-site-code-states',  // Change key name
    // ...
};
```

### Disable State Persistence

To make collapsed state not persist across page reloads:

**Edit:** `code-collapse.js` (comment out lines 440-445)

```javascript
function saveStates() {
    // Commented out to disable persistence
    // try {
    //     localStorage.setItem(CONFIG.storageKey, JSON.stringify(codeBlockStates));
    // } catch (e) {
    //     console.warn('Failed to save code block states:', e);
    // }
}
```

---

## Troubleshooting Integration

### Issue:

Buttons Not Appearing

**Check 1:** Verify files exist
```bash
ls -la your-project/docs/_static/code-collapse.*
```

**Check 2:** Verify conf.py includes files
```bash
grep "code-collapse" your-project/docs/conf.py
```

**Check 3:** Check browser console for errors
```
F12 → Console tab
Look for red error messages
```

### Issue:

Buttons Overlap Copy Button

**Cause:** sphinx-copybutton not loaded or different version

**Fix:** Adjust spacing in CSS (line 104-106)
```css
.copybtn + .code-collapse-btn {
    margin-left: 15px;  /* Increase gap */
}
```

### Issue:

Animation Doesn't Work

**Cause:** Browser doesn't support CSS features

**Check:** Browser version meets minimum requirements
- Chrome 90+, Firefox 88+, Edge 90+, Safari 14+

**Fix:** Update browser or disable animations (remove transition CSS)

---

## Deployment

### Static Hosting (GitHub Pages, Netlify, etc.)

**No special configuration needed.** Files are static JavaScript/CSS.

**Verify deployment:**
```bash
# Check files are uploaded
curl https://your-docs-site.com/_static/code-collapse.js
curl https://your-docs-site.com/_static/code-collapse.css
```

### CDN Deployment

If using a CDN (Cloudflare, Fastly):

1. After updating files, purge CDN cache for `_static/*`
2. Wait 5 minutes for cache propagation
3. Test with hard refresh (Ctrl+Shift+R)

### Read the Docs

**Works automatically** if files are in `_static/` and conf.py is configured.

RTD builds with sphinx-build, so no special steps needed.

---

## Testing Your Integration

### Quick Smoke Test (2 minutes)

```bash
# 1. Rebuild
sphinx-build -b html docs docs/_build/html

# 2.

Open in browser
open docs/_build/html/index.html  # Mac
start docs/_build/html/index.html  # Windows

# 3.

Check console
# Should see: [CodeCollapse] ✅ 100% coverage

# 4. Test buttons
# Click collapse (▼) → code hides
# Click expand (▲) → code shows
```

### Comprehensive Test

Use the provided test suite: `../../testing/BROWSER_TESTING_CHECKLIST.md`

Run in Chrome, Firefox, and Edge for full compatibility validation.

---

## Performance Considerations

### File Sizes

- **code-collapse.js**: 21KB (unminified)
- **code-collapse.css**: 8.9KB (unminified)
- **Total**: ~30KB added to your documentation

### Load Time Impact

- **Minimal** - Files load asynchronously
- **First page:** ~100ms additional load time
- **Subsequent pages:** Cached by browser (0ms)

### Runtime Performance

- **FPS:** 58-60 FPS during animations
- **Memory:** <100KB total (including state storage)
- **CPU:** Minimal impact (GPU-accelerated animations)

---

## Migration from Other Solutions

### If You Have Custom Code Folding

1. **Remove your custom solution** (JavaScript and CSS)
2. **Follow installation steps** above
3. **Test thoroughly** - behavior may differ
4. **Update any documentation** referencing old feature

### If You Use sphinx-togglebutton

**This feature is complementary** to sphinx-togglebutton:
- **sphinx-togglebutton**: Collapse arbitrary content (admonitions, etc.)
- **code-collapse**: Specifically for code blocks with better UX

You can use both together without conflicts.

---

## Getting Help

### Documentation

- **User Guide:** [user-guide.md](user-guide.md)
- **Configuration Reference:** [configuration-reference.md](configuration-reference.md)
- **Troubleshooting:** [troubleshooting.md](troubleshooting.md)
- **Technical Reference:** [technical-reference.md](technical-reference.md)

### Support Channels

- **GitHub Issues:** [link to repository]
- **Testing Guide:** `../../testing/TESTING_PROCEDURES.md`

---

## Example Projects Using This Feature

1. **This documentation** (DIP_SMC_PSO) - Live example
2. *Add your project here after integration!*

---

**Happy integrating!** 🚀
