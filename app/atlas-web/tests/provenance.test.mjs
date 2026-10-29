import test from "node:test";
import assert from "node:assert/strict";
import { seriesSource } from "../lib/provenance.mjs";
import { seriesMatches } from "../lib/proxies.mjs";
test("series license/DOI/year override physical-core defaults; explicit unknown stays unknown", () => {
  const r = {
    license: "CC-BY-4.0",
    dataset_doi: "first",
    paper_doi: "paper-one",
    publication_year: 2010,
    realm: "lake",
    provider: "PANGAEA",
  };
  const s = {
    license: "CC-BY-SA-4.0",
    dataset_doi: "second",
    paper_doi: null,
    publication_year: 2023,
  };
  assert.equal(seriesSource(s, r).license, "CC-BY-SA-4.0");
  assert.equal(seriesSource(s, r).dataset_doi, "second");
  assert.equal(seriesSource(s, r).paper_doi, null);
  assert.equal(seriesMatches(s, r, { yearMin: 2020 }), true);
  assert.equal(
    seriesMatches({ ...s, publication_year: null }, r, { yearMax: 2025 }),
    false,
  );
  assert.equal(seriesSource({}, r).publication_year, 2010);
});
