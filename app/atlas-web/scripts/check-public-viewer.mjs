import assert from "node:assert/strict";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = fileURLToPath(new URL("../", import.meta.url));
const config = JSON.parse(readFileSync(join(appRoot, "wrangler.public.json"), "utf8"));
assert.deepEqual(Object.keys(config).sort(), [
  "assets", "compatibility_date", "name", "preview_urls", "workers_dev",
], "El despliegue público solo puede configurar archivos estáticos.");
assert.equal(config.name, "med", "La URL pública debe conservar el Worker med.");
assert.equal(config.workers_dev, true);
assert.equal(config.preview_urls, false);
assert.deepEqual(config.assets, { directory: "./dist-public", not_found_handling: "none" });
const output = join(appRoot, config.assets.directory);

function filePaths(directory, prefix = "") {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const relative = prefix + entry.name;
    const path = join(directory, entry.name);
    if (entry.isDirectory()) return filePaths(path, relative + "/");
    assert.ok(entry.isFile(), "Entrada no regular: " + relative);
    assert.ok(statSync(path).size <= 25 * 1024 * 1024, "Límite Free por archivo: " + relative);
    return [relative];
  });
}

const catalog = JSON.parse(readFileSync(join(output, "snapshot/catalog.json"), "utf8"));
assert.ok(
  [...catalog.records, ...catalog.series].every((entry) => !entry.private && !entry.id?.startsWith("private_") &&
    !entry.proxy?.startsWith("private_")),
  "El catálogo público contiene entradas privadas.",
);
const staticFiles = new Set([
  "index.html", "_headers", "favicon.svg", "geo/land.geojson",
  "vendor/leaflet/LICENSE", "vendor/leaflet/leaflet.css", "vendor/leaflet/leaflet.js",
  "snapshot/catalog.json", "snapshot/inventory.json",
  ...Object.values(catalog.snapshot.groups).map((file) => {
    assert.match(file, /^[0-9a-f]{16}\.json$/);
    return "snapshot/obs/" + file;
  }),
]);
const files = filePaths(output);
assert.ok(files.length <= 20_000, "Límite Free de archivos.");
for (const file of files) {
  if (staticFiles.delete(file)) continue;
  assert.match(file, /^assets\/[\w-]+\.(?:js|css|svg|png|woff2)$/, "Archivo inesperado en el visor público.");
}
assert.deepEqual([...staticFiles], [], "Faltan archivos previstos del catálogo.");
console.log(`Visor público verificado: ${files.length} archivos, ${catalog.release.id}, sin servidor ni enlaces a bases de datos.`);
