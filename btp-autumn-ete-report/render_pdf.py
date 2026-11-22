#!/usr/bin/env python3
"""Render report DOCX to A4 PDF without LibreOffice Writer."""

from pathlib import Path
import re
import subprocess
import tempfile
import textwrap
import xml.etree.ElementTree as ET
from struct import unpack
from zipfile import ZipFile
import zlib

from build_report import OUTPUT as DOCX, build_report


ROOT = Path(__file__).resolve().parent
PDF = ROOT / "output" / "Aditya_Mazumdar_CHP400A_Autumn_ETE_Report_2026.pdf"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
A4_W, A4_H = 595.276, 841.89
LEFT, RIGHT, TOP, BOTTOM = 72., 72., 72., 62.
CONTENT_W = A4_W - LEFT - RIGHT


TRANSLATE = str.maketrans({
    "–": "-", "—": "-", "−": "-", "“": '"', "”": '"', "’": "'",
    "×": "x", "·": ".", "•": "-", "π": "pi ", "ω": "omega ",
    "ρ": "rho ", "σ": "sigma ", "η": "eta ", "λ": "lambda ", "μ": "mu ",
    "τ": "tau ", "κ": "kappa ", "Δ": "Delta ", "∇": "grad ", "∂": "partial ",
    "δ": "delta ", "₀": "_0", "₁": "_1", "₂": "_2", "₃": "_3", "ₙ": "_n",
    "ₛ": "_s", "ᵀ": "^T", "ᴸ": "^L", "¹": "^1", "²": "^2", "³": "^3", "⁻": "-", "√": "sqrt",
    "∫": "integral", "∞": "infinity", "≤": "<=", "≥": ">=", "≈": "~",
})

EQN_SOURCE = {
    "ω² = [(Δρ g k + σ k³)/(ρ₁ + ρ₂)] tanh(kh)":
        "omega sup 2 = left [ { Delta rho g k + sigma k sup 3 } over "
        "{ rho sub 1 + rho sub 2 } right ] roman tanh ( k h )",
    "∇ · u = 0": '"\\[gr]" cdot u = 0',
    "ρ(∂u/∂t + u · ∇u) = −∇p + ∇ · [μ(∇u + ∇uᵀ)] + ρg + σκδₛn":
        'rho left ( { "\\[pd]" u over "\\[pd]" t } + u cdot "\\[gr]" u right ) '
        '= - "\\[gr]" p + "\\[gr]" cdot left [ mu left ( "\\[gr]" u + '
        '"\\[gr]" u sup T right ) right ] + rho g + sigma kappa delta sub s n',
    "∂f/∂t + u · ∇f = 0":
        '{ "\\[pd]" f over "\\[pd]" t } + u cdot "\\[gr]" f = 0',
    "η(x,t) = a0 cos(kx − ωt)":
        "eta ( x , t ) = a sub 0 roman cos ( k x - omega t )",
    "Cₙ(t) = (2/L) ∫₀ᴸ η(x,t) cos(2πnx/λ) dx":
        "C sub n ( t ) = { 2 over L } int sub 0 sup L eta ( x , t ) "
        "roman cos left ( { 2 pi n x over lambda } right ) d x",
    "Sₙ(t) = −(2/L) ∫₀ᴸ η(x,t) sin(2πnx/λ) dx":
        "S sub n ( t ) = - { 2 over L } int sub 0 sup L eta ( x , t ) "
        "roman sin left ( { 2 pi n x over lambda } right ) d x",
    "Aₙ(t) = √[Cₙ²(t) + Sₙ²(t)]":
        "A sub n ( t ) = sqrt { C sub n sup 2 ( t ) + S sub n sup 2 ( t ) }",
}


def ascii_text(value):
    value = (value.replace("δₛ", "delta_s ").replace("uᵀ", "u^T")
             .replace("⁻¹", "^-1").replace("⁻²", "^-2").replace("⁻³", "^-3"))
    value = value.translate(TRANSLATE)
    value = re.sub(r"[ \t]+", " ", value)
    return value.encode("ascii", "replace").decode("ascii")


