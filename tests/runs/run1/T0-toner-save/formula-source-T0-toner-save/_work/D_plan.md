# D_plan

## Formula Mapping Matrix
| M-id | Formula (source behavior) | S-ids / H-ids | Request location | Latest source location | Target location | Target state | Port class | P-ids | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| M001 | build toner_save.c | S001 / H001 | REQ-A:Makefile:6 | SRC:Makefile:6 | TGT:Makefile:5 | MISSING | COPY_NEW (row 7) | P020 | High |
| M002 | enable feature for model (guard) | S002 / H002 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 | TGT:config/model_b.h:3 | MISSING | COPY_NEW (row 7); also row 11 ENABLE_GUARD → AUTO-DECIDED add | P007 | High |
| M003 | PJL include | S003 / H003 | REQ-A:src/cmd/pjl_commands.c:4 | SRC:src/cmd/pjl_commands.c:4 | TGT:src/cmd/pjl_commands.c:3 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P017 | High |
| M004 | PJL ECONOMODE registration | S004 / H004 | REQ-A:src/cmd/pjl_commands.c:27 | SRC:src/cmd/pjl_commands.c:27 | TGT:src/cmd/pjl_commands.c:23-26 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P018 | High |
| M005 | toner save logic (levels, density scaling, menu/PJL handlers, BUGFIX clamp) | S005–S011 / H005 | REQ-A:src/features/toner_save/toner_save.c:1-40 | SRC:src/features/toner_save/toner_save.c:1-42 | – | MISSING | COPY_NEW (row 7) | P006 | High |
| M006 | toner save API/enum | S012–S017 / H006 | REQ-A:src/features/toner_save/toner_save.h:1-13 | SRC:src/features/toner_save/toner_save.h:1-13 | – | MISSING | COPY_NEW (row 7) | P005 | High |
| M007 | menu include | S018 / H007 | REQ-A:src/panel/menu_table.c:4-6 | SRC:src/panel/menu_table.c:4-6 | TGT:src/panel/menu_table.c:3 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P015 | High |
| M008 | menu TONER_SAVE registration | S019 / H007 | REQ-A:src/panel/menu_table.c:11-13 | SRC:src/panel/menu_table.c:14-16 | TGT:src/panel/menu_table.c:5-11 | DIVERGED | TAKE_LATEST_PARTIAL (row 5) AUTO-DECIDED: exclude SRC:19-21; merge keeps TGT:10 FAX | P016 | High |
| M009 | render include | S020 / H008 | REQ-A:src/print/render.c:3-5 | SRC:src/print/render.c:3-5 | TGT:src/print/render.c:2 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P013 | High |
| M010 | apply toner save to page density | S021 / H008 | REQ-A:src/print/render.c:11-13 | SRC:src/print/render.c:11-13 | TGT:src/print/render.c:5-13 | DIVERGED | ADAPT_MERGE (row 12) | P014 | High |
| M011 | string ID STR_TONER_SAVE | S022 / H009 | REQ-A:src/resources/strings.h:6 | SRC:src/resources/strings.h:6 | TGT:src/resources/strings.h:3-9 | DIVERGED | ADAPT_MERGE (row 12); row 15 LAYOUT_RISK AUTO-DECIDED: port + HIGH risk | P008 | High |
| M012 | English text "Toner Save" | S023 / H010 | REQ-A:src/resources/strings_en.c:6 | SRC:src/resources/strings_en.c:6 | TGT:src/resources/strings_en.c:3-8 | DIVERGED | ADAPT_MERGE (row 12) | P009 | High |
| M013 | NV settings include | S024 / H011 | REQ-A:src/settings/nv_settings.c:2 | SRC:src/settings/nv_settings.c:2 | TGT:src/settings/nv_settings.c:1 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P011 | High |
| M014 | default level OFF | S025 / H012 | REQ-A:src/settings/nv_settings.c:15 | SRC:src/settings/nv_settings.c:15 | TGT:src/settings/nv_settings.c:10-17 | DIVERGED | ADAPT_MERGE (row 12) | P012 | High |
| M015 | NVRAM field toner_save_level | S026 / H013 | REQ-A:src/settings/nv_settings.h:8 | SRC:src/settings/nv_settings.h:8 | TGT:src/settings/nv_settings.h:5-11 | DIVERGED | ADAPT_MERGE (row 12); row 15 LAYOUT_RISK AUTO-DECIDED: port + HIGH risk | P010 | High |
| M016 | existing infrastructure | S008.d1, S010.d1, S010.d2, S011.d1, S018.d1, S019.d1, S004.d1 | – | SRC (see C_trace) | TGT same | SAME_AS_SOURCE | SKIP_ALREADY_PRESENT (row 4) | – | High |
| M017 | Density_Scale | S009.d1 | – | SRC:src/print/density.c:1-7 | – | MISSING | COPY_DEPENDENCY (row 8) | P002 | High |
| M018 | DENSITY_MAX + density.h | S009.d2, S009.d4 | – | SRC:src/print/density.h:1-5 | – | MISSING | COPY_DEPENDENCY (row 8) | P001 | High |
| M019 | Clamp 3-arg (used by BUGFIX line and Density_Scale) | S009.d3 | – | SRC:src/util/math_util.c:3-8, SRC:src/util/math_util.h:3 | TGT:src/util/math_util.c:3-8, TGT:src/util/math_util.h:3 | SIGNATURE_DIFF (no target callers) | REPLACE (row 14) | P003, P004 | High |
| M020 | build density.c | S009.d5 | – | SRC:Makefile:2 | TGT:Makefile:2 | MISSING | ADD_DATA (row 9, build entry) | P019 | High |
| M021 | eco_report feature, main.c driver | B4 hits X1, main.c | – | SRC:src/features/eco_report/*, SRC:src/main.c:11-13 | – | n/a | REPORT_ONLY (row 16) | – | High |

## Label convention
None found (searched R10 `(REQ|CR|PR|ECR|ECO|TICKET|ISSUE|BUG|FIX|MOD|CHG)[-_#: ]?[0-9]{2,}` on TGT → 0 hits). No labels added.

## Planned Changes
| P-id | Target file | Action | Anchor (exact target text or line) | Content source | Adaptation | Label |
|---|---|---|---|---|---|---|
| P001 | src/print/density.h | add-file | – | SRC:src/print/density.h:1-5 | none | none |
| P002 | src/print/density.c | add-file | – | SRC:src/print/density.c:1-7 | none | none |
| P003 | src/util/math_util.h | replace | TGT:src/util/math_util.h:3 `int Clamp(int v, int hi);` | SRC:src/util/math_util.h:3 | none | none |
| P004 | src/util/math_util.c | replace | TGT:src/util/math_util.c:3-8 `int Clamp(int v, int hi)` … `}` | SRC:src/util/math_util.c:3-8 | none | none |
| P005 | src/features/toner_save/toner_save.h | add-file | – | SRC:src/features/toner_save/toner_save.h:1-13 | none | none |
| P006 | src/features/toner_save/toner_save.c | add-file | – | SRC:src/features/toner_save/toner_save.c:1-42 | none | none |
| P007 | config/model_b.h | add-define | after TGT:config/model_b.h:3 `#define SUPPORT_FAX 1` | SRC:config/model_a.h:3 | file alias model_a.h→model_b.h (append at end as in source) | none |
| P008 | src/resources/strings.h | insert | after TGT:src/resources/strings.h:5 `    STR_DUPLEX,` | SRC:src/resources/strings.h:6 | none (3-way merge keeps STR_FAX) | none |
| P009 | src/resources/strings_en.c | insert | after TGT:src/resources/strings_en.c:5 `    [STR_DUPLEX] = "2-Sided",` | SRC:src/resources/strings_en.c:6 | none | none |
| P010 | src/settings/nv_settings.h | insert | after TGT:src/settings/nv_settings.h:7 `    int duplex;` | SRC:src/settings/nv_settings.h:8 | none (keeps fax_resolution) | none |
| P011 | src/settings/nv_settings.c | add-include | after TGT:src/settings/nv_settings.c:1 `#include "nv_settings.h"` | SRC:src/settings/nv_settings.c:2 | none | none |
| P012 | src/settings/nv_settings.c | insert | after TGT:src/settings/nv_settings.c:13 `    g_settings.duplex = 0;` | SRC:src/settings/nv_settings.c:15 | none | none |
| P013 | src/print/render.c | add-include | after TGT:src/print/render.c:2 `#include "../../config/model_config.h"` | SRC:src/print/render.c:3-5 | none | none |
| P014 | src/print/render.c | insert | after TGT:src/print/render.c:7 `    Log_Info("render start");` | SRC:src/print/render.c:11-13 | none (keeps SUPPORT_FAX block) | none |
| P015 | src/panel/menu_table.c | add-include | after TGT:src/panel/menu_table.c:3 `#include "../../config/model_config.h"` | SRC:src/panel/menu_table.c:4-6 | partial: SRC:7-9 (ECO include) excluded | none |
| P016 | src/panel/menu_table.c | add-registration | after TGT:src/panel/menu_table.c:7 `    { "DUPLEX",   Menu_Duplex },` | SRC:src/panel/menu_table.c:14-16 | partial: SRC:19-21 (ECO entry) excluded | none |
| P017 | src/cmd/pjl_commands.c | add-include | after TGT:src/cmd/pjl_commands.c:3 `#include "../core/log.h"` | SRC:src/cmd/pjl_commands.c:4 | none | none |
| P018 | src/cmd/pjl_commands.c | add-registration | after TGT:src/cmd/pjl_commands.c:25 `    { "DUPLEX", Pjl_SetDuplex },` | SRC:src/cmd/pjl_commands.c:27 | none | none |
| P019 | Makefile | add-to-build | replace TGT:Makefile:2 `SRCS = src/main.c src/core/log.c src/util/math_util.c \` | SRC:Makefile:2 | none (line becomes identical to SRC:Makefile:2) | none |
| P020 | Makefile | add-to-build | after TGT:Makefile:5 `       src/cmd/pjl_commands.c src/resources/strings_en.c` | SRC:Makefile:6 | none; SRC:Makefile:7 (eco_report) excluded | none |

## Exact text per P-id
### P001 (SRC:src/print/density.h:1-5)
```
#ifndef DENSITY_H
#define DENSITY_H
#define DENSITY_MAX 15
int Density_Scale(int base, int percent);
#endif
```
### P002 (SRC:src/print/density.c:1-7)
```
#include "density.h"
#include "../util/math_util.h"

int Density_Scale(int base, int percent)
{
    return Clamp(base * percent / 100, 0, DENSITY_MAX);
}
```
### P003 (SRC:src/util/math_util.h:3-3)
```
int Clamp(int v, int lo, int hi);
```
### P004 (SRC:src/util/math_util.c:3-8)
```
int Clamp(int v, int lo, int hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}
```
### P005 (SRC:src/features/toner_save/toner_save.h:1-13)
```
#ifndef TONER_SAVE_H
#define TONER_SAVE_H
enum {
    TONER_SAVE_OFF = 0,
    TONER_SAVE_LOW = 1,
    TONER_SAVE_HIGH = 2
};

int TonerSave_GetLevel(void);
int TonerSave_ApplyDensity(int density);
int TonerSave_MenuHandler(int key);
int TonerSave_PjlSet(const char *arg);
#endif
```
### P006 (SRC:src/features/toner_save/toner_save.c:1-42)
```
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
```
### P007 (SRC:config/model_a.h:3-3)
```
#define SUPPORT_TONER_SAVE 1
```
### P008 (SRC:src/resources/strings.h:6-6)
```
    STR_TONER_SAVE,
```
### P009 (SRC:src/resources/strings_en.c:6-6)
```
    [STR_TONER_SAVE] = "Toner Save",
```
### P010 (SRC:src/settings/nv_settings.h:8-8)
```
    int toner_save_level;
```
### P011 (SRC:src/settings/nv_settings.c:2-2)
```
#include "../features/toner_save/toner_save.h"
```
### P012 (SRC:src/settings/nv_settings.c:15-15)
```
    g_settings.toner_save_level = TONER_SAVE_OFF;
```
### P013 (SRC:src/print/render.c:3-5)
```
#ifdef SUPPORT_TONER_SAVE
#include "../features/toner_save/toner_save.h"
#endif
```
### P014 (SRC:src/print/render.c:11-13)
```
#ifdef SUPPORT_TONER_SAVE
    density = TonerSave_ApplyDensity(density);
#endif
```
### P015 (SRC:src/panel/menu_table.c:4-6)
```
#ifdef SUPPORT_TONER_SAVE
#include "../features/toner_save/toner_save.h"
#endif
```
### P016 (SRC:src/panel/menu_table.c:14-16)
```
#ifdef SUPPORT_TONER_SAVE
    { "TONER_SAVE", TonerSave_MenuHandler },
#endif
```
### P017 (SRC:src/cmd/pjl_commands.c:4-4)
```
#include "../features/toner_save/toner_save.h"
```
### P018 (SRC:src/cmd/pjl_commands.c:27-27)
```
    { "ECONOMODE", TonerSave_PjlSet },
```
### P019 (SRC:Makefile:2-2)
```
SRCS = src/main.c src/core/log.c src/util/math_util.c src/print/density.c \
```
### P020 (SRC:Makefile:6-6)
```
SRCS += src/features/toner_save/toner_save.c
```

## Snapshot plan
Before/ and After/ = full copy of TARGET_ROOT (no .git/build outputs present); they do not exist yet (nothing to replace).

## Validation plan
BUILD_CMD `make -s MODEL=B` in OUTPUT_ROOT/Before (baseline) and OUTPUT_ROOT/After; expected: exit 0, no new warnings (-Wall), binary `printer_B`. Run `./printer_B` in both (driver main.c prints toner_save/pjl/density). Fallback: `cc -fsyntax-only -Wall -DMODEL_B <SRCS>`. Diff `diff -ruN Before After > diffs/output.diff`, check only planned hunks.
