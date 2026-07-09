const CACHE_NAME = 'rhythm-preview-v71';
const PRECACHE = [
  './rhythm-favicon-32.png',
  './rhythm-apple-touch.png',
  './rhythm-icon-192.png',
  './rhythm-icon-512.png',
  './rythm-wordmark.png',
  './rythm-splash-mark.svg',
  './rythm-r-mark.png',
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
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  // Always hit the network for app shell so copy/UI fixes show immediately.
  if (isHtmlOrWorker(event.request, url)) {
    event.respondWith(
      fetch(event.request, { cache: 'no-store' }).catch(() => caches.match('./index.html'))
    );
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.ok && url.origin === self.location.origin) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        }
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
