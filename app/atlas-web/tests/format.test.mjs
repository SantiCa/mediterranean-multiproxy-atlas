import test from "node:test";
import assert from "node:assert/strict";
import { scientificNumber } from "../lib/format.mjs";
test("small Sr isotope differences remain visible and tiny flux never rounds to zero", () => {
  assert.notEqual(scientificNumber(0.70912345), scientificNumber(0.70912355));
  assert.match(scientificNumber(0.00000023), /e−/);
  assert.equal(scientificNumber(0), "0");
  assert.equal(scientificNumber(null), "—");
  assert.equal(scientificNumber(Infinity), "—");
});
