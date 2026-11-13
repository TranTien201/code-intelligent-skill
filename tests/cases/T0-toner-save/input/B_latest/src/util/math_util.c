#include "math_util.h"

int Clamp(int v, int hi)
{
    if (v < 0) return 0;
    if (v > hi) return hi;
    return v;
}
