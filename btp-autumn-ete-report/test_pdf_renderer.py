import subprocess
import unittest
from pathlib import Path

from render_pdf import ascii_text, decode_png, render_equation_png, render_report


ROOT = Path(__file__).resolve().parent
PDF = ROOT / "output" / "Aditya_Mazumdar_CHP400A_Autumn_ETE_Report_2026.pdf"


class PdfRendererTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        render_report()

    def test_creates_valid_a4_pdf_below_page_limit(self):
        self.assertTrue(PDF.exists())
        self.assertEqual(PDF.read_bytes()[:4], b"%PDF")
        info = subprocess.run(
            ["pdfinfo", str(PDF)], check=True, text=True, capture_output=True
        ).stdout
        pages = int(next(line.split(":", 1)[1] for line in info.splitlines()
                         if line.startswith("Pages:")).strip())
        self.assertLess(pages, 50)
        self.assertIn("A4", info)

    def test_pdf_contains_required_text(self):
        extracted = subprocess.run(
            ["pdftotext", str(PDF), "-"], check=True, text=True, capture_output=True
        ).stdout
        for text in (
            "NONLINEAR EFFECTS ON CAPILLARY-GRAVITY WAVES",
            "Chapter 2: Literature Review",
            "Chapter 4: Results and Discussion",
            "19.75%",
            "0.90572",
            "https://github.com/sivk-kex/btp-codes",
            "disclosed all instances",
        ):
            self.assertIn(text, extracted)
        self.assertNotIn("Supervisor comments", extracted)
        self.assertNotIn("?", extracted)
        self.assertNotIn("Update table of contents", extracted)
        self.assertIn("Chapter 1: Introduction", extracted)
        self.assertNotIn("Quantity | Standing/Fourier cases", extracted)
        self.assertNotIn("integral_", extracted)
        self.assertNotIn("sqrt[", extracted)
        self.assertIn("________________", extracted)
        self.assertRegex(extracted, r"(?m)^Chapter 2: Literature Review .* 3$")
        self.assertRegex(extracted, r"(?m)^References .* 21$")
        self.assertRegex(extracted, r"(?m)^Appendix A: Reproducibility Record .* 22$")

    def test_ascii_conversion_preserves_letter_t(self):
        self.assertEqual(ascii_text("technical test text"), "technical test text")

    def test_declaration_page_does_not_overflow_into_supervisor_comments(self):
        extracted = subprocess.run(
            ["pdftotext", "-layout", str(PDF), "-"],
            check=True, text=True, capture_output=True,
        ).stdout
        declaration_page = next(page for page in extracted.split("\f") if "Declarations" in page)
        normalized = " ".join(declaration_page.split())
        self.assertIn("[I/We] hereby declare", normalized)
        self.assertIn("[Insert Project Title]", normalized)
        self.assertIn("[available/non-available]", normalized)
        self.assertIn("[Supervisor Signature]", normalized)

    def test_methodology_equations_have_no_missing_glyphs(self):
        extracted = subprocess.run(
            ["pdftotext", "-layout", str(PDF), "-"],
            check=True, text=True, capture_output=True,
        ).stdout
        methodology_page = next(
            page for page in extracted.split("\f")
            if "Chapter 3: Numerical Methodology" in page
        )
        self.assertNotIn("?", methodology_page)
        self.assertNotIn("nabla", methodology_page)

    def test_equations_render_as_typeset_images(self):
        width, height, _ = decode_png(
            render_equation_png("Cₙ(t) = (2/L) ∫₀ᴸ η(x,t) cos(2πnx/λ) dx")
        )
        self.assertGreater(width, 500)
        self.assertGreater(height, 40)

    def test_embedded_figures_keep_print_resolution(self):
        image = ROOT.parent / "capwave-run" / "fourier-mode-evolution.png"
        width, _, _ = decode_png(image.read_bytes())
        self.assertGreaterEqual(width, 1200)


if __name__ == "__main__":
    unittest.main()
