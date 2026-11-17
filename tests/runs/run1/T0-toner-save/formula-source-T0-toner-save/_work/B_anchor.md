# B_anchor (all latest paths in SRC = SOURCE_ROOT; no history, content comparison only)

## Files
| id (file/S/H) | request location | latest location | anchor result | latest state | evidence | confidence |
|---|---|---|---|---|---|---|
| F1 | REQ-A:Makefile | SRC:Makefile | SAME_PATH | EVOLVED | `diff` REQ-A vs SRC: +L7 `SRCS += src/features/eco_report/eco_report.c` | High |
| F2 | REQ-A:config/model_a.h | SRC:config/model_a.h | SAME_PATH | EVOLVED | +L4 `#define SUPPORT_ECO_REPORT 1` | High |
| F3 | REQ-A:src/cmd/pjl_commands.c | SRC:src/cmd/pjl_commands.c | SAME_PATH | UNCHANGED_IN_LATEST | `diff` identical | High |
| F4 | REQ-A:src/features/toner_save/toner_save.c | SRC:src/features/toner_save/toner_save.c | SAME_PATH | EVOLVED | +L7 include math_util.h, +L24 Clamp | High |
| F5 | REQ-A:src/features/toner_save/toner_save.h | SRC:src/features/toner_save/toner_save.h | SAME_PATH | UNCHANGED_IN_LATEST | identical | High |
| F6 | REQ-A:src/panel/menu_table.c | SRC:src/panel/menu_table.c | SAME_PATH | EVOLVED | +L7-9 ECO include block, +L19-21 ECO table entry | High |
| F7 | REQ-A:src/print/render.c | SRC:src/print/render.c | SAME_PATH | UNCHANGED_IN_LATEST | identical | High |
| F8 | REQ-A:src/resources/strings.h | SRC:src/resources/strings.h | SAME_PATH | UNCHANGED_IN_LATEST | identical | High |
| F9 | REQ-A:src/resources/strings_en.c | SRC:src/resources/strings_en.c | SAME_PATH | UNCHANGED_IN_LATEST | identical | High |
| F10 | REQ-A:src/settings/nv_settings.c | SRC:src/settings/nv_settings.c | SAME_PATH | UNCHANGED_IN_LATEST | identical | High |
| F11 | REQ-A:src/settings/nv_settings.h | SRC:src/settings/nv_settings.h | SAME_PATH | UNCHANGED_IN_LATEST | identical | High |

