# Hardy Boys Collection (PWA)

Static site: `index.html` (app + embedded checklist data), `manifest.webmanifest`, `sw.js`, icons.
Host the folder on any HTTPS static host (GitHub Pages, Netlify, Cloudflare Pages). Open in Safari on iPhone → Share → Add to Home Screen.

- Data: IndexedDB on the device (localStorage fallback). Backup via JSON export/import; CSV exports for copies and full checklist.
- Rebuild after editing: `python3 tools/build_data.py && python3 tools/build.py` (sources in `src/`, template in `tools/index.src.html`).
- Important: browser storage is tied to the site's URL. Pick the permanent URL before entering real data, or export/import a backup when moving.
