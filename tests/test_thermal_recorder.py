import tempfile
import unittest
from pathlib import Path

import numpy as np
from matplotlib import image as mpl_image
from visualthermo.camera.thermal_recorder import ThermalRecorder


class ThermalRecorderTests(unittest.TestCase):
    def test_save_frame_generates_npy_and_png(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = ThermalRecorder(directory)
            frame = np.array([[29000, 30000], [31000, 32000]], dtype=np.uint16)
            npy_path = recorder.save_frame(frame, (29000, 32000))
            png_path = npy_path.with_suffix('.png')
            self.assertTrue(npy_path.exists())
            self.assertTrue(png_path.exists())
            self.assertEqual(npy_path.name[:6], 'frame_')
            np.testing.assert_array_equal(np.load(npy_path), frame)
            self.assertEqual(mpl_image.imread(png_path).shape[:2], frame.shape)


if __name__ == '__main__':
    unittest.main()
