import csv
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_forest_pollen_v17 as batch
import test_forest_pollen_v10 as previous_tests


class ReadingPollenCoastalBatch(previous_tests.ReadingPollenBatch):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data/processed/atlas-v17.json').read_bytes())
        cls.parent = json.loads(batch.BASE.read_bytes())
        cls.new = [series for series in cls.seed['series']
                   if series['id'] in cls.seed['append_series_ids']]
        cls.contract = json.loads(batch.CONTRACT.read_bytes())

    def test_blocked_chronologies_and_old_entities_are_not_reimported(self):
        super().test_blocked_chronologies_and_old_entities_are_not_reimported()
        events = {series['source_event'] for series in self.new}
        self.assertEqual(len(events), 5)
        self.assertFalse(events & {series.get('source_event') for series in self.parent['series']})
        self.assertFalse(events & {'ROQUETAS', 'ALCUDIA', 'Vilamora P01-5', 'Abi 05/07', 'LLIGAT'})

    def test_every_date_control_and_flag_reconciles_to_pinned_source(self):
        resource = self.contract['resources'][0]
        path = batch.pipeline.pollen.RAW / resource['file']
        if not path.exists():
            self.skipTest('Ignored Reading dates absent; restore with --fetch')
        self.assertEqual(batch.pipeline.pollen.sha(path.read_bytes()), resource['sha256'])
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            native = {index: dict(source_row=index, source_line=reader.line_num, original=row)
                      for index, row in enumerate(reader, 1)}
        records = {record['core']: record for record in self.seed['records'] if record.get('core')}
        for entry in self.contract['reading_entities']:
            audit = records[entry['entity']]['reading_dates_audit']
            self.assertEqual(audit['rows'], [native[index] for index in entry['date_rows']])
            self.assertEqual(audit['raw_sha256'], resource['sha256'])
            self.assertFalse(any(item['original']['material_dated'] == 'shells' for item in audit['rows']))
        candieira = records['CANDIEIR']['reading_dates_audit']['rows']
        self.assertEqual(sum(item['original']['age_used'] == 'no' for item in candieira), 5)
        self.assertTrue(any('parallel core VDL' in item['original']['notes']
                            for item in records['VdL PB2']['reading_dates_audit']['rows']))

    def test_identity_and_archive_context_are_explicit(self):
        report = json.loads((ROOT / 'reports/quantitative_v17_release.json').read_bytes())
        self.assertEqual(report['identity_audit'], self.contract['identity_audit'])
        for entry in self.contract['reading_entities']:
            record = next(record for record in self.seed['records'] if record.get('core') == entry['entity'])
            if entry['entity'] != 'CANDIEIR':
                self.assertIn('coastal or estuarine', record['archive_type'])
            for note in entry['qc_notes']:
                self.assertEqual(record['qc_notes'].count(note), 1)


if __name__ == '__main__':
    unittest.main()