def ps_escape(value):
    return ascii_text(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def paeth(a, b, c):
    estimate = a + b - c
    distances = abs(estimate-a), abs(estimate-b), abs(estimate-c)
    return (a, b, c)[distances.index(min(distances))]


def decode_png(data, max_width=1400, max_height=900):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("unsupported image format")
    position, chunks = 8, {}
    idat = []
    while position < len(data):
        length = unpack(">I", data[position:position+4])[0]
        kind = data[position+4:position+8]
        payload = data[position+8:position+8+length]
        position += length + 12
        if kind == b"IHDR":
            width, height, depth, color_type, _, _, interlace = unpack(">IIBBBBB", payload)
            chunks["ihdr"] = width, height, depth, color_type, interlace
        elif kind == b"IDAT":
            idat.append(payload)
        elif kind == b"IEND":
            break
    width, height, depth, color_type, interlace = chunks["ihdr"]
    if depth != 8 or interlace != 0 or color_type not in (0, 2, 6):
        raise ValueError(f"unsupported PNG depth/type/interlace: {depth}/{color_type}/{interlace}")
    channels = {0: 1, 2: 3, 6: 4}[color_type]
    stride = width*channels
    raw = zlib.decompress(b"".join(idat))
    rows, offset, previous = [], 0, bytearray(stride)
    for _ in range(height):
        filter_type = raw[offset]
        source = raw[offset+1:offset+1+stride]
        offset += stride + 1
        row = bytearray(stride)
        for index, byte in enumerate(source):
            left = row[index-channels] if index >= channels else 0
            up = previous[index]
            upper_left = previous[index-channels] if index >= channels else 0
            if filter_type == 0:
                value = byte
            elif filter_type == 1:
                value = byte + left
            elif filter_type == 2:
                value = byte + up
            elif filter_type == 3:
                value = byte + ((left + up)//2)
            elif filter_type == 4:
                value = byte + paeth(left, up, upper_left)
            else:
                raise ValueError(f"unknown PNG filter: {filter_type}")
            row[index] = value & 255
        rows.append(row)
        previous = row

    scale = min(1., max_width/width, max_height/height)
    out_w, out_h = max(1, int(width*scale)), max(1, int(height*scale))
    rgb = bytearray()
    for out_y in range(out_h):
        row = rows[min(height-1, int(out_y/scale))]
        for out_x in range(out_w):
            source_x = min(width-1, int(out_x/scale))*channels
            if color_type == 0:
                rgb.extend((row[source_x],)*3)
            else:
                rgb.extend(row[source_x:source_x+3])
    return out_w, out_h, bytes(rgb)


def render_equation_png(text):
    if text not in EQN_SOURCE:
        raise ValueError(f"no typesetting rule for equation: {text}")
    source = f".ps 14\n.EQ\n{EQN_SOURCE[text]}\n.EN\n"
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        ps_path, eps_path, png_path = (
            directory / "equation.ps",
            directory / "equation.eps",
            directory / "equation.png",
        )
        result = subprocess.run(
            ["groff", "-e", "-Tps"], input=source, text=True,
            check=True, capture_output=True,
        )
        ps_path.write_text(result.stdout)
        subprocess.run(["ps2epsi", str(ps_path), str(eps_path)], check=True)
        subprocess.run([
            "gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-dEPSCrop",
            "-sDEVICE=png16m", "-r180", f"-sOutputFile={png_path}", str(eps_path),
        ], check=True)
        return png_path.read_bytes()


def paragraph_info(element):
    texts = [node.text or "" for node in element.iter(W + "t")]
    text = "".join(texts).strip()
    ppr = element.find(W + "pPr")
    style = "Normal"
    align = None
    page_before = False
    if ppr is not None:
        node = ppr.find(W + "pStyle")
        if node is not None:
            style = node.get(W + "val", "Normal")
        node = ppr.find(W + "jc")
        if node is not None:
            align = node.get(W + "val")
        page_before = ppr.find(W + "pageBreakBefore") is not None
    explicit_break = any(
        node.get(W + "type") == "page" for node in element.iter(W + "br")
    )
    sizes = [int(node.get(W + "val")) for node in element.iter(W + "sz")
             if node.get(W + "val", "").isdigit()]
    bold = any(node.tag == W + "b" for node in element.iter())
    image_ids = [node.get(R + "embed") for node in element.iter()
                 if node.tag.endswith("}blip") and node.get(R + "embed")]
    return text, style, align, page_before or explicit_break, max(sizes, default=0), bold, image_ids


class Renderer:
    def __init__(self, media):
        self.media = media
        self.pages = [[]]
        self.y = A4_H - TOP

    @property
    def page(self):
        return self.pages[-1]

    def new_page(self):
        if self.page:
            self.pages.append([])
        self.y = A4_H - TOP

    def ensure(self, height):
        if self.y - height < BOTTOM + 20:
            self.new_page()

    def add_text(self, text, style="Normal", align=None, explicit_size=0, bold=False):
        if not text:
            return
        sizes = {"Heading1": 16, "Heading2": 14, "Heading3": 12,
                 "FrontHeading": 16, "Caption": 10, "Code": 9}
        size = explicit_size/2 if explicit_size else sizes.get(style, 12)
        size = min(size, 22)
        is_bold = bold or style in {"Heading1", "Heading2", "Heading3", "FrontHeading"}
        font = "Courier" if style == "Code" else "Times-Bold" if is_bold else "Times-Roman"
        if style == "FrontHeading":
            align = "center"
        leading = size*1.5 if style not in {"Caption", "Code"} else size*1.25
        before = 12 if style.startswith("Heading") else 7 if style == "FrontHeading" else 2
        after = 8 if style.startswith("Heading") or style == "FrontHeading" else 5
        max_chars = max(18, int(CONTENT_W/(size*0.48)))
        lines = textwrap.wrap(ascii_text(text), width=max_chars, break_long_words=False,
                              break_on_hyphens=False) or [""]
        needed = before + len(lines)*leading + after
        self.ensure(needed)
        self.y -= before
        for line in lines:
            self.y -= leading
            escaped = ps_escape(line)
            if align == "center":
                command = f"({escaped}) dup stringwidth pop 2 div {A4_W/2:.2f} exch sub {self.y:.2f} moveto show"
            elif align == "right":
                command = f"({escaped}) dup stringwidth pop {A4_W-RIGHT:.2f} exch sub {self.y:.2f} moveto show"
            else:
                command = f"{LEFT:.2f} {self.y:.2f} moveto ({escaped}) show"
            self.page.append(f"/{font} findfont {size:.2f} scalefont setfont 0 0 0 setrgbcolor {command}")
        self.y -= after

    def add_table(self, rows):
        if not rows:
            return
        size, leading, padding = 8.5, 10.5, 4.
        column_width = CONTENT_W/len(rows[0])
        max_chars = max(8, int((column_width - 2*padding)/(size*0.48)))

        def layout(cells):
            lines = [
                textwrap.wrap(ascii_text(cell), width=max_chars,
                              break_long_words=False, break_on_hyphens=False) or [""]
                for cell in cells
            ]
            return lines, max(len(cell_lines) for cell_lines in lines)*leading + 2*padding

        layouts = [layout(row) for row in rows]
        total_height = sum(height for _, height in layouts) + 8
        if total_height <= A4_H - TOP - BOTTOM - 20:
            self.ensure(total_height)

        for row_index, (cell_lines, row_height) in enumerate(layouts):
            self.ensure(row_height)
            top, bottom = self.y, self.y - row_height
            if row_index == 0:
                self.page.append(
                    f"0.90 0.94 0.96 setrgbcolor {LEFT:.2f} {bottom:.2f} "
                    f"{CONTENT_W:.2f} {row_height:.2f} rectfill"
                )
            for column in range(len(cell_lines) + 1):
                x = LEFT + column*column_width
                self.page.append(
                    f"0.45 setgray 0.5 setlinewidth newpath {x:.2f} {top:.2f} moveto "
                    f"{x:.2f} {bottom:.2f} lineto stroke"
                )
            self.page.append(
                f"0.45 setgray 0.5 setlinewidth newpath {LEFT:.2f} {top:.2f} moveto "
                f"{LEFT + CONTENT_W:.2f} {top:.2f} lineto stroke newpath "
                f"{LEFT:.2f} {bottom:.2f} moveto {LEFT + CONTENT_W:.2f} {bottom:.2f} lineto stroke"
            )
            font = "Times-Bold" if row_index == 0 else "Times-Roman"
            for column, lines in enumerate(cell_lines):
                x = LEFT + column*column_width + padding
                for line_index, line in enumerate(lines):
                    y = top - padding - size - line_index*leading
                    self.page.append(
                        f"/{font} findfont {size:.2f} scalefont setfont 0 0 0 setrgbcolor "
                        f"{x:.2f} {y:.2f} moveto ({ps_escape(line)}) show"
                    )
            self.y = bottom
        self.y -= 8

    def add_image(self, rel_id):
        width, height, rgb = decode_png(self.media[rel_id])
        display_w = min(CONTENT_W, 455.)
        display_h = display_w*height/width
        if display_h > 330:
            display_h = 330.
            display_w = display_h*width/height
        self.ensure(display_h + 12)
        x = (A4_W-display_w)/2
        y = self.y-display_h
        hex_data = rgb.hex()
        hex_lines = "\n".join(hex_data[index:index+120] for index in range(0, len(hex_data), 120))
        self.page.append(
            f"gsave {x:.2f} {y:.2f} translate {display_w:.2f} {display_h:.2f} scale\n"
            f"/picstr {width*3} string def\n{width} {height} 8 "
            f"[{width} 0 0 -{height} 0 {height}]\n"
            "{currentfile picstr readhexstring pop} false 3 colorimage\n"
            f"{hex_lines}\ngrestore"
        )
        self.y = y - 8

    def add_equation(self, text):
        width, height, rgb = decode_png(
            render_equation_png(text), max_width=1800, max_height=260
        )
        display_w = min(CONTENT_W, width*72./180.)
        display_h = display_w*height/width
        self.ensure(display_h + 16)
        x, y = (A4_W-display_w)/2., self.y-display_h-6
        hex_data = rgb.hex()
        hex_lines = "\n".join(
            hex_data[index:index+120] for index in range(0, len(hex_data), 120)
        )
        self.page.append(
            f"gsave {x:.2f} {y:.2f} translate {display_w:.2f} {display_h:.2f} scale\n"
            f"/picstr {width*3} string def\n{width} {height} 8 "
            f"[{width} 0 0 -{height} 0 {height}]\n"
            "{currentfile picstr readhexstring pop} false 3 colorimage\n"
            f"{hex_lines}\ngrestore"
        )
        self.y = y - 8


def render_report():
    build_report()
    with ZipFile(DOCX) as package:
        document = ET.fromstring(package.read("word/document.xml"))
        rels = ET.fromstring(package.read("word/_rels/document.xml.rels"))
        targets = {node.get("Id"): node.get("Target") for node in rels.findall(REL + "Relationship")}
        media = {
            rel_id: package.read("word/" + target)
            for rel_id, target in targets.items()
            if target and target.startswith("media/")
        }

        renderer = Renderer(media)
        body = document.find(W + "body")
        for child in body:
            if child.tag == W + "p":
                text, style, align, new_page, size, bold, image_ids = paragraph_info(child)
                if new_page:
                    renderer.new_page()
                for rel_id in image_ids:
                    renderer.add_image(rel_id)
                if text:
                    if style == "Equation":
                        renderer.add_equation(text)
                    else:
                        renderer.add_text(text, style, align, size, bold)
            elif child.tag == W + "tbl":
                rows = []
                for row in child.findall(W + "tr"):
                    cells = []
                    for cell in row.findall(W + "tc"):
                        cells.append(" ".join(
                            "".join(node.text or "" for node in paragraph.iter(W + "t"))
                            for paragraph in cell.findall(W + "p")
                        ).strip())
                    rows.append(cells)
                renderer.add_table(rows)

    ps = [
        "%!PS-Adobe-3.0",
        f"%%Pages: {len(renderer.pages)}",
        f"%%BoundingBox: 0 0 {int(A4_W)} {int(A4_H)}",
        f"<< /PageSize [{A4_W:.3f} {A4_H:.3f}] >> setpagedevice",
    ]
    for page_number, operations in enumerate(renderer.pages, 1):
        ps.append(f"%%Page: {page_number} {page_number}")
        ps.extend(operations)
        ps.append(
            f"/Times-Roman findfont 9 scalefont setfont "
            f"({page_number}) dup stringwidth pop 2 div {A4_W/2:.2f} exch sub 30 moveto show"
        )
        ps.append("showpage")
    ps.append("%%EOF")

    PDF.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".ps", encoding="ascii") as source:
        source.write("\n".join(ps))
        source.flush()
        subprocess.run([
            "gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE",
            "-sDEVICE=pdfwrite", "-sPAPERSIZE=a4", f"-sOutputFile={PDF}", source.name,
        ], check=True)
    return PDF


if __name__ == "__main__":
    print(render_report())
