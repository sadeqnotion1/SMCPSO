# Configuration Reference

**Last Updated:** 2025-10-12

---

## What This Page Covers

This reference guide explains every configuration option for the code-collapse feature. You'll learn how to customize the appearance, behavior, and performance of collapsible code blocks.

**Who This Is For:**
- Developers customizing the documentation theme
- Site administrators tuning performance settings
- Anyone wanting to understand available options

**What You Can Configure:**
- Animation speed and smoothness (how blocks expand/collapse)
- Button appearance and icons (what users see and click)
- Performance optimizations (GPU acceleration, memory usage)
- Browser compatibility settings (supporting older browsers)

**Quick Navigation:**
- [Basic Settings](#config-object-javascript) - Animation, icons, storage
- [Advanced Styling](#css-customization) - Colors, positioning, dark mode
- [Performance Tuning](#performance-settings) - GPU, memory optimization
- [Common Use Cases](#recommended-settings-by-use-case) - Pre-configured setups

---

## CONFIG Object (JavaScript)

The CONFIG object controls the core behavior of code block collapsing. These settings are located in `code-collapse.js` (lines 21-28). Each setting below includes its purpose and when you'd want to change it.

### storageKey

**What This Does:**
This setting controls where the browser remembers which code blocks you've collapsed. When you collapse a block and refresh the page, it stays collapsed because the state is saved in browser storage.

```javascript
storageKey: 'code-block-states'
```

**Technical Details:**
- **Type:** `string`
- **Default:** `'code-block-states'`
- **Purpose:** LocalStorage key name for saving collapse states

**When to Change:**
Change this if you're running multiple documentation sites on the same domain. Different keys prevent sites from interfering with each other's saved states.

**Example:**
```javascript
// For a second docs site on the same domain
storageKey: 'my-other-project-code-states'
```

### animationDuration

**What This Does:**
This controls how fast code blocks expand and collapse. The number represents milliseconds (1000 = 1 second). The animation makes the transition smooth instead of instant.

```javascript
animationDuration: 350
```

**Technical Details:**
- **Type:** `number` (milliseconds)
- **Default:** `350` (about one-third of a second)
- **Valid Range:** 100-1000ms

**Finding the Right Speed:**
- **Too fast (100-200ms):** Feels jarring and abrupt
- **Just right (300-500ms):** Smooth and natural (recommended)
- **Too slow (700-1000ms):** Feels sluggish and annoying

**When to Change:**
Adjust this based on your site's overall feel. Fast-paced sites may prefer 250ms. Documentation-heavy sites might prefer 400ms for a calmer experience.

**Examples:**
```javascript
animationDuration: 250  // Snappy, modern feel
animationDuration: 350  // Default, balanced
animationDuration: 500  // Relaxed, deliberate
```

### easing

**What This Does:**
This controls the "feel" of the animation - whether it moves at constant speed, accelerates, or has special effects like bouncing. Think of it like choosing between an elevator that starts/stops smoothly versus one that moves at constant speed.

```javascript
easing: 'cubic-bezier(0.4, 0.0, 0.2, 1)'
```

**Technical Details:**
- **Type:** `string` (CSS timing function)
- **Default:** `'cubic-bezier(0.4, 0.0, 0.2, 1)'` (Material Design standard)

**Common Options:**
- `'linear'` - Constant speed (robotic feel)
- `'ease-in-out'` - Slow start and end (smooth and natural)
- `'cubic-bezier(0.4, 0.0, 0.2, 1)'` - Material Design (professional feel)
- `'cubic-bezier(0.68, -0.55, 0.265, 1.55)'` - Bounce effect (playful feel)

**Visualization Tool:**
Use https://cubic-bezier.com to preview and create custom easing curves.

**When to Change:**
Choose based on your site's personality. Corporate sites use Material Design. Fun sites might use bounce. Minimalist sites prefer linear.

---

### expandedIcon

**What This Does:**
This is the symbol shown on the button when a code block is currently expanded (visible). It suggests "click me to collapse."

```javascript
expandedIcon: '▼'
```

**Technical Details:**
- **Type:** `string` (Unicode character or emoji)
- **Default:** `'▼'` (down-pointing triangle)

**Popular Alternatives:**
- `'➖'` (minus sign - like closing an accordion)
- `'[-]'` (ASCII minus in brackets)
- `'🔽'` (emoji down arrow)

**Design Tip:**
Use a single character for clean visual alignment. The icon should suggest "this is open, click to close."

---

### collapsedIcon

**What This Does:**
This is the symbol shown when a code block is currently collapsed (hidden). It suggests "click me to expand."

```javascript
collapsedIcon: '▲'
```

**Technical Details:**
- **Type:** `string` (Unicode character or emoji)
- **Default:** `'▲'` (up-pointing triangle)

**Popular Alternatives:**
- `'➕'` (plus sign - like opening an accordion)
- `'[+]'` (ASCII plus in brackets)
- `'🔼'` (emoji up arrow)

**Design Consistency:**
Pair this with expandedIcon logically. If expanded is `'[-]'`, collapsed should be `'[+]'`. If expanded is `'▼'`, collapsed should be `'▲'`.

---

### buttonTitle

**What This Does:**
This text appears when users hover their mouse over the collapse/expand button. It helps users understand what the button does.

```javascript
buttonTitle: 'Toggle code block'
```

**Technical Details:**
- **Type:** `string`
- **Default:** `'Toggle code block'`

**When to Change:**
Change this for non-English sites or to provide more specific instructions.

**Localization Examples:**
```javascript
buttonTitle: 'Código alternar'      // Spanish
buttonTitle: 'Basculer le code'     // French
buttonTitle: 'Code umschalten'      // German
buttonTitle: 'Click to show/hide'   // More explicit English
```

---

## Selectors Array (JavaScript)

**What This Section Covers:**
Selectors are CSS patterns that tell the code-collapse feature which elements on the page are code blocks. If you have custom code block styles or use a non-standard documentation generator, you'll need to adjust these.

Located in `code-collapse.js` (lines 43-50).

### Default Selectors

These selectors match the most common code block formats in Sphinx documentation. The feature will add collapse buttons to any element matching these patterns.

```javascript
const selectors = [
    'div.notranslate[class*="highlight-"]',      // Primary language blocks (python, bash, etc.)
    'div[class*="highlight-"]:not(.nohighlight)', // Catch-all for edge cases
    'div.doctest',                                // Python doctest examples
    'div.literal-block',                          // reStructuredText literal blocks
    'div.code-block',                             // code-block directive
    'pre.literal-block'                           // Pre-formatted text blocks
];
```

**How It Works:**
The system checks every element on the page against these patterns. If an element matches AND contains code content, it gets a collapse button.

### Adding Custom Selectors

If your code blocks use custom CSS classes (for example, from a theme or plugin), add your own selector.

**Example:** Adding support for a custom code class:
```javascript
const selectors = [
    // ... existing selectors ...
    'div.my-custom-code-class',  // Your custom selector here
];
```

**Testing Your Changes:**
After adding a selector, open your browser's console. You should see:
```
[Code Collapse] Initialized 47 blocks (100% coverage)
```

The "100% coverage" message means all your code blocks were found. If coverage is less than 100%, you may need additional selectors.

---

## CSS Customization

**What This Section Covers:**
If you want to change how the collapse buttons look (colors, size, position), you'll modify the CSS file. This section explains the most commonly customized properties.

All CSS customizations are in `code-collapse.css`. Changes take effect immediately after saving and refreshing your browser.

### Button Appearance

This controls where the button appears on each code block and how visible it is.

**File:** `code-collapse.css` (lines 65-80)

```css
.code-collapse-btn {
    position: absolute;
    top: 8px;           /* Distance from top */
    right: 8px;         /* Distance from right */
    padding: 4px 8px;   /* Button padding */
    opacity: 0.3;       /* Default opacity (subtle) */
    /* ... */
}

.code-collapse-btn:hover {
    opacity: 1.0;       /* Hover opacity (visible) */
    /* ... */
}
```

### Button Gap (Sibling Spacing)

**File:** `code-collapse.css` (lines 104-106)

```css
.copybtn + .code-collapse-btn {
    margin-left: 8px;   /* Gap between copy and collapse buttons */
}
```

- **Desktop:** 8px (default)
- **Mobile (< 768px):** 5px (line 250)

### Master Controls Styling

**File:** `code-collapse.css` (lines 10-21)

```css
.code-controls-master {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(99, 102, 241, 0.05));
    border: 2px solid rgba(59, 130, 246, 0.3);
    padding: 12px 16px;
    margin: 1.5rem 0;
    /* ... */
}
```

**Customize colors:**
- Background gradient: Change `rgba()` values
- Border color: Change `border` property
- Button colors: Lines 31-45 (`.code-control-btn`)

### Dark Mode Customization

**File:** `code-collapse.css` (lines 181-203)

```css
[data-theme="dark"] .code-controls-master {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(99, 102, 241, 0.1));
    border-color: rgba(59, 130, 246, 0.4);
}

[data-theme="dark"] .code-collapse-btn {
    background: transparent;
    color: inherit;
    opacity: 0.3;
}
```

**Note:** Adjust for your theme's dark mode colors.

---

## Exclusion Rules (JavaScript)

Located in `shouldSkipBlock()` function (lines 113-128)

### Default Exclusions

```javascript
function shouldSkipBlock(element) {
    // Skip math blocks
    if (element.classList.contains('nohighlight')) return true;
    if (element.classList.contains('amsmath')) return true;
    if (element.classList.contains('math')) return true;

    // Skip if no code content
    const preElement = element.querySelector('pre');
    if (!preElement) return true;

    // Skip very short blocks (<10 characters)
    const content = preElement.textContent.trim();
    if (content.length < 10) return true;

    return false;
}
```

### Adding Custom Exclusion

```javascript
function shouldSkipBlock(element) {
    // ... existing exclusions ...

    // Add custom exclusion
    if (element.classList.contains('no-collapse')) return true;

    return false;
}
```

---

## Performance Settings

### GPU Acceleration (CSS)

**File:** `code-collapse.css` (lines 114-131)

```css
div[class*="highlight"] {
    contain: layout;  /* Prevent layout shifts - can disable if issues */
}

div.highlight {
    transform: translateZ(0);           /* Force GPU layer - disable if GPU issues */
    backface-visibility: hidden;        /* Smooth rendering - can disable */
}

div[class*="highlight"] pre {
    will-change: max-height, opacity;   /* Performance hint - can disable */
}
```

**Disable if:** GPU acceleration causes issues on low-end devices.

### Animation Optimization

**Disable will-change if memory constrained:**
```css
div[class*="highlight"] pre {
    /* will-change: max-height, opacity; */ /* Commented out */
}
```

**Disable GPU acceleration if glitchy:**
```css
div.highlight {
    /* transform: translateZ(0); */
    /* backface-visibility: hidden; */
}
```

---

## Browser Compatibility Matrix

| Feature | Chrome 90+ | Firefox 88+ | Edge 90+ | Safari 14+ |
|---------|-----------|-------------|----------|-----------|
| Core functionality | ✅ | ✅ | ✅ | ✅ |
| `requestAnimationFrame` | ✅ | ✅ | ✅ | ✅ |
| `cubic-bezier()` | ✅ | ✅ | ✅ | ✅ |
| `localStorage` | ✅ | ✅ | ✅ | ✅ |
| `contain: layout` | ✅ Full | ⚠️ Partial | ✅ Full | ⚠️ Limited |
| `will-change` | ✅ | ✅ | ✅ | ✅ |
| `backface-visibility` | ✅ | ✅ | ✅ | ✅ |

**Legend:**
- ✅ Full support
- ⚠️ Partial/limited support (feature still works)
- ❌ Not supported

---

## Recommended Settings by Use Case

### Minimal Animation (Accessibility-Focused)

```javascript
// CONFIG
animationDuration: 200  // Faster
easing: 'linear'        // Simple

// CSS - Disable GPU features
// Comment out: contain, transform, will-change
```

### Maximum Performance (Modern Browsers)

```javascript
// CONFIG
animationDuration: 350  // Default
easing: 'cubic-bezier(0.4, 0.0, 0.2, 1)'  // Material Design

// CSS - Keep all GPU features enabled (default)
```

### Legacy Browser Support (Older Devices)

```javascript
// CONFIG
animationDuration: 400  // Slightly slower
easing: 'ease-in-out'   // Standard CSS

// CSS - Disable advanced features
// Comment out: contain, transform, backface-visibility, will-change
```

---

## Summary and Quick Reference

This configuration reference covered all customizable aspects of the code-collapse feature. Here's a quick recap of what you can control:

**JavaScript Settings** (in `code-collapse.js`):
- Storage key for remembering collapse states
- Animation speed and easing curves
- Button icons and hover text
- Which code blocks get collapse buttons
- Exclusion rules for special blocks

**CSS Styling** (in `code-collapse.css`):
- Button positioning and appearance
- Colors and opacity
- Dark mode styles
- Master control bar styling
- Mobile responsive adjustments

**Performance Tuning** (in CSS and JS):
- GPU acceleration toggles
- Animation optimization flags
- Memory usage controls
- Browser compatibility fallbacks

**Common Configurations:**
Refer to the [Recommended Settings by Use Case](#recommended-settings-by-use-case) section above for pre-configured setups for accessibility, performance, or legacy browser support.

**Next Steps:**
- Need implementation help? See [integration-guide.md](integration-guide.md)
- Having issues? See [troubleshooting.md](troubleshooting.md)
- Want to understand the internals? See [technical-reference.md](technical-reference.md)
- Looking for usage tips? See [user-guide.md](user-guide.md)

**Questions or Feedback:**
This feature is actively maintained. If you need configuration options not covered here, check the technical reference for advanced customization patterns.
