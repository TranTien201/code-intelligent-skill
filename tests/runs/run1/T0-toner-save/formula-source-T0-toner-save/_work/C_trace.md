# C_trace (TGT = TARGET_ROOT; comparisons R7 `diff -w`, port version from B_symbols §3)

| S-id | symbol | source location | target location | target state | evidence | confidence | note |
|---|---|---|---|---|---|---|---|
| S001 | Makefile `SRCS += …toner_save.c` | SRC:Makefile:6 | TGT:Makefile:1-5 (no entry) | MISSING | `grep -n toner_save TGT:Makefile` → none; TGT Makefile ≠ REQ-B (MODEL B, no density.c) | High | add after TGT:Makefile:5 |
| S002 | SUPPORT_TONER_SAVE (macro) | SRC:config/model_a.h:3 | TGT:config/model_b.h (file alias, macro absent) | MISSING | R2 macro grep → none; R11 file: model_a.h → model_b.h (alias_map) | High (macro) | guard not enabled in target → ENABLE_GUARD |
| S003 | pjl_commands.c (file scope) | SRC:src/cmd/pjl_commands.c:1-4 | TGT:src/cmd/pjl_commands.c:1-3 | SAME_AS_BEFORE | R7 TGT file == REQ-B file | High | |
| S004 | g_pjl_table (table) | SRC:src/cmd/pjl_commands.c:24-28 | TGT:src/cmd/pjl_commands.c:23-26 | SAME_AS_BEFORE | R7 == REQ-B | High | callers: Pjl_Dispatch TGT:…:29 |
| S005 | toner_save.c (file scope) | SRC:src/features/toner_save/toner_save.c:1-8 | – | MISSING | R11 `find -name toner_save.c` → none; R8 literals `100, 80, 60`, `k_percent` → none | High | new file |
| S006 | k_percent (table) | SRC:…/toner_save.c:9 | – | MISSING | R2/R8 none | High | |
| S007 | is_valid@src/features/toner_save/toner_save.c | SRC:…/toner_save.c:11-14 | – | MISSING | only TGT:src/panel/menu.c:5 `is_valid` (different static, body `key < 100`) – not equivalent | High | |
| S008 | TonerSave_GetLevel (function) | SRC:…/toner_save.c:16-19 | – | MISSING | R2 none; R12 caller anchor: no caller in TGT (eco_report absent) | High | |
| S009 | TonerSave_ApplyDensity (function) | SRC:…/toner_save.c:21-28 | – | MISSING | R2 none; R12 caller anchor TGT:src/print/render.c:7-8 – no call at that position | High | |
| S010 | TonerSave_MenuHandler (function) | SRC:…/toner_save.c:30-37 | – | MISSING | R2 none; table slot after DUPLEX in TGT:src/panel/menu_table.c:7 empty; R8 `Toner Save` none | High | |
| S011 | TonerSave_PjlSet (function) | SRC:…/toner_save.c:39-42 | – | MISSING | R2 none; R8 `ECONOMODE` only TGT:src/main.c:12 (driver) | High | |
| S012 | TONER_SAVE_H (preprocessor) | SRC:…/toner_save.h:1-2,13 | – | MISSING | R11 none | High | new file |
| S013 | TONER_SAVE_OFF..HIGH (enum) | SRC:…/toner_save.h:3-7 | – | MISSING | R2 none | High | |
| S014–S017 | TonerSave_* (prototype) | SRC:…/toner_save.h:9-12 | – | MISSING | R2 none | High | |
| S018 | SUPPORT_TONER_SAVE include block @menu_table.c | SRC:src/panel/menu_table.c:4-6 | TGT:src/panel/menu_table.c:1-3 | SAME_AS_BEFORE | R7 lines 1-3 == REQ-B 1-3 | High | insert after TGT:…:3 |
| S019 | g_menu_table (table) | SRC:src/panel/menu_table.c:11-22 | TGT:src/panel/menu_table.c:5-11 | DIVERGED | vs REQ-B: target-only TGT:…:10 `{ "FAX", Menu_Fax }` | High | callers: Menu_Dispatch TGT:…:13-21 |
| S020 | SUPPORT_TONER_SAVE include block @render.c | SRC:src/print/render.c:3-5 | TGT:src/print/render.c:1-3 | SAME_AS_BEFORE | R7 == REQ-B 1-3 | High | |
| S021 | Render_Page (function) | SRC:src/print/render.c:8-16 | TGT:src/print/render.c:5-13 | DIVERGED | target-only TGT:…:9-11 `#ifdef SUPPORT_FAX` block | High | callers: TGT:src/main.c:13 |
| S022 | StrId_t (enum) | SRC:src/resources/strings.h:3-9 | TGT:src/resources/strings.h:3-9 | DIVERGED | target-only TGT:…:7 `STR_FAX` | High | users: TGT:src/resources/strings_en.c:3,7,10 |
| S023 | g_strings_en (table) | SRC:src/resources/strings_en.c:3-8 | TGT:src/resources/strings_en.c:3-8 | DIVERGED | target-only TGT:…:7 `[STR_FAX] = "Fax"` | High | callers: Str_Get TGT:…:12 |
| S024 | nv_settings.c (file scope) | SRC:src/settings/nv_settings.c:1-2 | TGT:src/settings/nv_settings.c:1 | SAME_AS_BEFORE | R7 == REQ-B line 1 | High | |
| S025 | NV_LoadDefaults (function) | SRC:src/settings/nv_settings.c:11-18 | TGT:src/settings/nv_settings.c:10-17 | DIVERGED | target-only TGT:…:16 `fax_resolution = 200` | High | callers: TGT:src/main.c:9 |
| S026 | NvSettings_t (struct) | SRC:src/settings/nv_settings.h:5-11 | TGT:src/settings/nv_settings.h:5-11 | DIVERGED | target-only TGT:…:10 `int fax_resolution` | High | users: TGT:src/settings/nv_settings.c:3,5,12-16 |
| S008.d1 | NV_GetSettings (function) | SRC:src/settings/nv_settings.c:6-9 | TGT:src/settings/nv_settings.c:5-8 | SAME_AS_SOURCE | R7 SAME | High | |
| S009.d1 | Density_Scale (function) | SRC:src/print/density.c:4-7 | – | MISSING | R2 none; R11 `find -name 'density.*'` none; R8 `base * percent` none | High | copy density.c/.h |
| S009.d2 | DENSITY_MAX (macro) | SRC:src/print/density.h:3 | – | MISSING | R2 none | High | |
| S009.d3 | Clamp (function) | SRC:src/util/math_util.c:3-8 | TGT:src/util/math_util.c:3-8, TGT:src/util/math_util.h:3 | SIGNATURE_DIFF | TGT `int Clamp(int v, int hi)` (lo fixed 0) vs SRC `int Clamp(int v, int lo, int hi)` | High | target callers: none (`grep -rnw Clamp TGT` → only def + proto) |
| S009.d4 | density.h (header) | SRC:src/print/density.h:1-5 | – | MISSING | R11 none | High | closure iteration 1 |
| S009.d5 | build entry `src/print/density.c` | SRC:Makefile:2 | TGT:Makefile:2 (absent) | MISSING | TGT:Makefile:2 lacks density.c | High | closure iteration 1 |
| S010.d1 | Log_Info (function) | SRC:src/core/log.c:4-7 | TGT:src/core/log.c:4-7 | SAME_AS_SOURCE | file identical | High | |
| S010.d2 | Str_Get (function) | SRC:src/resources/strings_en.c:10-13 | TGT:src/resources/strings_en.c:10-13 | SAME_AS_SOURCE | R7 SAME | High | |
| S011.d1 | atoi (library) | `<stdlib.h>` | `<stdlib.h>` (toolchain) | SAME_AS_SOURCE | standard library | High | |
| S018.d1 | model_config.h (header) | SRC:config/model_config.h:1-8 | TGT:config/model_config.h:1-8 | SAME_AS_SOURCE | file identical; MODEL_B → model_b.h (TGT:…:5-6) | High | |
| S019.d1 | MenuEntry_t (typedef) | SRC:src/panel/menu.h:3-7 | TGT:src/panel/menu.h:3-7 | SAME_AS_SOURCE | R7 SAME | High | |
| S004.d1 | PjlEntry_t (typedef) | SRC:src/cmd/pjl_commands.c:6-10 | TGT:src/cmd/pjl_commands.c:5-9 | SAME_AS_SOURCE | R7 SAME | High | |

