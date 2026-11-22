/** Linear travelling capillary wave. */

#include <errno.h>
#include <limits.h>

#include "grid/multigrid.h"
#include "navier-stokes/centered.h"
#include "vof.h"
#include "tension.h"

scalar f[], * interfaces = {f};

#define WAVENUMBER (2.*pi)
#define DEPTH 1.
#define OMEGA0 (sqrt(pow(WAVENUMBER, 3.)*tanh(WAVENUMBER*DEPTH)/2.))
#define TAU_END (2.*pi)

double initial_amplitude;
FILE * output_fp;
bool output_failed;

uf.n[top] = 0.;
uf.n[bottom] = 0.;

int write_diagnostics (double tau)
{
  double projected_cosine = 0., projected_sine = 0.;
  foreach (reduction(+:projected_cosine) reduction(+:projected_sine)) {
    double phase_area = f[]*sq(Delta);
    projected_cosine += phase_area*cos(WAVENUMBER*x);
    projected_sine += phase_area*sin(WAVENUMBER*x);
  }
  double cosine = -2.*projected_cosine/L0;
  double sine = -2.*projected_sine/L0;
  double magnitude = sqrt(sq(cosine) + sq(sine));
  double phase = atan2(sine, cosine);
  if (fabs(phase) < 1e-10)
    phase = 0.;
  double crest_x = phase >= 0. ? phase/WAVENUMBER :
    1. + phase/WAVENUMBER;
  if (fprintf (output_fp, "%.10g %.10g %.10g %.10g %.10g %.10g\n",
               tau, cosine, sine, magnitude, phase, crest_x) < 0 ||
      fflush (output_fp) != 0) {
    perror ("output file");
    output_failed = true;
    return 1;
  }
  return 0;
}

int main (int argc, char ** argv)
{
  if (argc != 4) {
    fprintf (stderr, "usage: %s A0 OUTPUT.dat N\n", argv[0]);
    return 2;
  }

  char * amplitude_end, * grid_end;
  errno = 0;
  initial_amplitude = strtod (argv[1], &amplitude_end);
  bool invalid_amplitude = errno || amplitude_end == argv[1] ||
    *amplitude_end != '\0' || !isfinite(initial_amplitude);
  errno = 0;
  long grid = strtol (argv[3], &grid_end, 10);
  bool invalid_grid = errno || grid_end == argv[3] || *grid_end != '\0' ||
    grid > INT_MAX;
  if (invalid_amplitude || invalid_grid ||
      !(initial_amplitude > 0. && initial_amplitude <= 0.05) ||
      grid < 32 || (grid & (grid - 1))) {
    fprintf (stderr,
             "invalid input: require 0 < A0 <= 0.05 and power-of-two N >= 32\n");
    return 2;
  }
  N = grid;

  output_fp = fopen (argv[2], "w");
  if (!output_fp) {
    perror ("output file");
    return 2;
  }
  fprintf (output_fp, "# tau cosine sine magnitude phase crest_x\n");
  fprintf (output_fp,
           "# A0=%.10g N=%d wavelength=1 sigma=1 rho1=rho2=1 "
           "mu1=mu2=0.0182571749236 gravity=0 omega=%.10g\n",
           initial_amplitude, N, OMEGA0);
  size (2.);
  Y0 = -L0/2.;
  periodic (right);
  f.sigma = 1.;
  mu[] = {0.0182571749236, 0.0182571749236};
  CFL = 0.5;
  TOLERANCE = 1e-6 [*];
  run();

  if (fclose (output_fp) != 0 && !output_failed) {
    perror ("output file");
    output_failed = true;
  }
  if (output_failed)
    return 2;
  return 0;
}

event init (t = 0)
{
  fraction (f, y - initial_amplitude*cos(WAVENUMBER*x));

  double potential = initial_amplitude*OMEGA0/
    (WAVENUMBER*tanh(WAVENUMBER*DEPTH));
  foreach() {
    if (y <= 0.) {
      double vertical = WAVENUMBER*(y + DEPTH);
      u.x[] = potential*WAVENUMBER*cosh(vertical)/
        cosh(WAVENUMBER*DEPTH)*cos(WAVENUMBER*x);
      u.y[] = potential*WAVENUMBER*sinh(vertical)/
        cosh(WAVENUMBER*DEPTH)*sin(WAVENUMBER*x);
    }
    else {
      double vertical = WAVENUMBER*(DEPTH - y);
      u.x[] = -potential*WAVENUMBER*cosh(vertical)/
        cosh(WAVENUMBER*DEPTH)*cos(WAVENUMBER*x);
      u.y[] = potential*WAVENUMBER*sinh(vertical)/
        cosh(WAVENUMBER*DEPTH)*sin(WAVENUMBER*x);
    }
  }
  boundary ((scalar *){u});
  if (write_diagnostics (0.))
    return 1;
}

event vof (i++, first);

event diagnostics (t = 0.05/OMEGA0; t += 0.05/OMEGA0;
                   t <= TAU_END/OMEGA0)
{
  return write_diagnostics (OMEGA0*(t + dt/2.));
}

event stop (t = TAU_END/OMEGA0)
{
  return 1;
}
