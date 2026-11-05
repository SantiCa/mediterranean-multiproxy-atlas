import csv
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_forest_pollen_v10 as batch


class ReadingPollenBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v10.json').read_bytes())
        cls.parent = json.loads(batch.BASE.read_bytes())
        cls.new = [series for series in cls.seed['series']
                   if series['id'] in cls.seed['append_series_ids']]
        cls.contract = json.loads(batch.CONTRACT.read_bytes())

    def test_parent_and_comparison_contexts_are_preserved(self):
        for field in ('records', 'series'):
            current = {entry['id']: entry for entry in self.seed[field]}
            for entry in self.parent[field]:
                self.assertEqual(current[entry['id']], entry)
        self.assertEqual(self.seed['parent_version'], self.parent['version'])
        self.assertEqual(len(self.new), 60)
        self.assertEqual(len(self.seed['records']) - len(self.parent['records']), 10)
        for series in self.new:
            self.assertEqual(series['comparison_context_key'], batch.pollen.READING_CONTEXT)
            self.assertEqual(len(series['denominator_columns']), 205)
            self.assertEqual(series['publication_year'], None)
            self.assertEqual(series['dataset_publication_year'], 2022)

    def test_every_new_value_reconciles_with_hash_pinned_native_row(self):
        source = batch.pollen.RAW / 'iberia.csv'
        if not source.exists():
            self.skipTest('Ignored Reading original absent; restore with --fetch')
        resources = json.loads(batch.pollen.CONTRACT.read_bytes())['resources']
        self.assertEqual(batch.pollen.sha(source.read_bytes()),
                         next(entry['sha256'] for entry in resources if entry['file'] == 'iberia.csv'))
        with source.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            native = {index: (reader.line_num, row) for index, row in enumerate(reader, 1)}
        records = {record['id']: record for record in self.seed['records']}
        for series in self.new:
            samples = {row[0]: row for row in records[series['record_id']]['pollen_sample_audit']}
            for age, value, rowid, line, raw_age, raw_value, lower, upper, depth in series['rows']:
                native_line, row = native[rowid]
                total = sum(float(row[column]) for column in series['denominator_columns'])
                numerator = sum(float(row[column]) for column in series['source_columns'])
                self.assertEqual(line, native_line)
                self.assertEqual(row['entity_name'], series['source_event'])
                self.assertEqual(raw_age, row['INTCAL2020_median'])
                self.assertEqual(depth, row['avg_depth..cm.'])
                self.assertEqual(age, float(raw_age) / 1000)
                self.assertAlmostEqual(value, numerator * 100 / total)
                self.assertEqual(float(raw_value), numerator)
                self.assertEqual(samples[rowid][3], total)
                self.assertEqual(samples[rowid][7:], [row[column] for column in (
                    'INTCAL2020_uncert_5', 'INTCAL2020_uncert_95',
                    'INTCAL2020_uncert_25', 'INTCAL2020_uncert_75')])
                self.assertEqual((lower, upper), (None, None))

    def test_negative_ages_and_observed_zero_survive(self):
        self.assertTrue(any(row[0] < 0 for series in self.new for row in series['rows']))
        self.assertTrue(any(row[1] == 0 for series in self.new for row in series['rows']))
        for series in self.new:
            points = sorted((float(row[8]), row[0]) for row in series['rows'])
            self.assertTrue(all(second[0] > first[0] and second[1] >= first[1]
                                for first, second in zip(points, points[1:])))

    def test_blocked_chronologies_and_old_entities_are_not_reimported(self):
        previous = json.loads(batch.pollen.CONTRACT.read_bytes())
        names = {series['source_event'] for series in self.new}
        self.assertEqual(names, {entry['entity'] for entry in self.contract['reading_entities']})
        self.assertFalse(names & {entry['entity'] for entry in previous['reading_entities']})
        self.assertFalse(names & {'Villarquemado', 'ELX', 'GALDANA', 'ESGRAU', 'LLIGAT'})


if __name__ == '__main__':
    unittest.main()
