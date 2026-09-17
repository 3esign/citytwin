// Zero-dependency static server for the CityTwin face.  node faces/serve.js [city] [port]
// Serves faces/web/ at /, and cities/<city>/data/layers/ at /layers/ (GeoJSON + summaries only).
const http = require('http'), fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..');
const city = process.argv[2] || 'trebinje', port = Number(process.argv[3]) || 4870;
const web = path.join(__dirname, 'web'), layers = path.join(root, 'cities', city, 'data', 'layers');
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.geojson': 'application/geo+json', '.csv': 'text/csv; charset=utf-8' };
http.createServer((req, res) => {
  const u = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  let file;
  if (u.startsWith('/layers/')) {
    file = path.join(layers, path.basename(u));
    if (!/\.(geojson|json|csv)$/.test(file)) { res.writeHead(403); return res.end(); }
  } else if (u === '/city.json') file = path.join(root, 'cities', city, 'city.json');
  else file = path.join(web, u === '/' ? 'index.html' : path.normalize(u).replace(/^([/\\])+/, ''));
  if (!file.startsWith(web) && !file.startsWith(layers) && !file.endsWith('city.json')) { res.writeHead(403); return res.end(); }
  fs.readFile(file, (e, d) => {
    if (e) { res.writeHead(404); return res.end('not found'); }
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-cache' });
    res.end(d);
  });
}).listen(port, () => console.log(`CityTwin face: http://localhost:${port}  (city ${city})`));
