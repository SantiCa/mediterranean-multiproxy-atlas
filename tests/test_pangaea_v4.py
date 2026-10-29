"""PANGAEA v4 source-to-cell contracts; offline and explicit cache skips."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pangaea_v4',ROOT/'scripts/importers/curate_pangaea_v4.py')
curation=importlib.util.module_from_spec(spec)
spec.loader.exec_module(curation)

class ParserContract(unittest.TestCase):
    def test_censored_missing_and_zero(self):
        self.assertEqual(curation.number('0'),0)
        self.assertEqual(curation.number('-0.069'),-.069)
        for cell in ('','NaN','inf','<0.2','not measured'):
            self.assertIsNone(curation.number(cell))

@unittest.skipUnless(all((curation.RAW/f'{i}.tsv').exists() for i in curation.IDS),'Ignored reviewed native PANGAEA cache absent; curator --download required')
class NativeBatchContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=curation.curate()
    def test_event_grain_and_every_cell_locator(self):
        d=self.data
        self.assertEqual((len(d['records']),len(d['series']),sum(len(s['rows']) for s in d['series'])),(11,41,4271))
        self.assertEqual(len({r['source_event'] for r in d['records']}),11)
        self.assertEqual({r['id'] for r in d['records']},{s['record_id'] for s in d['series']})
        for s in d['series']+d['quarantined_series']:
            i=int(s['id'].split(':')[0].split('-')[1])
            head,cols,rows,headerline=curation.read_native(i)
            byrow={n:(line,cells) for n,line,cells in rows}
            self.assertEqual(s['source_header_original'],cols)
            for row in s['rows']:
                line,cells=byrow[row[2]]
                self.assertEqual(row[3],line)
                self.assertEqual(row[4],cells[s['age_column_index']])
                self.assertEqual(row[5],cells[s['source_column_index']])
                self.assertEqual(row[0],float(row[4]))
                self.assertEqual(row[1],float(row[5]))
                error_column=s['value_uncertainty_source_column_index']
                self.assertEqual(row[7],curation.number(cells[error_column]) if error_column is not None else None)
            self.assertTrue(s['dataset_doi'] and s['paper_doi'] and s['citation'] and s['license'] and s['license_url'])
    def test_native_scales_uncertainty_and_shared_method(self):
        ss={s['id']:s for s in self.data['series']}
        ruber=[s for s in self.data['series'] if s['proxy']=='G_ruber_white_d18O_PDB']
        self.assertEqual(len(ruber),4)
        self.assertEqual(len({s['compatibility_group'] for s in ruber}),1)
        self.assertTrue(all(s['unit']=='‰ PDB' for s in ruber))
        nd=ss['pangaea-944660:epsilon_Nd_detrital']
        self.assertIn('2 sigma',nd['uncertainty_type'])
        self.assertTrue(any(r[7] is not None for r in nd['rows']))
        self.assertEqual(ss['pangaea-962034:fucose_d18O']['license'],'CC-BY-SA-4.0')
        self.assertEqual(ss['pangaea-962034:fucose_d18O']['unit'],'‰ VSMOW')
        self.assertEqual(ss['pangaea-954457:TOC']['publication_year'],2023)
        self.assertNotIn('pangaea-995820:leaf_wax_dD_NMF',ss)
        rec=next(r for r in self.data['records'] if r['source_event']=='PEX19-01')
        self.assertEqual(rec['publication_year'],2023)
        self.assertIn('deglaciation',rec['paper_title'])
    def test_bacon_and_epsilon_parameters_are_not_symmetric_errors(self):
        ss={s['id']:s for s in self.data['series']}
        dead=ss['pangaea-940127:C30_fatty_acid_dD']
        self.assertEqual(dead['age_probability_levels'],[.025,.16,.84,.975])
        self.assertEqual(len(dead['age_probability_bounds']),179)
        self.assertTrue(all(r[6] is None for r in dead['rows']))
        pex=next(s for s in self.data['quarantined_series'] if s['id']=='pangaea-995820:precipitation_dD_leafwax')
        self.assertNotIn('uncertainty_bounds',pex)
        self.assertTrue(all(r[7] is None for r in pex['rows']))
        self.assertTrue(all(float(b['epsilon_minus12_parameter'])>float(b['epsilon_plus12_parameter']) for b in pex['native_epsilon_sensitivity_parameters']))
    def test_negative_TOC_is_quarantined_without_clipping(self):
        q=self.data['quarantined_series']
        self.assertEqual(len(q),4)
        toc=next(s for s in q if s['id']=='pangaea-667403:TOC')
        self.assertEqual(len(toc['rows']),135)
        self.assertEqual(min(r[1] for r in toc['rows']),-1.71)
        self.assertNotIn(toc['id'],{s['id'] for s in self.data['series']})
        self.assertEqual(sum(r[0] is None for s in self.data['series'] for r in s['rows']),0)

    def test_mixed_age_units_are_not_repaired_or_mapped(self):
        active_ids={s['id'] for s in self.data['series']}
        for s in self.data['quarantined_series']:
            if not s['id'].startswith('pangaea-995820:'):continue
            self.assertEqual(s['chronology_status'],'quarantined_mixed_units')
            self.assertEqual(len(s['rows']),132)
            self.assertEqual(s['rows'][27][0],.970)
            self.assertEqual(s['rows'][28][0],1003)
            self.assertEqual(max(r[0] for r in s['rows']),11150)
            self.assertNotIn(s['id'],active_ids)
        self.assertLess(max(r[0] for s in self.data['series'] for r in s['rows']),1000)

if __name__=='__main__':unittest.main()

