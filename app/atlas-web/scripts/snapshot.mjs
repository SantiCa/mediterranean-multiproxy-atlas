// Public data of the atlas as static Workers assets (no database reads): catalogue,
// one observation file per comparison group and the site inventory. Built from the
// newest versioned seed. Usage: node scripts/snapshot.mjs <seed.json> <outDir> [inventory.json]
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { groupKey } from "../lib/proxies.mjs";
import { applyQc } from "../lib/qc-corrections.mjs";

const [seedPath, out, inventoryPath] = process.argv.slice(2);
if (!seedPath || !out) throw new Error("uso: snapshot.mjs <seed.json> <outDir>");
const rawSeed = JSON.parse(readFileSync(seedPath, "utf8"));
const qcPath = fileURLToPath(new URL("../../../config/qc_corrections.json", import.meta.url));
const qcFile = existsSync(qcPath) ? JSON.parse(readFileSync(qcPath, "utf8")) : {};
// A newer file number must not hide fresh data curated into its parent release.
// Check before replacing the checked snapshot, so a stale v6 never publishes
// silently after v5 changes in another curation session.
const parentNumber = rawSeed.parent_version?.match(/-v(\d+)-/)?.[1];
if (parentNumber) {
  const parentPath = join(dirname(seedPath), `atlas-v${parentNumber}.json`);
  if (existsSync(parentPath) && JSON.parse(readFileSync(parentPath, "utf8")).version !== rawSeed.parent_version)
    throw new Error("Release padre modificada: regenerar la colección más reciente antes de crear el snapshot");
}
// Publication QC (config/qc_corrections.json): traceable, seed untouched.
const { seed, qc } = applyQc(rawSeed, qcFile);
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
    qc,
  }),
);
// Site inventory (tab «Sondeos»), queried in the browser by lib/inventory-local.mjs.
if (inventoryPath) writeFileSync(join(out, "inventory.json"), readFileSync(inventoryPath));
console.log(`snapshot ${seed.version}: ${series.length} series, ${groups.size} grupos, ${total} valores`);
