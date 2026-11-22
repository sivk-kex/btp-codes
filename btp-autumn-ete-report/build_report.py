#!/usr/bin/env python3
"""Build CHP-400A autumn ETE report as DOCX using only Python stdlib."""

from pathlib import Path
from struct import unpack
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
PROJECTS = ROOT.parent
TEMPLATE = Path("/home/redacted/Downloads/Declarations.docx")
OUTPUT = ROOT / "output" / "Aditya_Mazumdar_CHP400A_Autumn_ETE_Report_2026.docx"

NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"'
)

FIGURES = [
    ("capwave-run/capwave-amplitude-vs-time.png",
     "Capillary-wave amplitude history compared with the Prosperetti reference solution."),
    ("capwave-run/capwave-rms-convergence.png",
     "Relative RMS error for the standing capillary-wave benchmark across grid resolutions."),
    ("capwave-run/gravity-amplitude-vs-time.png",
     "Gravity-wave amplitude at N = 128 compared with the Prosperetti reference; reduced gravity G = 50 and density ratio 10."),
    ("capwave-run/gravity-rms-convergence.png",
     "Grid-convergence behaviour for the gravity-wave benchmark."),
    ("capwave-run/pan2024-amplitude-vs-time.png",
     "Pan et al. capillary-wave conditions: a0 = 0.01, equal fluid properties, N = 64, and zero gravity."),
    ("capwave-run/janodet2024-amplitude-vs-time.png",
     "Janodet et al. capillary-wave conditions: density ratio 1000, Laplace number 300, and N = 64."),
    ("capwave-run/kayal2022-amplitude-vs-time.png",
     "Kayal et al. nonlinear axisymmetric case with epsilon = 1.8 and maximum adaptive level 9."),
    ("capwave-run/fourier-mode-evolution.png",
     "Evolution of spatial Fourier modes for initial amplitudes 0.1 and 0.5."),
    ("capwave-run/fourier-spectrum-heatmap.png",
     "Time-dependent Fourier spectrum for the two initial-amplitude cases."),
    ("capwave-run/interface-evolution.png",
     "Interface profiles showing stronger deformation in the larger-amplitude case."),
    ("capwave-run/fourier-grid-convergence.png",
     "Grid sensitivity of peak Fourier-mode magnitudes."),
    ("capwave-run/travelling-wave-amplitude.png",
     "First-mode amplitude decay in the right-travelling capillary-wave case."),
    ("capwave-run/travelling-wave-phase.png",
     "Unwrapped travelling-wave phase compared with inviscid linear theory."),
]


def run(text, *, bold=False, italic=False, size=None, font=None):
    props = []
    if font:
        props.append(f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}"/>')
    if bold:
        props.append("<w:b/><w:bCs/>")
    if italic:
        props.append("<w:i/><w:iCs/>")
    if size:
        props.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    return (
        "<w:r><w:rPr>" + "".join(props) + "</w:rPr>"
        f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'
    )


def paragraph(text="", *, style=None, align=None, before=None, after=None,
              line=None, keep_next=False, page_break_before=False,
              indent=None, hanging=None, first_line=None, runs=None):
    props = []
    if style:
        props.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        props.append(f'<w:jc w:val="{align}"/>')
    spacing = []
    if before is not None:
        spacing.append(f'w:before="{before}"')
    if after is not None:
        spacing.append(f'w:after="{after}"')
    if line is not None:
        spacing.extend((f'w:line="{line}"', 'w:lineRule="auto"'))
    if spacing:
        props.append("<w:spacing " + " ".join(spacing) + "/>")
    if keep_next:
        props.append("<w:keepNext/>")
    if page_break_before:
        props.append("<w:pageBreakBefore/>")
    ind = []
    if indent is not None:
        ind.append(f'w:left="{indent}"')
    if hanging is not None:
        ind.append(f'w:hanging="{hanging}"')
    if first_line is not None:
        ind.append(f'w:firstLine="{first_line}"')
    if ind:
        props.append("<w:ind " + " ".join(ind) + "/>")
    body = "".join(runs) if runs is not None else run(text)
    return "<w:p><w:pPr>" + "".join(props) + "</w:pPr>" + body + "</w:p>"


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def heading(text, level=1, *, new_page=False):
    return paragraph(
        text, style=f"Heading{level}", keep_next=True,
        page_break_before=new_page,
    )


def bullet(text, level=0):
    return paragraph("• " + text, indent=540 + level*360, hanging=300, after=80)


def equation(text):
    return paragraph(text, style="Equation", align="center", before=120, after=120)


def table(rows, widths, *, header=True):
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for width in widths)
    row_xml = []
    for row_index, row in enumerate(rows):
        cells = []
        for value, width in zip(row, widths):
            shading = '<w:shd w:fill="D9EAF0"/>' if header and row_index == 0 else ""
            cell_runs = [run(str(value), bold=header and row_index == 0)]
            cells.append(
                "<w:tc><w:tcPr>"
                f'<w:tcW w:w="{width}" w:type="dxa"/>{shading}'
                '<w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>'
                '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tcMar>'
                "</w:tcPr>"
                + paragraph(runs=cell_runs, after=40, line=300)
                + "</w:tc>"
            )
        row_xml.append("<w:tr>" + "".join(cells) + "</w:tr>")
    borders = (
        '<w:tblBorders><w:top w:val="single" w:sz="4" w:color="808080"/>'
        '<w:left w:val="single" w:sz="4" w:color="808080"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="808080"/>'
        '<w:right w:val="single" w:sz="4" w:color="808080"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="B0B0B0"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="B0B0B0"/></w:tblBorders>'
    )
    return (
        '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/>' + borders
        + '</w:tblPr><w:tblGrid>' + grid + '</w:tblGrid>'
        + "".join(row_xml) + "</w:tbl>" + paragraph(after=100)
    )


