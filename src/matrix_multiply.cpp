#include "../include/matrix_multiply.h"

void multiplyMatricesSerial(double* A, double* B, double* C)
{
    for(int i = 0; i < N; i++)
    {
        for(int j = 0; j < N; j++)
        {
            C[i*N + j] = 0;
        }
    }

    for(int i = 0; i < N; i++)
    {
        for(int k = 0; k < N; k++)
        {
            double temp = A[i*N + k];

            for(int j = 0; j < N; j++)
            {
                C[i*N + j] += temp * B[k*N + j];
            }
        }
    }
}