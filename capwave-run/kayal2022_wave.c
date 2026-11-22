

#include "axi.h"
#include "navier-stokes/centered.h"
#define FILTERED 1
#include "two-phase.h"
#include "tension.h"

#define LQ 47.9
#define EPSILON 1.8
#define ETA0 (EPSILON/LQ)
#define OMEGA (sqrt(cube(LQ)))

int LEVEL = 10;

static double initial_surface (double r)
{
  return ETA0*j0(LQ*r);
}

int main (int argc, char ** argv)
{
  if (argc > 1)
    LEVEL = atoi (argv[1]);

  size (1.);
  origin (-0.5, 0.);
  init_grid (64);

  rho1 = 1.;
  rho2 = 1e-3;
  mu1 = mu2 = 0.;
  f.sigma = 1.;

  CFL = 0.25;
  TOLERANCE = 1e-7 [*];
  run();
}

event init (t = 0)
{
  refine (fabs(x - initial_surface(y)) < 4.*Delta && level < LEVEL);
  fraction (f, initial_surface(y) - x);
}

event vof (i++, first);

event amplitude (t = 0; t += 0.02/OMEGA; t <= 9.3/OMEGA)
{
  scalar xpos[];
  position (f, xpos, {1., 0.});

  double ymin = HUGE;
  foreach (reduction(min:ymin))
    if (xpos[] != nodata)
      ymin = min (ymin, y);

  double eta = 0., samples = 0.;
  foreach (reduction(+:eta) reduction(+:samples))
    if (xpos[] != nodata && y <= ymin + 1e-12) {
      eta += xpos[];
      samples++;
    }

  if (samples > 0.)
    fprintf (stdout, "%.10g %.10g %.10g\n", OMEGA*t, t, eta/samples/ETA0);
  fflush (stdout);
}

event adapt (i++)
{
  adapt_wavelet ({f, u}, (double[]){1e-4, 2e-3, 2e-3}, LEVEL, 6);
}
