# Streamlit Theme Integration Guide

**What This Workflow Covers:**
This guide shows how to integrate the DIP documentation theme into Streamlit applications using a token-driven theming system. You'll learn to achieve visual parity between Sphinx docs and Streamlit apps, customize design tokens (colors, spacing, typography), and maintain WCAG AA accessibility across both platforms.

**Who This Is For:**
- Streamlit developers building companion apps for technical documentation
- UI/UX designers maintaining visual consistency across platforms
- Documentation teams wanting matching Streamlit demos
- Anyone needing professional, accessible Streamlit themes

**What You'll Learn:**
- Integrating the token-based theme system (one function call)
- Customizing design tokens (colors, spacing, shadows, typography)
- Achieving visual parity between Sphinx docs and Streamlit UI
- Performance optimization (<3KB gzipped CSS)
- WCAG AA accessibility validation

**Version**: 2.0.0 | **Last Updated**: 2025-10-16

---

## Overview

The DIP Streamlit theme provides visual parity with Sphinx documentation by using a token-driven theming system. This guide shows how to integrate the theme into new projects or customize it for specific needs.

**Key Features:**
- Token-based design system (colors, spacing, typography, shadows)
- Automatic CSS generation from JSON tokens
- Scoped styling (no global conflicts)
- WCAG AA accessible
- Performance-optimized (<3KB gzipped)

---

## Quick Start

### 1. Copy Required Files

```bash
# From dip-smc-pso project root:
cp src/utils/streamlit_theme.py YOUR_PROJECT/src/utils/
cp .codex/phase2_audit/design_tokens_v2.json YOUR_PROJECT/config/
```

### 2. Add to Streamlit App

```python
# YOUR_PROJECT/app.py
import streamlit as st
from src.utils.streamlit_theme import inject_theme

# Apply theme BEFORE any st. calls
inject_theme(enable=True)

# Your Streamlit app code
st.title("My Application")
st.button("Click Me")
```

### 3. Verify Theme Applied

Run Streamlit and check browser DevTools:
```bash
streamlit run app.py
```

Inspect element → Should see:
```html
<div data-theme="dip-docs">
  <!-- Your app content with themed CSS -->
</div>
```

---

## Integration Methods

### Method 1: Direct Integration (Recommended)

**Use case**: Full theme with all design tokens

**Setup:**
```python
# app.py
from src.utils.streamlit_theme import inject_theme

inject_theme(enable=True)  # Uses default token path
```

**Pros:**
- Easiest setup
- Full feature set
- Automatic updates if tokens change

**Cons:**
- Requires token JSON file
- Larger CSS footprint

---

### Method 2: Custom Token Path

**Use case**: Multiple environments (dev, staging, prod) with different themes

**Setup:**
```python
# app.py
from src.utils.streamlit_theme import inject_theme
from pathlib import Path

# Point to your custom token file
custom_tokens = Path("config/my_tokens.json")
inject_theme(enable=True, token_path=custom_tokens)
```

**Token file structure:**
```json
{
  "colors": {
    "primary": {"value": "#2563eb"},
    "primary-hover": {"value": "#0b2763"},
    "text-primary": {"value": "#111827"}
  },
  "spacing": {
    "spacing-2": {"value": "8px"},
    "spacing-3": {"value": "12px"}
  }
  // ... etc
}
```

---

### Method 3: Programmatic Theme Generation

**Use case**: Dynamic themes generated at runtime

**Setup:**
```python
# app.py
import streamlit as st
from src.utils.streamlit_theme import generate_theme_css

# Custom token dict
custom_tokens = {
    "colors": {
        "primary": {"value": "#ff5733"},  # Custom brand color
        "text-primary": {"value": "#111827"}
    },
    "spacing": {
        "spacing-2": {"value": "8px"}
    }
    # Add all required tokens...
}

# Generate CSS from custom tokens
css = generate_theme_css(custom_tokens)

# Inject manually
st.markdown(f"""
<style>
{css}
</style>
<div data-theme="dip-docs">
""", unsafe_allow_html=True)

# Your app code...

st.markdown('</div>', unsafe_allow_html=True)  # Close wrapper
```