## Symbols
| id (file/S/H) | request location | latest location | anchor result | latest state | evidence | confidence |
|---|---|---|---|---|---|---|
| S001 | REQ-A:Makefile:6 | SRC:Makefile:6 | SAME_NAME | UNCHANGED_IN_LATEST | line identical (`grep -F`) | High |
| S002 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 | SAME_NAME | UNCHANGED_IN_LATEST | identical | High |
| S003 | REQ-A:src/cmd/pjl_commands.c:1-4 | SRC:src/cmd/pjl_commands.c:1-4 | SAME_NAME | UNCHANGED_IN_LATEST | identical | High |
| S004 | REQ-A:src/cmd/pjl_commands.c:24-28 | SRC:src/cmd/pjl_commands.c:24-28 | SAME_NAME | UNCHANGED_IN_LATEST | R7 SAME | High |
| S005 | REQ-A:src/features/toner_save/toner_save.c:1-7 | SRC:src/features/toner_save/toner_save.c:1-8 | SAME_NAME | EVOLVED | +L7 `#include "../../util/math_util.h"` | High |
| S006 | REQ-A:…/toner_save.c:8 | SRC:…/toner_save.c:9 | SAME_NAME | UNCHANGED_IN_LATEST | R7 SAME | High |
| S007 | REQ-A:…/toner_save.c:10-13 | SRC:…/toner_save.c:11-14 | SAME_NAME | UNCHANGED_IN_LATEST | R7 SAME (static; another `is_valid` at SRC:src/panel/menu.c:5) | High |
| S008 | REQ-A:…/toner_save.c:15-18 | SRC:…/toner_save.c:16-19 | SAME_NAME | UNCHANGED_IN_LATEST | R7 SAME | High |
| S009 | REQ-A:…/toner_save.c:20-26 | SRC:…/toner_save.c:21-28 | SAME_NAME | EVOLVED | +L24 Clamp line | High |
| S010 | REQ-A:…/toner_save.c:28-35 | SRC:…/toner_save.c:30-37 | SAME_NAME | UNCHANGED_IN_LATEST | R7 SAME | High |
| S011 | REQ-A:…/toner_save.c:37-40 | SRC:…/toner_save.c:39-42 | SAME_NAME | UNCHANGED_IN_LATEST | R7 SAME | High |
| S012 | REQ-A:…/toner_save.h:1-2,13 | SRC:…/toner_save.h:1-2,13 | SAME_NAME | UNCHANGED_IN_LATEST | identical file | High |
| S013 | REQ-A:…/toner_save.h:3-7 | SRC:…/toner_save.h:3-7 | SAME_NAME | UNCHANGED_IN_LATEST | identical file | High |
| S014-S017 | REQ-A:…/toner_save.h:9-12 | SRC:…/toner_save.h:9-12 | SAME_NAME | UNCHANGED_IN_LATEST | identical file | High |
| S018 | REQ-A:src/panel/menu_table.c:4-6 | SRC:src/panel/menu_table.c:4-6 | SAME_NAME | UNCHANGED_IN_LATEST | lines identical; new sibling block L7-9 is outside S018 (B4 hit X2) | High |
| S019 | REQ-A:src/panel/menu_table.c:8-16 | SRC:src/panel/menu_table.c:11-22 | SAME_NAME | EVOLVED | +L19-21 ECO_REPORT entry | High |
| S020 | REQ-A:src/print/render.c:3-5 | SRC:src/print/render.c:3-5 | SAME_NAME | UNCHANGED_IN_LATEST | identical | High |
| S021 | REQ-A:src/print/render.c:8-16 | SRC:src/print/render.c:8-16 | SAME_NAME | UNCHANGED_IN_LATEST | identical | High |
| S022 | REQ-A:src/resources/strings.h:3-9 | SRC:src/resources/strings.h:3-9 | SAME_NAME | UNCHANGED_IN_LATEST | identical | High |
| S023 | REQ-A:src/resources/strings_en.c:3-8 | SRC:src/resources/strings_en.c:3-8 | SAME_NAME | UNCHANGED_IN_LATEST | identical | High |
| S024 | REQ-A:src/settings/nv_settings.c:1-2 | SRC:src/settings/nv_settings.c:1-2 | SAME_NAME | UNCHANGED_IN_LATEST | identical | High |
| S025 | REQ-A:src/settings/nv_settings.c:11-18 | SRC:src/settings/nv_settings.c:11-18 | SAME_NAME | UNCHANGED_IN_LATEST | identical | High |
| S026 | REQ-A:src/settings/nv_settings.h:5-11 | SRC:src/settings/nv_settings.h:5-11 | SAME_NAME | UNCHANGED_IN_LATEST | identical | High |

## Hunks (all `+` lines checked with `grep -F` in the anchored body)
| id | request location | latest location | anchor result | latest state | evidence | confidence |
|---|---|---|---|---|---|---|
| H001 | REQ-A:Makefile:6 | SRC:Makefile:6 | SAME_PATH | PRESENT | 1/1 lines | High |
| H002 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 | SAME_PATH | PRESENT | 1/1 | High |
| H003 | REQ-A:src/cmd/pjl_commands.c:4 | SRC:…:4 | SAME_PATH | PRESENT | 1/1 | High |
| H004 | REQ-A:src/cmd/pjl_commands.c:27 | SRC:…:27 | SAME_PATH | PRESENT | 1/1 | High |
| H005 | REQ-A:…/toner_save.c:1-40 | SRC:…/toner_save.c:1-42 | SAME_PATH | PRESENT | 40/40 (+2 later lines) | High |
| H006 | REQ-A:…/toner_save.h:1-13 | SRC:…/toner_save.h:1-13 | SAME_PATH | PRESENT | 13/13 | High |
| H007 | REQ-A:src/panel/menu_table.c:4-6,11-13 | SRC:…:4-6,14-16 | SAME_PATH | PRESENT | 6/6 | High |
| H008 | REQ-A:src/print/render.c:3-5,11-13 | SRC:…:3-5,11-13 | SAME_PATH | PRESENT | 6/6 | High |
| H009 | REQ-A:src/resources/strings.h:6 | SRC:…:6 | SAME_PATH | PRESENT | 1/1 | High |
| H010 | REQ-A:src/resources/strings_en.c:6 | SRC:…:6 | SAME_PATH | PRESENT | 1/1 | High |
| H011 | REQ-A:src/settings/nv_settings.c:2 | SRC:…:2 | SAME_PATH | PRESENT | 1/1 | High |
| H012 | REQ-A:src/settings/nv_settings.c:15 | SRC:…:15 | SAME_PATH | PRESENT | 1/1 | High |
| H013 | REQ-A:src/settings/nv_settings.h:8 | SRC:…:8 | SAME_PATH | PRESENT | 1/1 | High |

