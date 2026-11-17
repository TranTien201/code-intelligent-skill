# B_anchor – request items in latest source (SOURCE_ROOT = A_latest)

Order used (B2.0): stable → medium → volatile; feature ids for R16/R17 in `B_feature_ids.txt` (17 names; external and file-scope nodes excluded so they stay literal anchors).
Raw evidence: `_work/B_sim_raw.txt` (R17), `_work/B_search_raw.txt` (R11, R16, name greps), `_work/B_aliased_vs_latest.txt` (B2.6).

## Files
| id (file/N/S/H) | request location | latest location | anchor result | latest state | method | evidence (signals) | confidence |
|---|---|---|---|---|---|---|---|
| F01 | REQ-A:Makefile | SRC:Makefile | SAME_PATH | EVOLVED | NAME | path exists; aliased L6 = SRC:Makefile:6; +L7 eco_report (other feature) | High |
| F02 | REQ-A:config/model_a.h | SRC:config/model_a.h | SAME_PATH | EVOLVED | NAME | L3 identical SRC:config/model_a.h:3; +L4 `SUPPORT_ECO_REPORT` | High |
| F03 | REQ-A:src/cmd/pjl_commands.c | SRC:src/cmd/pjl_commands.c | SAME_PATH | UNCHANGED_IN_LATEST | NAME | equal modulo aliases (diff empty) | High |
| F04 | REQ-A:src/features/toner_save/toner_save.c | SRC:src/features/eco/eco_mode.c | MOVED_FILE | EVOLVED | EDGE | R11a basename: none; R11c 58% (next 8%); EDGE builds SRC:Makefile:6 | High |
| F05 | REQ-A:src/features/toner_save/toner_save.h | SRC:src/features/eco/eco_mode.h | MOVED_FILE | UNCHANGED_IN_LATEST | EDGE | R11c 45% (next 9%); EDGE includes SRC:src/cmd/pjl_commands.c:4, SRC:src/print/render.c:4 | High |
| F06 | REQ-A:src/panel/menu_table.c | SRC:src/panel/menu_table.c | SAME_PATH | EVOLVED | NAME | +L7-9, +L19-21 eco_report (other feature) | High |
| F07 | REQ-A:src/print/render.c | SRC:src/print/render.c | SAME_PATH | UNCHANGED_IN_LATEST | NAME | equal modulo aliases | High |
| F08 | REQ-A:src/resources/strings.h | SRC:src/resources/strings.h | SAME_PATH | UNCHANGED_IN_LATEST | NAME | identical | High |
| F09 | REQ-A:src/resources/strings_en.c | SRC:src/resources/strings_en.c | SAME_PATH | UNCHANGED_IN_LATEST | NAME | identical | High |
| F10 | REQ-A:src/settings/nv_settings.c | SRC:src/settings/nv_settings.c | SAME_PATH | UNCHANGED_IN_LATEST | NAME | equal modulo aliases | High |
| F11 | REQ-A:src/settings/nv_settings.h | SRC:src/settings/nv_settings.h | SAME_PATH | UNCHANGED_IN_LATEST | NAME | equal modulo aliases | High |

