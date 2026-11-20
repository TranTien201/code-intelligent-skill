#include "../core/log.h"
#include "../../config/model_config.h"
#ifdef SUPPORT_TONER_SAVE
#include "../features/eco/eco_mode.h"
#endif
#include "render.h"

int Render_Page(int density)
{
    Log_Info("render start");
#ifdef SUPPORT_TONER_SAVE
    density = EcoMode_ApplyDensity(density);
#endif
    Log_Info("render done");
    return density;
}
