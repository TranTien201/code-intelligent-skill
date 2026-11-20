# B_symbols

## 1 – Changed symbols
| S-id | symbol (kind) | file | H-ids | change type | behavior before → after | new tokens used |
|---|---|---|---|---|---|---|
| S001 | N/A (non-code file) SRCS entry | Makefile | H001 | registration | build did not compile toner_save.c → `SRCS += src/features/toner_save/toner_save.c` | toner_save.c |
| S002 | SUPPORT_TONER_SAVE (macro) | config/model_a.h | H002 | guard | macro undefined → `#define SUPPORT_TONER_SAVE 1` for model A (enables menu entry + render hook) | SUPPORT_TONER_SAVE |
| S003 | includes@src/cmd/pjl_commands.c (file scope) | src/cmd/pjl_commands.c | H003 | new | no feature header → includes `../features/toner_save/toner_save.h` (unguarded) | toner_save.h |
| S004 | g_pjl_table (table) | src/cmd/pjl_commands.c | H004 | registration | PJL keywords COPIES, DUPLEX → + `"ECONOMODE"` → `TonerSave_PjlSet` (unguarded) | TonerSave_PjlSet |
| S005 | includes@src/features/toner_save/toner_save.c (file scope) | src/features/toner_save/toner_save.c | H005 | new | (new file) includes stdlib, toner_save.h, nv_settings.h, density.h, log.h, strings.h; latest adds math_util.h | density.h, math_util.h |
| S006 | k_percent (global) | src/features/toner_save/toner_save.c | H005 | new | none → density percent table {100, 80, 60} indexed by level OFF/LOW/HIGH | – |
| S007 | is_valid (function) | src/features/toner_save/toner_save.c | H005 | new | none → returns `TONER_SAVE_OFF <= level <= TONER_SAVE_HIGH` (0..2) | TONER_SAVE_OFF/HIGH |
| S008 | TonerSave_GetLevel (function) | toner_save.c/.h | H005, H006 | new | none → returns `NV_GetSettings()->toner_save_level` | NV_GetSettings, toner_save_level |
| S009 | TonerSave_ApplyDensity (function) | toner_save.c/.h | H005, H006 | new | none → level invalid → density unchanged; else `Density_Scale(density, k_percent[level])` (100/80/60 %); latest also clamps level to 0..2 first | Density_Scale, Clamp |
| S010 | TonerSave_MenuHandler (function) | toner_save.c/.h | H005, H006 | new | none → key outside 0..2 → -1; else stores key in `toner_save_level`, logs `Str_Get(STR_TONER_SAVE)` ("Toner Save"), returns key | Log_Info, Str_Get, STR_TONER_SAVE |
| S011 | TonerSave_PjlSet (function) | toner_save.c/.h | H005, H006 | new | none → `TonerSave_MenuHandler(atoi(arg))` | atoi |
| S012 | TONER_SAVE_H (preprocessor) | toner_save.h | H006 | new | none → include guard of toner_save.h | – |
| S013 | TONER_SAVE_OFF/LOW/HIGH (enum) | toner_save.h | H006 | new | none → OFF = 0, LOW = 1, HIGH = 2 | – |
| S014 | SUPPORT_TONER_SAVE@src/panel/menu_table.c (preprocessor) | src/panel/menu_table.c | H007 | guard | none → `#ifdef SUPPORT_TONER_SAVE` include toner_save.h | SUPPORT_TONER_SAVE |
| S015 | g_menu_table (table) | src/panel/menu_table.c | H007 | registration | menu COPIES, DUPLEX, QUALITY, LANGUAGE → + `"TONER_SAVE"` → `TonerSave_MenuHandler` after DUPLEX, under `#ifdef SUPPORT_TONER_SAVE` | TonerSave_MenuHandler |
| S016 | SUPPORT_TONER_SAVE@src/print/render.c (preprocessor) | src/print/render.c | H008 | guard | none → `#ifdef SUPPORT_TONER_SAVE` include toner_save.h | SUPPORT_TONER_SAVE |
| S017 | Render_Page (function) | src/print/render.c | H008 | logic | returns density unchanged → under guard `density = TonerSave_ApplyDensity(density)` between the two logs | TonerSave_ApplyDensity |
| S018 | StrId_t (enum) | src/resources/strings.h | H009 | layout | COPIES=0, DUPLEX=1, QUALITY=2, COUNT=3 → STR_TONER_SAVE=2 inserted; QUALITY 2→3, COUNT 3→4 | STR_TONER_SAVE |
| S019 | g_strings_en (table) | src/resources/strings_en.c | H010 | registration | + `[STR_TONER_SAVE] = "Toner Save"` (designated initializer) | STR_TONER_SAVE |
| S020 | includes@src/settings/nv_settings.c (file scope) | src/settings/nv_settings.c | H011 | new | + include toner_save.h (for TONER_SAVE_OFF) | toner_save.h |
| S021 | NV_LoadDefaults (function) | src/settings/nv_settings.c | H012 | logic | defaults copies=1, duplex=0, language=0, quality=1 → + `toner_save_level = TONER_SAVE_OFF` (0) after duplex | toner_save_level, TONER_SAVE_OFF |
| S022 | NvSettings_t (struct) | src/settings/nv_settings.h | H013 | layout | fields copies, duplex, language, quality → `int toner_save_level` inserted after duplex; language offset 8→12, quality 12→16 (int=4) – NVRAM struct | toner_save_level |

