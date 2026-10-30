import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts/importers'), str(ROOT / 'scripts/discovery')]
import curate_pangaea_v5 as c  # noqa: E402

H = ['Depth sed [m]', 'Age [ka BP]']


class AgeModelInterpolation(unittest.TestCase):
    def test_linear_inside_range_and_no_extrapolation(self):
        _, _, pts = c.model_points(H, [(1, 1, ['0.10', '1.0']), (2, 2, ['0.50', '5.0']), (3, 3, ['1.00', '12.0'])])
        self.assertEqual([c.interpolate(pts, z) for z in (0.1, 0.3, 1.0)], [1.0, 3.0, 12.0])
        self.assertIsNone(c.interpolate(pts, 0.05))
        self.assertIsNone(c.interpolate(pts, 1.2))
        self.assertIsNone(c.interpolate(pts, None))

    def test_a_bp_unit_change(self):
        _, _, pts = c.model_points(['Depth sed [m]', 'Age [a BP]'], [(1, 1, ['0', '1000']), (2, 2, ['1', '3000'])])
        self.assertEqual(c.interpolate(pts, 0.5), 2.0)

    def test_rejects_unusable_models(self):
        for header, rows in [(H, [(1, 1, ['0.1', '5']), (2, 2, ['0.5', '1'])]),       # inversión
                             (H, [(1, 1, ['0.1', '1']), (2, 2, ['0.1', '2'])]),       # misma profundidad
                             (H, [(1, 1, ['0.1', '1'])]),                             # un punto
                             (['Depth sed [m]', 'Age [ka BP] (14C)'], [(1, 1, ['0', '1']), (2, 2, ['1', '2'])]),
                             (['Age [ka BP]'], [(1, 1, ['1']), (2, 2, ['2'])])]:
            with self.assertRaises(ValueError):
                c.model_points(header, rows)

    def test_same_event_requires_label_and_coordinates(self):
        e = dict(label='MD95-2043', lat=36.143, lon=-2.621)
        self.assertTrue(c.same_event(e, dict(e)))
        self.assertFalse(c.same_event(e, dict(e, lat=36.2)))
        self.assertFalse(c.same_event(e, dict(e, label='MD95-2042')))


if __name__ == '__main__':
    unittest.main()


class ExtendedAgeRules(unittest.TestCase):
    def test_priority_and_new_units(self):
        self.assertEqual(c.age_rule(['Age [ka]', 'Age [ka BP]'])[0], 1)  # explicit BP wins
        k, rule, f = c.age_rule(['Depth sed [m]', 'Age [Ma]'])
        self.assertEqual((k, f(1.5)), (1, 1500))
        self.assertEqual(c.age_rule(['Age [ka]'])[1], c.UNSPECIFIED_KA)
        self.assertIsNone(c.age_rule(['Age [ka] (14C)']))

    def test_model_on_composite_depth(self):
        h = ['Depth sed [m]', 'Depth comp [mcd]', 'Age [ka BP]']
        d, _, pts = c.model_points(h, [(1, 1, ['1', '1.2', '10']), (2, 2, ['2', '2.5', '20'])], 'Depth comp [mcd]')
        self.assertEqual(d, 'Depth comp [mcd]')
        self.assertEqual(pts[0], (1.2, 10.0))
