#!/usr/bin/env python3
"""Render amplitude and phase histories for travelling_wave.c output."""

import math
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


def load_diagnostics(path):
    return [
        tuple(map(float, line.split()))
        for line in Path(path).read_text().splitlines()
        if line and not line.startswith("#")
    ]


def unwrap_phases(rows):
    phases = [rows[0][4]]
    for row in rows[1:]:
        delta = row[4] - phases[-1] % (2.*math.pi)
        if delta < -math.pi:
            delta += 2.*math.pi
        elif delta > math.pi:
            delta -= 2.*math.pi
        phases.append(phases[-1] + delta)
    return phases


def _axes(ps, title, xmax, ymax, ylabel):
    left, right, top, bottom = 140, 1515, 115, 745
    _text(ps, 100, 48, title, 34)
    _frame(ps, left, top, right, bottom)
    for fraction in (0., 0.25, 0.5, 0.75, 1.):
        x = left + fraction*(right-left)
        y = bottom - fraction*(bottom-top)
        _line(ps, x, top, x, bottom)
        _line(ps, left, y, right, y)
        _text(ps, x-12, bottom+28, f"{fraction*xmax:.2g}", 17)
        _text(ps, left-72, y+6, f"{fraction*ymax:.2g}", 17)
    _text(ps, 650, bottom+68, "Nondimensional time  tau", 21)
    ps.append(
        "gsave 34 315 translate 90 rotate 0.13 0.17 0.23 setrgbcolor "
        "/Helvetica findfont 22 scalefont setfont 0 0 moveto "
        f"({ylabel}) show grestore"
    )
    return left, right, top, bottom


def render_amplitude(rows, output):
    ps = _header()
    xmax = rows[-1][0]
    a0 = rows[0][3]
    left, right, _, bottom = _axes(
        ps, "Travelling-wave amplitude decay", xmax, 1., "Normalized amplitude  |A|/a0"
    )
    px = lambda value: left + value/xmax*(right-left)
    py = lambda value: bottom - value*(bottom-115)
    _polyline(ps, [(px(row[0]), py(row[3]/a0)) for row in rows], COLORS[0], 3)
    _text(ps, 140, 865, "Basilisk travelling capillary wave | a0 = 0.01 | N = 128", 19,
          "0.31 0.36 0.43")
    _render(ps, output)


def render_phase(rows, output):
    ps = _header()
    xmax = rows[-1][0]
    phases = unwrap_phases(rows)
    ymax = xmax
    left, right, _, bottom = _axes(
        ps, "Right-travelling wave phase", xmax, ymax, "Unwrapped phase  radians"
    )
    px = lambda value: left + value/xmax*(right-left)
    py = lambda value: bottom - value/ymax*(bottom-115)
    _polyline(ps, [(px(row[0]), py(phase)) for row, phase in zip(rows, phases)], COLORS[0], 3)
    _polyline(ps, [(px(0.), py(0.)), (px(xmax), py(xmax))], COLORS[1], 2)
    _line(ps, 1120, 145, 1170, 145, COLORS[0], 3)
    _text(ps, 1185, 151, "Basilisk", 18)
    _line(ps, 1320, 145, 1370, 145, COLORS[1], 2)
    _text(ps, 1385, 151, "Theory", 18)
    _text(ps, 140, 865, "Slope = 0.90572; positive phase means rightward propagation", 19,
          "0.31 0.36 0.43")
    _render(ps, output)


def render_all(directory=Path(".")):
    directory = Path(directory)
    rows = load_diagnostics(directory / "travelling-wave.dat")
    outputs = [
        directory / "travelling-wave-amplitude.png",
        directory / "travelling-wave-phase.png",
    ]
    render_amplitude(rows, outputs[0])
    render_phase(rows, outputs[1])
    return outputs


if __name__ == "__main__":
    for figure in render_all(Path(__file__).resolve().parent):
        print(figure.name)
