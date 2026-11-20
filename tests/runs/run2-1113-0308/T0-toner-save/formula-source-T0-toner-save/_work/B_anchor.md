# B_anchor – request items in latest source (SOURCE_ROOT = A_latest)

Method note: every request name was found by exact name (R2) in the same file; each NAME hit was verified by kind + body
(R7 `diff` REQ-A vs SRC; R17 for the one evolved function). No renames → alias map is identity; `B_aliased/` = REQ-A copy.

## Files
| id (file/N/S/H) | request location | latest location | anchor result | latest state | method | evidence (signals) | confidence |
|---|---|---|---|---|---|---|---|
| Makefile | REQ-A:Makefile | SRC:Makefile | SAME_PATH | EVOLVED | NAME | `diff`: +L7 `SRCS += src/features/eco_report/eco_report.c` (UNRELATED); L2 already lists `src/print/density.c` (also in REQ-B) | High |
| config/model_a.h | REQ-A:config/model_a.h | SRC:config/model_a.h | SAME_PATH | EVOLVED | NAME | +L4 `#define SUPPORT_ECO_REPORT 1` (UNRELATED) | High |
| src/cmd/pjl_commands.c | REQ-A:src/cmd/pjl_commands.c | SRC:src/cmd/pjl_commands.c | SAME_PATH | UNCHANGED_IN_LATEST | NAME | `cmp` identical | High |
| src/features/toner_save/toner_save.c | REQ-A:src/features/toner_save/toner_save.c | SRC:src/features/toner_save/toner_save.c | SAME_PATH | EVOLVED | NAME | +L7 include math_util.h, +L24 Clamp (BUGFIX) | High |
| src/features/toner_save/toner_save.h | REQ-A:src/features/toner_save/toner_save.h | SRC:src/features/toner_save/toner_save.h | SAME_PATH | UNCHANGED_IN_LATEST | NAME | `cmp` identical | High |
| src/panel/menu_table.c | REQ-A:src/panel/menu_table.c | SRC:src/panel/menu_table.c | SAME_PATH | EVOLVED | NAME | +L7-9, +L19-21 SUPPORT_ECO_REPORT blocks (UNRELATED) | High |
| src/print/render.c | REQ-A:src/print/render.c | SRC:src/print/render.c | SAME_PATH | UNCHANGED_IN_LATEST | NAME | `cmp` identical | High |
| src/resources/strings.h | REQ-A:src/resources/strings.h | SRC:src/resources/strings.h | SAME_PATH | UNCHANGED_IN_LATEST | NAME | `cmp` identical | High |
| src/resources/strings_en.c | REQ-A:src/resources/strings_en.c | SRC:src/resources/strings_en.c | SAME_PATH | UNCHANGED_IN_LATEST | NAME | `cmp` identical | High |
| src/settings/nv_settings.c | REQ-A:src/settings/nv_settings.c | SRC:src/settings/nv_settings.c | SAME_PATH | UNCHANGED_IN_LATEST | NAME | `cmp` identical | High |
| src/settings/nv_settings.h | REQ-A:src/settings/nv_settings.h | SRC:src/settings/nv_settings.h | SAME_PATH | UNCHANGED_IN_LATEST | NAME | `cmp` identical | High |

