# Tape creation (Python)

We believe that there is nothing better than examples to learn the use of any
software package. So here are a few examples which demonstrate how to use the
package. We strongly recommend you to read these.

## Example 1: A simple function

To import the pySAD framework, add the pySAD directory to your `PYTHONPATH`
environment variable and add the following import command in the beginning
of the python file you intend to create your tape from.
```
import pySAD as sad
```
Next, you need to add the subroutine you wish to create a tape for. While doing
this, you need to take care of a few things:
- Add an explicit `**kwargs` parameter in the end
- For all parameters add default argument values (`[]` for a scalar, `[m,n,...]`
for an ndarray)
- Add any function (like `exp` or `log`) with module name `ad` (i.e.
`sad.exp` or `sad.log`). The currently supported functions are:
`abs`, `exp`, `log`, `sqrt`, `maximum` (only for scalars),
`minimum` (only for scalars), `sin`, `cos`, `tan`, `sinh`, `cosh`, `tanh`,
`dot`, `cross` (only for 2D or 3D vectors) and `matmul`
- All outputs must be returned contained in a single list
- Some array manipulation functions (`resize`, `ravel` and indexing) also work
- Though not absolutely necessary, it is highly recommended to use conditional
statements only in `if` or `elif` commands. Also, when comparing a sad variable
with a normal variable (i.e. an `int` or a `float`), the first argument of the
conditional should always be the sad variable.
- It is also recommended that you place all binary operations (`+,-,*,/,**`)
inside parenthesis for the most efficient tape compilation. One can choose not
to do this though.

Let us create a function now:
```
def simpleFunction(x=[], y=[], z=[], **kwargs):
    if x>1.0:
        a = x*y + y*z/sad.exp(x*y)
    else:
        if z>0.0:
            a = z/sad.exp(x*y)
        else:
            a = x*y*z
    b = a - sad.exp(x*y/z)
    return [b]
```

Finally, to create the tape, create an `AD_Tape` object, compile the function,
and write the tape as follows:
```
tape = sad.AD_Tape()
tape.compile(simpleFunction, kwargs={})
tape.write("tape.txt", readable=True)
```

The `readable` flag in the `tape.write` subroutine is used to represent the
operators/functions as strings instead of numerical ids in the tape file.

This creates the following `tape.txt` file (with line numbers):
```
  1 3 1 36
  2        -1        -1        -1 CONST 0.000000000000000e+00
  3        -1        -1        -1 CONST 0.000000000000000e+00
  4        -1        -1        -1 CONST 0.000000000000000e+00
  5        -1        -1        -1 CONST 1.000000000000000e+00
  6        14         0         3  IFGT 0.000000000000000e+00
  7        -1         0         1   MUL 0.000000000000000e+00
  8        -1         1         2   MUL 0.000000000000000e+00
  9        -1         5        -1   EXP 0.000000000000000e+00
 10        -1         6         7   DIV 0.000000000000000e+00
 11        -1         5         8   ADD 0.000000000000000e+00
 12        -1         5         2   DIV 0.000000000000000e+00
 13        -1        10        -1   EXP 0.000000000000000e+00
 14        -1         9        11   SUB 0.000000000000000e+00
 15        -1        12         3   MUL 0.000000000000000e+00
 16         4        -1        -1 IFEND 0.000000000000000e+00
 17        34         0         3  IFLE 0.000000000000000e+00
 18        -1        -1        -1 CONST 0.000000000000000e+00
 19        25         2        16  IFGT 0.000000000000000e+00
 20        -1         0         1   MUL 0.000000000000000e+00
 21        -1        18        -1   EXP 0.000000000000000e+00
 22        -1         2        19   DIV 0.000000000000000e+00
 23        -1        18         2   DIV 0.000000000000000e+00
 24        -1        21        -1   EXP 0.000000000000000e+00
 25        -1        20        22   SUB 0.000000000000000e+00
 26        -1        23         3   MUL 0.000000000000000e+00
 27        17        -1        -1 IFEND 0.000000000000000e+00
 28        -1        -1        -1 CONST 0.000000000000000e+00
 29        34         2        26  IFLE 0.000000000000000e+00
 30        -1         0         1   MUL 0.000000000000000e+00
 31        -1        28         2   MUL 0.000000000000000e+00
 32        -1        28         2   DIV 0.000000000000000e+00
 33        -1        30        -1   EXP 0.000000000000000e+00
 34        -1        29        31   SUB 0.000000000000000e+00
 35        -1        32         3   MUL 0.000000000000000e+00
 36        27        -1        -1 IFEND 0.000000000000000e+00
 37        15        -1        -1 IFEND 0.000000000000000e+00
```