## Symbols (S-ids, see B_symbols.md)
| id (file/N/S/H) | request location | latest location | anchor result | latest state | method | evidence (signals) | confidence |
|---|---|---|---|---|---|---|---|
| S001 | REQ-A:Makefile:6 | SRC:Makefile:6 | SAME_PATH | EVOLVED | NAME | N002 | High |
| S002 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | N001 | High |
| S003 | REQ-A:src/cmd/pjl_commands.c:4 | SRC:src/cmd/pjl_commands.c:4 | SAME_PATH | UNCHANGED_IN_LATEST | NAME | N022 (modulo aliases) | High |
| S004 | REQ-A:src/cmd/pjl_commands.c:24-28 | SRC:src/cmd/pjl_commands.c:24-28 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | N011 (modulo aliases) | High |
| S005 | REQ-A:src/features/toner_save/toner_save.c:1-7 | SRC:src/features/eco/eco_mode.c:1-8 | MOVED_FILE | EVOLVED | EDGE | N023 | High |
| S006 | REQ-A:src/features/toner_save/toner_save.c:8 | SRC:src/features/eco/eco_mode.c:9 | MOVED_SYMBOL | UNCHANGED_IN_LATEST | NAME | N005 | High |
| S007 | REQ-A:src/features/toner_save/toner_save.c:10-13 | SRC:src/features/eco/eco_mode.c:11-14 | MOVED_SYMBOL | UNCHANGED_IN_LATEST | NAME | N006 | High |
| S008 | REQ-A:src/features/toner_save/toner_save.c:15-18 | SRC:src/features/eco/eco_mode.c:16-19 | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | N007 | High |
| S009 | REQ-A:src/features/toner_save/toner_save.c:20-26 | SRC:src/features/eco/eco_mode.c:28-34 | RENAMED_SYMBOL | EVOLVED | EDGE | N008 | High |
| S010 | REQ-A:src/features/toner_save/toner_save.c:28-35 | SRC:src/features/eco/eco_mode.c:36-43 | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | N009 | High |
| S011 | REQ-A:src/features/toner_save/toner_save.c:37-40 | SRC:src/features/eco/eco_mode.c:45-48 | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | N010 | High |
| S012 | REQ-A:src/features/toner_save/toner_save.h:1-2,13 | SRC:src/features/eco/eco_mode.h:1-2,13 | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | N003 | High |
| S013 | REQ-A:src/features/toner_save/toner_save.h:3-7 | SRC:src/features/eco/eco_mode.h:3-7 | MOVED_SYMBOL | UNCHANGED_IN_LATEST | NAME | N004 | High |
| S014 | REQ-A:src/features/toner_save/toner_save.h:9 | SRC:src/features/eco/eco_mode.h:9 | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | N027 | High |
| S015 | REQ-A:src/features/toner_save/toner_save.h:10 | SRC:src/features/eco/eco_mode.h:10 | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | N028 | High |
| S016 | REQ-A:src/features/toner_save/toner_save.h:11 | SRC:src/features/eco/eco_mode.h:11 | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | N029 | High |
| S017 | REQ-A:src/features/toner_save/toner_save.h:12 | SRC:src/features/eco/eco_mode.h:12 | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | N030 | High |
| S018 | REQ-A:src/panel/menu_table.c:4-6 | SRC:src/panel/menu_table.c:4-6 | SAME_PATH | EVOLVED | NAME | N024 | High |
| S019 | REQ-A:src/panel/menu_table.c:8-16 | SRC:src/panel/menu_table.c:11-22 | SAME_NAME | EVOLVED | NAME | N013 | High |
| S020 | REQ-A:src/print/render.c:3-5 | SRC:src/print/render.c:3-5 | SAME_PATH | UNCHANGED_IN_LATEST | NAME | N025 | High |
| S021 | REQ-A:src/print/render.c:8-16 | SRC:src/print/render.c:8-16 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | N015 | High |
| S022 | REQ-A:src/resources/strings.h:3-9 | SRC:src/resources/strings.h:3-9 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | N016/N017 | High |
| S023 | REQ-A:src/resources/strings_en.c:3-8 | SRC:src/resources/strings_en.c:3-8 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | N018 | High |
| S024 | REQ-A:src/settings/nv_settings.c:2 | SRC:src/settings/nv_settings.c:2 | SAME_PATH | UNCHANGED_IN_LATEST | NAME | N026 | High |
| S025 | REQ-A:src/settings/nv_settings.c:11-18 | SRC:src/settings/nv_settings.c:11-18 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | N021 | High |
| S026 | REQ-A:src/settings/nv_settings.h:5-11 | SRC:src/settings/nv_settings.h:5-11 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | N019/N020 | High |
| S027 (ext) | – | SRC:src/features/eco/eco_mode.c:21-26 | (new in latest) | EVOLVED | NAME | B4 hit: static helper extracted by BUGFIX fix #1234 | High |

