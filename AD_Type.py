import sys
import numpy as np

#------------------------------------------------------------------------------
# Tuples to check whether objects are instances of numeric or array types
#------------------------------------------------------------------------------
scalar_t = (int, float, np.int32, np.int64, np.uint32, np.uint64, np.float32, np.float64)
array_t = (np.ndarray)

#------------------------------------------------------------------------------
# Create an explicit type conversion to convert into AD_Type
#------------------------------------------------------------------------------
def AD(tape, var):

    # Numeric data

    if isinstance(var, scalar_t):
        return AD_Type(tape, data=AD_Scalar(tape, value=float(var)))
    
    # Array data

    if isinstance(var, array_t):
        
        varR = var.ravel()

        # Numeric data inside array
        
        if isinstance(varR[0], scalar_t):

            # Copy contents to AD_Scalar type array and assign to AD_Type
            
            rtn = np.empty_like(var, dtype=AD_Scalar)
            rtnR = rtn.ravel()

            for i in range(varR.size):
                
                rtnR[i] = AD_Scalar(tape, value=float(varR[i]))
            
            return AD_Type(tape, data=rtn)
    
    # Do nothing if none of the above holds

    return var

#------------------------------------------------------------------------------
# Class AD_Scalar: Interacts directly with AD_Tape class
# (assumes all logical/arithmetic operands to be of AD_Scalar type)
#------------------------------------------------------------------------------

