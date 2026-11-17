# Port Request Report

## Run Metadata
| Field | Value |
|---|---|
| SOURCE_ROOT | /Users/trantien/Documents/my-project/port-request-skill/tests/cases/T0-toner-save/input/A_latest |
| TARGET_ROOT | /Users/trantien/Documents/my-project/port-request-skill/tests/cases/T0-toner-save/input/B_latest |
| SOURCE_REQUEST | /Users/trantien/Documents/my-project/port-request-skill/tests/cases/T0-toner-save/input/REQ |
| TARGET_REQUEST_ID | T0-toner-save |
| OUTPUT_PARENT | /Users/trantien/Documents/my-project/port-request-skill/tests/runs/run1/T0-toner-save |
| OUTPUT_ROOT | /Users/trantien/Documents/my-project/port-request-skill/tests/runs/run1/T0-toner-save/formula-source-T0-toner-save |
| REPORT_PATH | /Users/trantien/Documents/my-project/port-request-skill/tests/runs/run1/T0-toner-save/formula-source-T0-toner-save/PORT_REPORT.md |
| Created at (UTC) | 2026-11-12T18:18:50Z |

## Workflow Status
| Checkpoint | Status | Approval to start | Next approval gate |
|---|---|---|---|
| A | Complete | Not required | Awaiting Checkpoint B approval |
| B | Complete | AUTO (APPROVAL_MODE=auto) | Awaiting Checkpoint C approval |
| C | Complete | AUTO (APPROVAL_MODE=auto) | Awaiting Checkpoint D approval |
| D | Complete | AUTO (APPROVAL_MODE=auto) | Awaiting Checkpoint E approval |
| E | Complete | AUTO (APPROVAL_MODE=auto) | Awaiting Checkpoint F approval |
| F | Complete | AUTO (APPROVAL_MODE=auto) | None |

## Checkpoint A - Source Request Snapshot Comparison
### Changed File Manifest
| No | file | file_status | function | function_status | Modified_line_before | Modified_line_after |
|---:|---|---|---|---|---|---|
| 1 | `Makefile` | modified | N/A (non-code file) | unknown | N/A | N/A |
| 2 | `config/model_a.h` | modified | SUPPORT_TONER_SAVE (macro) | added | N/A | L3: `#define SUPPORT_TONER_SAVE 1` |
| 3 | `src/cmd/pjl_commands.c` | modified | pjl_commands.c (file scope) | modified | N/A | L4: `#include "../features/toner_save/toner_save.h"` |
| 4 | `src/cmd/pjl_commands.c` | modified | g_pjl_table (table) | modified | N/A | L27: `    { "ECONOMODE", TonerSave_PjlSet },` |
| 5 | `src/features/toner_save/toner_save.c` | added | toner_save.c (file scope) | added | N/A | L1-L7: `#include <stdlib.h>`<br>`#include "toner_save.h"`<br>… (+5 lines, H005) |
| 6 | `src/features/toner_save/toner_save.c` | added | k_percent (table) | added | N/A | L8-L9: `static const int k_percent[] = { 100, 80, 60 };`<br>`` |
| 7 | `src/features/toner_save/toner_save.c` | added | is_valid (function) | added | N/A | L10-L14: `static int is_valid(int level)`<br>`{`<br>… (+3 lines, H005) |
| 8 | `src/features/toner_save/toner_save.c` | added | TonerSave_GetLevel (function) | added | N/A | L15-L19: `int TonerSave_GetLevel(void)`<br>`{`<br>… (+3 lines, H005) |
| 9 | `src/features/toner_save/toner_save.c` | added | TonerSave_ApplyDensity (function) | added | N/A | L20-L27: `int TonerSave_ApplyDensity(int density)`<br>`{`<br>… (+6 lines, H005) |
| 10 | `src/features/toner_save/toner_save.c` | added | TonerSave_MenuHandler (function) | added | N/A | L28-L36: `int TonerSave_MenuHandler(int key)`<br>`{`<br>… (+7 lines, H005) |
| 11 | `src/features/toner_save/toner_save.c` | added | TonerSave_PjlSet (function) | added | N/A | L37-L40: `int TonerSave_PjlSet(const char *arg)`<br>`{`<br>… (+2 lines, H005) |
| 12 | `src/features/toner_save/toner_save.h` | added | TONER_SAVE_H (preprocessor) | added | N/A | L1-L2: `#ifndef TONER_SAVE_H`<br>`#define TONER_SAVE_H` |
| 13 | `src/features/toner_save/toner_save.h` | added | TONER_SAVE_OFF..TONER_SAVE_HIGH (enum) | added | N/A | L3-L8: `enum {`<br>`    TONER_SAVE_OFF = 0,`<br>… (+4 lines, H006) |
| 14 | `src/features/toner_save/toner_save.h` | added | TonerSave_GetLevel (prototype) | added | N/A | L9: `int TonerSave_GetLevel(void);` |
| 15 | `src/features/toner_save/toner_save.h` | added | TonerSave_ApplyDensity (prototype) | added | N/A | L10: `int TonerSave_ApplyDensity(int density);` |
| 16 | `src/features/toner_save/toner_save.h` | added | TonerSave_MenuHandler (prototype) | added | N/A | L11: `int TonerSave_MenuHandler(int key);` |
| 17 | `src/features/toner_save/toner_save.h` | added | TonerSave_PjlSet (prototype) | added | N/A | L12: `int TonerSave_PjlSet(const char *arg);` |
| 18 | `src/features/toner_save/toner_save.h` | added | TONER_SAVE_H (preprocessor) | added | N/A | L13: `#endif` |
| 19 | `src/panel/menu_table.c` | modified | SUPPORT_TONER_SAVE (preprocessor) | added | N/A | L4-L6: `#ifdef SUPPORT_TONER_SAVE`<br>`#include "../features/toner_save/toner_save.h"`<br>`#endif` |
| 20 | `src/panel/menu_table.c` | modified | g_menu_table (table) | modified | N/A | L11-L13: `#ifdef SUPPORT_TONER_SAVE`<br>`    { "TONER_SAVE", TonerSave_MenuHandler },`<br>`#endif` |
| 21 | `src/print/render.c` | modified | SUPPORT_TONER_SAVE (preprocessor) | added | N/A | L3-L5: `#ifdef SUPPORT_TONER_SAVE`<br>`#include "../features/toner_save/toner_save.h"`<br>`#endif` |
| 22 | `src/print/render.c` | modified | Render_Page (function) | modified | N/A | L11-L13: `#ifdef SUPPORT_TONER_SAVE`<br>`    density = TonerSave_ApplyDensity(density);`<br>`#endif` |
| 23 | `src/resources/strings.h` | modified | StrId_t (enum) | modified | N/A | L6: `    STR_TONER_SAVE,` |
| 24 | `src/resources/strings_en.c` | modified | g_strings_en (table) | modified | N/A | L6: `    [STR_TONER_SAVE] = "Toner Save",` |
| 25 | `src/settings/nv_settings.c` | modified | nv_settings.c (file scope) | modified | N/A | L2: `#include "../features/toner_save/toner_save.h"` |
| 26 | `src/settings/nv_settings.c` | modified | NV_LoadDefaults (function) | modified | N/A | L15: `    g_settings.toner_save_level = TONER_SAVE_OFF;` |
| 27 | `src/settings/nv_settings.h` | modified | NvSettings_t (struct) | modified | N/A | L8: `    int toner_save_level;` |
### Line-Level Changes
#### `config/model_a.h`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H002 |  | L3: `#define SUPPORT_TONER_SAVE 1` |

