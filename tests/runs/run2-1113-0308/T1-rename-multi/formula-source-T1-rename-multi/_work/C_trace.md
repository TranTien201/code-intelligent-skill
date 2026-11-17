# C_trace – target state per item (TARGET_ROOT = B_latest)
Comparisons: R7 `diff -w` of target body vs port version (B5) and vs REQ-B, after alias map. Raw: `_work/C_search_raw.txt`.

| S-id | symbol | source location | target location | target state | evidence | confidence | note |
|---|---|---|---|---|---|---|---|
| S001 | Makefile SRCS entry eco_mode.c | SRC:Makefile:6 | TGT:Makefile:1-8 | DIVERGED | TGT:Makefile:1 `MODEL ?= B`, TGT:Makefile:2 lacks density.c (vs REQ-B:Makefile:2); no `SRCS +=` line | High | build entry MISSING; target-only MODEL B |
| S002 | SUPPORT_TONER_SAVE (macro) | SRC:config/model_a.h:3 | (TGT:config/model_b.h – not defined) | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`); target model config TGT:config/model_config.h:5-6 selects TGT:config/model_b.h (siblings TGT:config/model_b.h:2-3) | High | guard not enabled in target |
| S003 | file scope@pjl_commands.c | SRC:src/cmd/pjl_commands.c:1-4 | TGT:src/cmd/pjl_commands.c:1-3 | SAME_AS_BEFORE | file identical to REQ-B (diff empty) | High | |
| S004 | g_pjl_table (table) | SRC:src/cmd/pjl_commands.c:24-28 | TGT:src/cmd/pjl_commands.c:23-26 | SAME_AS_BEFORE | R7 = REQ-B:src/cmd/pjl_commands.c:23-26 | High | entry "ECONOMODE" MISSING |
| S005 | file scope@eco_mode.c | SRC:src/features/eco/eco_mode.c:1-8 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | new file |
| S006 | k_percent | SRC:src/features/eco/eco_mode.c:9 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | |
| S007 | is_valid@eco_mode.c | SRC:src/features/eco/eco_mode.c:11-14 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`); TGT:src/panel/menu.c:4 is another static is_valid (key, different body) – not equivalent, no clash (file-static) | High | |
| S008 | EcoMode_GetLevel | SRC:src/features/eco/eco_mode.c:16-19 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | |
| S009 | EcoMode_ApplyDensity | SRC:src/features/eco/eco_mode.c:28-34 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | |
| S010 | EcoMode_MenuHandler | SRC:src/features/eco/eco_mode.c:36-43 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | |
| S011 | EcoMode_PjlSet | SRC:src/features/eco/eco_mode.c:45-48 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | |
| S027 | eco_effective_level (ext) | SRC:src/features/eco/eco_mode.c:21-26 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | ext |
| S012 | ECO_MODE_H | SRC:src/features/eco/eco_mode.h:1-2,13 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | new file |
| S013 | TONER_SAVE_OFF/LOW/HIGH | SRC:src/features/eco/eco_mode.h:3-7 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | |
| S014 | EcoMode_GetLevel (prototype) | SRC:src/features/eco/eco_mode.h:9 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | |
| S015 | EcoMode_ApplyDensity (prototype) | SRC:src/features/eco/eco_mode.h:10 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | |
| S016 | EcoMode_MenuHandler (prototype) | SRC:src/features/eco/eco_mode.h:11 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | |
| S017 | EcoMode_PjlSet (prototype) | SRC:src/features/eco/eco_mode.h:12 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | |
| S018 | file scope@menu_table.c | SRC:src/panel/menu_table.c:1-6 | TGT:src/panel/menu_table.c:1-3 | SAME_AS_BEFORE | R7 = REQ-B:src/panel/menu_table.c:1-3 | High | |
| S019 | g_menu_table (table) | SRC:src/panel/menu_table.c:11-22 | TGT:src/panel/menu_table.c:5-11 | DIVERGED | target-only TGT:src/panel/menu_table.c:10 `{ "FAX", Menu_Fax },`; DUPLEX/QUALITY neighbours TGT:src/panel/menu_table.c:7-8 as in REQ-B | High | keep FAX entry |
| S020 | file scope@render.c | SRC:src/print/render.c:1-6 | TGT:src/print/render.c:1-3 | SAME_AS_BEFORE | R7 = REQ-B:src/print/render.c:1-3 | High | |
| S021 | Render_Page | SRC:src/print/render.c:8-16 | TGT:src/print/render.c:5-13 | DIVERGED | target-only TGT:src/print/render.c:9-11 (`#ifdef SUPPORT_FAX` fax header after "render done") | High | callers: TGT:src/main.c:13 |
| S022 | StrId_t (enum) | SRC:src/resources/strings.h:3-9 | TGT:src/resources/strings.h:3-9 | DIVERGED | target-only TGT:src/resources/strings.h:7 `STR_FAX` | High | callers (users): TGT:src/resources/strings_en.c:3-13 |
| S023 | g_strings_en (table) | SRC:src/resources/strings_en.c:3-8 | TGT:src/resources/strings_en.c:3-8 | DIVERGED | target-only TGT:src/resources/strings_en.c:7 `[STR_FAX] = "Fax"` | High | users: Str_Get TGT:src/resources/strings_en.c:12 |
| S024 | file scope@nv_settings.c | SRC:src/settings/nv_settings.c:1-2 | TGT:src/settings/nv_settings.c:1 | SAME_AS_BEFORE | R7 = REQ-B:src/settings/nv_settings.c:1 | High | |
| S025 | NV_LoadDefaults | SRC:src/settings/nv_settings.c:11-18 | TGT:src/settings/nv_settings.c:10-17 | DIVERGED | target-only TGT:src/settings/nv_settings.c:16 `fax_resolution = 200` | High | callers: TGT:src/main.c:9 |
| S026 | NvSettings_t (struct) | SRC:src/settings/nv_settings.h:5-11 | TGT:src/settings/nv_settings.h:5-11 | DIVERGED | target-only member TGT:src/settings/nv_settings.h:10 `int fax_resolution;`; shared members identical (not SIGNATURE_DIFF: no shared member changed) | High | users: TGT:src/settings/nv_settings.c:12-16; NVRAM layout |
| S008.d1 | NV_GetSettings | SRC:src/settings/nv_settings.c:6-9 | TGT:src/settings/nv_settings.c:5-8 | SAME_AS_SOURCE | R7 equal; proto TGT:src/settings/nv_settings.h:13 | High | stop |
| S009.d1 | Density_Scale | SRC:src/print/density.c:4-7 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`); target menu.c no longer uses it (TGT:src/panel/menu.c:19-23 vs SRC:src/panel/menu.c:20-23) | High | expanded in C4 |
| S009.d2 | DENSITY_MAX | SRC:src/print/density.h:3 | – | MISSING | MISSING searches: R2 name (latest + request names) 0 hits; R11 basename eco_mode.*/toner_save.* 0; R8 literals 0; R17 best blind ≤ 0.31 (`_work/C_search_raw.txt`) | High | |
| S009.d3 | density.h (header file) | SRC:src/print/density.h:1-5 | – | MISSING | R11 basename density.* 0 hits | High | |
| S009.d4 | build entry src/print/density.c | SRC:Makefile:2 | TGT:Makefile:2 (absent) | MISSING | TGT:Makefile:2-5 SRCS list lacks density.c (REQ-B:Makefile:2 had it) | High | C4 iteration 1 |
| S027.d1 | Clamp | SRC:src/util/math_util.c:3-8 (proto SRC:src/util/math_util.h:3) | TGT:src/util/math_util.c:3-8 (proto TGT:src/util/math_util.h:3) | SIGNATURE_DIFF | target `int Clamp(int v, int hi)` (lower bound fixed 0, TGT:src/util/math_util.c:5) vs source `int Clamp(int v, int lo, int hi)`; target callers: none (`grep -rnw Clamp` → only def + proto) | High | ported callers: eco_mode.c:24 (lo=TONER_SAVE_OFF=0), density.c:6 (lo=0) |
| S010.d1 | Log_Info | SRC:src/core/log.c:4-7 | TGT:src/core/log.c:4-7 | SAME_AS_SOURCE | file identical | High | stop |
| S010.d2 | Str_Get | SRC:src/resources/strings_en.c:10-13 | TGT:src/resources/strings_en.c:10-13 | SAME_AS_SOURCE | R7 equal | High | stop |

## Data dependencies (target status per place)
| item | place | target status |
|---|---|---|
| STR_TONER_SAVE | enum StrId_t TGT:src/resources/strings.h:3-9 | MISSING (insert after STR_DUPLEX TGT:src/resources/strings.h:5) |
| STR_TONER_SAVE | language table g_strings_en TGT:src/resources/strings_en.c:3-8 (only language file: `ls TGT:src/resources`) | MISSING (after [STR_DUPLEX] TGT:src/resources/strings_en.c:5) |
| StrId_t layout | arrays sized by STR_COUNT: TGT:src/resources/strings_en.c:3 only | size follows automatically; STR_QUALITY 2→3, STR_FAX 3→4 shift |
| eco_level | struct TGT:src/settings/nv_settings.h:5-11 | MISSING (after duplex TGT:src/settings/nv_settings.h:7) |
| eco_level | default NV_LoadDefaults TGT:src/settings/nv_settings.c:10-17 | MISSING (after duplex default TGT:src/settings/nv_settings.c:13) |
| eco_level | version/checksum/migration | none in target (`grep -rniE 'version\|crc\|checksum\|migrat'` → 0) |
| "ECONOMODE" | g_pjl_table TGT:src/cmd/pjl_commands.c:23-26 | MISSING |
| "TONER_SAVE" | g_menu_table TGT:src/panel/menu_table.c:5-11 | MISSING |
| SUPPORT_TONER_SAVE | TGT:config/model_b.h | MISSING (guard not enabled) |
| build eco_mode.c | TGT:Makefile | MISSING |
| build density.c | TGT:Makefile:2-5 | MISSING |

## Flows
FLOW-1 source (menu): SRC:src/main.c:11 Menu_Dispatch("TONER_SAVE") → SRC:src/panel/menu_table.c:15 entry → SRC:src/features/eco/eco_mode.c:36 EcoMode_MenuHandler → :11 is_valid, SRC:src/settings/nv_settings.h:8 eco_level, SRC:src/core/log.c:4 Log_Info(Str_Get(STR_TONER_SAVE) SRC:src/resources/strings_en.c:6)
FLOW-1 target: TGT:src/main.c:11 → TGT:src/panel/menu_table.c:5-11 → MISSING at "TONER_SAVE" entry (returns -1)
FLOW-2 source (PJL): SRC:src/main.c:12 Pjl_Dispatch("ECONOMODE") → SRC:src/cmd/pjl_commands.c:27 → SRC:src/features/eco/eco_mode.c:45 EcoMode_PjlSet → :36 EcoMode_MenuHandler
FLOW-2 target: TGT:src/main.c:12 → TGT:src/cmd/pjl_commands.c:23-26 → MISSING at "ECONOMODE" entry (returns -1)
FLOW-3 source (render density): SRC:src/main.c:13 Render_Page → SRC:src/print/render.c:12 EcoMode_ApplyDensity → SRC:src/features/eco/eco_mode.c:21 eco_effective_level → :16 EcoMode_GetLevel, SRC:src/util/math_util.c:3 Clamp, :11 is_valid → SRC:src/print/density.c:4 Density_Scale → SRC:src/util/math_util.c:3 Clamp, SRC:src/print/density.h:3 DENSITY_MAX
FLOW-3 target: TGT:src/main.c:13 → TGT:src/print/render.c:5 Render_Page → MISSING at ApplyDensity call (+ Density_Scale, density.h MISSING; Clamp SIGNATURE_DIFF)
FLOW-4 source (defaults): SRC:src/main.c:9 NV_LoadDefaults → SRC:src/settings/nv_settings.c:15 eco_level = TONER_SAVE_OFF
FLOW-4 target: TGT:src/main.c:9 → TGT:src/settings/nv_settings.c:10 → MISSING at eco_level field/default
Target-only behavior to keep: FAX menu entry TGT:src/panel/menu_table.c:10, fax header TGT:src/print/render.c:9-11, STR_FAX TGT:src/resources/strings.h:7 / strings_en.c:7, fax_resolution TGT:src/settings/nv_settings.h:10 / nv_settings.c:16, SUPPORT_FAX TGT:config/model_b.h:3, Menu_Quality without Density_Scale TGT:src/panel/menu.c:19-23.

## Closure
Iteration 1: +1 item (S009.d4 build entry density.c, from expanding MISSING S009.d1 Density_Scale / S009.d3 density.h: includes density.h, math_util.h (TGT present), uses Clamp (already S027.d1), DENSITY_MAX (S009.d2))
Iteration 2: +0 items (Clamp body has no project deps) → fixpoint.
