const CACHE_NAME = 'harbor-preview-v136';
const PRECACHE = [
  './harbor-favicon-32.png',
  './harbor-apple-touch.png',
  './harbor-icon-192.png',
  './harbor-icon-512.png',
  './harbor-mark.png',
  './harbor-mark.svg',
  './harbor-splash-anchor.png',
  './harbor-fab-anchor.png',
  './manifest.webmanifest'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

function isHtmlOrWorker(request, url) {
  if (request.mode === 'navigate') return true;
  const path = url.pathname.toLowerCase();
  return path.endsWith('.html') || path.endsWith('/sw.js') || path.endsWith('sw.js') || path.endsWith('/');
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // HTML + SW: network-first so UI copy and shell updates ship immediately
  if (isHtmlOrWorker(request, url)) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Static assets: cache-first, refresh in background
  event.respondWith(
    caches.match(request).then((cached) => {
      const network = fetch(request)
        .then((response) => {
          if (response && response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
