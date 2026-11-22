import tempfile
import unittest
from pathlib import Path

from plot_travelling_wave import load_diagnostics, render_all, unwrap_phases


class TravellingWavePlotTest(unittest.TestCase):
    def test_loader_skips_headers_and_unwraps_phase(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "wave.dat"
            data.write_text(
                "# header\n"
                "0 1 0 1 3.0 0.1\n"
                "1 0 1 0.8 -3.0 0.2\n"
            )
            rows = load_diagnostics(data)
            self.assertEqual(len(rows), 2)
            self.assertGreater(unwrap_phases(rows)[1], unwrap_phases(rows)[0])

    def test_renderer_creates_both_graphs(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            (directory / "travelling-wave.dat").write_text(
                "# header\n"
                "0 0.01 0 0.01 0 0\n"
                "1 0.005 -0.005 0.007 0.8 0.1\n"
            )
            outputs = render_all(directory)
            self.assertEqual(len(outputs), 2)
            self.assertTrue(all(path.stat().st_size > 0 for path in outputs))


if __name__ == "__main__":
    unittest.main()
