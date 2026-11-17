#include <stdlib.h>
#include "toner_save.h"
#include "../../settings/nv_settings.h"
#include "../../print/density.h"
#include "../../core/log.h"
#include "../../resources/strings.h"
#include "../../util/math_util.h"

static const int k_percent[] = { 100, 80, 60 };

static int is_valid(int level)
{
    return level >= TONER_SAVE_OFF && level <= TONER_SAVE_HIGH;
}

int TonerSave_GetLevel(void)
{
    return NV_GetSettings()->toner_save_level;
}

int TonerSave_ApplyDensity(int density)
{
    int level = TonerSave_GetLevel();
    level = Clamp(level, TONER_SAVE_OFF, TONER_SAVE_HIGH); /* fix #1234: NV value hong */
    if (!is_valid(level))
        return density;
    return Density_Scale(density, k_percent[level]);
}

int TonerSave_MenuHandler(int key)
{
    if (!is_valid(key))
        return -1;
    NV_GetSettings()->toner_save_level = key;
    Log_Info(Str_Get(STR_TONER_SAVE));
    return key;
}

int TonerSave_PjlSet(const char *arg)
{
    return TonerSave_MenuHandler(atoi(arg));
}
