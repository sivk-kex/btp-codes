#!/usr/bin/env python3
"""Integration check for nonlinear capillary-wave Fourier output."""

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "nonlinear_fourier.c"
QCC = ROOT.parent / "basilisk" / "src" / "qcc"


class NonlinearFourierTest(unittest.TestCase):
    def test_initial_cosine_is_isolated_in_first_harmonic(self):
        self.assertTrue(SOURCE.exists(), "nonlinear_fourier.c missing")

        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "nonlinear_fourier"
            subprocess.run(
                [
                    str(QCC),
                    "-O2",
                    "-Wall",
                    "-DTAU_END=0.",
                    SOURCE.name,
                    "-o",
                    str(executable),
                    "-lm",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            for amplitude in (0.1, 0.5):
                spectrum = Path(directory) / f"fourier-{amplitude}.dat"
                profiles = Path(directory) / f"profiles-{amplitude}.dat"
                subprocess.run(
                    [
                        str(executable),
                        str(amplitude),
                        str(spectrum),
                        str(profiles),
                        "64",
                    ],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )

                rows = [
                    tuple(map(float, line.split()))
                    for line in spectrum.read_text().splitlines()
                    if line and not line.startswith("#")
                ]
                self.assertIn("cells_per_wavelength=32", spectrum.read_text())
                self.assertEqual(len(rows), 8)
                self.assertEqual([int(row[1]) for row in rows], list(range(1, 9)))
                self.assertAlmostEqual(rows[0][4], amplitude, delta=0.01 * amplitude)
                self.assertAlmostEqual(rows[0][5], 1.0, delta=0.01)
                self.assertLess(max(row[5] for row in rows[1:]), 0.01)
                self.assertIn("# frame 0", profiles.read_text())


if __name__ == "__main__":
    unittest.main()
