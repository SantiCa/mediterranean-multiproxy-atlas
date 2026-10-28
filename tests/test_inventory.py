"""Scientific metadata grain and provenance invariants, independent of live APIs."""
import unittest,json,math
from pathlib import Path
class InventoryIntegrity(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=json.loads((Path(__file__).resolve().parents[1]/'data/processed/inventory-v2.json').read_text(encoding='utf8'))
 def test_id_grain_and_scope(self):
  rows=self.d['records'];self.assertEqual(len(rows),15572);self.assertEqual(len({r['id'] for r in rows}),len(rows))
  for r in rows:
   if r['latitude'] is not None:
    self.assertTrue(28<=r['latitude']<=48 and -10<=r['longitude']<=42)
   self.assertTrue(r['source_url'].startswith('https://'));self.assertEqual(len(r['raw_sha256']),64)
 def test_campaigns_are_source_declared(self):
  ids={c['id'] for c in self.d['campaigns']};self.assertEqual(len(ids),289)
  for r in self.d['records']:
   for c in r['campaigns']:
    self.assertIn(c['id'],ids);self.assertTrue(c['source_locator']);self.assertTrue(c['name'])
 def test_dataset_is_not_a_core_and_age_is_not_publication_year(self):
  ds=[r for r in self.d['records'] if r['record_type']=='dataset'];self.assertEqual(len(ds),9726)
  for r in ds:self.assertFalse(r['campaigns']);self.assertNotIn('publication_year',r)
  t=self.d['time_extent'];self.assertEqual(t['numeric_max'],429.69);self.assertEqual(t['metadata_max'],121000)
 def test_complete_published_paleomed_snapshot(self):
  rows=[r for r in self.d['records'] if r['provider']=='PaleoMED20'];self.assertEqual(len(rows),1524)
  self.assertTrue(all(r['license']=='https://creativecommons.org/licenses/by/4.0/' for r in rows))
  # The compilation does not manufacture quantitative observations from proxy presence.
  self.assertTrue(all('rows' not in r and 'observations' not in r for r in self.d['records']))
if __name__=='__main__':unittest.main()
