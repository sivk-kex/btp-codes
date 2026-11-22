# Nonlinear Effects on Capillary-Gravity Waves

Code, simulation data, plots, tests, and report artifacts for Aditya Mazumdar's CHP-400A B.Tech. project at IIT Roorkee. Work uses Basilisk to validate capillary and gravity-wave benchmarks, quantify amplitude-dependent harmonic generation, and test a right-travelling capillary wave.

## Repository contents

| Path | Contents |
|---|---|
| `capwave-run/` | Basilisk capillary-wave sources, raw outputs, Fourier and travelling-wave studies, plots, tests, and reproduction guides |
| `capwave-run/raw_data_Janodet_et_al_2024/` | Reference data used for the Janodet comparison |
| `gravity-run/` | Reduced-gravity benchmark source, outputs, plotting script, test, and reproduction guide |
| `btp-autumn-ete-report/` | Report builder, checks, evidence notes, bibliography, final DOCX, and final PDF |

Compiled executables, Python caches, temporary compiler directories, superseded truncated data, and large intermediate render files are intentionally excluded. All source code and data needed for reported results are included.

## Main reported studies

- Standard capillary-wave comparison with Prosperetti reference data.
- Reduced-gravity benchmark at 8, 16, 32, and 64 cells per wavelength.
- Standing-wave Fourier comparison for initial amplitudes `a0 = 0.1` and `a0 = 0.5`.
- Grid-sensitivity study at 32, 64, and 128 cells per wavelength.
- Pan, Janodet, and Kayal literature-parameter checks.
- Small-amplitude right-travelling capillary-wave validation.

Main `a0 = 0.5`, `N = 128` Fourier archive contains 500 stored times through `tau = 24.95` and six interface-profile frames. Peak normalized magnitudes for modes 3, 5, and 7 are approximately `19.75%`, `10.43%`, and `6.91%`.

## Requirements

- Basilisk source tree with `qcc`
- C compiler and standard math library
- Python 3
- Ghostscript and groff only when rebuilding report PDF

No third-party Python package is required.

Tests expect Basilisk at `basilisk/` in repository root. Point that path to an existing Basilisk source tree:

```bash
ln -s /absolute/path/to/basilisk basilisk
```

## Reproduce simulations

Run commands from `capwave-run/` unless guide says otherwise.

```bash
../basilisk/src/qcc -O2 -Wall nonlinear_fourier.c -o nonlinear_fourier -lm
./nonlinear_fourier 0.1 fourier-a0-0.1.dat profiles-a0-0.1.dat 128
./nonlinear_fourier 0.5 fourier-a0-0.5.dat profiles-a0-0.5.dat 128
python3 plot_nonlinear_fourier.py
python3 -m unittest discover -v
```

Detailed assumptions and commands:

- [`capwave-run/NONLINEAR_FOURIER_GUIDE.md`](capwave-run/NONLINEAR_FOURIER_GUIDE.md)
- [`capwave-run/TRAVELLING_WAVE_GUIDE.md`](capwave-run/TRAVELLING_WAVE_GUIDE.md)
- [`capwave-run/KAYAL2022_REPRODUCE.md`](capwave-run/KAYAL2022_REPRODUCE.md)
- [`gravity-run/GRAVITY_REPRODUCE.md`](gravity-run/GRAVITY_REPRODUCE.md)

Rebuild report artifacts with:

```bash
python3 btp-autumn-ete-report/build_report.py
python3 btp-autumn-ete-report/render_pdf.py
python3 -m unittest discover -s btp-autumn-ete-report -p 'test_*.py' -v
```

## Report

- [Final PDF](btp-autumn-ete-report/output/Aditya_Mazumdar_CHP400A_Autumn_ETE_Report_2026.pdf)
- [Editable DOCX](btp-autumn-ete-report/output/Aditya_Mazumdar_CHP400A_Autumn_ETE_Report_2026.docx)
- [Quality checks](btp-autumn-ete-report/QA.md)

Report source expects department declaration template outside this repository. Final DOCX and PDF are included so committee review does not require rebuilding them.
