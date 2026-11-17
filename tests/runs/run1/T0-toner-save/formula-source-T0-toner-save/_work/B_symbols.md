# B_symbols

## 1. Changed symbols
| S-id | symbol (kind) | file | H-ids | change type | behavior before → after | new tokens used |
|---|---|---|---|---|---|---|
| S001 | SRCS toner_save entry (N/A non-code file) | Makefile | H001 | registration | build did not compile toner_save.c → `SRCS += src/features/toner_save/toner_save.c` | SRCS |
| S002 | SUPPORT_TONER_SAVE (macro) | config/model_a.h | H002 | new | macro undefined → defined `1` for MODEL_A (enables guarded menu entry + render hook) | SUPPORT_TONER_SAVE |
| S003 | pjl_commands.c (file scope) | src/cmd/pjl_commands.c | H003 | new | adds unguarded `#include "../features/toner_save/toner_save.h"` | – |
| S004 | g_pjl_table (table) | src/cmd/pjl_commands.c | H004 | registration | 2 PJL cmds (COPIES, DUPLEX) → +`{ "ECONOMODE", TonerSave_PjlSet }` (unguarded) | TonerSave_PjlSet |
| S005 | toner_save.c (file scope) | src/features/toner_save/toner_save.c | H005 | new | new file includes stdlib, toner_save.h, nv_settings.h, density.h, log.h, strings.h (+ latest: math_util.h) | – |
| S006 | k_percent (table) | …/toner_save.c | H005 | new | none → `{100, 80, 60}` % per level OFF/LOW/HIGH | k_percent |
| S007 | is_valid@src/features/toner_save/toner_save.c (function) | …/toner_save.c | H005 | new | none → true iff `TONER_SAVE_OFF <= level <= TONER_SAVE_HIGH` (0..2) | is_valid |
| S008 | TonerSave_GetLevel (function) | …/toner_save.c | H005 | new | none → returns `NV_GetSettings()->toner_save_level` | NV_GetSettings, toner_save_level |
| S009 | TonerSave_ApplyDensity (function) | …/toner_save.c | H005 | new | none → if level valid returns `Density_Scale(density, k_percent[level])` else density unchanged; latest: level clamped to 0..2 first | Density_Scale, Clamp |
| S010 | TonerSave_MenuHandler (function) | …/toner_save.c | H005 | new | none → key outside 0..2 → -1; else stores key in NV toner_save_level, logs "Toner Save", returns key | Log_Info, Str_Get, STR_TONER_SAVE |
| S011 | TonerSave_PjlSet (function) | …/toner_save.c | H005 | new | none → `TonerSave_MenuHandler(atoi(arg))` | atoi |
| S012 | TONER_SAVE_H (preprocessor) | src/features/toner_save/toner_save.h | H006 | new | include guard of new header | TONER_SAVE_H |
| S013 | TONER_SAVE_OFF..TONER_SAVE_HIGH (enum) | …/toner_save.h | H006 | new | none → OFF=0, LOW=1, HIGH=2 | TONER_SAVE_* |
| S014 | TonerSave_GetLevel (prototype) | …/toner_save.h | H006 | new | `int TonerSave_GetLevel(void);` | – |
| S015 | TonerSave_ApplyDensity (prototype) | …/toner_save.h | H006 | new | `int TonerSave_ApplyDensity(int density);` | – |
| S016 | TonerSave_MenuHandler (prototype) | …/toner_save.h | H006 | new | `int TonerSave_MenuHandler(int key);` | – |
| S017 | TonerSave_PjlSet (prototype) | …/toner_save.h | H006 | new | `int TonerSave_PjlSet(const char *arg);` | – |
| S018 | SUPPORT_TONER_SAVE (preprocessor) @menu_table.c | src/panel/menu_table.c | H007 | guard | none → `#ifdef SUPPORT_TONER_SAVE #include toner_save.h #endif` | – |
| S019 | g_menu_table (table) | src/panel/menu_table.c | H007 | registration | menu COPIES, DUPLEX, QUALITY, LANGUAGE → + `{ "TONER_SAVE", TonerSave_MenuHandler }` after DUPLEX, under `#ifdef SUPPORT_TONER_SAVE` | TonerSave_MenuHandler |
| S020 | SUPPORT_TONER_SAVE (preprocessor) @render.c | src/print/render.c | H008 | guard | none → guarded include of toner_save.h | – |
| S021 | Render_Page (function) | src/print/render.c | H008 | logic | density passed through unchanged → under guard `density = TonerSave_ApplyDensity(density)` between the two Log_Info calls | TonerSave_ApplyDensity |
| S022 | StrId_t (enum) | src/resources/strings.h | H009 | layout | `STR_COPIES=0, STR_DUPLEX=1, STR_QUALITY=2, STR_COUNT=3` → `STR_TONER_SAVE=2` inserted; STR_QUALITY 2→3, STR_COUNT 3→4 | STR_TONER_SAVE |
| S023 | g_strings_en (table) | src/resources/strings_en.c | H010 | constant | + `[STR_TONER_SAVE] = "Toner Save"` (designated initializer) | STR_TONER_SAVE |
| S024 | nv_settings.c (file scope) | src/settings/nv_settings.c | H011 | new | adds unguarded include of toner_save.h (for TONER_SAVE_OFF) | – |
| S025 | NV_LoadDefaults (function) | src/settings/nv_settings.c | H012 | logic | defaults copies=1, duplex=0, language=0, quality=1 → + `toner_save_level = TONER_SAVE_OFF` (0) | g_settings, TONER_SAVE_OFF |
| S026 | NvSettings_t (struct) | src/settings/nv_settings.h | H013 | layout | fields copies,duplex,language,quality → `int toner_save_level` inserted after duplex; offsets of `language` 8→12, `quality` 12→16 (int=4); struct stored in NVRAM (comment SRC:src/settings/nv_settings.h:4) | toner_save_level |
No `ext` symbols (no EXTENSION_NEW found).

