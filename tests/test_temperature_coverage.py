"""Scientific triage guards; no network or bulk downloads in tests."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('coverage_temperature', ROOT / 'scripts/temperature_coverage.py')
coverage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coverage)


class TemperatureCoverage(unittest.TestCase):
    def test_lab_and_downhole_temperature_are_not_paleo_sst(self):
        for name in ('Rock-Eval pyrolysis results', 'Downhole temperature in ODP Hole 161-977A', 'Curie Temperatures of IODP Hole'):
            self.assertEqual(coverage.classify(name, ['Temperature'])[0], 'outside_target_temperature')

    def test_oxygen_isotopes_and_ratios_do_not_become_temperature(self):
        self.assertEqual(coverage.classify('Mg/Ca in Candona', ['Mg/Ca', 'δ18O'])[0], 'metadata_ambiguous')

    def test_targets_are_separated_and_native_review_is_required(self):
        for title, target in [('Sea surface temperature reconstruction', 'sea_surface'),
                              ('Bottom water temperature reconstruction', 'bottom_water'),
                              ('Chironomid-inferred July-air temperature', 'air'),
                              ('Global Database of Borehole Temperatures and Climate Reconstructions', 'ground_surface')]:
            state, reason, hint = coverage.classify(title, [])
            self.assertEqual(state, 'pending_native_review')
            self.assertEqual(hint, target)

    def test_admission_is_temperature_series_not_presence_of_doi(self):
        seed = dict(records=[dict(id='core', provider='PANGAEA', dataset_doi='10.fake/one')],
            series=[dict(id='not-temp', record_id='core', family='Micropaleontología', rows=[[1, 2]])])
        self.assertEqual(coverage.admitted_sources(seed), ({}, {}))
