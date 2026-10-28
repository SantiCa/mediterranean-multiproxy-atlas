"""Scientific integrity checks against the actual downloaded sources."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from prepare_seed import read_table
from seed_query import select


class ScientificIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all((ROOT / f"data/raw/pangaea/{item}.tsv").exists()
                   for item in (438816, 901666, 759535, 898587, 921230)):
            raise unittest.SkipTest("Seed originals absent: run python scripts/fetch_seed.py")
        cls.rows = json.loads((ROOT / "data/processed/observations.json").read_text(encoding="utf-8"))

    def test_all_raw_objects_match_manifest(self):
        manifest = json.loads((ROOT / "data/provenance/downloads.json").read_text())
        for item in manifest:
            self.assertEqual(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest(), item["sha256"])

    def test_every_selected_cell_and_line_traces_to_raw(self):
        tables = {}
        for row in self.rows:
            dataset_id = row["dataset_id"]
            if dataset_id not in tables:
                path = ROOT / f"data/raw/pangaea/{dataset_id}.tsv"
                tables[dataset_id] = (read_table(path)[1], path.read_text(encoding="utf-8").splitlines())
            table, lines = tables[dataset_id]
            cell = table[row["source_row"] - 1][row["source_column"]]
            self.assertEqual(cell, row["source_value"])
            self.assertEqual(float(cell), row["value"])
            self.assertIn(cell, lines[row["source_line"] - 1].split("\t"))

    def test_unknown_age_does_not_enter_time_filter(self):
        depth_only = [r for r in self.rows if r["dataset_id"] == 898587]
        self.assertTrue(depth_only)
        self.assertTrue(all(r["age_ka_bp"] is None for r in depth_only))
        self.assertFalse(select(depth_only, age_min=0, age_max=150))
        self.assertEqual(len(select(depth_only)), len(depth_only))

    def test_negative_BP_age_and_real_zeros_survive(self):
        self.assertTrue(any(r["age_ka_bp"] is not None and r["age_ka_bp"] < 0 for r in self.rows))
        self.assertTrue(any(r["dataset_id"] == 898587 and r["value"] == 0 for r in self.rows))
        self.assertFalse(any(r["age_ka_bp"] is not None and r["age_ka_bp"] < 0 for r in select(self.rows, age_min=0)))

    def test_publication_year_is_not_dataset_year_or_sample_age(self):
        paper_2020 = select(self.rows, paper_year_min=2020, paper_year_max=2020)
        self.assertTrue(paper_2020)
        self.assertTrue(all(r["dataset_citation_year"] == 2024 and r["age_ka_bp"] > 300 for r in paper_2020))
        self.assertFalse(select(self.rows, paper_year_min=2024, paper_year_max=2024))

    def test_joint_filters_are_conjunctive(self):
        rows = select(self.rows, proxy="MgCa_SST", age_min=0, age_max=11.7, paper_year_min=2019, paper_year_max=2019)
        self.assertTrue(rows)
        self.assertTrue(all(r["proxy"] == "MgCa_SST" and 0 <= r["age_ka_bp"] <= 11.7 and r["publication_year"] == 2019 for r in rows))

    def test_bad_ranges_fail_explicitly(self):
        with self.assertRaises(ValueError):
            select(self.rows, age_min=20, age_max=0)

    def test_identifiers_unique_and_uncertainty_not_fabricated(self):
        self.assertEqual(len(self.rows), len({r["observation_id"] for r in self.rows}))
        self.assertTrue(all(r["age_uncertainty_ka"] is None for r in self.rows))
        errors = [r for r in self.rows if r["value_uncertainty"] is not None]
        self.assertTrue(errors)
        self.assertTrue(all(r["proxy"] == "MgCa_SST" for r in errors))


if __name__ == "__main__":
    unittest.main()
