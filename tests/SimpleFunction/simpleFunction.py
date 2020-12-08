import pySAD as sad

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