#### `src/cmd/pjl_commands.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H003 |  | L4: `#include "../features/toner_save/toner_save.h"` |
| H004 |  | L27: `    { "ECONOMODE", TonerSave_PjlSet },` |

#### `src/features/toner_save/toner_save.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H005 |  | L1: `#include <stdlib.h>` |
| H005 |  | L2: `#include "toner_save.h"` |
| H005 |  | L3: `#include "../../settings/nv_settings.h"` |
| H005 |  | L4: `#include "../../print/density.h"` |
| H005 |  | L5: `#include "../../core/log.h"` |
| H005 |  | L6: `#include "../../resources/strings.h"` |
| H005 |  | L7: `` |
| H005 |  | L8: `static const int k_percent[] = { 100, 80, 60 };` |
| H005 |  | L9: `` |
| H005 |  | L10: `static int is_valid(int level)` |
| H005 |  | L11: `{` |
| H005 |  | L12: `    return level >= TONER_SAVE_OFF && level <= TONER_SAVE_HIGH;` |
| H005 |  | L13: `}` |
| H005 |  | L14: `` |
| H005 |  | L15: `int TonerSave_GetLevel(void)` |
| H005 |  | L16: `{` |
| H005 |  | L17: `    return NV_GetSettings()->toner_save_level;` |
| H005 |  | L18: `}` |
| H005 |  | L19: `` |
| H005 |  | L20: `int TonerSave_ApplyDensity(int density)` |
| H005 |  | L21: `{` |
| H005 |  | L22: `    int level = TonerSave_GetLevel();` |
| H005 |  | L23: `    if (!is_valid(level))` |
| H005 |  | L24: `        return density;` |
| H005 |  | L25: `    return Density_Scale(density, k_percent[level]);` |
| H005 |  | L26: `}` |
| H005 |  | L27: `` |
| H005 |  | L28: `int TonerSave_MenuHandler(int key)` |
| H005 |  | L29: `{` |
| H005 |  | L30: `    if (!is_valid(key))` |
| H005 |  | L31: `        return -1;` |
| H005 |  | L32: `    NV_GetSettings()->toner_save_level = key;` |
| H005 |  | L33: `    Log_Info(Str_Get(STR_TONER_SAVE));` |
| H005 |  | L34: `    return key;` |
| H005 |  | L35: `}` |
| H005 |  | L36: `` |
| H005 |  | L37: `int TonerSave_PjlSet(const char *arg)` |
| H005 |  | L38: `{` |
| H005 |  | L39: `    return TonerSave_MenuHandler(atoi(arg));` |
| H005 |  | L40: `}` |

#### `src/features/toner_save/toner_save.h`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H006 |  | L1: `#ifndef TONER_SAVE_H` |
| H006 |  | L2: `#define TONER_SAVE_H` |
| H006 |  | L3: `enum {` |
| H006 |  | L4: `    TONER_SAVE_OFF = 0,` |
| H006 |  | L5: `    TONER_SAVE_LOW = 1,` |
| H006 |  | L6: `    TONER_SAVE_HIGH = 2` |
| H006 |  | L7: `};` |
| H006 |  | L8: `` |
| H006 |  | L9: `int TonerSave_GetLevel(void);` |
| H006 |  | L10: `int TonerSave_ApplyDensity(int density);` |
| H006 |  | L11: `int TonerSave_MenuHandler(int key);` |
| H006 |  | L12: `int TonerSave_PjlSet(const char *arg);` |
| H006 |  | L13: `#endif` |

#### `src/panel/menu_table.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H007 |  | L4: `#ifdef SUPPORT_TONER_SAVE` |
| H007 |  | L5: `#include "../features/toner_save/toner_save.h"` |
| H007 |  | L6: `#endif` |
| H007 |  | L11: `#ifdef SUPPORT_TONER_SAVE` |
| H007 |  | L12: `    { "TONER_SAVE", TonerSave_MenuHandler },` |
| H007 |  | L13: `#endif` |

#### `src/print/render.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H008 |  | L3: `#ifdef SUPPORT_TONER_SAVE` |
| H008 |  | L4: `#include "../features/toner_save/toner_save.h"` |
| H008 |  | L5: `#endif` |
| H008 |  | L11: `#ifdef SUPPORT_TONER_SAVE` |
| H008 |  | L12: `    density = TonerSave_ApplyDensity(density);` |
| H008 |  | L13: `#endif` |

#### `src/resources/strings.h`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H009 |  | L6: `    STR_TONER_SAVE,` |

#### `src/resources/strings_en.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H010 |  | L6: `    [STR_TONER_SAVE] = "Toner Save",` |

#### `src/settings/nv_settings.c`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H011 |  | L2: `#include "../features/toner_save/toner_save.h"` |
| H012 |  | L15: `    g_settings.toner_save_level = TONER_SAVE_OFF;` |

#### `src/settings/nv_settings.h`
| H-id | Modified_Before (-) | Modified_After (+) |
|---|---|---|
| H013 |  | L8: `    int toner_save_level;` |
### Gate Result
PASS – File count – `_work/A_files.txt` 11 files (no exclusions; `Only in After/src: features` expanded to 2 files) == 11 distinct manifest files
PASS – Diff files – 11/11 `diffs/source/<path>.diff` non-empty
PASS – Hunk count – `grep -c '^@@'` over diffs/source = 13 == 13 H-ids (H001–H013) in `_work/A_hunks.md`
PASS – Hunk coverage – every H-id has ≥1 manifest row; 26 code rows all trace to H002–H013, row 1 (Makefile) to H001
PASS – Point coverage – sum of point lines −0/+74 == `git diff --no-index --numstat` totals 0 deleted / 74 added
PASS – Vocabulary – file_status ∈ {added, modified}; function_status ∈ {added, modified, unknown}; functions use `<name> (<kind>)` / `N/A (non-code file)`
PASS – Consistency – all rows pure additions → `Modified_line_before = N/A`; no deleted files; Makefile row = `N/A (non-code file) \| unknown \| N/A \| N/A`
PASS – Not identified – none
PASS – Template – manifest header identical to template; rows 1..27 without gaps
PASS – Line-Level Changes – 10 subsections (one per changed code file; Makefile non-code); only `+` lines, blank `-` cells
PASS – Inputs untouched – `find "$SOURCE_REQUEST" -newer .start_marker -type f` → 0 files
PASS – Status row – A = Complete, Next approval gate = `Awaiting Checkpoint B approval`
Notes: tools OK: diff grep awk sed find rsync shasum file iconv git (none missing). All files us-ascii, LF. Naming choices: `<file> (file scope)` for include lines; anonymous enum named `TONER_SAVE_OFF..TONER_SAVE_HIGH (enum)`; blank separator lines assigned to the preceding point.

