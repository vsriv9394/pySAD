import inspect
import numpy as np
from pySAD.AD_Type import AD_Type

operationsList = \
{
    "CONST": 0,
    "NEG":   1,
    "ADD":   2,
    "SUB":   3,
    "MUL":   4,
    "DIV":   5,
    "POW":   6,
    "ABS":   7,
    "EXP":   8,
    "LOG":   9,
    "SQRT": 10,
    "MAX":  11,
    "MIN":  12,
    "SIN":  13,
    "COS":  14,
    "TAN":  15,
    "SINH": 16,
    "COSH": 17,
    "TANH": 18,
    "IFEQ": 19,
    "IFNE": 20,
    "IFLT": 21,
    "IFGE": 22,
    "IFGT": 23, 
    "IFLE": 24
}

class AD_Instruction:

    def __init__(self, operand1, operand2, operation, value):

        self.blockEnd  = -1
        self.operand1  = operand1
        self.operand2  = operand2
        self.operation = operation
        self.value     = value
        
class AD_Tape:

    def __init__(self):

        self.nInputs               = 0
        self.nOutputs              = 0
        self.idsOfConditionals     = []
        self.instructions          = []
        
        self.conditionalValues     = []
        self.conditionalCounter    = 0

        self.idsOfNonZeroConstants = [{}]
        self.children              = [{}]

    def getChildrenStructure(self):

        rtn = {}
        for key in operationsList.keys():
            rtn[key] = {}
        return rtn

    def addInstruction(self, operand1, operand2, operation, value):

        if operation=="CONST" and value!=0.0:
            self.idsOfNonZeroConstants[-1][value] = len(self.instructions)

        if operation not in ["CONST", "IFEQ", "IFNE", "IFLT", "IFLE", "IFGT", "IFGE"]:
            if operand1 not in self.children[-1].keys():
                self.children[-1][operand1] = self.getChildrenStructure()
            self.children[-1][operand1][operation][operand2] = len(self.instructions)
        
        if operation in ["IFEQ", "IFNE", "IFLT", "IFLE", "IFGT", "IFGE"]:
            self.idsOfConditionals.append(len(self.instructions))

        self.instructions.append(AD_Instruction(operand1, operand2, operation, value))

    def initFunctionArgs(self, function):

        args = inspect.getfullargspec(function).args
        defaults = inspect.getfullargspec(function).defaults
        argDict = {}
        for i in range(len(args)):
            argDict[args[i]] = AD_Type(self, shape=defaults[i])
            self.nInputs += int(np.prod(defaults[i]))
        return argDict

    def compile(self, function, kwargs={}):

        argDict = self.initFunctionArgs(function)
        for key in kwargs.keys():
            if key not in argDict.keys():
                argDict[key] = kwargs[key]

        self.conditionalCounter = 0
        outputs = function(**argDict)
        outputs = [output*1.0 for output in outputs]
        
        for output in outputs:
            self.nOutputs += int(np.prod(output.shape))

        while len(self.conditionalValues)>0:
            
            self.conditionalValues[-1] = False
            self.instructions[self.idsOfConditionals[-1]].blockEnd = len(self.instructions)
            self.idsOfConditionals = self.idsOfConditionals[:-1]
            
            self.conditionalCounter = 0
            outputs = function(**argDict)
            outputs = [output*1.0 for output in outputs]
            
            while self.conditionalValues[-1]==False:
                self.instructions[self.idsOfConditionals[-1]].blockEnd = len(self.instructions)
                self.conditionalValues = self.conditionalValues[:-1]
                self.idsOfConditionals = self.idsOfConditionals[:-1]
                self.idsOfNonZeroConstants = self.idsOfNonZeroConstants[:-1]
                self.children = self.children[:-1]
                if len(self.conditionalValues)==0:
                    break

    def write(self, filename, readable=False):

        with open(filename, "w") as f:

            f.write("%d %d %d\n"%(self.nInputs, self.nOutputs, len(self.instructions)))
            for i in range(len(self.instructions)):
                t = self.instructions[i]
                if readable:
                    f.write("%9d %9d %9d %5s %.15le\n"%(t.blockEnd, t.operand1, t.operand2, t.operation, t.value))
                else:
                    f.write("%9d %9d %9d %9d %.15le\n"%(t.blockEnd, t.operand1, t.operand2, operationsList[t.operation], t.value))

    def evaluate(self, inputs):

        effSize = len(self.instructions)
        for i in range(self.nInputs):
            self.instructions[i].value = inputs[i]
        for i in range(self.nInputs,effSize):
            y = self.instructions[i]
            x1 = self.instructions[y.operand1].value
            x2 = self.instructions[y.operand2].value
            if y.operation=="IFEQ":
                if(x1==x2): effSize=y.blockEnd
                else: i=y.blockEnd;
            if y.operation=="IFNE":
                if(x1!=x2): effSize=y.blockEnd
                else: i=y.blockEnd;
            if y.operation=="IFLT":
                if(x1< x2): effSize=y.blockEnd
                else: i=y.blockEnd;
            if y.operation=="IFGE":
                if(x1>=x2): effSize=y.blockEnd
                else: i=y.blockEnd;
            if y.operation=="IFGT":
                if(x1> x2): effSize=y.blockEnd
                else: i=y.blockEnd;
            if y.operation=="IFLE":
                if(x1<=x2): effSize=y.blockEnd
                else: i=y.blockEnd;
            if y.operation=="NEG":   y.value = -x1
            if y.operation=="ADD":   y.value = x1+x2
            if y.operation=="SUB":   y.value = x1-x2
            if y.operation=="MUL":   y.value = x1*x2
            if y.operation=="DIV":   y.value = x1/x2
            if y.operation=="POW":   y.value = x1**x2
            if y.operation=="ABS":   y.value = np.abs(x1)
            if y.operation=="EXP":   y.value = np.exp(x1)
            if y.operation=="LOG":   y.value = np.log(x1)
            if y.operation=="SQRT":  y.value = np.sqrt(x1)
            if y.operation=="MAX":   y.value = np.maximum(x1,x2)
            if y.operation=="MIN":   y.value = np.minimum(x1,x2)
            if y.operation=="SIN":   y.value = np.sin(x1)
            if y.operation=="COS":   y.value = np.cos(x1)
            if y.operation=="TAN":   y.value = np.tan(x1)
            if y.operation=="SINH":  y.value = np.sinh(x1)
            if y.operation=="COSH":  y.value = np.cosh(x1)
            if y.operation=="TANH":  y.value = np.tanh(x1)
        return [self.instructions[i].value for i in range(effSize-self.nOutputs,effSize)]
