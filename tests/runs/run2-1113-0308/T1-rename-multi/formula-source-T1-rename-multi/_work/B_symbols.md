# B_symbols

## 1 – Changed symbols (request view + ext)
| S-id | symbol (kind) | file | H-ids | change type | behavior before → after | new tokens used |
|---|---|---|---|---|---|---|
| S001 | N/A (non-code file) Makefile | Makefile | H001 | registration | build list without toner_save.c → adds `SRCS += src/features/toner_save/toner_save.c` (latest: eco/eco_mode.c) | – |
| S002 | SUPPORT_TONER_SAVE (macro) | config/model_a.h | H002 | guard | macro undefined (feature compiled out) → defined `1` for model A | SUPPORT_TONER_SAVE |
| S003 | file scope@src/cmd/pjl_commands.c | src/cmd/pjl_commands.c | H003 | new | no feature header → includes toner_save.h (latest eco_mode.h) | – |
| S004 | g_pjl_table (table) | src/cmd/pjl_commands.c | H004 | registration | PJL `ECONOMODE` unknown (Pjl_Dispatch returns -1) → entry `{ "ECONOMODE", TonerSave_PjlSet }` | TonerSave_PjlSet |
| S005 | file scope@src/features/toner_save/toner_save.c | toner_save.c → eco/eco_mode.c | H005 | new | – → includes stdlib.h, own header, nv_settings.h, density.h, log.h, strings.h (latest + math_util.h) | – |
| S006 | k_percent (global) | toner_save.c → eco_mode.c | H005 | new | – → density percent per level {100, 80, 60} | – |
| S007 | is_valid@src/features/toner_save/toner_save.c (function) | toner_save.c → eco_mode.c | H005 | new | – → true when TONER_SAVE_OFF(0) ≤ level ≤ TONER_SAVE_HIGH(2) | TONER_SAVE_OFF, TONER_SAVE_HIGH |
| S008 | TonerSave_GetLevel → EcoMode_GetLevel (function) | toner_save.c → eco_mode.c | H005 | new | – → returns NV field toner_save_level (latest eco_level) | NV_GetSettings |
| S009 | TonerSave_ApplyDensity → EcoMode_ApplyDensity (function) | toner_save.c → eco_mode.c | H005 | new | – → if level invalid returns density unchanged, else Density_Scale(density, 100/80/60 %) ; latest: level clamped to 0..2 first (fix #1234) | Density_Scale, k_percent |
| S010 | TonerSave_MenuHandler → EcoMode_MenuHandler (function) | toner_save.c → eco_mode.c | H005 | new | – → key outside 0..2 → -1; else stores key in NV field, logs "Toner Save", returns key | Log_Info, Str_Get, STR_TONER_SAVE |
| S011 | TonerSave_PjlSet → EcoMode_PjlSet (function) | toner_save.c → eco_mode.c | H005 | new | – → atoi(arg) then MenuHandler | atoi |
| S012 | TONER_SAVE_H → ECO_MODE_H (preprocessor) | toner_save.h → eco/eco_mode.h | H006 | new | – → include guard | – |
| S013 | TONER_SAVE_OFF/LOW/HIGH (enum) | toner_save.h → eco_mode.h | H006 | new | – → OFF=0, LOW=1, HIGH=2 | – |
| S014 | TonerSave_GetLevel → EcoMode_GetLevel (prototype) | toner_save.h → eco_mode.h | H006 | new | – → `int …(void);` | – |
| S015 | TonerSave_ApplyDensity → EcoMode_ApplyDensity (prototype) | toner_save.h → eco_mode.h | H006 | new | – → `int …(int density);` | – |
| S016 | TonerSave_MenuHandler → EcoMode_MenuHandler (prototype) | toner_save.h → eco_mode.h | H006 | new | – → `int …(int key);` | – |
| S017 | TonerSave_PjlSet → EcoMode_PjlSet (prototype) | toner_save.h → eco_mode.h | H006 | new | – → `int …(const char *arg);` | – |
| S018 | file scope@src/panel/menu_table.c | src/panel/menu_table.c | H007 | guard | – → `#ifdef SUPPORT_TONER_SAVE` include of feature header | SUPPORT_TONER_SAVE |
| S019 | g_menu_table (table) | src/panel/menu_table.c | H007 | registration | menu "TONER_SAVE" unknown (Menu_Dispatch -1) → guarded entry `{ "TONER_SAVE", TonerSave_MenuHandler }` between DUPLEX and QUALITY | TonerSave_MenuHandler |
| S020 | file scope@src/print/render.c | src/print/render.c | H008 | guard | – → guarded include of feature header | – |
| S021 | Render_Page (function) | src/print/render.c | H008 | logic | returns density unchanged → (if SUPPORT_TONER_SAVE) density = TonerSave_ApplyDensity(density) before "render done" | TonerSave_ApplyDensity |
| S022 | StrId_t (enum) | src/resources/strings.h | H009 | layout | STR_COPIES=0, STR_DUPLEX=1, STR_QUALITY=2, STR_COUNT=3 → STR_TONER_SAVE=2 inserted; STR_QUALITY 2→3, STR_COUNT 3→4 | STR_TONER_SAVE |
| S023 | g_strings_en (table) | src/resources/strings_en.c | H010 | constant | – → `[STR_TONER_SAVE] = "Toner Save"` | – |
| S024 | file scope@src/settings/nv_settings.c | src/settings/nv_settings.c | H011 | new | – → includes feature header (for TONER_SAVE_OFF) | – |
| S025 | NV_LoadDefaults (function) | src/settings/nv_settings.c | H012 | logic | field not initialised → default toner_save_level (latest eco_level) = TONER_SAVE_OFF (0) | TONER_SAVE_OFF |
| S026 | NvSettings_t (struct) | src/settings/nv_settings.h | H013 | layout | {copies, duplex, language, quality} → int toner_save_level (latest eco_level) inserted after duplex: language offset 8→12, quality 12→16, sizeof 16→20 (int=4) | – |
| S027 | eco_effective_level (function) | SRC:src/features/eco/eco_mode.c:21-26 | ext | new | (latest only, BUGFIX fix #1234) level = Clamp(EcoMode_GetLevel(), 0, 2); return is_valid ? level : -1 | Clamp |

## 2 – Dependencies
| S-id | dir (out/in) | dependency (kind) | defined at (SRC:path:line) | in diff? | note |
|---|---|---|---|---|---|
| S008/S010 | out | S008.d1 NV_GetSettings (function) | SRC:src/settings/nv_settings.c:6 (proto SRC:src/settings/nv_settings.h:13) | no | |
| S009 | out | S009.d1 Density_Scale (function) | SRC:src/print/density.c:4 (proto SRC:src/print/density.h:4) | no | file src/print/density.c built at SRC:Makefile:2 |
| S009 | out | S009.d2 DENSITY_MAX (macro, via Density_Scale body) | SRC:src/print/density.h:3 | no | recursion depth 2 |
| S009 | out | S009.d3 density.h (header, file) | SRC:src/print/density.h:1-5 | no | included by SRC:src/features/eco/eco_mode.c:4 |
| S027 | out | S027.d1 Clamp (function) | SRC:src/util/math_util.c:3 (proto SRC:src/util/math_util.h:3) | no | also used by Density_Scale SRC:src/print/density.c:6 |
| S010 | out | S010.d1 Log_Info (function) | SRC:src/core/log.c:4 (proto SRC:src/core/log.h:3) | no | generic infrastructure (6 files) – stop |
| S010 | out | S010.d2 Str_Get (function) | SRC:src/resources/strings_en.c:10 (proto SRC:src/resources/strings.h:11) | no | |
| S011 | out | atoi (library) | <stdlib.h> | no | standard |
| S021 | in | Render_Page caller main | SRC:src/main.c:13 | no | CONSUMER of render (pre-existing) |
| S010 | in | g_menu_table entry "TONER_SAVE" | SRC:src/panel/menu_table.c:15 | yes (H007) | needed-for-behavior |
| S011 | in | g_pjl_table entry "ECONOMODE" | SRC:src/cmd/pjl_commands.c:27 | yes (H004) | needed-for-behavior |
| S009 | in | Render_Page call | SRC:src/print/render.c:12 | yes (H008) | needed-for-behavior |
| S008 | in | EcoReport_Print | SRC:src/features/eco_report/eco_report.c:7 | no | CONSUMER → REPORT_ONLY |
| S026 | in | NV_LoadDefaults default | SRC:src/settings/nv_settings.c:15 | yes (H012) | needed-for-behavior |
Recursion: depth 2 (Density_Scale → Clamp, DENSITY_MAX); stop: Log_Info generic (used in 6 files), nothing new below Clamp.

## 3 – Port version
| S-id | content source (SRC:path:lines) | includes blocks | excluded UNRELATED lines |
|---|---|---|---|
| S001 | SRC:Makefile:6 | REFACTOR (path) | SRC:Makefile:7 (eco_report, AUTO-DECIDED UNRELATED) |
| S002 | SRC:config/model_a.h:3 | – | SRC:config/model_a.h:4 (SUPPORT_ECO_REPORT) |
| S003 | SRC:src/cmd/pjl_commands.c:4 | REFACTOR (path) | – |
| S004 | SRC:src/cmd/pjl_commands.c:27 | REFACTOR (name) | – |
| S005 | SRC:src/features/eco/eco_mode.c:1-8 | BUGFIX (:7) | – |
| S006 | SRC:src/features/eco/eco_mode.c:9-10 | – | – |
| S007 | SRC:src/features/eco/eco_mode.c:11-15 | – | – |
| S008 | SRC:src/features/eco/eco_mode.c:16-20 | REFACTOR | – |
| S027 | SRC:src/features/eco/eco_mode.c:21-27 | BUGFIX | – |
| S009 | SRC:src/features/eco/eco_mode.c:28-35 | REFACTOR + BUGFIX | – |
| S010 | SRC:src/features/eco/eco_mode.c:36-44 | REFACTOR | – |
| S011 | SRC:src/features/eco/eco_mode.c:45-48 | REFACTOR | – |
| S012–S017 | SRC:src/features/eco/eco_mode.h:1-13 | REFACTOR | – |
| S018 | SRC:src/panel/menu_table.c:4-6 | REFACTOR (path) | SRC:src/panel/menu_table.c:7-9 (AUTO-DECIDED UNRELATED) |
| S019 | SRC:src/panel/menu_table.c:14-16 | REFACTOR (name) | SRC:src/panel/menu_table.c:19-21 (AUTO-DECIDED UNRELATED) |
| S020 | SRC:src/print/render.c:3-5 | REFACTOR (path) | – |
| S021 | SRC:src/print/render.c:11-13 | REFACTOR (name) | – |
| S022 | SRC:src/resources/strings.h:6 | – | – |
| S023 | SRC:src/resources/strings_en.c:6 | – | – |
| S024 | SRC:src/settings/nv_settings.c:2 | REFACTOR (path) | – |
| S025 | SRC:src/settings/nv_settings.c:15 | REFACTOR (field name) | – |
| S026 | SRC:src/settings/nv_settings.h:8 | REFACTOR (field name) | – |
Whole files eco_mode.c (48 lines) and eco_mode.h (13 lines) are port version without exclusions.

## 3b – Data dependencies (R13, all file types)
| S-id | kind | item | places in source (SRC:path:line, all of them) |
|---|---|---|---|
| S022/S023 | string-id | STR_TONER_SAVE | SRC:src/resources/strings.h:6 (enum), SRC:src/resources/strings_en.c:6 (only language table; `ls src/resources` = strings.h, strings_en.c), use SRC:src/features/eco/eco_mode.c:41 |
| S022 | enum entry (layout) | StrId_t values shift; arrays sized by STR_COUNT | SRC:src/resources/strings_en.c:3 `g_strings_en[STR_COUNT]` (only array; `grep -rnw STR_COUNT`) |
| S026/S025 | settings field | eco_level | struct SRC:src/settings/nv_settings.h:8; default SRC:src/settings/nv_settings.c:15; readers SRC:src/features/eco/eco_mode.c:18, :40; version/CRC/migration: none (`grep -rniE 'version\|crc\|checksum\|migrat'` → 0 hits) |
| S004 | registry entry | "ECONOMODE" → EcoMode_PjlSet | SRC:src/cmd/pjl_commands.c:27 |
| S019 | registry entry | "TONER_SAVE" → EcoMode_MenuHandler | SRC:src/panel/menu_table.c:15 (guarded :14-16) |
| S002 | config macro | SUPPORT_TONER_SAVE | defined SRC:config/model_a.h:3 (selected via SRC:config/model_config.h:3-4 for MODEL_A); used SRC:src/panel/menu_table.c:4,14, SRC:src/print/render.c:3,11 |
| S001 | build entry | src/features/eco/eco_mode.c | SRC:Makefile:6; dependency file src/print/density.c SRC:Makefile:2 |
| – | data/resource files | none | no non-code data files reference the feature (`grep -rnI` toner/eco over all files) |

## 4 – Tests
none found (searched: `find -iname 'test*' -o -iname 'ut'` → 0 dirs; `grep -lwE 'EcoMode_.*|STR_TONER_SAVE' | grep -iE 'test|_ut|spec'` → 0). Behavioral driver only: SRC:src/main.c:9-13.

## Guards / headers per ported line
- SUPPORT_TONER_SAVE: SRC:src/panel/menu_table.c:4-6,14-16, SRC:src/print/render.c:3-5,11-13; enabled SRC:config/model_a.h:3 (MODEL_A). pjl_commands.c:27, nv_settings.c:15 are unguarded (as in request).
- Headers: eco_mode.h included by pjl_commands.c:4, menu_table.c:5, render.c:4, nv_settings.c:2, eco_mode.c:2; eco_mode.c also includes nv_settings.h, density.h, log.h, strings.h, math_util.h (SRC:src/features/eco/eco_mode.c:1-7).

## Token accounting (B_new_tokens.txt)
46 identifiers in port text; 26 dropped as C keywords / path fragments / locals / library (`atoi`, `stdlib`); 20 project tokens: all are S-ids (EcoMode_* ×4, ECO_MODE_H, TONER_SAVE_OFF/LOW/HIGH, is_valid, k_percent, eco_effective_level, eco_level, STR_TONER_SAVE, SUPPORT_TONER_SAVE) or dependencies (NV_GetSettings S008.d1, Density_Scale S009.d1, Clamp S027.d1, Log_Info S010.d1, Str_Get S010.d2, g_settings = existing static SRC:src/settings/nv_settings.c:4).
