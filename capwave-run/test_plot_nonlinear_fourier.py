#!/usr/bin/env python3
"""Checks parsers used by nonlinear Fourier plots."""

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PLOTTER = ROOT / "plot_nonlinear_fourier.py"


class FourierPlotDataTest(unittest.TestCase):
    def load_plotter(self):
        self.assertTrue(PLOTTER.exists(), "plot_nonlinear_fourier.py missing")
        spec = importlib.util.spec_from_file_location("fourier_plotter", PLOTTER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_spectrum_rows_are_grouped_by_harmonic(self):
        plotter = self.load_plotter()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fourier.dat"
            path.write_text(
                "# tau harmonic cosine sine magnitude magnitude_over_a0\n"
                "0 1 0.1 0 0.1 1\n"
                "0 2 0 0 0 0\n"
                "0.05 1 0.09 0 0.09 0.9\n"
            )
            modes = plotter.load_spectrum(path)

        self.assertEqual(modes[1], [(0.0, 1.0), (0.05, 0.9)])
        self.assertEqual(modes[2], [(0.0, 0.0)])

    def test_profile_frames_keep_tau_and_segments(self):
        plotter = self.load_plotter()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.dat"
            path.write_text(
                "# frame 0 time 0\n"
                "0 0.1\n1 0.1\n\n"
                "# end\n"
                "# frame 5 time 0.4\n"
                "0 -0.1\n1 -0.1\n\n"
                "# end\n"
            )
            frames = plotter.load_profiles(path)

        self.assertEqual(sorted(frames), [0.0, 5.0])
        self.assertEqual(frames[0.0], [[(0.0, 0.1), (1.0, 0.1)]])

    def test_renderer_creates_three_png_figures(self):
        plotter = self.load_plotter()
        self.assertTrue(hasattr(plotter, "render_all"), "render_all missing")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for label, amplitude in (("0.1", 0.1), ("0.5", 0.5)):
                spectrum = output / f"fourier-a0-{label}.dat"
                spectrum.write_text(
                    "# tau harmonic cosine sine magnitude magnitude_over_a0\n"
                    + "".join(
                        f"{tau} {mode} 0 0 {value*amplitude} {value}\n"
                        for tau, value in ((0, 1), (1, 0.8))
                        for mode in range(1, 9)
                    )
                )
                (output / f"profiles-a0-{label}.dat").write_text(
                    "# frame 0 time 0\n"
                    f"0 {amplitude}\n1 {amplitude}\n\n"
                    "# end\n"
                    "# frame 5 time 0.4\n"
                    f"0 {-amplitude}\n1 {-amplitude}\n\n"
                    "# end\n"
                )
            figures = plotter.render_all(output)

            self.assertEqual(len(figures), 3)
            for figure in figures:
                self.assertEqual(figure.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_grid_peaks_use_maximum_from_each_resolution(self):
        plotter = self.load_plotter()
        self.assertTrue(hasattr(plotter, "load_grid_peaks"), "load_grid_peaks missing")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = {
                32: "fourier-a0-{label}-N64.dat",
                64: "fourier-a0-{label}.dat",
                128: "fourier-a0-{label}-N256.dat",
            }
            expected = {32: 0.2, 64: 0.25, 128: 0.3}
            for label in ("0.1", "0.5"):
                for resolution, pattern in names.items():
                    (root / pattern.format(label=label)).write_text(
                        "# tau harmonic cosine sine magnitude magnitude_over_a0\n"
                        f"0 3 0 0 0.1 0.1\n"
                        f"1 3 0 0 {expected[resolution]} {expected[resolution]}\n"
                    )

            peaks = plotter.load_grid_peaks(root)

        self.assertEqual(peaks["0.1"][32][3], 0.2)
        self.assertEqual(peaks["0.5"][64][3], 0.25)
        self.assertEqual(peaks["0.5"][128][3], 0.3)

    def test_grid_convergence_renderer_creates_png(self):
        plotter = self.load_plotter()
        self.assertTrue(
            hasattr(plotter, "render_grid_convergence"),
            "render_grid_convergence missing",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = {
                32: "fourier-a0-{label}-N64.dat",
                64: "fourier-a0-{label}.dat",
                128: "fourier-a0-{label}-N256.dat",
            }
            for label in ("0.1", "0.5"):
                for resolution, pattern in names.items():
                    (root / pattern.format(label=label)).write_text(
                        "# tau harmonic cosine sine magnitude magnitude_over_a0\n"
                        + "".join(
                            f"0 {mode} 0 0 {1/mode} {1/mode}\n"
                            for mode in (1, 3, 5, 7)
                        )
                    )

            figure = plotter.render_grid_convergence(root)

            self.assertEqual(figure.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()
