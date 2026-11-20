# C_trace – target state per item (TARGET_ROOT = B_latest)

Search notes: R2 by name over TGT (all names below); `find TGT -name 'toner*' -o -name 'density*' -o -name 'eco*'` → none;
R8 literals `"ECONOMODE"`, `"TONER_SAVE"`, `"Toner Save"`, `{ 100, 80, 60 }`, `fix #1234` → only TGT:src/main.c:11-12 (driver calls, no definition);
R17 `--ref-file SRC:src/features/toner_save/toner_save.c --root TGT` : TonerSave_ApplyDensity best blind 0.08, TonerSave_MenuHandler 0.11, Density_Scale (ref SRC:src/print/density.c) 0.15 → no equivalent (< 0.6);
R10/R11: TGT has no `model_a.h`; `config/model_config.h` (identical to SRC) selects `model_b.h` for `MODEL_B` (TGT:config/model_config.h:5-6) and TGT:Makefile:1 `MODEL ?= B` → file mapping `config/model_a.h → config/model_b.h` (relation EDGE `includes` slot + content: shares `MODEL_NAME`/`SUPPORT_DUPLEX` lines; High).

| S-id | symbol | source location | target location | target state | evidence | confidence | note |
|---|---|---|---|---|---|---|---|
| S001 | Makefile `SRCS += src/features/toner_save/toner_save.c` | SRC:Makefile:6 | TGT:Makefile (after L5) | MISSING | `grep -n toner_save TGT:Makefile` → 0; TGT:Makefile:2-5 SRCS list has no feature file | High | build entry; target Makefile otherwise = REQ-B except MODEL B and no density.c |
| S002 | SUPPORT_TONER_SAVE (macro) | SRC:config/model_a.h:3 | TGT:config/model_b.h (after L3) | MISSING | R2 macro grep TGT → 0; target model header = `config/model_b.h` (TGT:config/model_config.h:5-6) | High | guard not enabled in target → must be added to model_b.h |
| S003 | includes@src/cmd/pjl_commands.c | SRC:src/cmd/pjl_commands.c:4 | TGT:src/cmd/pjl_commands.c:1-3 | SAME_AS_BEFORE | R7: whole file TGT == REQ-B (`cmp`) | High | |
| S004 | g_pjl_table (table) | SRC:src/cmd/pjl_commands.c:24-28 | TGT:src/cmd/pjl_commands.c:23-26 | SAME_AS_BEFORE | `cmp` TGT == REQ-B | High | |
| S005 | includes@toner_save.c | SRC:src/features/toner_save/toner_save.c:1-8 | – | MISSING | file absent (find); R11 basename/content → none | High | |
| S006 | k_percent (global) | SRC:…toner_save.c:9 | – | MISSING | R2 + R8 `100, 80, 60` → 0 | High | |
| S007 | is_valid (function) | SRC:…toner_save.c:11-14 | – | MISSING | R2 → 0 | High | |
| S008 | TonerSave_GetLevel (function) | SRC:…toner_save.c:16-19 | – | MISSING | R2 → 0; R12 L1 via `toner_save_level` (field MISSING) → nothing | High | |
| S009 | TonerSave_ApplyDensity (function) | SRC:…toner_save.c:21-28 | – | MISSING | R2 → 0; R17 best blind 0.08; L1 caller Render_Page TGT:src/print/render.c:5-13 has no call | High | |
| S010 | TonerSave_MenuHandler (function) | SRC:…toner_save.c:30-37 | – | MISSING | R2 → 0; L1 registry g_menu_table TGT:src/panel/menu_table.c:5-11 has no TONER_SAVE slot | High | |
| S011 | TonerSave_PjlSet (function) | SRC:…toner_save.c:39-42 | – | MISSING | R2 → 0; L1 registry g_pjl_table TGT:src/cmd/pjl_commands.c:23-26 has no ECONOMODE slot | High | |
| S012 | TONER_SAVE_H (preprocessor) | SRC:…toner_save.h:1-2,13 | – | MISSING | file absent | High | |
| S013 | TONER_SAVE_OFF/LOW/HIGH (enum) | SRC:…toner_save.h:3-7 | – | MISSING | R2 enum-const → 0 | High | |
| S014 | SUPPORT_TONER_SAVE@menu_table.c | SRC:src/panel/menu_table.c:4-6 | TGT:src/panel/menu_table.c:1-3 | SAME_AS_BEFORE | R7 TGT:1-3 == REQ-B:1-3 | High | insert after L3 |
| S015 | g_menu_table (table) | SRC:src/panel/menu_table.c:11-22 | TGT:src/panel/menu_table.c:5-11 | DIVERGED | R7 vs REQ-B: target-only TGT:src/panel/menu_table.c:10 `{ "FAX", Menu_Fax },` | High | callers: Menu_Dispatch TGT:src/panel/menu_table.c:16-18 (table walk); keep FAX entry |
| S016 | SUPPORT_TONER_SAVE@render.c | SRC:src/print/render.c:3-5 | TGT:src/print/render.c:1-2 | SAME_AS_BEFORE | R7 TGT:1-2 == REQ-B:1-2 | High | insert after L2 |
| S017 | Render_Page (function) | SRC:src/print/render.c:8-16 | TGT:src/print/render.c:5-13 | DIVERGED | target-only TGT:src/print/render.c:9-11 `#ifdef SUPPORT_FAX` block | High | callers: TGT:src/main.c:13; keep FAX block |
| S018 | StrId_t (enum) | SRC:src/resources/strings.h:3-9 | TGT:src/resources/strings.h:3-9 | DIVERGED | target-only TGT:src/resources/strings.h:7 `STR_FAX,` | High | callers/uses: TGT:src/resources/strings_en.c:3-7, Str_Get TGT:src/resources/strings_en.c:10 |
| S019 | g_strings_en (table) | SRC:src/resources/strings_en.c:3-8 | TGT:src/resources/strings_en.c:3-8 | DIVERGED | target-only TGT:src/resources/strings_en.c:7 `[STR_FAX] = "Fax",` | High | callers: Str_Get TGT:src/resources/strings_en.c:12 |
| S020 | includes@nv_settings.c | SRC:src/settings/nv_settings.c:2 | TGT:src/settings/nv_settings.c:1-2 | SAME_AS_BEFORE | R7 TGT:1-2 == REQ-B:1-2 | High | |
| S021 | NV_LoadDefaults (function) | SRC:src/settings/nv_settings.c:11-18 | TGT:src/settings/nv_settings.c:10-17 | DIVERGED | target-only TGT:src/settings/nv_settings.c:16 `fax_resolution = 200;` | High | callers: TGT:src/main.c:9 |
| S022 | NvSettings_t (struct) | SRC:src/settings/nv_settings.h:5-11 | TGT:src/settings/nv_settings.h:5-11 | DIVERGED | target-only TGT:src/settings/nv_settings.h:10 `int fax_resolution;` | High | users: NV_GetSettings/NV_LoadDefaults TGT:src/settings/nv_settings.c:3-17; NVRAM struct (TGT:src/settings/nv_settings.h:4) |
| S009.d1 | Clamp (function) | SRC:src/util/math_util.c:3-8, SRC:src/util/math_util.h:3 | TGT:src/util/math_util.c:3-8, TGT:src/util/math_util.h:3 | SIGNATURE_DIFF | TGT `int Clamp(int v, int hi)` (2 params, lower bound fixed 0, TGT:src/util/math_util.c:5) vs SRC `int Clamp(int v, int lo, int hi)` | High | target callers: none (`grep -rnw Clamp TGT` → only definition + prototype) |
| S009.d2 | Density_Scale (function) | SRC:src/print/density.c:4-7 | – | MISSING | R2 → 0; `find -name 'density*'` → 0; R8 `percent / 100` → 0 | High | |
| S009.d3 | DENSITY_MAX (macro) | SRC:src/print/density.h:3 | – | MISSING | R2 → 0 | High | |
| S009.d4 | density.h (header) | SRC:src/print/density.h:1-5 | – | MISSING | find → 0 | High | |
| S009.d5 | Makefile entry `src/print/density.c` | SRC:Makefile:2 | TGT:Makefile:2 | MISSING | TGT:Makefile:2 `SRCS = src/main.c src/core/log.c src/util/math_util.c \` (no density.c) | High | |
| S008.d1 | NV_GetSettings (function) | SRC:src/settings/nv_settings.c:6-9 | TGT:src/settings/nv_settings.c:5-8 | SAME_AS_SOURCE | R7 `diff` identical | High | |
| S010.d1 | Log_Info (function) | SRC:src/core/log.c:4 | TGT:src/core/log.c:4 | SAME_AS_SOURCE | `cmp` log.c, log.h identical | High | |
| S010.d2 | Str_Get (function) | SRC:src/resources/strings_en.c:10-13 | TGT:src/resources/strings_en.c:10-13 | SAME_AS_SOURCE | R7 identical | High | |
| S021.d1 | g_settings (global) | SRC:src/settings/nv_settings.c:4 | TGT:src/settings/nv_settings.c:3 | SAME_AS_SOURCE | same text | High | |
| S005.d1 | math_util.h (header) | SRC:src/util/math_util.h:1-4 | TGT:src/util/math_util.h:1-4 | SIGNATURE_DIFF | only L3 Clamp prototype differs (see S009.d1) | High | callers: none |
| S005.d2 | headers log.h / strings.h / nv_settings.h | SRC:src/core/log.h, SRC:src/resources/strings.h, SRC:src/settings/nv_settings.h | TGT: same paths | DIVERGED | log.h `cmp` identical; strings.h/nv_settings.h differ only by S018/S022 lines | High | content handled by S018/S022 |
| S015.d1 | model_config.h | SRC:config/model_config.h:3-7 | TGT:config/model_config.h:3-7 | SAME_AS_SOURCE | `cmp` identical | High | |
| S004.d1 | Pjl_Dispatch (function) | SRC:src/cmd/pjl_commands.c:30-38 | TGT:src/cmd/pjl_commands.c:28-36 | SAME_AS_SOURCE | R7 identical | High | |
| S015.d2 | Menu_Dispatch (function) | SRC:src/panel/menu_table.c:24-32 | TGT:src/panel/menu_table.c:13-21 | SAME_AS_SOURCE | R7 identical | High | |
| S017.d1 | main driver | SRC:src/main.c:7-15 | TGT:src/main.c:7-15 | SAME_AS_SOURCE | `cmp` identical | High | consumer (report only) |
| S008.d2 | EcoReport_Print (consumer) | SRC:src/features/eco_report/eco_report.c:5-9 | – | MISSING | R2 → 0 | High | CONSUMER, report only |
| S009.d6 | Menu_Quality → Density_Scale (consumer) | SRC:src/panel/menu.c:22 | TGT:src/panel/menu.c:19-23 | DIVERGED | TGT body `Log_Info("quality"); return key;` | High | CONSUMER of a dependency, report only; callers: g_menu_table TGT:src/panel/menu_table.c:8 |

Data deps per place (R13 on target):
- STR_TONER_SAVE: enum TGT:src/resources/strings.h:3-9 MISSING; language tables: only `strings_en.c` in TGT (`find -name 'strings_*'`) – entry MISSING; STR_COUNT-sized array TGT:src/resources/strings_en.c:3 (designated init, grows automatically).
- toner_save_level: struct field MISSING (TGT:src/settings/nv_settings.h:5-11); default MISSING (TGT:src/settings/nv_settings.c:10-17); version/checksum: none in TGT (`grep -rniE 'version|checksum|crc|migrat'` → 0).
- Registry: "ECONOMODE" MISSING in TGT:src/cmd/pjl_commands.c:23-26; "TONER_SAVE" MISSING in TGT:src/panel/menu_table.c:5-11.
- Config: SUPPORT_TONER_SAVE MISSING in TGT:config/model_b.h:1-3 (no -D in TGT:Makefile).
- Build: toner_save.c and density.c MISSING in TGT:Makefile:2-5.

Closure: Iteration 1: +0 items (density.c/.h bodies expanded: Clamp = S009.d1, DENSITY_MAX = S009.d3, math_util.h = S005.d1; nothing new) → fixpoint.

Flows:
FLOW-1 source (render density): SRC:src/main.c:13 → SRC:src/print/render.c:12 Render_Page → SRC:src/features/toner_save/toner_save.c:21 TonerSave_ApplyDensity → :23 TonerSave_GetLevel → SRC:src/settings/nv_settings.c:6 NV_GetSettings → SRC:…toner_save.c:24 Clamp (SRC:src/util/math_util.c:3) → :27 Density_Scale (SRC:src/print/density.c:4 → Clamp(…, 0, DENSITY_MAX=15))
FLOW-1 target: TGT:src/main.c:13 → TGT:src/print/render.c:5 Render_Page → MISSING at TonerSave_ApplyDensity (no hook; SUPPORT_TONER_SAVE undefined)
FLOW-2 source (panel menu): SRC:src/main.c:11 Menu_Dispatch("TONER_SAVE") → SRC:src/panel/menu_table.c:24 → entry SRC:src/panel/menu_table.c:15 → SRC:…toner_save.c:30 TonerSave_MenuHandler → is_valid :11 → NV field write :34 → Log_Info(Str_Get(STR_TONER_SAVE)) SRC:src/resources/strings_en.c:6
FLOW-2 target: TGT:src/main.c:11 → TGT:src/panel/menu_table.c:13 Menu_Dispatch → MISSING at "TONER_SAVE" entry (returns -1)
FLOW-3 source (PJL): SRC:src/main.c:12 Pjl_Dispatch("ECONOMODE") → SRC:src/cmd/pjl_commands.c:30 → entry :27 → SRC:…toner_save.c:39 TonerSave_PjlSet → TonerSave_MenuHandler
FLOW-3 target: TGT:src/main.c:12 → TGT:src/cmd/pjl_commands.c:28 Pjl_Dispatch → MISSING at "ECONOMODE" entry (returns -1)
FLOW-4 source (NV default): SRC:src/main.c:9 NV_LoadDefaults → SRC:src/settings/nv_settings.c:15 toner_save_level = TONER_SAVE_OFF
FLOW-4 target: TGT:src/main.c:9 → TGT:src/settings/nv_settings.c:10 NV_LoadDefaults → MISSING at toner_save_level
Target-only behavior to keep: FAX menu entry TGT:src/panel/menu_table.c:10, Menu_Fax TGT:src/panel/menu.c, STR_FAX TGT:src/resources/strings.h:7 + TGT:src/resources/strings_en.c:7, fax_resolution TGT:src/settings/nv_settings.h:10 + default TGT:src/settings/nv_settings.c:16, SUPPORT_FAX block TGT:src/print/render.c:9-11, SUPPORT_FAX TGT:config/model_b.h:3.