## Hunks (B2.6, aliased + lines searched in the anchored latest bodies)
| id (file/N/S/H) | request location | latest location | anchor result | latest state | method | evidence (signals) | confidence |
|---|---|---|---|---|---|---|---|
| H001 | REQ-A:Makefile:6 | SRC:Makefile:6 | SAME_PATH | PRESENT | ALIAS | line found (modulo aliases) | High |
| H002 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 | SAME_PATH | PRESENT | NAME | grep -F exact | High |
| H003 | REQ-A:src/cmd/pjl_commands.c:4 | SRC:src/cmd/pjl_commands.c:4 | SAME_PATH | PRESENT | ALIAS | (modulo aliases) | High |
| H004 | REQ-A:src/cmd/pjl_commands.c:27 | SRC:src/cmd/pjl_commands.c:27 | SAME_PATH | PRESENT | ALIAS | (modulo aliases) | High |
| H005 | REQ-A:src/features/toner_save/toner_save.c:1-40 | SRC:src/features/eco/eco_mode.c:1-48 | MOVED_FILE | PARTIAL | ALIAS | 33/34 non-blank lines found (modulo aliases); missing REQ-A L23 `if (!is_valid(level))` → replaced by BUGFIX SRC:src/features/eco/eco_mode.c:25,31 | High |
| H006 | REQ-A:src/features/toner_save/toner_save.h:1-13 | SRC:src/features/eco/eco_mode.h:1-13 | MOVED_FILE | PRESENT | ALIAS | 12/12 non-blank lines (modulo aliases) | High |
| H007 | REQ-A:src/panel/menu_table.c:4-6,11-13 | SRC:src/panel/menu_table.c:4-6,14-16 | SAME_PATH | PRESENT | ALIAS | 6/6 (modulo aliases) | High |
| H008 | REQ-A:src/print/render.c:3-5,11-13 | SRC:src/print/render.c:3-5,11-13 | SAME_PATH | PRESENT | ALIAS | 6/6 (modulo aliases) | High |
| H009 | REQ-A:src/resources/strings.h:6 | SRC:src/resources/strings.h:6 | SAME_PATH | PRESENT | NAME | exact | High |
| H010 | REQ-A:src/resources/strings_en.c:6 | SRC:src/resources/strings_en.c:6 | SAME_PATH | PRESENT | NAME | exact | High |
| H011 | REQ-A:src/settings/nv_settings.c:2 | SRC:src/settings/nv_settings.c:2 | SAME_PATH | PRESENT | ALIAS | (modulo aliases) | High |
| H012 | REQ-A:src/settings/nv_settings.c:15 | SRC:src/settings/nv_settings.c:15 | SAME_PATH | PRESENT | ALIAS | (modulo aliases) | High |
| H013 | REQ-A:src/settings/nv_settings.h:8 | SRC:src/settings/nv_settings.h:8 | SAME_PATH | PRESENT | ALIAS | (modulo aliases) | High |

