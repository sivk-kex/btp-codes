#!/usr/bin/env python3
"""Integration checks for travelling capillary-wave simulation."""

import math
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "travelling_wave.c"
QCC = ROOT.parent / "basilisk" / "src" / "qcc"


class TravellingWaveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SOURCE.exists():
            raise AssertionError("travelling_wave.c missing")
        cls.directory = tempfile.TemporaryDirectory()
        cls.executable = Path(cls.directory.name) / "travelling_wave"
        cls.compile_result = subprocess.run(
            [
                str(QCC),
                "-O2",
                "-Wall",
                SOURCE.name,
                "-o",
                str(cls.executable),
                "-lm",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_compiles_cleanly(self):
        self.assertEqual(self.compile_result.stderr, "")

    @classmethod
    def valid_rows(cls):
        if not hasattr(cls, "_valid_rows"):
            output = Path(cls.directory.name) / "travelling-wave.dat"
            subprocess.run(
                [str(cls.executable), "0.01", str(output), "64"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            cls._valid_rows = [
                tuple(map(float, line.split()))
                for line in output.read_text().splitlines()
                if line and not line.startswith("#")
            ]
        return cls._valid_rows

    def test_rejects_amplitude_outside_linear_scope(self):
        result = subprocess.run(
            [str(self.executable), "0.1", "unused.dat", "64"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("require 0 < A0 <= 0.05", result.stderr)

    def test_rejects_non_power_of_two_grid(self):
        result = subprocess.run(
            [str(self.executable), "0.01", "unused.dat", "48"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("power-of-two N >= 32", result.stderr)

    def test_rejects_malformed_numeric_arguments(self):
        for amplitude, grid in (("0.01bad", "32"), ("0.01", "32.5")):
            with self.subTest(amplitude=amplitude, grid=grid):
                result = subprocess.run(
                    [str(self.executable), amplitude, "/dev/null", grid],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("invalid input", result.stderr)

    def test_reports_output_file_failure(self):
        output = Path(self.directory.name) / "missing" / "wave.dat"
        result = subprocess.run(
            [str(self.executable), "0.01", str(output), "64"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("output file", result.stderr)

    @unittest.skipUnless(Path("/dev/full").exists(), "/dev/full unavailable")
    def test_reports_output_write_failure(self):
        result = subprocess.run(
            [str(self.executable), "0.01", "/dev/full", "32"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("output file", result.stderr)

    def test_initial_interface_is_requested_first_mode(self):
        rows = self.valid_rows()
        self.assertGreaterEqual(len(rows), 1)
        tau, cosine, sine, magnitude, phase, crest_x = rows[0]
        self.assertAlmostEqual(tau, 0.0, delta=1e-12)
        self.assertAlmostEqual(cosine, 0.01, delta=0.0001)
        self.assertAlmostEqual(sine, 0.0, delta=1e-12)
        self.assertAlmostEqual(magnitude, 0.01, delta=0.0001)
        self.assertAlmostEqual(phase, 0.0, delta=1e-10)
        self.assertAlmostEqual(crest_x, 0.0, delta=1e-10)

    def test_first_mode_travels_right_at_theoretical_phase_speed(self):
        rows = self.valid_rows()
        self.assertGreaterEqual(len(rows), 120)
        taus = [row[0] for row in rows]
        raw_phases = [row[4] for row in rows]
        phases = [raw_phases[0]]
        for previous, current in zip(raw_phases, raw_phases[1:]):
            delta = current - previous
            while delta <= -math.pi:
                delta += 2.*math.pi
            while delta > math.pi:
                delta -= 2.*math.pi
            phases.append(phases[-1] + delta)

        mean_tau = sum(taus)/len(taus)
        mean_phase = sum(phases)/len(phases)
        slope = sum(
            (tau - mean_tau)*(phase - mean_phase)
            for tau, phase in zip(taus, phases)
        )/sum((tau - mean_tau)**2 for tau in taus)

        self.assertGreaterEqual(taus[-1], 2.*math.pi - 0.05)
        self.assertGreater(phases[-1], 5.5)
        self.assertTrue(all(
            current - previous > -0.02
            for previous, current in zip(phases, phases[1:])
        ))
        self.assertGreater(slope, 0.9)
        self.assertLess(slope, 1.1)


if __name__ == "__main__":
    unittest.main()