def png_size(path):
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not PNG: {path}")
    return unpack(">II", data[16:24])


def image_paragraph(path, rel_id, doc_id):
    width_px, height_px = png_size(path)
    max_w, max_h = 5_852_160, 4_297_680  # 6.4 x 4.7 inches
    scale = min(max_w/width_px, max_h/height_px)
    cx, cy = int(width_px*scale), int(height_px*scale)
    drawing = f'''
<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">
<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{doc_id}" name="Figure {doc_id}"/>
<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="{escape(path.name)}"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="{rel_id}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>
</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'''
    return paragraph(align="center", before=120, after=80, runs=[drawing])


def field_paragraph(instruction, fallback):
    return (
        '<w:p><w:pPr><w:spacing w:after="120"/></w:pPr>'
        '<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
        f'<w:r><w:instrText xml:space="preserve"> {escape(instruction)} </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        f'<w:r><w:t>{escape(fallback)}</w:t></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
    )


def caption(number, text):
    return paragraph(
        style="Caption", align="center", keep_next=False,
        runs=[run(f"Figure {number}. ", bold=True), run(text)],
    )


def add_figure(parts, number, image_index):
    path = PROJECTS / FIGURES[image_index][0]
    parts.append(image_paragraph(path, f"rId{100 + image_index}", number))
    parts.append(caption(number, FIGURES[image_index][1]))


