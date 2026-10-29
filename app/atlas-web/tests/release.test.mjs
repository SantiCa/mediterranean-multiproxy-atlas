import test from "node:test";
import assert from "node:assert/strict";
import { pickRelease } from "../lib/release.mjs";
const manifest = { releases: [
  { version: "v3", series: ["a"], records: ["r1"] },
  { version: "v4", series: ["a", "b"], records: ["r1", "r2"] },
] };
test("serves the newest complete release only", () => {
  assert.equal(pickRelease(manifest, ["v3"]).version, "v3");
  assert.equal(pickRelease(manifest, ["v3", "v4"]).version, "v4");
  assert.ok(!pickRelease(manifest, ["v3"]).seriesIds.has("b"));
  assert.equal(pickRelease(manifest, ["other"]), null);
});
