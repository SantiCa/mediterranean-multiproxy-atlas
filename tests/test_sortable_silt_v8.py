import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_sortable_silt_v8 as v8


class SortableSiltRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v8.json').read_bytes())
        cls.contract = json.loads(v8.CONTRACT.read_bytes())
        cls.new = {s['source_event']: s for s in cls.seed['series'] if s['id'] in cls.seed['append_series_ids']}

    def test_partial_coverage_and_calendar_age(self):
        expected = {'339-U1386': (33, 30), '339-U1390': (187, 186), 'CADKS24': (86, 32)}
        self.assertEqual(set(self.new), set(expected))
        for core, (samples, dated) in expected.items():
            rows = self.new[core]['rows']
            self.assertEqual((len(rows), sum(row[0] is not None for row in rows)), (samples, dated))
            self.assertTrue(all(row[4] is None for row in rows), 'Interpolated age is not a native sample cell')
        cadiz = {row[8]: row for row in self.new['CADKS24']['rows']}
        self.assertIsNone(cadiz['2.10'][0])
        self.assertAlmostEqual(cadiz['2.20'][0], 11.7322962962963)
        self.assertIsNone(cadiz['5.30'][0])

    def test_native_measurements_and_locators(self):
        if not (v8.RAW / 'mend-ss.xlsx').exists() or not (v8.RAW / '971577.tsv').exists():
            self.skipTest('Restore pinned files with build_sortable_silt_v8.py --fetch')
        from openpyxl import load_workbook

        workbook = load_workbook(v8.RAW / 'mend-ss.xlsx', read_only=True, data_only=True)
        try:
            for series in self.new.values():
                if series['source_sheet']:
                    native = {i: (str(c[0]), str(c[1])) for i, c in enumerate(workbook[series['source_sheet']].values, 1)}
                else:
                    _, _, native_rows = v8.parse_tsv((v8.RAW / '971577.tsv').read_bytes())
                    native = {line: tuple(c[:2]) for _, line, c in native_rows}
                for _, value, _, line, _, source_value, _, _, depth in series['rows']:
                    self.assertEqual((depth, source_value), native[line])
                    self.assertEqual(value, float(source_value))
        finally:
            workbook.close()