## 2 – Dependencies
| S-id | dir (out/in) | dependency (kind) | defined at (SRC:path:line) | in diff? | note |
|---|---|---|---|---|---|
| S009.d1 | out | Clamp (function) | SRC:src/util/math_util.c:3-8, proto SRC:src/util/math_util.h:3 | no | `int Clamp(int v, int lo, int hi)`; used by BUGFIX line SRC:…toner_save.c:24 and by Density_Scale |
| S009.d2 | out | Density_Scale (function) | SRC:src/print/density.c:4-7, proto SRC:src/print/density.h:4 | no | file pair density.c/.h; calls Clamp(…, 0, DENSITY_MAX) |
| S009.d3 | out | DENSITY_MAX (macro) | SRC:src/print/density.h:3 | no | = 15; used by Density_Scale |
| S009.d4 | out | density.h (header, guard DENSITY_H) | SRC:src/print/density.h:1-5 | no | included by toner_save.c L4 |
| S009.d5 | out | Makefile entry `src/print/density.c` (build) | SRC:Makefile:2 | no | density.c is compiled via the main SRCS list |
| S008.d1 | out | NV_GetSettings (function) | SRC:src/settings/nv_settings.c:6-9, proto SRC:src/settings/nv_settings.h:13 | no | infrastructure |
| S010.d1 | out | Log_Info (function) | SRC:src/core/log.c:4, proto SRC:src/core/log.h:3 | no | infrastructure |
| S010.d2 | out | Str_Get (function) | SRC:src/resources/strings_en.c:10-13, proto SRC:src/resources/strings.h:11 | no | infrastructure |
| S021.d1 | out | g_settings (global) | SRC:src/settings/nv_settings.c:4 | no | static NvSettings_t |
| S005.d1 | out | math_util.h (header) | SRC:src/util/math_util.h:1-4 | no | Clamp prototype |
| S005.d2 | out | log.h, strings.h, nv_settings.h (headers) | SRC:src/core/log.h, SRC:src/resources/strings.h, SRC:src/settings/nv_settings.h | no | existing headers |
| S015.d1 | out | model_config.h include (guard source) | SRC:src/panel/menu_table.c:3, SRC:config/model_config.h:3-7 | no | selects model_a.h/model_b.h by `-DMODEL_<X>` |
| S004.d1 | in | Pjl_Dispatch (function) | SRC:src/cmd/pjl_commands.c:30-38 | no | dispatches g_pjl_table by keyword; needed-for-behavior (already exists) |
| S015.d2 | in | Menu_Dispatch (function) | SRC:src/panel/menu_table.c:24-32 | no | dispatches g_menu_table; needed-for-behavior (already exists) |
| S017.d1 | in | main → Render_Page / Menu_Dispatch("TONER_SAVE") / Pjl_Dispatch("ECONOMODE") | SRC:src/main.c:11-13 | no | driver; CONSUMER (not ported) |
| S008.d2 | in | EcoReport_Print (function) | SRC:src/features/eco_report/eco_report.c:5-9 | no | CONSUMER → REPORT_ONLY |
| S009.d6 | in | Menu_Quality uses Density_Scale | SRC:src/panel/menu.c:22 | no | CONSUMER of dependency S009.d2 (other feature) → REPORT_ONLY |

