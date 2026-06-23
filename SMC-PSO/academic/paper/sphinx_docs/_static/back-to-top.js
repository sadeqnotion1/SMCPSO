/**
 * ============================================================================
 * DIP-SMC-PSO Documentation - Back to Top Button
 * ============================================================================
 * Provides smooth scroll-to-top functionality for improved navigation on
 * long documentation pages.
 */

(function() {
    'use strict';

    /**
     * Initialize Back to Top button functionality
     */
    function initBackToTop() {
        // Create back to top button element
        const backToTop = document.createElement('div');
        backToTop.className = 'back-to-top';
        backToTop.innerHTML = '↑';
        backToTop.setAttribute('title', 'Back to top');
        backToTop.setAttribute('role', 'button');
        backToTop.setAttribute('aria-label', 'Scroll to top');
        backToTop.setAttribute('tabindex', '0');

        // Append to body
        document.body.appendChild(backToTop);

        // Show/hide button based on scroll position
        let scrollTimeout;
        function handleScroll() {
            // Debounce scroll events for better performance
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;

                if (scrollPosition > 300) {
                    backToTop.classList.add('show');
                } else {
                    backToTop.classList.remove('show');
                }
            }, 50);
        }

        // Smooth scroll to top functionality
        function scrollToTop(event) {
            event.preventDefault();

            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });

            // Focus management for accessibility
            setTimeout(() => {
                // Focus on main content or first heading after scroll
                const mainContent = document.querySelector('main h1, article h1, .document h1');
                if (mainContent) {
                    mainContent.setAttribute('tabindex', '-1');
                    mainContent.focus();
                    mainContent.removeAttribute('tabindex');
                }
            }, 500);
        }

        // Event listeners
        window.addEventListener('scroll', handleScroll, { passive: true });
        backToTop.addEventListener('click', scrollToTop);

        // Keyboard accessibility (Enter or Space key)
        backToTop.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                scrollToTop(event);
            }
        });

        // Initial check
        handleScroll();
    }

    /**
     * Make table of contents sticky on long pages
     */
    function makeTOCSticky() {
        const toc = document.querySelector('.toc-tree, .contents.local, nav.contents');

        if (toc && !toc.classList.contains('toc-scroll')) {
            // Only apply if page is long enough
            const pageHeight = document.documentElement.scrollHeight;
            const viewportHeight = window.innerHeight;

            if (pageHeight > viewportHeight * 2) {
                toc.classList.add('toc-scroll');
            }
        }
    }

    /**
     * Enhance download links with better styling
     */
    function enhanceDownloadLinks() {
        const downloadLinks = document.querySelectorAll('a.download, a[download]');

        downloadLinks.forEach(link => {
            if (!link.classList.contains('download-link')) {
                link.classList.add('download-link');
            }
        });
    }

    /**
     * Add smooth scroll behavior to all internal links
     */
    function addSmoothScrollToInternalLinks() {
        const internalLinks = document.querySelectorAll('a[href^="#"]');

        internalLinks.forEach(link => {
            link.addEventListener('click', function(event) {
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    event.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });

                    // Update URL without jumping
                    if (history.pushState) {
                        history.pushState(null, null, '#' + targetId);
                    }
                }
            });
        });
    }

    /**
     * Initialize reading progress bar
     */
    function initReadingProgress() {
        // Create progress bar element
        const progressBar = document.createElement('div');
        progressBar.className = 'reading-progress';
        progressBar.setAttribute('role', 'progressbar');
        progressBar.setAttribute('aria-label', 'Reading progress');
        progressBar.setAttribute('aria-valuenow', '0');
        progressBar.setAttribute('aria-valuemin', '0');
        progressBar.setAttribute('aria-valuemax', '100');
        document.body.appendChild(progressBar);

        // Update progress on scroll
        function updateProgress() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;

            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', Math.round(progress).toString());
        }

        // Debounced scroll handler
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(updateProgress, 50);
        }, { passive: true });

        // Initial update
        updateProgress();

        console.log('Reading progress bar initialized');
    }

    /**
     * Highlight active section in TOC
     */
    function initTOCHighlighting() {
        const tocLinks = document.querySelectorAll('.toc-scroll a[href^="#"], .contents.local a[href^="#"]');

        if (tocLinks.length === 0) {
            console.log('No TOC links found for highlighting');
            return;
        }

        // Get all sections referenced in TOC
        const sections = Array.from(tocLinks).map(link => {
            const id = link.getAttribute('href').substring(1);
            return {
                element: document.getElementById(id),
                link: link,
                id: id
            };
        }).filter(item => item.element !== null);

        if (sections.length === 0) return;

        function updateActiveTOC() {
            const scrollPos = window.pageYOffset + 100; // Offset for header

            // Find current section
            let activeSection = null;
            for (const section of sections) {
                if (section.element.offsetTop <= scrollPos) {
                    activeSection = section;
                } else {
                    break;
                }
            }

            // Update TOC links
            sections.forEach(section => {
                if (activeSection && section.id === activeSection.id) {
                    section.link.classList.add('active');
                    section.link.setAttribute('aria-current', 'location');
                } else {
                    section.link.classList.remove('active');
                    section.link.removeAttribute('aria-current');
                }
            });

            // Scroll TOC to show active item
            if (activeSection && activeSection.link) {
                const tocContainer = activeSection.link.closest('.toc-scroll, .contents.local');
                if (tocContainer) {
                    const linkRect = activeSection.link.getBoundingClientRect();
                    const containerRect = tocContainer.getBoundingClientRect();

                    // If link is outside visible area, scroll it into view
                    if (linkRect.top < containerRect.top || linkRect.bottom > containerRect.bottom) {
                        activeSection.link.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
                    }
                }
            }
        }

        // Throttled scroll handler
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(updateActiveTOC, 100);
        }, { passive: true });

        // Initial update
        updateActiveTOC();

        console.log(`TOC highlighting initialized for ${sections.length} sections`);
    }

    /**
     * Initialize all enhancements when DOM is ready
     */
    function init() {
        initBackToTop();
        makeTOCSticky();
        enhanceDownloadLinks();
        addSmoothScrollToInternalLinks();
        initReadingProgress();
        initTOCHighlighting();

        console.log('DIP-SMC-PSO Documentation enhancements loaded');
    }

    // Run initialization when DOM is fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // DOM already loaded
        init();
    }

})();