## Checkpoint B - Source Change Analysis
### Files Analyzed
| file | result |
|---|---|
| `Makefile` | analyzed |
| `config/model_a.h` | analyzed |
| `src/cmd/pjl_commands.c` | analyzed |
| `src/features/toner_save/toner_save.c` | analyzed |
| `src/features/toner_save/toner_save.h` | analyzed |
| `src/panel/menu_table.c` | analyzed |
| `src/print/render.c` | analyzed |
| `src/resources/strings.h` | analyzed |
| `src/resources/strings_en.c` | analyzed |
| `src/settings/nv_settings.c` | analyzed |
| `src/settings/nv_settings.h` | analyzed |
### Latest Source Anchoring
| H/S-id | request location | latest location | anchor result | latest state | evidence | confidence |
|---|---|---|---|---|---|---|
| Files F1–F11 | REQ-A:<same path> | SRC:<same path> | SAME_PATH (11/11) | EVOLVED: Makefile, model_a.h, toner_save.c, menu_table.c; others UNCHANGED_IN_LATEST | `diff -u REQ-A SRC` per file | High |
| S001–S004, S006–S008, S010–S018, S020–S026 | REQ-A (see `_work/B_anchor.md`) | SRC same lines (toner_save.c +1/+2 shift) | SAME_NAME | UNCHANGED_IN_LATEST | R7 SAME | High |
| S005 | REQ-A:src/features/toner_save/toner_save.c:1-7 | SRC:src/features/toner_save/toner_save.c:1-8 | SAME_NAME | EVOLVED | +L7 include math_util.h (BUGFIX) | High |
| S009 | REQ-A:src/features/toner_save/toner_save.c:20-26 | SRC:src/features/toner_save/toner_save.c:21-28 | SAME_NAME | EVOLVED | +L24 `Clamp(...)` `/* fix #1234 */` (BUGFIX) | High |
| S019 | REQ-A:src/panel/menu_table.c:8-16 | SRC:src/panel/menu_table.c:11-22 | SAME_NAME | EVOLVED | +L19-21 ECO_REPORT entry (UNRELATED) | High |
| H001–H013 | REQ-A | SRC | SAME_PATH | PRESENT (13/13) | all `+` lines found with `grep -F` | High |
Alias map: no renames/moves (`_work/alias_map.md`).
### Changed Symbols and Behavior
| S-id | symbol (kind) | H-ids / ext | change type | behavior before → after | later evolution |
|---|---|---|---|---|---|
| S001 | SRCS entry (Makefile) | H001 | registration | + build of toner_save.c | file: +eco_report.c line (UNRELATED) |
| S002 | SUPPORT_TONER_SAVE (macro) | H002 | new | undefined → `1` for model A | file: +SUPPORT_ECO_REPORT (UNRELATED) |
| S003 | pjl_commands.c (file scope) | H003 | new | + include toner_save.h | none |
| S004 | g_pjl_table (table) | H004 | registration | + `ECONOMODE` → TonerSave_PjlSet | none |
| S005 | toner_save.c (file scope) | H005 | new | includes for new file | BUGFIX: + math_util.h (SRC L7) |
| S006 | k_percent (table) | H005 | new | `{100,80,60}` % per level | none |
| S007 | is_valid@src/features/toner_save/toner_save.c (function) | H005 | new | valid iff 0 ≤ level ≤ 2 | none |
| S008 | TonerSave_GetLevel (function) | H005 | new | returns NV toner_save_level | none |
| S009 | TonerSave_ApplyDensity (function) | H005 | new | valid level → `Density_Scale(density, k_percent[level])`, else density | BUGFIX: level clamped 0..2 (SRC L24) |
| S010 | TonerSave_MenuHandler (function) | H005 | new | key ∉0..2 → -1; else store in NV, log "Toner Save", return key | none |
| S011 | TonerSave_PjlSet (function) | H005 | new | `MenuHandler(atoi(arg))` | none |
| S012 | TONER_SAVE_H (preprocessor) | H006 | new | include guard | none |
| S013 | TONER_SAVE_OFF..TONER_SAVE_HIGH (enum) | H006 | new | OFF=0, LOW=1, HIGH=2 | none |
| S014–S017 | TonerSave_* (prototype) ×4 | H006 | new | 4 prototypes | none |
| S018 | SUPPORT_TONER_SAVE (preprocessor) @menu_table.c | H007 | guard | guarded include | none (ECO block L7-9 is separate, UNRELATED) |
| S019 | g_menu_table (table) | H007 | registration | + `TONER_SAVE` → TonerSave_MenuHandler after DUPLEX, guarded | UNRELATED: ECO_REPORT entry SRC L19-21 → partial take |
| S020 | SUPPORT_TONER_SAVE (preprocessor) @render.c | H008 | guard | guarded include | none |
| S021 | Render_Page (function) | H008 | logic | density unchanged → `TonerSave_ApplyDensity(density)` (guarded) | none |
| S022 | StrId_t (enum) | H009 | layout | + STR_TONER_SAVE=2; STR_QUALITY 2→3, STR_COUNT 3→4 | none |
| S023 | g_strings_en (table) | H010 | constant | + `"Toner Save"` | none |
| S024 | nv_settings.c (file scope) | H011 | new | + include toner_save.h | none |
| S025 | NV_LoadDefaults (function) | H012 | logic | + default toner_save_level = OFF (0) | none |
| S026 | NvSettings_t (struct) | H013 | layout | + `int toner_save_level` after duplex; language offset 8→12, quality 12→16 | none |
### Dependencies and Test Coverage
- Outgoing code deps: S008.d1 NV_GetSettings `SRC:src/settings/nv_settings.c:6`; S009.d1 Density_Scale `SRC:src/print/density.c:4`; S009.d2 DENSITY_MAX `SRC:src/print/density.h:3`; S009.d3 Clamp `SRC:src/util/math_util.c:3`; S010.d1 Log_Info `SRC:src/core/log.c:4` (infrastructure, stop); S010.d2 Str_Get `SRC:src/resources/strings_en.c:10`; S011.d1 atoi (libc); S018.d1 model_config.h `SRC:config/model_config.h:3-6`; S019.d1 MenuEntry_t `SRC:src/panel/menu.h:4`; S004.d1 PjlEntry_t `SRC:src/cmd/pjl_commands.c:7`. Depth 2.
- Data deps: string STR_TONER_SAVE (strings.h:6, strings_en.c:6; only one language table); enum StrId_t sizes `g_strings_en[STR_COUNT]` (designated init); NVRAM field toner_save_level + default (no version/CRC found); registry entries menu `TONER_SAVE`, PJL `ECONOMODE`; config SUPPORT_TONER_SAVE in model_a.h; build entry Makefile:6.
- Incoming: g_menu_table/Menu_Dispatch, g_pjl_table/Pjl_Dispatch, Render_Page (all in request). CONSUMERS (report only): eco_report feature (`SRC:src/features/eco_report/eco_report.c:7`), `SRC:src/main.c:11-13`.
- Guards: SUPPORT_TONER_SAVE (S018–S021), enabled `SRC:config/model_a.h:3`. Tokens: `_work/B_new_tokens.txt` (21 project, 4 local, 5 path, 14 std).
- Tests: none found (patterns in `_work/B_symbols.md` §4).
- B4 searches: prefix `TonerSave_|TONER_SAVE|toner_save`, guard `SUPPORT_TONER_SAVE`, `k_percent|is_valid`, literals `ECONOMODE|Toner Save` → 0 EXTENSION_NEW, 1 CONSUMER feature (eco_report) + main.c.
### Blockers and Context Risk
- Blockers: none (no NOT_FOUND / REMOVED / GONE / PARTIAL / Low / UNCLEAR).
- Partial take: S019 excludes `SRC:src/panel/menu_table.c:19-21`; file-level UNRELATED lines also excluded: Makefile:7, model_a.h:4, menu_table.c:7-9 (eco_report).
- R14 judgment: ECO blocks are within ±3 lines of request lines (signal 3) but carry another feature's guard/tokens → classified UNRELATED, not UNCLEAR.
- Layout risk: S022 (STR_QUALITY value shift), S026 (NVRAM struct offsets shift, no version/CRC).
- Unguarded feature includes/entries in pjl_commands.c and nv_settings.c (feature always compiled there).
### Gate Result
PASS – Files – 11/11 manifest files listed as analyzed
PASS – Symbol coverage – H001–H013 each in ≥1 S-id (S001–S026); every S lists H-ids; no ext
PASS – Behavior – 26/26 S-ids have concrete before → after
PASS – Anchoring complete – files 11/11, S 26/26, H 13/13 in `_work/B_anchor.md`
PASS – Relocation evidence – 0 MOVED/RENAMED/SPLIT/MERGED; alias_map records none
PASS – No silent loss – 0 NOT_FOUND/REMOVED/GONE/PARTIAL/Low
PASS – Evolution – 3 EVOLVED symbols: 2 BUGFIX blocks, 1 UNRELATED block (+3 file-level UNRELATED); 0 UNCLEAR; partial take S019 listed
PASS – Extensions searched – 4 pattern searches recorded; hits: eco_report CONSUMER, main.c CONSUMER, 0 EXTENSION_NEW
PASS – Tokens – `_work/B_new_tokens.txt`: 21 project tokens all S-id/dependency; 4 locals, 5 path fragments, 14 std/keywords
PASS – Code dependency evidence – 10 outgoing deps with SRC:path:line; depth 2, stop = infrastructure/libc
PASS – Data dependencies – string ID, enum, settings field, registry, config, build, data files checked (findings/none)
PASS – Incoming / guards / headers / tests – recorded; tests none found (command listed)
PASS – Read-only – `find SOURCE_ROOT SOURCE_REQUEST -newer .start_marker` → 0
PASS – Status row – B = Complete, Next = Awaiting Checkpoint C approval

