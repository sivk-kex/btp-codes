# Linear travelling capillary wave

## Purpose

This case extends the standing-wave benchmark with a right-travelling wave. It keeps the same two-dimensional VOF, centered Navier--Stokes, surface-tension, and fluid-property setup.

## Model

- Domain: `2 x 2`; wavelength: `1`; grid: `N = 128`.
- Horizontal boundary: periodic.
- Top and bottom boundaries: no penetration.
- Surface tension: `sigma = 1`; gravity: `0`.
- Fluid densities: `rho1 = rho2 = 1`.
- Fluid viscosities: `mu1 = mu2 = 0.0182571749236`.
- Initial interface: `eta(x,0) = 0.01 cos(2 pi x)`.

Unlike the standing-wave case, this simulation initializes a phase-matched velocity-potential field. For a right-travelling wave,

`eta(x,t) = a0 cos(kx - omega t)`.

The finite-depth linear frequency is

`omega^2 = sigma k^3 tanh(kh)/(rho1 + rho2)`.

## Run

From `capwave-run`:

```bash
../basilisk/src/qcc -O2 -Wall travelling_wave.c -o travelling_wave -lm
./travelling_wave 0.01 travelling-wave.dat 128
python3 -m unittest -v test_travelling_wave.py
```

Data columns are:

```text
tau cosine sine magnitude phase crest_x
```

Phase comes from the first spatial Fourier mode. Crest position is phase divided by wavenumber, wrapped to one wavelength.

## Result

- Samples: `126`, from `tau = 0` to `6.255`.
- Initial first-mode amplitude: `0.00998795`.
- Final unwrapped phase: `5.70890 rad`.
- Fitted phase rate: `d phase/d tau = 0.90572`.
- Measured phase speed: `0.90572` times inviscid linear theory.
- Final amplitude: `0.00495856`, or `49.65%` of initial amplitude.

Phase increased at every recorded step, confirming rightward propagation rather than standing oscillation. Difference from inviscid theory is consistent with this viscous, discretized initialization; this run is a numerical validation of travelling behavior, not an exact inviscid solution.

## Scope

This result validates one small-amplitude, pure-capillary travelling wave. Gravity, unequal fluid properties, large-amplitude waves, and wave interactions remain separate future cases.
