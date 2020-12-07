#pragma once

#include <cstdlib>
#include <vector>
#include <string>
#include <cassert>
#include "SAD_Jacobian.h"
#include "SAD_TapeEntry.h"

class SAD_Tape
{
  private:

    size_t nInputs;
    size_t nOutputs;
    size_t effectiveTapeSize;
    std::vector<SAD_TapeEntry> data;
    SAD_Jacobian jacobian;

  public:

    // Constructors and Initializers

    SAD_Tape(void) { }

    void init(const std::string& filename)
    {
      int rtn; size_t nData;
      size_t blockEnd, parent1, parent2; int operation; double value;

      FILE *fp;
      
      fp = fopen(filename.c_str(), "r");
      
        rtn = fscanf(fp, "%lu", &nInputs);
        rtn = fscanf(fp, "%lu", &nOutputs);
        rtn = fscanf(fp, "%lu", &nData);
        
        jacobian.init(nOutputs, nInputs);
        data.resize(nData);
        
        for(int iData=0; iData<nData; iData++)
        {
          rtn = fscanf(fp, "%lu", &blockEnd);
          rtn = fscanf(fp, "%lu", &parent1);
          rtn = fscanf(fp, "%lu", &parent2);
          rtn = fscanf(fp, "%d",  &operation);
          rtn = fscanf(fp, "%le", &value);
          data[iData].init(blockEnd, parent1, parent2, operation, value);
        }
      
      fclose(fp);
    }

    // Destructors

    virtual ~SAD_Tape() { }

    // Set inputs, and get outputs and jacobians

    inline void setInput(size_t iInput, const double& val)
    {
      assert(iInput<nInputs);
      data[iInput].value = val;
    }

    inline double getOutput(size_t iOutput)
    {
      assert(iOutput<nOutputs);
      return data[effectiveTapeSize-nOutputs+iOutput-1].value;
    }

    inline double getJacobian(size_t iOutput, size_t iInput)
    {
      assert(iInput<nInputs && iOutput<nOutputs);
      return jacobian(iOutput, iInput);
    }

    // Evaluate outputs

    inline void evaluateOutputs(void)
    {
      effectiveTapeSize = data.size();
      
      for(size_t i=nInputs; i<effectiveTapeSize; i++)
      {
        data[i].evaluated = false;
        
        if(data[i].isConditionalStatement())
        {
          if(data[i].returnsTrue(data)) effectiveTapeSize = data[i].blockEnd;
          else i = data[i].blockEnd;
          i--;
        }
        
        else
          data[i].calculateValue(data);
      }
    }

    // Evaluate outputs and jacobians

    inline void evaluateOutputsAndJacobian(int iOutput)
    {
      int outputIndex;
      evaluateOutputs();

      for(size_t iOutput=0; iOutput<nOutputs; iOutput++)
      {
        outputIndex = effectiveTapeSize-nOutputs+iOutput-1;
        preprocessForSensitivityCalculationOf(outputIndex);
        
        for(size_t i=outputIndex; i>=nInputs; i--)
          data[i].calculateSensitivity(data);

        setJacobianValuesAfterSensitivityEvaluation(iOutput);
      }
    }

    // Utilities

    inline void preprocessForSensitivityCalculationOf(size_t outputIndex)
    {
      for(size_t i=nInputs; i<outputIndex; i++)
        data[i].deriv = 0.0;
      data[outputIndex].deriv = 1.0;
    }

    inline void setJacobianValuesAfterSensitivityEvaluation(size_t iOutput)
    {
      for(size_t iInput=0; iInput<nInputs; iInput++)
        jacobian(iOutput,iInput) = data[iInput].deriv;
    }
};