---

### Method 4: Config-Driven Toggle

**Use case**: Allow users to enable/disable theme via config

**Setup:**
```python
# config.yaml
streamlit:
  enable_dip_theme: true  # User can toggle

# app.py
import yaml
from pathlib import Path
from src.utils.streamlit_theme import inject_theme

# Load config
config = yaml.safe_load(Path("config.yaml").read_text())
theme_enabled = config.get("streamlit", {}).get("enable_dip_theme", False)

# Apply conditionally
inject_theme(enable=theme_enabled)
```

**Benefits:**
- Easy A/B testing
- User preference support
- Environment-specific themes

---

## Customization Guide

### Customizing Colors

**1. Copy design tokens:**
```bash
cp .codex/phase2_audit/design_tokens_v2.json config/my_tokens.json
```

**2. Edit color values:**
```json
{
  "colors": {
    "primary": {
      "value": "#ff5733",  // Your brand color
      "description": "Primary action color"
    },
    "primary-hover": {
      "value": "#cc3300",  // Darker hover state
      "description": "Primary hover state"
    },
    "text-primary": {
      "value": "#1a1a1a",  // Adjust text darkness
      "description": "Primary text color"
    }
  }
}
```

**3. Update app to use custom tokens:**
```python
inject_theme(enable=True, token_path=Path("config/my_tokens.json"))
```

**4. Verify contrast ratios:**
Use browser DevTools accessibility panel to ensure ≥4.5:1 contrast for WCAG AA compliance.

---

### Customizing Spacing

**Scale Options:**
```json
{
  "spacing": {
    "spacing-1": {"value": "4px"},   // Compact UI
    "spacing-2": {"value": "8px"},   // Default
    "spacing-3": {"value": "12px"},  // Comfortable
    "spacing-4": {"value": "16px"},  // Spacious
    "spacing-5": {"value": "24px"}   // Extra spacious
  }
}
```

**Use Cases:**
- **spacing-1/2**: Dense dashboards with many widgets
- **spacing-3/4**: Standard business apps
- **spacing-4/5**: Content-focused presentations

---

### Customizing Typography

**Font Stack Options:**
```json
{
  "typography": {
    "font-family-body": {
      "value": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    },
    "font-family-mono": {
      "value": "'Fira Code', 'Cascadia Code', Consolas, Monaco, 'Courier New', monospace"
    }
  }
}
```

**Custom Font Example:**
```json
{
  "typography": {
    "font-family-body": {
      "value": "'Inter', -apple-system, sans-serif"
    }
  }
}
```

**Include font:**
```python
# app.py
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
</style>
""", unsafe_allow_html=True)

inject_theme(enable=True)  # Uses custom tokens with Inter font
```

---

### Adding Custom Widgets

**1. Extend CSS template:**
```python
# custom_theme.py
from src.utils.streamlit_theme import load_design_tokens, generate_theme_css

def generate_custom_css(tokens: dict) -> str:
    """Generate CSS with custom widget styles."""
    base_css = generate_theme_css(tokens)

    # Add custom styles
    custom_rules = """
    [data-theme="dip-docs"] .stAlert {
        border-left: 4px solid var(--dip-primary);
        background-color: rgba(37, 99, 235, 0.05);
    }

    [data-theme="dip-docs"] .stDataFrame {
        border: 1px solid var(--dip-border);
        border-radius: var(--dip-radius-md);
    }
    """

    return base_css + custom_rules

# Use in app
tokens = load_design_tokens()
css = generate_custom_css(tokens)
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

**2. Target Streamlit widgets:**

Common selectors:
```css
/* Buttons */
.stButton > button { ... }

/* Text inputs */
.stTextInput > div > div > input { ... }

/* Selectboxes */
.stSelectbox > div > div { ... }

/* Metrics */
div[data-testid="stMetric"] { ... }

