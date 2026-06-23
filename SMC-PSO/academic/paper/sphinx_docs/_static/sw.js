/**
 * ============================================================================
 * SERVICE WORKER - Progressive Web App (PWA) Support
 * ============================================================================
 *
 * Phase 6: Offline Documentation Access
 *
 * Caching Strategy:
 *   - HTML pages: Network-first (always fresh when online)
 *   - Static assets (CSS, JS): Cache-first (performance)
 *   - Images/fonts: Cache-first with network fallback
 *   - External CDN: Cache-first for Pyodide, Plotly, Three.js
 *
 * Features:
 *   - Offline documentation access (15-20MB cache)
 *   - Background updates for new versions
 *   - Automatic cache cleanup on activation
 *   - Offline page fallback for uncached content
 *
 * Browser Support: Chrome 40+, Firefox 44+, Safari 11.1+, Edge 17+
 * ============================================================================
 */

// ============================================================================
// Cache Configuration
// ============================================================================

const CACHE_VERSION = 'v1.6.0'; // Phase 6 - PWA
const CACHE_NAME = `dip-smc-docs-${CACHE_VERSION}`;
const OFFLINE_CACHE = `offline-${CACHE_VERSION}`;

// Cache expiration: 30 days
const CACHE_EXPIRATION_MS = 30 * 24 * 60 * 60 * 1000;

// ============================================================================
// Assets to Precache (Core Documentation)
// ============================================================================

const PRECACHE_URLS = [
  // Core HTML pages
  '/index.html',
  '/guides/getting-started.html',
  '/guides/tutorials/tutorial-01-first-simulation.html',
  '/guides/theory/smc-theory.html',
  '/guides/interactive/index.html',
  '/guides/interactive/live-python-demo.html',
  '/guides/interactive/mathematical-visualizations-demo.html',
  '/api/index.html',
  '/reference/index.html',

  // Offline fallback page
  '/offline.html',

  // Core CSS (Sphinx theme)
  '/_static/pygments.css',
  '/_static/custom.css',

  // Phase 1: Visual Navigation & Control Room
  '/_static/visual-sitemap.js',
  '/_static/visual-tree.css',
  '/_static/control-room.js',
  '/_static/control-room.css',
  '/_static/code-collapse.js',
  '/_static/code-collapse.css',
  '/_static/threejs-pendulum.js',
  '/_static/threejs-pendulum.css',

  // Phase 2: Pyodide Live Python
  '/_static/pyodide-worker.js',
  '/_static/pyodide-runner.js',
  '/_static/code-runner.css',

  // Phase 3: Plotly Charts
  '/_static/plotly-integration.js',
  '/_static/plotly-charts.css',

  // Phase 5: Mathematical Visualizations
  '/_static/mathviz-interactive.js',
  '/_static/mathviz.css',

  // Phase 6: PWA
  '/_static/pwa-register.js',
  '/_static/pwa.css',

  // Core utilities
  '/_static/lazy-load.js',
  '/_static/dark-mode.js',
  '/_static/back-to-top.js',

  // Fonts and images (if any)
  // Add specific paths as needed
];

// ============================================================================
// External CDN Resources (Cache for offline)
// ============================================================================

const CDN_URLS = [
  // Three.js (Phase 1)
  'https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js',
  'https://cdn.jsdelivr.net/npm/three@0.158.0/examples/js/controls/OrbitControls.js',

  // Pyodide (Phase 2) - Core only, packages loaded on-demand
  'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js',
  'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.asm.js',
  'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.asm.data',
  'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.asm.wasm',

  // Plotly.js (Phase 3, reused in Phase 5)
  'https://cdn.plot.ly/plotly-2.27.0.min.js',
];

// ============================================================================
// Service Worker Install Event
// ============================================================================

self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker version:', CACHE_VERSION);

  event.waitUntil(
    (async () => {
      try {
        // Open cache
        const cache = await caches.open(CACHE_NAME);

        // Precache core documentation assets
        console.log('[SW] Precaching', PRECACHE_URLS.length, 'core assets...');
        await cache.addAll(PRECACHE_URLS);

        // Cache external CDN resources (with error handling)
        console.log('[SW] Caching', CDN_URLS.length, 'CDN resources...');
        for (const url of CDN_URLS) {
          try {
            await cache.add(url);
          } catch (error) {
            console.warn('[SW] Failed to cache CDN resource:', url, error);
            // Continue even if CDN caching fails (graceful degradation)
          }
        }

        // Create offline cache with fallback page
        const offlineCache = await caches.open(OFFLINE_CACHE);
        await offlineCache.add('/offline.html');

        console.log('[SW] Precaching complete. Skip waiting...');

        // Force activation immediately (no waiting for old SW to close)
        await self.skipWaiting();

      } catch (error) {
        console.error('[SW] Install failed:', error);
        throw error;
      }
    })()
  );
});

