"""Reviewed v4 admission/incremental-release contracts, with no network required."""
import json
from collections import Counter
from pathlib import Path
import sqlite3
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class QuantitativeV4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=json.loads((ROOT/'data/processed/atlas-v3.json').read_text(encoding='utf8'))
        cls.seed=json.loads((ROOT/'data/processed/atlas-v4.json').read_text(encoding='utf8'))
    def test_parent_records_series_and_observations_are_unchanged(self):
        r={r['id']:r for r in self.seed['records']};s={s['id']:s for s in self.seed['series']}
        for original in self.base['records']:self.assertEqual(original,r[original['id']])
        for original in self.base['series']:self.assertEqual(original,s[original['id']])
        self.assertEqual(self.seed['parent_version'],self.base['version'])
        self.assertEqual(set(self.seed['append_series_ids']),set(s)-{s['id'] for s in self.base['series']})
    def test_admitted_values_have_valid_ages_units_and_source_identity(self):
        self.assertEqual((len(self.seed['records']),len(self.seed['series']),sum(len(s['rows']) for s in self.seed['series'])),(46,152,103534))
        allages=[r[0] for s in self.seed['series'] for r in s['rows'] if r[0] is not None]
        self.assertEqual((min(allages),max(allages)),(-.069,1365.0))
        for s in self.seed['series']:
            self.assertEqual(len({r[2] for r in s['rows']}),len(s['rows']))
            self.assertTrue(s['unit'] and s['compatibility_group'] and s['chronology_label'])
        active={s['dataset_doi'] for s in self.seed['series'] if s.get('dataset_doi')}
        self.assertNotIn('10.1594/PANGAEA.995820',active)
        self.assertNotIn('10.1594/PANGAEA.667403',active)
        pex=next(r for r in self.seed['records'] if r['id']=='pangaea-954457')
        self.assertNotIn('datacite:10.1594/pangaea.995820',pex['inventory_ids'])
        self.assertIn('datacite:10.1594/pangaea.995820',pex['held_quantitative_inventory_ids'])
        self.assertEqual(sum(r[0] is None for s in self.seed['series'] for r in s['rows']),101)
    def test_incremental_sqlite_import_preserves_parent_rows_and_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            db=sqlite3.connect(Path(directory)/'v4.sqlite')
            db.execute('PRAGMA foreign_keys=ON')
            for p in sorted((ROOT/'migrations').glob('*.sql')):db.executescript(p.read_text(encoding='utf8'))
            def insert(source):
                for r in source['records']:db.execute('INSERT OR IGNORE INTO atlas_records VALUES(?,?,?,?,?,?)',(r['id'],r['name'],r['realm'],r['latitude'],r['longitude'],json.dumps(r)))
                for s in source['series']:
                    db.execute('INSERT OR IGNORE INTO atlas_series VALUES(?,?,?,?,?,?)',(s['id'],s['record_id'],s['proxy'],s['label'],s['unit'],json.dumps({k:v for k,v in s.items() if k!='rows'})))
                    db.executemany('INSERT OR IGNORE INTO atlas_observations VALUES(?,?,?,?,?,?,?,?,?,?,?)',[(s['id']+':'+str(r[2]),s['id'],*r) for r in s['rows']])
            insert(self.base)
            parent_count=db.execute('SELECT count(*) FROM atlas_observations').fetchone()[0]
            insert({'records':self.seed['records'],'series':[s for s in self.seed['series'] if s['id'] in self.seed['append_series_ids']]})
            self.assertEqual(db.execute('SELECT count(*) FROM atlas_observations').fetchone()[0]-parent_count,22195)
            for s in self.seed['series']:
                actual={r[2]:list(r) for r in db.execute('SELECT age_ka_bp,value,source_row,source_line,original_age,original_value,age_uncertainty_ka,value_uncertainty,depth_original FROM atlas_observations WHERE series_id=?',(s['id'],))}
                self.assertEqual(actual,{r[2]:r for r in s['rows']})
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
            db.close()