## Data dependency places (target)
| item | place | target status |
|---|---|---|
| STR_TONER_SAVE | TGT:src/resources/strings.h enum | MISSING (enum DIVERGED: STR_FAX) |
| STR_TONER_SAVE | TGT:src/resources/strings_en.c (only language table; `grep g_strings_` → strings_en only) | MISSING |
| StrId_t-sized tables | TGT:src/resources/strings_en.c:3 `[STR_COUNT]` | present, sized automatically (designated init) |
| toner_save_level field | TGT:src/settings/nv_settings.h struct | MISSING |
| toner_save_level default | TGT:src/settings/nv_settings.c NV_LoadDefaults | MISSING |
| NV version/checksum | TGT (`grep -niE 'version|crc|checksum|migrat'`) | none exists |
| menu entry TONER_SAVE | TGT:src/panel/menu_table.c g_menu_table | MISSING |
| PJL entry ECONOMODE | TGT:src/cmd/pjl_commands.c g_pjl_table | MISSING |
| config SUPPORT_TONER_SAVE | TGT:config/model_b.h | MISSING (guard not enabled) |
| build entries | TGT:Makefile toner_save.c, density.c | MISSING |

## Closure
Iteration 1: +2 items (S009.d4 density.h, S009.d5 Makefile density.c entry) from MISSING Density_Scale; SIGNATURE_DIFF Clamp has no outgoing deps.
Iteration 2: +0 items (DENSITY_MAX, Clamp already rows) → fixpoint.

