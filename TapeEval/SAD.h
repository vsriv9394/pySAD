#ifndef AD_Tape
#define AD_Tape

#include "math.h"
#include "assert.h"
#include "string.h"
#include "stdlib.h"
#include "stdio.h"

#ifdef __cplusplus
extern "C"
{
#endif

  enum operationsEnum
  {
    CONST,
    NEG,
    ADD,
    SUB,
    MUL,
    DIV,
    POW,
    ABS,
    EXP,
    LOG,
    SQRT,
    MAX,
    MIN,
    SIN,
    COS,
    TAN,
    SINH,
    COSH,
    TANH,
    IFEND,
    IFEQ,
    IFNE,
    IFLT,
    IFGE,
    IFGT,
    IFLE
  };

  typedef struct
  {
    int blockEnd;
    int operand1;
    int operand2;
    int operation;
    double value;
    double deriv;
  } SAD_Instruction;

  typedef struct
  {
    int effectiveTapeSize;
    int tapeSize;
    int nInputs;
    int nOutputs;
    double *jacobian;
    SAD_Instruction *instructions;
  } SAD_Tape;

  void readTapeFromFile(SAD_Tape *tape, char *filename)
  {
    FILE *fp = fopen(filename, "r");
    int rtn;
    rtn = fscanf(fp, "%d", &(tape->nInputs));
    rtn = fscanf(fp, "%d", &(tape->nOutputs));
    rtn = fscanf(fp, "%d", &(tape->tapeSize));
    //printf("%d %d %d\n", tape->nInputs, tape->nOutputs, tape->tapeSize);
    tape->effectiveTapeSize = tape->tapeSize;
    tape->jacobian = (double*)calloc((tape->nOutputs)*(tape->nInputs), sizeof(double));
    tape->instructions = (SAD_Instruction*)calloc(tape->tapeSize, sizeof(SAD_Instruction));
    for(int i=0; i<tape->tapeSize; i++)
    {
      rtn = fscanf(fp, "%d",  &(tape->instructions[i].blockEnd));
      rtn = fscanf(fp, "%d",  &(tape->instructions[i].operand1));
      rtn = fscanf(fp, "%d",  &(tape->instructions[i].operand2));
      rtn = fscanf(fp, "%d",  &(tape->instructions[i].operation));
      rtn = fscanf(fp, "%le", &(tape->instructions[i].value));
      /*
      printf("%d %d %d %d %le\n",
              tape->instructions[i].blockEnd,
              tape->instructions[i].operand1,
              tape->instructions[i].operand2,
              tape->instructions[i].operation,
              tape->instructions[i].value);
      // */
    }
    fclose(fp);
  }

  void deleteTape(SAD_Tape tape)
  {
    free(tape.jacobian);
    free(tape.instructions);
  }

  int isConditionalStatement(SAD_Instruction *instructions, int i)
  {
    return ((instructions[i].operation>IFEND) ? 1 : 0);
  }

  int conditionalIsTrue(SAD_Instruction *instructions, int i)
  {
    int op1 = instructions[i].operand1;
    int op2 = instructions[i].operand2;
    double x1 = instructions[op1].value;
    double x2 = instructions[op2].value;
    switch(instructions[i].operation)
    {
      case IFEQ: return x1==x2; break;
      case IFNE: return x1!=x2; break;
      case IFLT: return x1< x2; break;
      case IFGE: return x1>=x2; break;
      case IFGT: return x1> x2; break;
      case IFLE: return x1<=x2; break;
      default: return -1;
    }
  }

  void calculateValue(SAD_Instruction *instructions, int i)
  {
    double y = 0.0;
    int op1 = instructions[i].operand1;
    int op2 = instructions[i].operand2;
    double x1 = instructions[op1].value;
    double x2 = instructions[op2].value;
    switch(instructions[i].operation)
    {
        case NEG:  y = -x1; break;
        case ADD:  y = x1 + x2; break;
        case SUB:  y = x1 - x2; break;
        case MUL:  y = x1 * x2; break;
        case DIV:  y = x1 / x2; break;
        case POW:  y = pow(x1, x2); break;
        case ABS:  y = fabs(x1); break;
        case EXP:  y =  exp(x1); break;
        case LOG:  y =  log(x1); break;
        case SQRT: y = sqrt(x1); break;
        case MAX:  y = (x1>x2) ? x1 : x2; break;
        case MIN:  y = (x1<x2) ? x1 : x2; break;
        case SIN:  y =  sin(x1); break;
        case COS:  y =  cos(x1); break;
        case TAN:  y =  tan(x1); break;
        case SINH: y = sinh(x1); break;
        case COSH: y = cosh(x1); break;
        case TANH: y = tanh(x1); break;
    }
    if(instructions[i].operand1!=-1)
      instructions[i].value = y;
  }
    
  void calculateSensitivity(SAD_Instruction *instructions, int i)
  {
    int op1 = instructions[i].operand1;
    int op2 = instructions[i].operand2;
    if(op1!=-1)
    {
      double d1, d2;
      double y = instructions[i].value;
      double x1 = instructions[op1].value;
      double x2 = 0.0;
      if(op2!=-1) x2 = instructions[op2].value;
      switch(instructions[i].operation)
      {
        case NEG:  d1 = -1.0; break;
        case ADD:  d1 = 1.0; d2 = 1.0; break;
        case SUB:  d1 = 1.0; d2 = -1.0; break;
        case MUL:  d1 = x2; d2 = x1; break;
        case DIV:  d1 = 1.0/x2; d2 = -y/x2; break;
        case POW:  d1 = x2*y/x1; d2 = y*log(fabs(x1)); break;
        case EXP:  d1 = y; break;
        case LOG:  d1 = 1.0/x1; break;
        case SQRT: d1 = 0.5/y; break;
        case MAX:  d1 = (x1>x2) ? 1.0 : 0.0; d2 = (x1>x2) ? 0.0 : 1.0; break;
        case MIN:  d1 = (x1<x2) ? 1.0 : 0.0; d2 = (x1<x2) ? 0.0 : 1.0; break;
        case ABS:  d1 = (x1==0) ? 1.0 : y/x1; break;
        case SIN:  d1 = cos(x1); break;
        case COS:  d1 = -sin(x1); break;
        case TAN:  d1 = 1.0 + y*y; break;
        case SINH: d1 = cosh(x1); break;
        case COSH: d1 = sinh(x1); break;
        case TANH: d1 = 1.0 - y*y; break;
      }
      instructions[op1].deriv += d1 * instructions[i].deriv;
      if(op2!=-1) instructions[op2].deriv += d2 * instructions[i].deriv;
    }
  }

  void setTapeInput(SAD_Tape tape, int iInput, double val)
  {
    assert(iInput<tape.nInputs);
    tape.instructions[iInput].value = val;
  }

  double getTapeOutput(SAD_Tape tape, int iOutput)
  {
    assert(iOutput<tape.nOutputs);
    return tape.instructions[tape.effectiveTapeSize-tape.nOutputs+iOutput-1].value;
  }

  double getTapeJacobian(SAD_Tape tape, int iOutput, int iInput)
  {
    assert(iInput<tape.nInputs && iOutput<tape.nOutputs);
    return tape.jacobian[iOutput*(tape.nInputs) + iInput];
  }

  void evaluateOutputs(SAD_Tape *tape)
  {
    tape->effectiveTapeSize = tape->tapeSize;

    for(int i=tape->nInputs; i<tape->effectiveTapeSize; i++)
    {
      if(isConditionalStatement(tape->instructions, i))
      {
        if(conditionalIsTrue(tape->instructions, i))
        {
          tape->effectiveTapeSize = tape->instructions[i].blockEnd;
        }
        else
        {
          i = tape->instructions[i].blockEnd;
        }
      }
      else
      {
        calculateValue(tape->instructions, i);
      }
    }
  }

  void evaluateTapeOutputsAndJacobian(SAD_Tape *tape)
  {
    int outputID;
    evaluateOutputs(tape);

    for(int iOutput=0; iOutput<tape->nOutputs; iOutput++)
    {
      outputID = tape->effectiveTapeSize - tape->nOutputs + iOutput - 1;

      for(int i=tape->nInputs; i<outputID; i++) tape->instructions[i].deriv = 0.0;
      tape->instructions[outputID].deriv = 1.0;

      for(int i=outputID; i>=tape->nInputs; i--)
      {
        if(tape->instructions[i].operation==IFEND) i = tape->instructions[i].blockEnd;
        calculateSensitivity(tape->instructions, i);
      }

      for(int iInput=0; iInput<tape->nInputs; iInput++)
      {
        tape->jacobian[iOutput*(tape->nInputs)+iInput] = tape->instructions[iInput].deriv;
      }
    }
  }

#ifdef __cplusplus
}
#endif

#endif