## 2. Dependencies
| S-id | dir (out/in) | dependency (kind) | defined at (SRC:path:line) | in diff? | note |
|---|---|---|---|---|---|
| S008.d1 | out | NV_GetSettings (function) | SRC:src/settings/nv_settings.c:6 (proto SRC:src/settings/nv_settings.h:13) | no | header nv_settings.h |
| S009.d1 | out | Density_Scale (function) | SRC:src/print/density.c:4 (proto SRC:src/print/density.h:4) | no | header density.h; build entry `src/print/density.c` SRC:Makefile:2 |
| S009.d2 | out | DENSITY_MAX (macro) | SRC:src/print/density.h:3 | no | recursion from Density_Scale body |
| S009.d3 | out | Clamp (function) | SRC:src/util/math_util.c:3 (proto SRC:src/util/math_util.h:3) | no (BUGFIX line) | also used by Density_Scale; build entry SRC:Makefile:2 |
| S010.d1 | out | Log_Info (function) | SRC:src/core/log.c:4 (proto SRC:src/core/log.h:3) | no | generic infrastructure – stop |
| S010.d2 | out | Str_Get (function) | SRC:src/resources/strings_en.c:10 (proto SRC:src/resources/strings.h:11) | no | |
| S011.d1 | out | atoi (library) | `<stdlib.h>` | no | standard library – stop |
| S018.d1 | out | model_config.h (header) | SRC:config/model_config.h:1-8; included SRC:src/panel/menu_table.c:3, SRC:src/print/render.c:2 | no | maps MODEL_A→model_a.h; MODEL_x from `-DMODEL_$(MODEL)` SRC:Makefile:10 |
| S019.d1 | out | MenuEntry_t (typedef) | SRC:src/panel/menu.h:4-7 | no | table type, handler `int (*)(int)` |
| S004.d1 | out | PjlEntry_t (typedef) | SRC:src/cmd/pjl_commands.c:7-10 | no | handler `int (*)(const char*)` |
| S010/S008 | in | g_menu_table entry → Menu_Dispatch | SRC:src/panel/menu_table.c:15, :24-32 | yes (S019) | needed-for-behavior (registration) |
| S011 | in | g_pjl_table entry → Pjl_Dispatch | SRC:src/cmd/pjl_commands.c:27, :30-38 | yes (S004) | needed-for-behavior (registration) |
| S009 | in | Render_Page call | SRC:src/print/render.c:12 | yes (S021) | needed-for-behavior |
| S008/S013 | in | EcoReport_Print | SRC:src/features/eco_report/eco_report.c:7 | no | CONSUMER (X1) – report only |
| – | in | main() calls Menu_Dispatch("TONER_SAVE"), Pjl_Dispatch("ECONOMODE"), Render_Page | SRC:src/main.c:11-13 | no | CONSUMER (driver) – report only |
Recursion: depth 2 (Density_Scale → DENSITY_MAX, Clamp); stop: Log_Info generic infrastructure (used in 5 files), libc.

