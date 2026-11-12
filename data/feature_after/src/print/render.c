#include "../core/log.h"
#include "../../config/model_config.h"
#ifdef SUPPORT_TONER_SAVE
#include "../features/toner_save/toner_save.h"
#endif
#include "render.h"

int Render_Page(int density)
{
    Log_Info("render start");
#ifdef SUPPORT_TONER_SAVE
    density = TonerSave_ApplyDensity(density);
#endif
    Log_Info("render done");
    return density;
}
