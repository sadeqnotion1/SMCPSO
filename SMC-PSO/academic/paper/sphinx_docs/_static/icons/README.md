# Icon System (UI-029)

**Purpose**: Standardized SVG icon library for documentation
**Style**: Heroicons-inspired (24x24 outline icons)
**License**: MIT-compatible
**Created**: 2025-10-16

---

## Available Icons

### Status Icons (`docs/_static/icons/status/`)

| Icon | File | Usage | Color Class |
|------|------|-------|-------------|
| ✓ | `check.svg` | Success, passed, confirmed | `.icon-success` (green) |
| ✗ | `x-mark.svg` | Failed, error, blocked | `.icon-danger` (red) |
| ⚠ | `warning.svg` | Warning, caution | `.icon-warning` (orange) |
| ℹ | `info.svg` | Information, note | `.icon-info` (blue) |

### Navigation Icons (`docs/_static/icons/navigation/`)

| Icon | File | Usage | Color Class |
|------|------|-------|-------------|
| → | `arrow-right.svg` | Next step, forward | `.icon-primary` |
| ← | `arrow-left.svg` | Previous step, back | `.icon-primary` |
| ↓ | `arrow-down.svg` | Expand, more details | `.icon-primary` |

---

## Usage in Markdown

### Method 1: Inline Image (Simplest)

```markdown
![check](/_static/icons/status/check.svg){.icon .icon-success}
```

### Method 2: HTML (More Control)

```html
<img src="/_static/icons/status/check.svg" class="icon icon-success" alt="Success" />
```

### Method 3: Raw SVG (Best Accessibility)

```html
<svg class="icon icon-success" aria-label="Success">
  <use href="/_static/icons/status/check.svg#icon"></use>
</svg>
```

---

## CSS Classes

All icons use classes from `docs/_static/custom.css`:

```css
.icon                 /* Base icon styling (1em × 1em) */
.icon-sm              /* Small (0.875em) */
.icon-lg              /* Large (1.25em) */

.icon-success         /* Green (#059669) */
.icon-danger          /* Red (#dc2626) */
.icon-warning         /* Orange (#d97706) */
.icon-info            /* Blue (#2563eb) */
.icon-primary         /* Primary blue */
```

---

## Example: Performance Metrics Table

**Before**:
```markdown
| Metric | Formula | Lower is Better |
|--------|---------|-----------------|
| ISE    | ∫‖x‖² dt | ✓ |
```

**After**:
```markdown
| Metric | Formula | Lower is Better |
|--------|---------|-----------------|
| ISE    | ∫‖x‖² dt | ![check](/_static/icons/status/check.svg){.icon .icon-success} |
```

---

## Accessibility

All SVG icons include:
- `role="img"` - Identifies as image for screen readers
- `aria-label="..."` - Provides text alternative
- `stroke="currentColor"` - Inherits text color for contrast
- Minimum 3:1 contrast ratio (verified with design tokens)

---

## Browser Support

- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅
- All modern browsers with SVG support

---

## File Size

- **Per icon**: ~250-400 bytes (optimized SVG)
- **Total (7 icons)**: ~2.5 KB
- **Gzipped**: ~1 KB (negligible overhead)

---

## Migration Guide

### Unicode → SVG Replacement Map

| Old (Unicode) | New (SVG) | Class |
|---------------|-----------|-------|
| ✓ | `check.svg` | `.icon-success` |
| ✗ | `x-mark.svg` | `.icon-danger` |
| ⚠️ | `warning.svg` | `.icon-warning` |
| ℹ️ | `info.svg` | `.icon-info` |
| → | `arrow-right.svg` | `.icon-primary` |
| ← | `arrow-left.svg` | `.icon-primary` |
| ↓ | `arrow-down.svg` | `.icon-primary` |

### Sed Command for Batch Replacement

```bash
# Replace ✓ with SVG check icon in all markdown files
find docs/guides -name "*.md" -exec sed -i 's/✓/![check](\/_static\/icons\/status\/check.svg){.icon .icon-success}/g' {} +
```

**Warning**: Review changes manually before committing!

---

## Adding New Icons

1. **Create SVG** with 24×24 viewBox:
   ```xml
   <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"
        role="img" aria-label="Icon name">
     <!-- SVG path here -->
   </svg>
   ```

2. **Optimize** with [SVGOMG](https://jakearchibald.github.io/svgomg/)

3. **Save** to appropriate subdirectory:
   - `status/` - Checkmarks, alerts, status indicators
   - `navigation/` - Arrows, directional elements
   - `actions/` - Interactive buttons (search, settings, etc.)

4. **Update** this README with icon details

5. **Test** icon renders correctly in Sphinx build

---

## License

Icons based on Heroicons design language (MIT License).
Compatible with project's academic/research license.

**Last Updated**: 2025-10-16
