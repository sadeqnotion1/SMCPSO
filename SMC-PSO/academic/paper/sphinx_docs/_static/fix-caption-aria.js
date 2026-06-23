/**
 * Fix missing aria-level on caption headings (Sphinx theme ARIA compliance)
 *
 * Issue: Sphinx generates <p class="caption" role="heading"> without aria-level
 * Fix: Add aria-level="2" to all caption headings on page load
 *
 * axe-core violation: aria-required-attr (critical)
 * Affected pages: Pages with toctree captions (benchmarks, analysis, etc.)
 */

(function() {
    'use strict';

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixCaptionAria);
    } else {
        fixCaptionAria();
    }

    function fixCaptionAria() {
        // Find all caption elements with role="heading" but no aria-level
        const captions = document.querySelectorAll('p.caption[role="heading"]:not([aria-level])');

        if (captions.length === 0) {
            return; // No captions to fix
        }

        console.log(`[Caption ARIA Fix] Found ${captions.length} caption headings missing aria-level`);

        captions.forEach((caption, index) => {
            // Set aria-level to 2 (captions are typically subheadings under main heading)
            caption.setAttribute('aria-level', '2');
            console.log(`[Caption ARIA Fix] Fixed caption ${index + 1}:`, caption.textContent.trim().substring(0, 50));
        });

        console.log('[Caption ARIA Fix] Complete');
    }
})();
