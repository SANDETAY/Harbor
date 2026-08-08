/* Harbor service worker — cache-bust + activate promptly for testers.
 * Capacitor iOS does not rely on this; web/PWA does.
 */
const CACHE_NAME = 'harbor-v547';

self.addEventListener('install', (event) => {
  // Activate new SW immediately on install
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)));
      await self.clients.claim();
    })()
  );
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Network-only: always fetch live app shell (avoid stale multi-MB index.html)
self.addEventListener('fetch', (event) => {
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
