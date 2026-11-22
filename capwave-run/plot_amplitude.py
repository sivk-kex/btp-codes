from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


data_path = Path("pan2024-wave.dat")
output_path = Path("pan2024-amplitude-vs-time.png")
rows = [
    tuple(map(float, line.split()))
    for line in data_path.read_text().splitlines()
    if line and not line.startswith("#")
]

width, height = 1400, 850
left, top, right, bottom = 150, 95, 1340, 725
x_min, x_max = 0.0, 25.0
y_min, y_max = -0.02, 1.05


def font(size):
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size
    )


def px(value):
    return left + (value - x_min)/(x_max - x_min)*(right - left)


def py(value):
    return bottom - (value - y_min)/(y_max - y_min)*(bottom - top)


image = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(image)
title_font, label_font, tick_font = font(38), font(28), font(22)

draw.text((left, 25), "Standing capillary wave: amplitude decay",
          font=title_font, fill="#16273b")
draw.rectangle((left, top, right, bottom), outline="#708090", width=2)

for value in range(0, 26, 5):
    x = px(value)
    draw.line((x, top, x, bottom), fill="#e1e5ea", width=1)
    draw.text((x - 10, bottom + 12), str(value), font=tick_font, fill="#374151")
for value in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
    y = py(value)
    draw.line((left, y, right, y), fill="#e1e5ea", width=1)
    label = f"{value:.1f}"
    box = draw.textbbox((0, 0), label, font=tick_font)
    draw.text((left - box[2] - 15, y - 12), label,
              font=tick_font, fill="#374151")

theory = [(px(tau), py(reference)) for tau, _, reference in rows]
simulation = [(px(tau), py(amplitude)) for tau, amplitude, _ in rows]
draw.line(theory, fill="#d13c3c", width=4, joint="curve")
draw.line(simulation, fill="#174f9b", width=3, joint="curve")

for tau, amplitude, _ in rows[::30]:
    x, y = px(tau), py(amplitude)
    draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill="#174f9b")

draw.text((right - 410, top + 25), "—  Prosperetti theory",
          font=tick_font, fill="#d13c3c")
draw.text((right - 410, top + 62), "—  Basilisk PLIC-VOF",
          font=tick_font, fill="#174f9b")
draw.text(((left + right)//2 - 170, bottom + 62),
          "Nondimensional time  τ = ω₀t", font=label_font, fill="#26384c")
y_label = Image.new("RGBA", (500, 50), (255, 255, 255, 0))
ImageDraw.Draw(y_label).text((0, 0), "Relative amplitude  a(t)/a₀",
                            font=label_font, fill="#26384c")
y_label = y_label.rotate(90, expand=True)
image.paste(y_label, (28, (top + bottom - y_label.height)//2), y_label)
draw.text((left, height - 45),
          "Pan et al. (2024), Fig. 23 parameters · 64 × 256 cells · La = 3000",
          font=tick_font, fill="#526174")

image.save(output_path)
print(output_path)
