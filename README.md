# Introduction

pySAD is a python-based framework to create algorithmic tapes for use in C/C++
subroutines. To prevent the tape from being too heavy on memory, one can create
a tape for subroutines to be called iteratively.

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
  b = a - sad.sqrt(x*y/z)
  return [b]
```

Finally, to create the tape, create an `AD_Tape` object, compile the function,
and write the tape as follows:
```
tape = sad.AD_Tape()
tape.compile(simpleFunction, kwargs={})
tape.write('tape.txt', readable=True)
```

The `readable` flag in the `tape.write` subroutine is used to represent the
operators/functions as strings instead of numerical ids in the tape file.

This creates the following tape file:
```
```
