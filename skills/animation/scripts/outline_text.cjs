// Outline text into SVG paths at build time, so text that moves, scales or sits under a camera move scales as
// geometry and never snaps to the pixel grid (live <text> and HTML text jitter by whole pixels under slow moves).
// Kerning and ligatures are applied (fontkit's layout). Runs on macOS and Windows.
//
// Usage:   node outline_text.cjs spec.json out.js
// spec:    { "<key>": ["<font file, relative to the spec or absolute>", "<string>"], ... }
// out.js:  window.GLYPHS = { "<key>": { d, adv, upm, asc, desc } }   (all in font units, y up)
//
// In the page (SVG), for a run at baseline (x, y) and font size `size` px:
//   <path d="${g.d}" transform="translate(x y) scale(${size/g.upm} ${-size/g.upm})"/>
//   width on screen = g.adv * size / g.upm   (centre: x - width/2, right-align: x - width)
//   cap/ascender height = g.asc * size / g.upm, descender = g.desc * size / g.upm (negative)
// Word-by-word builds: give each word its own key (and its x from the full line's advances if needed).
//
// fontkit: set FONTKIT=<path to the fontkit folder>, or `npm i fontkit` next to this script; otherwise the newest
// copy in the npx cache is used (hyperframes brings one): ~/.npm/_npx/*/node_modules/fontkit on macOS,
// %LOCALAPPDATA%\npm-cache\_npx\*\node_modules\fontkit on Windows.
const fs = require('fs'), path = require('path'), os = require('os');

function findFontkit() {
  if (process.env.FONTKIT) return process.env.FONTKIT;
  try { return require.resolve('fontkit'); } catch (e) {}
  const roots = [path.join(os.homedir(), '.npm', '_npx')];
  if (process.env.LOCALAPPDATA) roots.push(path.join(process.env.LOCALAPPDATA, 'npm-cache', '_npx'));
  if (process.env.APPDATA) roots.push(path.join(process.env.APPDATA, 'npm-cache', '_npx'));
  const found = [];
  for (const r of roots) {
    let dirs = [];
    try { dirs = fs.readdirSync(r); } catch (e) { continue; }
    for (const d of dirs) {
      const p = path.join(r, d, 'node_modules', 'fontkit');
      try { found.push([fs.statSync(p).mtimeMs, p]); } catch (e) {}
    }
  }
  if (!found.length) {
    console.error('fontkit not found. Run `npm i fontkit` in this folder, or set FONTKIT to its folder.');
    process.exit(1);
  }
  return found.sort((a, b) => b[0] - a[0])[0][1];
}

const [spec, out] = process.argv.slice(2);
if (!spec || !out) { console.error('Usage: node outline_text.cjs spec.json out.js'); process.exit(1); }
const fontkit = require(findFontkit());
const S = JSON.parse(fs.readFileSync(spec, 'utf8')), cache = {}, G = {};
for (const [k, [file, str]] of Object.entries(S)) {
  const fp = path.resolve(path.dirname(spec), file);
  const f = cache[fp] || (cache[fp] = fontkit.openSync(fp));
  const run = f.layout(str);
  let x = 0, d = '';
  run.glyphs.forEach((g, i) => {
    const p = run.positions[i];
    d += g.path.translate(x + p.xOffset, p.yOffset).toSVG();
    x += p.xAdvance;
  });
  G[k] = { d, adv: x, upm: f.unitsPerEm, asc: f.ascent, desc: f.descent };
}
fs.writeFileSync(out, 'window.GLYPHS=Object.assign(window.GLYPHS||{},' + JSON.stringify(G) + ');\n');
console.log(Object.keys(G).length + ' strings ->', out);