## Nodes
| id (file/N/S/H) | request location | latest location | anchor result | latest state | method | evidence (signals) | confidence |
|---|---|---|---|---|---|---|---|
| N001 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 SUPPORT_TONER_SAVE | SAME_NAME | UNCHANGED_IN_LATEST | NAME | same line text | High |
| N002 | REQ-A:Makefile:6 | SRC:Makefile:6 SRCS += toner_save.c | SAME_NAME | UNCHANGED_IN_LATEST | NAME | same line text | High |
| N003 | REQ-A:src/cmd/pjl_commands.c:27 | SRC:src/cmd/pjl_commands.c:27 "ECONOMODE" | SAME_NAME | UNCHANGED_IN_LATEST | NAME | same line text | High |
| N004 | REQ-A:src/panel/menu_table.c:12 | SRC:src/panel/menu_table.c:15 "TONER_SAVE" | SAME_NAME | UNCHANGED_IN_LATEST | NAME | same line text (shifted +3 by ECO_REPORT include block) | High |
| N005 | REQ-A:src/resources/strings.h:6 | SRC:src/resources/strings.h:6 STR_TONER_SAVE | SAME_NAME | UNCHANGED_IN_LATEST | NAME | same line | High |
| N006 | REQ-A:src/resources/strings_en.c:6 | SRC:src/resources/strings_en.c:6 "Toner Save" | SAME_NAME | UNCHANGED_IN_LATEST | NAME | same line | High |
| N007 | REQ-A:src/settings/nv_settings.h:8 | SRC:src/settings/nv_settings.h:8 toner_save_level | SAME_NAME | UNCHANGED_IN_LATEST | NAME | same line | High |
| N008 | REQ-A:src/features/toner_save/toner_save.h:1 | SRC:src/features/toner_save/toner_save.h:1 TONER_SAVE_H | SAME_NAME | UNCHANGED_IN_LATEST | NAME | file identical | High |
| N009 | REQ-A:src/features/toner_save/toner_save.h:1 | SRC:src/features/toner_save/toner_save.h:1 toner_save.h | SAME_NAME | UNCHANGED_IN_LATEST | NAME | file identical | High |
| N010 | REQ-A:src/features/toner_save/toner_save.h:3 | SRC:src/features/toner_save/toner_save.h:3 TONER_SAVE_OFF/LOW/HIGH | SAME_NAME | UNCHANGED_IN_LATEST | NAME | file identical | High |
| N011 | REQ-A:src/cmd/pjl_commands.c:24 | SRC:src/cmd/pjl_commands.c:24 g_pjl_table | SAME_NAME | UNCHANGED_IN_LATEST | NAME | R7 range 24-28 identical | High |
| N012 | REQ-A:src/panel/menu_table.c:8 | SRC:src/panel/menu_table.c:11 g_menu_table | SAME_NAME | EVOLVED | NAME | R7: request lines kept; +L19-21 ECO_REPORT entry | High |
| N013 | REQ-A:src/resources/strings.h:3 | SRC:src/resources/strings.h:3 StrId_t | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| N014 | REQ-A:src/resources/strings_en.c:3 | SRC:src/resources/strings_en.c:3 g_strings_en | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| N015 | REQ-A:src/settings/nv_settings.h:5 | SRC:src/settings/nv_settings.h:5 NvSettings_t | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| N016 | REQ-A:src/features/toner_save/toner_save.c:8 | SRC:src/features/toner_save/toner_save.c:9 k_percent | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical text | High |
| N017 | REQ-A:src/features/toner_save/toner_save.c:10 | SRC:src/features/toner_save/toner_save.c:11 is_valid | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical body; only static `is_valid` in SRC | High |
| N018 | REQ-A:src/features/toner_save/toner_save.c:15 | SRC:src/features/toner_save/toner_save.c:16 TonerSave_GetLevel | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical body | High |
| N019 | REQ-A:src/features/toner_save/toner_save.c:20 | SRC:src/features/toner_save/toner_save.c:21 TonerSave_ApplyDensity | SAME_NAME | EVOLVED | NAME | R17 blind 0.96, sig =, calls 3/3; +L24 Clamp (BUGFIX) | High |
| N020 | REQ-A:src/features/toner_save/toner_save.c:28 | SRC:src/features/toner_save/toner_save.c:30 TonerSave_MenuHandler | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical body | High |
| N021 | REQ-A:src/features/toner_save/toner_save.c:37 | SRC:src/features/toner_save/toner_save.c:39 TonerSave_PjlSet | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical body | High |
| N022 | REQ-A:src/print/render.c:8 | SRC:src/print/render.c:8 Render_Page | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| N023 | REQ-A:src/settings/nv_settings.c:11 | SRC:src/settings/nv_settings.c:11 NV_LoadDefaults | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| N024 | REQ-A:src/features/toner_save/toner_save.c:1 | SRC:src/features/toner_save/toner_save.c:1 toner_save.c | SAME_NAME | EVOLVED | NAME | +L7 `#include "../../util/math_util.h"` (BUGFIX support) | High |
| N025 | REQ-A:src/cmd/pjl_commands.c:4 | SRC:src/cmd/pjl_commands.c:4 includes@pjl_commands.c | SAME_NAME | UNCHANGED_IN_LATEST | NAME | same line | High |
| N026 | REQ-A:src/settings/nv_settings.c:2 | SRC:src/settings/nv_settings.c:2 includes@nv_settings.c | SAME_NAME | UNCHANGED_IN_LATEST | NAME | same line | High |
| N027 | REQ-A:src/panel/menu_table.c:4 | SRC:src/panel/menu_table.c:4 SUPPORT_TONER_SAVE@menu_table.c | SAME_NAME | UNCHANGED_IN_LATEST | NAME | L4-6 same | High |
| N028 | REQ-A:src/print/render.c:3 | SRC:src/print/render.c:3 SUPPORT_TONER_SAVE@render.c | SAME_NAME | UNCHANGED_IN_LATEST | NAME | L3-5 same | High |
| N029 | outside request | SRC:src/settings/nv_settings.c:6 NV_GetSettings | SAME_NAME | UNCHANGED_IN_LATEST | NAME | definition + proto SRC:src/settings/nv_settings.h:13 | High |
| N030 | outside request | SRC:src/print/density.c:4 Density_Scale | SAME_NAME | UNCHANGED_IN_LATEST | NAME | proto SRC:src/print/density.h:4 | High |
| N031 | outside request | SRC:src/core/log.c:4 Log_Info | SAME_NAME | UNCHANGED_IN_LATEST | NAME | proto SRC:src/core/log.h:3 | High |
| N032 | outside request | SRC:src/resources/strings_en.c:10 Str_Get | SAME_NAME | UNCHANGED_IN_LATEST | NAME | proto SRC:src/resources/strings.h:11 | High |

