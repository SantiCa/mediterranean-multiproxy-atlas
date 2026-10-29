"""Release integration checks run from versioned data, without network."""
import json
import math
from pathlib import Path
import sqlite3
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class QuantitativeRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed=json.loads((ROOT/'data/processed/atlas-v3.json').read_text(encoding='utf8'))
    def test_baseline_values_and_observation_ids_are_immutable(self):
        baseline=json.loads((ROOT/'data/processed/atlas-v1.json').read_text(encoding='utf8'))
        byid={s['id']:s for s in self.seed['series']}
        for series in baseline['series']:
            self.assertEqual(series['rows'],byid[series['id']]['rows'])
        for series in self.seed['series']:
            self.assertEqual(len(series['rows']),len({r[2] for r in series['rows']}))
            self.assertEqual(series['observation_count'],len(series['rows']))
    def test_chronology_unknowns_units_and_quarantine(self):
        self.assertEqual((len(self.seed['records']),len(self.seed['series']),sum(len(s['rows']) for s in self.seed['series'])),(29,89,81339))
        self.assertEqual(sum(r[0] is None for s in self.seed['series'] for r in s['rows']),101)
        self.assertNotIn('noaa-13666-54312:23340:terr',{s['id'] for s in self.seed['series']})
        self.assertTrue(all(s['unit'] and s['compatibility_group'] and s['chronology_label'] for s in self.seed['series']))
        ages=[r[0] for s in self.seed['series'] for r in s['rows'] if r[0] is not None]
        self.assertEqual((min(ages),max(ages)),(-.0574,1365.0))
        editorial=next(r for r in self.seed['records'] if r['id']=='pangaea-438795')
        self.assertIsNone(editorial['publication_year'])
        self.assertIsNone(editorial['paper_doi'])
    def test_sqlite_roundtrip_all_81339_observations(self):
        with tempfile.TemporaryDirectory() as directory:
            db=sqlite3.connect(Path(directory)/'roundtrip.sqlite')
            db.execute('PRAGMA foreign_keys=ON')
            for path in sorted((ROOT/'migrations').glob('*.sql')):db.executescript(path.read_text(encoding='utf8'))
            for r in self.seed['records']:db.execute('INSERT INTO atlas_records VALUES(?,?,?,?,?,?)',(r['id'],r['name'],r['realm'],r['latitude'],r['longitude'],json.dumps(r)))
            for s in self.seed['series']:
                db.execute('INSERT INTO atlas_series VALUES(?,?,?,?,?,?)',(s['id'],s['record_id'],s['proxy'],s['label'],s['unit'],'{}'))
                db.executemany('INSERT INTO atlas_observations VALUES(?,?,?,?,?,?,?,?,?,?,?)',[(s['id']+':'+str(r[2]),s['id'],*r) for r in s['rows']])
                actual={r[2]:list(r) for r in db.execute('SELECT age_ka_bp,value,source_row,source_line,original_age,original_value,age_uncertainty_ka,value_uncertainty,depth_original FROM atlas_observations WHERE series_id=?',(s['id'],))}
                self.assertEqual(actual,{r[2]:r for r in s['rows']})
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
            db.close()
