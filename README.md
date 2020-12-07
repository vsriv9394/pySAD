# Introduction

pySAD is a python-based framework to create algorithmic tapes for use in C/C++
subroutines. To prevent the tape from being too heavy on memory, one can create
a tape for subroutines to be called iteratively.

# Tutorial

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
`ad.exp` or `ad.log`). The currently supported functions are:
`abs`, `exp`, `log`, `sqrt`, `maximum` (only for scalars),
`minimum` (only for scalars), `sin`, `cos`, `tan`, `sinh`, `cosh`, `tanh`,
`dot`, `cross` (only for 2D or 3D vectors) and `matmul`

Let us create a function now:
```
def simpleFunction(x=[], y=[], z=[], **kwargs):
  a = x*y+z/ad.exp(x*y)
```
