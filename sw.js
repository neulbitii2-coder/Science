/* 선택 사항: index.html 과 같은 폴더에 두면 오프라인에서도 앱이 열립니다.
   (없어도 앱은 정상 동작합니다 — index.html 이 있을 때만 등록합니다.) */
const CACHE = "smishing-v1";
const ASSETS = ["./", "./index.html"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  if(e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then(hit =>
      hit || fetch(e.request)
        .then(res => {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match("./index.html"))
    )
  );
});
