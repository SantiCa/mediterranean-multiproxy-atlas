// Static fallback served from Workers assets when D1 is unavailable (e.g. Free daily
// limit reached). Built from the newest versioned seed, never from D1, so values are
// the seed itself. Usage: node scripts/snapshot.mjs <seed.json> <outDir>
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { groupKey } from "../lib/proxies.mjs";

const [seedPath, out] = process.argv.slice(2);
if (!seedPath || !out) throw new Error("uso: snapshot.mjs <seed.json> <outDir>");
const seed = JSON.parse(readFileSync(seedPath, "utf8"));
rmSync(out, { recursive: true, force: true });
mkdirSync(join(out, "obs"), { recursive: true });

// Same order as the API: records by name, series by id, rows by age (nulls first) then source row.
const byStr = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
const records = [...seed.records].sort((a, b) => byStr(a.name, b.name));
const series = [...seed.series].sort((a, b) => byStr(a.id, b.id));
const rowOrder = (a, b) =>
  a[0] === b[0] ? a[2] - b[2] : a[0] === null ? -1 : b[0] === null ? 1 : a[0] - b[0];

const groups = new Map();
let total = 0;
for (const s of series) {
  const k = groupKey(s);
  if (!groups.has(k)) groups.set(k, []);
  groups.get(k).push({ ...s, rows: [...s.rows].sort(rowOrder) });
  total += s.rows.length;
}
const files = {};
for (const [k, list] of groups) {
  const file = createHash("sha1").update(k).digest("hex").slice(0, 16) + ".json";
  files[k] = file;
  writeFileSync(
    join(out, "obs", file),
    JSON.stringify({ version: seed.version, group: k, series: list }),
  );
}
const meta = series.map(({ rows, ...m }) => ({ ...m, rows: [] }));
writeFileSync(
  join(out, "catalog.json"),
  JSON.stringify({
    release: { id: seed.version, observation_count: total, imported_at: null },
    records,
    series: meta,
    snapshot: { groups: files },
  }),
);
console.log(`snapshot ${seed.version}: ${series.length} series, ${groups.size} grupos, ${total} valores`);
