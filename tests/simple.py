import pySAD as ad

def func(x=[], y=[], z=[], **kwargs):

    a = x+y*z
    if a<3:
        b = 1.0
    else:
        if x<0.5:
            b = ad.sin(a)
        else:
            b = ad.sqrt(z/x)
    c = ad.log(ad.exp(y)*ad.minimum(b,z))

    return [c]

if __name__=="__main__":

    tape = ad.AD_Tape()
    tape.compile(func)
    tape.write("tape", readable=True)
    print(tape.evaluate(inputs=[0.4, 2.0, 3.0]))
    print(func(x=0.4, y=2.0, z=3.0))
