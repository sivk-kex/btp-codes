/** Fourier evolution of finite-amplitude capillary waves. */

#include "grid/multigrid.h"
#include "navier-stokes/centered.h"
#include "vof.h"
#include "tension.h"

scalar f[], * interfaces = {f};

#define OMEGA0 11.1366559937
#define MODE_COUNT 8
#ifndef TAU_END
# define TAU_END 25.
#endif

double initial_amplitude;
FILE * spectrum_fp, * profile_fp;
// Boundary conditions.
uf.n[left]   = 0.;
uf.n[right]  = 0.;
uf.n[top]    = 0.;
uf.n[bottom] = 0.;

int main (int argc, char ** argv)
{
  if (argc != 5) {
    fprintf (stderr,
             "usage: %s A0 FOURIER.dat PROFILES.dat N\n", argv[0]);
    return 2;
  }

  initial_amplitude = atof (argv[1]);
  N = atoi (argv[4]);
  if (!(initial_amplitude > 0. && initial_amplitude < 1.) ||
      N < 32 || (N & (N - 1))) {
    fprintf (stderr,
             "invalid input: require 0 < A0 < 1 and power-of-two N >= 32\n");
    return 2;
  }

  size (2.);
  Y0 = -L0/2.;

  spectrum_fp = fopen (argv[2], "w");
  profile_fp = fopen (argv[3], "w");
  if (!spectrum_fp || !profile_fp) {
    perror ("output file");
    return 2;
  }

  fprintf (spectrum_fp,
           "# tau harmonic cosine sine magnitude magnitude_over_a0\n");
  fprintf (spectrum_fp,
           "# A0=%.10g N=%d cells_per_wavelength=%g sigma=1 rho1=rho2=1 "
           "mu1=mu2=0.0182571749236 gravity=0\n",
           initial_amplitude, N, N/L0);
  f.sigma = 1.;
  mu[] = {0.0182571749236, 0.0182571749236};
  CFL = 0.5;
  TOLERANCE = 1e-6 [*];
  run();

  fclose (spectrum_fp);
  fclose (profile_fp);
}

event init (t = 0)
{
  double wavenumber = 2.*pi;
  fraction (f, y - initial_amplitude*cos(wavenumber*x));
}

event vof (i++, first);

/**
For non-zero harmonics, vertically integrated VOF fraction is equivalent
to interface height, apart from sign. This remains defined if interface
temporarily stops being single-valued.
*/
event spectrum (t = 0; t += 0.05/OMEGA0; t <= TAU_END/OMEGA0)
{
  double wavenumber = 2.*pi;
  for (int harmonic = 1; harmonic <= MODE_COUNT; harmonic++) {
    double projected_cosine = 0., projected_sine = 0.;
    foreach (reduction(+:projected_cosine) reduction(+:projected_sine)) {
      double phase_area = f[]*sq(Delta);
      projected_cosine += phase_area*cos(wavenumber*harmonic*x);
      projected_sine += phase_area*sin(wavenumber*harmonic*x);
    }

    double cosine = -2.*projected_cosine/L0;
    double sine = 2.*projected_sine/L0;
    double magnitude = sqrt(sq(cosine) + sq(sine));
    fprintf (spectrum_fp, "%.10g %d %.10g %.10g %.10g %.10g\n",
             OMEGA0*t, harmonic, cosine, sine, magnitude,
             magnitude/initial_amplitude);
  }
  fputc ('\n', spectrum_fp);
  fflush (spectrum_fp);
}

event profiles (t = 0; t += 5./OMEGA0; t <= TAU_END/OMEGA0)
{
  fprintf (profile_fp, "# frame %.10g time %.10g\n", OMEGA0*t, t);
  output_facets (f, profile_fp);
  fprintf (profile_fp, "# end\n");
  fflush (profile_fp);
}

event stop (t = TAU_END/OMEGA0)
{
  return 1;
}
