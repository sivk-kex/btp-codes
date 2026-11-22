import math
import re
import subprocess
import tempfile
from pathlib import Path


root = Path(__file__).parent
reference_path = root.parent / "basilisk/src/test/prosperetti-gravity.h"
reference = [
    tuple(map(float, match))
    for match in re.findall(
        r"\{\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\}",
        reference_path.read_text(),
    )
]
simulation = [
    tuple(map(float, line.split()))
    for line in (root / "wave-128").read_text().splitlines()
    if line
]
errors = [
    tuple(map(float, line.split()))
    for line in (root / "gravity.log").read_text().splitlines()
    if len(line.split()) == 2
]

width, height = 1400, 850
left, top, right, bottom = 155, 95, 1335, 710


def escaped(value):
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def text(ps, x, y, value, size=22, color="0.16 0.20 0.27"):
    ps.append(f"{color} setrgbcolor /Helvetica findfont {size} scalefont setfont "
              f"{x:.2f} {height-y:.2f} moveto ({escaped(value)}) show")


def line(ps, x1, y1, x2, y2, color="0.86 0.89 0.92", stroke=1):
    ps.append(f"{color} setrgbcolor {stroke} setlinewidth newpath "
              f"{x1:.2f} {height-y1:.2f} moveto {x2:.2f} {height-y2:.2f} lineto stroke")


def polyline(ps, points, color, stroke):
    ps.append(f"{color} setrgbcolor {stroke} setlinewidth 1 setlinejoin newpath")
    for index, (x, y) in enumerate(points):
        ps.append(f"{x:.2f} {height-y:.2f} {'moveto' if index == 0 else 'lineto'}")
    ps.append("stroke")


def frame(ps):
    for x1, y1, x2, y2 in (
        (left, top, right, top), (right, top, right, bottom),
        (right, bottom, left, bottom), (left, bottom, left, top),
    ):
        line(ps, x1, y1, x2, y2, "0.36 0.42 0.49", 2)


def render(ps, output):
    ps.extend(["showpage", "%%EOF"])
    with tempfile.NamedTemporaryFile("w", suffix=".ps") as source:
        source.write("\n".join(ps))
        source.flush()
        subprocess.run([
            "gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE",
            "-sDEVICE=png16m", "-r72", f"-g{width}x{height}", "-dFIXEDMEDIA",
            f"-sOutputFile={output}", source.name,
        ], check=True)


# Amplitude versus time.
ps = ["%!PS-Adobe-3.0", f"<< /PageSize [{width} {height}] >> setpagedevice",
      "1 1 1 setrgbcolor clippath fill"]
xmax, ymax = 30., 0.01
px = lambda value: left + value/xmax*(right-left)
py = lambda value: top + (ymax-value)/ymax*(bottom-top)

text(ps, left, 52, "Gravity-wave amplitude decay", 36, "0.08 0.14 0.22")
frame(ps)
for value in range(0, 31, 5):
    x = px(value)
    line(ps, x, top, x, bottom)
    text(ps, x-10, bottom+32, str(value))
for index in range(6):
    value = index*0.002
    y = py(value)
    line(ps, left, y, right, y)
    text(ps, left-82, y+7, f"{value:.3f}" if value else "0")

polyline(ps, [(px(t), py(a)) for t, a in reference], "0.72 0.18 0.88", 3)
for t, amplitude in simulation[::10]:
    x, y = px(t), py(amplitude)
    line(ps, x-5, y-5, x+5, y+5, "0.05 0.64 0.57", 1.5)
    line(ps, x-5, y+5, x+5, y-5, "0.05 0.64 0.57", 1.5)

line(ps, right-250, top+30, right-185, top+30, "0.72 0.18 0.88", 3)
text(ps, right-175, top+37, "Prosperetti", 21)
line(ps, right-218, top+60, right-208, top+70, "0.05 0.64 0.57", 1.5)
line(ps, right-218, top+70, right-208, top+60, "0.05 0.64 0.57", 1.5)
text(ps, right-198, top+72, "Basilisk N=128", 21)
text(ps, (left+right)/2-155, bottom+76, "Nondimensional time  tau", 27)
ps.append("gsave 42 265 translate 90 rotate 0.15 0.22 0.30 setrgbcolor "
          "/Helvetica findfont 27 scalefont setfont 0 0 moveto "
          "(Relative amplitude) show grestore")
text(ps, left, height-22, "Basilisk src/test/gravity.c | reduced gravity | rho1/rho2 = 10", 20,
     "0.32 0.38 0.45")
render(ps, root / "gravity-amplitude-vs-time.png")


# RMS error convergence.
ps = ["%!PS-Adobe-3.0", f"<< /PageSize [{width} {height}] >> setpagedevice",
      "1 1 1 setrgbcolor clippath fill"]
xmin, xmax = math.log2(6.), math.log2(180.)
ymin, ymax = -4., 0.
px = lambda value: left + (math.log2(value)-xmin)/(xmax-xmin)*(right-left)
py = lambda value: bottom - (math.log10(value)-ymin)/(ymax-ymin)*(bottom-top)

text(ps, left, 52, "Gravity-wave grid convergence", 36, "0.08 0.14 0.22")
frame(ps)
for value in (8, 16, 32, 64, 128):
    x = px(value)
    line(ps, x, top, x, bottom, "0.78 0.82 0.86", 1)
    text(ps, x-14, bottom+32, str(value))
for exponent in range(0, -5, -1):
    value = 10.**exponent
    y = py(value)
    line(ps, left, y, right, y, "0.78 0.82 0.86", 1)
    text(ps, left-95, y+7, f"1e{exponent}" if exponent else "1")

polyline(ps, [(px(n), py(error)) for n, error in errors], "0.58 0.12 0.96", 3)
for n, error in errors:
    x, y = px(n), py(error)
    ps.append(f"0.58 0.12 0.96 setrgbcolor newpath {x:.2f} {height-y:.2f} 6 0 360 arc fill")
second_order = [(2.**(3+i/30), 2./(2.**(3+i/30))**2) for i in range(121)]
polyline(ps, [(px(n), py(error)) for n, error in second_order], "0.05 0.64 0.57", 3)

line(ps, right-270, top+30, right-205, top+30, "0.58 0.12 0.96", 3)
text(ps, right-195, top+37, "Basilisk", 21)
line(ps, right-270, top+62, right-205, top+62, "0.05 0.64 0.57", 3)
text(ps, right-195, top+69, "Second order", 21)
text(ps, (left+right)/2-165, bottom+76, "Grid points per wavelength", 27)
ps.append("gsave 42 260 translate 90 rotate 0.15 0.22 0.30 setrgbcolor "
          "/Helvetica findfont 27 scalefont setfont 0 0 moveto "
          "(Relative RMS error) show grestore")
text(ps, left, height-22,
     "Errors: N/lambda = 8, 16, 32, 64 | 0.1267, 0.03176, 0.008078, 0.004558",
     20, "0.32 0.38 0.45")
render(ps, root / "gravity-rms-convergence.png")

print("gravity-amplitude-vs-time.png")
print("gravity-rms-convergence.png")
