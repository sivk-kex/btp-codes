# Basilisk gravity-wave test reproduction

Source: `basilisk/src/test/gravity.c` (run unchanged).

## Case

- Two-phase reduced-gravity wave on a `2 x 2` constant-resolution domain.
- Initial interface: `y = 0.01 cos(2 pi x)`; wavelength `1`.
- `G.y = 50`, `rho1 = 1`, `rho2 = 0.1`.
- `mu1 = mu2 = 0.0182571749236`.
- Resolutions: `N = 16, 32, 64, 128`, corresponding to 8, 16, 32,
  and 64 grid points per wavelength.
- Prosperetti reference values come from
  `basilisk/src/test/prosperetti-gravity.h`.

## Run

```bash
cd /home/redacted/Desktop/projects
./basilisk/src/qcc -O2 -Wall basilisk/src/test/gravity.c -o gravity-run/gravity -lm
cd gravity-run
./gravity > gravity.facets 2> gravity.log
python3 plot_gravity.py
python3 test_gravity_reproduction.py
```

## Results

| Grid points per wavelength | Relative RMS error |
|---:|---:|
| 8 | 0.126713 |
| 16 | 0.031758 |
| 32 | 0.00807759 |
| 64 | 0.00455815 |

Observed orders over successive refinements are approximately `2.00`, `1.98`,
and `0.83`. First two refinements show expected second-order convergence;
finest pair shows error flattening also visible on Basilisk reference graph.

Generated graphs:

- `gravity-amplitude-vs-time.png`
- `gravity-rms-convergence.png`
