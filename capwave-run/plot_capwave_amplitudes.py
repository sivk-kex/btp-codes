#!/usr/bin/env python3
"""Plot traditional capwave amplitude histories for two initial amplitudes."""

from pathlib import Path

from plot_nonlinear_fourier import (
    COLORS,
    _frame,
    _header,
    _line,
    _polyline,
    _render,
    _text,
)


def load_amplitude(path):
    return [
        tuple(map(float, line.split()))
        for line in Path(path).read_text().splitlines()
        if line
    ]


def render_case(rows, label, output):
    ps = _header()
    _text(ps, 100, 48, f"Capillary-wave amplitude: a0 = {label}", 34)
    left, right, top, bottom = 140, 1515, 115, 745
    xmax = max(tau for tau, _ in rows)
    ymax = max(amplitude for _, amplitude in rows)*1.08
    px = lambda value: left + value/xmax*(right-left)
    py = lambda value: bottom - value/ymax*(bottom-top)
    _frame(ps, left, top, right, bottom)
    for fraction in (0., 0.25, 0.5, 0.75, 1.):
        x = left + fraction*(right-left)
        _line(ps, x, top, x, bottom)
        _text(ps, x-12, bottom+28, f"{fraction*xmax:g}", 17)
        value = fraction*ymax
        y = py(value)
        _line(ps, left, y, right, y)
        _text(ps, left-78, y+6, f"{value:.3g}", 17)
    _polyline(ps, [(px(tau), py(amplitude)) for tau, amplitude in rows], COLORS[0], 3)
    _text(ps, 650, bottom+68, "Nondimensional time  tau", 21)
    ps.append(
        "gsave 34 315 translate 90 rotate 0.13 0.17 0.23 setrgbcolor "
        "/Helvetica findfont 22 scalefont setfont 0 0 moveto "
        r"(Wave amplitude A\(t\)) show grestore"
    )
    _text(ps, 140, 865,
          "Traditional capwave.c amplitude output | N = 128 | only a0 changed",
          19, "0.31 0.36 0.43")
    _render(ps, output)


def render_all(directory=Path(".")):
    directory = Path(directory)
    outputs = []
    for label in ("0.1", "0.5"):
        output = directory / f"amplitude-a0-{label}-vs-time.png"
        render_case(
            load_amplitude(directory / f"capwave-a0-{label}.dat"),
            label,
            output,
        )
        outputs.append(output)
    return outputs


if __name__ == "__main__":
    for figure in render_all(Path(__file__).resolve().parent):
        print(figure.name)
