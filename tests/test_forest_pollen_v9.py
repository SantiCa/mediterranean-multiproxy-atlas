import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_forest_pollen_v9 as pollen


class ForestPollenRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v9.json').read_bytes())
        cls.new = [s for s in cls.seed['series'] if s['id'] in cls.seed['append_series_ids']]

    def test_missing_cells_and_empty_sums_are_not_observed_zero(self):
        self.assertEqual(pollen.abundance({'a': '0', 'b': '2'}, ['a', 'b']), 2)
        for token in ('', 'NaN', '-1', '<2'):
            with self.assertRaises(ValueError):
                pollen.abundance({'a': token}, ['a'])
        with self.assertRaises(ValueError):
            pollen.fraction(0, 0)

    def test_native_monticchio_values_and_lamination_scale(self):
        s = next(s for s in self.new if s['proxy'] == 'Woody_taxa_percent_')
        self.assertEqual(s['record_id'], 'noaa-5463-8909')
        self.assertEqual(len(s['rows']), 496)
        self.assertEqual(s['rows'][0][:6], [0.0587, 71.62, 1, 6, '58.7 ', '71.62'])
        self.assertEqual(s['comparison_context_key'], 'monticchio1999_native_published_pollen_percent')

    def test_every_derived_cell_reconciles_to_retained_sum(self):
        records = {r['id']: r for r in self.seed['records']}
        derived = [s for s in self.new if s['evidence_type'] == 'derived_relative_abundance']
        self.assertEqual(len(derived), 29 * 6)
        for s in derived:
            sums = {a[0]: a[3] for a in records[s['record_id']]['pollen_sample_audit']}
            self.assertEqual(len(s['denominator_columns']), 205)
            for age, value, source_row, _, raw_age, raw_value, lower, upper, _ in s['rows']:
                self.assertAlmostEqual(value, float(raw_value) * 100 / sums[source_row])
                self.assertEqual(age, float(raw_age) / 1000)
                self.assertEqual((lower, upper), (None, None), 'Ambiguous source uncertainty is not reinterpreted')
        self.assertTrue(any(r[0] < 0 for s in derived for r in s['rows']))

    def test_piniform_subtypes_remain_explicit(self):
        pinus = [s for s in self.new if s['proxy'] == 'Pinus_' and s['record_id'].startswith('reading9-')]
        self.assertTrue(all(s['source_columns'] == ['Pinus', 'Pinus..diploxylon.', 'Pinus..haploxylon.'] for s in pinus))
        self.assertTrue(all(s['comparison_context_key'] == pollen.READING_CONTEXT for s in pinus))

    def test_unverified_md99_2337_has_not_acquired_ages(self):
        report = json.loads((ROOT / 'reports/quantitative_v9_release.json').read_bytes())
        self.assertTrue(any(x['record'] == 'MD99-2337' for x in report['held']))
        self.assertFalse(any(s.get('source_event') == 'MD99-2337' for s in self.new))


if __name__ == '__main__':
    unittest.main()
