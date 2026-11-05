import csv
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_forest_pollen_v16 as batch
import test_forest_pollen_v10 as previous_tests


class ReadingPollenSeventhBatch(previous_tests.ReadingPollenBatch):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v16.json').read_bytes())
        cls.parent = json.loads(batch.BASE.read_bytes())
        cls.new = [series for series in cls.seed['series']
                   if series['id'] in cls.seed['append_series_ids']]
        cls.contract = json.loads(batch.CONTRACT.read_bytes())

    def test_blocked_chronologies_and_old_entities_are_not_reimported(self):
        super().test_blocked_chronologies_and_old_entities_are_not_reimported()
        events = {series['source_event'] for series in self.new}
        self.assertEqual(len(events), 8)
        self.assertFalse(events & {series.get('source_event') for series in self.parent['series']})
        self.assertFalse(events & {'PEDRIDO', 'CANALEJA', 'CUCU', 'Armena', 'Estanya Catena'})

    def test_all_vectors_are_audited_for_exact_duplicates(self):
        admission = batch.pipeline.pollen.admission
        seen = {(admission.quantity(series), admission.digest(admission.vector(series)))
                for series in self.parent['series']}
        for series in self.new:
            fingerprint = (admission.quantity(series), admission.digest(admission.vector(series)))
            self.assertNotIn(fingerprint, seen)
            seen.add(fingerprint)

    def test_held_zero_sums_reconcile_to_native_rows(self):
        source = batch.pipeline.pollen.RAW / 'iberia.csv'
        if not source.exists():
            self.skipTest('Ignored Reading original absent; restore with --fetch')
        parser = json.loads(batch.pipeline.pollen.CONTRACT.read_bytes())
        with source.open(encoding='utf-8-sig', newline='') as stream:
            native = list(enumerate(csv.DictReader(stream), 1))
        report = json.loads((ROOT / 'reports/quantitative_v16_release.json').read_bytes())
        for name, expected_total, expected_empty in [('Armena', 53, 11), ('Estanya Catena', 92, 2)]:
            rows = [(index, row) for index, row in native if row['entity_name'] == name]
            empty = [index for index, row in rows
                     if sum(float(row[column]) for column in parser['reading_header'][15:]) == 0]
            held = next(entry for entry in self.contract['held'] if entry['record'] == 'Reading ' + name)
            self.assertEqual((len(rows), len(empty)), (expected_total, expected_empty))
            self.assertEqual(held['source_rows'], empty)
            self.assertIn(held, report['held'])
        selected = [series for series in self.new if series['source_event'] == 'PozoN_2015 core']
        self.assertTrue(all(len(series['rows']) == 41 for series in selected))
        self.assertTrue(all(any('carbón' in note for note in series['qc_notes']) for series in selected))


if __name__ == '__main__':
    unittest.main()
