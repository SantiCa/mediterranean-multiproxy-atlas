import { execFileSync } from "node:child_process";
import { copyFileSync, mkdirSync, realpathSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "vite";

const appRoot = fileURLToPath(new URL("../", import.meta.url));
const processed = realpathSync(join(appRoot, "../../data/processed"));
const seedArgument = process.argv[2];
if (!seedArgument) throw new Error("Uso: build-public-viewer.mjs <data/processed/atlas-vN.json>");

const seed = realpathSync(resolve(seedArgument));
if (dirname(seed) !== processed || !/^atlas-v\d+\.json$/.test(basename(seed)))
  throw new Error("Selecciona una versión curada en data/processed.");

const output = join(appRoot, "dist-public");
const snapshot = join(output, "snapshot");
const inventory = join(appRoot, "data/inventory.json");

function runScript(name, ...args) {
  execFileSync(process.execPath, [join(appRoot, "scripts", name), ...args], { stdio: "inherit" });
}

await build({ configFile: join(appRoot, "vite.public.config.ts") });
runScript("snapshot.mjs", seed, snapshot, inventory);
runScript("check-snapshot.mjs", seed, snapshot);

const files = [
  "favicon.svg",
  "geo/land.geojson",
  "vendor/leaflet/leaflet.css",
  "vendor/leaflet/leaflet.js",
  "vendor/leaflet/LICENSE",
];
for (const file of files) {
  const target = join(output, file);
  mkdirSync(dirname(target), { recursive: true });
  copyFileSync(join(appRoot, "public", file), target);
}
copyFileSync(join(appRoot, "public-viewer/_headers"), join(output, "_headers"));
runScript("check-public-viewer.mjs");
