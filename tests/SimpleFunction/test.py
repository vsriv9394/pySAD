import pySAD as sad
import numpy as np
from simpleFunction import simpleFunction

# Tape creation

tape = sad.AD_Tape()
tape.compile(simpleFunction, kwargs={})
tape.write("tape.txt", readable=False)

b = simpleFunction(x=0.4, y=2.0, z=-3.0)

print(tape.evaluate(inputs=[0.4, 2.0, -3.0]))
print(b[0])

# Tape evaluation using C

jac_b = np.zeros((1,3))
tape = sad.AD_EvalTape(filename="tape.txt",  libName="./libSAD.so", subroutineName="evaluateTape")
b = tape.evaluate(0.4, 2.0, -3.0, jac_b, nScalarOutputs=1)
print(b)
print(jac_b)

# Derivative verification

b1 = simpleFunction(x=0.4+1e-6, y=2.0, z=-3.0)
print((b1[0]-b[0])/1e-6)

b1 = simpleFunction(x=0.4, y=2.0+1e-6, z=-3.0)
print((b1[0]-b[0])/1e-6)

b1 = simpleFunction(x=0.4, y=2.0, z=-3.0+1e-6)
print((b1[0]-b[0])/1e-6)
