import pySAD as sad
from simpleFunction import simpleFunction

# Tape creation

tape = sad.AD_Tape()
tape.compile(simpleFunction, kwargs={})
tape.write("tape.txt", readable=False)

b = simpleFunction(x=0.4, y=2.0, z=-3.0)

print(tape.evaluate(inputs=[0.4, 2.0, -3.0]))
print(b[0])

# Tape evaluation using C

tape = sad.AD_EvalTape(filename="tape.txt")
out = tape.evaluate(0.4, 2.0, -3.0, nScalarOutputs=3)
print(out)

# Derivative verification

b1 = simpleFunction(x=0.4+1e-6, y=2.0, z=-3.0)
print((b1[0]-b[0])/1e-6)

b1 = simpleFunction(x=0.4, y=2.0+1e-6, z=-3.0)
print((b1[0]-b[0])/1e-6)
