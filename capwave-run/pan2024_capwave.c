/** Reproduction of Pan et al., JCP 508 (2024) 113016, Fig. 23. */

#include "grid/multigrid.h"
#include "navier-stokes/centered.h"
#include "vof.h"
#include "tension.h"
#include "prosperetti.h"

scalar f[], * interfaces = {f};

uf.n[left]   = 0.;
uf.n[right]  = 0.;
uf.n[top]    = 0.;
uf.n[bottom] = 0.;

double squared_error = 0.;
int samples = 0;

int main()
{
  dimensions (1, 4);
  size (1.);
  Y0 = -2.;
  N = 64;
  f.sigma = 1.;
  mu[] = {0.0182571749236, 0.0182571749236};
  CFL = 0.5;
  TOLERANCE = 1e-6 [*];
  run();
}

event init (t = 0)
{
  fraction (f, y - 0.01*cos(2.*pi*x));
}

event vof (i++, first);

event amplitude (t += 3.04290519077e-3; t <= 2.2426211256)
{
  scalar position_y[];
  position (f, position_y, {0, 1 [0]});
  double amplitude = statsf(position_y).max;
  double tau = t*11.1366559937;
  fprintf (stdout, "%.8g %.8g %.8g\n",
           tau, amplitude/0.01, prosperetti[samples][1]/0.01);
  squared_error += sq(amplitude - prosperetti[samples][1]);
  samples++;
}

event report (t = end)
  fprintf (stderr, "samples=%d relative_RMS_error=%.8g\n",
           samples, sqrt(squared_error/samples)/0.01);
