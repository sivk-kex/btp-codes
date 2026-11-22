# Evidence ledger

This ledger limits report claims to results already generated in the project.

## Standing capillary-wave benchmark

- Source code: `capwave-run/capwave.c`, based on Basilisk `src/test/capwave.c`.
- Reference data: `capwave-run/prosperetti.h`.
- Conditions: two-dimensional `2 x 2` domain; wavelength `1`; initial amplitude `0.01`; surface tension `1`; equal densities `1`; equal viscosities `0.0182571749236`; gravity `0`.
- Resolution study: 8, 16, 32, and 64 cells per wavelength.
- Evidence files: `capwave-run/wave-16`, `wave-32`, `wave-64`, `wave-128`, and `capwave-run/capwave.log`.
- Figures: `capwave-run/capwave-amplitude-vs-time.png` and `capwave-run/capwave-rms-convergence.png`.
- Permitted interpretation: Basilisk reproduces damped small-amplitude oscillation and shows convergence toward Prosperetti's reference solution.
- Limit: this benchmark lies in the linear, pure-capillary regime.

## Gravity-wave benchmark

- Source: unchanged Basilisk `src/test/gravity.c`; reproduction notes in `gravity-run/GRAVITY_REPRODUCE.md`.
- Conditions: two-dimensional `2 x 2` domain; wavelength `1`; initial amplitude `0.01`; reduced gravity `G.y = 50`; densities `1` and `0.1`; viscosities `0.0182571749236`.
- Relative RMS errors at 8, 16, 32, and 64 cells per wavelength: `0.126713`, `0.031758`, `0.00807759`, and `0.00455815`.
- Observed refinement orders: about `2.00`, `1.98`, and `0.83`.
- Figures: `capwave-run/gravity-amplitude-vs-time.png` and `capwave-run/gravity-rms-convergence.png`.
- Permitted interpretation: first two refinement pairs show approximately second-order convergence; error reduction flattens at finest pair.
- Limit: gravity benchmark validates solver behaviour; it is separate from amplitude-driven nonlinear study.

## Literature-parameter reproductions

- Pan et al. case: `capwave-run/pan2024_capwave.c`, `pan2024-wave.dat`, and `pan2024-amplitude-vs-time.png`.
- Janodet et al. case: `capwave-run/janodet2024_capwave.c`, `janodet2024-wave.dat`, and `janodet2024-amplitude-vs-time.png`.
- Kayal et al. case: `capwave-run/kayal2022_wave.c`, `kayal2022-wave.dat`, `kayal2022-amplitude-vs-time.png`, and `KAYAL2022_REPRODUCE.md`.
- Permitted interpretation: selected published conditions were reproduced to test setup behaviour outside one standard benchmark.
- Limit: agreement quality must be stated only where project files quantify it; reproduction alone does not validate every physical regime.

## Initial-amplitude and Fourier study

- Source: `capwave-run/nonlinear_fourier.c` and `capwave-run/NONLINEAR_FOURIER_GUIDE.md`.
- Controlled variable: initial amplitude changes from `a0 = 0.1` to `a0 = 0.5`; fluid and numerical properties stay fixed.
- Fixed conditions: `2 x 2` domain; wavelength `1`; surface tension `1`; equal densities `1`; equal viscosities `0.0182571749236`; gravity `0`; maximum CFL `0.5`; final nondimensional time `25`.
- Main-grid result: `N = 128`, equal to 64 cells per wavelength.
- Maximum normalized odd harmonics:
  - `a0 = 0.1`: mode 3 = `2.09%`; mode 5 = `0.136%`; mode 7 = `0.0334%`.
  - `a0 = 0.5`: mode 3 = `19.75%`; mode 5 = `10.43%`; mode 7 = `6.91%`.
- Change between two finest grids for `a0 = 0.5`: mode 1 = `0.090%`, mode 3 = `0.083%`, mode 5 = `0.233%`, mode 7 = `0.059%`; therefore strong-mode variation is below `0.24%`.
- Small-amplitude mode 7 changes by `175%` and decreases on refinement. Treat it as unresolved numerical residue.
- Even modes remain near zero because equal fluid properties, zero gravity, and cosine initialization preserve half-wave symmetry.
- Figures: `fourier-mode-evolution.png`, `fourier-spectrum-heatmap.png`, `interface-evolution.png`, and `fourier-grid-convergence.png`.
- Permitted interpretation: larger initial amplitude generates stronger odd spatial harmonics, showing nonlinear wave-shape deformation.
- Limit: result isolates amplitude-driven nonlinearity; it does not yet combine gravity, unequal fluid properties, or three-dimensional effects.

## Travelling-wave extension

- Source: `capwave-run/travelling_wave.c`, `travelling-wave.dat`, and `TRAVELLING_WAVE_GUIDE.md`.
- Conditions: two-dimensional `2 x 2` domain; wavelength `1`; `N = 128`; initial amplitude `0.01`; surface tension `1`; gravity `0`; equal densities `1`; equal viscosities `0.0182571749236`.
- Initial condition: `eta(x,0) = 0.01 cos(2 pi x)` with phase-matched velocity-potential field for rightward propagation.
- Samples: `126`, covering nondimensional time `0` to `6.255`.
- Initial first-mode amplitude: `0.00998795`.
- Final unwrapped phase: `5.70890 rad`.
- Fitted phase rate and speed ratio: `0.90572` of inviscid linear theory.
- Final amplitude: `0.00495856`, equal to `49.65%` of initial amplitude.
- Phase increases at every stored time.
- Figures: `travelling-wave-amplitude.png` and `travelling-wave-phase.png`.
- Permitted interpretation: simulation produces rightward travelling behaviour rather than standing oscillation.
- Limit: viscosity and numerical discretization both contribute to speed difference and damping; this study does not separate them. Gravity, unequal properties, and large amplitude remain future cases.

## Research-gap wording

Use: established literature covers small-amplitude linear benchmarks and strongly nonlinear focusing or jetting, while this project examines the controlled transition in harmonic content as initial amplitude rises under one fixed two-fluid numerical setup.

Avoid: “nonlinear capillary waves have not been studied”, “first-ever”, “novel solver”, or any general novelty claim.

## AI disclosure

Exact scope approved by student: AI tools assisted with code drafting, report organization, and language editing. Do not list literature searching, data analysis, scientific interpretation, or figure generation as AI roles.

