// Cell-by-cell check that the static snapshot reproduces the versioned seed, plus
// Workers static-asset limits (≤ 25 MiB per file, ≤ 20 000 files on Free).
// Usage: node scripts/check-snapshot.mjs <seed.json> <snapshotDir>
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { groupKey } from "../lib/proxies.mjs";
const [seedPath, dir] = process.argv.slice(2);
const seed = JSON.parse(readFileSync(seedPath, "utf8"));
const cat = JSON.parse(readFileSync(join(dir, "catalog.json"), "utf8"));
const fail = (m) => {
  console.error("::error title=Instantánea::" + m);
  process.exit(1);
};
if (cat.release.id !== seed.version) fail("versión distinta");
if (cat.records.length !== seed.records.length || cat.series.length !== seed.series.length) fail("recuentos distintos");
if (cat.series.some((s) => s.rows.length)) fail("el catálogo no debe llevar observaciones");
const want = new Map(seed.series.map((s) => [s.id, s]));
let cells = 0, files = 0, biggest = 0;
for (const [key, file] of Object.entries(cat.snapshot.groups)) {
  const path = join(dir, "obs", file), size = statSync(path).size;
  biggest = Math.max(biggest, size);
  const g = JSON.parse(readFileSync(path, "utf8"));
  if (g.group !== key || g.version !== seed.version) fail("cabecera de " + file);
  for (const s of g.series) {
    const w = want.get(s.id);
    if (!w || groupKey(w) !== key) fail("serie ajena " + s.id);
    const a = new Map(s.rows.map((r) => [r[2], JSON.stringify(r)]));
    if (a.size !== w.rows.length || w.rows.some((r) => a.get(r[2]) !== JSON.stringify(r))) fail("valores distintos en " + s.id);
    const { rows, ...m } = s, { rows: _, ...n } = w;
    if (JSON.stringify(m) !== JSON.stringify(n)) fail("metadatos distintos en " + s.id);
    cells += s.rows.length;
    want.delete(s.id);
  }
  files++;
}
if (want.size) fail(want.size + " series sin archivo");
const count = (d) => readdirSync(d, { withFileTypes: true }).reduce((n, e) => n + (e.isDirectory() ? count(join(d, e.name)) : 1), 0);
const total = count(dir);
if (biggest > 25 * 2 ** 20) fail("archivo > 25 MiB");
if (total > 19000) fail("demasiados archivos estáticos (" + total + ")");
console.log(`OK ${seed.version}: ${cells} valores comparados celda a celda, ${files} grupos, ${total} archivos, máx. ${(biggest / 2 ** 20).toFixed(1)} MiB`);
