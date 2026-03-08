#ifndef TIMER_H
#define TIMER_H

#include <chrono>

using namespace std;

class Timer {

private:
    chrono::high_resolution_clock::time_point startTime;
    chrono::high_resolution_clock::time_point endTime;

public:
    void start();
    void stop();
    double getElapsedSeconds();
};

#endif