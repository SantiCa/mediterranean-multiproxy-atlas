import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_forest_pollen_v14 as batch
import test_forest_pollen_v10 as previous_tests


class ReadingPollenFifthBatch(previous_tests.ReadingPollenBatch):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v14.json').read_bytes())
        cls.parent = json.loads(batch.BASE.read_bytes())
        cls.new = [series for series in cls.seed['series']
                   if series['id'] in cls.seed['append_series_ids']]
        cls.contract = json.loads(batch.CONTRACT.read_bytes())

    def test_blocked_chronologies_and_old_entities_are_not_reimported(self):
        super().test_blocked_chronologies_and_old_entities_are_not_reimported()
        self.assertFalse({series['source_event'] for series in self.new}
                         & {series.get('source_event') for series in self.parent['series']})
        self.assertNotIn('PEDRIDO', {series['source_event'] for series in self.new})

    def test_all_vectors_are_audited_for_exact_duplicates(self):
        admission = batch.pipeline.pollen.admission
        seen = {(admission.quantity(series), admission.digest(admission.vector(series)))
                for series in self.parent['series']}
        for series in self.new:
            fingerprint = (admission.quantity(series), admission.digest(admission.vector(series)))
            self.assertNotIn(fingerprint, seen)
            seen.add(fingerprint)

    def test_xl_version_correction_reaches_record_and_every_series(self):
        entry = next(entry for entry in self.contract['reading_entities'] if entry['entity'] == 'XL')
        record = next(record for record in self.seed['records'] if record.get('core') == 'XL')
        selected = [series for series in self.new if series['source_event'] == 'XL']
        self.assertEqual(len(selected), 6)
        for item in [record] + selected:
            for note in entry['qc_notes']:
                self.assertEqual(item['qc_notes'].count(note), 1)
        self.assertTrue(all(series['age_column_original'] == 'INTCAL2020_median' for series in selected))


if __name__ == '__main__':
    unittest.main()