## Symbols (S) and hunks (H)
| id (file/N/S/H) | request location | latest location | anchor result | latest state | method | evidence (signals) | confidence |
|---|---|---|---|---|---|---|---|
| S001 / H001 | REQ-A:Makefile:6 | SRC:Makefile:6 | SAME_NAME | UNCHANGED_IN_LATEST · H001 PRESENT | NAME | `grep -F` line found SRC:Makefile:6 | High |
| S002 / H002 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 | SAME_NAME | UNCHANGED_IN_LATEST · H002 PRESENT | NAME | SRC:config/model_a.h:3 | High |
| S003 / H003 | REQ-A:src/cmd/pjl_commands.c:4 | SRC:src/cmd/pjl_commands.c:4 | SAME_NAME | UNCHANGED_IN_LATEST · H003 PRESENT | NAME | same | High |
| S004 / H004 | REQ-A:src/cmd/pjl_commands.c:24-28 | SRC:src/cmd/pjl_commands.c:24-28 | SAME_NAME | UNCHANGED_IN_LATEST · H004 PRESENT | NAME | L27 found | High |
| S005 / H005 | REQ-A:src/features/toner_save/toner_save.c:1-7 | SRC:src/features/toner_save/toner_save.c:1-8 | SAME_NAME | EVOLVED · H005 PRESENT | NAME | 40/40 request lines found; +L7 BUGFIX include | High |
| S006 / H005 | REQ-A:…toner_save.c:8 | SRC:…toner_save.c:9 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| S007 / H005 | REQ-A:…toner_save.c:10-13 | SRC:…toner_save.c:11-14 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| S008 / H005,H006 | REQ-A:…toner_save.c:15-18 | SRC:…toner_save.c:16-19 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| S009 / H005,H006 | REQ-A:…toner_save.c:20-26 | SRC:…toner_save.c:21-28 | SAME_NAME | EVOLVED | NAME | R17 0.96 + `diff`: +L24 | High |
| S010 / H005,H006 | REQ-A:…toner_save.c:28-35 | SRC:…toner_save.c:30-37 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| S011 / H005,H006 | REQ-A:…toner_save.c:37-40 | SRC:…toner_save.c:39-42 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| S012 / H006 | REQ-A:…toner_save.h:1-2,13 | SRC:…toner_save.h:1-2,13 | SAME_NAME | UNCHANGED_IN_LATEST · H006 PRESENT | NAME | file identical | High |
| S013 / H006 | REQ-A:…toner_save.h:3-7 | SRC:…toner_save.h:3-7 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| S014 / H007 | REQ-A:src/panel/menu_table.c:4-6 | SRC:src/panel/menu_table.c:4-6 | SAME_NAME | UNCHANGED_IN_LATEST · H007 PRESENT | NAME | L4-6 found; L11-13 at SRC:14-16 | High |
| S015 / H007 | REQ-A:src/panel/menu_table.c:8-16 | SRC:src/panel/menu_table.c:11-22 | SAME_NAME | EVOLVED | NAME | +L19-21 ECO_REPORT (UNRELATED) | High |
| S016 / H008 | REQ-A:src/print/render.c:3-5 | SRC:src/print/render.c:3-5 | SAME_NAME | UNCHANGED_IN_LATEST · H008 PRESENT | NAME | file identical | High |
| S017 / H008 | REQ-A:src/print/render.c:8-16 | SRC:src/print/render.c:8-16 | SAME_NAME | UNCHANGED_IN_LATEST | NAME | identical | High |
| S018 / H009 | REQ-A:src/resources/strings.h:3-9 | SRC:src/resources/strings.h:3-9 | SAME_NAME | UNCHANGED_IN_LATEST · H009 PRESENT | NAME | identical | High |
| S019 / H010 | REQ-A:src/resources/strings_en.c:3-8 | SRC:src/resources/strings_en.c:3-8 | SAME_NAME | UNCHANGED_IN_LATEST · H010 PRESENT | NAME | identical | High |
| S020 / H011 | REQ-A:src/settings/nv_settings.c:2 | SRC:src/settings/nv_settings.c:2 | SAME_NAME | UNCHANGED_IN_LATEST · H011 PRESENT | NAME | identical | High |
| S021 / H012 | REQ-A:src/settings/nv_settings.c:11-18 | SRC:src/settings/nv_settings.c:11-18 | SAME_NAME | UNCHANGED_IN_LATEST · H012 PRESENT | NAME | identical | High |
| S022 / H013 | REQ-A:src/settings/nv_settings.h:5-11 | SRC:src/settings/nv_settings.h:5-11 | SAME_NAME | UNCHANGED_IN_LATEST · H013 PRESENT | NAME | identical | High |

