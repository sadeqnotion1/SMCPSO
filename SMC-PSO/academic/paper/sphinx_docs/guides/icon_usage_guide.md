# Icon Usage Guide

**Purpose**: Reference for using the standardized SVG icon system in documentation
**Resolution**: UI-029 (Icon system deployment)
**Last Updated**: 2025-10-16

---

## Available Icons

### Status Icons

Located in `docs/_static/icons/status/`

| Visual | File | Purpose | Example Use Case |
|--------|------|---------|------------------|
| ![check](../_static/icons/status/check.svg) | `check.svg` | Success, passed, confirmed | Requirements checklist |
| ![x-mark](../_static/icons/status/x-mark.svg) | `x-mark.svg` | Failed, error, blocked | Test failures, invalid states |
| ![warning](../_static/icons/status/warning.svg) | `warning.svg` | Warning, caution | Configuration notes, deprecations |
| ![info](../_static/icons/status/info.svg) | `info.svg` | Information, note | Optional features, tips |

### Navigation Icons

Located in `docs/_static/icons/navigation/`

| Visual | File | Purpose | Example Use Case |
|--------|------|---------|------------------|
| ![arrow-right](../_static/icons/navigation/arrow-right.svg) | `arrow-right.svg` | Next, forward, proceed | Workflow steps, navigation |
| ![arrow-left](../_static/icons/navigation/arrow-left.svg) | `arrow-left.svg` | Previous, back, return | Back references, prerequisites |
| ![arrow-down](../_static/icons/navigation/arrow-down.svg) | `arrow-down.svg` | Expand, details, subsection | Collapsible sections, dropdowns |

---

## Usage in Markdown

### Standard Syntax (Recommended)

Use markdown image syntax with relative paths:

```markdown
![check](../_static/icons/status/check.svg)
```

**Advantages**:
- Simple, readable markdown
- Works in all markdown renderers
- Accessible by default (alt text)
- No custom CSS required

**Example**:

```markdown
## Prerequisites

- ![check](../_static/icons/status/check.svg) Python 3.9+
- ![check](../_static/icons/status/check.svg) NumPy 1.21+
- ![info](../_static/icons/status/info.svg) Optional: CUDA GPU
```bash

### HTML Syntax (Advanced)

For custom styling or CSS classes:

```html
<img src="../_static/icons/status/check.svg" alt="check" class="icon icon-success" />
```

**Use when**:
- Custom sizing required (`.icon-sm`, `.icon-lg`)
- Color overrides needed (`.icon-success`, `.icon-danger`)
- Inline with specific text styling

**Example**:

```html
<p>Status: <img src="../_static/icons/status/check.svg" alt="Passed" class="icon icon-success" /> Tests passed</p>
```bash

### Inline SVG (Rare)

For maximum control or animation:

```html
<svg class="icon icon-warning" aria-label="Warning">
  <use href="../_static/icons/status/warning.svg#icon"></use>
</svg>
```

**Use only when**:
- CSS animations required
- Dynamic color changes via JavaScript
- Embedding in complex layouts

---

## CSS Styling

All icons support these CSS classes (defined in `docs/_static/custom.css`):

### Size Classes

```css
.icon       /* Default: 1em × 1em (matches text height) */
.icon-sm    /* Small: 0.875em × 0.875em */
.icon-lg    /* Large: 1.25em × 1.25em */
```

**Example**:

```html
<img src="../_static/icons/status/check.svg" class="icon icon-lg" alt="check" />
```

### Color Classes

```css
.icon-success   /* Green (#059669) - Success, pass */
.icon-danger    /* Red (#dc2626) - Error, fail */
.icon-warning   /* Orange (#d97706) - Warning, caution */
.icon-info      /* Blue (#2563eb) - Info, note */
.icon-primary   /* Primary blue - Navigation */
```

**Example**:

```html
<img src="../_static/icons/status/check.svg" class="icon icon-success" alt="check" />
```

---

## Common Use Cases

### Requirements Checklist