## Checkpoint C - Source/Target Flow Trace
### Source Behavior
- FLOW-1 (density reduction): `SRC:src/main.c:13` → `SRC:src/print/render.c:12` Render_Page → `SRC:src/features/toner_save/toner_save.c:21` TonerSave_ApplyDensity → `:16` GetLevel → `SRC:src/settings/nv_settings.c:6` → `:24` Clamp → `:11` is_valid → `SRC:src/print/density.c:4` Density_Scale
- FLOW-2 (panel menu): `SRC:src/main.c:11` → `SRC:src/panel/menu_table.c:24` Menu_Dispatch → `:15` entry → `toner_save.c:30` TonerSave_MenuHandler → NV field, Log_Info(Str_Get(STR_TONER_SAVE))
- FLOW-3 (PJL ECONOMODE): `SRC:src/main.c:12` → `SRC:src/cmd/pjl_commands.c:30` → `:27` entry → `toner_save.c:39` TonerSave_PjlSet → MenuHandler
- FLOW-4 (defaults): `SRC:src/main.c:9` → `SRC:src/settings/nv_settings.c:15` → `SRC:src/settings/nv_settings.h:8`
### Target Behavior
- FLOW-1 target: `TGT:src/main.c:13` → `TGT:src/print/render.c:5` → MISSING at TonerSave_ApplyDensity (guard not enabled)
- FLOW-2 target: `TGT:src/main.c:11` → `TGT:src/panel/menu_table.c:13` → MISSING at g_menu_table entry
- FLOW-3 target: `TGT:src/main.c:12` → `TGT:src/cmd/pjl_commands.c:29` → MISSING at g_pjl_table entry
- FLOW-4 target: `TGT:src/main.c:9` → `TGT:src/settings/nv_settings.c:10` → MISSING at toner_save_level

| id | item | target location | target state | confidence |
|---|---|---|---|---|
| S001 | Makefile toner_save.c entry | `TGT:Makefile:1-5` | MISSING | High |
| S002 | SUPPORT_TONER_SAVE (macro) | `TGT:config/model_b.h` (alias of model_a.h) | MISSING | High |
| S003, S004 | pjl include, g_pjl_table | `TGT:src/cmd/pjl_commands.c:1-3, 23-26` | SAME_AS_BEFORE | High |
| S005–S017 | toner_save.c / toner_save.h contents | – | MISSING | High |
| S018 | menu_table include block | `TGT:src/panel/menu_table.c:1-3` | SAME_AS_BEFORE | High |
| S019 | g_menu_table | `TGT:src/panel/menu_table.c:5-11` | DIVERGED | High |
| S020 | render include block | `TGT:src/print/render.c:1-3` | SAME_AS_BEFORE | High |
| S021 | Render_Page | `TGT:src/print/render.c:5-13` | DIVERGED | High |
| S022 | StrId_t | `TGT:src/resources/strings.h:3-9` | DIVERGED | High |
| S023 | g_strings_en | `TGT:src/resources/strings_en.c:3-8` | DIVERGED | High |
| S024 | nv_settings.c include | `TGT:src/settings/nv_settings.c:1` | SAME_AS_BEFORE | High |
| S025 | NV_LoadDefaults | `TGT:src/settings/nv_settings.c:10-17` | DIVERGED | High |
| S026 | NvSettings_t | `TGT:src/settings/nv_settings.h:5-11` | DIVERGED | High |
| S008.d1, S010.d1, S010.d2, S011.d1, S018.d1, S019.d1, S004.d1 | NV_GetSettings, Log_Info, Str_Get, atoi, model_config.h, MenuEntry_t, PjlEntry_t | TGT same files | SAME_AS_SOURCE | High |
| S009.d1, S009.d2, S009.d4 | Density_Scale, DENSITY_MAX, density.h | – | MISSING | High |
| S009.d3 | Clamp | `TGT:src/util/math_util.c:3`, `TGT:src/util/math_util.h:3` | SIGNATURE_DIFF | High |
| S009.d5 | Makefile density.c entry | `TGT:Makefile:2` | MISSING | High |
### Gaps, Evidence, and Confidence
- DIVERGED (target-only lines to keep): S019 `TGT:src/panel/menu_table.c:10` FAX entry; S021 `TGT:src/print/render.c:9-11` SUPPORT_FAX block; S022 `TGT:src/resources/strings.h:7` STR_FAX; S023 `TGT:src/resources/strings_en.c:7`; S025 `TGT:src/settings/nv_settings.c:16`; S026 `TGT:src/settings/nv_settings.h:10` fax_resolution. Callers in `_work/C_trace.md`.
- SIGNATURE_DIFF: Clamp `int Clamp(int v, int hi)` (TGT) vs `int Clamp(int v, int lo, int hi)` (SRC); target callers: none.
- Missing infrastructure: `src/print/density.{c,h}` (Density_Scale, DENSITY_MAX) and Makefile entry; target `Menu_Quality` no longer uses Density_Scale (`TGT:src/panel/menu.c:19-23`).
- Alias map: file `config/model_a.h` → `config/model_b.h` (Medium: include-slot anchor in model_config.h + Makefile MODEL B + MODEL_NAME/SUPPORT_DUPLEX similarity). No symbol renames.
- Data gaps: STR_TONER_SAVE (enum + en table), NV field + default (no version/CRC in target), menu entry, PJL entry, config macro, build entries (toner_save.c, density.c).
- Guard gap: SUPPORT_TONER_SAVE not enabled in `TGT:config/model_b.h` (siblings SUPPORT_DUPLEX, SUPPORT_FAX defined there).
- Closure: iteration 1 +2 (density.h, density.c build entry), iteration 2 +0 → fixpoint.
### Blockers
None (no Low / RENAMED_CANDIDATE / unresolved items).
### Gate Result
PASS – Coverage – B: 26 S + 10 deps = 36; C_trace: 26 S (S014–S017 in one row) + 12 deps (10 + 2 closure) rows
PASS – State vocabulary – only SAME_AS_SOURCE/SAME_AS_BEFORE/DIVERGED/SIGNATURE_DIFF/MISSING used
PASS – Evidence – non-MISSING rows cite TGT:path:line; MISSING rows list R2/R11/R12/R8 searches
PASS – Comparison done – SAME_AS_* from R7 `diff -w` vs REQ-B / port version
PASS – Target renames – 0 symbol renames; file alias model_a.h→model_b.h Medium (R11 signals) in alias_map
PASS – Callers – 7 DIVERGED/SIGNATURE_DIFF rows list target callers (Clamp: none)
PASS – Data gaps – per-place status table in `_work/C_trace.md` (enum, en table, NV field, default, version/CRC none, registries, config, build)
PASS – Fixpoint reached – iteration 2 added 0
PASS – Flows – FLOW-1..4 source + target chains with break points
PASS – No assumed equivalence – 0 Low / RENAMED_CANDIDATE
PASS – Read-only + status row – marker check on SOURCE_ROOT/TARGET_ROOT/SOURCE_REQUEST → 0 files; C = Complete

