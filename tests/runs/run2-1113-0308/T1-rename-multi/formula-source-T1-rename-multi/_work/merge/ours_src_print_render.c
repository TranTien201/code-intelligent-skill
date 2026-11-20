#include "../core/log.h"
#include "../../config/model_config.h"
#include "render.h"

int Render_Page(int density)
{
    Log_Info("render start");
    Log_Info("render done");
#ifdef SUPPORT_FAX
    Log_Info("fax header");
#endif
    return density;
}
