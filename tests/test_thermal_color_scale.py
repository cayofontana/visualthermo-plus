import unittest
import numpy as np

from visualthermo.camera.thermal_color_scale import ColorScaleMode, ThermalColorScale


class ThermalColorScaleTests(unittest.TestCase):
    def test_automatic_tracks_each_frame(self):
        scale = ThermalColorScale()
        self.assertEqual(scale.update(np.array([[10, 20]], dtype=np.uint16)), (10, 20))
        self.assertEqual(scale.update(np.array([[30, 40]], dtype=np.uint16)), (30, 40))

    def test_fixed_keeps_previous_limits(self):
        scale = ThermalColorScale()
        scale.update(np.array([[10, 20]], dtype=np.uint16))
        self.assertEqual(scale.toggle(), ColorScaleMode.FIXED)
        self.assertEqual(scale.update(np.array([[30, 40]], dtype=np.uint16)), (10, 20))
        self.assertEqual(scale.toggle(), ColorScaleMode.ADAPTIVE)
        self.assertEqual(scale.toggle(), ColorScaleMode.AUTOMATIC)
        self.assertEqual(scale.update(np.array([[30, 40]], dtype=np.uint16)), (30, 40))

    def test_adaptive_smooths_extremes(self):
        scale = ThermalColorScale(alpha=0.2)
        scale.update(np.array([[10, 20]], dtype=np.uint16))
        self.assertEqual(scale.toggle(), ColorScaleMode.FIXED)
        self.assertEqual(scale.toggle(), ColorScaleMode.ADAPTIVE)
        self.assertEqual(scale.update(np.array([[30, 40]], dtype=np.uint16)), (14.0, 24.0))
        limits = scale.update(np.array([[30, 40]], dtype=np.uint16))
        self.assertAlmostEqual(limits[0], 17.2)
        self.assertAlmostEqual(limits[1], 27.2)
        self.assertEqual(scale.toggle(), ColorScaleMode.AUTOMATIC)
        self.assertEqual(scale.update(np.array([[30, 40]], dtype=np.uint16)), (30, 40))

    def test_adaptive_initializes_without_previous_frame(self):
        scale = ThermalColorScale()
        scale.toggle()
        scale.toggle()
        self.assertEqual(scale.update(np.array([[100, 200]], dtype=np.uint16)), (100.0, 200.0))

    def test_invalid_alpha(self):
        for alpha in (0, -0.1, 1.1):
            with self.assertRaises(ValueError):
                ThermalColorScale(alpha=alpha)

    def test_constant_frame_has_nonzero_range(self):
        scale = ThermalColorScale()
        self.assertEqual(scale.update(np.full((2, 2), 100, dtype=np.uint16)), (100, 101))


if __name__ == '__main__':
    unittest.main()
