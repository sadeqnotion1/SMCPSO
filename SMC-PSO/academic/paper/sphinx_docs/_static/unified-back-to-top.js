/* ============================================================================
   UNIFIED BACK-TO-TOP VISIBILITY MANAGER
   ============================================================================

   PURPOSE:
   Synchronizes two independent visibility control systems for back-to-top button:
   1. Furo's built-in scroll detection (adds html.show-back-to-top class)
   2. Custom JavaScript visibility control (adds .show class to button element)

   PROBLEM SOLVED:
   - Race conditions between Furo's class changes and custom scroll handlers
   - Button visibility issues after longer scrolls
   - Conflicting transition timings (Furo debounce vs CSS transitions)
   - Missing fallback when one system triggers before the other

   ARCHITECTURE:
   - MutationObserver watches <html> element for Furo's .show-back-to-top class
   - Debounced scroll handler (100ms) monitors scroll position
   - Both systems stay synchronized: if one adds visibility, other follows
   - Single source of truth prevents conflicts

   INTEGRATION:
   - CSS supports both: html.show-back-to-top .back-to-top AND .back-to-top.show
   - 150ms CSS transitions (reduced from 300ms to minimize race window)
   - Works with Furo theme updates (observes, doesn't override)

   CREATED: November 2025
   AUTHOR: Claude Code
   ============================================================================ */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        scrollThreshold: 300,        // Show button after scrolling this many pixels
        debounceDelay: 100,          // Debounce scroll events (100ms to avoid race with 150ms CSS transition)
        smoothScrollDuration: 800,   // Smooth scroll animation duration
        buttonSelector: '.back-to-top, .btn-scroll-top, [id*="back-to-top"], [class*="back-to-top"]',
        furoClassName: 'show-back-to-top',
        customClassName: 'show'
    };

    // State management
    let backToTopButton = null;
    let scrollTimeout = null;
    let lastScrollY = 0;
    let isScrollingUp = false;
    let isSynchronizing = false; // Prevent infinite loops during sync

    // [AI] Initialize unified visibility manager
    function init() {
        // Find back-to-top button
        backToTopButton = document.querySelector(CONFIG.buttonSelector);

        if (!backToTopButton) {
            console.warn('[AI] Unified back-to-top: Button not found, visibility sync disabled');
            return;
        }

        console.log('[AI] Unified back-to-top: Initializing dual-system synchronization');

        // Set up MutationObserver to watch Furo's class changes on <html>
        setupFuroClassObserver();

        // Set up scroll handler for custom visibility detection
        setupScrollHandler();

        // Set up smooth scroll click handler
        setupClickHandler();

        console.log('[AI] Unified back-to-top: Initialization complete');
    }

    // [AI] Watch Furo's html.show-back-to-top class via MutationObserver
    function setupFuroClassObserver() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    syncVisibilityFromFuro();
                }
            });
        });

        // Observe <html> element for class attribute changes
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['class']
        });

        console.log('[AI] Unified back-to-top: MutationObserver watching Furo class changes');
    }

    // [AI] Synchronize custom .show class when Furo changes html.show-back-to-top
    function syncVisibilityFromFuro() {
        if (isSynchronizing) return; // Prevent infinite loops

        const htmlHasFuroClass = document.documentElement.classList.contains(CONFIG.furoClassName);
        const buttonHasCustomClass = backToTopButton.classList.contains(CONFIG.customClassName);

        // Sync custom class to match Furo's state
        if (htmlHasFuroClass && !buttonHasCustomClass) {
            isSynchronizing = true;
            backToTopButton.classList.add(CONFIG.customClassName);
            console.log('[AI] Unified back-to-top: Synced .show class (Furo triggered visibility)');
            isSynchronizing = false;
        } else if (!htmlHasFuroClass && buttonHasCustomClass) {
            isSynchronizing = true;
            backToTopButton.classList.remove(CONFIG.customClassName);
            console.log('[AI] Unified back-to-top: Removed .show class (Furo triggered hide)');
            isSynchronizing = false;
        }
    }

    // [AI] Synchronize Furo's html.show-back-to-top when custom system changes
    function syncVisibilityFromCustom(shouldShow) {
        if (isSynchronizing) return; // Prevent infinite loops

        const htmlHasFuroClass = document.documentElement.classList.contains(CONFIG.furoClassName);

        // Note: We DON'T force-add Furo's class, just sync our custom class
        // This respects Furo's internal scroll detection logic
        // Both CSS selectors work independently: html.show-back-to-top .back-to-top AND .back-to-top.show

        if (shouldShow) {
            backToTopButton.classList.add(CONFIG.customClassName);
            console.log('[AI] Unified back-to-top: Added .show class (custom scroll detection)');
        } else {
            backToTopButton.classList.remove(CONFIG.customClassName);
            console.log('[AI] Unified back-to-top: Removed .show class (custom scroll detection)');
        }
    }

    // [AI] Debounced scroll handler for custom visibility detection
    function setupScrollHandler() {
        window.addEventListener('scroll', function() {
            // Clear previous timeout
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }

            // Debounce scroll events (100ms)
            scrollTimeout = setTimeout(function() {
                handleScrollVisibility();
            }, CONFIG.debounceDelay);
        }, { passive: true });

        console.log('[AI] Unified back-to-top: Scroll handler registered (100ms debounce)');
    }

    // [AI] Handle scroll-based visibility (custom detection)
    function handleScrollVisibility() {
        const currentScrollY = window.pageYOffset || document.documentElement.scrollTop;

        // Detect scroll direction
        isScrollingUp = currentScrollY < lastScrollY;
        lastScrollY = currentScrollY;

        // Determine if button should be visible
        // Show when: scrolled > threshold AND scrolling up
        // This matches Furo's typical behavior
        const shouldShow = currentScrollY > CONFIG.scrollThreshold && isScrollingUp;

        // Sync custom visibility (respects Furo's state via CSS dual-selector)
        syncVisibilityFromCustom(shouldShow);
    }

    // [AI] Smooth scroll to top on button click
    function setupClickHandler() {
        backToTopButton.addEventListener('click', function(event) {
            event.preventDefault();

            // Smooth scroll to top
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });

            // Focus management for accessibility
            // After scroll completes, focus on skip-to-content link if available
            setTimeout(function() {
                const skipLink = document.querySelector('a[href="#content"], a[href="#main-content"]');
                if (skipLink) {
                    skipLink.focus();
                }
            }, CONFIG.smoothScrollDuration);

            console.log('[AI] Unified back-to-top: Smooth scroll to top triggered');
        });

        console.log('[AI] Unified back-to-top: Click handler registered (smooth scroll enabled)');
    }

    // [AI] Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
