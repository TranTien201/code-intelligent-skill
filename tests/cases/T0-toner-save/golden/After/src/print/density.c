#include "density.h"
#include "../util/math_util.h"

int Density_Scale(int base, int percent)
{
    return Clamp(base * percent / 100, 0, DENSITY_MAX);
}
