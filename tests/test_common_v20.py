"""Admission and native-cell regressions for the organic carbon/nutrient batch."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_common_v20 as batch


class CommonBatchV20(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v20.json').read_bytes())
        cls.parent = json.loads(batch.BASE.read_bytes())
        cls.contract = json.loads(batch.CONTRACT.read_bytes())
        cls.new = [s for s in cls.seed['series'] if s['id'] in cls.seed['append_series_ids']]

    @classmethod
    def tearDownClass(cls):
        cls.seed = cls.parent = cls.contract = cls.new = None

    def test_parent_schema_and_quarantine_are_unchanged(self):
        self.assertEqual(set(self.seed), set(self.parent))
        self.assertEqual(self.seed['row_format'], self.parent['row_format'])
        self.assertEqual(self.seed['curation_excluded_series'], self.parent['curation_excluded_series'])
        for name in ('records', 'series'):
            byid = {entry['id']: entry for entry in self.seed[name]}
            allowed = set().union(*(entry.keys() for entry in self.parent[name]))
            for entry in self.parent[name]:
                self.assertEqual(byid[entry['id']], entry)
            for entry in self.seed[name]:
                self.assertFalse(set(entry) - allowed)
        self.assertEqual(len(self.new), 3)
        self.assertEqual(sum(len(s['rows']) for s in self.new), 98)
        self.assertEqual(len(self.seed['records']), len(self.parent['records']))

    def test_native_values_units_ages_depths_and_localizers(self):
        entry = next(e for e in self.contract['datasets'] if e['id'] == 896609)
        path = batch.RAW / '896609.tsv'
        if not path.exists():
            self.skipTest('Restore ignored native originals with build_common_v20.py --fetch')
        raw = path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), entry['sha'])
        native = batch.pipeline.curator.native
        _, header, rows = native.parse_tsv(raw)
        self.assertEqual(header, entry['header'])
        byrow = {index: (line, cells) for index, line, cells in rows}
        age_col, _, transform = native.age_rule(header)
        for series in self.new:
            column = series['source_column_index']
            spec = next(c for c in entry['columns'] if c['column'] == column)
            self.assertEqual(series['unit'], spec['unit'])
            self.assertEqual(series['comparison_parameter_name'], spec['name'])
            for row in series['rows']:
                self.assertEqual(len(row), 9)
                line, cells = byrow[row[2]]
                self.assertEqual(row[3], line)
                self.assertEqual(row[4], cells[age_col])
                self.assertEqual(row[0], transform(float(cells[age_col])))
                self.assertEqual(row[5], cells[column])
                self.assertEqual(row[1], float(cells[column]))
                self.assertEqual(row[8], cells[native.depth_column(header)])
                self.assertIsNone(row[6])
                self.assertIsNone(row[7])

    def test_environmental_interpretation_and_labile_fraction(self):
        for s in self.new:
            self.assertTrue(s['proxy'])
            self.assertTrue(any(n.startswith('Variable ambiental interpretada/reconstruida: ') for n in s['qc_notes']))
            self.assertTrue(any(n.startswith('Unidad estándar del proxy: ') for n in s['qc_notes']))
            self.assertIn(s['unit'], {'mg/g', 'µg/g'})
        phosphorus = next(s for s in self.new if s['source_column_index'] == 6)
        self.assertEqual(phosphorus['comparison_context_key'], 'phosphorus_labile_olsen_sediment')
        self.assertEqual(len(phosphorus['rows']), 32, 'Missing native cell must not become zero')
        self.assertEqual({s['record_id'] for s in self.new}, {'pangaea5-ben14_p4'})

    def test_negative_percentage_and_ambiguous_age_source_remain_excluded(self):
        audit = json.loads((ROOT / 'reports/common_v20_extraction_audit.json').read_bytes())
        self.assertTrue(any(s['dataset'].endswith('667403') and s['status'] == 'quarantined' for s in audit['audit']))
        self.assertTrue(any(s['id'] == 993109 and s['status'] == 'held' for s in audit['held']))
        self.assertEqual({s['dataset_doi'] for s in self.new}, {'10.1594/PANGAEA.896609'})
        self.assertEqual(hashlib.sha256(batch.BASE.read_bytes()).hexdigest(), self.contract['parent_sha256'])


if __name__ == '__main__':
    unittest.main()
