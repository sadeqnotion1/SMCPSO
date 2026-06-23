/**
 * ============================================================================
 * DIP-SMC-PSO Documentation - Smooth Scroll Fix for Back-to-Top
 * ============================================================================
 * Adds smooth scrolling behavior to Furo's back-to-top button.
 * Integrates with Furo's visibility control (html.show-back-to-top).
 *
 * This script intercepts clicks on the back-to-top button and adds smooth
 * scrolling animation instead of instant jump.
 *
 * Dependencies: None (vanilla JavaScript)
 * Integration: Furo theme (v2025.09.25+)
 * Maintainer: AI Agent (Nov 2025)
 *
 * @see docs/_static/custom.css - Back-to-top button styling
 * @see docs/conf.py - JavaScript loading configuration
 */

(function() {
    'use strict';

    /**
     * Initialize smooth scroll behavior on DOM ready
     */
    document.addEventListener('DOMContentLoaded', function() {
        const backToTop = document.querySelector('.back-to-top');

        if (!backToTop) {
            console.warn('[AI] Back-to-top button not found - smooth scroll handler not attached');
            return;
        }

        /**
         * Handle back-to-top button click
         * Prevents default anchor jump and adds smooth scroll animation
         */
        backToTop.addEventListener('click', function(e) {
            e.preventDefault();

            // Smooth scroll to top
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });

            /**
             * Focus management for accessibility
             * After scroll completes, focus the main heading for screen readers
             * This provides context about where the page was scrolled to
             */
            setTimeout(function() {
                const mainHeading = document.querySelector('main h1, article h1, .document h1');
                if (mainHeading) {
                    // Make heading focusable temporarily
                    mainHeading.setAttribute('tabindex', '-1');
                    mainHeading.focus();
                    // Remove tabindex after focus to preserve natural tab order
                    mainHeading.removeAttribute('tabindex');
                }
            }, 500); // Delay to allow smooth scroll animation to complete
        });

        console.log('[AI] Smooth scroll enabled for back-to-top button');
    });
})();
