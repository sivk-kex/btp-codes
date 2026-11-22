
#include "grid/multigrid.h"
#include "navier-stokes/centered.h"
#define FILTERED 1
#include "two-phase.h"
#include "tension.h"

#define WAVELENGTH (2.*pi)
#define SIGMA 2.
#define OMEGA0 (sqrt(SIGMA/(1000. + 1.)))

uf.n[top] = 0.;
uf.n[bottom] = 0.;

int main()
{
  dimensions (1, 3);
  size (WAVELENGTH);
  Y0 = -1.5*WAVELENGTH;
  periodic (right);
  N = 64;

  rho1 = 1000.;
  rho2 = 1.;
  mu1 = sqrt(rho1*SIGMA*WAVELENGTH/300.);
  mu2 = mu1/1000.;
  f.sigma = SIGMA;

  CFL = 0.5;
  TOLERANCE = 1e-7 [*];
  run();
}

event init (t = 0)
{
  fraction (f, WAVELENGTH/100.*cos(x) - y);
}

event vof (i++, first);

event amplitude (t += 0.05/OMEGA0; t <= 25./OMEGA0)
{
  scalar position_y[];
  position (f, position_y, {0, 1 [0]});

  double projection = 0.;
  foreach (reduction(+:projection))
    if (position_y[] != nodata)
      projection += position_y[]*cos(x)*Delta;

  double amplitude = 2.*projection/WAVELENGTH;
  fprintf (stdout, "%.10g %.10g %.10g %.10g\n",
           t, OMEGA0*t, amplitude, amplitude/(WAVELENGTH/100.));
}
