import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_common_v19 as batch


class CommonProxyBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v19.json').read_bytes())
        cls.parent = json.loads(batch.BASE.read_bytes())
        cls.contract = json.loads(batch.CONTRACT.read_bytes())
        cls.new = [series for series in cls.seed['series'] if series['id'] in cls.seed['append_series_ids']]

    @classmethod
    def tearDownClass(cls):
        cls.seed = cls.parent = cls.contract = cls.new = None

    def test_parent_and_field_structure_are_unchanged(self):
        self.assertEqual(set(self.seed), set(self.parent))
        self.assertEqual(self.seed['row_format'], self.parent['row_format'])
        self.assertEqual(self.seed['curation_excluded_series'], self.parent['curation_excluded_series'])
        for name in ('records', 'series'):
            byid = {entry['id']: entry for entry in self.seed[name]}
            allowed_fields = set().union(*(entry.keys() for entry in self.parent[name]))
            for entry in self.parent[name]:
                self.assertEqual(byid[entry['id']], entry)
            for entry in self.seed[name]:
                self.assertFalse(set(entry) - allowed_fields, 'No additional database fields')
        self.assertEqual(len(self.new), 38)
        self.assertEqual(sum(len(series['rows']) for series in self.new), 5182)
        self.assertEqual(len(self.seed['records']) - len(self.parent['records']), 2)

    def test_each_native_cell_age_uncertainty_and_event_is_preserved(self):
        cache = {}
        for entry in self.contract['datasets']:
            if entry['status'] != 'ready':
                continue
            path = batch.RAW / f"{entry['id']}.tsv"
            if not path.exists():
                self.skipTest('Ignored originals absent; restore build_common_v19.py --fetch')
            raw = path.read_bytes()
            self.assertEqual(batch.curator.native.sha(raw), entry['sha'])
            _, header, rows = batch.curator.native.parse_tsv(raw)
            self.assertEqual(header, entry['header'])
            cache[entry['id']] = (entry, {index: (line, cells) for index, line, cells in rows})
        for series in self.new:
            ident = int(series['dataset_doi'].rsplit('.', 1)[1])
            entry, native = cache[ident]
            spec = next(column for column in entry['columns'] if column['column'] == series['source_column_index'])
            age_rule = batch.curator.native.age_rule(entry['header'])
            depth = batch.curator.native.depth_column(entry['header'])
            for age, value, rowid, line, raw_age, raw_value, age_error, error, raw_depth in series['rows']:
                source_line, cells = native[rowid]
                self.assertEqual(line, source_line)
                self.assertEqual(raw_age, cells[age_rule[0]])
                self.assertEqual(age, age_rule[2](float(raw_age)))
                self.assertEqual(raw_value, cells[spec['column']])
                self.assertEqual(value, float(raw_value))
                self.assertEqual(raw_depth, cells[depth])
                self.assertIsNone(age_error)
                if spec.get('error_column') is not None:
                    self.assertEqual(error, batch.curator.native.number(cells[spec['error_column']]))
                else:
                    self.assertIsNone(error)
                if 'Event' in entry['header']:
                    self.assertEqual(series['source_event'], cells[entry['header'].index('Event')])

    def test_required_proxy_environment_and_scientific_units_are_explicit(self):
        for series in self.new:
            self.assertTrue(series['proxy'])
            self.assertTrue(series['comparison_parameter_name'])
            self.assertIn(series['unit'], {'°C', 'sin unidad', '‰ PDB', 'g/m**2/a'})
            self.assertTrue(any(note.startswith('Variable ambiental interpretada/reconstruida: ')
                                for note in series['qc_notes']))
            self.assertTrue(any(note.startswith('Unidad estándar del proxy: ')
                                for note in series['qc_notes']))
            self.assertTrue(all(len(row) == 9 for row in series['rows']))

    def test_distinct_methods_depth_contexts_and_species_remain_separate(self):
        marmara = [series for series in self.new if series['dataset_doi'].endswith('853815')
                   and series['unit'] == '°C']
        self.assertEqual(len({series['method'] for series in marmara}), 3)
        self.assertEqual(len({series['compatibility_group'] for series in marmara}), 3)
        for series in self.new:
            if series['dataset_doi'].endswith('854722') and series['unit'] == '°C':
                self.assertEqual(series['comparison_context_key'], 'black_sea_0_200m_archived')
            if series['dataset_doi'].endswith('966665'):
                self.assertNotEqual(series['source_column_index'], 9, 'Alternate +0.64 correction is not a new replicate')
                self.assertTrue(series['taxon'])
                self.assertEqual(series['unit'], '‰ PDB')
            if series['dataset_doi'].endswith('939417') and series['unit'] == '°C':
                self.assertIn('calibration_unspecified', series['comparison_context_key'])

    def test_no_complete_same_record_vectors_are_reimported_under_another_proxy_id(self):
        admission = batch.admission
        seen = {(series['record_id'], series['unit'], admission.digest(admission.vector(series)))
                for series in self.parent['series']}
        for series in self.new:
            fingerprint = (series['record_id'], series['unit'], admission.digest(admission.vector(series)))
            self.assertNotIn(fingerprint, seen)
            seen.add(fingerprint)

    def test_coincident_cores_do_not_create_two_spatial_locations(self):
        parent_ids = {record['id'] for record in self.parent['records']}
        new_records = [record for record in self.seed['records'] if record['id'] not in parent_ids]
        self.assertEqual(len(new_records), 2)
        self.assertEqual(len({(record['latitude'], record['longitude']) for record in new_records}), 1)
        report = json.loads((ROOT / 'reports/quantitative_v19_release.json').read_bytes())
        self.assertFalse(report['integration_quarantine'])
        self.assertFalse(report['partial_numeric_overlap_links'])
        self.assertTrue(any(entry['id'] == 939418 and entry['status'] == 'held'
                            for entry in self.contract['datasets']))
        self.assertFalse(any(series['dataset_doi'].endswith('939418') for series in self.new))


if __name__ == '__main__':
    unittest.main()