def build_body():
    p = []

    # Cover
    p.extend([
        paragraph("INDIAN INSTITUTE OF TECHNOLOGY ROORKEE", align="center", before=400,
                  runs=[run("INDIAN INSTITUTE OF TECHNOLOGY ROORKEE", bold=True, size=32)]),
        paragraph("DEPARTMENT OF CHEMICAL ENGINEERING", align="center",
                  runs=[run("DEPARTMENT OF CHEMICAL ENGINEERING", bold=True, size=28)]),
        paragraph("B.TECH. PROJECT REPORT", align="center", before=900,
                  runs=[run("B.TECH. PROJECT REPORT", bold=True, size=28)]),
        paragraph("NONLINEAR EFFECTS ON CAPILLARY-GRAVITY WAVES", align="center", before=480,
                  runs=[run("NONLINEAR EFFECTS ON CAPILLARY-GRAVITY WAVES", bold=True, size=40)]),
        paragraph("Submitted in partial fulfilment of the requirements of CHP-400A", align="center", before=480,
                  runs=[run("Submitted in partial fulfilment of the requirements of CHP-400A", italic=True)]),
        paragraph("Autumn Semester 2026", align="center", after=600),
        paragraph("Submitted by", align="center", before=300, runs=[run("Submitted by", bold=True)]),
        paragraph("Aditya Mazumdar", align="center", runs=[run("Aditya Mazumdar", bold=True, size=28)]),
        paragraph("Enrollment No. 23321003 | Group PKF_AM", align="center"),
        paragraph("Under the supervision of", align="center", before=420, runs=[run("Under the supervision of", bold=True)]),
        paragraph("Prof. Palas K. Farsoiya", align="center", runs=[run("Prof. Palas K. Farsoiya", bold=True)]),
        paragraph("November 2026", align="center", before=500),
        page_break(),
    ])

    # Certificate and declarations
    p.extend([
        paragraph("SUPERVISOR CERTIFICATE", style="FrontHeading"),
        paragraph(
            "This is to certify that the B.Tech. project report entitled “Nonlinear Effects on "
            "Capillary-Gravity Waves”, submitted by Aditya Mazumdar (Enrollment No. 23321003) "
            "for CHP-400A, represents work carried out under my supervision during the Autumn "
            "Semester 2026. To the best of my knowledge, this report presents the student's "
            "project work and has not been submitted elsewhere for another academic award.",
            first_line=540,
        ),
        paragraph("Prof. Palas K. Farsoiya", before=900, runs=[run("Prof. Palas K. Farsoiya", bold=True)]),
        paragraph("Project Supervisor"),
        paragraph("Department of Chemical Engineering"),
        paragraph("Indian Institute of Technology Roorkee"),
        paragraph("Date:"),
        page_break(),
        paragraph("DECLARATIONS", style="FrontHeading"),
        heading("Candidate declaration", 2),
        paragraph(
            "I hereby declare that the report for CHP-400A titled “Nonlinear Effects on "
            "Capillary-Gravity Waves” represents my own work carried out under the supervision "
            "of Prof. Palas K. Farsoiya.", first_line=540,
        ),
        paragraph("Aditya Mazumdar | Enrollment No. 23321003", before=420),
        heading("AI-use declaration", 2),
        paragraph(
            "I hereby declare that I have disclosed all instances where AI (Artificial "
            "Intelligence) was used in creation of this report. AI use was limited to code "
            "drafting, report organization, and language editing.", first_line=540,
        ),
        paragraph("Aditya Mazumdar", before=360),
        heading("Data and code declaration", 2),
        paragraph(
            "The original code, simulation inputs, numerical outputs, and plotting scripts used "
            "in this report are available to the evaluation committee through: "
            "https://github.com/sivk-kex/btp-codes.", first_line=540,
        ),
        paragraph("Signature of Supervisor", before=360),
        paragraph("Aditya Mazumdar", before=260),
        page_break(),
        heading("Supervisor comments", 2),
        paragraph("Signature of Supervisor", before=1800),
        page_break(),
    ])

    p.extend([
        paragraph("ACKNOWLEDGEMENTS", style="FrontHeading"),
        paragraph(
            "I thank Prof. Palas K. Farsoiya for supervising this project and for guiding the "
            "selection of capillary-gravity waves as the central problem. I also acknowledge "
            "the developers of Basilisk for making the solver, benchmark cases, and numerical "
            "documentation openly available. The published analytical and numerical studies "
            "cited in this report provided reference cases for checking the implementation.",
            first_line=540,
        ),
        page_break(),
        paragraph("ABSTRACT", style="FrontHeading"),
        paragraph(
            "Capillary-gravity waves arise when surface tension and gravity restore a disturbed "
            "fluid interface. Small-amplitude waves are described well by linear theory, but "
            "larger disturbances change shape and transfer energy into additional spatial "
            "harmonics. This project develops a reproducible numerical framework for studying "
            "that transition. Two-dimensional two-phase simulations were performed in Basilisk "
            "using a centered Navier-Stokes solver and piecewise-linear volume-of-fluid interface "
            "tracking. Standard capillary and gravity wave tests were reproduced first, followed "
            "by selected published parameter cases. The main controlled comparison held fluid "
            "properties, grid, wavelength, and surface tension fixed while changing the initial "
            "standing-wave amplitude from 0.1 to 0.5. Fourier decomposition of the evolving "
            "interface showed that the smaller wave remained dominated by the fundamental mode, "
            "whereas the larger wave generated normalized peak magnitudes of 19.75%, 10.43%, "
            "and 6.91% in modes 3, 5, and 7. These strong modes changed by less than 0.24% "
            "between the two finest grids. A separate small-amplitude travelling-wave case "
            "produced monotonic rightward phase propagation at 0.90572 of the inviscid linear "
            "phase speed and retained 49.65% of its first-mode amplitude after one nominal "
            "period. Results demonstrate a working route from benchmark validation to "
            "amplitude-dependent harmonic analysis. Combined nonlinear capillary-gravity "
            "travelling waves, unequal fluid properties, and three-dimensional effects remain "
            "future work.", first_line=540,
        ),
        paragraph("Keywords: capillary waves; gravity waves; nonlinear waves; Basilisk; volume of fluid; Fourier analysis.",
                  runs=[run("Keywords: ", bold=True), run("capillary waves; gravity waves; nonlinear waves; Basilisk; volume of fluid; Fourier analysis.")]),
        page_break(),
        paragraph("CONTENTS", style="FrontHeading"),
        paragraph("Chapter 1: Introduction ........................ 11"),
        paragraph("Chapter 2: Literature Review ................... 13"),
        paragraph("Chapter 3: Numerical Methodology ............... 15"),
        paragraph("Chapter 4: Results and Discussion .............. 18"),
        paragraph("Chapter 5: Conclusions and Future Work ......... 28"),
        paragraph("Data Availability and AI-Use Disclosure ........ 29"),
        paragraph("References ..................................... 30"),
        paragraph("Appendix A: Reproducibility .................... 31"),
        paragraph("Appendix B: Project File Inventory ............. 33"),
        page_break(),
        paragraph("LIST OF FIGURES", style="FrontHeading"),
    ])
    for index, (_, title) in enumerate(FIGURES, 1):
        p.append(paragraph(f"Figure {index}. {title}", after=70))
    p.extend([
        page_break(),
        paragraph("LIST OF TABLES", style="FrontHeading"),
        paragraph("Table 1. Main physical and numerical quantities."),
        paragraph("Table 2. Gravity-wave relative RMS errors."),
        paragraph("Table 3. Peak normalized Fourier modes."),
        paragraph("Table 4. Travelling-wave diagnostics."),
        page_break(),
        paragraph("NOMENCLATURE", style="FrontHeading"),
        table([
            ("Symbol", "Meaning", "Units"),
            ("a0", "Initial interface amplitude", "m or nondimensional"),
            ("A_n", "Magnitude of spatial Fourier mode n", "m or nondimensional"),
            ("Bo", "Bond number, Δρgλ²/σ", "-"),
            ("f", "Volume fraction of reference fluid", "-"),
            ("g", "Gravitational acceleration", "m s⁻²"),
            ("k", "Wavenumber, 2π/λ", "m⁻¹"),
            ("La", "Laplace number, ρσλ/μ²", "-"),
            ("N", "Grid cells along one domain direction", "-"),
            ("p", "Pressure", "Pa"),
            ("t", "Time", "s"),
            ("u", "Velocity vector", "m s⁻¹"),
            ("η", "Interface displacement", "m"),
            ("λ", "Wavelength", "m"),
            ("μ", "Dynamic viscosity", "Pa s"),
            ("ρ", "Density", "kg m⁻³"),
            ("σ", "Surface tension", "N m⁻¹"),
            ("τ", "Nondimensional time, ω0t", "-"),
            ("ω", "Angular frequency", "s⁻¹"),
        ], [1300, 5000, 1700]),
    ])

    # Chapter 1
    p.extend([
        heading("CHAPTER 1: INTRODUCTION", 1, new_page=True),
        heading("1.1 Background", 2),
        paragraph(
            "A disturbance at an interface between two fluids creates curvature and changes the "
            "local pressure. Surface tension resists that curvature, while gravity resists "
            "vertical displacement when the fluids have different densities. Their combined "
            "action produces capillary-gravity waves. Surface tension dominates short waves; "
            "gravity becomes more important at longer wavelengths. Viscosity removes mechanical "
            "energy and causes wave amplitude to decay with time.", first_line=540,
        ),
        paragraph(
            "Linear wave theory assumes that interface displacement and slope remain small. "
            "Under that assumption, each sinusoidal mode evolves independently. Larger initial "
            "amplitudes break this simplification. Wave crests and troughs become asymmetric, "
            "curvature changes rapidly, and higher spatial harmonics appear. Measuring these "
            "harmonics provides a direct way to quantify departure from a sinusoidal shape.",
            first_line=540,
        ),
        heading("1.2 Engineering relevance", 2),
        paragraph(
            "Interfacial waves occur in sprays, atomization, coating flows, falling liquid films, "
            "and gas-liquid contactors. Wave shape affects local film thickness, interfacial area, "
            "and the conditions leading to breakup. The present work does not model a complete "
            "industrial device. It isolates a controlled wave so that numerical accuracy and "
            "nonlinear deformation can be understood before realistic geometries are added.",
            first_line=540,
        ),
        heading("1.3 Problem statement", 2),
        paragraph(
            "Classical small-amplitude benchmarks are useful for checking a solver, but they do "
            "not show how a finite-amplitude wave changes shape. Strongly nonlinear studies often "
            "focus on localized dimples, focusing, or jet formation. This project examines the "
            "intermediate transition under one numerical framework: fluid properties and solver "
            "settings remain fixed while initial amplitude changes, and Fourier modes measure the "
            "resulting deformation.", first_line=540,
        ),
        heading("1.4 Aim and scope", 2),
        paragraph(
            "The project aims to build and validate a Basilisk workflow for two-phase interfacial "
            "waves, then use it to quantify amplitude-driven nonlinear effects. Autumn work covers "
            "two-dimensional standing-wave benchmarks, initial-amplitude comparison, Fourier and "
            "grid-sensitivity analysis, and one linear travelling-wave extension. Current results "
            "do not constitute a full nonlinear capillary-gravity travelling-wave study.",
            first_line=540,
        ),
        heading("1.5 Report organization", 2),
        paragraph(
            "Chapter 2 reviews linear theory, numerical interface tracking, and nonlinear wave "
            "studies before stating the research gap and objectives. Chapter 3 gives governing "
            "equations, simulation conditions, and diagnostics. Chapter 4 presents validation, "
            "harmonic, grid, and travelling-wave results. Chapter 5 summarizes the autumn work "
            "and defines spring-semester tasks.", first_line=540,
        ),
    ])

    # Chapter 2
    p.extend([
        heading("CHAPTER 2: LITERATURE REVIEW", 1, new_page=True),
        heading("2.1 Linear viscous interfacial waves", 2),
        paragraph(
            "Prosperetti formulated the initial-value problem for motion of two superposed viscous "
            "fluids [1]. The solution remains a standard reference for small-amplitude capillary "
            "waves because it includes transient viscous effects. Modern numerical methods compare "
            "predicted amplitude histories against this reference to test surface-tension forces, "
            "curvature calculation, and interface advection.", first_line=540,
        ),
        paragraph(
            "For an inviscid wave of wavenumber k at an interface between deep fluids, the linear "
            "dispersion relation combines gravitational and capillary restoring forces. Finite "
            "depth modifies it through a hyperbolic-tangent factor. Viscosity adds damping and can "
            "shift transient behaviour away from the inviscid prediction.", first_line=540,
        ),
        equation("ω² = [(Δρ g k + σ k³)/(ρ₁ + ρ₂)] tanh(kh)"),
        heading("2.2 Numerical tracking of fluid interfaces", 2),
        paragraph(
            "Volume-of-fluid methods represent each cell by a fluid fraction and reconstruct the "
            "interface in cells containing both fluids. Popinet presented an adaptive solver for "
            "surface-tension-driven interfacial flows with balanced force and height-function "
            "curvature treatments [2]. Basilisk provides this framework together with standard "
            "capillary and gravity wave tests [6,7].", first_line=540,
        ),
        paragraph(
            "Pan et al. used a small-amplitude capillary wave to assess an edge-based interface "
            "tracking method against analytical theory and PLIC-VOF results [3]. Janodet et al. "
            "examined implicit surface-tension treatment for flows with large density ratios [5]. "
            "Both studies demonstrate why a damped capillary wave remains a demanding numerical "
            "test even though its geometry is simple.", first_line=540,
        ),
        heading("2.3 Nonlinear capillary waves", 2),
        paragraph(
            "Nonlinearity couples spatial modes that remain independent in linear theory. Kayal, "
            "Basak, and Dasgupta studied dimple and jet formation from a collapsing capillary-wave "
            "trough [4]. Their work connects weakly nonlinear theory with strongly nonlinear "
            "focusing and shows that energy spreads across additional modes as deformation grows. "
            "That regime is more extreme and geometrically different from the periodic standing "
            "wave used in the main controlled comparison here.", first_line=540,
        ),
        heading("2.4 Research gap", 2),
        paragraph(
            "Existing studies establish small-amplitude linear benchmarks and investigate strongly "
            "nonlinear focusing or jetting. A useful intermediate question is how a smooth periodic "
            "wave departs from its original sinusoidal shape as only the starting amplitude rises. "
            "This project addresses that controlled transition with one two-fluid VOF setup, "
            "quantitative Fourier diagnostics, and grid-sensitivity checks. It also tests whether "
            "the workflow can move from standing to travelling waves before gravity and unequal "
            "fluid properties are combined in later work.", first_line=540,
        ),
        heading("2.5 Objectives", 2),
        bullet("Reproduce standard capillary and gravity wave benchmarks in Basilisk."),
        bullet("Check selected literature parameter cases before changing wave amplitude."),
        bullet("Compare standing waves with initial amplitudes 0.1 and 0.5 under otherwise identical conditions."),
        bullet("Measure spatial harmonics and test their sensitivity to grid resolution."),
        bullet("Initialize and diagnose a right-travelling capillary wave as an extension of the standing-wave workflow."),
        bullet("Define a reproducible route toward nonlinear capillary-gravity travelling-wave studies."),
    ])

    # Chapter 3
    p.extend([
        heading("CHAPTER 3: NUMERICAL METHODOLOGY", 1, new_page=True),
        heading("3.1 Governing equations", 2),
        paragraph(
            "Each fluid is treated as incompressible and Newtonian. A single velocity field is "
            "solved over the domain, while density and viscosity depend on volume fraction f. "
            "Surface tension acts at the reconstructed interface.", first_line=540,
        ),
        equation("∇ · u = 0"),
        equation("ρ(∂u/∂t + u · ∇u) = −∇p + ∇ · [μ(∇u + ∇uᵀ)] + ρg + σκδₛn"),
        equation("∂f/∂t + u · ∇f = 0"),
        paragraph(
            "Here n is interface normal, κ is curvature, and δs restricts capillary force to "
            "the interface. Mixture properties follow f through ρ = fρ1 + (1-f)ρ2 and the "
            "corresponding viscosity interpolation.", first_line=540,
        ),
        heading("3.2 Numerical method", 2),
        paragraph(
            "Simulations use Basilisk's centered finite-volume Navier-Stokes solver on a Cartesian "
            "multigrid. PLIC-VOF reconstruction tracks the interface, height functions estimate "
            "curvature, and the balanced surface-tension formulation limits parasitic currents. "
            "Controlled standing, gravity, and travelling cases use fixed grids so changes "
            "across resolutions can be compared directly. The Kayal literature reproduction "
            "instead uses an adaptive axisymmetric quadtree, matching that problem's geometry.",
            first_line=540,
        ),
        heading("3.3 Physical and numerical parameters", 2),
        table([
            ("Quantity", "Standing/Fourier cases", "Travelling case"),
            ("Domain", "2 × 2", "2 × 2"),
            ("Wavelength λ", "1", "1"),
            ("Surface tension σ", "1", "1"),
            ("Densities", "ρ1 = ρ2 = 1", "ρ1 = ρ2 = 1"),
            ("Viscosities", "μ1 = μ2 = 0.0182571749236", "same"),
            ("Gravity", "0", "0"),
            ("Primary grid", "N = 128", "N = 128"),
            ("Cells per wavelength", "64", "64"),
            ("Initial amplitude", "0.1 and 0.5", "0.01"),
            ("Maximum CFL", "0.5", "solver controlled"),
        ], [2400, 3300, 2300]),
        paragraph("Table 1. Main physical and numerical quantities used in the controlled studies.", style="Caption", align="center"),
        heading("3.4 Initial and boundary conditions", 2),
        paragraph(
            "Standing-wave cases begin from a stationary cosine interface, η(x,0) = a0 cos(2πx), "
            "with zero velocity and no-normal-flow conditions on all four boundaries. Their 2 × 2 "
            "domain contains two wavelengths. The travelling-wave case uses periodic horizontal "
            "boundaries and no penetration at the top and bottom. It uses the same interface shape "
            "at a0 = 0.01 but adds a phase-matched linear velocity potential so the crest moves to "
            "the right.", first_line=540,
        ),
        equation("η(x,t) = a0 cos(kx − ωt)"),
        heading("3.5 Amplitude and Fourier diagnostics", 2),
        paragraph(
            "Amplitude history measures oscillation and viscous decay. To describe shape rather "
            "than only height, the interface is decomposed into spatial Fourier modes. For each "
            "harmonic n, cosine and sine projections are evaluated from the vertically integrated "
            "VOF field.", first_line=540,
        ),
        equation("Cₙ(t) = (2/L) ∫₀ᴸ η(x,t) cos(2πnx/λ) dx"),
        equation("Sₙ(t) = −(2/L) ∫₀ᴸ η(x,t) sin(2πnx/λ) dx"),
        equation("Aₙ(t) = √[Cₙ²(t) + Sₙ²(t)]"),
        paragraph(
            "Here λ = 1 is wavelength and L = 2 is domain length. The minus sign in S_n records "
            "the signed convention used by the vertically integrated VOF implementation; it does "
            "not affect magnitude A_n. Magnitudes are divided by a0 so cases with different "
            "starting amplitudes can be compared. In the travelling-wave case, phase is obtained from the first-mode cosine "
            "and sine coefficients and unwrapped through time. A positive, increasing phase marks "
            "rightward propagation.", first_line=540,
        ),
        heading("3.6 Grid and validation procedure", 2),
        paragraph(
            "Benchmark calculations use successive grid refinements and compare amplitude histories "
            "with reference data. Fourier cases are repeated at 32, 64, and 128 cells per wavelength. "
            "A mode is interpreted as resolved only when its magnitude changes little between the "
            "two finest grids. Large relative change in a very small mode is treated as numerical "
            "residue rather than physical harmonic generation.", first_line=540,
        ),
        heading("3.7 Reproducibility", 2),
        paragraph(
            "Source files, input parameters, raw numerical outputs, plotting scripts, and tests are "
            "kept together in the project workspace. Main controlled studies can be regenerated "
            "from Appendix A and the named reproduction guides. Tests check compilation, input validation, output "
            "structure, Fourier initialization, phase propagation, and plot generation.",
            first_line=540,
        ),
    ])

    # Chapter 4
    p.extend([
        heading("CHAPTER 4: RESULTS AND DISCUSSION", 1, new_page=True),
        heading("4.1 Small-amplitude capillary benchmark", 2),
        paragraph(
            "The standard capillary-wave test reproduces damped oscillation about the equilibrium "
            "interface. Amplitude history follows the Prosperetti reference more closely as the "
            "grid is refined. The convergence plot confirms that the numerical setup captures the "
            "small-amplitude surface-tension response before finite-amplitude cases are considered.",
            first_line=540,
        ),
    ])
    add_figure(p, 1, 0)
    add_figure(p, 2, 1)
    p.extend([
        heading("4.2 Gravity-wave benchmark", 2),
        paragraph(
            "The reduced-gravity benchmark was run at 8, 16, 32, and 64 cells per wavelength. "
            "Relative RMS errors were 0.126713, 0.031758, 0.00807759, and 0.00455815. The first "
            "two refinement steps give observed orders of about 2.00 and 1.98. The finest step "
            "falls to about 0.83, consistent with visible error flattening rather than continued "
            "ideal second-order reduction.", first_line=540,
        ),
    ])
    add_figure(p, 3, 2)
    add_figure(p, 4, 3)
    p.extend([
        table([
            ("Cells per wavelength", "Relative RMS error"),
            ("8", "0.126713"),
            ("16", "0.031758"),
            ("32", "0.00807759"),
            ("64", "0.00455815"),
        ], [3600, 3600]),
        paragraph("Table 2. Gravity-wave relative RMS errors.", style="Caption", align="center"),
        heading("4.3 Selected literature-parameter cases", 2),
        paragraph(
            "Three additional cases broadened the setup checks. Pan et al. supplied a modern "
            "small-amplitude capillary-wave comparison, Janodet et al. supplied a large-density-"
            "ratio case, and Kayal et al. supplied a nonlinear wave case. These reproductions test "
            "different conditions, but they are not used to claim complete validation of every "
            "physical regime.", first_line=540,
        ),
    ])
    add_figure(p, 5, 4)
    add_figure(p, 6, 5)
    add_figure(p, 7, 6)
    p.extend([
        heading("4.4 Effect of initial amplitude", 2),
        paragraph(
            "The controlled nonlinear study changed only initial amplitude. At a0 = 0.1, the "
            "fundamental mode remains dominant and the interface stays close to sinusoidal. At "
            "a0 = 0.5, the profile becomes steeper and higher odd harmonics grow. Even modes remain "
            "near numerical zero because the equal-fluid, zero-gravity configuration and cosine "
            "initial condition preserve half-wave symmetry.", first_line=540,
        ),
        table([
            ("Initial amplitude", "Mode 3 peak", "Mode 5 peak", "Mode 7 peak"),
            ("0.1", "2.09%", "0.136%", "0.0334%"),
            ("0.5", "19.75%", "10.43%", "6.91%"),
        ], [2200, 1900, 1900, 1900]),
        paragraph("Table 3. Peak Fourier magnitudes normalized by initial amplitude.", style="Caption", align="center"),
    ])
    add_figure(p, 8, 7)
    add_figure(p, 9, 8)
    add_figure(p, 10, 9)
    p.extend([
        paragraph(
            "Mode 3 increases from 2.09% to 19.75% when starting amplitude rises from 0.1 to 0.5. "
            "Modes 5 and 7 also reach 10.43% and 6.91% in the larger case. This transfer from the "
            "fundamental to higher odd modes quantifies nonlinear shape change; it is more specific "
            "than judging nonlinearity from a single crest height.", first_line=540,
        ),
        heading("4.5 Grid sensitivity of harmonic peaks", 2),
        paragraph(
            "For a0 = 0.5, modes 1, 3, 5, and 7 change by 0.090%, 0.083%, 0.233%, and 0.059% "
            "between the two finest grids. Every strong mode therefore changes by less than 0.24%. "
            "For a0 = 0.1, mode 7 is only 0.0334% of a0 on the main grid and changes by 175% under "
            "refinement. Its absolute value is tiny and decreases on the finer grid, so it is "
            "reported as unresolved numerical residue rather than a physical result.", first_line=540,
        ),
    ])
    add_figure(p, 11, 10)
    p.extend([
        heading("4.6 Travelling-wave extension", 2),
        paragraph(
            "A separate pure-capillary travelling-wave validation used a0 = 0.01 and N = 128. "
            "The first-mode phase increased throughout 126 stored samples, confirming rightward "
            "propagation instead of standing oscillation. Linear regression gave a phase rate of "
            "0.90572 relative to inviscid linear theory. First-mode amplitude decreased from "
            "0.00998795 to 0.00495856, leaving 49.65% of its initial value after one nominal period.",
            first_line=540,
        ),
        table([
            ("Diagnostic", "Value"),
            ("Stored samples", "126"),
            ("Final nondimensional time", "6.255"),
            ("Final unwrapped phase", "5.70890 rad"),
            ("Measured/theoretical phase speed", "0.90572"),
            ("Final/initial first-mode amplitude", "49.65%"),
        ], [4200, 3000]),
        paragraph("Table 4. Travelling-wave diagnostics.", style="Caption", align="center"),
    ])
    add_figure(p, 12, 11)
    add_figure(p, 13, 12)
    p.extend([
        paragraph(
            "The speed deficit and amplitude decay cannot be assigned to one mechanism from this "
            "single run. Both viscosity and discretized initialization contribute. The result "
            "therefore validates travelling behaviour only; it does not establish an exact "
            "inviscid solution or a nonlinear capillary-gravity result.", first_line=540,
        ),
        heading("4.7 Current limitations", 2),
        bullet("Main amplitude study uses equal densities and viscosities with zero gravity."),
        bullet("Travelling-wave study covers one small initial amplitude and one primary resolution."),
        bullet("Physical viscous damping has not been separated from numerical dissipation."),
        bullet("Two-dimensional periodic geometry does not represent three-dimensional focusing or breakup."),
        bullet("Intermediate amplitudes between 0.1 and 0.5 have not yet been mapped."),
    ])

    # Chapter 5 and back matter
    p.extend([
        heading("CHAPTER 5: CONCLUSIONS AND FUTURE WORK", 1, new_page=True),
        heading("5.1 Conclusions", 2),
        paragraph(
            "Autumn work established a reproducible Basilisk workflow for standing and travelling "
            "interfacial waves. Standard capillary and gravity tests were reproduced before the "
            "initial amplitude was increased. This sequence separated setup validation from the "
            "main nonlinear comparison.", first_line=540,
        ),
        paragraph(
            "The controlled standing-wave study showed that a0 = 0.5 produces much stronger odd "
            "harmonics than a0 = 0.1. Mode 3 reached 19.75% of initial amplitude, while modes 5 "
            "and 7 reached 10.43% and 6.91%. Their variation below 0.24% between the two finest "
            "grids supports interpretation as resolved nonlinear deformation. The travelling-wave "
            "case added a working phase-based diagnostic and confirmed rightward propagation.",
            first_line=540,
        ),
        heading("5.2 Spring-semester work", 2),
        bullet("Run intermediate initial amplitudes to locate gradual onset of strong higher harmonics."),
        bullet("Add gravity to the finite-amplitude standing and travelling cases through a controlled comparison."),
        bullet("Introduce realistic density and viscosity ratios after each simpler case is verified."),
        bullet("Repeat travelling-wave calculations at multiple resolutions to separate numerical error from physical damping."),
        bullet("Study counter-propagating waves and interactions only after single-wave validation."),
        bullet("Use HPC resources for fine-grid sweeps or three-dimensional cases if scope and access permit."),
        heading("DATA AVAILABILITY", 1, new_page=True),
        paragraph(
            "Code, simulation inputs, raw numerical output, plotting scripts, and tests are "
            "archived for committee access at https://github.com/sivk-kex/btp-codes. Main working "
            "files currently reside "
            "in the `capwave-run` and `gravity-run` project directories.", first_line=540,
        ),
        heading("AI-USE DISCLOSURE", 1),
        paragraph(
            "I hereby declare that I have disclosed all instances where AI (Artificial "
            "Intelligence) was used in creation of this report. AI use was limited to code "
            "drafting, report organization, and language editing.", first_line=540,
        ),
        heading("REFERENCES", 1, new_page=True),
        paragraph("[1] Prosperetti, A. Motion of Two Superposed Viscous Fluids. Phys. Fluids 1981, 24 (7), 1217–1223. https://doi.org/10.1063/1.863522."),
        paragraph("[2] Popinet, S. An Accurate Adaptive Solver for Surface-Tension-Driven Interfacial Flows. J. Comput. Phys. 2009, 228 (16), 5838–5866. https://doi.org/10.1016/j.jcp.2009.04.042."),
        paragraph("[3] Pan, J.; et al. An Edge-Based Interface Tracking (EBIT) Method for Multiphase-Flow Simulation with Surface Tension. J. Comput. Phys. 2024, 508, 113016. https://doi.org/10.1016/j.jcp.2024.113016."),
        paragraph("[4] Kayal, L.; Basak, S.; Dasgupta, R. Dimples, Jets and Self-Similarity in Nonlinear Capillary Waves. J. Fluid Mech. 2022, 951, A26. https://doi.org/10.1017/jfm.2022.854."),
        paragraph("[5] Janodet, R.; van Wachem, B.; Denner, F. A Fully-Coupled Algorithm with Implicit Surface Tension Treatment for Interfacial Flows with Large Density Ratios. J. Comput. Phys. 2025, 520, 113520. https://doi.org/10.1016/j.jcp.2024.113520."),
        paragraph("[6] Basilisk. Capillary Wave Test and Source Code. https://basilisk.fr/src/test/capwave.c (accessed 2026-11-22)."),
        paragraph("[7] Basilisk. Gravity Wave Test and Source Code. https://basilisk.fr/src/test/gravity.c (accessed 2026-11-22)."),
        heading("APPENDIX A: REPRODUCIBILITY", 1, new_page=True),
        paragraph("Working directory for capillary cases: /home/redacted/Desktop/projects/capwave-run", style="Code"),
        heading("A.1 Standard capillary benchmark", 2),
        paragraph("../basilisk/src/qcc -O2 -Wall capwave.c -o capwave -lm", style="Code"),
        paragraph("./capwave > capwave.out 2> capwave.log", style="Code"),
        paragraph("python3 plot_capwave_validation.py", style="Code"),
        heading("A.2 Standard gravity benchmark", 2),
        paragraph("cd /home/redacted/Desktop/projects", style="Code"),
        paragraph("./basilisk/src/qcc -O2 -Wall basilisk/src/test/gravity.c -o gravity-run/gravity -lm", style="Code"),
        paragraph("cd gravity-run && ./gravity > gravity.facets 2> gravity.log", style="Code"),
        paragraph("python3 plot_gravity.py", style="Code"),
        heading("A.3 Fourier standing-wave study", 2),
        paragraph("../basilisk/src/qcc -O2 -Wall nonlinear_fourier.c -o nonlinear_fourier -lm", style="Code"),
        paragraph("./nonlinear_fourier 0.1 fourier-a0-0.1.dat profiles-a0-0.1.dat 128", style="Code"),
        paragraph("./nonlinear_fourier 0.5 fourier-a0-0.5.dat profiles-a0-0.5.dat 128", style="Code"),
        paragraph("./nonlinear_fourier 0.5 fourier-a0-0.5-N64.dat profiles-a0-0.5-N64.dat 64", style="Code"),
        paragraph("./nonlinear_fourier 0.5 fourier-a0-0.5-N256.dat profiles-a0-0.5-N256.dat 256", style="Code"),
        paragraph("python3 plot_nonlinear_fourier.py", style="Code"),
        heading("A.4 Literature-parameter cases", 2),
        paragraph("../basilisk/src/qcc -O2 -Wall pan2024_capwave.c -o pan2024_capwave -lm", style="Code"),
        paragraph("./pan2024_capwave > pan2024-wave.dat 2> pan2024.log", style="Code"),
        paragraph("../basilisk/src/qcc -O2 -Wall janodet2024_capwave.c -o janodet2024_capwave -lm", style="Code"),
        paragraph("./janodet2024_capwave > janodet2024-wave.dat 2> janodet2024.log", style="Code"),
        paragraph("../basilisk/src/qcc -O2 -Wall kayal2022_wave.c -o kayal2022_wave -lm", style="Code"),
        paragraph("./kayal2022_wave 9 > kayal2022-wave.dat 2> kayal2022.log", style="Code"),
        paragraph("See KAYAL2022_REPRODUCE.md for model assumptions and validation landmarks.", first_line=540),
        heading("A.5 Travelling-wave study", 2),
        paragraph("../basilisk/src/qcc -O2 -Wall travelling_wave.c -o travelling_wave -lm", style="Code"),
        paragraph("./travelling_wave 0.01 travelling-wave.dat 128", style="Code"),
        paragraph("python3 plot_travelling_wave.py", style="Code"),
        heading("A.6 Verification", 2),
        paragraph("python3 -m unittest discover -v", style="Code"),
        heading("APPENDIX B: PROJECT FILE INVENTORY", 1, new_page=True),
        table([
            ("File or directory", "Purpose"),
            ("capwave-run/capwave.c", "Classical standing capillary-wave benchmark"),
            ("gravity-run/", "Gravity-wave reproduction and convergence output"),
            ("capwave-run/nonlinear_fourier.c", "Finite-amplitude standing-wave and Fourier solver"),
            ("capwave-run/travelling_wave.c", "Right-travelling capillary-wave solver"),
            ("capwave-run/*.dat", "Raw amplitude, Fourier, phase, and interface data"),
            ("capwave-run/plot_*.py", "Data-driven plotting scripts"),
            ("capwave-run/test_*.py", "Compilation, physics, output, and plotting checks"),
        ], [3300, 4700]),
    ])

    section = (
        '<w:sectPr><w:footerReference w:type="default" r:id="rId90"/>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
        'w:header="720" w:footer="720" w:gutter="0"/>'
        '<w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr>'
    )
    return "<w:body>" + "".join(p) + section + "</w:body>"