## 3. Port version
| S-id | content source (SRC:path:lines) | includes blocks | excluded UNRELATED lines |
|---|---|---|---|
| S001 | SRC:Makefile:6 | request | SRC:Makefile:7 (eco_report) |
| S002 | SRC:config/model_a.h:3 | request | SRC:config/model_a.h:4 (SUPPORT_ECO_REPORT) |
| S003 | SRC:src/cmd/pjl_commands.c:4 | request | – |
| S004 | SRC:src/cmd/pjl_commands.c:27 | request | – |
| S005 | SRC:src/features/toner_save/toner_save.c:1-8 | request + BUGFIX L7 | – |
| S006-S011 | SRC:src/features/toner_save/toner_save.c:9-42 | request + BUGFIX L24 | – |
| S012-S017 | SRC:src/features/toner_save/toner_save.h:1-13 | request | – |
| S018 | SRC:src/panel/menu_table.c:4-6 | request | SRC:src/panel/menu_table.c:7-9 (ECO include) |
| S019 | SRC:src/panel/menu_table.c:14-16 | request (partial take) | SRC:src/panel/menu_table.c:19-21 |
| S020 | SRC:src/print/render.c:3-5 | request | – |
| S021 | SRC:src/print/render.c:11-13 | request | – |
| S022 | SRC:src/resources/strings.h:6 | request | – |
| S023 | SRC:src/resources/strings_en.c:6 | request | – |
| S024 | SRC:src/settings/nv_settings.c:2 | request | – |
| S025 | SRC:src/settings/nv_settings.c:15 | request | – |
| S026 | SRC:src/settings/nv_settings.h:8 | request | – |
Whole new files toner_save.c / toner_save.h = latest SRC files verbatim (no UNRELATED blocks).

## 3b. Data dependencies (R13, all file types searched with `grep -rnI`)
| S-id | kind | item | places in source (SRC:path:line, all of them) |
|---|---|---|---|
| S022/S023 | string ID | STR_TONER_SAVE | SRC:src/resources/strings.h:6; SRC:src/resources/strings_en.c:6 (only language table; `grep g_strings_` → strings_en only) |
| S022 | enum entry | StrId_t / STR_COUNT sizing | SRC:src/resources/strings_en.c:3 `g_strings_en[STR_COUNT]` (designated initializers → value shift safe in table); no switch over StrId_t |
| S026/S025 | settings/NVRAM field | toner_save_level | SRC:src/settings/nv_settings.h:8 (field); SRC:src/settings/nv_settings.c:15 (default); no version/CRC/checksum/migration found (`grep -niE 'version|crc|checksum|migrat'` → none) |
| S019/S004 | registry entry | menu "TONER_SAVE", PJL "ECONOMODE" | SRC:src/panel/menu_table.c:15; SRC:src/cmd/pjl_commands.c:27 |
| S002 | config macro | SUPPORT_TONER_SAVE | SRC:config/model_a.h:3 (via SRC:config/model_config.h:3-4 when MODEL_A); uses SRC:src/panel/menu_table.c:4,14; SRC:src/print/render.c:3,11 |
| S001 | build entry | toner_save.c | SRC:Makefile:6 |
| – | data/resource files | none | none found |

## Guards / headers
- Guard SUPPORT_TONER_SAVE: S018, S019 (menu entry), S020, S021 (render hook). Enabled SRC:config/model_a.h:3. Unguarded uses: S003/S004 (pjl), S024/S025 (nv_settings), S026 field.
- Headers: toner_save.h included by pjl_commands.c:4, nv_settings.c:2, menu_table.c:5 (guarded), render.c:4 (guarded), eco_report.c:2 (consumer).

## 4. Tests
none found (searched: `find -type d -iname 'test*' -o -iname 'unittest*' -o -iname ut`; `grep -rlw TonerSave_* | grep -iE 'test|_ut|spec'`). Runtime driver only: SRC:src/main.c:11-13.