class AD_Scalar:

    def __init__(self, tape, operand1=-1, operand2=-1, operation="CONST", value=0.0):

        # Initialize tape
        self.tape   = tape

        # Initialize ID (assume for now that a new entry will be added)
        self.tapeID = len(tape.instructions)

        # If an arithmetic operation is added
        if operation not in ["CONST", "IFEQ", "IFNE", "IFLT", "IFLE", "IFGT", "IFGE"]:
            
            # Iterate over the histories for all conditional blocks
            for childDict in tape.children:

                # Check if an entry is present with the current operands and operation
                # If found, change the ID
                if operand1 in childDict.keys():
                    if operand2 in childDict[operand1][operation].keys():
                        self.tapeID = childDict[operand1][operation][operand2]
                        return
            
            # Do the same thing with operand2 and operand1 exchanged for commutative
            # operators, if an entry is not found previously
            if operation in ["ADD", "MUL", "MAX", "MIN"]:
                for childDict in tape.children:
                    if operand2 in childDict.keys():
                        if operand1 in childDict[operand2][operation].keys():
                            self.tapeID = childDict[operand2][operation][operand1]
                            return

        # If a constant is entered, check if the same value already exists
        # over all conditional blocks, if yes, change the ID
        if operation=="CONST" and value!=0.0:
            for idDict in tape.idsOfNonZeroConstants:
                if value in idDict.keys():
                    self.tapeID = idDict[value]
                    return

        # In case, an arithmetic operation or constant is not found in history
        # add a new one to the tape (Logical operators are always added)
        tape.addInstruction(operand1, operand2, operation, value)

    # Add operators (reverse operators needed when the second operator is an array)

    def __add__(self, other):
        return AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="ADD")

    def __radd__(self, other):
        return other + self

    def __sub__(self, other):
        return AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="SUB")

    def __rsub__(self, other):
        return other-self

    def __mul__(self, other):
        return AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="MUL")

    def __rmul__(self, other):
        return other * self

    def __truediv__(self, other):
        return AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="DIV")

    def __rtruediv__(self, other):
        return other/self

    def __pow__(self, other):
        return AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="POW")

    def __rpow__(self, other):
        return other**self

    def __eq__(self, other):
        # Check if this conditional is unregistered
        if self.tape.conditionalCounter>=len(self.tape.conditionalValues):
            # Add this conditional
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFEQ")
            # Add the value for this conditional as True in the tape
            self.tape.conditionalValues.append(True)
            # Create entries for this new conditional block in children and non-zero constants
            self.tape.children.append({})
            self.tape.idsOfNonZeroConstants.append({})
            # Increment the total number of conditionals encountered in this realization
            self.tape.conditionalCounter += 1
            return True
        # Check if this is the last registered conditional (Must be False, look in AD_Tape and more conditionals may be
        # present in the tape)
        elif self.tape.conditionalCounter==len(self.tape.conditionalValues)-1 and self.tape.conditionalValues[-1]==False:
            # Add this conditional
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFNE")
            # The conditional block for this conditional with value True is over, so create fresh entries for the block
            # with False value
            self.tape.children[-1] = {}
            self.tape.idsOfNonZeroConstants[-1] = {}
            # Increment the total number of conditionals encountered in this realization
            self.tape.conditionalCounter += 1
            return False
        else:
            # If registered and not the last registered one, DO NOT ADD THE CONDITIONAL (same conditional block continues)
            # Other operations are not duplicated as previous entries are found
            rtn = self.tape.conditionalValues[self.tape.conditionalCounter]
            # Increment the total number of conditionals encountered in this realization
            self.tape.conditionalCounter += 1
            return rtn

    def __ne__(self, other):
        if self.tape.conditionalCounter>=len(self.tape.conditionalValues):
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFNE")
            self.tape.conditionalValues.append(True)
            self.tape.children.append({})
            self.tape.idsOfNonZeroConstants.append({})
            self.tape.conditionalCounter += 1
            return True
        elif self.tape.conditionalCounter==len(self.tape.conditionalValues)-1 and self.tape.conditionalValues[-1]==False:
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFEQ")
            self.tape.children[-1] = {}
            self.tape.idsOfNonZeroConstants[-1] = {}
            self.tape.conditionalCounter += 1
            return False
        else:
            rtn = self.tape.conditionalValues[self.tape.conditionalCounter]
            self.tape.conditionalCounter += 1
            return rtn

    def __lt__(self, other):
        if self.tape.conditionalCounter>=len(self.tape.conditionalValues):
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFLT")
            self.tape.conditionalValues.append(True)
            self.tape.children.append({})
            self.tape.idsOfNonZeroConstants.append({})
            self.tape.conditionalCounter += 1
            return True
        elif self.tape.conditionalCounter==len(self.tape.conditionalValues)-1 and self.tape.conditionalValues[-1]==False:
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFGE")
            self.tape.children[-1] = {}
            self.tape.idsOfNonZeroConstants[-1] = {}
            self.tape.conditionalCounter += 1
            return False
        else:
            rtn = self.tape.conditionalValues[self.tape.conditionalCounter]
            self.tape.conditionalCounter += 1
            return rtn

    def __ge__(self, other):
        if self.tape.conditionalCounter>=len(self.tape.conditionalValues):
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFGE")
            self.tape.conditionalValues.append(True)
            self.tape.children.append({})
            self.tape.idsOfNonZeroConstants.append({})
            self.tape.conditionalCounter += 1
            return True
        elif self.tape.conditionalCounter==len(self.tape.conditionalValues)-1 and self.tape.conditionalValues[-1]==False:
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFLT")
            self.tape.children[-1] = {}
            self.tape.idsOfNonZeroConstants[-1] = {}
            self.tape.conditionalCounter += 1
            return False
        else:
            rtn = self.tape.conditionalValues[self.tape.conditionalCounter]
            self.tape.conditionalCounter += 1
            return rtn

    def __gt__(self, other):
        if self.tape.conditionalCounter>=len(self.tape.conditionalValues):
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFGT")
            self.tape.conditionalValues.append(True)
            self.tape.children.append({})
            self.tape.idsOfNonZeroConstants.append({})
            self.tape.conditionalCounter += 1
            return True
        elif self.tape.conditionalCounter==len(self.tape.conditionalValues)-1 and self.tape.conditionalValues[-1]==False:
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFLE")
            self.tape.children[-1] = {}
            self.tape.idsOfNonZeroConstants[-1] = {}
            self.tape.conditionalCounter += 1
            return False
        else:
            rtn = self.tape.conditionalValues[self.tape.conditionalCounter]
            self.tape.conditionalCounter += 1
            return rtn

    def __le__(self, other):
        if self.tape.conditionalCounter>=len(self.tape.conditionalValues):
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFLE")
            self.tape.conditionalValues.append(True)
            self.tape.children.append({})
            self.tape.idsOfNonZeroConstants.append({})
            self.tape.conditionalCounter += 1
            return True
        elif self.tape.conditionalCounter==len(self.tape.conditionalValues)-1 and self.tape.conditionalValues[-1]==False:
            rtn = AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="IFGT")
            self.tape.children[-1] = {}
            self.tape.idsOfNonZeroConstants[-1] = {}
            self.tape.conditionalCounter += 1
            return False
        else:
            rtn = self.tape.conditionalValues[self.tape.conditionalCounter]
            self.tape.conditionalCounter += 1
            return rtn

    def maxComparedTo(self, other):
        return AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="MAX")

    def minComparedTo(self, other):
        return AD_Scalar(self.tape, operand1=self.tapeID, operand2=other.tapeID, operation="MIN")

    def __neg__(self):
        return AD_Scalar(self.tape, operand1=self.tapeID, operation="NEG")

    def abs(self):
        return AD_Scalar(self.tape, operand1=self.tapeID, operation="ABS")

    def exp(self):
        return AD_Scalar(self.tape, operand1=self.tapeID, operation="EXP")

    def log(self):
        return AD_Scalar(self.tape, operand1=self.tapeID, operation="LOG")

    def sqrt(self):
        return AD_Scalar(self.tape, operand1=self.tapeID, operation="SQRT")

    def sin(self):
        return AD_Scalar(self.tape, operand1=self.tapeID, operation="SIN")

    def cos(self):
        return AD_Scalar(self.tape, operand1=self.tapeID, operation="COS")

    def tan(self):
        return AD_Scalar(self.tape, operand1=self.tapeID, operation="TAN")

    def sinh(self):
        return AD_Scalar(self.tape, operand1=self.tapeID, operation="SINH")

    def cosh(self):
        return AD_Scalar(self.tape, operand1=self.tapeID, operation="COSH")

    def tanh(self):
        return AD_Scalar(self.tape, operand1=self.tapeID, operation="TANH")