def styles_xml():
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {NS}>
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
<w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="360" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>
<w:pPr><w:spacing w:after="160" w:line="360" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="240"/><w:outlineLvl w:val="0"/></w:pPr>
<w:rPr><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="220" w:after="120"/><w:outlineLvl w:val="1"/></w:pPr>
<w:rPr><w:b/><w:bCs/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:keepNext/><w:spacing w:before="180" w:after="100"/><w:outlineLvl w:val="2"/></w:pPr>
<w:rPr><w:b/><w:bCs/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="FrontHeading"><w:name w:val="Front Heading"/><w:basedOn w:val="Normal"/>
<w:pPr><w:jc w:val="center"/><w:spacing w:before="240" w:after="420"/><w:keepNext/></w:pPr>
<w:rPr><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="caption"/><w:basedOn w:val="Normal"/>
<w:pPr><w:jc w:val="center"/><w:spacing w:after="220" w:line="300" w:lineRule="auto"/><w:keepNext/></w:pPr>
<w:rPr><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Equation"><w:name w:val="Equation"/><w:basedOn w:val="Normal"/>
<w:pPr><w:jc w:val="center"/><w:spacing w:before="120" w:after="120"/><w:keepLines/></w:pPr>
<w:rPr><w:i/><w:iCs/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/><w:basedOn w:val="Normal"/>
<w:pPr><w:spacing w:after="80" w:line="240" w:lineRule="auto"/><w:ind w:left="360"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/><w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr></w:style>
</w:styles>'''


def settings_xml():
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings {NS}><w:zoom w:percent="100"/><w:mirrorMargins/><w:updateFields w:val="true"/>
<w:defaultTabStop w:val="720"/><w:compat/></w:settings>'''


