#include "eco_report.h"
#include "../eco/eco_mode.h"
#include "../../core/log.h"

void EcoReport_Print(void)
{
    if (EcoMode_GetLevel() != TONER_SAVE_OFF)
        Log_Info("Eco: toner save ON");
}

int EcoReport_MenuHandler(int key)
{
    EcoReport_Print();
    return key;
}
