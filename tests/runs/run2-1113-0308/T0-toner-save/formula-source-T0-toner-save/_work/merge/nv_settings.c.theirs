#include "nv_settings.h"
#include "../features/toner_save/toner_save.h"

static NvSettings_t g_settings;

NvSettings_t *NV_GetSettings(void)
{
    return &g_settings;
}

void NV_LoadDefaults(void)
{
    g_settings.copies = 1;
    g_settings.duplex = 0;
    g_settings.toner_save_level = TONER_SAVE_OFF;
    g_settings.language = 0;
    g_settings.quality = 1;
}