```markdown
## Prerequisites

- ![check](../_static/icons/status/check.svg) Python 3.9+
- ![check](../_static/icons/status/check.svg) Git installed
- ![check](../_static/icons/status/check.svg) 10 GB disk space
- ![info](../_static/icons/status/info.svg) Optional: GPU
```

### Performance Metrics Table

```markdown
| Metric | Formula | Lower is Better |
|--------|---------|-----------------|
| ISE | ∫‖x‖² dt | ![check](../_static/icons/status/check.svg) |
| ITAE | ∫t·‖x‖ dt | ![check](../_static/icons/status/check.svg) |
```

### Step-by-Step Workflows

```markdown
1. Install dependencies ![arrow-right](../_static/icons/navigation/arrow-right.svg) 2. Configure settings
2. Configure settings ![arrow-right](../_static/icons/navigation/arrow-right.svg) 3. Run simulation
3. Run simulation ![arrow-right](../_static/icons/navigation/arrow-right.svg) 4. Analyze results
```

### Warning Callouts

```markdown
![warning](../_static/icons/status/warning.svg) **Warning**: This configuration may cause instability.
```

### Status Indicators

```markdown
- ![check](../_static/icons/status/check.svg) Tests passing (95% coverage)
- ![x-mark](../_static/icons/status/x-mark.svg) Linting failed (23 issues)
- ![warning](../_static/icons/status/warning.svg) Documentation incomplete (3 files)
```

---

## Design Tokens Integration

Icons use colors from the design token system:

```css
/* From docs/_static/design-tokens.css */
--color-success: #059669;  /* Green (check icons) */
--color-danger: #dc2626;   /* Red (x-mark icons) */
--color-warning: #d97706;  /* Orange (warning icons) */
--color-info: #2563eb;     /* Blue (info icons) */
--color-primary: #2563eb;  /* Blue (navigation icons) */
```

**Color Guidelines**:
- **Success (Green)**: Positive states, passed tests, confirmed actions
- **Danger (Red)**: Errors, failures, critical warnings
- **Warning (Orange)**: Cautions, deprecations, advisories
- **Info (Blue)**: Neutral information, tips, optional features
- **Primary (Blue)**: Navigation, links, interactive elements

---

## Accessibility Requirements

All icon usage must follow WCAG 2.1 Level AA:

### Alt Text

Always provide descriptive alt text:

```markdown
![check](../_static/icons/status/check.svg)  <!-- Alt text: "check" -->
```bash

For HTML:

```html
<img src="../_static/icons/status/check.svg" alt="Success" />
```

### Contrast Ratio

Ensure minimum 3:1 contrast between icon color and background:

