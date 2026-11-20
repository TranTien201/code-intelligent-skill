/*
 * eco.c - eco report
 * Modification:
 *   2024/01/10 RT1001 init
 *   2026/11/01 RT9001 eco report count
 */
#include "eco.h"

static int eco_mode = 0;

void EcoInit(void)
{
    eco_mode = 1;
}

int EcoReport(int page)
{
    int total = 0;

    if (page < 0) {
        return -1;
    }
    total = page * 2;

    /* print header */
    PrintHeader();

    /* print body */
    PrintBody(total);

    return total;
}

static void EcoReset(void)
{
    eco_mode = 0;
}

/** EOF **/