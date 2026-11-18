import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { DatabaseSync } from "node:sqlite";
import { summarize } from "../lib/science.mjs";
import {
  REVIEW_GROUP,
  appliedReviewExclusions,
  applyReviewExclusions,
  findReviewSample,
  reviewExportSamples,
  reviewSampleKey,
} from "../lib/review-pilot.mts";

const rows = [
  [7, 10, 3, 11, "7.0", "10.0"],
  [7, 20, 4, 12, "7.0", "20.0"],
  [8, 40, 5, 13, "8.0", "40.0"],
];
const series = {
  id: "series-a", record_id: "core-a", proxy: "alkenone_SST", unit: "°C",
  compatibility_group: "sst_alkenone_mueller1998_annual",
  raw_sha256: "source-hash", source_url: "https://example.test/source", rows,
};
const record = { id: series.record_id, latitude: 35, longitude: 6 };
const window = { proxy: series.proxy, group: REVIEW_GROUP, min: 7, max: 8, minN: 1, stat: "mean", mode: "raw" };
const snapshot = { version: "release-a", group: REVIEW_GROUP, series: [series] };
const sampleKey = reviewSampleKey(series, rows[1]);
const proposal = { id: "proposal-a", sampleKey, status: "pending", evidence: findReviewSample(snapshot, sampleKey) };

test("preview and approved views exclude only the named sample, keeping duplicates in age and the source intact", () => {
  const valueFor = (proposals, view) => {
    const exclusions = appliedReviewExclusions(proposals, view);
    return summarize({ records: [record], series: applyReviewExclusions([series], exclusions) }, window)[0];
  };
  assert.equal(valueFor([proposal], { mode: "approved" }).n, 3);
  assert.equal(valueFor([proposal], { mode: "preview", proposalId: proposal.id }).value, 25);
  const approved = { ...proposal, status: "approved" };
  assert.equal(valueFor([approved], { mode: "approved" }).n, 2);
  assert.equal(valueFor([approved], { mode: "original" }).n, 3);
  assert.equal(valueFor([{ ...proposal, status: "rejected" }], { mode: "approved" }).n, 3);
  assert.equal(series.rows[1][5], "20.0");
  assert.equal(findReviewSample(snapshot, reviewSampleKey(series, [7, 21, 4, 12])), null);
});

test("export retains the original row and audit evidence for a reference-only exclusion", () => {
  const approved = { ...proposal, status: "approved" };
  const exclusions = appliedReviewExclusions([approved], { mode: "approved" });
  const exported = reviewExportSamples(series, [rows[2]], exclusions, {
    ...window, min: 8, mode: "z", refMin: 6, refMax: 7,
  });
  assert.equal(exported[0].exclusion, null);
  assert.equal(exported[1].row[5], "20.0");
  assert.equal(exported[1].inWindow, false);
  assert.equal(exported[1].exclusion.id, proposal.id);
});

test("the review migration preserves the private-data tables and prevents concurrent active proposals for the same release and row", () => {
  const db = new DatabaseSync(":memory:");
  try {
    for (const migration of ["0004_private_data.sql", "0005_review_proposals.sql"])
      db.exec(readFileSync(new URL(`../drizzle/${migration}`, import.meta.url), "utf8"));
    const insert = db.prepare(
      "INSERT INTO atlas_review_proposals (id, release_id, sample_key, evidence_json, reason, created_by, created_at) VALUES (?, ?, ?, '{}', 'motivo', 'editor', 'ahora')",
    );
    insert.run("first", "release-a", sampleKey);
    assert.throws(() => insert.run("duplicate", "release-a", sampleKey), /UNIQUE constraint/);
    insert.run("other-version", "release-b", sampleKey);
    db.exec("UPDATE atlas_review_proposals SET status = 'rejected' WHERE id = 'first'");
    insert.run("second", "release-a", sampleKey);
    assert.equal(db.prepare("SELECT COUNT(*) AS count FROM atlas_review_proposals").get().count, 3);
  } finally {
    db.close();
  }
});
