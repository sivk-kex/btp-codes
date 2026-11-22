#!/usr/bin/env python3
"""Checks traditional capwave amplitude selection and plots."""

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
QCC = ROOT.parent / "basilisk" / "src" / "qcc"
PLOTTER = ROOT / "plot_capwave_amplitudes.py"


class TraditionalCapwaveAmplitudeTest(unittest.TestCase):
    def test_capwave_compiles_cleanly_with_a0_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    str(QCC),
                    "-O2",
                    "-Wall",
                    "-DA0=0.1",
                    "capwave.c",
                    "-o",
                    str(Path(directory) / "capwave"),
                    "-lm",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.stderr, "")

    def test_a0_compile_flag_changes_initial_capwave_amplitude(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            executable = directory / "capwave-a0-0.1"
            subprocess.run(
                [
                    str(QCC),
                    "-O2",
                    "-Wall",
                    "-DA0=0.1",
                    "capwave.c",
                    "-o",
                    str(executable),
                    "-lm",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [str(executable)],
                cwd=directory,
                check=True,
                capture_output=True,
                text=True,
            )
            first_amplitude = float(
                (directory / "wave-128").read_text().splitlines()[0].split()[1]
            )

        self.assertAlmostEqual(first_amplitude, 0.1, delta=0.002)

    def test_plotter_creates_one_graph_per_initial_amplitude(self):
        self.assertTrue(PLOTTER.exists(), "plot_capwave_amplitudes.py missing")
        spec = importlib.util.spec_from_file_location("capwave_amplitude_plotter", PLOTTER)
        plotter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plotter)

        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            for label, amplitude in (("0.1", 0.1), ("0.5", 0.5)):
                (directory / f"capwave-a0-{label}.dat").write_text(
                    f"0 {amplitude}\n1 {0.8*amplitude}\n"
                )

            figures = plotter.render_all(directory)

            self.assertEqual(
                [figure.name for figure in figures],
                [
                    "amplitude-a0-0.1-vs-time.png",
                    "amplitude-a0-0.5-vs-time.png",
                ],
            )
            for figure in figures:
                self.assertEqual(figure.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()
