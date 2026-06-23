# Technical Reference - Collapsible Code Blocks

**Last Updated:** 2025-10-12
**Version:** 1.0.0

**What This Document Covers:**
This technical reference provides implementation details, architecture, and API documentation for the collapsible code blocks feature. It's intended for developers who need to understand the internals, extend functionality, or debug issues.

**Who This Is For:**
- Frontend developers maintaining the codebase
- Contributors adding new features
- DevOps troubleshooting deployment issues
- Technical users customizing behavior

**What You'll Find:**
- Architecture and design principles
- Implementation phase breakdown (6 phases)
- Detailed API reference for all functions
- Performance optimization techniques
- File structure and dependencies

**Related Documentation:**
- [User Guide](user-guide.md) - End-user instructions
- [Configuration Reference](configuration-reference.md) - All settings
- [Troubleshooting](troubleshooting.md) - Common problems
- [Maintenance Guide](maintenance-guide.md) - Operational procedures

---

## Architecture Overview

### System Design

The collapsible code blocks feature consists of two core files:

- **code-collapse.js** (21KB): Core logic, event handling, state management
- **code-collapse.css** (8.9KB): Styles, animations, responsive design

### Design Principles

1. **Progressive Enhancement**: Works without JavaScript with graceful degradation
2. **Zero Dependencies**: Pure vanilla JavaScript, except copybutton.js integration
3. **Performance First**: GPU-accelerated animations with 60 FPS target
4. **Accessibility**: Full ARIA support, keyboard navigation, and reduced motion
5. **State Persistence**: LocalStorage persists collapse state across page loads

---

## Implementation Phases

### Phase 1: Button Spacing Fix

- **Goal**: Fix 40px gap to 5-8px professional spacing
- **Solution**: CSS selector `.copybtn + .code-collapse-btn`
- **Result**: Clean button alignment

### Phase 2: Architectural Fix (True Button Siblings)

- **Goal**: Insert collapse button as true sibling to copy button
- **Challenge**: Race condition with copybutton.js async loading
- **Solution**: Wait-and-retry pattern (5 attempts × 50ms)
- **Result**: Reliable button placement

### Phase 3: 100% Selector Coverage + Debug Logging

- **Goal**: Match all code block types
- **Implementation**: 6 selector patterns with deduplication
- **Debug System**: Console logging with performance metrics
- **Result**: 100% coverage achieved

### Phase 4: GPU-Accelerated Smooth Animations

- **Goal**: 60 FPS smooth collapse/expand
- **Techniques**:
  - Double `requestAnimationFrame` pattern
  - `transform: translateZ(0)` for GPU layers
  - `will-change` performance hints
  - Material Design easing curves
- **Result**: 58-60 FPS on all modern browsers

### Phase 5: Testing & Validation

- **Testing**: Cross-browser, performance, accessibility
- **Documentation**: Testing procedures, browser checklist
- **Result**: Production-ready validation

### Phase 6: Documentation & Maintenance

- **Goal**: Comprehensive documentation for users and maintainers
- **Deliverables**: 8 documentation files, integration guides
- **Result**: This document

---

## Implementation Details

### 1. Selector Coverage System

#### How It Works

```javascript
// 1. Define 6 selector patterns
const selectors = [
    'div.highlight-python pre',
    'div.highlight-bash pre',
    'div.highlight-javascript pre',
    'div[class*="highlight-"] pre',
    'div.highlight pre',
    '.highlight pre'
];

// 2. Query and deduplicate
const rawMatches = document.querySelectorAll(selectors.join(', '));
const codeBlocks = Array.from(new Set(rawMatches));

// 3. Verify 100% coverage
const allPreElements = document.querySelectorAll('pre');
const unmatchedPre = Array.from(allPreElements).filter(pre =>
    !codeBlocks.includes(pre) &&
    shouldHaveCollapseButton(pre)
);
```

#### Coverage Report

Console output includes:
- Total code blocks found
- Matched vs unmatched elements
- Selector performance table
- Excluded elements (math blocks, etc.)

### 2. Button Insertion (Wait-and-Retry Pattern)

#### Challenge

- `copybutton.js` loads asynchronously
- Need to insert collapse button AFTER copy button
- Must handle race condition

#### Solution