Notice that the outputs (in this case, the single output) is located right
above the `IFEND` operations. Also, note that to force these outputs at the
end of the `if` blocks,  they have been multiplied with instruction 3 (line 5)
which is a constant 1.0. Also, note how quantities are reused:
- Any non-zero constants are declared only once inside a conditional block no
matter how many times they are used inside the code (for example, the constant
1 mentioned above is recycled for all its uses in the function)
- Any function evaluations that have been previously performed are not repeated
in the tape, e.g. `x*y` evaluated in line 7 has been re-used in line 9, even
though we have `exp(x*y)` mentioned in the code and the natural behaviour would
have been to recalculate. This is really useful, because it takes away the added
effort needed to optimize the code. It is here, that using parentheses around
all binary operations remove any and all redundancies and make the code as
efficient as it can be.

In addition to this, the framework is numpy compatible, i.e. to run any unit
tests while code development, you don't need to redefine this function using
numpy to test if it is working correctly. Rather, just call it by passing
`float` and `numpy.ndarray` as argument values and it just works! For example,
to evaluate the above function for argument values `x=0.4, y=2.0, z=-3.0` just
call:
```
simpleFunction(x=0.4, y=2.0, z=-3.0)
```
and it should return
```
[-3.1659283383646493]
```

## Example 2: A neural network

Although, this framework was create with physical problems in mind, we can also
create a neural network just as simply, as follows. This should be self-explanatory.
Note how any function compiled using pySAD can call a child function just as
naturally as in any other python framework.
```
import pySAD as sad
import numpy as np

''' 
Number of nodes in each layer in the NN
'''

nNodes = np.array([3, 7, 7, 1])

'''
prev: 1-D array containing previous node values
weights: 2-D array containing weights
biases: 1-D array containing biases
'''

def calcLayerNN(prev, weights, biases):

    curr = sad.matmul(weights, prev) + biases
    curr = curr / (1.0 + sad.exp(-curr))
    return curr

'''
inputs: 1-D array of features
theta: Parameter vector containing all weights and biases
'''

def calcNN(inputs=[nNodes[0]], theta=[sum(nNodes[1:]+sum(nNodes[:-1]*nNodes[1:]))], **kwargs):

    beg = 0

    nodes = inputs

    for i in range(len(nNodes)-1):

        biases = theta[beg:beg+nNodes[i+1]]
        beg += nNodes[i+1]

        weights = theta[beg:beg+nNodes[i+1]*nNodes[i]]
        weights.resize((nNodes[i+1], nNodes[i]))
        beg += nNodes[i+1]*nNodes[i]

        nodes = calcLayerNN(nodes, weights, biases)

    return [nodes]

tape = sad.AD_Tape()
tape.compile(calcNN, kwargs={})
tape.write("nnTape.txt", readable=True)
```

# Tape Evaluation

Now, the tape so obtained can be used to evaluate outputs and jacobians. This
can be done in any language, but C/C++ is chosen for its speed and convenience.
Also, pure C subroutines can be easily ported to almost any other language, which
makes things even better. A python wrapper for the same has also been provided.

Here is an example to show how this is done.

## Example: "The" simple function

Copy or link the header file `pySAD/TapeEval/SAD.h` in the working directory.
Then, a file containing C-subroutines can be written as follows.

```
#include "SAD.h"
#include <stdio.h>

#ifdef __cplusplus
extern "C"
{
#endif
  void evaluateTape(SAD_Tape tape, double x, double y, double z, double *b, double *dbdx, double *dbdy, double *dbdz)
  {
    setTapeInput(tape, 0, x);
    setTapeInput(tape, 1, y);
    setTapeInput(tape, 2, z);

    evaluateTapeOutputsAndJacobian(&tape);

    b[0]    = getTapeOutput(tape, 0);
    dbdx[0] = getTapeJacobian(tape, 0, 0);
    dbdy[0] = getTapeJacobian(tape, 0, 1);
    dbdz[0] = getTapeJacobian(tape, 0, 2);
  }
#ifdef __clpusplus
}
#endif
```
