"""Scientific ingestion contracts for the bounded NOAA batch (offline)."""
import importlib.util
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("curate_noaa_v3", ROOT / "scripts/importers/curate_noaa_v3.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NOAAParserContracts(unittest.TestCase):
    def test_missing_is_not_zero_or_negative_bp(self):
        self.assertEqual(module.numeric("0"), 0)
        self.assertEqual(module.numeric(" -57.4 "), -57.4)
        for native in ("-999", "-999.00", "NA ", "#DIV/0!"):
            self.assertIsNone(module.numeric(native))
        with self.assertRaises(ValueError):
            module.numeric("unexpected")

    def test_schema_retains_source_line_and_interior_empty_cells(self):
        raw = b"# description\n## age\tage,,,calendar year before present\n\nage\tvalue\tnote\t\n0\t\tA\t\n"
        header, rows, definitions = module.read_table(raw)
        self.assertEqual(header, ["age", "value", "note"])
        self.assertEqual(rows, [(1, 5, {"age": "0", "value": "", "note": "A"})])
        self.assertIn("calendar year before present", definitions["age"])


@unittest.skipUnless((module.CACHE / "28070.json").exists(), "Ignored NOAA originals absent; run curator --fetch")
class NOAAActualSourceIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fragment, cls.audit = module.curate()

    def test_every_numeric_cell_has_an_exact_original_locator(self):
        sources = {}
        for source in self.audit["source_files"]:
            _, rows, _ = module.read_table((module.CACHE / source["file"]).read_bytes())
            sources[source["url"]] = (source, {r[0]: r for r in rows})
        for series in self.fragment["series"]:
            source, rows = sources[series["source_url"]]
            self.assertEqual(series["raw_sha256"], source["sha256"])
            for age, value, source_row, source_line, age_cell, value_cell, age_error, value_error, depth in series["rows"]:
                native = rows[source_row]
                cells = native[2]
                self.assertEqual(native[1], source_line)
                self.assertEqual(cells[source["age_column"]], age_cell)
                self.assertEqual(cells[series["source_column"]], value_cell)
                self.assertEqual(float(value_cell), value)
                native_age = module.numeric(age_cell)
                self.assertEqual(None if native_age is None else native_age * source["age_factor_to_ka"], age)
                self.assertIsNone(age_error)
                self.assertIsNone(value_error)
                self.assertTrue(math.isfinite(value))

    def test_quarantine_and_chronology_dependencies_are_not_silently_fixed(self):
        self.assertEqual(len(self.fragment["quarantined_series"]), 1)
        q = self.fragment["quarantined_series"][0]
        self.assertEqual(q["out_of_range_percent_cells"], 18)
        self.assertEqual(max(row[1] for row in q["rows"]), 124.2)
        self.assertNotIn(q["id"], {s["id"] for s in self.fragment["series"]})
        ohrid = next(r for r in self.fragment["records"] if r["source_id"] == "28070")
        self.assertEqual(ohrid["publication_year"], 2020)
        self.assertEqual(ohrid["publication_year_native"], 2019)
        self.assertEqual(ohrid["chronology_status"], "orbital_tuning")
        self.assertEqual(len(ohrid["source_files"]), 6)
        self.assertIsNone(ohrid["raw_sha256"])
        xrf = next(s for s in self.fragment["series"] if s["source_table_id"] == "40702")
        self.assertEqual(xrf["source_error_cells"], 12)
        self.assertEqual(xrf["values_missing_age"], 61)
        self.assertEqual(sum(row[0] is None for row in xrf["rows"]), 61)

    def test_calibrations_and_denominators_stay_separate(self):
        sst = [s for s in self.fragment["series"] if s["variable_id"] == "sea_surface_temperature"]
        self.assertEqual(len(sst), 4)
        self.assertEqual(len({s["compatibility_group"] for s in sst}), 1)
        self.assertTrue(all("conte2006" in s["compatibility_group"] for s in sst))
        maat = [s for s in self.fragment["series"] if s["variable_id"] == "mean_annual_air_temperature"]
        self.assertEqual(len({s["compatibility_group"] for s in maat}), 3)
        pollen = [s for s in self.fragment["series"] if s["source_column"] in {"AP%", "AP%-pine"}]
        self.assertEqual(len({s["compatibility_group"] for s in pollen}), 2)
        self.assertEqual(self.audit["counts"], {"records": 7, "series": 52, "observations": 28806})


if __name__ == "__main__":
    unittest.main()
