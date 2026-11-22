#!/usr/bin/env python3
"""Smoke-check outputs from Basilisk src/test/gravity.c."""

from pathlib import Path
from struct import unpack


root = Path(__file__).parent
initial_errors = []
for resolution in (16, 32, 64, 128):
    path = root / f"wave-{resolution}"
    assert path.exists(), f"missing {path.name}"
    rows = [
        tuple(map(float, line.split()))
        for line in path.read_text().splitlines()
        if line and not line.startswith("#")
    ]
    assert len(rows) >= 700, f"{path.name}: only {len(rows)} samples"
    initial_errors.append(abs(rows[0][1] - 0.01))

assert all(fine < coarse for coarse, fine in zip(initial_errors, initial_errors[1:])), initial_errors
assert initial_errors[-1] < 5e-5, initial_errors[-1]

log_rows = []
for line in (root / "gravity.log").read_text().splitlines():
    fields = line.split()
    if len(fields) == 2:
        try:
            log_rows.append(tuple(map(float, fields)))
        except ValueError:
            pass

assert [row[0] for row in log_rows] == [8., 16., 32., 64.], log_rows
errors = [row[1] for row in log_rows]
assert all(fine < coarse for coarse, fine in zip(errors, errors[1:])), errors

for name in ("gravity-amplitude-vs-time.png", "gravity-rms-convergence.png"):
    image_path = root / name
    assert image_path.exists(), f"missing graph: {name}"
    image = image_path.read_bytes()
    assert image.startswith(b"\x89PNG\r\n\x1a\n"), f"invalid PNG: {name}"
    assert unpack(">II", image[16:24]) == (1400, 850), f"wrong dimensions: {name}"

print(f"PASS: four resolutions; relative RMS errors {errors}")
