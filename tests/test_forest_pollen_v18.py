import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_forest_pollen_v18 as batch
import test_forest_pollen_v10 as previous_tests


class ReadingPollenPartialBatch(previous_tests.ReadingPollenBatch):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v18.json').read_bytes())
        cls.parent = json.loads(batch.BASE.read_bytes())
        cls.new = [series for series in cls.seed['series']
                   if series['id'] in cls.seed['append_series_ids']]
        cls.contract = json.loads(batch.CONTRACT.read_bytes())

    def test_blocked_chronologies_and_old_entities_are_not_reimported(self):
        super().test_blocked_chronologies_and_old_entities_are_not_reimported()
        events = {series['source_event'] for series in self.new}
        self.assertEqual(events, {'Armena', 'PEDRIDO'})
        self.assertFalse(events & {series.get('source_event') for series in self.parent['series']})
        self.assertFalse(events & {'ELX', 'Estanya Catena', 'CUCU', 'CANALEJA'})

    def test_all_original_samples_survive_but_zero_denominators_produce_no_values(self):
        records = {record.get('core'): record for record in self.seed['records']}
        for entry, expected_native, expected_retained in zip(self.contract['reading_entities'], [53, 71], [42, 8]):
            record = records[entry['entity']]
            audit = record['pollen_sample_audit']
            self.assertEqual(len(audit), expected_native)
            empty = {row[0] for row in audit if row[3] == 0}
            self.assertEqual(empty, set(entry['zero_sum_rows']))
            self.assertEqual(empty, {row['source_row'] for row in record['pollen_excluded_samples']})
            for series in self.new:
                if series['source_event'] == entry['entity']:
                    self.assertEqual(len(series['rows']), expected_retained)
                    self.assertFalse(empty & {row[2] for row in series['rows']})
            self.assertTrue(all(item['original']['material_dated'] in entry['date_materials']
                                for item in record['reading_dates_audit']['rows']))

    def test_zero_sum_exclusions_are_explicit_and_fail_closed(self):
        pollen = batch.pipeline.pollen
        if not (pollen.RAW / 'iberia.csv').exists():
            self.skipTest('Ignored original absent; restore with --fetch')
        parser = json.loads(pollen.CONTRACT.read_bytes())
        resource = next(entry for entry in parser['resources'] if entry['file'] == 'iberia.csv')
        entry = copy.deepcopy(self.contract['reading_entities'][0])
        for invalid in ([], entry['zero_sum_rows'] + [999999], entry['zero_sum_rows'] + [entry['last_row']]):
            with self.assertRaises(ValueError):
                pollen.reading(resource, dict(parser, reading_entities=[dict(entry, zero_sum_rows=invalid)]))


if __name__ == '__main__':
    unittest.main()
