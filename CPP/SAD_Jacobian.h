#pragma once
#include <vector>

/*
 *  Jacobian class to access the jacobian entries easily
 *  while maintaining easy portability to python (one-dimensional array)
 */

class SAD_Jacobian
{
  private:
    
    size_t m;                 // Number of dependent variables
    size_t n;                 // Number of independent variables
    std::vector<double> data; // Jacobian data

  public:

    // Constructors
    
    SAD_Jacobian(void) { }

    void init(size_t m, size_t n)
    {
      this->m = m;
      this->n = n;
      data.resize(m*n, 0.0);
    }

    // Destructor

    ~SAD_Jacobian() { }

    // Indexing operators

    inline const double& operator()(int i, int j) const { return data[i*m+j]; }
    inline double& operator()(int i, int j) { return data[i*m+j]; }
};
