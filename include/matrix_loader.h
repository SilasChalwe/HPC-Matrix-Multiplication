#ifndef MATRIX_LOADER_H
#define MATRIX_LOADER_H

#include <string>
#include "constants.h"

using namespace std;

bool loadMatrices(const string& filename, double* A, double* B);

#endif