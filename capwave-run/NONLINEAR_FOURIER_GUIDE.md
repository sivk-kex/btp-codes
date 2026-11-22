# Finite-amplitude capillary waves: Fourier analysis

## What was changed

The original capillary-wave test used a small sinusoidal disturbance. This
study keeps the physical and numerical conditions fixed and changes only the
initial amplitude:

- Case 1: `a0 = 0.1`
- Case 2: `a0 = 0.5`

The initial interface is

\[
\eta(x,0)=a_0\cos(2\pi x),
\]

where the wavelength is `lambda = 1`. The `a0 = 0.5` wave is five times
taller and much steeper than the `a0 = 0.1` wave.

## Conditions kept fixed

| Quantity | Value |
|---|---:|
| Domain | `2 x 2` |
| Wavelength | `1` |
| Surface tension, `sigma` | `1` |
| Fluid densities | `rho1 = rho2 = 1` |
| Fluid viscosities | `mu1 = mu2 = 0.0182571749236` |
| Gravity | `0` |
| Grid | `N = 128`, giving 64 cells per wavelength |
| Maximum CFL number | `0.5` |
| Final nondimensional time | `tau = 25` |

This is a pure capillary-wave comparison. It does not yet include gravity or
an air-water density ratio.

## What the Fourier transform measures

At every output time, the code separates the interface into spatial
harmonics. For harmonic `n`, it calculates

\[
C_n(t)=\frac{2}{L}\int_0^L\eta(x,t)\cos(2\pi n x)\,dx,
\]

\[
S_n(t)=\frac{2}{L}\int_0^L\eta(x,t)\sin(2\pi n x)\,dx,
\]

and

\[
A_n(t)=\sqrt{C_n^2+S_n^2}.
\]

The graphs show `A_n/a0`, so both amplitudes can be compared on the same
scale. The code evaluates these coefficients from the vertically integrated
VOF field. For a single-valued interface, this is equivalent to transforming
the interface height.

Mode meanings:

- Mode 1: original sinusoidal wave.
- Modes 2-8: new spatial harmonics generated during evolution.
- Strong higher modes: stronger nonlinear deformation.

## Main result

| Case | Maximum mode 3 | Maximum mode 5 | Maximum mode 7 |
|---|---:|---:|---:|
| `a0 = 0.1` | `0.0209 a0` | `0.00136 a0` | `0.000334 a0` |
| `a0 = 0.5` | `0.1975 a0` | `0.1043 a0` | `0.0691 a0` |

The `a0 = 0.1` case remains close to a linear standing wave. Mode 1 dominates,
while higher modes stay small. The `a0 = 0.5` case transfers much more of its
shape into modes 3, 5, and 7. This harmonic generation is the nonlinear
effect requested in the email.

## Grid-sensitivity check

The calculation was repeated at 32, 64, and 128 cells per wavelength. The
table reports the change between the two finest grids:

| Case | Mode 1 | Mode 3 | Mode 5 | Mode 7 |
|---|---:|---:|---:|---:|
| `a0 = 0.1` | `0.090%` | `0.356%` | `2.14%` | `175%` |
| `a0 = 0.5` | `0.090%` | `0.083%` | `0.233%` | `0.059%` |

Modes 1, 3, 5, and 7 in the `a0 = 0.5` case are grid-independent to within
`0.24%`. This supports their interpretation as physical nonlinear
harmonics. Mode 7 in the `a0 = 0.1` case is extremely small and decreases
from `3.34e-4 a0` to `1.22e-4 a0` as the grid is refined. It is unresolved
numerical residue and should not be presented as a physical result.

Even modes remain near numerical zero. Equal fluid properties, zero gravity,
and the cosine initial condition preserve half-wave symmetry. That symmetry
cancels even harmonics. Odd-mode growth therefore indicates nonlinearity; the
absence of even modes does not indicate linear behaviour.

## How to read the figures

### `fourier-mode-evolution.png`

Each curve shows one Fourier mode against nondimensional time. Mode 1 falls
to zero whenever the standing wave passes through its flat position. In the
`a0 = 0.5` panel, modes 3, 5, and 7 rise far above their values in the
`a0 = 0.1` panel.

### `fourier-spectrum-heatmap.png`

Horizontal direction is time. Vertical direction is harmonic number. Colour
shows normalized magnitude on a logarithmic scale:

- Red: order `1`
- Brown/green: `10^-1` to `10^-2`
- Blue: `10^-3` or smaller

### `interface-evolution.png`

Curves show interface profiles every five nondimensional time units. The
larger-amplitude case starts much steeper and changes shape more strongly.

## Reproduce the study

Run from `/home/redacted/Desktop/projects/capwave-run`:

```bash
../basilisk/src/qcc -O2 -Wall nonlinear_fourier.c -o nonlinear_fourier -lm

./nonlinear_fourier 0.1 fourier-a0-0.1.dat profiles-a0-0.1.dat 128
./nonlinear_fourier 0.5 fourier-a0-0.5.dat profiles-a0-0.5.dat 128

python3 plot_nonlinear_fourier.py
python3 test_nonlinear_fourier.py
python3 test_plot_nonlinear_fourier.py
```

## Output files

- `nonlinear_fourier.c`: Basilisk simulation and Fourier calculation.
- `fourier-a0-0.1.dat`: Fourier coefficients for `a0 = 0.1`.
- `fourier-a0-0.5.dat`: Fourier coefficients for `a0 = 0.5`.
- `profiles-a0-0.1.dat`: interface snapshots for `a0 = 0.1`.
- `profiles-a0-0.5.dat`: interface snapshots for `a0 = 0.5`.
- `fourier-mode-evolution.png`: direct mode comparison.
- `fourier-spectrum-heatmap.png`: time-dependent Fourier spectrum.
- `interface-evolution.png`: interface-shape comparison.
- `fourier-grid-convergence.png`: peak harmonics at 32, 64, and 128 cells
  per wavelength.
- `fourier-a0-0.1-N64.dat` and `fourier-a0-0.5-N64.dat`: 32-cell results.
- `fourier-a0-0.1-N256.dat` and `fourier-a0-0.5-N256.dat`: 128-cell results.

Each Fourier data row contains:

```text
tau  harmonic  cosine  sine  magnitude  magnitude_over_a0
```

## Short explanation for discussion

> I kept the classical capillary-wave conditions fixed and increased only
> the initial amplitude from 0.1 to 0.5. I decomposed the evolving interface
> into eight Fourier modes. At 0.1, the first mode dominates and the response
> stays close to linear. At 0.5, modes 3, 5, and 7 become much stronger,
> showing nonlinear transfer from the original wavelength into higher spatial
> harmonics. Even modes remain negligible because this equal-fluid,
> zero-gravity case preserves half-wave symmetry.

## Current limitation

These results isolate amplitude-driven nonlinearity in the standard
capillary test. A later capillary-gravity study must add gravity and unequal
fluid densities as a separate comparison; those changes should not be mixed
into this amplitude-only result.
