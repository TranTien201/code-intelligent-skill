#include <stdlib.h>
#include "eco_mode.h"
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

int EcoMode_GetLevel(void)
{
    return NV_GetSettings()->eco_level;
}

static int eco_effective_level(void)
{
    int level = EcoMode_GetLevel();
    level = Clamp(level, TONER_SAVE_OFF, TONER_SAVE_HIGH); /* fix #1234: NV value hong */
    return is_valid(level) ? level : -1;
}

int EcoMode_ApplyDensity(int density)
{
    int level = eco_effective_level();
    if (level < 0)
        return density;
    return Density_Scale(density, k_percent[level]);
}

int EcoMode_MenuHandler(int key)
{
    if (!is_valid(key))
        return -1;
    NV_GetSettings()->eco_level = key;
    Log_Info(Str_Get(STR_TONER_SAVE));
    return key;
}

int EcoMode_PjlSet(const char *arg)
{
    return EcoMode_MenuHandler(atoi(arg));
}
