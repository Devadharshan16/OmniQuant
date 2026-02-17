/* eslint-disable no-restricted-globals */

const CACHE_NAME = 'omniquant-v2-cache-v1';
const API_CACHE_NAME = 'omniquant-api-cache-v1';

// Core files to cache for offline functionality
const CORE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
];

// Install event - cache core assets
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[ServiceWorker] Caching core assets');
      return cache.addAll(CORE_ASSETS).catch((err) => {
        console.warn('[ServiceWorker] Some assets failed to cache:', err);
        // Don't fail installation if some assets aren't available yet
      });
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME) {
            console.log('[ServiceWorker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - network first for API, cache first for assets
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API requests - network first with cache fallback
  // Check if URL is to an API endpoint (different origin or contains /api/)
  const isApiRequest = 
    url.pathname.includes('/api/') || 
    url.pathname.includes('/quick_scan') ||
    url.pathname.includes('/health') ||
    url.pathname.includes('/metrics') ||
    (url.origin !== self.location.origin && !url.pathname.endsWith('.js') && !url.pathname.endsWith('.css'));

  if (isApiRequest) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Clone response and cache it
          const responseClone = response.clone();
          caches.open(API_CACHE_NAME).then((cache) => {
            cache.put(request, responseClone);
          });
          return response;
        })
        .catch(() => {
          // Network failed, try cache
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              console.log('[ServiceWorker] Serving API from cache:', request.url);
              return cachedResponse;
            }
            // Return offline response
            return new Response(
              JSON.stringify({
                success: false,
                error: 'Offline - cached data not available',
                offline: true
              }),
              {
                headers: { 'Content-Type': 'application/json' }
              }
            );
          });
        })
    );
    return;
  }

  // App assets - cache first with network fallback
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      // Not in cache, fetch from network
      return fetch(request).then((response) => {
        // Don't cache non-successful responses
        if (!response || response.status !== 200 || response.type === 'error') {
          return response;
        }

        // Clone and cache for future
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(request, responseClone);
        });

        return response;
      });
    })
  );
});

// Listen for messages from the app
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(cacheNames.map((cacheName) => caches.delete(cacheName)));
      }).then(() => {
        event.ports[0].postMessage({ success: true });
      })
    );
  }
});
