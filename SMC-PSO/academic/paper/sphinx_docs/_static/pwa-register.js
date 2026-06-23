/**
 * ============================================================================
 * PWA REGISTRATION & MANAGEMENT
 * ============================================================================
 *
 * Handles Progressive Web App functionality:
 *   - Service worker registration and lifecycle
 *   - Update detection and notifications
 *   - Install prompt management
 *   - Offline/online status monitoring
 *   - Cache management utilities
 *
 * Browser Support: Chrome 40+, Firefox 44+, Safari 11.1+, Edge 17+
 * ============================================================================
 */

(function() {
  'use strict';

  // ============================================================================
  // Configuration
  // ============================================================================

  const CONFIG = {
    serviceWorkerPath: '/sw.js',
    updateCheckInterval: 60 * 60 * 1000, // Check for updates every hour
    installPromptDelay: 30 * 1000, // Show install prompt after 30 seconds
    toastDuration: 8000, // Toast notification duration (8 seconds)
  };

  // ============================================================================
  // State Management
  // ============================================================================

  const state = {
    registration: null,
    deferredInstallPrompt: null,
    isOnline: navigator.onLine,
    isUpdateAvailable: false,
    swVersion: null,
  };

  // ============================================================================
  // DOM Ready Initialization
  // ============================================================================

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    console.log('[PWA] Initializing Progressive Web App features...');

    // Check browser support
    if (!('serviceWorker' in navigator)) {
      console.warn('[PWA] Service workers are not supported in this browser');
      return;
    }

    // Register service worker
    registerServiceWorker();

    // Setup event listeners
    setupNetworkListeners();
    setupInstallPromptListener();
    setupVisibilityListener();

    // Initialize UI
    createOfflineIndicator();
    createUpdateNotification();
    createInstallButton();

    console.log('[PWA] Initialization complete');
  }

  // ============================================================================
  // Service Worker Registration
  // ============================================================================

  async function registerServiceWorker() {
    try {
      console.log('[PWA] Registering service worker:', CONFIG.serviceWorkerPath);

      const registration = await navigator.serviceWorker.register(CONFIG.serviceWorkerPath, {
        scope: '/',
        updateViaCache: 'none', // Always check for updates
      });

      state.registration = registration;
      console.log('[PWA] Service worker registered successfully');

      // Handle service worker updates
      registration.addEventListener('updatefound', handleUpdateFound);

      // Check for updates periodically
      setInterval(() => {
        registration.update();
      }, CONFIG.updateCheckInterval);

      // Listen for messages from service worker
      navigator.serviceWorker.addEventListener('message', handleSWMessage);

      // Check if there's an update waiting
      if (registration.waiting) {
        showUpdateNotification();
      }

      // Handle controller change (new SW activated)
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        console.log('[PWA] New service worker activated, reloading page...');
        window.location.reload();
      });

    } catch (error) {
      console.error('[PWA] Service worker registration failed:', error);
    }
  }

  function handleUpdateFound() {
    console.log('[PWA] Update found! Installing new service worker...');

    const installingWorker = state.registration.installing;

    installingWorker.addEventListener('statechange', () => {
      if (installingWorker.state === 'installed') {
        if (navigator.serviceWorker.controller) {
          // New update available
          console.log('[PWA] New version available');
          state.isUpdateAvailable = true;
          showUpdateNotification();
        } else {
          // First install
          console.log('[PWA] Service worker installed for the first time');
        }
      }
    });
  }

  function handleSWMessage(event) {
    const { type, version } = event.data;

    console.log('[PWA] Message from service worker:', type, version);

    if (type === 'SW_ACTIVATED') {
      state.swVersion = version;
      console.log('[PWA] Service worker activated, version:', version);
    }
  }

  // ============================================================================
  // Update Notification
  // ============================================================================

  function createUpdateNotification() {
    const toast = document.createElement('div');
    toast.id = 'pwa-update-toast';
    toast.className = 'pwa-toast pwa-toast-hidden';
    toast.innerHTML = `
      <div class="pwa-toast-content">
        <span class="pwa-toast-icon">&#128257;</span>
        <div class="pwa-toast-text">
          <strong>New version available!</strong>
          <p>Click to update and get the latest features</p>
        </div>
        <button class="pwa-toast-button" onclick="window.PWA.updateApp()">
          Update Now
        </button>
        <button class="pwa-toast-close" onclick="window.PWA.dismissUpdate()" aria-label="Dismiss">
          &times;
        </button>
      </div>
    `;
    document.body.appendChild(toast);
  }

  function showUpdateNotification() {
    const toast = document.getElementById('pwa-update-toast');
    if (toast) {
      toast.classList.remove('pwa-toast-hidden');
      toast.classList.add('pwa-toast-visible');
    }
  }

  function hideUpdateNotification() {
    const toast = document.getElementById('pwa-update-toast');
    if (toast) {
      toast.classList.remove('pwa-toast-visible');
      toast.classList.add('pwa-toast-hidden');
    }
  }

  // ============================================================================
  // Offline Indicator
  // ============================================================================

  function createOfflineIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'pwa-offline-indicator';
    indicator.className = 'pwa-offline-indicator';
    indicator.innerHTML = `
      <span class="pwa-offline-icon">&#128268;</span>
      <span class="pwa-offline-text">Offline Mode</span>
    `;
    document.body.appendChild(indicator);

    updateOfflineIndicator();
  }

  function updateOfflineIndicator() {
    const indicator = document.getElementById('pwa-offline-indicator');
    if (!indicator) return;

    if (state.isOnline) {
      indicator.classList.remove('pwa-offline-visible');
    } else {
      indicator.classList.add('pwa-offline-visible');
    }
  }

  // ============================================================================
  // Install Prompt
  // ============================================================================

  function createInstallButton() {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      console.log('[PWA] App is already installed');
      return;
    }

    // Create install button (hidden by default)
    const button = document.createElement('button');
    button.id = 'pwa-install-button';
    button.className = 'pwa-install-button pwa-install-hidden';
    button.innerHTML = `
      <span class="pwa-install-icon">&#128190;</span>
      <span class="pwa-install-text">Install App</span>
    `;
    button.addEventListener('click', promptInstall);

    // Add to page (find suitable location or append to body)
    const header = document.querySelector('header') || document.querySelector('.wy-nav-top');
    if (header) {
      header.appendChild(button);
    } else {
      document.body.appendChild(button);
    }

    // Show button after delay if install prompt is available
    if (state.deferredInstallPrompt) {
      setTimeout(() => {
        showInstallButton();
      }, CONFIG.installPromptDelay);
    }
  }

  function setupInstallPromptListener() {
    window.addEventListener('beforeinstallprompt', (e) => {
      console.log('[PWA] Install prompt available');

      // Prevent default install prompt
      e.preventDefault();

      // Store for later use
      state.deferredInstallPrompt = e;

      // Show custom install button after delay
      setTimeout(() => {
        showInstallButton();
      }, CONFIG.installPromptDelay);
    });

    // Detect when app is installed
    window.addEventListener('appinstalled', () => {
      console.log('[PWA] App installed successfully!');
      state.deferredInstallPrompt = null;
      hideInstallButton();
      showToast('App installed successfully!', 'success');
    });
  }

  function showInstallButton() {
    const button = document.getElementById('pwa-install-button');
    if (button && state.deferredInstallPrompt) {
      button.classList.remove('pwa-install-hidden');
      button.classList.add('pwa-install-visible');
    }
  }

  function hideInstallButton() {
    const button = document.getElementById('pwa-install-button');
    if (button) {
      button.classList.remove('pwa-install-visible');
      button.classList.add('pwa-install-hidden');
    }
  }

  async function promptInstall() {
    if (!state.deferredInstallPrompt) {
      console.log('[PWA] Install prompt not available');
      return;
    }

    console.log('[PWA] Showing install prompt');

    // Show native install prompt
    state.deferredInstallPrompt.prompt();

    // Wait for user choice
    const { outcome } = await state.deferredInstallPrompt.userChoice;

    console.log('[PWA] Install prompt outcome:', outcome);

    if (outcome === 'accepted') {
      showToast('Installing app...', 'info');
    }

    // Clear prompt
    state.deferredInstallPrompt = null;
    hideInstallButton();
  }

  // ============================================================================
  // Network Status Monitoring
  // ============================================================================

  function setupNetworkListeners() {
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
  }

  function handleOnline() {
    console.log('[PWA] Connection restored');
    state.isOnline = true;
    updateOfflineIndicator();
    showToast('Connection restored', 'success');

    // Check for updates when back online
    if (state.registration) {
      state.registration.update();
    }
  }

  function handleOffline() {
    console.log('[PWA] Connection lost');
    state.isOnline = false;
    updateOfflineIndicator();
    showToast('Offline mode - cached content available', 'info');
  }

  // ============================================================================
  // Page Visibility (for update checks)
  // ============================================================================

  function setupVisibilityListener() {
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && state.registration) {
        // Check for updates when page becomes visible
        state.registration.update();
      }
    });
  }

  // ============================================================================
  // Toast Notifications
  // ============================================================================

  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `pwa-mini-toast pwa-mini-toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    // Show toast
    setTimeout(() => toast.classList.add('pwa-mini-toast-visible'), 100);

    // Hide and remove toast
    setTimeout(() => {
      toast.classList.remove('pwa-mini-toast-visible');
      setTimeout(() => toast.remove(), 300);
    }, CONFIG.toastDuration);
  }

  // ============================================================================
  // Public API
  // ============================================================================

  window.PWA = {
    // Update app (activate waiting service worker)
    updateApp: function() {
      console.log('[PWA] User requested app update');

      if (state.registration && state.registration.waiting) {
        // Tell waiting service worker to skip waiting
        state.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
        hideUpdateNotification();
      }
    },

    // Dismiss update notification
    dismissUpdate: function() {
      console.log('[PWA] User dismissed update notification');
      hideUpdateNotification();
    },

    // Manual install trigger
    install: function() {
      promptInstall();
    },

    // Get cache size estimation
    getCacheSize: async function() {
      if (!state.registration || !state.registration.active) {
        return null;
      }

      return new Promise((resolve) => {
        const messageChannel = new MessageChannel();
        messageChannel.port1.onmessage = (event) => {
          resolve(event.data.size);
        };

        state.registration.active.postMessage(
          { type: 'GET_CACHE_SIZE' },
          [messageChannel.port2]
        );
      });
    },

    // Clear all caches
    clearCache: async function() {
      if (!state.registration || !state.registration.active) {
        return false;
      }

      return new Promise((resolve) => {
        const messageChannel = new MessageChannel();
        messageChannel.port1.onmessage = (event) => {
          if (event.data.success) {
            showToast('Cache cleared successfully', 'success');
            resolve(true);
          } else {
            showToast('Failed to clear cache', 'error');
            resolve(false);
          }
        };

        state.registration.active.postMessage(
          { type: 'CLEAR_CACHE' },
          [messageChannel.port2]
        );
      });
    },

    // Get current state
    getState: function() {
      return {
        ...state,
        isInstalled: window.matchMedia('(display-mode: standalone)').matches,
        isSupported: 'serviceWorker' in navigator,
      };
    },
  };

  // ============================================================================
  // Export for debugging
  // ============================================================================

  console.log('[PWA] API available at window.PWA');
  console.log('[PWA] Commands:');
  console.log('  - PWA.updateApp(): Apply pending update');
  console.log('  - PWA.install(): Show install prompt');
  console.log('  - PWA.getCacheSize(): Get cache size in bytes');
  console.log('  - PWA.clearCache(): Clear all caches');
  console.log('  - PWA.getState(): Get current PWA state');

})();
