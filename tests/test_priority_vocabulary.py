import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/discovery'))
from priority_vocabulary import ratio_alias, target_family


class PriorityVocabulary(unittest.TestCase):
    def test_long_element_names_and_logarithms_remain_distinct(self):
        self.assertEqual(ratio_alias('Titanium/Calcium ratio'), 'Ti/Ca')
        self.assertEqual(ratio_alias('ln-Zirconium/Aluminium ratio'), 'ln Zr/Al')
        self.assertEqual(ratio_alias('log-Barium/Aluminium ratio'), 'log Ba/Al')
        self.assertIsNone(ratio_alias('Strontium-87/Strontium-86 ratio'))

    def test_false_oxygen_and_forest_matches_are_excluded(self):
        self.assertIsNone(target_family('Oxygen index, mass CO2', 'Rock-Eval pyrolysis', 'marine'))
        self.assertIsNone(target_family('Stephanodiscus alpinus', 'Diatom abundance'))
        self.assertIsNone(target_family('Uranium', 'Thorium-Uranium dating', 'marine'))
        self.assertIsNone(target_family('Quercus', 'Plant DNA taxa detected in lake'))

    def test_forest_and_current_targets_require_context(self):
        self.assertEqual(target_family('Fagus', 'Pollen profile'), 'polen')
        self.assertEqual(target_family('Pollen, temperate forest', 'CLAM age model and biomes'), 'polen')
        self.assertEqual(target_family('Size fraction 0.063-0.010 mm, sortable silt', 'Sortable silt'), 'corrientes')
