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
        self.assertEqual(scale.toggle(), ColorScaleMode.AUTOMATIC)
        self.assertEqual(scale.update(np.array([[30, 40]], dtype=np.uint16)), (30, 40))

    def test_constant_frame_has_nonzero_range(self):
        scale = ThermalColorScale()
        self.assertEqual(scale.update(np.full((2, 2), 100, dtype=np.uint16)), (100, 101))


if __name__ == '__main__':
    unittest.main()