def footer_xml():
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr {NS}><w:p><w:pPr><w:jc w:val="center"/></w:pPr>
<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText> PAGE </w:instrText></w:r>
<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r>
<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>'''


def relationships_xml():
    relationships = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>',
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/webSettings" Target="webSettings.xml"/>',
        '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>',
        '<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>',
        '<Relationship Id="rId90" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>',
    ]
    for index, _ in enumerate(FIGURES):
        relationships.append(
            f'<Relationship Id="rId{100 + index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            f'Target="media/report_figure_{index + 1:02d}.png"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(relationships) + "</Relationships>"
    )


def patch_content_types(xml):
    if 'Extension="png"' not in xml:
        xml = xml.replace(
            "</Types>",
            '<Default Extension="png" ContentType="image/png"/></Types>',
        )
    if 'PartName="/word/footer1.xml"' not in xml:
        xml = xml.replace(
            "</Types>",
            '<Override PartName="/word/footer1.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>',
        )
    return xml


def build_report():
    with ZipFile(TEMPLATE) as source:
        files = {name: source.read(name) for name in source.namelist()}

    document = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document {NS}>' + build_body() + "</w:document>"
    )
    files["word/document.xml"] = document.encode("utf-8")
    files["word/styles.xml"] = styles_xml().encode("utf-8")
    files["word/settings.xml"] = settings_xml().encode("utf-8")
    files["word/footer1.xml"] = footer_xml().encode("utf-8")
    files["word/_rels/document.xml.rels"] = relationships_xml().encode("utf-8")
    files["[Content_Types].xml"] = patch_content_types(
        files["[Content_Types].xml"].decode("utf-8")
    ).encode("utf-8")

    for index, (relative, _) in enumerate(FIGURES, 1):
        files[f"word/media/report_figure_{index:02d}.png"] = (PROJECTS / relative).read_bytes()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as target:
        for name, data in files.items():
            target.writestr(name, data)

    with ZipFile(OUTPUT) as check:
        if check.testzip() is not None:
            raise RuntimeError("invalid DOCX ZIP package")
        if len([name for name in check.namelist() if name.startswith("word/media/")]) != len(FIGURES):
            raise RuntimeError("figure embedding incomplete")
    return OUTPUT


if __name__ == "__main__":
    print(build_report())