// ============================================================================
// Service Worker Activate Event
// ============================================================================

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker version:', CACHE_VERSION);

  event.waitUntil(
    (async () => {
      try {
        // Get all cache names
        const cacheNames = await caches.keys();

        // Delete old caches (except current version)
        const cachesToDelete = cacheNames.filter((cacheName) => {
          return cacheName.startsWith('dip-smc-docs-') && cacheName !== CACHE_NAME ||
                 cacheName.startsWith('offline-') && cacheName !== OFFLINE_CACHE;
        });

        if (cachesToDelete.length > 0) {
          console.log('[SW] Deleting', cachesToDelete.length, 'old caches:', cachesToDelete);
          await Promise.all(cachesToDelete.map((cache) => caches.delete(cache)));
        }

        // Claim all clients immediately (no page reload required)
        console.log('[SW] Claiming clients...');
        await self.clients.claim();

        // Notify clients about successful activation
        const clients = await self.clients.matchAll();
        clients.forEach((client) => {
          client.postMessage({
            type: 'SW_ACTIVATED',
            version: CACHE_VERSION,
          });
        });

        console.log('[SW] Activation complete. Service worker ready.');

      } catch (error) {
        console.error('[SW] Activation failed:', error);
        throw error;
      }
    })()
  );
});

// ============================================================================
// Service Worker Fetch Event (Request Interception)
// ============================================================================

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome-extension and other non-http(s) requests
  if (!url.protocol.startsWith('http')) {
    return;
  }

  event.respondWith(
    (async () => {
      try {
        // Strategy selection based on content type
        if (isHTMLPage(url)) {
          return await networkFirstStrategy(request);
        } else if (isStaticAsset(url)) {
          return await cacheFirstStrategy(request);
        } else if (isCDNResource(url)) {
          return await cacheFirstStrategy(request);
        } else {
          // Default: network-first for everything else
          return await networkFirstStrategy(request);
        }
      } catch (error) {
        console.error('[SW] Fetch error:', request.url, error);

        // Fallback to offline page for HTML requests
        if (isHTMLPage(url)) {
          const offlineCache = await caches.open(OFFLINE_CACHE);
          const offlinePage = await offlineCache.match('/offline.html');
          if (offlinePage) {
            return offlinePage;
          }
        }

        // Return generic error response
        return new Response('Offline and resource not cached', {
          status: 503,
          statusText: 'Service Unavailable',
          headers: { 'Content-Type': 'text/plain' },
        });
      }
    })()
  );
});

// ============================================================================
// Caching Strategies
// ============================================================================

/**
 * Network-First Strategy
 * Try network first, fall back to cache if offline
 * Best for: HTML pages (always fresh content)
 */
async function networkFirstStrategy(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);

    // If successful, cache the response and return it
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }

    // If network response is invalid, try cache
    return await cacheFirstStrategy(request);

  } catch (error) {
    // Network failed (offline), try cache
    console.log('[SW] Network unavailable, using cache:', request.url);
    const cachedResponse = await caches.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    throw error; // Let outer handler deal with it
  }
}

/**
 * Cache-First Strategy
 * Check cache first, fall back to network if not cached
 * Best for: Static assets (CSS, JS, images)
 */
async function cacheFirstStrategy(request) {
  // Try cache first
  const cachedResponse = await caches.match(request);

  if (cachedResponse) {
    // Check cache age
    const cacheDate = new Date(cachedResponse.headers.get('date'));
    const now = new Date();
    const age = now - cacheDate;

    // If cache is fresh, return it
    if (age < CACHE_EXPIRATION_MS) {
      return cachedResponse;
    }

    // Cache is stale, try network update in background
    fetch(request).then((networkResponse) => {
      if (networkResponse && networkResponse.status === 200) {
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(request, networkResponse);
        });
      }
    }).catch(() => {
      // Network failed, but we have cached version
      console.log('[SW] Background update failed, using stale cache:', request.url);
    });

    // Return cached version immediately
    return cachedResponse;
  }

  // Not in cache, fetch from network and cache it
  const networkResponse = await fetch(request);

  if (networkResponse && networkResponse.status === 200) {
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, networkResponse.clone());
  }

  return networkResponse;
}

// ============================================================================
// URL Classification Helpers
// ============================================================================

function isHTMLPage(url) {
  return url.pathname.endsWith('.html') || url.pathname.endsWith('/');
}

function isStaticAsset(url) {
  const extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.gif', '.woff', '.woff2', '.ttf', '.eot'];
  return extensions.some((ext) => url.pathname.endsWith(ext));
}

function isCDNResource(url) {
  const cdnDomains = ['cdn.jsdelivr.net', 'cdn.plot.ly', 'unpkg.com'];
  return cdnDomains.some((domain) => url.hostname.includes(domain));
}

// ============================================================================
// Message Handler (Client Communication)
// ============================================================================

self.addEventListener('message', (event) => {
  console.log('[SW] Received message:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    // Client requested immediate update
    console.log('[SW] Client requested skip waiting');
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'CLEAR_CACHE') {
    // Client requested cache clear
    console.log('[SW] Client requested cache clear');
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => caches.delete(cacheName))
        );
      }).then(() => {
        event.ports[0].postMessage({ success: true });
      })
    );
  }

  if (event.data && event.data.type === 'GET_CACHE_SIZE') {
    // Client requested cache size estimation
    event.waitUntil(
      estimateCacheSize().then((size) => {
        event.ports[0].postMessage({ size });
      })
    );
  }
});

// ============================================================================
// Cache Size Estimation
// ============================================================================

async function estimateCacheSize() {
  let totalSize = 0;

  const cacheNames = await caches.keys();

  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const requests = await cache.keys();

    for (const request of requests) {
      const response = await cache.match(request);
      if (response) {
        const blob = await response.blob();
        totalSize += blob.size;
      }
    }
  }

  return totalSize;
}

// ============================================================================
// End of Service Worker
// ============================================================================

console.log('[SW] Service worker script loaded. Version:', CACHE_VERSION);
