/**
 * Collapsible Code Blocks with Curtain Animation
 * Adds minimize/expand functionality to all code blocks
 *
 * SELECTOR COVERAGE:
 * - Language blocks: highlight-python, highlight-bash, etc. (40+ types)
 * - Edge cases: highlight-##, highlight-**, highlight-- (markdown artifacts)
 * - Literal blocks: div.literal-block, pre.literal-block
 * - Doctest blocks: div.doctest
 *
 * EXCLUSIONS:
 * - Math blocks: .amsmath, .math, .nohighlight (LaTeX equations)
 * - Very short blocks: <10 characters (likely not code)
 *
 * DEBUG: Check console for coverage report on page load
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        storageKey: 'code-block-states',
        animationDuration: 350, // milliseconds (350ms feels smoother than 300ms)
        easing: 'cubic-bezier(0.4, 0.0, 0.2, 1)', // Material Design standard easing
        expandedIcon: '▼',
        collapsedIcon: '▲',
        buttonTitle: 'Toggle code block'
    };

    // State management
    let codeBlockStates = {};

    // Initialization guard - prevent duplicate execution
    let initialized = false;

    /**
     * Initialize collapsible code blocks
     */
    function initCollapsibleCode() {
        // Prevent duplicate initialization
        if (initialized) {
            console.log('[CodeCollapse] Already initialized, skipping');
            return;
        }
        initialized = true;

        // Load saved states
        loadStates();

        // Find all code blocks - target only outer containers to avoid duplicates
        // Sphinx generates nested structure: <div class="highlight-{lang} notranslate"><div class="highlight"><pre>
        // We target the OUTER div (with notranslate) to avoid adding buttons to both layers
        const selectors = [
            'div.notranslate[class*="highlight-"]',           // Primary: Language blocks with notranslate
            'div[class*="highlight-"]:not(.nohighlight)',     // Catch-all: Edge cases (##, **, --)
            'div.doctest',                                     // Doctest blocks
            'div.literal-block',                               // Literal blocks
            'div.code-block',                                  // Code-block directive
            'pre.literal-block'                                // Pre-formatted literal blocks
        ];

        const rawMatches = document.querySelectorAll(selectors.join(', '));

        // Deduplicate using Set (maintains DOM order)
        const codeBlocks = Array.from(new Set(rawMatches));

        // === DEBUG LOGGING SYSTEM ===
        console.log(`[CodeCollapse] Found ${codeBlocks.length} code blocks (${rawMatches.length} raw matches)`);

        // Find all <pre> elements in the document
        const allPreElements = document.querySelectorAll('pre');
        console.log(`[CodeCollapse] Total <pre> elements: ${allPreElements.length}`);

        // Identify unmatched <pre> elements
        const unmatchedPre = Array.from(allPreElements).filter(pre => {
            // Check if this <pre> is inside any matched code block
            return !codeBlocks.some(block => block.contains(pre));
        });

        if (unmatchedPre.length > 0) {
            console.warn(`[CodeCollapse] ⚠️ ${unmatchedPre.length} unmatched <pre> elements found:`);
            unmatchedPre.forEach((pre, idx) => {
                const parent = pre.parentElement;
                const classes = parent ? parent.className : 'NO PARENT';
                console.warn(`  [${idx + 1}] Parent classes: "${classes}"`);
                console.warn(`      Content preview: "${pre.textContent.substring(0, 50)}..."`);
            });
        } else {
            console.log('[CodeCollapse] ✅ 100% coverage - all <pre> elements matched');
        }

        // Log selector performance
        const selectorStats = {};
        selectors.forEach(selector => {
            const count = document.querySelectorAll(selector).length;
            selectorStats[selector] = count;
        });
        console.table(selectorStats);

        if (codeBlocks.length === 0) {
            return; // No code blocks on this page
        }

        // Add master controls
        addMasterControls(codeBlocks.length);

        // Process each code block
        codeBlocks.forEach((codeBlock, index) => {
            processCodeBlock(codeBlock, index);
        });

        // Setup keyboard shortcuts
        setupKeyboardShortcuts();

        // Watch for dynamically added code blocks
        setupMutationObserver();
    }

    /**
     * Check if block should be skipped (math, invalid, etc.)
     */
    function shouldSkipBlock(element) {
        // Skip math blocks (LaTeX, MathJax, KaTeX)
        if (element.classList.contains('nohighlight')) return true;
        if (element.classList.contains('amsmath')) return true;
        if (element.classList.contains('math')) return true;

        // Skip if no actual code content
        const preElement = element.querySelector('pre');
        if (!preElement) return true;

        // Skip very short blocks (likely not code)
        const content = preElement.textContent.trim();
        if (content.length < 10) return true;

        return false;
    }

    /**
     * Process individual code block
     */
    function processCodeBlock(codeBlock, index) {
        // Skip if already processed
        if (codeBlock.classList.contains('collapsible-processed')) {
            return;
        }

        // Skip math/invalid blocks
        if (shouldSkipBlock(codeBlock)) {
            console.log(`[CodeCollapse] Skipped block ${index}: ${codeBlock.className}`);
            return;
        }

        // Mark as processed
        codeBlock.classList.add('collapsible-processed');
        codeBlock.setAttribute('data-code-index', index);

        // UI-004 FIX: Add unique ID and ARIA attributes for accessibility
        const codeBlockId = `code-block-${index}`;
        codeBlock.id = codeBlockId;
        codeBlock.setAttribute('role', 'region');
        codeBlock.setAttribute('aria-label', `Code block ${index + 1}`);

        // Get the pre element (actual code content)
        const preElement = codeBlock.querySelector('pre');
        if (!preElement) return;

        // Create collapse button
        const collapseBtn = createCollapseButton(index);

        // UI-004 FIX: Create ARIA live region for collapsed notice (screen reader accessible)
        const noticeId = `code-notice-${index}`;
        const noticeElement = document.createElement('div');
        noticeElement.id = noticeId;
        noticeElement.className = 'code-collapse-notice';
        noticeElement.setAttribute('aria-live', 'polite');
        noticeElement.setAttribute('aria-atomic', 'true');
        noticeElement.style.display = 'none'; // Hidden by default
        noticeElement.textContent = 'Code hidden (click ▲ to expand)';

        // Find INNER highlight container where copy button lives
        const innerHighlight = codeBlock.querySelector('div.highlight');
        if (!innerHighlight) {
            console.warn('[CodeCollapse] No inner highlight container found', codeBlock);
            return;
        }

        // Insert notice element after the inner highlight
        codeBlock.appendChild(noticeElement);

        // Wait for copybutton.js to add the copy button, then insert collapse button as sibling
        const insertCollapseButton = (attempt = 0) => {
            const copyBtn = innerHighlight.querySelector('.copybtn');

            if (copyBtn) {
                // SUCCESS: Copy button exists, insert collapse button as SIBLING
                copyBtn.parentNode.insertBefore(collapseBtn, copyBtn.nextSibling);

                // Apply saved state
                const savedState = codeBlockStates[index];
                if (savedState === 'collapsed') {
                    collapseCodeBlock(codeBlock, false); // No animation on page load
                }
            } else if (attempt < 5) {
                // RETRY: Copy button not ready yet, wait and try again
                setTimeout(() => insertCollapseButton(attempt + 1), 50);
            } else {
                // FALLBACK: No copy button after 250ms, insert at end of inner container
                innerHighlight.appendChild(collapseBtn);

                // Apply saved state
                const savedState = codeBlockStates[index];
                if (savedState === 'collapsed') {
                    collapseCodeBlock(codeBlock, false);
                }
            }
        };

        // Start insertion process
        insertCollapseButton();
    }

    /**
     * Create collapse button
     * UI-004 FIX: Enhanced with aria-controls for screen reader navigation
     */
    function createCollapseButton(index) {
        const button = document.createElement('button');
        const codeBlockId = `code-block-${index}`;
        const noticeId = `code-notice-${index}`;

        button.className = 'code-collapse-btn';
        button.innerHTML = `<span class="collapse-icon">${CONFIG.expandedIcon}</span>`;
        button.title = CONFIG.buttonTitle;
        button.setAttribute('aria-label', `Toggle code block ${index + 1} visibility`);
        button.setAttribute('aria-expanded', 'true');
        button.setAttribute('aria-controls', `${codeBlockId} ${noticeId}`); // Controls both block and notice

        // Click handler
        button.addEventListener('click', (e) => {
            e.preventDefault();
            // Find the code block container (works for all block types)
            const codeBlock = button.closest('div.notranslate[class*="highlight-"], div.literal-block, div.code-block, div.doctest, pre.literal-block');
            toggleCodeBlock(codeBlock);
        });

        return button;
    }

    /**
     * Toggle code block state
     */
    function toggleCodeBlock(codeBlock) {
        const isCollapsed = codeBlock.classList.contains('code-collapsed');

        if (isCollapsed) {
            expandCodeBlock(codeBlock);
        } else {
            collapseCodeBlock(codeBlock);
        }
    }

    /**
     * Collapse code block with curtain animation
     * UI-004 FIX: Show ARIA live region notice for screen reader announcement
     */
    function collapseCodeBlock(codeBlock, animate = true) {
        const preElement = codeBlock.querySelector('pre');
        const button = codeBlock.querySelector('.code-collapse-btn');
        const icon = button.querySelector('.collapse-icon');
        const index = codeBlock.getAttribute('data-code-index');
        const noticeElement = codeBlock.querySelector('.code-collapse-notice');

        if (!animate) {
            codeBlock.classList.add('code-collapsed');
            preElement.style.maxHeight = '0';
            preElement.style.overflow = 'hidden';
            // Show notice for screen readers
            if (noticeElement) noticeElement.style.display = 'block';
        } else {
            // Add transitioning state
            codeBlock.classList.add('code-collapsing');

            // Measure current height (before transition)
            const currentHeight = preElement.scrollHeight;
            preElement.style.maxHeight = currentHeight + 'px';

            // Cleanup handler using transitionend for robustness
            const cleanupCollapse = () => {
                codeBlock.classList.remove('code-collapsing');
                codeBlock.classList.add('code-collapsed');
                preElement.style.overflow = 'hidden';
                // Show notice for screen readers (after animation completes)
                if (noticeElement) noticeElement.style.display = 'block';
                preElement.removeEventListener('transitionend', cleanupCollapse);
            };

            // Listen for animation completion
            preElement.addEventListener('transitionend', cleanupCollapse, { once: true });

            // Fallback timeout in case transitionend doesn't fire
            const fallbackTimeout = setTimeout(cleanupCollapse, CONFIG.animationDuration + 50);

            // Double requestAnimationFrame for smooth start
            requestAnimationFrame(() => {
                // Set up transition
                preElement.style.transition = `max-height ${CONFIG.animationDuration}ms ${CONFIG.easing}, opacity ${CONFIG.animationDuration}ms ${CONFIG.easing}`;

                // Trigger animation in next frame
                requestAnimationFrame(() => {
                    preElement.style.maxHeight = '0';
                    preElement.style.opacity = '0';
                });
            });
        }

        // Update button
        icon.textContent = CONFIG.collapsedIcon;
        button.setAttribute('aria-expanded', 'false');
        button.title = 'Expand code block';

        // Save state
        codeBlockStates[index] = 'collapsed';
        saveStates();
    }

    /**
     * Expand code block with curtain animation
     * UI-004 FIX: Hide ARIA live region notice when expanded
     */
    function expandCodeBlock(codeBlock, animate = true) {
        const preElement = codeBlock.querySelector('pre');
        const button = codeBlock.querySelector('.code-collapse-btn');
        const icon = button.querySelector('.collapse-icon');
        const index = codeBlock.getAttribute('data-code-index');
        const noticeElement = codeBlock.querySelector('.code-collapse-notice');

        // Remove collapsed class immediately
        codeBlock.classList.remove('code-collapsed');
        preElement.style.overflow = 'hidden';
        // Hide notice immediately when expanding
        if (noticeElement) noticeElement.style.display = 'none';

        if (!animate) {
            preElement.style.maxHeight = 'none';
            preElement.style.opacity = '1';
        } else {
            // Add transitioning state
            codeBlock.classList.add('code-collapsing');

            // Measure target height (temporarily set to auto to measure)
            preElement.style.maxHeight = 'none';
            const targetHeight = preElement.scrollHeight;
            preElement.style.maxHeight = '0';

            // Cleanup handler using transitionend for robustness
            const cleanupExpand = () => {
                codeBlock.classList.remove('code-collapsing');
                preElement.style.maxHeight = 'none';
                preElement.style.overflow = 'visible';
                preElement.removeEventListener('transitionend', cleanupExpand);
            };

            // Listen for animation completion
            preElement.addEventListener('transitionend', cleanupExpand, { once: true });

            // Fallback timeout in case transitionend doesn't fire
            const fallbackTimeout = setTimeout(cleanupExpand, CONFIG.animationDuration + 50);

            // Double requestAnimationFrame for smooth start
            requestAnimationFrame(() => {
                // Set up transition
                preElement.style.transition = `max-height ${CONFIG.animationDuration}ms ${CONFIG.easing}, opacity ${CONFIG.animationDuration}ms ${CONFIG.easing}`;

                // Trigger animation in next frame
                requestAnimationFrame(() => {
                    preElement.style.maxHeight = targetHeight + 'px';
                    preElement.style.opacity = '1';
                });
            });
        }

        // Update button
        icon.textContent = CONFIG.expandedIcon;
        button.setAttribute('aria-expanded', 'true');
        button.title = 'Collapse code block';

        // Save state
        codeBlockStates[index] = 'expanded';
        saveStates();

        // Scroll to code block if it was off-screen
        if (animate) {
            setTimeout(() => {
                const rect = codeBlock.getBoundingClientRect();
                if (rect.top < 0 || rect.top > window.innerHeight) {
                    codeBlock.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            }, CONFIG.animationDuration);
        }
    }

    /**
     * Add master controls (Collapse All / Expand All)
     * UI-005 FIX: Prevent duplicate control bars from appearing
     */
    function addMasterControls(count) {
        // UI-005 FIX: Check if controls already exist before adding new ones
        const existingControls = document.querySelector('.code-controls-master');
        if (existingControls) {
            console.log('[CodeCollapse] Master controls already exist, skipping duplicate');
            return;
        }

        // Find a good place to insert controls (e.g., after first heading)
        const mainContent = document.querySelector('.document, article, main');
        if (!mainContent) return;

        const controlsContainer = document.createElement('div');
        controlsContainer.className = 'code-controls-master';
        controlsContainer.innerHTML = `
            <span class="code-controls-label">${count} code blocks:</span>
            <button class="code-control-btn" id="collapse-all-btn" title="Collapse all code blocks (Ctrl+Shift+C)">
                <span>▲</span> Collapse All
            </button>
            <button class="code-control-btn" id="expand-all-btn" title="Expand all code blocks (Ctrl+Shift+E)">
                <span>▼</span> Expand All
            </button>
        `;

        // Insert at the top of content
        const firstHeading = mainContent.querySelector('h1, h2');
        if (firstHeading) {
            firstHeading.parentNode.insertBefore(controlsContainer, firstHeading.nextSibling);
        } else {
            mainContent.insertBefore(controlsContainer, mainContent.firstChild);
        }

        // Add event listeners
        document.getElementById('collapse-all-btn').addEventListener('click', collapseAll);
        document.getElementById('expand-all-btn').addEventListener('click', expandAll);
    }

    /**
     * Collapse all code blocks
     */
    function collapseAll() {
        const selectors = [
            'div.notranslate[class*="highlight-"]',
            'div[class*="highlight-"]:not(.nohighlight)',
            'div.doctest',
            'div.literal-block',
            'div.code-block',
            'pre.literal-block'
        ];
        const codeBlocks = document.querySelectorAll(selectors.join(', '));
        codeBlocks.forEach(codeBlock => {
            if (!codeBlock.classList.contains('code-collapsed')) {
                collapseCodeBlock(codeBlock, true);
            }
        });
    }

    /**
     * Expand all code blocks
     */
    function expandAll() {
        const selectors = [
            'div.notranslate[class*="highlight-"]',
            'div[class*="highlight-"]:not(.nohighlight)',
            'div.doctest',
            'div.literal-block',
            'div.code-block',
            'pre.literal-block'
        ];
        const codeBlocks = document.querySelectorAll(selectors.join(', '));
        codeBlocks.forEach(codeBlock => {
            if (codeBlock.classList.contains('code-collapsed')) {
                expandCodeBlock(codeBlock, true);
            }
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Shift+C - Collapse All
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                collapseAll();
            }
            // Ctrl+Shift+E - Expand All
            else if (e.ctrlKey && e.shiftKey && e.key === 'E') {
                e.preventDefault();
                expandAll();
            }
        });
    }

    /**
     * Save states to localStorage
     */
    function saveStates() {
        try {
            localStorage.setItem(CONFIG.storageKey, JSON.stringify(codeBlockStates));
        } catch (e) {
            console.warn('Failed to save code block states:', e);
        }
    }

    /**
     * Load states from localStorage
     */
    function loadStates() {
        try {
            const saved = localStorage.getItem(CONFIG.storageKey);
            if (saved) {
                codeBlockStates = JSON.parse(saved);
            }
        } catch (e) {
            console.warn('Failed to load code block states:', e);
            codeBlockStates = {};
        }
    }

    /**
     * Setup MutationObserver to watch for dynamically added code blocks
     */
    function setupMutationObserver() {
        // Create observer to watch for new code blocks
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    // Check if the added node is a code block or contains code blocks
                    if (node.nodeType === 1) { // Element node
                        const selectors = [
                            'div.notranslate[class*="highlight-"]',
                            'div[class*="highlight-"]:not(.nohighlight)',
                            'div.doctest',
                            'div.literal-block',
                            'div.code-block',
                            'pre.literal-block'
                        ];

                        // Check if the node itself is a code block
                        const isCodeBlock = selectors.some(selector => {
                            try {
                                return node.matches && node.matches(selector);
                            } catch (e) {
                                return false;
                            }
                        });

                        if (isCodeBlock && !node.classList.contains('collapsible-processed')) {
                            const allBlocks = document.querySelectorAll(selectors.join(', '));
                            const index = Array.from(allBlocks).indexOf(node);
                            if (index !== -1) {
                                processCodeBlock(node, index);
                            }
                        }

                        // Check if the node contains code blocks
                        if (node.querySelectorAll) {
                            const codeBlocks = node.querySelectorAll(selectors.join(', '));
                            codeBlocks.forEach((codeBlock) => {
                                if (!codeBlock.classList.contains('collapsible-processed')) {
                                    const allBlocks = document.querySelectorAll(selectors.join(', '));
                                    const index = Array.from(allBlocks).indexOf(codeBlock);
                                    if (index !== -1) {
                                        processCodeBlock(codeBlock, index);
                                    }
                                }
                            });
                        }
                    }
                });
            });
        });

        // Start observing the document body for changes
        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    }

    /**
     * Clear saved states (for debugging)
     */
    window.clearCodeBlockStates = function() {
        localStorage.removeItem(CONFIG.storageKey);
        codeBlockStates = {};
        console.log('Code block states cleared');
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCollapsibleCode);
    } else {
        initCollapsibleCode();
    }

    // Re-initialize on page navigation (for SPAs)
    window.addEventListener('load', initCollapsibleCode);

})();
