
#include "grid/multigrid.h"
#include "navier-stokes/centered.h"
#if CLSVOF
# include "two-phase-clsvof.h"
# include "integral.h"
# include "curvature.h"
#else
# include "vof.h"
# include "tension.h"

scalar f[], * interfaces = {f};
#endif
#include "prosperetti.h"

#ifndef A0
# define A0 0.01
#endif


uf.n[left]   = 0.;
uf.n[right]  = 0.;
uf.n[top]    = 0.;
uf.n[bottom] = 0.;

double se = 0; int ne = 0;

int main() {
  size (2. [1]);
  Y0 = -L0/2.;
#if CLSVOF
  const scalar sigma[] = 1.;
  d.sigmaf = sigma;
#else
  f.sigma = 1.;
#endif
  TOLERANCE = 1e-6 [*];
  mu[] = {0.0182571749236, 0.0182571749236};
  for (N = 16; N <= 128; N *= 2) {
    se = 0, ne = 0;
    run();
  }
}
event init (t = 0) {
  double k = 2., a = A0;
#if CLSVOF
  foreach()
    d[] = y - a*cos (k*pi*x);
#else
  fraction (f, y - a*cos (k*pi*x));
#endif
}
event vof (i++, first);
event amplitude (t += 3.04290519077e-3; t <= 2.2426211256) {
  scalar pos[];
  position (f, pos, {0,1 [0]});
  double max = statsf(pos).max;
  char name[80];
  sprintf (name, "wave-%d", N);
  static FILE * fp = fopen (name, "w");
  fprintf (fp, "%g %g\n", t*11.1366559937, max);
  fflush (fp);
  se += sq(max - prosperetti[ne][1]); ne++;
}

event error (t = end)
  fprintf (stderr, "%g %g\n", N/L0, sqrt(se/ne)/0.01);

/**
## Results

~~~gnuplot Evolution of the amplitude of the capillary wave as a function of non-dimensional time $\tau=\omega_0 t$
set xlabel 'tau'
set ylabel 'Relative amplitude'
plot '../prosperetti.h' u 2:4 w l t "Prosperetti", \
     'wave-128' every 10 w p t "Basilisk", \
     '../capwave-clsvof/wave-128' every 10 w p t "Basilisk (CLSVOF)"
~~~

~~~gnuplot Convergence of the RMS error as a function of resolution (number of grid points per wavelength)
set xlabel 'Number of grid points'
set ylabel 'Relative RMS error'
set logscale y
set logscale x 2
set grid
plot [5:200][1e-4:1]\
     'log' t "Basilisk" w lp, 2./x**2 t "Second order", \
     '../capwave-clsvof/log' t "Basilisk (CLSVOF)" w lp, \
     2./x**2 t "Second order"
~~~
*/