## Evolution blocks
| S-id | block (SRC lines) | class | R14 signals |
|---|---|---|---|
| S005 | SRC:src/features/toner_save/toner_save.c:7 `#include "../../util/math_util.h"` | BUGFIX | sig3 (adjacent to request L1-6); provides `Clamp` used by the S009 BUGFIX line |
| S009 | SRC:src/features/toner_save/toner_save.c:24 `level = Clamp(level, TONER_SAVE_OFF, TONER_SAVE_HIGH); /* fix #1234 … */` | BUGFIX | sig1 (TONER_SAVE_OFF/HIGH, `level`), sig3 (inside request body), sig4 (`fix #1234` comment); fixes out-of-range NV value |
| S019 | SRC:src/panel/menu_table.c:19-21 `#ifdef SUPPORT_ECO_REPORT` / `{ "ECO_REPORT", EcoReport_MenuHandler },` / `#endif` | UNRELATED | no feature token, not in SUPPORT_TONER_SAVE guard (sig1/2 absent); only positional proximity (3 lines after request L16) – contradicted by another feature's guard `SUPPORT_ECO_REPORT` + tokens `EcoReport_*` |
| F1 (file) | SRC:Makefile:7 `SRCS += src/features/eco_report/eco_report.c` | UNRELATED | eco_report build entry (X1 consumer) |
| F2 (file) | SRC:config/model_a.h:4 `#define SUPPORT_ECO_REPORT 1` | UNRELATED | eco_report enable macro (X1 consumer) |
| F6 (file) | SRC:src/panel/menu_table.c:7-9 ECO include block | UNRELATED | outside S018 range; eco_report tokens/guard (X1 consumer) |

## Extension hits (B4)
Searches run on SRC: `grep -rnI -E 'TonerSave_[A-Za-z0-9_]*|TONER_SAVE[A-Za-z0-9_]*|toner_save[A-Za-z0-9_]*'` (prefix + guard + feature symbols), `grep -rnwI -E 'k_percent|is_valid'`, `grep -rnI -E 'ECONOMODE|Toner Save'`, `grep -rn SUPPORT_TONER_SAVE` (guard blocks: menu_table.c:4,14, render.c:3,11 – all request lines).
| hit (SRC:path:line) | symbol | class | reason |
|---|---|---|---|
| SRC:src/features/eco_report/eco_report.c:2,7 (+ eco_report.h, Makefile:7, model_a.h:4, menu_table.c:7-9,19-21) | X1 EcoReport_Print / EcoReport_MenuHandler | CONSUMER | separate feature: own files, own prefix `EcoReport_`, own guard `SUPPORT_ECO_REPORT`; calls `TonerSave_GetLevel`, `TONER_SAVE_OFF` |
| SRC:src/main.c:11-12 | main (calls Menu_Dispatch("TONER_SAVE"), Pjl_Dispatch("ECONOMODE")) | CONSUMER | application test driver using the feature via dispatchers; not part of feature |
| SRC:src/panel/menu.c:5 | is_valid@src/panel/menu.c | (not a hit) | different static function with same name; unrelated body `key >= 0 && key < 100` |
No `EXTENSION_NEW` symbols found.
