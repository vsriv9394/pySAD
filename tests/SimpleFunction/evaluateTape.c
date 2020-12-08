#include "SAD.h"
#include <stdio.h>

#ifdef __cplusplus
extern "C"
{
#endif
  void evaluateTape(SAD_Tape tape, double x, double y, double z, double *jac_b, double *b)
  {
    setTapeInput(tape, 0, x);
    setTapeInput(tape, 1, y);
    setTapeInput(tape, 2, z);

    evaluateTapeOutputsAndJacobian(&tape);

    b[0]    = getTapeOutput(tape, 0);
    jac_b[0] = getTapeJacobian(tape, 0, 0);
    jac_b[1] = getTapeJacobian(tape, 0, 1);
    jac_b[2] = getTapeJacobian(tape, 0, 2);
  }
#ifdef __clpusplus
}
#endif
