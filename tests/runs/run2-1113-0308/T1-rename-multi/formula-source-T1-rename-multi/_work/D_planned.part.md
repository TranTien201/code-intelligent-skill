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
