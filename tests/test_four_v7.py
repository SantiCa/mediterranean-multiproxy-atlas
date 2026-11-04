import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/importers'))
import curate_four_v7 as curator


class FourProxyRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v7.json').read_bytes())
        cls.parent = json.loads(curator.BASE.read_bytes())
        cls.contract = json.loads(curator.CONTRACT.read_bytes())

    def test_parent_and_source_locators(self):
        self.assertEqual(self.seed['records'][:len(self.parent['records'])], self.parent['records'])
        self.assertEqual(self.seed['series'][:len(self.parent['series'])], self.parent['series'])
        added = self.seed['series'][len(self.parent['series']):]
        contracts = {e['id']: e for e in self.contract['datasets'] if e['status'] == 'ready'}
        for series in added:
            if series.get('provider') == 'Zenodo':
                self.assertEqual(series['record_id'], self.contract['zenodo']['parent_record_id'])
                continue
            entry = contracts[series['dataset_doi'].split('.')[-1]]
            self.assertEqual(series['source_column'], entry['header'][series['source_column_index']])
            self.assertEqual(series['raw_sha256'], entry['sha'])
            self.assertEqual(series['paper_doi'], entry['paper']['doi'])

    def test_native_values_and_ages(self):
        ready = [e for e in self.contract['datasets'] if e['status'] == 'ready']
        raw_dir = curator.RAW / 'pangaea'
        if not all((raw_dir / f"{e['id']}.tsv").exists() for e in ready):
            self.skipTest('Restore pinned source data with curate_four_v7.py --fetch')
        originals = {}
        for entry in ready:
            raw = curator.priority.resource(entry, 'tsv', raw_dir=raw_dir)
            _, header, rows = curator.priority.native.parse_tsv(raw)
            originals[entry['id']] = (header, {row: (line, cells) for row, line, cells in rows})
        for series in self.seed['series'][len(self.parent['series']):]:
            if not series['id'].startswith('pangaea7-'):
                continue
            header, rows = originals[series['dataset_doi'].split('.')[-1]]
            age_idx, _, convert = curator.age_rule(header)
            for age, value, row, line, raw_age, raw_value, *_ in series['rows']:
                native_line, cells = rows[row]
                self.assertEqual((line, raw_age, raw_value), (native_line, cells[age_idx], cells[series['source_column_index']]))
                self.assertEqual(value, float(raw_value))
                self.assertEqual(age, convert(float(raw_age)))
                if 'Event' in header:
                    self.assertEqual(series['source_event'], cells[header.index('Event')])

    def test_zenodo_sheet_values_and_unit_correction(self):
        if not (curator.RAW / 'u1389.xlsx').exists():
            self.skipTest('Restore pinned Zenodo workbook with curate_four_v7.py --fetch')
        from openpyxl import load_workbook

        book = load_workbook(curator.RAW / 'u1389.xlsx', data_only=True, read_only=True)
        try:
            sheet = book[self.contract['zenodo']['sheet']]
            rows = list(sheet.values)
        finally:
            book.close()
        zenodo = [s for s in self.seed['series'] if s.get('provider') == 'Zenodo']
        self.assertEqual(len(zenodo), 2)
        for series in zenodo:
            column = series['source_column_index']
            self.assertEqual(len(series['rows']), sum(r[column] is not None for r in rows[1:]))
            for age, value, _, line, *_ in series['rows']:
                self.assertEqual((age, value), (rows[line - 1][2], rows[line - 1][column]))
        mean = next(s for s in zenodo if s['source_column'] == 'SS')
        self.assertEqual(mean['unit'], 'µm')
        self.assertIn('mm', mean['original_unit'])


if __name__ == '__main__':
    unittest.main()
