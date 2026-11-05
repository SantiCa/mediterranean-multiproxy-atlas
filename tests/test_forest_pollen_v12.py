import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_forest_pollen_v12 as batch
import test_forest_pollen_v10 as previous_tests


class ReadingPollenThirdBatch(previous_tests.ReadingPollenBatch):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v12.json').read_bytes())
        cls.parent = json.loads(batch.BASE.read_bytes())
        cls.new = [series for series in cls.seed['series']
                   if series['id'] in cls.seed['append_series_ids']]
        cls.contract = json.loads(batch.CONTRACT.read_bytes())

    def test_blocked_chronologies_and_old_entities_are_not_reimported(self):
        super().test_blocked_chronologies_and_old_entities_are_not_reimported()
        old_events = {series.get('source_event') for series in self.parent['series']}
        new_events = {series['source_event'] for series in self.new}
        self.assertFalse(old_events & new_events)
        self.assertNotIn('PEDRIDO', new_events)

    def test_quinta02_chronology_correction_is_explicit_for_every_series(self):
        entry = next(entry for entry in self.contract['reading_entities'] if entry['entity'] == 'QUINTA02')
        record = next(record for record in self.seed['records'] if record.get('core') == 'QUINTA02')
        selected = [series for series in self.new if series['source_event'] == 'QUINTA02']
        self.assertEqual(len(selected), 6)
        for item in [record] + selected:
            for note in entry['qc_notes']:
                self.assertEqual(item['qc_notes'].count(note), 1)
        self.assertTrue(all(series['age_column_original'] == 'INTCAL2020_median' for series in selected))


if __name__ == '__main__':
    unittest.main()
