#include "eco_report.h"
#include "../toner_save/toner_save.h"
#include "../../core/log.h"

void EcoReport_Print(void)
{
    if (TonerSave_GetLevel() != TONER_SAVE_OFF)
        Log_Info("Eco: toner save ON");
}

int EcoReport_MenuHandler(int key)
{
    EcoReport_Print();
    return key;
}
