"""Regression: corrected-metre acronym must not cause a factor100 conversion."""
import csv
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ODP977ADepthAudit(unittest.TestCase):
    def test_annotation_keeps_native_metres_and_separate_frame(self):
        a=next(x for x in json.loads((ROOT/'config/curation_assertions.json').read_text(encoding='utf8'))['assertions'] if x['dataset_doi']=='10.1594/PANGAEA.921230')
        self.assertEqual((a['unit'],a['numeric_transform'],a['status']),('m','none','resolved'))
        self.assertIn('no automatic join',a['depth_join_policy'])
        self.assertFalse(a['prior_values_changed'])
    @unittest.skipUnless((ROOT/'data/raw/pangaea/921230.tsv').exists(),'Ignored native TSV absent')
    def test_versioned_series_retain_all_181_native_depth_strings(self):
        text=(ROOT/'data/raw/pangaea/921230.tsv').read_text(encoding='utf-8-sig')
        native=list(csv.DictReader(text.split('*/',1)[1].strip().splitlines(),delimiter='\t'))
        self.assertEqual(len(native),181)
        self.assertEqual((min(float(r['Depth corr [m]']) for r in native),max(float(r['Depth corr [m]']) for r in native)),(58.64,67.49))
        seed=json.loads((ROOT/'data/processed/atlas-v3.json').read_text(encoding='utf8'))
        series=[s for s in seed['series'] if s['record_id']=='pangaea-921230']
        self.assertEqual(len(series),2)
        for s in series:
            for row in s['rows']:
                self.assertEqual(row[8],native[row[2]-1]['Depth corr [m]'])
                self.assertEqual(row[0],float(native[row[2]-1]['Age [ka BP]']))
