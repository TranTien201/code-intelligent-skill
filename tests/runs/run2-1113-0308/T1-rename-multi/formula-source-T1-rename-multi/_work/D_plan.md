# D_plan

## Formula Mapping Matrix
| M-id | Formula (source behavior) | S-ids / H-ids | Request location | Latest source location | Target location | Target state | Port class | P-ids | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| M001 | F1 eco module: level get/validate, density scaling, menu/PJL handlers | S005–S011 / H005 | REQ-A:src/features/toner_save/toner_save.c:1-40 | SRC:src/features/eco/eco_mode.c:1-20,28-48 | `src/features/eco/eco_mode.c` (new) | MISSING | COPY_NEW (row 7) | P007 | High |
| M002 | F1 level clamp before scaling (fix #1234) | S027 (ext) | – | SRC:src/features/eco/eco_mode.c:21-27 | `src/features/eco/eco_mode.c` (new) | MISSING | COPY_NEW (row 7), flag `ext` – scope beyond request | P008 | High |
| M003 | F1 module interface: guard, level enum OFF/LOW/HIGH, 4 prototypes | S012–S017 / H006 | REQ-A:src/features/toner_save/toner_save.h:1-13 | SRC:src/features/eco/eco_mode.h:1-13 | `src/features/eco/eco_mode.h` (new) | MISSING | COPY_NEW (row 7) | P006 | High |
| M004 | F3 density scaling helper | S009.d1–d3 | – | SRC:src/print/density.c:1-7, SRC:src/print/density.h:1-5 | `src/print/density.{c,h}` (new) | MISSING | COPY_DEPENDENCY (row 8) | P004, P005 | High |
| M005 | F3 Clamp(v, lo, hi) used by fix #1234 and Density_Scale | S027.d1 | – | SRC:src/util/math_util.c:3-8, SRC:src/util/math_util.h:3 | TGT:src/util/math_util.c:3-8, TGT:src/util/math_util.h:3 | SIGNATURE_DIFF (no target callers) | REPLACE (row 14) | P002, P003 | High |
| M006 | F7 feature enabled for the model | S002 / H002 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 | TGT:config/model_b.h:1-3 | MISSING | ENABLE_GUARD (row 11) – AUTO-DECIDED (row 7 not usable: model_a.h is MODEL_A-only, absent in target) | P001 | High |
| M007 | F8 build eco module | S001 / H001 | REQ-A:Makefile:6 | SRC:Makefile:6 | TGT:Makefile:1-8 | DIVERGED | TAKE_LATEST_PARTIAL (row 5) – AUTO-DECIDED (exclude SRC:Makefile:7) | P020 | High |
| M008 | F8 build density helper | S009.d4 | – | SRC:Makefile:2 | TGT:Makefile:2-5 | MISSING | NON_CODE (row 18) | P021 | High |
| M009 | F2 PJL module sees feature header | S003 / H003 | REQ-A:src/cmd/pjl_commands.c:4 | SRC:src/cmd/pjl_commands.c:4 | TGT:src/cmd/pjl_commands.c:1-3 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P014 | High |
| M010 | F2 PJL "ECONOMODE" → EcoMode_PjlSet | S004 / H004 | REQ-A:src/cmd/pjl_commands.c:27 | SRC:src/cmd/pjl_commands.c:27 | TGT:src/cmd/pjl_commands.c:23-26 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P015 | High |
| M011 | F1 menu module sees feature header (guarded) | S018 / H007 | REQ-A:src/panel/menu_table.c:4-6 | SRC:src/panel/menu_table.c:4-6 | TGT:src/panel/menu_table.c:1-3 | SAME_AS_BEFORE | TAKE_LATEST_PARTIAL (row 5) – AUTO-DECIDED (exclude SRC:src/panel/menu_table.c:7-9) | P016 | High |
| M012 | F1 menu "TONER_SAVE" → EcoMode_MenuHandler (guarded) | S019 / H007 | REQ-A:src/panel/menu_table.c:11-13 | SRC:src/panel/menu_table.c:14-16 | TGT:src/panel/menu_table.c:5-11 | DIVERGED | TAKE_LATEST_PARTIAL (row 5) – AUTO-DECIDED (exclude SRC:src/panel/menu_table.c:19-21; merge keeps FAX) | P017 | High |
| M013 | F3 render module sees feature header (guarded) | S020 / H008 | REQ-A:src/print/render.c:3-5 | SRC:src/print/render.c:3-5 | TGT:src/print/render.c:1-3 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P018 | High |
| M014 | F3 Render_Page applies eco density | S021 / H008 | REQ-A:src/print/render.c:11-13 | SRC:src/print/render.c:11-13 | TGT:src/print/render.c:5-13 | DIVERGED | ADAPT_MERGE (row 12) | P019 | High |
| M015 | F5 string ID STR_TONER_SAVE | S022 / H009 | REQ-A:src/resources/strings.h:6 | SRC:src/resources/strings.h:6 | TGT:src/resources/strings.h:3-9 | DIVERGED | ADAPT_MERGE (row 12); layout shift → HIGH risk (row 15 noted) | P010 | High |
| M016 | F5 English text "Toner Save" | S023 / H010 | REQ-A:src/resources/strings_en.c:6 | SRC:src/resources/strings_en.c:6 | TGT:src/resources/strings_en.c:3-8 | DIVERGED | ADAPT_MERGE (row 12) | P011 | High |
| M017 | F6 NV module sees feature header | S024 / H011 | REQ-A:src/settings/nv_settings.c:2 | SRC:src/settings/nv_settings.c:2 | TGT:src/settings/nv_settings.c:1 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P012 | High |
| M018 | F6 default eco_level = TONER_SAVE_OFF | S025 / H012 | REQ-A:src/settings/nv_settings.c:15 | SRC:src/settings/nv_settings.c:15 | TGT:src/settings/nv_settings.c:10-17 | DIVERGED | ADAPT_MERGE (row 12) | P013 | High |
| M019 | F6 NV field eco_level | S026 / H013 | REQ-A:src/settings/nv_settings.h:8 | SRC:src/settings/nv_settings.h:8 | TGT:src/settings/nv_settings.h:5-11 | DIVERGED | ADAPT_MERGE (row 12); NVRAM layout shift → HIGH risk (row 15 noted) | P009 | High |
| M020 | infrastructure already present | S008.d1, S010.d1, S010.d2 | – | SRC:src/settings/nv_settings.c:6, SRC:src/core/log.c:4, SRC:src/resources/strings_en.c:10 | TGT:src/settings/nv_settings.c:5, TGT:src/core/log.c:4, TGT:src/resources/strings_en.c:10 | SAME_AS_SOURCE | SKIP_ALREADY_PRESENT (row 4) | – | High |
| M021 | consumers: eco_report feature, main driver | B4 CONSUMER hits | – | SRC:src/features/eco_report/eco_report.c:5-15, SRC:src/main.c:11-13 | (eco_report absent; TGT:src/main.c:11-13 identical) | – | REPORT_ONLY (row 16) | – | High |

## Planned Changes
| P-id | Target file | Action | Anchor (exact target text or line) | Content source | Adaptation | Label |
|---|---|---|---|---|---|---|
| P001 | `config/model_b.h` | add-define | TGT:config/model_b.h:3 `#define SUPPORT_FAX 1` | SRC:config/model_a.h:3 | position AUTO-DECIDED: appended after last feature define (TGT:config/model_b.h:3); request also appended at end of model_a.h | none |
| P002 | `src/util/math_util.h` | replace | TGT:src/util/math_util.h:3 `int Clamp(int v, int hi);` | SRC:src/util/math_util.h:3 | none (REPLACE row 14: target prototype `int Clamp(int v, int hi);` replaced) | none |
| P003 | `src/util/math_util.c` | replace | TGT:src/util/math_util.c:3 `int Clamp(int v, int hi)` | SRC:src/util/math_util.c:3-5 | none (REPLACE row 14: target L3-5 replaced; L4 `{` identical) | none |
| P004 | `src/print/density.h` | add-file | (new file) | SRC:src/print/density.h:1-5 | none | none |
| P005 | `src/print/density.c` | add-file | (new file) | SRC:src/print/density.c:1-7 | none | none |
| P006 | `src/features/eco/eco_mode.h` | add-file | (new file) | SRC:src/features/eco/eco_mode.h:1-13 | none | none |
| P007 | `src/features/eco/eco_mode.c` | add-file | (new file) | SRC:src/features/eco/eco_mode.c:1-20,28-48 | none (file written together with P008 as SRC:src/features/eco/eco_mode.c:1-48) | none |
| P008 | `src/features/eco/eco_mode.c` | insert | (new file) | SRC:src/features/eco/eco_mode.c:21-27 | none; ext (scope beyond request), inserted between EcoMode_GetLevel and EcoMode_ApplyDensity as in source | none |
| P009 | `src/settings/nv_settings.h` | insert | TGT:src/settings/nv_settings.h:7 `    int duplex;` | SRC:src/settings/nv_settings.h:8 | none; target-only `fax_resolution` kept | none |
| P010 | `src/resources/strings.h` | insert | TGT:src/resources/strings.h:5 `    STR_DUPLEX,` | SRC:src/resources/strings.h:6 | none; target-only `STR_FAX` kept | none |
| P011 | `src/resources/strings_en.c` | insert | TGT:src/resources/strings_en.c:5 `    [STR_DUPLEX] = "2-Sided",` | SRC:src/resources/strings_en.c:6 | none; target-only `[STR_FAX]` kept | none |
| P012 | `src/settings/nv_settings.c` | add-include | TGT:src/settings/nv_settings.c:1 `#include "nv_settings.h"` | SRC:src/settings/nv_settings.c:2 | none | none |
| P013 | `src/settings/nv_settings.c` | insert | TGT:src/settings/nv_settings.c:13 `    g_settings.duplex = 0;` | SRC:src/settings/nv_settings.c:15 | none; target-only fax default kept | none |
| P014 | `src/cmd/pjl_commands.c` | add-include | TGT:src/cmd/pjl_commands.c:3 `#include "../core/log.h"` | SRC:src/cmd/pjl_commands.c:4 | none | none |
| P015 | `src/cmd/pjl_commands.c` | add-registration | TGT:src/cmd/pjl_commands.c:25 `    { "DUPLEX", Pjl_SetDuplex },` | SRC:src/cmd/pjl_commands.c:27 | none | none |
| P016 | `src/panel/menu_table.c` | add-include | TGT:src/panel/menu_table.c:3 `#include "../../config/model_config.h"` | SRC:src/panel/menu_table.c:4-6 | partial take: SRC:src/panel/menu_table.c:7-9 (eco_report include) excluded | none |
| P017 | `src/panel/menu_table.c` | add-registration | TGT:src/panel/menu_table.c:7 `    { "DUPLEX",   Menu_Duplex },` | SRC:src/panel/menu_table.c:14-16 | partial take: SRC:src/panel/menu_table.c:19-21 (ECO_REPORT entry) excluded; target-only FAX entry kept | none |
| P018 | `src/print/render.c` | add-include | TGT:src/print/render.c:2 `#include "../../config/model_config.h"` | SRC:src/print/render.c:3-5 | none | none |
| P019 | `src/print/render.c` | insert | TGT:src/print/render.c:7 `    Log_Info("render start");` | SRC:src/print/render.c:11-13 | none; target-only SUPPORT_FAX block kept after "render done" | none |
| P020 | `Makefile` | add-to-build | TGT:Makefile:5 `       src/cmd/pjl_commands.c src/resources/strings_en.c` | SRC:Makefile:6 | partial take: SRC:Makefile:7 (eco_report.c) excluded | none |
| P021 | `Makefile` | add-to-build | TGT:Makefile:5 `       src/cmd/pjl_commands.c src/resources/strings_en.c` | SRC:Makefile:2 (density.c entry) | AUTO-DECIDED: source lists density.c inside `SRCS =` (SRC:Makefile:2); added as own `SRCS +=` line after P020 so existing target lines stay untouched | none |

## Exact texts (insert after anchor line unless mode says otherwise; machine copy: D_plan.json)
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