## Link cross-checks (B2.3)
| from | type | to | latest evidence (SRC:path:line) | result (consistent/changed/broken) |
|---|---|---|---|---|
| N002 | builds | N023 | SRC:Makefile:6 | consistent |
| N023 | includes | N003 | SRC:src/features/eco/eco_mode.c:2 | consistent |
| N022 | includes | N003 | SRC:src/cmd/pjl_commands.c:4 | consistent |
| N024 | includes | N003 | SRC:src/panel/menu_table.c:5 | consistent |
| N025 | includes | N003 | SRC:src/print/render.c:4 | consistent |
| N026 | includes | N003 | SRC:src/settings/nv_settings.c:2 | consistent |
| N001 | guards | N024 | SRC:src/panel/menu_table.c:4 | consistent |
| N001 | guards | N014 | SRC:src/panel/menu_table.c:14 | consistent |
| N001 | guards | N025 | SRC:src/print/render.c:3 | consistent |
| N001 | guards | N015 | SRC:src/print/render.c:11 | consistent |
| N003 | guards | N004 | SRC:src/features/eco/eco_mode.h:1 | consistent |
| N011 | registers | N012 | SRC:src/cmd/pjl_commands.c:27 | consistent |
| N012 | registers | N010 | SRC:src/cmd/pjl_commands.c:27 | consistent |
| N013 | registers | N014 | SRC:src/panel/menu_table.c:15 | consistent |
| N014 | registers | N009 | SRC:src/panel/menu_table.c:15 | consistent |
| N015 | calls | N008 | SRC:src/print/render.c:12 | consistent |
| N008 | calls | N007 | SRC:src/features/eco/eco_mode.c:23 | changed (now via helper eco_effective_level, BUGFIX) |
| N008 | calls | N006 | SRC:src/features/eco/eco_mode.c:25 | changed (now via helper eco_effective_level, BUGFIX) |
| N008 | reads | N005 | SRC:src/features/eco/eco_mode.c:33 | consistent |
| N008 | uses-external | N032 | SRC:src/features/eco/eco_mode.c:33 | consistent |
| N009 | calls | N006 | SRC:src/features/eco/eco_mode.c:38 | consistent |
| N009 | writes | N020 | SRC:src/features/eco/eco_mode.c:40 | consistent |
| N009 | uses-external | N031 | SRC:src/features/eco/eco_mode.c:40 | consistent |
| N009 | uses-external | N033 | SRC:src/features/eco/eco_mode.c:41 | consistent |
| N009 | uses-external | N034 | SRC:src/features/eco/eco_mode.c:41 | consistent |
| N009 | reads | N017 | SRC:src/features/eco/eco_mode.c:41 | consistent |
| N010 | calls | N009 | SRC:src/features/eco/eco_mode.c:47 | consistent |
| N007 | reads | N020 | SRC:src/features/eco/eco_mode.c:18 | consistent |
| N007 | uses-external | N031 | SRC:src/features/eco/eco_mode.c:18 | consistent |
| N006 | reads | N004 | SRC:src/features/eco/eco_mode.c:13 | consistent |
| N021 | defaults | N020 | SRC:src/settings/nv_settings.c:15 | consistent |
| N021 | reads | N004 | SRC:src/settings/nv_settings.c:15 | consistent |
| N019 | declares | N020 | SRC:src/settings/nv_settings.h:8 | consistent |
| N016 | declares | N017 | SRC:src/resources/strings.h:6 | consistent |
| N018 | localizes | N017 | SRC:src/resources/strings_en.c:6 | consistent |
| N018 | indexes | N016 | SRC:src/resources/strings_en.c:3 | consistent |
| N027 | declares | N007 | SRC:src/features/eco/eco_mode.h:9 | consistent |
| N028 | declares | N008 | SRC:src/features/eco/eco_mode.h:10 | consistent |
| N029 | declares | N009 | SRC:src/features/eco/eco_mode.h:11 | consistent |
| N030 | declares | N010 | SRC:src/features/eco/eco_mode.h:12 | consistent |

Counts: consistent 38 / changed 2 / broken 0.

## Iteration log
Iteration 1: +34 anchored (NAME 20, ANCHOR 2, EDGE 12 [incl. 2 MOVED_FILE via R11+EDGE], FUZZY 0 as primary, SIM 0 as primary, PATTERN 0 as primary)
Iteration 2: +0 anchored → stop.
Not-found eliminations: none (no NOT_FOUND nodes).

