import pySAD as sad

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
    
tape = sad.AD_Tape()
tape.compile(simpleFunction, kwargs={})
tape.write("tape.txt", readable=True)

#print(tape.evaluate(inputs=[0.4, 2.0, 3.0]))
#print(func(x=0.4, y=2.0, z=3.0))