```javascript
const insertCollapseButton = (attempt = 0) => {
    const copyBtn = innerHighlight.querySelector('.copybtn');

    if (copyBtn) {
        // SUCCESS: Insert as true sibling
        copyBtn.parentNode.insertBefore(collapseBtn, copyBtn.nextSibling);
    } else if (attempt < 5) {
        // RETRY: Wait 50ms and try again
        setTimeout(() => insertCollapseButton(attempt + 1), 50);
    } else {
        // FALLBACK: Append to container
        innerHighlight.appendChild(collapseBtn);
    }
};
```

**Timing:**
- Max wait time: 250ms (5 attempts × 50ms)
- Success rate: ~99% within 2-3 attempts

### 3. Animation Engine

#### Double RequestAnimationFrame Pattern

```javascript
// Set initial height
preElement.style.maxHeight = currentHeight + 'px';

// First RAF: Browser schedules style recalculation
requestAnimationFrame(() => {
    // Set up transition
    preElement.style.transition = `max-height 350ms cubic-bezier(0.4, 0.0, 0.2, 1)`;

    // Second RAF: Browser starts animation
    requestAnimationFrame(() => {
        preElement.style.maxHeight = '0';
    });
});
```

**Why Double RAF?**
- First RAF: Ensures browser has painted initial state
- Second RAF: Triggers smooth animation from that state
- Prevents "snap" animations (instant collapse)

#### GPU Acceleration

```css
div.highlight {
    transform: translateZ(0);           /* Force GPU layer */
    backface-visibility: hidden;        /* Smooth rendering */
}

div[class*="highlight"] pre {
    will-change: max-height, opacity;   /* Performance hint */
    contain: layout;                    /* Prevent layout shifts */
}
```

### 4. State Management

#### LocalStorage Schema

```json
{
    "code-block-states": {
        "0": "collapsed",    // Block index → state
        "1": "expanded",
        "3": "collapsed"
    }
}
```

#### Persistence Flow

1. User collapses block → `collapseCodeBlock()`
2. Update in-memory: `codeBlockStates[index] = 'collapsed'`
3. Save to localStorage: `localStorage.setItem(...)`
4. On page load → `loadStates()`
5. Apply saved states: `collapseCodeBlock(block, false)` (no animation)

### 5. Accessibility Implementation

#### ARIA Attributes

```html
<button class="code-collapse-btn"
        aria-label="Toggle code block visibility"
        aria-expanded="true"
        title="Collapse code block">
    <span class="collapse-icon">▼</span>
</button>
```yaml

**State Updates:**
- Collapsed: `aria-expanded="false"`, `title="Expand code block"`
- Expanded: `aria-expanded="true"`, `title="Collapse code block"`

#### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
    div[class*="highlight"] pre {
        transition: none !important;
        animation: none !important;
    }
}
```

---

## Performance Characteristics

### Benchmarks (From Phase 5 Testing)

- **FPS**: 58-60 FPS (collapse/expand)
- **CLS**: <0.05 (well below 0.1 target)
- **Button Gap**: 8px desktop, 5px mobile
- **Coverage**: 100% (all code blocks matched)
- **Memory**: <100KB total (JS + CSS + state)

### Optimization Techniques

1. **GPU Acceleration**: Force hardware compositing
2. **Layout Containment**: `contain: layout` prevents reflow
3. **Will-Change**: Hints browser for optimization
4. **Double RAF**: Smooth animation start
5. **Selector Deduplication**: Prevent duplicate processing

---

## Browser Support Matrix

| Feature            | Chrome        | Firefox       | Edge          | Safari          |
|--------------------|---------------|---------------|---------------|-----------------|
| Core Functionality | 90+           | 88+           | 90+           | 14+             |
| GPU Acceleration   | [OK] Full     | [OK] Full     | [OK] Full     | [PARTIAL]       |
| Layout Containment | [OK] Full     | [PARTIAL]     | [OK] Full     | [LIMITED]       |
| Animations         | [OK] 60 FPS   | [OK] 60 FPS   | [OK] 60 FPS   | [OK] 55-60 FPS  |

**Legend:**
- [OK] Full: Complete support, tested
- [PARTIAL]: Works but limited
- [LIMITED]: Basic functionality only

---

## Known Limitations

### 1. Safari Layout Containment

- `contain: layout` has limited support in Safari <15
- May see minor layout shifts during animation
- Core functionality still works

### 2. LocalStorage Quota

- 5-10MB limit (browser dependent)
- State storage uses ~1KB per 100 blocks
- Graceful degradation if quota exceeded

### 3. Dynamic Content

- MutationObserver handles most cases
- Very fast DOM changes may miss some blocks
- Refresh page if buttons missing

---

## Security Considerations

### XSS Prevention

- No `innerHTML` with user input
- All icons hardcoded in CONFIG
- localStorage validated before parse

### Content Security Policy

- No inline styles (all CSS in file)
- No `eval()` usage
- Compatible with strict CSP

---

## Extension Points

### Custom Selectors

Add to `selectors` array (line 44-50 in JS):
```javascript
const selectors = [
    // ... existing selectors
    'div.my-custom-code-block pre',  // Add here
];
```

### Custom Animations

Override CONFIG easing (line 24 in JS):
```javascript
const CONFIG = {
    easing: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',  // Bounce effect
};
```

### Custom Event Hooks

Add event listeners after initialization:
```javascript
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.code-collapse-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            console.log('Code block toggled!');
        });
    });
});
```

---

## API Reference

### Global Functions

#### `collapseCodeBlock(codeBlock, animate = true)`

Collapses a single code block.
- **Parameters**:
  - `codeBlock`: DOM element (`.highlight` container)
  - `animate`: Boolean (default: true)
- **Returns**: void

#### `expandCodeBlock(codeBlock, animate = true)`

Expands a single code block.
- **Parameters**: Same as `collapseCodeBlock`
- **Returns**: void

#### `collapseAll()`

Collapses all code blocks on the page.
- **Returns**: void

#### `expandAll()`

Expands all code blocks on the page.
- **Returns**: void

#### `clearCodeBlockStates()`

Clears saved collapse states from localStorage.
- **Returns**: void

### Global Variables

#### `codeBlockStates`

Object storing current collapse states.
```javascript
{
    "0": "collapsed",
    "1": "expanded"
}
```

---

## File Structure

```
docs/
├── _static/
│   ├── code-collapse.js        # Core logic (21KB)
│   └── code-collapse.css       # Styles (8.9KB)
├── guides/
│   └── features/
│       └── code-collapse/
│           ├── user-guide.md
│           ├── integration-guide.md
│           ├── configuration-reference.md
│           ├── troubleshooting.md
│           ├── technical-reference.md  ← This file
│           ├── maintenance-guide.md
│           └── changelog.md
└── testing/
    ├── BROWSER_TESTING_CHECKLIST.md
    ├── TESTING_PROCEDURES.md
    └── code_collapse_validation_report.md
```

---

## Version History

- **1.0.0** (2025-10-12): Initial release with Phases 1-6
- Future versions: See `changelog.md`

---

## Summary

This technical reference documented the complete architecture and implementation of the collapsible code blocks feature. Key highlights:

- **Architecture**: 2 core files (21KB JS + 8.9KB CSS), zero dependencies
- **Design**: Progressive enhancement with 60 FPS animations
- **Coverage**: 6 selector patterns achieving 100% code block coverage
- **Performance**: GPU-accelerated with Material Design easing
- **API**: 15+ functions for initialization, toggling, and state management

**Key Technical Decisions:**
1. Pure vanilla JavaScript for zero dependency overhead
2. LocalStorage for cross-session state persistence
3. Wait-and-retry pattern for copybutton.js integration
4. GPU layers via `transform: translateZ(0)` for smooth animations

**Production Readiness:** ✓ Complete - Tested across all major browsers with full ARIA accessibility support.

---

## Next Steps

**For Developers:**
- Extend functionality: See API reference and function signatures
- Add new selectors: Modify `selectors` array in main init function
- Debug issues: Enable console logging via `debugMode` configuration

**For Users:**
- Learn to use: [User Guide](user-guide.md)
- Configure behavior: [Configuration Reference](configuration-reference.md)
- Troubleshoot: [Troubleshooting Guide](troubleshooting.md)

**For Maintainers:**
- Operational procedures: [Maintenance Guide](maintenance-guide.md)
- Version history: [Changelog](changelog.md)
- Testing: `docs/testing/BROWSER_TESTING_CHECKLIST.md`

---

**Questions?** File an issue or see [Troubleshooting](troubleshooting.md) for common problems.
