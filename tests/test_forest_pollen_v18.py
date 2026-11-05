import copy
import csv
from decimal import Decimal
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

    @classmethod
    def tearDownClass(cls):
        cls.seed = cls.parent = cls.new = cls.contract = None

    def test_parent_and_comparison_contexts_are_preserved(self):
        current_records = {record['id']: record for record in self.seed['records']}
        for record in self.parent['records']:
            self.assertEqual(record, current_records[record['id']])
        qc = self.contract['integrated_qc']
        removed = {entry['id'] for entry in qc['holds']}
        corrected = {series['id'] for series in self.parent['series']
                     if series.get('dataset_doi') == qc['age_corrections'][0]['dataset_doi']}
        current = {series['id']: series for series in self.seed['series']}
        for series in self.parent['series']:
            if series['id'] in removed:
                self.assertNotIn(series['id'], current)
            elif series['id'] not in corrected:
                self.assertEqual(series, current[series['id']])
        self.assertEqual(self.seed['parent_version'], self.parent['version'])
        self.assertEqual(len(self.new), 12)
        self.assertEqual(len(self.seed['records']) - len(self.parent['records']), 2)
        self.assertTrue(all(series['comparison_context_key'] == batch.pipeline.pollen.READING_CONTEXT
                            for series in self.new))

    def test_reviewed_age_changes_preserve_every_other_native_cell(self):
        parent = {series['id']: series for series in self.parent['series']}
        corrected = [series for series in self.seed['series']
                     if series.get('dataset_doi') == '10.1594/PANGAEA.929110']
        self.assertEqual(len(corrected), 19)
        for series in corrected:
            original = {row[2]: row for row in parent[series['id']]['rows']}
            for row in series['rows']:
                self.assertEqual(row[1:], original[row[2]][1:])
                self.assertEqual(row[0], float(Decimal('1.95') - Decimal(row[4])))
                self.assertTrue(1.45 <= row[0] <= 3.45)
            self.assertEqual(series['age_min_ka_bp'], min(row[0] for row in series['rows']))
            self.assertEqual(series['age_max_ka_bp'], max(row[0] for row in series['rows']))
            self.assertEqual(series['age_scale'], 'calendar ka BP (reference 1950)')

    def test_mondsee_original_table_remains_hash_pinned(self):
        source = self.contract['integrated_qc']['age_source']
        path = ROOT / source['path']
        if not path.exists():
            self.skipTest('Ignored Mondsee original absent; restore with --fetch')
        raw = path.read_bytes()
        self.assertEqual(batch.pipeline.pollen.sha(raw), source['sha256'])
        lines = raw.decode('utf8').splitlines()
        start = next(index for index, line in enumerate(lines) if line.startswith('Age [ka BP]\t'))
        table = list(csv.reader(lines[start:], delimiter='\t'))
        for series in self.seed['series']:
            if series.get('dataset_doi') == '10.1594/PANGAEA.929110':
                for row in series['rows']:
                    cells = table[row[2]]
                    self.assertEqual(row[4], cells[0])
                    self.assertAlmostEqual(row[0] * 1000, float(cells[1]))

    def test_held_duplicates_keep_complete_originals_outside_active_series(self):
        parent = {series['id']: series for series in self.parent['series']}
        active = {series['id']: series for series in self.seed['series']}
        quarantine = self.seed['curation_excluded_series']
        self.assertEqual(len(quarantine), 6)
        self.assertEqual(sum(len(entry['original_series']['rows']) for entry in quarantine), 1879)
        for entry in quarantine:
            self.assertNotIn(entry['id'], active)
            self.assertEqual(entry['original_series'], parent[entry['id']])
            retained = active[entry['duplicate_of']]
            self.assertEqual(retained['record_id'], entry['original_series']['record_id'])
            self.assertEqual(batch.pipeline.pollen.admission.vector(retained),
                             batch.pipeline.pollen.admission.vector(entry['original_series']))
        runtime_qc = json.loads((ROOT / 'config/qc_corrections.json').read_bytes())
        self.assertEqual(runtime_qc['holds'], [])
        self.assertEqual(runtime_qc['age_corrections'], [])

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
