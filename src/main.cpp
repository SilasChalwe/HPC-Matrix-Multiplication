#include <iostream>
#include <fstream>

#include "../include/matrix_loader.h"
#include "../include/matrix_multiply.h"
#include "../include/timer.h"

using namespace std;

int main()
{
    cout << "=====================================\n";
    cout << "Serial Matrix Multiplication (HPC)\n";
    cout << "Matrix Size: " << N << " x " << N << endl;
    cout << "=====================================\n";

    double* A = new double[N*N];
    double* B = new double[N*N];
    double* C = new double[N*N];

    cout << "Loading matrices from JSON...\n";

    if(!loadMatrices("data/matrices.json", A, B))
    {
        cout << "Matrix loading failed.\n";
        return 1;
    }

    cout << "Matrices loaded successfully.\n";

    Timer timer;

    cout << "Starting serial multiplication...\n";

    timer.start();

    multiplyMatricesSerial(A, B, C);

    timer.stop();

    double executionTime = timer.getElapsedSeconds();

    cout << "\nExecution Time: " << executionTime << " seconds\n";

    long long multiplications = (long long)N * N * N;
    long long additions = (long long)N * N * (N - 1);
    long long totalOps = multiplications + additions;

    cout << "\nOperation Statistics\n";
    cout << "----------------------\n";
    cout << "Multiplications : " << multiplications << endl;
    cout << "Additions       : " << additions << endl;
    cout << "Total Operations: " << totalOps << endl;

    ofstream resultFile("results/execution_times.csv", ios::app);

    resultFile << N << "," << executionTime << endl;

    resultFile.close();

    cout << "\nResults saved to results/execution_times.csv\n";

    delete[] A;
    delete[] B;
    delete[] C;

    cout << "\nProgram completed successfully.\n";

    return 0;
}