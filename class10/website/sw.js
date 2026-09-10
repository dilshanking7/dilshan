const CACHE_NAME = 'jac10-study-hub-v1';
const ASSETS = [
  './',
  './index.html',
  './quiz.html',
  './notes.html',
  './formulas.html',
  './subjects.html',
  './subject.html',
  './periodic.html',
  './lab.html',
  './mathlab.html',
  './practical.html',
  './diagrams.html',
  './stories.html',
  './history.html',
  './pdf.html',
  './css/style.css',
  './js/common.js',
  './js/data.js',
  './js/allquestions.js',
  './js/quiz.js',
  './js/explain.js',
  './js/lang.js',
  './manifest.json'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request).then((res) => {
      if (res.ok && e.request.method === 'GET') {
        const clone = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(e.request, clone));
      }
      return res;
    }).catch(() => caches.match('./index.html')))
  );
});
