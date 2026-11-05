import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_forest_pollen_v15 as batch
import test_forest_pollen_v10 as previous_tests


class ReadingPollenSixthBatch(previous_tests.ReadingPollenBatch):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v15.json').read_bytes())
        cls.parent = json.loads(batch.BASE.read_bytes())
        cls.new = [series for series in cls.seed['series']
                   if series['id'] in cls.seed['append_series_ids']]
        cls.contract = json.loads(batch.CONTRACT.read_bytes())

    def test_blocked_chronologies_and_old_entities_are_not_reimported(self):
        super().test_blocked_chronologies_and_old_entities_are_not_reimported()
        events = {series['source_event'] for series in self.new}
        self.assertFalse(events & {series.get('source_event') for series in self.parent['series']})
        self.assertFalse(events & {'PEDRIDO', 'CANALEJA'})
        report = json.loads((ROOT / 'reports/quantitative_v15_release.json').read_bytes())
        held = next(entry for entry in self.contract['held'] if entry['record'] == 'Reading CANALEJA')
        self.assertIn(held, report['held'])
        self.assertEqual(len(held['source_rows']), 6)

    def test_all_vectors_including_four_sample_cave_are_audited(self):
        admission = batch.pipeline.pollen.admission
        seen = {(admission.quantity(series), admission.digest(admission.vector(series)))
                for series in self.parent['series']}
        for series in self.new:
            fingerprint = (admission.quantity(series), admission.digest(admission.vector(series)))
            self.assertNotIn(fingerprint, seen)
            seen.add(fingerprint)
            if series['source_event'] == 'CUCU':
                self.assertEqual(len(series['rows']), 4)
                self.assertTrue(any('cueva' in note for note in series['qc_notes']))

    def test_source_chronology_notes_reach_records_and_series(self):
        for entry in self.contract['reading_entities']:
            if not entry.get('qc_notes'):
                continue
            record = next(record for record in self.seed['records'] if record.get('core') == entry['entity'])
            selected = [series for series in self.new if series['source_event'] == entry['entity']]
            self.assertEqual(len(selected), 6)
            for item in [record] + selected:
                for note in entry['qc_notes']:
                    self.assertEqual(item['qc_notes'].count(note), 1)
            self.assertTrue(all(series['age_column_original'] == 'INTCAL2020_median' for series in selected))


if __name__ == '__main__':
    unittest.main()