## Evolution blocks (B3, aliased REQ-A vs latest)
| S-id | block (SRC lines) | class (EXTENSION/BUGFIX/REFACTOR/UNRELATED/UNCLEAR) | R14 signals |
|---|---|---|---|
| S001 | SRC:Makefile:6 | REFACTOR | path rename only (equal modulo aliases) |
| S001 | SRC:Makefile:7 `SRCS += src/features/eco_report/eco_report.c` | UNCLEAR → AUTO-DECIDED UNRELATED | sig3 (±1 line of request line) vs. contradiction: builds another feature's file (eco_report, CONSUMER, own guard SUPPORT_ECO_REPORT) |
| S005 | SRC:src/features/eco/eco_mode.c:7 `#include "../../util/math_util.h"` | BUGFIX | sig1 needed by `Clamp` in fix #1234 line :24; sig3 adjacent to request include lines |
| S009 | SRC:src/features/eco/eco_mode.c:21-26 (new helper eco_effective_level) + :30-31 | BUGFIX | sig1 feature tokens TONER_SAVE_OFF/HIGH, is_valid, EcoMode_GetLevel; sig3 replaces request L22-23; sig4 comment `fix #1234: NV value hong` |
| S018 | SRC:src/panel/menu_table.c:7-9 (eco_report include) | UNCLEAR → AUTO-DECIDED UNRELATED | sig3 adjacent to request L4-6 vs. other guard SUPPORT_ECO_REPORT + other feature tokens |
| S019 | SRC:src/panel/menu_table.c:19-21 (ECO_REPORT entry) | UNCLEAR → AUTO-DECIDED UNRELATED | sig3 (3 lines after request L16) vs. other guard SUPPORT_ECO_REPORT, handler EcoReport_MenuHandler |
| F02 (file, no S) | SRC:config/model_a.h:4 `#define SUPPORT_ECO_REPORT 1` | UNRELATED | not in a request symbol; guard of CONSUMER eco_report |

## Extension hits (B4)
Searches run (latest + request names): `grep -rnw -E 'EcoMode_[A-Za-z]+|eco_effective_level'`, `grep -rnwE 'TonerSave_[A-Za-z]+|toner_save_level|TONER_SAVE_H'` (0 hits), `grep -rnw SUPPORT_TONER_SAVE`, `grep -rnw -e eco_level -e STR_TONER_SAVE -e ECONOMODE -e '"TONER_SAVE"'`, `grep -rn -e ECO_REPORT -e EcoReport -e eco_report`, prefix `Eco[A-Za-z]*_`, guard blocks R5 inverse.
| hit (SRC:path:line) | symbol | class (EXTENSION_NEW/CONSUMER/UNCLEAR) | reason |
|---|---|---|---|
| SRC:src/features/eco/eco_mode.c:21-26 | eco_effective_level | EXTENSION_NEW | in the feature's file, only reachable from EcoMode_ApplyDensity; BUGFIX helper → S027 (ext) |
| SRC:src/features/eco_report/eco_report.c:5-15 | EcoReport_Print, EcoReport_MenuHandler | CONSUMER | uses EcoMode_GetLevel (:7) + TONER_SAVE_OFF; own guard SUPPORT_ECO_REPORT, own files, own prefix EcoReport_ → REPORT_ONLY |
| SRC:src/features/eco_report/eco_report.h:1-5 | ECO_REPORT_H, prototypes | CONSUMER | header of eco_report |
| SRC:src/panel/menu_table.c:7-9,19-21 | eco_report include + menu entry | CONSUMER | guarded by SUPPORT_ECO_REPORT |
| SRC:Makefile:7 | build entry eco_report.c | CONSUMER | builds eco_report |
| SRC:config/model_a.h:4 | SUPPORT_ECO_REPORT | CONSUMER | eco_report guard |
| SRC:src/main.c:11-12 | main (Menu_Dispatch "TONER_SAVE", Pjl_Dispatch "ECONOMODE") | CONSUMER | pre-existing caller through dispatch tables; identical in target TGT:src/main.c:11-12 |

