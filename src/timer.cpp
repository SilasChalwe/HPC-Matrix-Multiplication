#include "../include/timer.h"

void Timer::start()
{
    startTime = chrono::high_resolution_clock::now();
}

void Timer::stop()
{
    endTime = chrono::high_resolution_clock::now();
}

double Timer::getElapsedSeconds()
{
    chrono::duration<double> duration = endTime - startTime;
    return duration.count();
}