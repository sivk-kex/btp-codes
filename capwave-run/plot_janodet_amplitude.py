import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


a0 = 2*math.pi/100
omega0 = math.sqrt(2/1001)
authors = [(0.0, 1.0)] + [
    (time*omega0, height/a0)
    for time, height in (
        map(float, line.split())
        for line in Path(
            "raw_data_Janodet_et_al_2024/02_capillary_wave/WaveHeight_M050_S8"
        ).read_text().splitlines()
    )
]
simulation = [
    (values[1], values[3])
    for line in Path("janodet2024-wave.dat").read_text().splitlines()
    if line and not line.startswith("#")
    for values in [tuple(map(float, line.split()))]
]


def interpolate(points, x):
    for left, right in zip(points, points[1:]):
        if left[0] <= x <= right[0]:
            weight = (x - left[0])/(right[0] - left[0])
            return left[1] + weight*(right[1] - left[1])
    return points[-1][1]


rms = math.sqrt(sum(
    (value - interpolate(authors, tau))**2 for tau, value in simulation
)/len(simulation))

width, height = 1400, 850
left, top, right, bottom = 150, 95, 1340, 725


def font(size):
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size
    )


def px(value):
    return left + value/25*(right - left)


def py(value):
    return bottom - (value + 0.7)/1.75*(bottom - top)


image = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(image)
title_font, label_font, tick_font = font(36), font(27), font(22)
draw.text((left, 25), "Large-density-ratio capillary wave",
          font=title_font, fill="#16273b")
draw.rectangle((left, top, right, bottom), outline="#708090", width=2)

for value in range(0, 26, 5):
    x = px(value)
    draw.line((x, top, x, bottom), fill="#e1e5ea")
    draw.text((x - 10, bottom + 12), str(value), font=tick_font, fill="#374151")
for value in (-0.5, 0.0, 0.5, 1.0):
    y = py(value)
    draw.line((left, y, right, y), fill="#e1e5ea")
    draw.text((left - 60, y - 12), f"{value:.1f}",
              font=tick_font, fill="#374151")

draw.line([(px(x), py(y)) for x, y in authors], fill="#d13c3c", width=4)
draw.line([(px(x), py(y)) for x, y in simulation], fill="#174f9b", width=3)
for x, y in simulation[::20]:
    draw.ellipse((px(x) - 4, py(y) - 4, px(x) + 4, py(y) + 4), fill="#174f9b")

draw.text((right - 470, top + 25), "—  Authors' M50 data",
          font=tick_font, fill="#d13c3c")
draw.text((right - 470, top + 62), "—  Basilisk VOF, 64 cells/λ",
          font=tick_font, fill="#174f9b")
draw.text(((left + right)//2 - 170, bottom + 62),
          "Nondimensional time  τ = ω₀t", font=label_font, fill="#26384c")
y_label = Image.new("RGBA", (500, 50), (255, 255, 255, 0))
ImageDraw.Draw(y_label).text((0, 0), "Signed amplitude  a(t)/a₀",
                            font=label_font, fill="#26384c")
y_label = y_label.rotate(90, expand=True)
image.paste(y_label, (28, (top + bottom - y_label.height)//2), y_label)
draw.text((left, height - 45),
          f"Janodet et al. case · ρ₁/ρ₂ = μ₁/μ₂ = 1000 · La = 300 · RMS difference = {rms:.3g}",
          font=tick_font, fill="#526174")
image.save("janodet2024-amplitude-vs-time.png")
print(f"janodet2024-amplitude-vs-time.png RMS={rms:.8g}")
