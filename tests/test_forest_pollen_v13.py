import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_forest_pollen_v13 as batch
import test_forest_pollen_v10 as previous_tests


class ReadingPollenFourthBatch(previous_tests.ReadingPollenBatch):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v13.json').read_bytes())
        cls.parent = json.loads(batch.BASE.read_bytes())
        cls.new = [series for series in cls.seed['series']
                   if series['id'] in cls.seed['append_series_ids']]
        cls.contract = json.loads(batch.CONTRACT.read_bytes())

    def test_blocked_chronologies_and_old_entities_are_not_reimported(self):
        super().test_blocked_chronologies_and_old_entities_are_not_reimported()
        self.assertFalse({series['source_event'] for series in self.new}
                         & {series.get('source_event') for series in self.parent['series']})
        self.assertNotIn('PEDRIDO', {series['source_event'] for series in self.new})

    def test_short_records_are_complete_and_audited_for_exact_duplicates(self):
        admission = batch.pipeline.pollen.admission
        seen = {(admission.quantity(series), admission.digest(admission.vector(series)))
                for series in self.parent['series']}
        for series in self.new:
            fingerprint = (admission.quantity(series), admission.digest(admission.vector(series)))
            self.assertNotIn(fingerprint, seen, 'Include vectors shorter than admission threshold')
            seen.add(fingerprint)
            if series['source_event'] in ('SERTAL', 'ESTACAS'):
                self.assertEqual(len(series['rows']), 9)
                self.assertTrue(any('nueve muestras' in note for note in series['qc_notes']))

    def test_dataset_reference_and_version_correction_are_not_lost(self):
        for series in self.new:
            if series['source_event'] == 'N-PEQ':
                self.assertEqual(series['dataset_doi'], '10.17864/1947.000369')
                self.assertEqual(series['related_paper_dois'], [])
                self.assertIsNone(series['paper_doi'])
                self.assertIn('10.1594/PANGAEA.738850', series['citation'])
            entry = next(entry for entry in self.contract['reading_entities']
                         if entry['entity'] == series['source_event'])
            for note in entry.get('qc_notes', []):
                self.assertEqual(series['qc_notes'].count(note), 1)


if __name__ == '__main__':
    unittest.main()
