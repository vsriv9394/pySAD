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
