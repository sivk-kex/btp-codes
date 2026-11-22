#!/usr/bin/env python3
"""Smoke-check Kayal et al. (2022) Figure 4(b) reproduction data."""

from pathlib import Path


data = Path(__file__).with_name("kayal2022-wave.dat")
assert data.exists(), f"missing simulation output: {data.name}"

rows = [
    tuple(map(float, line.split()))
    for line in data.read_text().splitlines()
    if line and not line.startswith("#")
]
assert len(rows) >= 150, f"too few samples: {len(rows)}"

time = [row[0] for row in rows]
amplitude = [row[2] for row in rows]
assert all(b > a for a, b in zip(time, time[1:])), "time must increase"
assert abs(amplitude[0] - 1.0) < 0.03, amplitude[0]
assert min(amplitude) < -0.8, min(amplitude)
assert max(amplitude[time.index(min(t for t in time if t > 6.0)):]) > 0.8

print(f"PASS: {len(rows)} samples, amplitude range [{min(amplitude):.3f}, {max(amplitude):.3f}]")