## Flows
FLOW-1 source: SRC:src/main.c:13 → SRC:src/print/render.c:12 Render_Page → SRC:src/features/toner_save/toner_save.c:21 TonerSave_ApplyDensity → :16 TonerSave_GetLevel → SRC:src/settings/nv_settings.c:6 NV_GetSettings (toner_save_level) → SRC:…/toner_save.c:24 Clamp (SRC:src/util/math_util.c:3) → :11 is_valid → SRC:src/print/density.c:4 Density_Scale → Clamp/DENSITY_MAX
FLOW-1 target: TGT:src/main.c:13 → TGT:src/print/render.c:5 Render_Page → MISSING at TonerSave_ApplyDensity (and guard SUPPORT_TONER_SAVE not enabled in TGT:config/model_b.h)
FLOW-2 source: SRC:src/main.c:11 → SRC:src/panel/menu_table.c:24 Menu_Dispatch → :15 g_menu_table entry → SRC:…/toner_save.c:30 TonerSave_MenuHandler → is_valid, NV toner_save_level, SRC:src/core/log.c:4 Log_Info(SRC:src/resources/strings_en.c:10 Str_Get(STR_TONER_SAVE))
FLOW-2 target: TGT:src/main.c:11 → TGT:src/panel/menu_table.c:13 Menu_Dispatch → MISSING at g_menu_table entry TONER_SAVE (returns -1)
FLOW-3 source: SRC:src/main.c:12 → SRC:src/cmd/pjl_commands.c:30 Pjl_Dispatch → :27 entry ECONOMODE → SRC:…/toner_save.c:39 TonerSave_PjlSet → TonerSave_MenuHandler
FLOW-3 target: TGT:src/main.c:12 → TGT:src/cmd/pjl_commands.c:29 Pjl_Dispatch → MISSING at g_pjl_table entry ECONOMODE
FLOW-4 source: SRC:src/main.c:9 NV_LoadDefaults → SRC:src/settings/nv_settings.c:15 toner_save_level = TONER_SAVE_OFF → SRC:src/settings/nv_settings.h:8 field
FLOW-4 target: TGT:src/main.c:9 → TGT:src/settings/nv_settings.c:10 NV_LoadDefaults → MISSING at toner_save_level field/default
Target-only behavior to keep: FAX menu entry TGT:src/panel/menu_table.c:10, Menu_Fax TGT:src/panel/menu.c:29-33, STR_FAX/"Fax" TGT:src/resources/strings.h:7 / strings_en.c:7, fax_resolution TGT:src/settings/nv_settings.h:10 / nv_settings.c:16, render fax block TGT:src/print/render.c:9-11, Menu_Quality without Density_Scale TGT:src/panel/menu.c:19-23.
