# Kayal et al. (2022), Figure 4(b) reproduction

Target: L. Kayal, S. Basak, and R. Dasgupta, “Dimples, jets and
self-similarity in nonlinear capillary waves,” *Journal of Fluid Mechanics*,
vol. 951, A26, 2022. DOI: https://doi.org/10.1017/jfm.2022.854
(peer reviewed, open access).

## Model

- Axisymmetric, incompressible two-phase Basilisk simulation.
- Surface tension and inertia only; gravity and viscosity are zero.
- Container radius `R0 = 1`; radial mode `l15 = 47.9`.
- Initial interface `eta(r,0) = a0 J0(l15 r)`, with
  `a0 = epsilon/l15` and `epsilon = 1.8`.
- Quiescent initial velocity.
- Paper nondimensionalisation:
  `t = sqrt(sigma*l15^3/(rho*R0^3))*t_hat` and
  `eta(0,t)/epsilon = eta_hat(0,t)/a0`.

Paper does not report simulation grid, gas density, AMR tolerances, or finite
depth. Reproduction uses maximum quadtree level 9, liquid/gas density ratio
1000, depth `0.5 R0`, gas height `0.5 R0`, and 67 finest cells per initial
wavelength. These choices reproduce Figure 4(b)’s time-signal landmarks but
do not claim bitwise reproduction of authors' unpublished setup.

## Run

From `/home/redacted/Desktop/projects/capwave-run`:

```bash
../basilisk/src/qcc -O2 -Wall kayal2022_wave.c -o kayal2022_wave -lm
./kayal2022_wave 9 > kayal2022-wave.dat 2> kayal2022.log
python3 test_kayal2022.py
python3 plot_kayal2022_amplitude.py
```

Data columns are nondimensional time, dimensional solver time, and normalized
centre amplitude.

## Result

- Initial normalized amplitude: `0.99891`.
- Minimum: `-1.14127` at `t = 4.04`.
- Rebound maximum: `1.08104` at `t = 7.38`.
- Level-8 check: minimum `-1.11908` at `t = 4.12` (about 2% amplitude change).

Published Figure 4(b) shows corresponding minimum near `-1.1` around `t = 4`
and rebound slightly above `1` around `t = 7.5`.
