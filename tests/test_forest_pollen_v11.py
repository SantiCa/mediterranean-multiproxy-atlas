import csv
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_forest_pollen_v11 as batch
import test_forest_pollen_v10 as previous_tests


class ReadingPollenNextBatch(previous_tests.ReadingPollenBatch):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v11.json').read_bytes())
        cls.parent = json.loads(batch.BASE.read_bytes())
        cls.new = [series for series in cls.seed['series']
                   if series['id'] in cls.seed['append_series_ids']]
        cls.contract = json.loads(batch.CONTRACT.read_bytes())

    def test_blocked_chronologies_and_old_entities_are_not_reimported(self):
        super().test_blocked_chronologies_and_old_entities_are_not_reimported()
        old = json.loads(batch.pipeline.CONTRACT.read_bytes())
        names = {series['source_event'] for series in self.new}
        self.assertFalse(names & {entry['entity'] for entry in old['reading_entities']})
        self.assertNotIn('PEDRIDO', names)

    def test_pedrido_zero_denominators_remain_auditable_and_excluded(self):
        source = batch.pipeline.pollen.RAW / 'iberia.csv'
        if not source.exists():
            self.skipTest('Ignored Reading original absent; restore with --fetch')
        parser_contract = json.loads(batch.pipeline.pollen.CONTRACT.read_bytes())
        with source.open(encoding='utf-8-sig', newline='') as stream:
            rows = [(index, row) for index, row in enumerate(csv.DictReader(stream), 1)
                    if row['entity_name'] == 'PEDRIDO']
        empty = [index for index, row in rows
                 if sum(float(row[column]) for column in parser_contract['reading_header'][15:]) == 0]
        held = next(entry for entry in self.contract['held'] if entry['record'] == 'Reading PEDRIDO')
        self.assertEqual(len(rows), 71)
        self.assertEqual(len(empty), 63)
        self.assertEqual(held['source_rows'], empty)
        report = json.loads((ROOT / 'reports/quantitative_v11_release.json').read_bytes())
        self.assertIn(held, report['held'])


if __name__ == '__main__':
    unittest.main()
