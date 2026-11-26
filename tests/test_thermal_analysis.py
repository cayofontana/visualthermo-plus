import tempfile
import unittest
from pathlib import Path

import numpy as np
from visualthermo.analysis import ThermalNoiseAnalyzer


class ThermalNoiseAnalyzerTests(unittest.TestCase):
    def test_statistics_and_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.npz'
            frames = np.array([[[100, 110]], [[102, 112]], [[104, 114]]], dtype=np.uint16)
            timestamps = np.array(['2026-11-16T18:00:00-03:00', '2026-11-16T18:00:01-03:00', '2026-11-16T18:00:02-03:00'])
            np.savez_compressed(path, frames=frames, timestamps=timestamps)
            analyzer = ThermalNoiseAnalyzer(path)
            report = analyzer.export(Path(directory) / 'out')
            self.assertEqual(report['frame_count'], 3)
            self.assertAlmostEqual(report['temporal_std_mean_y16'], 2)
            self.assertAlmostEqual(report['spatial_mean_removed_std_mean_y16'], 0)
            self.assertTrue((Path(directory) / 'out' / 'timeline.csv').exists())
            np.testing.assert_array_equal(np.load(path)['frames'], frames)

    def test_reject_invalid_dtype(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.npz'
            np.savez(path, frames=np.ones((2, 1, 1), dtype=np.float32), timestamps=np.array(['2026-11-16T18:00:00-03:00', '2026-11-16T18:00:01-03:00']))
            with self.assertRaises(ValueError):
                ThermalNoiseAnalyzer(path)
