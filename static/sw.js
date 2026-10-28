// Jungwon AI Student Assistant - Service Worker (PWA)
const CACHE_NAME = 'jungwon-ai-app-v4';
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/static/icon.svg',
  '/health',
  '/api/calendar'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  // Pass API requests directly to network first with cache fallback
  if (e.request.url.includes('/api/')) {
    e.respondWith(
      fetch(e.request).catch(() => {
        return new Response(JSON.stringify({ error: '오프라인 상태입니다.' }), {
          headers: { 'Content-Type': 'application/json' }
        });
      })
    );
    return;
  }

  e.respondWith(
    caches.match(e.request).then((cachedResponse) => {
      return cachedResponse || fetch(e.request).then((networkResponse) => {
        return networkResponse;
      });
    })
  );
});
