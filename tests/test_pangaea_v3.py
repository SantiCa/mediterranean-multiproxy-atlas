"""Source-to-cell regression checks; native files are local and never fetched by CI."""
import csv
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pangaea_v3', ROOT / 'scripts/importers/curate_pangaea_v3.py')
curation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(curation)


class PangaeaV3Contracts(unittest.TestCase):
    def test_censored_and_calendar_cells(self):
        self.assertIsNone(curation.number('<0.5'))
        self.assertIsNone(curation.number('NaN'))
        self.assertEqual(curation.number('0'), 0)
        self.assertEqual(curation.to_age('2003', 'Age [a AD/CE]'), -0.053)
        self.assertEqual(curation.to_age('-53', 'Varve age [a BP]'), -0.053)
        with self.assertRaises(ValueError):
            curation.to_age('10000', '14C age [a BP]')

    @unittest.skipUnless((curation.RAW / '818921.tsv').exists(), 'Ignored native source cache not available')
    def test_every_ingested_cell_matches_native(self):
        result = curation.curate()
        self.assertEqual(len(result['records']), 9)
        self.assertEqual(len(result['series']), 15)
        self.assertEqual(sum(len(s['rows']) for s in result['series']), 37782)
        for series in result['series']:
            dataset_id = int(series['record_id'].split('-')[1])
            text = curation.native(dataset_id, 'tsv').decode('utf-8-sig')
            native = list(csv.DictReader(text.split('*/', 1)[1].strip().splitlines(), delimiter='\t'))
            native_lines = text.splitlines()
            column_index = series_column_index(series, text)
            self.assertEqual(len({r[2] for r in series['rows']}), len(series['rows']))
            for row in series['rows']:
                source = native[row[2]-1]
                self.assertEqual(row[4], source[series['age_column_original']])
                self.assertEqual(row[5], source[series['source_column']])
                self.assertEqual(row[1], float(row[5]))
                self.assertEqual(row[8], source.get('Depth sed [m]'))
                self.assertEqual(native_lines[row[3]-1].split('\t')[column_index], row[5])

    @unittest.skipUnless((curation.RAW / '818921.tsv').exists(), 'Ignored native source cache not available')
    def test_chronology_units_and_instrument_isolation(self):
        result = curation.curate()
        mondsee = next(s for s in result['series'] if s['record_id'] == 'pangaea-818921')
        self.assertEqual(mondsee['age_column_original'], 'Varve age [a BP]')
        self.assertEqual(min(r[0] for r in mondsee['rows']), -0.053)
        self.assertEqual(mondsee['unit'], 'cps')
        self.assertIn('PANGAEA818921', mondsee['compatibility_group'])
        for series in result['series']:
            for row in series['rows']:
                if series['age_column_original'] == 'Varve age [a BP]':
                    self.assertEqual(row[0], float(row[4])/1000)
                elif series['age_column_original'] == 'Age [a AD/CE]':
                    self.assertEqual(row[0], (1950-float(row[4]))/1000)
                else:
                    self.assertEqual(row[0], float(row[4]))
        self.assertFalse(any(a['repeated_age_value_depth'] for d in result['audit'] for a in d['series']))
        isotopes = [s for s in result['series'] if s['record_id'] == 'pangaea-836213']
        self.assertEqual({s['unit'] for s in isotopes}, {'‰ VPDB'})
        self.assertEqual(len({s['compatibility_group'] for s in isotopes}), 4)
        editorial = next(r for r in result['records'] if r['dataset_id'] == 438795)
        self.assertIsNone(editorial['publication_year'])
        self.assertIsNone(editorial['paper_doi'])
        self.assertEqual(editorial['related_reference_year'], 2003)
        mr3 = next(s for s in result['series'] if s['record_id'] == 'pangaea-871130')
        self.assertEqual(len(mr3['uncertainty_bounds']), 42)
        self.assertTrue(all(r[7] is None for r in mr3['rows']))


def series_column_index(series, text):
    return text.split('*/', 1)[1].strip().splitlines()[0].split('\t').index(series['source_column'])