/* Sidebar */
section[data-testid="stSidebar"] { ... }

/* Tabs */
div[data-testid="stTabs"] button { ... }
```

**Find selectors:**
1. Open browser DevTools (F12)
2. Click element picker (Ctrl+Shift+C)
3. Click widget
4. Copy selector from Elements panel

---

## Advanced Customization

### Creating Theme Variants

**Use case**: Light/dark mode, seasonal themes, brand variations

**Structure:**
```
config/
├── tokens/
│   ├── base.json          # Shared tokens
│   ├── light.json         # Light theme overrides
│   ├── dark.json          # Dark theme overrides
│   └── brand_blue.json    # Brand variant
```

**Implementation:**
```python
# theme_manager.py
import json
from pathlib import Path
from src.utils.streamlit_theme import generate_theme_css

def load_theme_variant(base_path: Path, variant: str) -> dict:
    """Load base tokens + variant overrides."""
    base = json.loads(base_path.read_text())

    variant_path = base_path.parent / f"{variant}.json"
    if variant_path.exists():
        overrides = json.loads(variant_path.read_text())
        # Merge overrides into base (deep merge)
        return {**base, **overrides}

    return base

# app.py
import streamlit as st

# User selects theme
theme_variant = st.sidebar.selectbox("Theme", ["light", "dark", "brand_blue"])

# Load and apply
tokens = load_theme_variant(Path("config/tokens/base.json"), theme_variant)
css = generate_theme_css(tokens)
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

---

### Performance Optimization

**1. Minify CSS:**
```python
import re

def minify_css(css: str) -> str:
    """Remove unnecessary whitespace from CSS."""
    # Remove comments
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    # Remove excess whitespace
    css = re.sub(r'\s+', ' ', css)
    # Remove spaces around special chars
    css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
    return css.strip()

# Use in app
css = generate_theme_css(tokens)
css_min = minify_css(css)
st.markdown(f"<style>{css_min}</style>", unsafe_allow_html=True)
```

**2. Cache CSS generation:**
```python
import streamlit as st
from src.utils.streamlit_theme import load_design_tokens, generate_theme_css

@st.cache_data
def get_cached_css() -> str:
    """Generate CSS once per session."""
    tokens = load_design_tokens()
    return generate_theme_css(tokens)

# App code
css = get_cached_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

**3. Conditional loading:**
```python
# Only load theme on certain pages
import streamlit as st

def should_load_theme() -> bool:
    """Load theme only on public-facing pages."""
    # Check query params
    params = st.experimental_get_query_params()
    return params.get("theme", ["true"])[0] == "true"

if should_load_theme():
    inject_theme(enable=True)
```

---

## Best Practices

### 1. Theme Initialization Timing

**DO:**
```python
# app.py
import streamlit as st
from src.utils.streamlit_theme import inject_theme

# FIRST: Apply theme before any st. calls
inject_theme(enable=True)

# THEN: Your app content
st.title("My App")
st.button("Click")
```

**DON'T:**
```python
# BAD: Theme after content
st.title("My App")  # Already rendered without theme
inject_theme(enable=True)  # Too late
```

---

### 2. Design Token Structure

**DO:**
```json
{
  "colors": {
    "primary": {
      "value": "#2563eb",
      "description": "Primary brand color for CTAs"
    }
  }
}
```

**DON'T:**
```json
{
  "button-color": "#2563eb"  // Not structured, hard to maintain
}
```

---

### 3. CSS Specificity

**DO:**
```css
/* Scoped to theme wrapper */
[data-theme="dip-docs"] .stButton > button {
  background-color: var(--dip-primary);
}
```

**DON'T:**
```css
/* Global override - conflicts with other styles */
button {
  background-color: blue;
}
```

---

### 4. Accessibility Validation

**Always validate contrast ratios:**
```bash
# After customizing colors
cd .codex/phase3/validation/streamlit
python wave3_axe_audit.py
```

**Minimum contrast ratios (WCAG AA):**
- Normal text: 4.5:1
- Large text (18pt+): 3:1
- UI components: 3:1

---

### 5. Version Control

**Track token changes:**
```bash
# config/tokens/CHANGELOG.md
## [2.0.1] - 2025-10-20
### Changed
- Increased primary button contrast from #2563eb to #1d4ed8
- Adjusted spacing-3 from 12px to 14px for better touch targets
```

**Use semantic versioning:**
- **Major**: Breaking changes (token structure changes)
- **Minor**: New tokens added
- **Patch**: Value adjustments (color tweaks)

---

## Troubleshooting

### Issue: Theme not applying

**Symptoms:**
- Widgets look like default Streamlit
- No custom colors/spacing

**Diagnosis:**
```python
# Add debug logging
from src.utils.streamlit_theme import inject_theme
import streamlit as st

