#include "SAD.h"
#include <stdio.h>

#ifdef __cplusplus
extern "C"
{
#endif
  void evaluateTape(SAD_Tape tape, double x, double y, double z, double *b, double *dbdx, double *dbdy)
  {
    setTapeInput(tape, 0, x);
    setTapeInput(tape, 1, y);
    setTapeInput(tape, 2, z);

    evaluateTapeOutputsAndJacobian(&tape);

    b[0]    = getTapeOutput(tape, 0);
    dbdx[0] = getTapeJacobian(tape, 0, 0);
    dbdy[0] = getTapeJacobian(tape, 0, 1);
  }
#ifdef __clpusplus
}
#endif