Recursion: Density_Scale → Clamp, DENSITY_MAX (depth 2); Clamp body uses nothing project-specific → stop. NV_GetSettings/Log_Info/Str_Get: infrastructure already existing in REQ-B (stop).

## 3 – Port version
| S-id | content source (SRC:path:lines) | includes blocks | excluded UNRELATED lines |
|---|---|---|---|
| S001 | SRC:Makefile:6 | request | SRC:Makefile:7 (eco_report) |
| S002 | SRC:config/model_a.h:3 | request | SRC:config/model_a.h:4 (SUPPORT_ECO_REPORT) |
| S003 | SRC:src/cmd/pjl_commands.c:4 | request | – |
| S004 | SRC:src/cmd/pjl_commands.c:27 | request | – |
| S005–S011 | SRC:src/features/toner_save/toner_save.c:1-42 (whole file) | request + BUGFIX L7, L24 | – |
| S012–S013 | SRC:src/features/toner_save/toner_save.h:1-13 (whole file) | request | – |
| S014 | SRC:src/panel/menu_table.c:4-6 | request | SRC:src/panel/menu_table.c:7-9 |
| S015 | SRC:src/panel/menu_table.c:14-16 | request | SRC:src/panel/menu_table.c:19-21 (partial take) |
| S016 | SRC:src/print/render.c:3-5 | request | – |
| S017 | SRC:src/print/render.c:11-13 | request | – |
| S018 | SRC:src/resources/strings.h:6 | request | – |
| S019 | SRC:src/resources/strings_en.c:6 | request | – |
| S020 | SRC:src/settings/nv_settings.c:2 | request | – |
| S021 | SRC:src/settings/nv_settings.c:15 | request | – |
| S022 | SRC:src/settings/nv_settings.h:8 | request | – |
| S009.d1 | SRC:src/util/math_util.c:3-8, SRC:src/util/math_util.h:3 | dependency | – |
| S009.d2–d4 | SRC:src/print/density.c:1-7, SRC:src/print/density.h:1-5 | dependency | – |
| S009.d5 | SRC:Makefile:2 (`src/print/density.c` in SRCS) | dependency | – |

## 3b – Data dependencies (R13, all file types)
| S-id | kind | item | places in source (SRC:path:line, all of them) |
|---|---|---|---|
| S018/S019 | string-id | STR_TONER_SAVE | SRC:src/resources/strings.h:6 (enum), SRC:src/resources/strings_en.c:6 (only language table: `find -name 'strings_*'` → strings_en.c only), SRC:src/features/toner_save/toner_save.c:35 (use) |
| S018 | enum sizing | STR_COUNT-sized arrays | SRC:src/resources/strings_en.c:3 `g_strings_en[STR_COUNT]` (only array sized by StrId_t; designated initializers → order-safe) |
| S013 | enum entry | TONER_SAVE_OFF/LOW/HIGH | SRC:…toner_save.h:4-6; k_percent[3] SRC:…toner_save.c:9 (indexed by level); uses SRC:…toner_save.c:13,24; SRC:src/settings/nv_settings.c:15; SRC:src/features/eco_report/eco_report.c:7 (consumer) |
| S022/S021 | nv-field | toner_save_level | struct SRC:src/settings/nv_settings.h:8; default SRC:src/settings/nv_settings.c:15; read/write SRC:…toner_save.c:18,34. No NV version/checksum/migration found (`grep -rniE 'version|checksum|crc|migrat'` → none) |
| S004 | registry entry | "ECONOMODE" | SRC:src/cmd/pjl_commands.c:27; SRC:src/main.c:12 (driver use) |
| S015 | registry entry | "TONER_SAVE" | SRC:src/panel/menu_table.c:15; SRC:src/main.c:11 (driver use) |
| S002 | config macro | SUPPORT_TONER_SAVE | SRC:config/model_a.h:3 (only define); used SRC:src/panel/menu_table.c:4,14, SRC:src/print/render.c:3,11; no -D in Makefile |
| S001 | build entry | toner_save.c | SRC:Makefile:6 |
| S009.d5 | build entry | density.c | SRC:Makefile:2 |

## 4 – Tests
none found (searched: `find "$SOURCE_ROOT" -iname '*test*' -o -iname '*_ut*' -o -iname 'ut'` → 0; `grep -rlw TonerSave_* | grep -iE 'test|_ut|spec'` → 0). `SRC:src/main.c:9-14` is a smoke driver that exercises TONER_SAVE menu, ECONOMODE PJL and Render_Page.
