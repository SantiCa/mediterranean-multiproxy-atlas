"""Offline scientific contracts and full native-cell checks for NOAA v4."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('curate_noaa_v4',ROOT/'scripts/importers/curate_noaa_v4.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
contract=json.loads(m.CONTRACT.read_text(encoding='utf8'))

class NOAA4ParserContracts(unittest.TestCase):
    def test_explicit_age_references_missing_and_signed_values(self):
        self.assertEqual(m.age_ka('1994','CE'),-.044)
        self.assertEqual(m.age_ka('4803','BP_years'),4.803)
        self.assertEqual(m.number('0'),0)
        self.assertEqual(m.number('-0.002'),-.002)
        self.assertIsNone(m.number('NA'))
        self.assertIsNone(m.number('<0.01'))
        with self.assertRaises(ValueError):m.age_ka('10000','radiocarbon_BP')
    def test_encoding_and_optional_comment_do_not_shift_line_identity(self):
        table={'encoding':'cp1252','legacy_header_line':3,'optional_trailing_columns':['Comments']}
        raw=b'Lake\nSilica\nage\tvalue\tComments\n10\t0\n20\t5\t\n'
        header,rows,_=m.read_table(raw,table)
        self.assertEqual(rows,[(1,4,{'age':'10','value':'0','Comments':''}),(2,5,{'age':'20','value':'5','Comments':''})])
        self.assertEqual(header,['age','value','Comments'])

@unittest.skipUnless((m.CACHE/'kaite2021sr.txt').exists(),'Ignored NOAA v4 originals absent; run curator --fetch')
class NOAA4NativeIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=m.curate()
        cls.resources={r['filename']:r for r in contract['resources']}
    def test_every_value_age_uncertainty_and_locator_matches_source(self):
        tables={Path(t['filename']).stem:t for t in contract['tables']}
        raw_tables={}
        for table in contract['tables']:
            resource=self.resources[table['filename']]
            raw=m.native(resource)
            _,rows,_=m.read_table(raw,table)
            raw_tables[Path(table['filename']).stem]=(table,{r[0]:r for r in rows},raw.removeprefix(b'\xef\xbb\xbf').decode(table['encoding']).splitlines())
        for series in self.result['series']+self.result['quarantined_series']:
            table,byrow,lines=raw_tables[series['source_table_id']]
            specification=next(s for s in table['specs'] if s['column']==series['source_column'])
            for row in series['rows']:
                ordinal,line,native=byrow[row[2]]
                self.assertEqual(row[3],line)
                self.assertEqual(row[4],native[table['age_column']])
                self.assertEqual(row[0],m.age_ka(row[4],table['age_transform']))
                self.assertEqual(row[5],native[series['source_column']])
                self.assertEqual(row[1],float(row[5]))
                self.assertEqual(row[8],native.get(table.get('depth_column')))
                self.assertEqual(lines[row[3]-1].split('\t')[series['source_header_original'].index(series['source_column'])],row[5])
                self.assertEqual(row[7],m.number(native[specification['uncertainty_column']]) if specification.get('uncertainty_column') else None)
                self.assertIsNone(row[6])
    def test_counts_new_core_identity_and_quarantines(self):
        r=self.result
        self.assertEqual((len(r['records']),len(r['series']),sum(len(s['rows']) for s in r['series'])),(6,22,17924))
        self.assertEqual((len(r['quarantined_series']),sum(len(s['rows']) for s in r['quarantined_series'])),(7,3007))
        baseline=json.loads((ROOT/'data/processed/atlas-v3.json').read_text(encoding='utf8'))
        self.assertFalse({r['id'] for r in baseline['records']}&{r['id'] for r in self.result['records']})
        self.assertFalse(self.result['duplicate_review']['exact_vector_duplicates'])
        self.assertFalse(self.result['duplicate_review']['large_partial_matches'])
        quarantined={s['proxy']:s for s in r['quarantined_series']}
        self.assertEqual(quarantined['normative_biogenic_silica_raw']['negative_value_cells'],73)
        self.assertTrue(all(s['negative_value_cells']>0 or s['proxy']=='TRIO1_La_Th' for s in r['quarantined_series']))
    def test_units_representations_and_coordinate_discrepancy_are_explicit(self):
        kaite=next(r for r in self.result['records'] if r['source_id']=='33716')
        self.assertEqual((kaite['latitude'],kaite['longitude']),(43+2/60,-(3+39/60)))
        self.assertNotEqual(kaite['source_coordinates_noaa_text'],kaite['source_coordinates_noaa_json'])
        sr=next(s for s in self.result['series'] if s['proxy']=='speleothem_87Sr_86Sr')
        flux=next(s for s in self.result['series'] if s['proxy']=='dust_flux_Saharan_Kaite')
        self.assertEqual(sr['evidence_type'],'measurement')
        self.assertEqual(flux['evidence_type'],'published_reconstruction')
        self.assertEqual(flux['unit'],'g/m²/año')
        normalized=[s for s in self.result['series'] if s['family']=='Mineralogía']
        self.assertEqual(len(normalized),2)
        self.assertTrue(any(s['negative_value_cells'] for s in normalized))
        self.assertTrue(all(s['unit']=='índice normalizado' for s in normalized))
        self.assertFalse(any(s['source_column']=='d18O_vsmow' for s in self.result['series']))
        ifoulki=[s for s in self.result['series'] if s['record_id']=='noaa-23970-57635']
        self.assertTrue(all(s['source_encoding']=='cp1252' for s in ifoulki))
        self.assertTrue(all(s['age_transform']=='CE' for s in ifoulki))
