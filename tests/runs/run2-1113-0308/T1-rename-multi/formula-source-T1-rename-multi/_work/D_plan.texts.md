### P001 (M006) – add-define config/model_b.h
- anchor: TGT:config/model_b.h:3 `#define SUPPORT_FAX 1`
- mode: insert-after
- content source: SRC:config/model_a.h:3
- adaptation: position AUTO-DECIDED: appended after last feature define (TGT:config/model_b.h:3); request also appended at end of model_a.h
- label: none
```c
#define SUPPORT_TONER_SAVE 1
```

### P002 (M005) – replace src/util/math_util.h
- anchor: TGT:src/util/math_util.h:3 `int Clamp(int v, int hi);`
- mode: replace
- content source: SRC:src/util/math_util.h:3
- adaptation: none (REPLACE row 14: target prototype `int Clamp(int v, int hi);` replaced)
- label: none
```c
int Clamp(int v, int lo, int hi);
```

### P003 (M005) – replace src/util/math_util.c
- anchor: TGT:src/util/math_util.c:3 `int Clamp(int v, int hi)`
- mode: replace3
- content source: SRC:src/util/math_util.c:3-5
- adaptation: none (REPLACE row 14: target L3-5 replaced; L4 `{` identical)
- label: none
```c
int Clamp(int v, int lo, int hi)
{
    if (v < lo) return lo;
```

### P004 (M004) – add-file src/print/density.h
- anchor: (new file)
- mode: add-file
- content source: SRC:src/print/density.h:1-5
- adaptation: none
- label: none
```c
#ifndef DENSITY_H
#define DENSITY_H
#define DENSITY_MAX 15
int Density_Scale(int base, int percent);
#endif
```

### P005 (M004) – add-file src/print/density.c
- anchor: (new file)
- mode: add-file
- content source: SRC:src/print/density.c:1-7
- adaptation: none
- label: none
```c
#include "density.h"
#include "../util/math_util.h"

int Density_Scale(int base, int percent)
{
    return Clamp(base * percent / 100, 0, DENSITY_MAX);
}
```

### P006 (M003) – add-file src/features/eco/eco_mode.h
- anchor: (new file)
- mode: add-file
- content source: SRC:src/features/eco/eco_mode.h:1-13
- adaptation: none
- label: none
```c
#ifndef ECO_MODE_H
#define ECO_MODE_H
enum {
    TONER_SAVE_OFF = 0,
    TONER_SAVE_LOW = 1,
    TONER_SAVE_HIGH = 2
};

int EcoMode_GetLevel(void);
int EcoMode_ApplyDensity(int density);
int EcoMode_MenuHandler(int key);
int EcoMode_PjlSet(const char *arg);
#endif
```

### P007 (M001) – add-file src/features/eco/eco_mode.c
- anchor: (new file)
- mode: add-file
- content source: SRC:src/features/eco/eco_mode.c:1-20,28-48
- adaptation: none (file written together with P008 as SRC:src/features/eco/eco_mode.c:1-48)
- label: none
```c
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
```

### P008 (M002) – insert src/features/eco/eco_mode.c
- anchor: P007 file, after SRC line 20 (blank after EcoMode_GetLevel) – new file
- mode: ext-in-file
- content source: SRC:src/features/eco/eco_mode.c:21-27
- adaptation: none; ext (scope beyond request), inserted between EcoMode_GetLevel and EcoMode_ApplyDensity as in source
- label: none
```c
static int eco_effective_level(void)
{
    int level = EcoMode_GetLevel();
    level = Clamp(level, TONER_SAVE_OFF, TONER_SAVE_HIGH); /* fix #1234: NV value hong */
    return is_valid(level) ? level : -1;
}

```

### P009 (M019) – insert src/settings/nv_settings.h
- anchor: TGT:src/settings/nv_settings.h:7 `    int duplex;`
- mode: insert-after
- content source: SRC:src/settings/nv_settings.h:8
- adaptation: none; target-only `fax_resolution` kept
- label: none
```c
    int eco_level;
```

### P010 (M015) – insert src/resources/strings.h
- anchor: TGT:src/resources/strings.h:5 `    STR_DUPLEX,`
- mode: insert-after
- content source: SRC:src/resources/strings.h:6
- adaptation: none; target-only `STR_FAX` kept
- label: none
```c
    STR_TONER_SAVE,
```