#------------------------------------------------------------------------------
# Class AD_Type: can contain either a scalar or an array
#------------------------------------------------------------------------------

class AD_Type:

    def __init__(self, tape, shape=[], data=None):

        if data is not None:
            
            self.data = data
        
        else:
            
            #[] means scalar
            if len(shape)==0:
                
                self.data = AD_Scalar(tape)
            
            #[m,n,...] means array
            else:
                
                self.data = np.empty(shape, dtype=AD_Scalar)
                dataR = self.data.ravel()
                for i in range(dataR.size):
                    dataR[i] = AD_Scalar(tape)

        self.isArray = isinstance(self.data, (np.ndarray))
        if self.isArray:
            self.shape = self.data.shape
        else:
            self.shape = []
        self.tape = tape

    def resize(self, newshape):
        if self.isArray:
            self.data.resize(shape)
            self.shape = shape
        else:
            return self

    def T(self):
        if self.isArray:
            return AD_Type(self.tape, data=self.data.T)
        else:
            return self

    def __getitem__(self, key):
        return AD_Type(self.tape, data=self.data[key])

    def __setitem__(self, key, newValue):
        self.data[key] = newValue.data

    def __neg__(self):
        return AD_Type(self.tape, data=-self.data)

    # Reverse operations are needed if the left quantity is not of AD_Type

    def __add__(self, other):
        other = AD(self.tape, other)
        if self.isArray==False and other.isArray==True:
            return AD_Type(self.tape, data=other.data.__radd__(self.data))
        else:
            return AD_Type(self.tape, data=self.data+other.data)

    def __sub__(self, other):
        other = AD(self.tape, other)
        if self.isArray==False and other.isArray==True:
            return AD_Type(self.tape, data=other.data.__rsub__(self.data))
        else:
            return AD_Type(self.tape, data=self.data-other.data)

    def __mul__(self, other):
        other = AD(self.tape, other)
        if self.isArray==False and other.isArray==True:
            return AD_Type(self.tape, data=other.data.__rmul__(self.data))
        else:
            return AD_Type(self.tape, data=self.data*other.data)

    def __truediv__(self, other):
        other = AD(self.tape, other)
        if self.isArray==False and other.isArray==True:
            return AD_Type(self.tape, data=other.data.__rtruediv__(self.data))
        else:
            return AD_Type(self.tape, data=self.data/other.data)

    def __pow__(self, other):
        other = AD(self.tape, other)
        if self.isArray==False and other.isArray==True:
            return AD_Type(self.tape, data=other.data.__rpow__(self.data))
        else:
            return AD_Type(self.tape, data=self.data**other.data)

    def __radd__(self, other):
        other = AD(self.tape, other)
        if self.isArray==True and other.isArray==False:
            return AD_Type(self.tape, data=self.data.__radd__(other.data))
        else:
            return AD_Type(self.tape, data=other.data+self.data)

    def __rsub__(self, other):
        other = AD(self.tape, other)
        if self.isArray==True and other.isArray==False:
            return AD_Type(self.tape, data=self.data.__rsub__(other.data))
        else:
            return AD_Type(self.tape, data=other.data-self.data)

    def __rmul__(self, other):
        other = AD(self.tape, other)
        if self.isArray==True and other.isArray==False:
            return AD_Type(self.tape, data=self.data.__rmul__(other.data))
        else:
            return AD_Type(self.tape, data=other.data*self.data)

    def __rtruediv__(self, other):
        other = AD(self.tape, other)
        if self.isArray==True and other.isArray==False:
            return AD_Type(self.tape, data=self.data.__rtruediv__(other.data))
        else:
            return AD_Type(self.tape, data=other.data/self.data)

    def __rpow__(self, other):
        other = AD(self.tape, other)
        if self.isArray==True and other.isArray==False:
            return AD_Type(self.tape, data=self.data.__rpow__(other.data))
        else:
            return AD_Type(self.tape, data=other.data**self.data)

    def __eq__(self, other):
        other = AD(self.tape, other)
        if self.isArray or other.isArray:
            print("Error: Comparing arrays!")
            sys.exit(0)
        else:
            return self.data==other.data

    def __ne__(self, other):
        other = AD(self.tape, other)
        if self.isArray or other.isArray:
            print("Error: Comparing arrays!")
            sys.exit(0)
        else:
            return self.data!=other.data

    def __lt__(self, other):
        other = AD(self.tape, other)
        if self.isArray or other.isArray:
            print("Error: Comparing arrays!")
            sys.exit(0)
        else:
            return self.data<other.data

    def __ge__(self, other):
        other = AD(self.tape, other)
        if self.isArray or other.isArray:
            print("Error: Comparing arrays!")
            sys.exit(0)
        else:
            return self.data>=other.data

    def __gt__(self, other):
        other = AD(self.tape, other)
        if self.isArray or other.isArray:
            print("Error: Comparing arrays!")
            sys.exit(0)
        else:
            return self.data>other.data

    def __le__(self, other):
        other = AD(self.tape, other)
        if self.isArray or other.isArray:
            print("Error: Comparing arrays!")
            sys.exit(0)
        else:
            return self.data<=other.data

