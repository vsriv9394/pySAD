#include "SAD_Operations.h"
#include <cmath>
#include <vector>

/*
 *  Tape Entry class (for use only in C/C++)
 */

class SAD_Tape;

class SAD_TapeEntry
{
  friend class SAD_Tape;

  private:

    size_t blockEnd; // End of the block (for connditional entries)
    size_t parent1;  // First operand
    size_t parent2;  // Second operand
    int operation;   // Operation between operands to get value
    double value;    // Value of the entry
    double deriv;    // Sensitivity w.r.t. this entry
    bool evaluated;  // True if this value was calculated in forwprop

  public:

    // Constructors

    SAD_TapeEntry(void) { }

    void init(size_t blockEnd, size_t parent1, size_t parent2, int operation, double value)
    {
      this->blockEnd  = blockEnd;
      this->parent1   = parent1;
      this->parent2   = parent2;
      this->operation = operation;
      this->value     = value;
    }

    // Destructor

    ~SAD_TapeEntry() { }

    // Subroutines for conditional statements
    
    inline bool isConditionalStatement(void) { return operation>=IFEQ; }

    inline bool returnsTrue(std::vector<SAD_TapeEntry>& tapeVec)
    {
      double x1 = tapeVec[parent1].value;
      double x2 = tapeVec[parent2].value;
      switch(operation)
      {
        case IFEQ: return x1==x2; break;
        case IFNE: return x1!=x2; break;
        case IFLT: return x1< x2; break;
        case IFLE: return x1<=x2; break;
        case IFGT: return x1> x2; break;
        case IFGE: return x1>=x2; break;
        default: throw(-1);
      }
    }

    // Value Evaluation

    void calculateValue(std::vector<SAD_TapeEntry>& tapeVec)
    {
      double y, x1, x2;
      if(parent1!=-1) x1 = tapeVec[parent1].value;
      if(parent2!=-1) x2 = tapeVec[parent2].value;
      switch(operation)
      {
        case NEG:  y = -x1; break;
        case ADD:  y = x1 + x2; break;
        case SUB:  y = x1 - x2; break;
        case MUL:  y = x1 * x2; break;
        case DIV:  y = x1 / x2; break;
        case POW:  y = pow(x1, x2); break;
        case EXP:  y =  exp(x1); break;
        case LOG:  y =  log(x1); break;
        case SQRT: y = sqrt(x1); break;
        case MAX:  y = (x1>x2) ? x1 : x2; break;
        case MIN:  y = (x1<x2) ? x1 : x2; break;
        case ABS:  y = fabs(x1); break;
        case SIN:  y =  sin(x1); break;
        case COS:  y =  cos(x1); break;
        case TAN:  y =  tan(x1); break;
        case SINH: y = sinh(x1); break;
        case COSH: y = cosh(x1); break;
        case TANH: y = tanh(x1); break;
      }
      value = y;
      evaluated = true;
    }

    // Sensitivity evaluation

    void calculateSensitivity(std::vector<SAD_TapeEntry>& tapeVec)
    {
      if(evaluated && parent1!=-1)
      {
        double y=value, x1, x2, d1, d2;
        x1 = tapeVec[parent1].value;
        if(parent2!=-1) x2 = tapeVec[parent2].value;
        switch(operation)
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
        tapeVec[parent1].deriv += d1 * deriv;
        if(parent2!=-1) tapeVec[parent2].deriv += d2 * deriv;
      }
    }
};
