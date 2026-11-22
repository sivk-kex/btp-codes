from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1280, 720
LEFT, TOP, RIGHT, BOTTOM = 125, 95, 1220, 575
X_MIN, X_MAX = 0.0, 2.0
Y_MIN, Y_MAX = -0.012, 0.012


def font(size):
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size
    )


def load_profiles(path):
    frames = []
    current = None
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if line.startswith("# frame"):
            _, _, time, tau = line.split()
            current = {"time": float(time), "tau": float(tau), "points": []}
        elif line == "# end":
            frames.append(current)
            current = None
        elif line and current is not None:
            x, y = map(float, line.split())
            current["points"].append((x, y))
    return frames


def profile_points(points):
    grouped = {}
    for x, y in points:
        grouped.setdefault(round(x, 9), []).append(y)
    return [(x, sum(values)/len(values)) for x, values in sorted(grouped.items())]


def px(x):
    return LEFT + (x - X_MIN)/(X_MAX - X_MIN)*(RIGHT - LEFT)


def py(y):
    return BOTTOM - (y - Y_MIN)/(Y_MAX - Y_MIN)*(BOTTOM - TOP)


def centered(draw, xy, text, text_font, fill):
    box = draw.textbbox((0, 0), text, font=text_font)
    draw.text((xy[0] - (box[2] - box[0])/2, xy[1]), text,
              font=text_font, fill=fill)


def render(frame):
    image = Image.new("RGB", (WIDTH, HEIGHT), (244, 247, 250))
    draw = ImageDraw.Draw(image)
    title_font, body_font, tick_font = font(34), font(23), font(19)

    draw.text((LEFT, 28), "Viscous capillary-wave decay", font=title_font,
              fill=(20, 39, 64))
    time_label = f"τ = {frame['tau']:.2f}    t = {frame['time']:.3f}"
    time_box = draw.textbbox((0, 0), time_label, font=body_font)
    draw.text((RIGHT - time_box[2], 38), time_label, font=body_font,
              fill=(43, 70, 102))

    draw.rectangle((LEFT, TOP, RIGHT, BOTTOM), fill=(255, 255, 255),
                   outline=(116, 132, 150), width=2)

    x_ticks = [0, 0.5, 1, 1.5, 2]
    y_ticks = [-0.01, -0.005, 0, 0.005, 0.01]
    for value in x_ticks:
        x = px(value)
        draw.line((x, TOP, x, BOTTOM), fill=(224, 229, 235), width=1)
        centered(draw, (x, BOTTOM + 12), f"{value:g}", tick_font,
                 (55, 65, 81))
    for value in y_ticks:
        y = py(value)
        draw.line((LEFT, y, RIGHT, y), fill=(224, 229, 235), width=1)
        label = f"{value:+.3f}" if value else "0"
        box = draw.textbbox((0, 0), label, font=tick_font)
        draw.text((LEFT - box[2] - 12, y - (box[3] - box[1])/2), label,
                  font=tick_font, fill=(55, 65, 81))

    points = [(px(x), py(y)) for x, y in profile_points(frame["points"])]
    water = [(LEFT, BOTTOM), *points, (RIGHT, BOTTOM)]
    draw.polygon(water, fill=(91, 169, 224))

    zero = py(0)
    for x in range(LEFT, RIGHT, 18):
        draw.line((x, zero, min(x + 9, RIGHT), zero),
                  fill=(112, 122, 133), width=2)
    draw.line(points, fill=(4, 61, 107), width=5, joint="curve")

    centered(draw, ((LEFT + RIGHT)/2, BOTTOM + 45),
             "Horizontal position x  (wavelength λ = 1)", body_font,
             (32, 48, 68))
    draw.text((LEFT, TOP - 34), "Interface elevation y", font=body_font,
              fill=(32, 48, 68))
    note = "Basilisk VOF · N = 128 · σ = 1 · μ = 0.018257"
    centered(draw, ((LEFT + RIGHT)/2, HEIGHT - 38), note, tick_font,
             (78, 91, 108))
    return image


frames = load_profiles(Path("profiles.dat"))
target = Path("capwave.clear.mp4")

with av.open(target, "w", options={"movflags": "+faststart"}) as output_file:
    stream = output_file.add_stream(
        "libx264", rate=25,
        options={"profile": "baseline", "preset": "medium", "crf": "18"},
    )
    stream.width, stream.height = WIDTH, HEIGHT
    stream.pix_fmt = "yuv420p"
    stream.codec_context.max_b_frames = 0

    for index, data in enumerate(frames):
        image = render(data)
        if index == 0:
            image.save("capwave-preview.png")
        video_frame = av.VideoFrame.from_image(image)
        for packet in stream.encode(video_frame):
            output_file.mux(packet)

    for packet in stream.encode():
        output_file.mux(packet)

print(f"frames={len(frames)} output={target}")