- **Success green (#059669)** on white: 4.5:1 ✓
- **Danger red (#dc2626)** on white: 5.2:1 ✓
- **Warning orange (#d97706)** on white: 4.1:1 ✓
- **Info blue (#2563eb)** on white: 6.3:1 ✓

### Decorative vs Semantic

**Semantic icons** (convey information):
- Use meaningful alt text
- Include in reading order

**Decorative icons** (visual enhancement only):
- Use empty alt: `alt=""`
- Add `aria-hidden="true"`

---

## Migration from Unicode

Replace Unicode symbols with SVG icons:

| Old (Unicode) | New (SVG) | Usage |
|---------------|-----------|-------|
| ✓ | `![check](../_static/icons/status/check.svg)` | Success |
| ✗ | `![x-mark](../_static/icons/status/x-mark.svg)` | Error |
| ⚠️ | `![warning](../_static/icons/status/warning.svg)` | Warning |
| ℹ️ | `![info](../_static/icons/status/info.svg)` | Info |
| → | `![arrow-right](../_static/icons/navigation/arrow-right.svg)` | Next |
| ← | `![arrow-left](../_static/icons/navigation/arrow-left.svg)` | Previous |
| ↓ | `![arrow-down](../_static/icons/navigation/arrow-down.svg)` | Expand |

**Automated replacement** (review before committing):

```bash
# Replace checkmarks in markdown files
find docs/guides -name "*.md" -exec sed -i 's/✓/![check](..\/\\_static\/icons\/status\/check.svg)/g' {} +

# Replace x-marks
find docs/guides -name "*.md" -exec sed -i 's/✗/![x-mark](..\/\\_static\/icons\/status\/x-mark.svg)/g' {} +

# Replace warnings
find docs/guides -name "*.md" -exec sed -i 's/⚠️/![warning](..\/\\_static\/icons\/status\/warning.svg)/g' {} +
```

---

## Browser Support

SVG icons work in all modern browsers:

- Chrome 90+ ![check](../_static/icons/status/check.svg)
- Firefox 88+ ![check](../_static/icons/status/check.svg)
- Safari 14+ ![check](../_static/icons/status/check.svg)
- Edge 90+ ![check](../_static/icons/status/check.svg)

**Fallback**: Browsers without SVG support (IE11) display alt text.

---

## Performance Impact

**File Sizes**:
- Per icon: 250-400 bytes (optimized SVG)
- Total library (7 icons): ~2.5 KB
- Gzipped: ~1 KB

**Page Load**:
- Icons load asynchronously with page
- No JavaScript required
- Cached after first load
- Negligible impact on performance

---

## Adding New Icons

Follow this process to add icons to the library:

### 1. Design Icon

Create 24×24 SVG with Heroicons-style outline:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round"
     role="img" aria-label="Icon description">
  <!-- SVG paths here -->
</svg>
```yaml

### 2. Optimize

Use [SVGOMG](https://jakearchibald.github.io/svgomg/) with these settings:
- Precision: 2
- Remove viewBox: NO
- Remove xmlns: NO
- Prefer viewBox: YES

### 3. Save to Directory

```bash
# Status icons
docs/_static/icons/status/new-icon.svg

# Navigation icons
docs/_static/icons/navigation/new-icon.svg

# Action icons (if needed)
docs/_static/icons/actions/new-icon.svg
```

### 4. Update Documentation

Add icon to:
- `docs/_static/icons/README.md` (icon library reference)
- This file (`docs/guides/icon_usage_guide.md`) (usage examples)

### 5. Test Rendering

Build Sphinx documentation and verify:

```bash
sphinx-build -M html docs docs/_build
# Check: docs/_build/html/guides/icon_usage_guide.html
```

---

## Troubleshooting

### Icon Not Displaying

**Symptom**: Broken image icon or empty space

**Causes & Solutions**:
1. **Incorrect path**: Use `../_static/` not `/_static/` in guides
2. **Missing file**: Verify icon exists in `docs/_static/icons/`
3. **Build issue**: Rebuild Sphinx docs: `sphinx-build -M html docs docs/_build`
4. **Browser cache**: Hard refresh (Ctrl+Shift+R)

### Icon Too Large/Small

**Symptom**: Icon doesn't match text size

**Solution**: Add `.icon` class for 1em sizing:

```html
<img src="../_static/icons/status/check.svg" class="icon" alt="check" />
```

### Wrong Icon Color

**Symptom**: Icon displays in wrong color

**Solution**: Add color class:

```html
<img src="../_static/icons/status/check.svg" class="icon icon-success" alt="check" />
```

### Icon Not Accessible

**Symptom**: Screen reader doesn't announce icon

**Solution**: Ensure meaningful alt text:

```markdown
![Success - all tests passed](../_static/icons/status/check.svg)
```

---

## Best Practices

1. **Consistency**: Use the same icon for the same meaning across all documentation
2. **Accessibility**: Always provide alt text or aria-label
3. **Performance**: Use standard markdown syntax (not inline SVG) for better caching
4. **Semantics**: Use semantic color classes (`.icon-success`, not custom colors)
5. **Contrast**: Verify 3:1 minimum contrast ratio for readability
6. **Sizing**: Default `.icon` class matches text; use `.icon-lg` sparingly for emphasis
7. **Context**: Pair icons with text (not standalone) for clarity

---

## References

- Icon library README: `docs/_static/icons/README.md`
- Custom CSS: `docs/_static/custom.css`
- Design tokens: `docs/_static/design-tokens.css`
- Phase 3 icon audit: `.codex/phase3/icon_audit_ui029.md`
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/

---

**Last Updated**: 2025-10-16
**Framework Version**: 1.0
