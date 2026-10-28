"""Validate published compact data, database import and original-cell lineage."""
import json
from contextlib import closing
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_atlas_v1 import write_sqlite


class AtlasV1Integrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/'data/processed/atlas-v1.json'
        if not path.exists():raise unittest.SkipTest('Atlas seed not present')
        cls.seed=json.loads(path.read_text(encoding='utf-8'))

    def test_counts_identity_and_unknown_age(self):
        seed=self.seed
        self.assertEqual(len(seed['records']),13)
        self.assertEqual(len(seed['series']),22)
        self.assertEqual(sum(len(s['rows']) for s in seed['series']),14751)
        ids=[(s['id'],row[2]) for s in seed['series'] for row in s['rows']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(sum(row[0] is None for s in seed['series'] for row in s['rows']),40)
        self.assertTrue(any(row[0] is not None and row[0]<0 for s in seed['series'] for row in s['rows']))
        self.assertTrue(any(row[7] is not None for s in seed['series'] for row in s['rows']))

    def test_database_migrations_and_foreign_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'atlas.sqlite'
            write_sqlite(self.seed,path,ROOT/'migrations')
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
                self.assertFalse(db.execute('PRAGMA foreign_key_check').fetchall())
                self.assertEqual(db.execute('SELECT count(*) FROM atlas_observations').fetchone()[0],14751)
                self.assertGreater(db.execute('SELECT count(*) FROM atlas_observations WHERE value_uncertainty IS NOT NULL').fetchone()[0],0)
            with self.assertRaises(RuntimeError):write_sqlite(self.seed,path,ROOT/'migrations')

    def test_existing_seed_cells_preserved(self):
        original=json.loads((ROOT/'data/processed/observations.json').read_text(encoding='utf-8'))
        series={s['id']:s for s in self.seed['series']}
        indexed={key:{r[2]:r for r in s['rows']} for key,s in series.items()}
        for old in original:
            row=indexed[f"pangaea-{old['dataset_id']}:{old['proxy']}"][old['source_row']]
            self.assertEqual(row[0],old['age_ka_bp']);self.assertEqual(row[1],old['value'])
            self.assertEqual(row[3],old['source_line']);self.assertEqual(row[5],old['source_value'])
            self.assertEqual(row[7],old['value_uncertainty'])


if __name__=='__main__':unittest.main()
