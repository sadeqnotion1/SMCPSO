/**
 * ============================================================================
 * DIP-SMC-PSO Documentation - Dark Mode Toggle
 * ============================================================================
 * Provides user-selectable dark mode with localStorage persistence.
 * Respects system preferences and allows manual override.
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'dip-smc-pso-theme';
    const THEMES = {
        LIGHT: 'light',
        DARK: 'dark',
        AUTO: 'auto'
    };

    /**
     * Initialize dark mode toggle
     */
    function initDarkMode() {
        // Create toggle button
        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle';
        toggle.setAttribute('aria-label', 'Toggle dark mode');
        toggle.setAttribute('title', 'Toggle dark/light theme');
        toggle.innerHTML = `
            <span class="theme-icon light" aria-hidden="true">🌙</span>
            <span class="theme-icon dark" aria-hidden="true">☀️</span>
        `;

        // Add to page (top-right corner)
        document.body.appendChild(toggle);

        // Load saved preference or detect system preference
        const savedTheme = localStorage.getItem(STORAGE_KEY);
        const initialTheme = savedTheme || detectSystemTheme();

        applyTheme(initialTheme);

        // Toggle on click
        toggle.addEventListener('click', toggleTheme);

        // Listen for system theme changes (optional)
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                // Only apply if user hasn't manually set a theme
                if (!localStorage.getItem(STORAGE_KEY)) {
                    applyTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
                }
            });
        }

        console.log('Dark mode initialized with theme:', initialTheme);
    }

    /**
     * Detect system color scheme preference
     */
    function detectSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return THEMES.DARK;
        }
        return THEMES.LIGHT;
    }

    /**
     * Toggle between light and dark themes
     */
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK;

        applyTheme(newTheme);
        localStorage.setItem(STORAGE_KEY, newTheme);

        // Announce theme change for screen readers
        announceThemeChange(newTheme);
    }

    /**
     * Apply theme to document
     */
    function applyTheme(theme) {
        // Validate theme
        if (!Object.values(THEMES).includes(theme)) {
            theme = THEMES.LIGHT;
        }

        // Set theme attribute on document root
        document.documentElement.setAttribute('data-theme', theme);

        // Update toggle button state
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.setAttribute('data-theme', theme);

            // Update aria-label
            const label = theme === THEMES.DARK ?
                'Switch to light mode' :
                'Switch to dark mode';
            toggle.setAttribute('aria-label', label);
            toggle.setAttribute('title', label);
        }

        // Update meta theme-color for browser UI
        updateMetaThemeColor(theme);
    }

    /**
     * Update meta theme-color tag for mobile browser UI
     */
    function updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');

        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }

        // Set theme color based on current theme
        const color = theme === THEMES.DARK ? '#1a1a1a' : '#ffffff';
        metaThemeColor.setAttribute('content', color);
    }

    /**
     * Announce theme change for screen readers
     */
    function announceThemeChange(theme) {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'sr-only';  // Screen reader only
        announcement.textContent = `Theme switched to ${theme} mode`;

        document.body.appendChild(announcement);

        // Remove after announcement
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    /**
     * Add keyboard shortcut for theme toggle (Ctrl+Shift+D)
     */
    function initKeyboardShortcut() {
        document.addEventListener('keydown', (event) => {
            // Ctrl+Shift+D (or Cmd+Shift+D on Mac)
            if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'D') {
                event.preventDefault();
                toggleTheme();
            }
        });

        console.log('Dark mode keyboard shortcut enabled (Ctrl+Shift+D)');
    }

    /**
     * Initialize when DOM is ready
     */
    function init() {
        initDarkMode();
        initKeyboardShortcut();

        console.log('DIP-SMC-PSO Dark Mode loaded');
    }

    // Run initialization when DOM is fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // DOM already loaded
        init();
    }

})();
