### Source Behavior
- FLOW-1 source (menu): SRC:src/main.c:11 Menu_Dispatch("TONER_SAVE") → SRC:src/panel/menu_table.c:15 entry → SRC:src/features/eco/eco_mode.c:36 EcoMode_MenuHandler → :11 is_valid, SRC:src/settings/nv_settings.h:8 eco_level, SRC:src/core/log.c:4 Log_Info(Str_Get(STR_TONER_SAVE) SRC:src/resources/strings_en.c:6)
- FLOW-2 source (PJL): SRC:src/main.c:12 Pjl_Dispatch("ECONOMODE") → SRC:src/cmd/pjl_commands.c:27 → SRC:src/features/eco/eco_mode.c:45 EcoMode_PjlSet → :36 EcoMode_MenuHandler
- FLOW-3 source (render density): SRC:src/main.c:13 Render_Page → SRC:src/print/render.c:12 EcoMode_ApplyDensity → SRC:src/features/eco/eco_mode.c:21 eco_effective_level → :16 EcoMode_GetLevel, SRC:src/util/math_util.c:3 Clamp, :11 is_valid → SRC:src/print/density.c:4 Density_Scale → SRC:src/util/math_util.c:3 Clamp, SRC:src/print/density.h:3 DENSITY_MAX
- FLOW-4 source (defaults): SRC:src/main.c:9 NV_LoadDefaults → SRC:src/settings/nv_settings.c:15 eco_level = TONER_SAVE_OFF

### Target Behavior
- FLOW-1 target: TGT:src/main.c:11 → TGT:src/panel/menu_table.c:5-11 → MISSING at "TONER_SAVE" entry (returns -1)
- FLOW-2 target: TGT:src/main.c:12 → TGT:src/cmd/pjl_commands.c:23-26 → MISSING at "ECONOMODE" entry (returns -1)
- FLOW-3 target: TGT:src/main.c:13 → TGT:src/print/render.c:5 Render_Page → MISSING at ApplyDensity call (+ Density_Scale, density.h MISSING; Clamp SIGNATURE_DIFF)
- FLOW-4 target: TGT:src/main.c:9 → TGT:src/settings/nv_settings.c:10 → MISSING at eco_level field/default
- Target-only behavior to keep: FAX menu entry TGT:src/panel/menu_table.c:10, fax header TGT:src/print/render.c:9-11, STR_FAX TGT:src/resources/strings.h:7 / strings_en.c:7, fax_resolution TGT:src/settings/nv_settings.h:10 / nv_settings.c:16, SUPPORT_FAX TGT:config/model_b.h:3, Menu_Quality without Density_Scale TGT:src/panel/menu.c:19-23.

| id | item | target location | target state | confidence |
|---|---|---|---|---|
| S001 | Makefile SRCS entry eco_mode.c | TGT:Makefile:1-8 | DIVERGED | High |
| S002 | SUPPORT_TONER_SAVE (macro) | (TGT:config/model_b.h – not defined) | MISSING | High |
| S003 | file scope@pjl_commands.c | TGT:src/cmd/pjl_commands.c:1-3 | SAME_AS_BEFORE | High |
| S004 | g_pjl_table (table) | TGT:src/cmd/pjl_commands.c:23-26 | SAME_AS_BEFORE | High |
| S005 | file scope@eco_mode.c | – | MISSING | High |
| S006 | k_percent | – | MISSING | High |
| S007 | is_valid@eco_mode.c | – | MISSING | High |
| S008 | EcoMode_GetLevel | – | MISSING | High |
| S009 | EcoMode_ApplyDensity | – | MISSING | High |
| S010 | EcoMode_MenuHandler | – | MISSING | High |
| S011 | EcoMode_PjlSet | – | MISSING | High |
| S027 | eco_effective_level (ext) | – | MISSING | High |
| S012 | ECO_MODE_H | – | MISSING | High |
| S013 | TONER_SAVE_OFF/LOW/HIGH | – | MISSING | High |
| S014 | EcoMode_GetLevel (prototype) | – | MISSING | High |
| S015 | EcoMode_ApplyDensity (prototype) | – | MISSING | High |
| S016 | EcoMode_MenuHandler (prototype) | – | MISSING | High |
| S017 | EcoMode_PjlSet (prototype) | – | MISSING | High |
| S018 | file scope@menu_table.c | TGT:src/panel/menu_table.c:1-3 | SAME_AS_BEFORE | High |
| S019 | g_menu_table (table) | TGT:src/panel/menu_table.c:5-11 | DIVERGED | High |
| S020 | file scope@render.c | TGT:src/print/render.c:1-3 | SAME_AS_BEFORE | High |
| S021 | Render_Page | TGT:src/print/render.c:5-13 | DIVERGED | High |
| S022 | StrId_t (enum) | TGT:src/resources/strings.h:3-9 | DIVERGED | High |
| S023 | g_strings_en (table) | TGT:src/resources/strings_en.c:3-8 | DIVERGED | High |
| S024 | file scope@nv_settings.c | TGT:src/settings/nv_settings.c:1 | SAME_AS_BEFORE | High |
| S025 | NV_LoadDefaults | TGT:src/settings/nv_settings.c:10-17 | DIVERGED | High |
| S026 | NvSettings_t (struct) | TGT:src/settings/nv_settings.h:5-11 | DIVERGED | High |
| S008.d1 | NV_GetSettings | TGT:src/settings/nv_settings.c:5-8 | SAME_AS_SOURCE | High |
| S009.d1 | Density_Scale | – | MISSING | High |
| S009.d2 | DENSITY_MAX | – | MISSING | High |
| S009.d3 | density.h (header file) | – | MISSING | High |
| S009.d4 | build entry src/print/density.c | TGT:Makefile:2 (absent) | MISSING | High |
| S027.d1 | Clamp | TGT:src/util/math_util.c:3-8 (proto TGT:src/util/math_util.h:3) | SIGNATURE_DIFF | High |
| S010.d1 | Log_Info | TGT:src/core/log.c:4-7 | SAME_AS_SOURCE | High |
| S010.d2 | Str_Get | TGT:src/resources/strings_en.c:10-13 | SAME_AS_SOURCE | High |

