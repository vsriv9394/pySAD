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
tape.write("tape.txt", readable=True)
```

The `readable` flag in the `tape.write` subroutine is used to represent the
operators/functions as strings instead of numerical ids in the tape file.

This creates the following `tape.txt` file:
```
1   3 1 32
2          -1        -1        -1 CONST 0.000000000000000e+00
3          -1        -1        -1 CONST 0.000000000000000e+00
4          -1        -1        -1 CONST 0.000000000000000e+00
5          -1        -1        -1 CONST 1.000000000000000e+00
6          14         0         3  IFGT 0.000000000000000e+00
7          -1         0         1   MUL 0.000000000000000e+00
8          -1         1         2   MUL 0.000000000000000e+00
9          -1         5        -1   EXP 0.000000000000000e+00
10         -1         6         7   DIV 0.000000000000000e+00
11         -1         5         8   ADD 0.000000000000000e+00
12         -1         5         2   DIV 0.000000000000000e+00
13         -1        10        -1  SQRT 0.000000000000000e+00
14         -1         9        11   SUB 0.000000000000000e+00
15         -1        12         3   MUL 0.000000000000000e+00
16         32         0         3  IFLE 0.000000000000000e+00
17         -1        -1        -1 CONST 0.000000000000000e+00
18         24         2        15  IFGT 0.000000000000000e+00
19         -1         0         1   MUL 0.000000000000000e+00
20         -1        17        -1   EXP 0.000000000000000e+00
21         -1         2        18   DIV 0.000000000000000e+00
22         -1        17         2   DIV 0.000000000000000e+00
23         -1        20        -1  SQRT 0.000000000000000e+00
24         -1        19        21   SUB 0.000000000000000e+00
25         -1        22         3   MUL 0.000000000000000e+00
26         -1        -1        -1 CONST 0.000000000000000e+00
27         32         2        24  IFLE 0.000000000000000e+00
28         -1         0         1   MUL 0.000000000000000e+00
29         -1        26         2   MUL 0.000000000000000e+00
30         -1        26         2   DIV 0.000000000000000e+00
31         -1        28        -1  SQRT 0.000000000000000e+00
32         -1        27        29   SUB 0.000000000000000e+00
33         -1        30         3   MUL 0.000000000000000e+00
```