st.write("Theme injection starting...")
inject_theme(enable=True)
st.write("Theme injection complete")
```

**Solutions:**
1. Check `inject_theme()` called before widgets
2. Verify token file exists at specified path
3. Check browser console for CSS errors (F12)
4. Hard refresh browser (Ctrl+Shift+R)

---

### Issue: Custom colors not showing

**Symptoms:**
- Some colors work, others don't
- CSS variables undefined

**Diagnosis:**
```javascript
// Browser console
console.log(getComputedStyle(document.documentElement).getPropertyValue('--dip-primary'));
// Should output: "#2563eb"
```

**Solutions:**
1. Verify token structure matches expected format
2. Check CSS generation includes your custom colors
3. Ensure color values are valid CSS (hex, rgb, rgba)

---

### Issue: Performance degradation

**Symptoms:**
- Slow page loads
- Large CSS size
- Browser lag

**Diagnosis:**
```bash
# Measure CSS size
cd .codex/phase3/validation/streamlit
python wave3_performance.py
```

**Solutions:**
1. Remove unused CSS rules
2. Minify CSS (see Performance Optimization section)
3. Cache CSS generation with `@st.cache_data`
4. Use CSS shorthand properties

---

### Issue: Accessibility violations

**Symptoms:**
- axe audit fails
- Low contrast warnings

**Diagnosis:**
```bash
# Run accessibility audit
cd .codex/phase3/validation/streamlit
python wave3_axe_audit.py
```

**Solutions:**
1. Adjust colors to meet 4.5:1 contrast ratio
2. Use browser DevTools Accessibility panel
3. Test with contrast checker: https://webaim.org/resources/contrastchecker/
4. Review `wave3/axe_audit_report.json` for specific issues

---

## Examples

### Example 1: Corporate Branding

```python
# app.py
import streamlit as st
from src.utils.streamlit_theme import inject_theme
from pathlib import Path

# Corporate blue theme
inject_theme(enable=True, token_path=Path("config/corporate_blue.json"))

st.title("Acme Corp Dashboard")
st.button("Generate Report")  # Uses corporate blue
```

```json
// config/corporate_blue.json
{
  "colors": {
    "primary": {"value": "#003d82"},        // Acme corporate blue
    "primary-hover": {"value": "#002452"},  // Darker blue
    "text-primary": {"value": "#1a1a1a"}
  }
}
```

---

### Example 2: High-Contrast Accessibility

```json
// config/high_contrast.json
{
  "colors": {
    "primary": {"value": "#0000ff"},        // Pure blue
    "text-primary": {"value": "#000000"},   // Pure black
    "bg-primary": {"value": "#ffffff"},     // Pure white
    "text-secondary": {"value": "#111111"}  // Nearly black
  }
}
```yaml

**Benefits:**
- 21:1 contrast ratio (AAA level)
- Accessible to users with low vision
- Compliant with strict accessibility requirements

---

### Example 3: Dark Mode

```json
// config/dark_mode.json
{
  "colors": {
    "primary": {"value": "#60a5fa"},        // Light blue (visible on dark)
    "text-primary": {"value": "#f3f4f6"},   // Light gray
    "text-secondary": {"value": "#d1d5db"},
    "bg-primary": {"value": "#1f2937"},     // Dark gray
    "bg-secondary": {"value": "#111827"},   // Darker gray
    "border": {"value": "#374151"}
  }
}
```

**Implementation:**
```python
# app.py
import streamlit as st
from pathlib import Path

