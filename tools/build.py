import json, hashlib, pathlib
root = pathlib.Path('/workspace/hardyboys')
data = json.loads((root/'tools/data.json').read_text())
src = (root/'tools/index.src.html').read_text()
djs = json.dumps(data, ensure_ascii=False, separators=(',',':')).replace('</', '<\\/')
ver = '1.1-' + hashlib.sha1((src+djs).encode()).hexdigest()[:8]
html = src.replace('/*DATA*/', djs).replace('/*VERSION*/', ver)
(root/'index.html').write_text(html)
(root/'manifest.webmanifest').write_text(json.dumps({
 "name":"Hardy Boys Collection","short_name":"Hardy Shelf","description":"Catalog your Hardy Boys book collection: originals, revised texts, digests, Casefiles and more.",
 "start_url":"./","scope":"./","display":"standalone","orientation":"portrait","background_color":"#f7f1e1","theme_color":"#14213d",
 "icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png"},{"src":"icon-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]}, indent=1))
(root/'sw.js').write_text(f"""// Hardy Boys Collection service worker (offline app shell)
const CACHE='hb-{ver}';
const ASSETS=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon-maskable-512.png','./apple-touch-icon.png'];
self.addEventListener('install',e=>{{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()))}});
self.addEventListener('activate',e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});
self.addEventListener('fetch',e=>{{
  if(e.request.method!=='GET'||new URL(e.request.url).origin!==location.origin)return;
  // network-first for the page (so updates arrive), cache fallback offline; cache-first for static assets
  if(e.request.mode==='navigate'){{e.respondWith(fetch(e.request).then(r=>{{const cp=r.clone();caches.open(CACHE).then(c=>c.put('./index.html',cp));return r}}).catch(()=>caches.match('./index.html')));return}}
  e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));
}});
""")
print('built', ver, len(html))
