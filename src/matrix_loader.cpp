#include "../include/matrix_loader.h"
#include <fstream>
#include <iostream>
#include "../include/json.hpp"

using namespace std;

using json = nlohmann::json;

bool loadMatrices(const string& filename, double* A, double* B)
{
    ifstream file(filename);

    if(!file.is_open())
    {
        cout << "Error opening JSON file.\n";
        return false;
    }

    json data;
    file >> data;

    auto matrixA = data["matrixA"];
    auto matrixB = data["matrixB"];

    int index = 0;

    for(int i = 0; i < N; i++)
    {
        for(int j = 0; j < N; j++)
        {
            A[i*N + j] = matrixA[index];
            B[i*N + j] = matrixB[index];
            index++;
        }
    }

    return true;
}