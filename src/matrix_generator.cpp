#include <iostream>
#include <fstream>
#include <random>
#include "../include/constants.h"
using namespace std;

int main()
{
    cout << "Generating " << N << "x" << N << " matrices...\n";

    // random number generator
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<int> dis(1, 100); // numbers 1-100

    ofstream file("data/matrices.json");
    if (!file.is_open())
    {
        cout << "Error opening data/matrices.json for writing.\n";
        return 1;
    }

    file << "{\n";

    // matrixA
    file << "  \"matrixA\":[";
    for (int i = 0; i < N*N; i++)
    {
        file << dis(gen);
        if (i != N*N - 1) file << ",";
    }
    file << "],\n";

    // matrixB
    file << "  \"matrixB\":[";
    for (int i = 0; i < N*N; i++)
    {
        file << dis(gen);
        if (i != N*N - 1) file << ",";
    }
    file << "]\n";

    file << "}\n";

    file.close();

    cout << "Matrices generated successfully in data/matrices.json\n";
    return 0;
}