import unittest
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "Aditya_Mazumdar_CHP400A_Autumn_ETE_Report_2026.docx"


class AutumnReportTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(OUTPUT.exists(), f"missing report: {OUTPUT}")
        with ZipFile(OUTPUT) as package:
            self.assertIsNone(package.testzip())
            self.names = set(package.namelist())
            self.document = package.read("word/document.xml").decode("utf-8")
            self.styles = package.read("word/styles.xml").decode("utf-8")
            self.settings = package.read("word/settings.xml").decode("utf-8")

    def test_contains_required_report_sections(self):
        for text in (
            "NONLINEAR EFFECTS ON CAPILLARY-GRAVITY WAVES",
            "SUPERVISOR CERTIFICATE",
            "DECLARATIONS",
            "ACKNOWLEDGEMENTS",
            "ABSTRACT",
            "CONTENTS",
            "NOMENCLATURE",
            "CHAPTER 1: INTRODUCTION",
            "CHAPTER 2: LITERATURE REVIEW",
            "CHAPTER 3: NUMERICAL METHODOLOGY",
            "CHAPTER 4: RESULTS AND DISCUSSION",
            "CHAPTER 5: CONCLUSIONS AND FUTURE WORK",
            "DATA AVAILABILITY",
            "REFERENCES",
            "APPENDIX A: REPRODUCIBILITY",
        ):
            self.assertIn(text, self.document)

    def test_uses_required_page_and_text_format(self):
        self.assertIn('w:ascii="Times New Roman"', self.styles)
        self.assertIn('w:sz w:val="24"', self.styles)
        self.assertIn('w:line="360"', self.styles)
        self.assertIn('w:pgSz w:w="11906" w:h="16838"', self.document)
        self.assertIn('<w:mirrorMargins/>', self.settings)

    def test_contains_required_declarations(self):
        self.assertIn("represents my own work", self.document)
        self.assertIn(
            "I hereby declare that I have disclosed all instances where AI (Artificial Intelligence) was used in creation of this report.",
            self.document,
        )
        self.assertIn("code drafting, report organization, and language editing", self.document)
        self.assertNotIn("All technical content", self.document)
        self.assertIn("https://github.com/sivk-kex/btp-codes", self.document)
        self.assertNotIn("DATA_ARCHIVE_URL_PENDING", self.document)
        self.assertIn("Signature of Supervisor", self.document)
        self.assertNotIn("________________", self.document)

    def test_embeds_project_figures(self):
        media = [name for name in self.names if name.startswith("word/media/")]
        self.assertGreaterEqual(len(media), 10)
        self.assertGreaterEqual(self.document.count("Figure "), 10)

    def test_preserves_scientific_scope(self):
        for value in ("19.75%", "10.43%", "6.91%", "0.24%", "0.90572", "49.65%"):
            self.assertIn(value, self.document)
        lowered = self.document.lower()
        self.assertNotIn("first-ever", lowered)
        self.assertNotIn("nonlinear capillary waves have not been studied", lowered)
        self.assertIn("pure-capillary travelling-wave validation", lowered)

    def test_methodology_matches_solver_implementation(self):
        self.assertIn('<w:pStyle w:val="Equation"/>', self.document)
        self.assertIn("cos(2πnx/λ)", self.document)
        self.assertIn("sin(2πnx/λ)", self.document)
        self.assertIn("no-normal-flow conditions on all four boundaries", self.document)
        self.assertIn("periodic horizontal boundaries", self.document)
        self.assertIn("adaptive axisymmetric quadtree", self.document)

    def test_front_matter_and_reproduction_commands_are_consistent(self):
        self.assertIn("Table 4. Travelling-wave diagnostics.", self.document)
        self.assertNotIn("Table 5. Travelling-wave diagnostics.", self.document)
        for command in (
            "./nonlinear_fourier 0.5 fourier-a0-0.5-N64.dat profiles-a0-0.5-N64.dat 64",
            "./nonlinear_fourier 0.5 fourier-a0-0.5-N256.dat profiles-a0-0.5-N256.dat 256",
            "../basilisk/src/qcc -O2 -Wall kayal2022_wave.c -o kayal2022_wave -lm",
        ):
            self.assertIn(command, self.document)

    def test_main_n128_fourier_archive_is_complete_and_matches_reported_peaks(self):
        path = ROOT.parent / "capwave-run" / "fourier-a0-0.5.dat"
        modes = defaultdict(list)
        for line in path.read_text().splitlines():
            if line and not line.startswith("#"):
                tau, harmonic, _, _, _, normalized = map(float, line.split())
                modes[int(harmonic)].append((tau, normalized))
        self.assertEqual(len(modes[1]), 500)
        self.assertAlmostEqual(modes[1][-1][0], 24.95, places=6)
        self.assertAlmostEqual(max(value for _, value in modes[3]), 0.1975, delta=0.0002)
        profiles = (ROOT.parent / "capwave-run" / "profiles-a0-0.5.dat").read_text()
        self.assertGreaterEqual(profiles.count("# frame"), 6)


if __name__ == "__main__":
    unittest.main()