Hunk presence: 13/13 `PRESENT` (all 74 `+` lines found with `grep -F` in the anchored latest files; none needed aliasing or R16).

## Iteration log
Iteration 1: +32 anchored (NAME 32, ALIAS 0, EDGE 0, FUZZY 0, ANCHOR 0, SIM 0, PATTERN 0)
Iteration 2: +0 anchored (nothing open) → loop finished.
Not-found eliminations: none (no node left open).

## Link cross-checks
All 41 edges of `A_links.md` re-read in latest source under the same names (N004/N012 lines shifted +3, N016–N021 +1..+2):
| from | type | to | latest evidence (SRC:path:line) | result |
|---|---|---|---|---|
| all 41 edges | (as A_links.md) | | same line text at SRC lines listed in Nodes table (e.g. N022 calls N019 SRC:src/print/render.c:12; N004 registers N020 SRC:src/panel/menu_table.c:15; N019 calls N017 SRC:src/features/toner_save/toner_save.c:25) | consistent (41) |
Counts: consistent 41 / changed 0 / broken 0.

## Evolution blocks (diff aliased REQ-A vs latest; alias = identity)
| S-id | block (SRC lines) | class (EXTENSION/BUGFIX/REFACTOR/UNRELATED/UNCLEAR) | R14 signals |
|---|---|---|---|
| S009 | SRC:src/features/toner_save/toner_save.c:24 `level = Clamp(level, TONER_SAVE_OFF, TONER_SAVE_HIGH); /* fix #1234: NV value hong */` | BUGFIX | 1 feature tokens `level`,`TONER_SAVE_OFF/HIGH`; 3 within ±3 of request line L22; 4 comment `fix #1234` (guards against bad NV value) |
| S005 | SRC:src/features/toner_save/toner_save.c:7 `#include "../../util/math_util.h"` | BUGFIX | in the feature's own file; supplies `Clamp` prototype for the S009 BUGFIX line |
| S015 | SRC:src/panel/menu_table.c:19-21 `#ifdef SUPPORT_ECO_REPORT` / `{ "ECO_REPORT", EcoReport_MenuHandler },` / `#endif` | UNRELATED | other feature's guard `SUPPORT_ECO_REPORT` and prefix `EcoReport_`; no toner-save token |
| file menu_table.c (file scope) | SRC:src/panel/menu_table.c:7-9 eco_report.h include block | UNRELATED | guard `SUPPORT_ECO_REPORT` |
| file Makefile | SRC:Makefile:7 `SRCS += src/features/eco_report/eco_report.c` | UNRELATED | other feature's file |
| file config/model_a.h | SRC:config/model_a.h:4 `#define SUPPORT_ECO_REPORT 1` | UNRELATED | other feature's guard macro |

## Extension hits (B4)
Searches run on SRC (latest names = request names):
`grep -rnw -E 'TonerSave_[A-Za-z0-9_]*|TONER_SAVE_[A-Z_]*|toner_save_level|STR_TONER_SAVE|SUPPORT_TONER_SAVE|ECONOMODE|"TONER_SAVE"|"Toner Save"'` + `grep -rn toner_save` (file paths) + `grep -n SUPPORT_TONER_SAVE` blocks.
| hit (SRC:path:line) | symbol | class (EXTENSION_NEW/CONSUMER/UNCLEAR) | reason |
|---|---|---|---|
| SRC:src/features/eco_report/eco_report.c:7 | EcoReport_Print (calls TonerSave_GetLevel, reads TONER_SAVE_OFF) | CONSUMER | separate feature: own folder, own prefix `EcoReport_`, own guard `SUPPORT_ECO_REPORT` (SRC:config/model_a.h:4), registered separately SRC:src/panel/menu_table.c:20 |
| SRC:src/features/eco_report/eco_report.c:2 | include of toner_save.h | CONSUMER | same feature as above |
| SRC:src/main.c:11-12 | main (calls Menu_Dispatch("TONER_SAVE"), Pjl_Dispatch("ECONOMODE")) | CONSUMER | demo driver, outside feature; identical in target (TGT:src/main.c:11-12) |
| all other hits | request symbols themselves | – | already anchored (N001–N028) |
EXTENSION_NEW: none.
