/* 선택 사항: index.html 과 같은 폴더에 두면 오프라인에서도 앱이 열립니다.
   (없어도 앱은 정상 동작합니다.)

   전략은 네트워크 우선입니다. 항상 서버에서 최신을 먼저 받아오고,
   인터넷이 끊겼을 때만 캐시를 씁니다. 캐시 우선으로 두면 새로 배포해도
   방문자에게 옛날 화면이 계속 보이기 때문입니다. */
const CACHE = "smishing-v2";
const ASSETS = ["./", "./index.html"];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(ASSETS))
      .catch(() => {})
      .then(() => self.skipWaiting())
  );
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
  if(new URL(e.request.url).origin !== self.location.origin) return;

  e.respondWith(
    fetch(e.request)
      .then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
        return res;
      })
      .catch(() => caches.match(e.request).then(hit => hit || caches.match("./index.html")))
  );
});