### P011 (M016) – insert src/resources/strings_en.c
- anchor: TGT:src/resources/strings_en.c:5 `    [STR_DUPLEX] = "2-Sided",`
- mode: insert-after
- content source: SRC:src/resources/strings_en.c:6
- adaptation: none; target-only `[STR_FAX]` kept
- label: none
```c
    [STR_TONER_SAVE] = "Toner Save",
```

### P012 (M017) – add-include src/settings/nv_settings.c
- anchor: TGT:src/settings/nv_settings.c:1 `#include "nv_settings.h"`
- mode: insert-after
- content source: SRC:src/settings/nv_settings.c:2
- adaptation: none
- label: none
```c
#include "../features/eco/eco_mode.h"
```

### P013 (M018) – insert src/settings/nv_settings.c
- anchor: TGT:src/settings/nv_settings.c:13 `    g_settings.duplex = 0;`
- mode: insert-after
- content source: SRC:src/settings/nv_settings.c:15
- adaptation: none; target-only fax default kept
- label: none
```c
    g_settings.eco_level = TONER_SAVE_OFF;
```

### P014 (M009) – add-include src/cmd/pjl_commands.c
- anchor: TGT:src/cmd/pjl_commands.c:3 `#include "../core/log.h"`
- mode: insert-after
- content source: SRC:src/cmd/pjl_commands.c:4
- adaptation: none
- label: none
```c
#include "../features/eco/eco_mode.h"
```

### P015 (M010) – add-registration src/cmd/pjl_commands.c
- anchor: TGT:src/cmd/pjl_commands.c:25 `    { "DUPLEX", Pjl_SetDuplex },`
- mode: insert-after
- content source: SRC:src/cmd/pjl_commands.c:27
- adaptation: none
- label: none
```c
    { "ECONOMODE", EcoMode_PjlSet },
```

### P016 (M011) – add-include src/panel/menu_table.c
- anchor: TGT:src/panel/menu_table.c:3 `#include "../../config/model_config.h"`
- mode: insert-after
- content source: SRC:src/panel/menu_table.c:4-6
- adaptation: partial take: SRC:src/panel/menu_table.c:7-9 (eco_report include) excluded
- label: none
```c
#ifdef SUPPORT_TONER_SAVE
#include "../features/eco/eco_mode.h"
#endif
```

### P017 (M012) – add-registration src/panel/menu_table.c
- anchor: TGT:src/panel/menu_table.c:7 `    { "DUPLEX",   Menu_Duplex },`
- mode: insert-after
- content source: SRC:src/panel/menu_table.c:14-16
- adaptation: partial take: SRC:src/panel/menu_table.c:19-21 (ECO_REPORT entry) excluded; target-only FAX entry kept
- label: none
```c
#ifdef SUPPORT_TONER_SAVE
    { "TONER_SAVE", EcoMode_MenuHandler },
#endif
```

### P018 (M013) – add-include src/print/render.c
- anchor: TGT:src/print/render.c:2 `#include "../../config/model_config.h"`
- mode: insert-after
- content source: SRC:src/print/render.c:3-5
- adaptation: none
- label: none
```c
#ifdef SUPPORT_TONER_SAVE
#include "../features/eco/eco_mode.h"
#endif
```

### P019 (M014) – insert src/print/render.c
- anchor: TGT:src/print/render.c:7 `    Log_Info("render start");`
- mode: insert-after
- content source: SRC:src/print/render.c:11-13
- adaptation: none; target-only SUPPORT_FAX block kept after "render done"
- label: none
```c
#ifdef SUPPORT_TONER_SAVE
    density = EcoMode_ApplyDensity(density);
#endif
```

### P020 (M007) – add-to-build Makefile
- anchor: TGT:Makefile:5 `       src/cmd/pjl_commands.c src/resources/strings_en.c`
- mode: insert-after
- content source: SRC:Makefile:6
- adaptation: partial take: SRC:Makefile:7 (eco_report.c) excluded
- label: none
```c
SRCS += src/features/eco/eco_mode.c
```

### P021 (M008) – add-to-build Makefile
- anchor: TGT:Makefile:5 `       src/cmd/pjl_commands.c src/resources/strings_en.c`
- mode: insert-after-P020
- content source: SRC:Makefile:2 (density.c entry)
- adaptation: AUTO-DECIDED: source lists density.c inside `SRCS =` (SRC:Makefile:2); added as own `SRCS +=` line after P020 so existing target lines stay untouched
- label: none
```c
SRCS += src/print/density.c
```
