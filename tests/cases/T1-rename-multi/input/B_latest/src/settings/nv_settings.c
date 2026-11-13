#include "nv_settings.h"

static NvSettings_t g_settings;

NvSettings_t *NV_GetSettings(void)
{
    return &g_settings;
}

void NV_LoadDefaults(void)
{
    g_settings.copies = 1;
    g_settings.duplex = 0;
    g_settings.language = 0;
    g_settings.quality = 1;
    g_settings.fax_resolution = 200;
}