Counts (35 items: 27 S-ids incl. 1 ext + 8 dependencies): SAME_AS_SOURCE 3 · SAME_AS_BEFORE 5 · DIVERGED 7 · SIGNATURE_DIFF 1 · MISSING 19 · RENAMED 0 · RENAMED_CANDIDATE 0.

### Gaps, Evidence, and Confidence
- Feature absent in target: no `EcoMode_*`/`TonerSave_*`, no `eco_mode.*`/`toner_save.*`, no literals `100, 80, 60`, `Toner Save`; R17 of latest bodies vs target best blind 0.31 (not a match). `"TONER_SAVE"`/`"ECONOMODE"` only appear in the caller TGT:src/main.c:11-12 (dispatch currently returns -1). Raw: `_work/C_search_raw.txt`.
- DIVERGED items differ from REQ-B only by target-only FAX lines (TGT:src/panel/menu_table.c:10, TGT:src/print/render.c:9-11, TGT:src/resources/strings.h:7, TGT:src/resources/strings_en.c:7, TGT:src/settings/nv_settings.c:16, TGT:src/settings/nv_settings.h:10) and the Makefile (MODEL B, no density.c). Request anchor lines (DUPLEX neighbours, "render start") are intact → 3-way merge possible.
- SIGNATURE_DIFF: `Clamp` TGT:src/util/math_util.c:3 `int Clamp(int v, int hi)` (lo fixed 0) vs SRC:src/util/math_util.c:3 `int Clamp(int v, int lo, int hi)`; target callers: none. Ported callers: SRC:src/features/eco/eco_mode.c:24, SRC:src/print/density.c:6 (both lo = 0).
- Code gaps: `src/print/density.c`, `src/print/density.h` (Density_Scale, DENSITY_MAX) MISSING + their build entry.
- Data gaps: STR_TONER_SAVE (enum + the only language table), eco_level (struct + default; no version/CRC exists), "ECONOMODE" PJL entry, "TONER_SAVE" menu entry, build entries (eco_mode.c, density.c).
- Guard gap: `SUPPORT_TONER_SAVE` not defined for MODEL_B (TGT:config/model_config.h:5-6 → TGT:config/model_b.h, siblings SUPPORT_DUPLEX/SUPPORT_FAX at TGT:config/model_b.h:2-3).
- Header gap: `eco_mode.h` absent (new); `math_util.h`, `log.h`, `strings.h`, `nv_settings.h` present.
- Layout: inserting `eco_level` after `duplex` shifts `language`, `quality`, `fax_resolution` (NVRAM struct, TGT:src/settings/nv_settings.h:4); STR_TONER_SAVE shifts STR_QUALITY 2→3, STR_FAX 3→4.
- Alias map target column filled (`_work/alias_map.md`): all feature names MISSING (no target rename rule); target static `is_valid@src/panel/menu.c` unrelated.
- Closure: Iteration 1 +1 (build entry density.c); Iteration 2 +0 → fixpoint.

### Blockers
None blocking (no Low, no RENAMED_CANDIDATE). Decisions handed to D:
1. `Clamp` SIGNATURE_DIFF with no target callers → decision table row 14 (`REPLACE`). Question for review: replace target `Clamp(v, hi)` by source `Clamp(v, lo, hi)`? (yes/no)
2. `SUPPORT_TONER_SAVE` not enabled for MODEL_B → row 11 (`ENABLE_GUARD`, auto: add, flag). Question: enable toner save on model B? (yes/no)
3. NVRAM/enum layout shift in target (HIGH risk, row 15).

### Gate Result
PASS – 1 Coverage – 27/27 S-ids (incl. ext S027) + 8/8 dependencies (S008.d1, S009.d1–d4, S027.d1, S010.d1–d2) in `_work/C_trace.md` = 35 rows
PASS – 2 State vocabulary – only SAME_AS_SOURCE/SAME_AS_BEFORE/DIVERGED/SIGNATURE_DIFF/MISSING
PASS – 3 Evidence – 16 non-MISSING rows have TGT:path:line; 19 MISSING rows list R2/R11/R8/R17 searches
PASS – 4 Comparison done – SAME_AS_* by R7 (`diff` vs REQ-B / port version), modulo aliases where noted
PASS – 5 Target renames – 0 RENAMED / 0 RENAMED_CANDIDATE (no target equivalents found)
PASS – 6 Callers – SIGNATURE_DIFF/DIVERGED rows list target callers/users or none
PASS – 7 Data gaps – per place: enum, language table (1), STR_COUNT array, struct, default, version/CRC (none), 2 registries, config, 2 build entries
PASS – 8 Fixpoint reached – Iteration 2 +0
PASS – 9 Flows – FLOW-1..4 source + target chains with break points
PASS – 10 No assumed equivalence – no Low / RENAMED_CANDIDATE
PASS – 11 Read-only + status – `find SOURCE_ROOT TARGET_ROOT SOURCE_REQUEST -newer .start_marker` → 0; C = Complete