## Checkpoint D - Formula Mapping and Plan
### Formula Mapping Matrix
| M-id | Formula (source behavior) | S-ids / H-ids | Request location | Latest source location | Target location | Target state | Port class | P-ids | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| M001 | build toner_save.c | S001 / H001 | REQ-A:Makefile:6 | SRC:Makefile:6 | TGT:Makefile:5 | MISSING | COPY_NEW (row 7) | P020 | High |
| M002 | enable feature for model (guard) | S002 / H002 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 | TGT:config/model_b.h:3 | MISSING | COPY_NEW (row 7); also row 11 ENABLE_GUARD → AUTO-DECIDED add | P007 | High |
| M003 | PJL include | S003 / H003 | REQ-A:src/cmd/pjl_commands.c:4 | SRC:src/cmd/pjl_commands.c:4 | TGT:src/cmd/pjl_commands.c:3 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P017 | High |
| M004 | PJL ECONOMODE registration | S004 / H004 | REQ-A:src/cmd/pjl_commands.c:27 | SRC:src/cmd/pjl_commands.c:27 | TGT:src/cmd/pjl_commands.c:23-26 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P018 | High |
| M005 | toner save logic (levels, density scaling, menu/PJL handlers, BUGFIX clamp) | S005–S011 / H005 | REQ-A:src/features/toner_save/toner_save.c:1-40 | SRC:src/features/toner_save/toner_save.c:1-42 | – | MISSING | COPY_NEW (row 7) | P006 | High |
| M006 | toner save API/enum | S012–S017 / H006 | REQ-A:src/features/toner_save/toner_save.h:1-13 | SRC:src/features/toner_save/toner_save.h:1-13 | – | MISSING | COPY_NEW (row 7) | P005 | High |
| M007 | menu include | S018 / H007 | REQ-A:src/panel/menu_table.c:4-6 | SRC:src/panel/menu_table.c:4-6 | TGT:src/panel/menu_table.c:3 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P015 | High |
| M008 | menu TONER_SAVE registration | S019 / H007 | REQ-A:src/panel/menu_table.c:11-13 | SRC:src/panel/menu_table.c:14-16 | TGT:src/panel/menu_table.c:5-11 | DIVERGED | TAKE_LATEST_PARTIAL (row 5) AUTO-DECIDED: exclude SRC:19-21; merge keeps TGT:10 FAX | P016 | High |
| M009 | render include | S020 / H008 | REQ-A:src/print/render.c:3-5 | SRC:src/print/render.c:3-5 | TGT:src/print/render.c:2 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P013 | High |
| M010 | apply toner save to page density | S021 / H008 | REQ-A:src/print/render.c:11-13 | SRC:src/print/render.c:11-13 | TGT:src/print/render.c:5-13 | DIVERGED | ADAPT_MERGE (row 12) | P014 | High |
| M011 | string ID STR_TONER_SAVE | S022 / H009 | REQ-A:src/resources/strings.h:6 | SRC:src/resources/strings.h:6 | TGT:src/resources/strings.h:3-9 | DIVERGED | ADAPT_MERGE (row 12); row 15 LAYOUT_RISK AUTO-DECIDED: port + HIGH risk | P008 | High |
| M012 | English text "Toner Save" | S023 / H010 | REQ-A:src/resources/strings_en.c:6 | SRC:src/resources/strings_en.c:6 | TGT:src/resources/strings_en.c:3-8 | DIVERGED | ADAPT_MERGE (row 12) | P009 | High |
| M013 | NV settings include | S024 / H011 | REQ-A:src/settings/nv_settings.c:2 | SRC:src/settings/nv_settings.c:2 | TGT:src/settings/nv_settings.c:1 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P011 | High |
| M014 | default level OFF | S025 / H012 | REQ-A:src/settings/nv_settings.c:15 | SRC:src/settings/nv_settings.c:15 | TGT:src/settings/nv_settings.c:10-17 | DIVERGED | ADAPT_MERGE (row 12) | P012 | High |
| M015 | NVRAM field toner_save_level | S026 / H013 | REQ-A:src/settings/nv_settings.h:8 | SRC:src/settings/nv_settings.h:8 | TGT:src/settings/nv_settings.h:5-11 | DIVERGED | ADAPT_MERGE (row 12); row 15 LAYOUT_RISK AUTO-DECIDED: port + HIGH risk | P010 | High |
| M016 | existing infrastructure | S008.d1, S010.d1, S010.d2, S011.d1, S018.d1, S019.d1, S004.d1 | – | SRC (see C_trace) | TGT same | SAME_AS_SOURCE | SKIP_ALREADY_PRESENT (row 4) | – | High |
| M017 | Density_Scale | S009.d1 | – | SRC:src/print/density.c:1-7 | – | MISSING | COPY_DEPENDENCY (row 8) | P002 | High |
| M018 | DENSITY_MAX + density.h | S009.d2, S009.d4 | – | SRC:src/print/density.h:1-5 | – | MISSING | COPY_DEPENDENCY (row 8) | P001 | High |
| M019 | Clamp 3-arg (used by BUGFIX line and Density_Scale) | S009.d3 | – | SRC:src/util/math_util.c:3-8, SRC:src/util/math_util.h:3 | TGT:src/util/math_util.c:3-8, TGT:src/util/math_util.h:3 | SIGNATURE_DIFF (no target callers) | REPLACE (row 14) | P003, P004 | High |
| M020 | build density.c | S009.d5 | – | SRC:Makefile:2 | TGT:Makefile:2 | MISSING | ADD_DATA (row 9, build entry) | P019 | High |
| M021 | eco_report feature, main.c driver | B4 hits X1, main.c | – | SRC:src/features/eco_report/*, SRC:src/main.c:11-13 | – | n/a | REPORT_ONLY (row 16) | – | High |
### Target Request-Label Convention
None found (searched: R10 `(REQ|CR|PR|ECR|ECO|TICKET|ISSUE|BUG|FIX|MOD|CHG)[-_#: ]?[0-9]{2,}` on TARGET_ROOT → 0 hits). No labels will be added.
### Planned Changes
| P-id | Target file | Action | Anchor (exact target text or line) | Content source | Adaptation | Label |
|---|---|---|---|---|---|---|
| P001 | src/print/density.h | add-file | – | SRC:src/print/density.h:1-5 | none | none |
| P002 | src/print/density.c | add-file | – | SRC:src/print/density.c:1-7 | none | none |
| P003 | src/util/math_util.h | replace | TGT:src/util/math_util.h:3 `int Clamp(int v, int hi);` | SRC:src/util/math_util.h:3 | none | none |
| P004 | src/util/math_util.c | replace | TGT:src/util/math_util.c:3-8 `int Clamp(int v, int hi)` … `}` | SRC:src/util/math_util.c:3-8 | none | none |
| P005 | src/features/toner_save/toner_save.h | add-file | – | SRC:src/features/toner_save/toner_save.h:1-13 | none | none |
| P006 | src/features/toner_save/toner_save.c | add-file | – | SRC:src/features/toner_save/toner_save.c:1-42 | none | none |
| P007 | config/model_b.h | add-define | after TGT:config/model_b.h:3 `#define SUPPORT_FAX 1` | SRC:config/model_a.h:3 | file alias model_a.h→model_b.h (append at end as in source) | none |
| P008 | src/resources/strings.h | insert | after TGT:src/resources/strings.h:5 `    STR_DUPLEX,` | SRC:src/resources/strings.h:6 | none (3-way merge keeps STR_FAX) | none |
| P009 | src/resources/strings_en.c | insert | after TGT:src/resources/strings_en.c:5 `    [STR_DUPLEX] = "2-Sided",` | SRC:src/resources/strings_en.c:6 | none | none |
| P010 | src/settings/nv_settings.h | insert | after TGT:src/settings/nv_settings.h:7 `    int duplex;` | SRC:src/settings/nv_settings.h:8 | none (keeps fax_resolution) | none |
| P011 | src/settings/nv_settings.c | add-include | after TGT:src/settings/nv_settings.c:1 `#include "nv_settings.h"` | SRC:src/settings/nv_settings.c:2 | none | none |
| P012 | src/settings/nv_settings.c | insert | after TGT:src/settings/nv_settings.c:13 `    g_settings.duplex = 0;` | SRC:src/settings/nv_settings.c:15 | none | none |
| P013 | src/print/render.c | add-include | after TGT:src/print/render.c:2 `#include "../../config/model_config.h"` | SRC:src/print/render.c:3-5 | none | none |
| P014 | src/print/render.c | insert | after TGT:src/print/render.c:7 `    Log_Info("render start");` | SRC:src/print/render.c:11-13 | none (keeps SUPPORT_FAX block) | none |
| P015 | src/panel/menu_table.c | add-include | after TGT:src/panel/menu_table.c:3 `#include "../../config/model_config.h"` | SRC:src/panel/menu_table.c:4-6 | partial: SRC:7-9 (ECO include) excluded | none |
| P016 | src/panel/menu_table.c | add-registration | after TGT:src/panel/menu_table.c:7 `    { "DUPLEX",   Menu_Duplex },` | SRC:src/panel/menu_table.c:14-16 | partial: SRC:19-21 (ECO entry) excluded | none |
| P017 | src/cmd/pjl_commands.c | add-include | after TGT:src/cmd/pjl_commands.c:3 `#include "../core/log.h"` | SRC:src/cmd/pjl_commands.c:4 | none | none |
| P018 | src/cmd/pjl_commands.c | add-registration | after TGT:src/cmd/pjl_commands.c:25 `    { "DUPLEX", Pjl_SetDuplex },` | SRC:src/cmd/pjl_commands.c:27 | none | none |
| P019 | Makefile | add-to-build | replace TGT:Makefile:2 `SRCS = src/main.c src/core/log.c src/util/math_util.c \` | SRC:Makefile:2 | none (line becomes identical to SRC:Makefile:2) | none |
| P020 | Makefile | add-to-build | after TGT:Makefile:5 `       src/cmd/pjl_commands.c src/resources/strings_en.c` | SRC:Makefile:6 | none; SRC:Makefile:7 (eco_report) excluded | none |

Full new text per P-id: `_work/D_plan.md`. Order: headers/types/macros (P001–P010) before users (P011–P020).
### Validation Plan
- Snapshot scope: full `TARGET_ROOT` copy (19 files, no `.git`/build outputs) into `OUTPUT_ROOT/Before` and `OUTPUT_ROOT/After`; neither exists yet (nothing replaced).
- Build: `make -s MODEL=B` (BUILD_CMD) in `OUTPUT_ROOT/Before` (baseline) and `OUTPUT_ROOT/After`; expect exit 0 and no new `-Wall` warnings; run `./printer_B` in both (main.c prints toner_save / pjl / density results).
- Fallback: `cc -fsyntax-only -Wall -DMODEL_B <SRCS from Makefile>`.
- Diff: `diff -ruN Before After > diffs/output.diff`; every output hunk must trace to a P-id.
### Risks
- HIGH (LAYOUT_RISK, AUTO-DECIDED): M015 inserts `toner_save_level` after `duplex` in NVRAM struct `NvSettings_t` → offsets of `language`, `quality`, `fax_resolution` shift by 4 bytes; no NV version/CRC exists in target to detect old data.
- HIGH (LAYOUT_RISK, AUTO-DECIDED): M011 inserts `STR_TONER_SAVE` after `STR_DUPLEX` → `STR_QUALITY` 2→3, `STR_FAX` 3→4, `STR_COUNT` 4→5 (table uses designated initializers, so in-tree OK).
- AUTO-DECIDED (ENABLE_GUARD row 11): M002 adds `#define SUPPORT_TONER_SAVE 1` to `TGT:config/model_b.h` → feature enabled for model B.
- AUTO-DECIDED (TAKE_LATEST_PARTIAL row 5): M008/P015/P016/P020 exclude eco_report lines `SRC:src/panel/menu_table.c:7-9,19-21`, `SRC:Makefile:7`, `SRC:config/model_a.h:4`.
- REPLACE (row 14): M019 changes target `Clamp(int v, int hi)` → `Clamp(int v, int lo, int hi)`; target has no callers today, but any out-of-tree caller would break.
- Scope beyond request: BUGFIX lines from latest (`SRC:src/features/toner_save/toner_save.c:7,24`) and dependency files `src/print/density.{c,h}`.
- Adaptations ≠ none: P007 (file alias model_a.h→model_b.h), P015/P016/P020 (partial take).
- Target behavior change: Menu_Dispatch("TONER_SAVE") / Pjl_Dispatch("ECONOMODE") now handled; Render_Page output density scaled by toner level (default OFF = 100 %).
### Blockers
None.
### Gate Result
PASS – Mapping coverage – C_trace rows 38 items (26 S + 12 deps) → all in M001–M020; B4 consumers → M021
PASS – Classes – all classes from decision-table.md with row number per M
PASS – Decisions – ENABLE_GUARD (M002), TAKE_LATEST_PARTIAL (M008), LAYOUT_RISK (M011, M015) marked AUTO-DECIDED; no CONFLICT/NEEDS_CONFIRMATION/UNCLASSIFIED/SOURCE_GONE
PASS – Plan coverage – 19 change M-ids → P001–P020; M016/M021 (SKIP/REPORT_ONLY) have none; each P names one M
PASS – Anchors – 16 non-add-file anchors, each `grep -c -F` = 1 in target file
PASS – Data – STR_TONER_SAVE enum (P008) + en table (P009, only language); NV field (P010) + default (P012); version/CRC none in target; menu (P016), PJL (P018), config (P007), build (P019, P020)
PASS – Aliases – no symbol aliases; file alias applied in P007
PASS – Extensions – no `ext` items
PASS – Content – every P has source + full text in `_work/D_plan.md`; adaptations listed in Risks
PASS – Build inclusion – toner_save.c (P020), density.c (P019)
PASS – Order – P001–P010 declarations/types/macros before P011–P020
PASS – Label convention – None found with pattern
PASS – Validation plan – command, dirs, baseline, fallback; no open questions
PASS – No snapshots – `OUTPUT_ROOT/Before`, `After` absent
PASS – Status row – D = Complete, Next = Awaiting Checkpoint E approval

## Checkpoint E - Before/After Implementation
### Output File Manifest
| File | Action (added/modified/deleted) | E-ids |
|---|---|---|
| `Makefile` | modified | E019, E020 |
| `config/model_b.h` | modified | E007 |
| `src/cmd/pjl_commands.c` | modified | E017, E018 |
| `src/features/toner_save/toner_save.c` | added | E006 |
| `src/features/toner_save/toner_save.h` | added | E005 |
| `src/panel/menu_table.c` | modified | E015, E016 |
| `src/print/density.c` | added | E002 |
| `src/print/density.h` | added | E001 |
| `src/print/render.c` | modified | E013, E014 |
| `src/resources/strings.h` | modified | E008 |
| `src/resources/strings_en.c` | modified | E009 |
| `src/settings/nv_settings.c` | modified | E011, E012 |
| `src/settings/nv_settings.h` | modified | E010 |
| `src/util/math_util.c` | modified | E004 |
| `src/util/math_util.h` | modified | E003 |
### Exact Changes
Executing plan approved by: AUTO (APPROVAL_MODE=auto)

| E-id | P-id | File:lines (OUT-A) | Change | Status (applied/skipped + reason) |
|---|---|---|---|---|
| E001 | P001 | `OUT-A:src/print/density.h:1-5` | add-file `cp -p` SRC:src/print/density.h | applied |
| E002 | P002 | `OUT-A:src/print/density.c:1-7` | add-file `cp -p` SRC:src/print/density.c | applied |
| E003 | P003 | `OUT-A:src/util/math_util.h:3` | Clamp prototype → `int Clamp(int v, int lo, int hi);` | applied |
| E004 | P004 | `OUT-A:src/util/math_util.c:3-8` | Clamp body replaced with SRC:src/util/math_util.c:3-8 | applied |
| E005 | P005 | `OUT-A:src/features/toner_save/toner_save.h:1-13` | add-file `cp -p` SRC | applied |
| E006 | P006 | `OUT-A:src/features/toner_save/toner_save.c:1-42` | add-file `cp -p` SRC (incl. BUGFIX L7, L24) | applied |
| E007 | P007 | `OUT-A:config/model_b.h:4` | +`#define SUPPORT_TONER_SAVE 1` | applied |
| E008 | P008 | `OUT-A:src/resources/strings.h:6` | +`STR_TONER_SAVE,` (git merge-file, conflicts=0) | applied |
| E009 | P009 | `OUT-A:src/resources/strings_en.c:6` | +`[STR_TONER_SAVE] = "Toner Save",` (merge, conflicts=0) | applied |
| E010 | P010 | `OUT-A:src/settings/nv_settings.h:8` | +`int toner_save_level;` (merge, conflicts=0) | applied |
| E011 | P011 | `OUT-A:src/settings/nv_settings.c:2` | +include toner_save.h | applied |
| E012 | P012 | `OUT-A:src/settings/nv_settings.c:15` | +`g_settings.toner_save_level = TONER_SAVE_OFF;` (merge, conflicts=0) | applied |
| E013 | P013 | `OUT-A:src/print/render.c:3-5` | +guarded include | applied |
| E014 | P014 | `OUT-A:src/print/render.c:11-13` | +guarded `TonerSave_ApplyDensity` call (merge, conflicts=0) | applied |
| E015 | P015 | `OUT-A:src/panel/menu_table.c:4-6` | +guarded include (ECO block excluded) | applied |
| E016 | P016 | `OUT-A:src/panel/menu_table.c:11-13` | +guarded TONER_SAVE entry (ECO entry excluded) | applied |
| E017 | P017 | `OUT-A:src/cmd/pjl_commands.c:4` | +include toner_save.h | applied |
| E018 | P018 | `OUT-A:src/cmd/pjl_commands.c:27` | +`{ "ECONOMODE", TonerSave_PjlSet },` | applied |
| E019 | P019 | `OUT-A:Makefile:2` | +`src/print/density.c` in SRCS | applied |
| E020 | P020 | `OUT-A:Makefile:6` | +`SRCS += src/features/toner_save/toner_save.c` | applied |
### Diff Summary
`git diff --no-index --stat Before After`: 15 files changed, 92 insertions(+), 4 deletions(-); 17 hunks (`diffs/output.diff`).
- `Makefile` +2/−1 · `config/model_b.h` +1 · `src/cmd/pjl_commands.c` +2 · `src/features/toner_save/toner_save.c` +42 (new) · `src/features/toner_save/toner_save.h` +13 (new) · `src/panel/menu_table.c` +6 · `src/print/density.c` +7 (new) · `src/print/density.h` +5 (new) · `src/print/render.c` +6 · `src/resources/strings.h` +1 · `src/resources/strings_en.c` +1 · `src/settings/nv_settings.c` +2 · `src/settings/nv_settings.h` +1 · `src/util/math_util.c` +2/−2 · `src/util/math_util.h` +1/−1
### Blockers
None. All 5 ADAPT_MERGE P-ids merged with `git merge-file` (conflicts=0); target-only lines (FAX entry, STR_FAX, fax_resolution, SUPPORT_FAX block) preserved.
### Gate Result
PASS – Before identical – `diff -rq -x .git TARGET_ROOT Before` → BEFORE_IDENTICAL
PASS – Every P applied – 20/20 P-ids → E001–E020 applied, 0 skipped
PASS – No unplanned change – 17/17 hunks mapped to E-ids (`_work/E_changes.md`)
PASS – Files – 15 files in `git diff --name-only` == 15 in Output File Manifest
PASS – Verbatim – 20/20 E-ids: inserted text `diff -w` == D_plan text
PASS – Encoding / EOL – all 11 modified files us-ascii, LF before and after; 4 new files us-ascii, LF
PASS – Labels – none (D: None found)
PASS – No validation run – no build/test executed in E
PASS – Read-only inputs – marker check → 0 files
PASS – Status row – E = Complete, Next = Awaiting Checkpoint F approval

## Checkpoint F - Validation and Handoff
### Validation Commands and Results
| Where | Command | Exit | Result |
|---|---|---|---|
| `OUTPUT_ROOT/Before` | `make -s MODEL=B` | 0 | baseline builds, no warnings |
| `OUTPUT_ROOT/After` | `make -s MODEL=B` | 0 | builds, no warnings (-Wall) |
| `OUTPUT_ROOT/Before` | `./printer_B` | 0 | `toner_save=-1`, `pjl=-1`, `density=10` |
| `OUTPUT_ROOT/After` | `./printer_B` | 0 | `toner_save=2`, `pjl=1`, `density=8` (LOW 80 %), `[INFO] Toner Save` logged, `fax header` still printed |
Details: `_work/F_validation.md`.
### Before/After Comparison
`diffs/output.diff` regenerated in F: identical to E version (excluding build artifact `printer_B`, present in both trees). 17 hunks → 20 E-ids → 20 approved P-ids; no E-F fixes.
### Traceability Matrix
| H-id | S-id | M-id | P-id | E-id | Output hunk | Result |
|---|---|---|---|---|---|---|
| H001 | S001 | M001 | P020 | E020 | `Makefile@@-1,8` | ported |
| H002 | S002 | M002 | P007 | E007 | `config/model_b.h@@-1,3` | ported (AUTO-DECIDED guard enable) |
| H003 | S003 | M003 | P017 | E017 | `src/cmd/pjl_commands.c@@-1,6` | ported |
| H004 | S004 | M004 | P018 | E018 | `src/cmd/pjl_commands.c@@-23,6` | ported |
| H005 | S005–S011 | M005 | P006 | E006 | `src/features/toner_save/toner_save.c@@-0,0` | ported (+ BUGFIX drift SRC L7, L24) |
| H006 | S012–S017 | M006 | P005 | E005 | `src/features/toner_save/toner_save.h@@-0,0` | ported |
| H007 | S018, S019 | M007, M008 | P015, P016 | E015, E016 | `src/panel/menu_table.c@@-1,10` | ported (partial take, ECO excluded) |
| H008 | S020, S021 | M009, M010 | P013, P014 | E013, E014 | `src/print/render.c@@-1,10` | ported |
| H009 | S022 | M011 | P008 | E008 | `src/resources/strings.h@@-3,6` | ported (LAYOUT_RISK) |
| H010 | S023 | M012 | P009 | E009 | `src/resources/strings_en.c@@-3,6` | ported |
| H011 | S024 | M013 | P011 | E011 | `src/settings/nv_settings.c@@-1,4` | ported |
| H012 | S025 | M014 | P012 | E012 | `src/settings/nv_settings.c@@-11,6` | ported |
| H013 | S026 | M015 | P010 | E010 | `src/settings/nv_settings.h@@-5,6` | ported (LAYOUT_RISK) |
| – (dep) | S008.d1 NV_GetSettings | M016 | – (SKIP) | – | – | already present |
| – (dep) | S010.d1 Log_Info | M016 | – (SKIP) | – | – | already present |
| – (dep) | S010.d2 Str_Get | M016 | – (SKIP) | – | – | already present |
| – (dep) | S011.d1 atoi | M016 | – (SKIP) | – | – | already present |
| – (dep) | S018.d1 model_config.h | M016 | – (SKIP) | – | – | already present |
| – (dep) | S019.d1 MenuEntry_t | M016 | – (SKIP) | – | – | already present |
| – (dep) | S004.d1 PjlEntry_t | M016 | – (SKIP) | – | – | already present |
| – (dep) | S009.d1 Density_Scale | M017 | P002 | E002 | `src/print/density.c@@-0,0` | ported |
| – (dep) | S009.d2 DENSITY_MAX | M018 | P001 | E001 | `src/print/density.h@@-0,0` | ported |
| – (dep) | S009.d4 density.h | M018 | P001 | E001 | `src/print/density.h@@-0,0` | ported |
| – (dep) | S009.d3 Clamp | M019 | P003, P004 | E003, E004 | `src/util/math_util.h@@-1,4`, `src/util/math_util.c@@-1,8` | ported (REPLACE signature) |
| – (dep) | S009.d5 Makefile density.c | M020 | P019 | E019 | `Makefile@@-1,8` | ported |
| – (B4) | eco_report (X1), main.c | M021 | – (REPORT_ONLY) | – | – | report only |
Counts: 13 H-ids → ported 13 · deps → ported 5, already present 7 · report only 1 · skipped 0 · blocked 0.
### Limitations and Tests Not Run
- No unit tests exist (B7: none found); validation = build + run of `src/main.c` driver only.
- NVRAM compatibility of the shifted `NvSettings_t` layout and shifted `StrId_t` values not testable here (no persisted data / other language tables).
- eco_report (consumer) intentionally not ported; not validated on target.
### Final Handoff
- OUTPUT_ROOT: `/Users/trantien/Documents/my-project/port-request-skill/tests/runs/run1/T0-toner-save/formula-source-T0-toner-save`
- After: `OUTPUT_ROOT/After` · Diff: `OUTPUT_ROOT/diffs/output.diff` · Report: `OUTPUT_ROOT/PORT_REPORT.md`
- Validation status: **Validated** (BUILD_CMD exit 0 Before/After; driver run shows toner save active).
- Needs human review:
  1. AUTO-DECIDED ENABLE_GUARD (M002): `#define SUPPORT_TONER_SAVE 1` added to `config/model_b.h`.
  2. AUTO-DECIDED TAKE_LATEST_PARTIAL (M008): eco_report lines excluded from menu_table.c / Makefile / config.
  3. AUTO-DECIDED LAYOUT_RISK HIGH (M011): `STR_TONER_SAVE` inserted → STR_QUALITY 2→3, STR_FAX 3→4.
  4. AUTO-DECIDED LAYOUT_RISK HIGH (M015): `toner_save_level` inserted in NVRAM struct → language/quality/fax_resolution offsets +4; no NV version/CRC.
  5. REPLACE (M019): target `Clamp(v, hi)` → `Clamp(v, lo, hi)` (no current target callers).
  6. Drift ported: BUGFIX `Clamp` line + `math_util.h` include in toner_save.c (`SRC:src/features/toner_save/toner_save.c:7,24`); new dependency files `src/print/density.{c,h}`.
  7. REPORT_ONLY: eco_report feature (`SRC:src/features/eco_report/*`) and `src/main.c` driver.
  8. B judgment: ECO blocks next to request lines classified UNRELATED (R14 signal 3 positional only).
- Next steps: review items 1–5; decide NVRAM migration/versioning for model B; copy `After/` changes into the target repo.
### Gate Result
PASS – Commands recorded – 4 commands (Before baseline + After) with dir/exit/result
PASS – Honest status – Validated: confirmed BUILD_CMD exit 0 + driver run 0; no unit tests exist
PASS – Diff stable – regenerated diff == E version (build artifact excluded); no E-F fixes
PASS – Traceability complete – 13 H rows + 12 dependency rows + 1 report-only; counts shown
PASS – Only approved changes – 17 hunks → E001–E020 → P001–P020
PASS – Input integrity – REQUEST_UNCHANGED; `-newer` check on SOURCE_ROOT/TARGET_ROOT empty
PASS – Handoff – paths, status, human-review list, limitations present
PASS – Single report – `find OUTPUT_ROOT -name '*REPORT*'` → 1; REPORT_PATH / Created at unchanged
PASS – Status row – F = Complete, Next approval gate = None
