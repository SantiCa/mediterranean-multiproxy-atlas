"""Parent immutability and exact cell/event provenance, never network tests."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/importers'))
import curate_priority_v6 as c
import curate_noaa_priority_v6 as noaa


@unittest.skipUnless((ROOT/'data/processed/atlas-v6.json').exists(), 'v6 not generated')
class PriorityRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(c.BASE.read_text(encoding='utf8'))
        cls.seed = json.loads((ROOT/'data/processed/atlas-v6.json').read_text(encoding='utf8'))
        cls.new = [s for s in cls.seed['series'] if s['id'] not in {s['id'] for s in cls.base['series']}]

    def test_parent_metadata_and_rows_are_immutable(self):
        for name in ('records', 'series'):
            current = {r['id']:r for r in self.seed[name]}
            for original in self.base[name]:
                self.assertEqual(original, current[original['id']])
        self.assertEqual(self.seed['parent_version'], self.base['version'])

    def test_every_new_observation_is_the_native_cell_and_event(self):
        if not (c.RAW/'966843.tsv').exists():
            self.skipTest('Ignored native originals absent; restore curator --fetch')
        cache = {}
        for s in self.new:
            if not s['dataset_doi'].startswith('10.1594/PANGAEA.'):
                continue
            dataset = s['dataset_doi'].split('.')[-1]
            if dataset not in cache:
                raw = (c.RAW/(dataset+'.tsv')).read_bytes()
                _, h, rows = c.native.parse_tsv(raw)
                cache[dataset] = (hashlib.sha256(raw).hexdigest(), h, {r:(line,cells) for r,line,cells in rows})
            sha, h, rows = cache[dataset]
            self.assertEqual(sha, s['raw_sha256'])
            self.assertEqual(s['source_column'], h[s['source_column_index']])
            age = c.native.age_rule(h)
            self.assertEqual(len(s['rows']), len({r[2] for r in s['rows']}))
            for a,value,row,line,original_age,original_value,_,_,_ in s['rows']:
                native_line, cells = rows[row]
                self.assertEqual(line, native_line)
                self.assertEqual(original_value, cells[s['source_column_index']])
                self.assertEqual(value, c.native.number(original_value))
                self.assertEqual(original_age, cells[age[0]])
                self.assertEqual(a, age[2](c.native.number(original_age)) if c.native.number(original_age) is not None else None)
                if 'Event' in h:
                    self.assertEqual(s['source_event'], cells[h.index('Event')])

    def test_holds_are_not_reinterpreted_or_clipped(self):
        for s in self.new:
            self.assertNotIn('mean_carb_free_percent', s.get('comparison_context_key') or '')
            if s['dataset_doi'].startswith('10.1594/PANGAEA.'):
                self.assertIn('/by/', s['license_url'])
            if s['unit'] == '%':
                self.assertTrue(all(0 <= r[1] <= 100 for r in s['rows']))
            if (s.get('parameter_name_pangaea') or '').startswith(('ln-', 'log-')):
                self.assertIn('ratio', s['parameter_name_pangaea'])

    def test_identical_location_does_not_merge_different_event_rows(self):
        matched = [s for s in self.new if s['dataset_doi']=='10.1594/PANGAEA.966843']
        self.assertEqual({s['source_event'] for s in matched}, {'GC-01A-PC','GC-01A-TC'})
        self.assertEqual(len({s['record_id'] for s in matched}), 2)

    def test_noaa_native_cells_calendar_unit_change_and_reported_sigma(self):
        if not (noaa.RAW/'43639-selvaggi2025-geochem.txt').exists():
            self.skipTest('Ignored NOAA originals absent; restore curator --fetch')
        config=json.loads(noaa.CONTRACT.read_text(encoding='utf8'))
        tables={f['table_id']:f for f in config['files']}
        for s in self.new:
            if not s['id'].startswith('noaa6-'):
                continue
            f=tables[s['source_table_id']];raw=(noaa.RAW/f['filename']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),s['raw_sha256'])
            _,h,native_rows=noaa.read_table(raw);rows={r:(line,cells) for r,line,cells in native_rows}
            for age,value,row,line,original_age,original_value,_,sigma,_ in s['rows']:
                native_line,cells=rows[row]
                self.assertEqual((line,original_age,original_value),(native_line,cells[h.index('Age_BP')],cells[s['source_column_index']]))
                self.assertEqual(age,float(original_age)/1000)
                self.assertEqual(value,float(original_value))
                if s['source_column']=='U/Mn':
                    self.assertEqual(sigma,c.native.number(cells[h.index('U/Mn_std')]))
        current=next(s for s in self.new if s.get('source_column')=='Ti/Ca' and s['id'].startswith('noaa6-'))
        self.assertLess(min(r[0] for r in current['rows']),0)
        self.assertTrue(any(h['study_id']=='10418' for h in config['held']))
        self.assertFalse(any(r.get('source_id')=='10418' for r in self.seed['records']))