## Nodes (kept last: links_view.py reads the last row per N-id; cross-check rows also start with N-ids)
| id (file/N/S/H) | request location | latest location | anchor result | latest state | method | evidence (signals) | confidence |
|---|---|---|---|---|---|---|---|
| N001 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 SUPPORT_TONER_SAVE | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical line; also guards SRC:src/panel/menu_table.c:4,14, SRC:src/print/render.c:3,11 | High |
| N002 | REQ-A:Makefile:6 | SRC:Makefile:6 Makefile | SAME_PATH | EVOLVED | NAME | L6 equal modulo aliases; L7 added (eco_report) | High |
| N003 | REQ-A:src/features/toner_save/toner_save.h:1 | SRC:src/features/eco/eco_mode.h:1 ECO_MODE_H | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | EDGE guard of moved header (F05) + ANCHOR same structure L1-2,13; name TONER_SAVE_H: 0 hits (L0) | High |
| N004 | REQ-A:src/features/toner_save/toner_save.h:3 | SRC:src/features/eco/eco_mode.h:3 TONER_SAVE_OFF/LOW/HIGH | MOVED_SYMBOL | UNCHANGED_IN_LATEST | NAME | enum body identical L3-7 (values 0/1/2) | High |
| N005 | REQ-A:src/features/toner_save/toner_save.c:8 | SRC:src/features/eco/eco_mode.c:9 k_percent | MOVED_SYMBOL | UNCHANGED_IN_LATEST | NAME | identical; R17 blind 1.00 lits 3/3 | High |
| N006 | REQ-A:src/features/toner_save/toner_save.c:10 | SRC:src/features/eco/eco_mode.c:11 is_valid | MOVED_SYMBOL | UNCHANGED_IN_LATEST | NAME | body identical; R17 1.00 SIG =; other static is_valid@SRC:src/panel/menu.c:5 rejected (blind 0.12) | High |
| N007 | REQ-A:src/features/toner_save/toner_save.c:15 | SRC:src/features/eco/eco_mode.c:16 EcoMode_GetLevel | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | EDGE(N027 declares slot SRC:src/features/eco/eco_mode.h:9) + FUZZY SRC:src/features/eco/eco_mode.c:18 + SIG = (SIM 1.00 TOO-SHORT) | High |
| N008 | REQ-A:src/features/toner_save/toner_save.c:20 | SRC:src/features/eco/eco_mode.c:28 EcoMode_ApplyDensity | RENAMED_SYMBOL | EVOLVED | EDGE | EDGE(N015 calls SRC:src/print/render.c:12) + SIM 0.71 + SIG = ; part of body moved into eco_effective_level SRC:src/features/eco/eco_mode.c:21-26 (blind 0.36, no SPLIT flag) | High |
| N009 | REQ-A:src/features/toner_save/toner_save.c:28 | SRC:src/features/eco/eco_mode.c:36 EcoMode_MenuHandler | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | EDGE(N014 registers SRC:src/panel/menu_table.c:15) + SIM 1.00 + SIG = + FUZZY :40 | High |
| N010 | REQ-A:src/features/toner_save/toner_save.c:37 | SRC:src/features/eco/eco_mode.c:45 EcoMode_PjlSet | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | EDGE(N012 registers SRC:src/cmd/pjl_commands.c:27) + SIG = + PATTERN TonerSave_→EcoMode_ (SIM 1.00 TOO-SHORT) | High |
| N011 | REQ-A:src/cmd/pjl_commands.c:24 | SRC:src/cmd/pjl_commands.c:24 g_pjl_table | SAME_NAME | UNCHANGED_IN_LATEST | NAME | equal modulo aliases | High |
| N012 | REQ-A:src/cmd/pjl_commands.c:27 | SRC:src/cmd/pjl_commands.c:27 "ECONOMODE" | SAME_NAME | UNCHANGED_IN_LATEST | ANCHOR | literal "ECONOMODE" unique in table | High |
| N013 | REQ-A:src/panel/menu_table.c:8 | SRC:src/panel/menu_table.c:11 g_menu_table | SAME_NAME | EVOLVED | NAME | +ECO_REPORT entry L19-21 | High |
| N014 | REQ-A:src/panel/menu_table.c:12 | SRC:src/panel/menu_table.c:15 "TONER_SAVE" | SAME_NAME | UNCHANGED_IN_LATEST | ANCHOR | literal "TONER_SAVE" under same guard L14-16 | High |
| N015 | REQ-A:src/print/render.c:8 | SRC:src/print/render.c:8 Render_Page | SAME_NAME | UNCHANGED_IN_LATEST | NAME | equal modulo aliases | High |
| N016 | REQ-A:src/resources/strings.h:3 | SRC:src/resources/strings.h:3 StrId_t | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| N017 | REQ-A:src/resources/strings.h:6 | SRC:src/resources/strings.h:6 STR_TONER_SAVE | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical, same position | High |
| N018 | REQ-A:src/resources/strings_en.c:3 | SRC:src/resources/strings_en.c:3 g_strings_en | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| N019 | REQ-A:src/settings/nv_settings.h:5 | SRC:src/settings/nv_settings.h:5 NvSettings_t | SAME_NAME | UNCHANGED_IN_LATEST | NAME | equal modulo aliases | High |
| N020 | REQ-A:src/settings/nv_settings.h:8 | SRC:src/settings/nv_settings.h:8 eco_level | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | EDGE(N019 declares, same slot duplex→?→language) + FUZZY SRC:src/features/eco/eco_mode.c:18, :40 (kept=3) + EDGE(N021 defaults SRC:src/settings/nv_settings.c:15) | High |
| N021 | REQ-A:src/settings/nv_settings.c:11 | SRC:src/settings/nv_settings.c:11 NV_LoadDefaults | SAME_NAME | UNCHANGED_IN_LATEST | NAME | equal modulo aliases | High |
| N022 | REQ-A:src/cmd/pjl_commands.c:4 | SRC:src/cmd/pjl_commands.c:4 file-scope | SAME_PATH | UNCHANGED_IN_LATEST | NAME | include path aliased (eco/eco_mode.h) | High |
| N023 | REQ-A:src/features/toner_save/toner_save.c:1 | SRC:src/features/eco/eco_mode.c:1 file-scope | MOVED_FILE | EVOLVED | EDGE | F04; +L7 `#include "../../util/math_util.h"` | High |
| N024 | REQ-A:src/panel/menu_table.c:4 | SRC:src/panel/menu_table.c:4 file-scope | SAME_PATH | EVOLVED | NAME | L4-6 aliased equal; +L7-9 eco_report include | High |
| N025 | REQ-A:src/print/render.c:3 | SRC:src/print/render.c:3 file-scope | SAME_PATH | UNCHANGED_IN_LATEST | NAME | equal modulo aliases | High |
| N026 | REQ-A:src/settings/nv_settings.c:2 | SRC:src/settings/nv_settings.c:2 file-scope | SAME_PATH | UNCHANGED_IN_LATEST | NAME | equal modulo aliases | High |
| N027 | REQ-A:src/features/toner_save/toner_save.h:9 | SRC:src/features/eco/eco_mode.h:9 EcoMode_GetLevel | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | EDGE declares N007 + NEIGHBOR (slot 1 after enum) + SIG = + PATTERN | High |
| N028 | REQ-A:src/features/toner_save/toner_save.h:10 | SRC:src/features/eco/eco_mode.h:10 EcoMode_ApplyDensity | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | EDGE declares N008 + NEIGHBOR slot 2 + SIG = + PATTERN | High |
| N029 | REQ-A:src/features/toner_save/toner_save.h:11 | SRC:src/features/eco/eco_mode.h:11 EcoMode_MenuHandler | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | EDGE declares N009 + NEIGHBOR slot 3 + SIG = + PATTERN | High |
| N030 | REQ-A:src/features/toner_save/toner_save.h:12 | SRC:src/features/eco/eco_mode.h:12 EcoMode_PjlSet | RENAMED_SYMBOL | UNCHANGED_IN_LATEST | EDGE | EDGE declares N010 + NEIGHBOR slot 4 + SIG = + PATTERN | High |
| N031 | outside request | SRC:src/settings/nv_settings.c:6 NV_GetSettings | SAME_NAME | UNCHANGED_IN_LATEST | NAME | definition; prototype SRC:src/settings/nv_settings.h:13 | High |
| N032 | outside request | SRC:src/print/density.c:4 Density_Scale | SAME_NAME | UNCHANGED_IN_LATEST | NAME | definition; prototype SRC:src/print/density.h:4 | High |
| N033 | outside request | SRC:src/core/log.c:4 Log_Info | SAME_NAME | UNCHANGED_IN_LATEST | NAME | definition; prototype SRC:src/core/log.h:3 | High |
| N034 | outside request | SRC:src/resources/strings_en.c:10 Str_Get | SAME_NAME | UNCHANGED_IN_LATEST | NAME | definition; prototype SRC:src/resources/strings.h:11 | High |

