"""Validate explicit subsets of native multi-event source tables."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/importers'))
from curate_priority_v6 import select_events


class EventSelectionTest(unittest.TestCase):
    def setUp(self):
        self.events = {'A': {'label': 'A'}, 'B': {'label': 'B'}}

    def test_default_keeps_all_events(self):
        self.assertEqual(select_events(self.events, None), self.events)

    def test_explicit_selection_keeps_only_requested_events(self):
        self.assertEqual(select_events(self.events, ['B']), {'B': self.events['B']})

    def test_invalid_selections_are_rejected(self):
        for selection in ([], ['A', 'A'], ['missing']):
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                select_events(self.events, selection)


if __name__ == '__main__':
    unittest.main()
