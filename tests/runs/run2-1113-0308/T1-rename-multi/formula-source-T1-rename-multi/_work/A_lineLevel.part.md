#### `config/model_a.h`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H002 |  | L3: `#define SUPPORT_TONER_SAVE 1` |

#### `src/cmd/pjl_commands.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H003 |  | L4: `#include "../features/toner_save/toner_save.h"` |
| H004 |  | L27: `    { "ECONOMODE", TonerSave_PjlSet },` |

#### `src/features/toner_save/toner_save.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H005 |  | L1: `#include <stdlib.h>` |
| H005 |  | L2: `#include "toner_save.h"` |
| H005 |  | L3: `#include "../../settings/nv_settings.h"` |
| H005 |  | L4: `#include "../../print/density.h"` |
| H005 |  | L5: `#include "../../core/log.h"` |
| H005 |  | L6: `#include "../../resources/strings.h"` |
| H005 |  | L7: (blank) |
| H005 |  | L8: `static const int k_percent[] = { 100, 80, 60 };` |
| H005 |  | L9: (blank) |
| H005 |  | L10: `static int is_valid(int level)` |
| H005 |  | L11: `{` |
| H005 |  | L12: `    return level >= TONER_SAVE_OFF && level <= TONER_SAVE_HIGH;` |
| H005 |  | L13: `}` |
| H005 |  | L14: (blank) |
| H005 |  | L15: `int TonerSave_GetLevel(void)` |
| H005 |  | L16: `{` |
| H005 |  | L17: `    return NV_GetSettings()->toner_save_level;` |
| H005 |  | L18: `}` |
| H005 |  | L19: (blank) |
| H005 |  | L20: `int TonerSave_ApplyDensity(int density)` |
| H005 |  | L21: `{` |
| H005 |  | L22: `    int level = TonerSave_GetLevel();` |
| H005 |  | L23: `    if (!is_valid(level))` |
| H005 |  | L24: `        return density;` |
| H005 |  | L25: `    return Density_Scale(density, k_percent[level]);` |
| H005 |  | L26: `}` |
| H005 |  | L27: (blank) |
| H005 |  | L28: `int TonerSave_MenuHandler(int key)` |
| H005 |  | L29: `{` |
| H005 |  | L30: `    if (!is_valid(key))` |
| H005 |  | L31: `        return -1;` |
| H005 |  | L32: `    NV_GetSettings()->toner_save_level = key;` |
| H005 |  | L33: `    Log_Info(Str_Get(STR_TONER_SAVE));` |
| H005 |  | L34: `    return key;` |
| H005 |  | L35: `}` |
| H005 |  | L36: (blank) |
| H005 |  | L37: `int TonerSave_PjlSet(const char *arg)` |
| H005 |  | L38: `{` |
| H005 |  | L39: `    return TonerSave_MenuHandler(atoi(arg));` |
| H005 |  | L40: `}` |

#### `src/features/toner_save/toner_save.h`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H006 |  | L1: `#ifndef TONER_SAVE_H` |
| H006 |  | L2: `#define TONER_SAVE_H` |
| H006 |  | L3: `enum {` |
| H006 |  | L4: `    TONER_SAVE_OFF = 0,` |
| H006 |  | L5: `    TONER_SAVE_LOW = 1,` |
| H006 |  | L6: `    TONER_SAVE_HIGH = 2` |
| H006 |  | L7: `};` |
| H006 |  | L8: (blank) |
| H006 |  | L9: `int TonerSave_GetLevel(void);` |
| H006 |  | L10: `int TonerSave_ApplyDensity(int density);` |
| H006 |  | L11: `int TonerSave_MenuHandler(int key);` |
| H006 |  | L12: `int TonerSave_PjlSet(const char *arg);` |
| H006 |  | L13: `#endif` |

#### `src/panel/menu_table.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H007 |  | L4: `#ifdef SUPPORT_TONER_SAVE` |
| H007 |  | L5: `#include "../features/toner_save/toner_save.h"` |
| H007 |  | L6: `#endif` |
| H007 |  | L11: `#ifdef SUPPORT_TONER_SAVE` |
| H007 |  | L12: `    { "TONER_SAVE", TonerSave_MenuHandler },` |
| H007 |  | L13: `#endif` |

#### `src/print/render.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H008 |  | L3: `#ifdef SUPPORT_TONER_SAVE` |
| H008 |  | L4: `#include "../features/toner_save/toner_save.h"` |
| H008 |  | L5: `#endif` |
| H008 |  | L11: `#ifdef SUPPORT_TONER_SAVE` |
| H008 |  | L12: `    density = TonerSave_ApplyDensity(density);` |
| H008 |  | L13: `#endif` |

#### `src/resources/strings.h`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H009 |  | L6: `    STR_TONER_SAVE,` |

#### `src/resources/strings_en.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H010 |  | L6: `    [STR_TONER_SAVE] = "Toner Save",` |

#### `src/settings/nv_settings.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H011 |  | L2: `#include "../features/toner_save/toner_save.h"` |
| H012 |  | L15: `    g_settings.toner_save_level = TONER_SAVE_OFF;` |

#### `src/settings/nv_settings.h`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H013 |  | L8: `    int toner_save_level;` |
