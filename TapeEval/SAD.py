import ctypes as C
import numpy as np

def convertToCtypes(data):
    int_t = (int, np.int32, np.int64)
    float_t = (float, np.float32, np.float64)
    array_t = (np.ndarray)
    if isinstance(data, int_t):
        return C.c_int(data)
    if isinstance(data, float_t):
        return C.c_double(data)
    if isinstance(data, array_t):
        if isinstance(data.ravel()[0], int_t):
            return data.ctypes.data_as(C.POINTER(C.c_int))
        if isinstance(data.ravel()[0], float_t):
            return data.ctypes.data_as(C.POINTER(C.c_double))

def getCtypesType(data):
    int_t = (int, np.int32, np.int64)
    float_t = (float, np.float32, np.float64)
    array_t = (np.ndarray)
    if isinstance(data, int_t):
        return C.c_int
    if isinstance(data, float_t):
        return C.c_double
    if isinstance(data, array_t):
        if isinstance(data.ravel()[0], int_t):
            return C.POINTER(C.c_int)
        if isinstance(data.ravel()[0], float_t):
            return C.POINTER(C.c_double)

class SAD_Instruction(C.Structure):

    _fields_ = \
    [
        ("blockEnd",     C.c_int),
        ("operand1",     C.c_int),
        ("operand2",     C.c_int),
        ("operation",    C.c_int),
        ("value",     C.c_double),
        ("deriv",     C.c_double)
    ]

class SAD_Tape(C.Structure):

    _fields_ = \
    [
        ("effectiveTapeSize",               C.c_int),
        ("tapeSize",                        C.c_int),
        ("nInputs",                         C.c_int),
        ("nOutputs",                        C.c_int),
        ("jacobian",          C.POINTER(C.c_double)),
        ("instructions", C.POINTER(SAD_Instruction))
    ]

    def __init__(self, filename=None, subroutineName="evaluateTape"):
        
        self.alloc = False

        libSAD = C.CDLL("./libSAD.so")

        self.deleteTape = libSAD.__getattr__("deleteTape")
        self.deleteTape.restype = None
        self.deleteTape.argtypes = [SAD_Tape]

        self.readTapeFromFile = libSAD.__getattr__("readTapeFromFile")
        self.readTapeFromFile.restype = None
        self.readTapeFromFile.argtypes = [C.POINTER(SAD_Tape), C.c_char_p]
        
        self.evaluateTape = libSAD.__getattr__(subroutineName)
        self.evaluateTape.restype = None
        self.evaluateTape.argtypes = [SAD_Tape]

        if filename is not None: self.readFromFile(filename)

    def __del__(self):
        if self.alloc:
            self.deleteTape(self)

    def readFromFile(self, filename):
        self.readTapeFromFile(self, filename.encode())
        self.alloc = True

    def evaluate(self, *args, nScalarOutputs=None):
        
        if len(self.evaluateTape.argtypes)==1:
            for arg in args:
                self.evaluateTape.argtypes.append(getCtypesType(arg))
            if nScalarOutputs is not None:
                DP = C.POINTER(C.c_double)
                self.evaluateTape.argtypes.extend([DP for i in range(nScalarOutputs)])
        
        functionArgs = [self]
        for arg in args:
            functionArgs.append(convertToCtypes(arg))
        if nScalarOutputs is not None:
            outputs = [np.array([0.0]) for i in range(nScalarOutputs)]
            for i in range(nScalarOutputs):
                functionArgs.append(convertToCtypes(outputs[i]))

        #print(self.evaluateTape.argtypes)
        #print(functionArgs)
        
        self.evaluateTape(*functionArgs)
        
        if nScalarOutputs is not None:
            rtn = [float(outputs[i][0]) for i in range(nScalarOutputs)]
            return rtn
