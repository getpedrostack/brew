/* Service worker — app shell offline, amigável a updates. Só ativa em http(s). */
const CACHE = 'wbrc-shell-v2';
const ASSETS = [
  './brew.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './icon-180.png',
  './icon-32.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const isDoc = req.mode === 'navigate' || req.destination === 'document' || url.pathname.endsWith('.html');

  if (isDoc) {
    // network-first: versão mais nova quando online; cache como fallback offline
    e.respondWith(
      fetch(req).then(resp => {
        const copy = resp.clone();
        caches.open(CACHE).then(c => c.put(req, copy));
        return resp;
      }).catch(() => caches.match(req).then(h => h || caches.match('./brew.html')))
    );
    return;
  }

  // demais GET: stale-while-revalidate (rápido + atualiza em segundo plano)
  e.respondWith(
    caches.match(req).then(hit => {
      const net = fetch(req).then(resp => {
        if (url.origin === location.origin) {
          const copy = resp.clone();
          caches.open(CACHE).then(c => c.put(req, copy));
        }
        return resp;
      }).catch(() => hit);
      return hit || net;
    })
  );
});
