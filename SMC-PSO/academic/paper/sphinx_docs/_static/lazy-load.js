/**
 * ============================================================================
 * DIP-SMC-PSO Documentation - Lazy Loading for Images
 * ============================================================================
 * Improves page load performance by deferring image loading until they enter
 * the viewport. Particularly beneficial for long documentation pages with
 * many diagrams and screenshots.
 */

(function() {
    'use strict';

    /**
     * Initialize lazy loading using Intersection Observer API
     */
    function initLazyLoading() {
        // Find all images that should be lazy-loaded
        const lazyImages = document.querySelectorAll('img[data-src]');

        if (lazyImages.length === 0) {
            console.log('Lazy-load: No images with data-src attribute found');
            return;
        }

        // Intersection Observer configuration
        const observerOptions = {
            root: null,  // viewport
            rootMargin: '50px',  // Start loading 50px before visible
            threshold: 0.01
        };

        // Create observer
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;

                    // Load the actual image
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');

                        // Add loading class for animation
                        img.classList.add('lazy-loading');

                        // Remove loading class when loaded
                        img.addEventListener('load', () => {
                            img.classList.remove('lazy-loading');
                            img.classList.add('lazy-loaded');
                        });

                        // Handle load errors
                        img.addEventListener('error', () => {
                            img.classList.remove('lazy-loading');
                            img.classList.add('lazy-error');
                        });
                    }

                    // Stop observing this image
                    observer.unobserve(img);
                }
            });
        }, observerOptions);

        // Observe all lazy images
        lazyImages.forEach(img => imageObserver.observe(img));

        console.log(`Lazy-load: Initialized for ${lazyImages.length} images`);
    }

    /**
     * Convert existing images to lazy-load (on very long pages)
     * Automatically enables for pages > 3x viewport height
     */
    function enableLazyLoadingOnLongPages() {
        const pageHeight = document.documentElement.scrollHeight;
        const viewportHeight = window.innerHeight;

        // Only enable on pages > 3x viewport height
        if (pageHeight > viewportHeight * 3) {
            const images = document.querySelectorAll('img:not([data-src])');
            let convertedCount = 0;

            images.forEach((img, index) => {
                // Skip first 5 images (above the fold - immediate loading)
                if (index < 5) return;

                // Skip images without src attribute
                if (!img.src || img.src === '') return;

                // Skip SVG placeholders
                if (img.src.startsWith('data:image/svg+xml')) return;

                // Convert to lazy-load
                img.dataset.src = img.src;
                // Use 1x1 transparent PNG placeholder
                img.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
                convertedCount++;
            });

            if (convertedCount > 0) {
                console.log(`Lazy-load: Converted ${convertedCount} images on long page (${Math.round(pageHeight/viewportHeight)}x viewport height)`);
            }
        }
    }

    /**
     * Fallback for browsers without Intersection Observer support
     */
    function initLazyLoadingFallback() {
        const lazyImages = document.querySelectorAll('img[data-src]');

        if (lazyImages.length === 0) return;

        console.log('Lazy-load: Using scroll-based fallback (Intersection Observer not supported)');

        function loadVisibleImages() {
            lazyImages.forEach(img => {
                if (isElementInViewport(img)) {
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        img.classList.add('lazy-loaded');
                    }
                }
            });
        }

        function isElementInViewport(el) {
            const rect = el.getBoundingClientRect();
            return (
                rect.top >= -100 &&
                rect.left >= -100 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) + 100 &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth) + 100
            );
        }

        // Check on scroll and resize
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(loadVisibleImages, 100);
        }, { passive: true });

        window.addEventListener('resize', loadVisibleImages);

        // Initial check
        loadVisibleImages();
    }

    /**
     * Initialize when DOM is ready
     */
    function init() {
        // Convert long pages automatically
        enableLazyLoadingOnLongPages();

        // Initialize lazy loading with observer or fallback
        if ('IntersectionObserver' in window) {
            initLazyLoading();
        } else {
            initLazyLoadingFallback();
        }
    }

    // Run initialization when DOM is fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // DOM already loaded
        init();
    }

})();