def abs(x):
    if isinstance(x, (AD_Type)):
        return AD_Type(x.tape, data=np.abs(x.data))
    else:
        return np.abs(x)

def exp(x):
    if isinstance(x, (AD_Type)):
        return AD_Type(x.tape, data=np.exp(x.data))
    else:
        return np.exp(x)

def log(x):
    if isinstance(x, (AD_Type)):
        return AD_Type(x.tape, data=np.log(x.data))
    else:
        return np.log(x)

def sqrt(x):
    if isinstance(x, (AD_Type)):
        return AD_Type(x.tape, data=np.sqrt(x.data))
    else:
        return np.sqrt(x)

def maximum(x, y):
    if isinstance(x, (AD_Type)) or isinstance(y, (AD_Type)):
        if isinstance(x, (AD_Type))==False: x = AD(y.tape, x)
        if isinstance(y, (AD_Type))==False: y = AD(x.tape, y)
        if x.isArray or y.isArray:
            print("Error: max: Comparing arrays!")
            sys.exit(0)
        else:
            return AD_Type(x.tape, data=x.data.maxComparedTo(y.data))
    else:
        return np.maximum(x,y)

def minimum(x, y):
    if isinstance(x, (AD_Type)) or isinstance(y, (AD_Type)):
        if isinstance(x, (AD_Type))==False: x = AD(y.tape, x)
        if isinstance(y, (AD_Type))==False: y = AD(x.tape, y)
        if x.isArray or y.isArray:
            print("Error: min: Comparing arrays!")
            sys.exit(0)
        else:
            return AD_Type(x.tape, data=x.data.minComparedTo(y.data))
    else:
        return np.minimum(x,y)

def sin(x):
    if isinstance(x, (AD_Type)):
        return AD_Type(x.tape, data=np.sin(x.data))
    else:
        return np.sin(x)

def cos(x):
    if isinstance(x, (AD_Type)):
        return AD_Type(x.tape, data=np.cos(x.data))
    else:
        return np.cos(x)

def tan(x):
    if isinstance(x, (AD_Type)):
        return AD_Type(x.tape, data=np.tan(x.data))
    else:
        return np.tan(x)

def sinh(x):
    if isinstance(x, (AD_Type)):
        return AD_Type(x.tape, data=np.sinh(x.data))
    else:
        return np.sinh(x)

def cosh(x):
    if isinstance(x, (AD_Type)):
        return AD_Type(x.tape, data=np.cosh(x.data))
    else:
        return np.cosh(x)

def tanh(x):
    if isinstance(x, (AD_Type)):
        return AD_Type(x.tape, data=np.tanh(x.data))
    else:
        return np.tanh(x)

def dot(x, y):
    if isinstance(x, (AD_Type)) or isinstance(y, (AD_Type)):
        if isinstance(x, (AD_Type))==False: x = AD(y.tape, x)
        if isinstance(y, (AD_Type))==False: y = AD(x.tape, y)
        return AD_Type(x.tape, data=np.dot(x.data, y.data))
    else:
        return np.dot(x)

def cross(x, y):
    if isinstance(x, (AD_Type)) or isinstance(y, (AD_Type)):
        if isinstance(x, (AD_Type))==False: x = AD(y.tape, x)
        if isinstance(y, (AD_Type))==False: y = AD(x.tape, y)
        return AD_Type(x.tape, data=np.cross(x.data, y.data))
    else:
        return np.cross(x,y)

def matmul(x, y):
    if isinstance(x, (AD_Type)) or isinstance(y, (AD_Type)):
        if isinstance(x, (AD_Type))==False: x = AD(y.tape, x)
        if isinstance(y, (AD_Type))==False: y = AD(x.tape, y)
        return AD_Type(x.tape, data=np.matmul(x.data, y.data))
    else:
        return np.matmul(x,y)
