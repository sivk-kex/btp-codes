import subprocess
import tempfile
from pathlib import Path


rows = [
    tuple(map(float, line.split()))
    for line in Path("kayal2022-wave.dat").read_text().splitlines()
    if line and not line.startswith("#")
]
curve = [(t, amplitude) for t, _, amplitude in rows if t <= 8.2]
minimum = min(curve, key=lambda point: point[1])
rebound = max((point for point in curve if point[0] > 6.), key=lambda point: point[1])

width, height = 1400, 850
left, top, right, bottom = 150, 95, 1340, 725
x_min, x_max = 0., 8.2
y_min, y_max = -1.3, 1.25


def px(value):
    return left + (value - x_min)/(x_max - x_min)*(right - left)


def py(value):
    return height - (bottom - (value - y_min)/(y_max - y_min)*(bottom - top))


def escaped(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


ps = [
    "%!PS-Adobe-3.0",
    f"<< /PageSize [{width} {height}] >> setpagedevice",
    "1 1 1 setrgbcolor clippath fill",
]


def line(x1, y1, x2, y2, color="0.88 0.90 0.92", stroke=1):
    ps.append(f"{color} setrgbcolor {stroke} setlinewidth newpath "
              f"{x1:.2f} {height-y1:.2f} moveto {x2:.2f} {height-y2:.2f} lineto stroke")


def text(x, y, value, size=22, color="0.22 0.25 0.32"):
    ps.append(f"{color} setrgbcolor /Helvetica findfont {size} scalefont setfont "
              f"{x:.2f} {height-y:.2f} moveto ({escaped(value)}) show")


text(left, 52, "Nonlinear axisymmetric capillary wave", 36, "0.09 0.15 0.23")
line(left, top, right, top, "0.44 0.50 0.56", 2)
line(right, top, right, bottom, "0.44 0.50 0.56", 2)
line(right, bottom, left, bottom, "0.44 0.50 0.56", 2)
line(left, bottom, left, top, "0.44 0.50 0.56", 2)

for value in range(9):
    x = px(value)
    line(x, top, x, bottom)
    text(x - 7, bottom + 30, str(value))
for value in (-1., -0.5, 0., 0.5, 1.):
    screen_y = height - py(value)
    line(left, screen_y, right, screen_y)
    text(left - 65, screen_y + 8, f"{value:g}")

ps.append("0.89 0.10 0.11 setrgbcolor 5 setlinewidth 1 setlinejoin newpath")
for index, (t, amplitude) in enumerate(curve):
    command = "moveto" if index == 0 else "lineto"
    ps.append(f"{px(t):.2f} {py(amplitude):.2f} {command}")
ps.append("stroke")

for t, amplitude in curve[::10]:
    ps.append(f"0.89 0.10 0.11 setrgbcolor newpath {px(t):.2f} {py(amplitude):.2f} "
              "3 0 360 arc fill")

for label, point, dx, dy in (
    (f"minimum {minimum[1]:.3f} at t={minimum[0]:.2f}", minimum, 18, -14),
    (f"rebound {rebound[1]:.3f} at t={rebound[0]:.2f}", rebound, -300, 55),
):
    x, y = px(point[0]), py(point[1])
    ps.append(f"0.09 0.31 0.61 setrgbcolor newpath {x:.2f} {y:.2f} 7 0 360 arc fill")
    ps.append(f"0.09 0.31 0.61 setrgbcolor /Helvetica findfont 22 scalefont setfont "
              f"{x+dx:.2f} {y+dy:.2f} moveto ({escaped(label)}) show")

text((left + right)/2 - 145, bottom + 75, "Nondimensional time  t", 27, "0.15 0.22 0.30")
ps.append("gsave 42 270 translate 90 rotate 0.15 0.22 0.30 setrgbcolor "
          "/Helvetica findfont 27 scalefont setfont 0 0 moveto "
          "(Centre amplitude  eta\\(0,t\\)/epsilon) show grestore")
text(left, height - 22,
     "Kayal, Basak & Dasgupta (2022), Fig. 4(b) case | epsilon = 1.8 | l15 = 47.9 | level 9",
     20, "0.32 0.38 0.45")
ps.extend(["showpage", "%%EOF"])

with tempfile.NamedTemporaryFile("w", suffix=".ps") as source:
    source.write("\n".join(ps))
    source.flush()
    subprocess.run([
        "gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE",
        "-sDEVICE=png16m", "-r72", f"-g{width}x{height}", "-dFIXEDMEDIA",
        "-sOutputFile=kayal2022-amplitude-vs-time.png", source.name,
    ], check=True)

print("kayal2022-amplitude-vs-time.png")