mode = st.sidebar.radio("Mode", ["Light", "Dark"])
token_path = Path(f"config/{mode.lower()}_mode.json")

from src.utils.streamlit_theme import inject_theme
inject_theme(enable=True, token_path=token_path)
```

---

### Example 4: Seasonal Themes

```python
# app.py
import streamlit as st
from datetime import datetime
from pathlib import Path
from src.utils.streamlit_theme import inject_theme

def get_seasonal_theme() -> str:
    """Select theme based on current month."""
    month = datetime.now().month

    if month in [3, 4, 5]:
        return "spring"  # Pastel greens
    elif month in [6, 7, 8]:
        return "summer"  # Bright blues
    elif month in [9, 10, 11]:
        return "autumn"  # Warm oranges
    else:
        return "winter"  # Cool blues/grays

theme = get_seasonal_theme()
inject_theme(enable=True, token_path=Path(f"config/{theme}.json"))
```

---

## Testing Your Integration

### Unit Tests

```python
# tests/test_custom_theme.py
import pytest
from src.utils.streamlit_theme import load_design_tokens, generate_theme_css
from pathlib import Path

def test_custom_tokens_load():
    """Verify custom tokens load correctly."""
    tokens = load_design_tokens(Path("config/my_tokens.json"))

    assert "colors" in tokens
    assert "primary" in tokens["colors"]
    assert tokens["colors"]["primary"]["value"] == "#ff5733"

def test_custom_css_generation():
    """Verify CSS generates from custom tokens."""
    tokens = load_design_tokens(Path("config/my_tokens.json"))
    css = generate_theme_css(tokens)

    assert "--dip-primary: #ff5733" in css
    assert "data-theme=\"dip-docs\"" in css
```

### Visual Regression Testing

```bash
# Run full validation pipeline
cd .codex/phase3/validation/streamlit

# 1. Generate baseline (default theme)
python wave3_screenshot_capture.py baseline

# 2. Apply your custom theme and capture
# (Update config.yaml to use your theme)
python wave3_screenshot_capture.py themed

# 3. Compare
python wave3_visual_regression.py

# 4. Check results
cat wave3/visual_regression_summary.md
```

---

## Migration Guide

### From Streamlit's Built-in Theming

**Before (config.toml):**
```toml
[theme]
primaryColor = "#2563eb"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f3f4f6"
textColor = "#111827"
font = "sans serif"
```

**After (DIP theme):**
```python
# app.py
from src.utils.streamlit_theme import inject_theme
inject_theme(enable=True)

# Delete .streamlit/config.toml theme section
```

**Benefits:**
- Token-based design system (consistent across docs + app)
- More granular control (spacing, shadows, borders)
- Better performance (<3KB vs larger built-in theme)
- WCAG AA validated

---

## Resources

**Documentation:**
- Validation Pipeline: `.codex/phase3/validation/streamlit/wave3/VALIDATION_GUIDE.md`
- Theme Module: `src/utils/streamlit_theme.py`
- Design Tokens: `.codex/phase2_audit/design_tokens_v2.json`

**Tools:**
- Contrast Checker: https://webaim.org/resources/contrastchecker/
- Color Palette Generator: https://coolors.co/
- axe DevTools: https://www.deque.com/axe/devtools/

**Community:**
- GitHub Issues: https://github.com/theSadeQ/dip-smc-pso/issues
- Streamlit Forum: https://discuss.streamlit.io/

---

## Support

**Questions?**
- Check troubleshooting section above
- Review validation guide for common issues
- Open GitHub issue with `streamlit` tag

**Contributing:**
- Submit theme customization examples
- Report bugs in theme module
- Suggest new token categories

See CONTRIBUTING.md for contribution guidelines.
