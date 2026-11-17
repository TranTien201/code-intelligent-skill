# D_plan – Formula Mapping Matrix and Planned Changes (full detail)

## Formula Mapping Matrix
| M-id | Formula (source behavior) | S-ids / H-ids | Request location | Latest source location | Target location | Target state | Port class | P-ids | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| M001 | build toner_save.c | S001 / H001 | REQ-A:Makefile:6 | SRC:Makefile:6 | TGT:Makefile:5 | MISSING | NON_CODE (row 18) | P020 | High |
| M002 | enable feature guard for the model | S002 / H002 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 | TGT:config/model_b.h:3 | MISSING | COPY_NEW (row 7) | P001 | High |
| M003 | PJL file includes feature header | S003 / H003 | REQ-A:src/cmd/pjl_commands.c:4 | SRC:src/cmd/pjl_commands.c:4 | TGT:src/cmd/pjl_commands.c:3 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P013 | High |
| M004 | PJL `ECONOMODE` → TonerSave_PjlSet | S004 / H004 | REQ-A:src/cmd/pjl_commands.c:27 | SRC:src/cmd/pjl_commands.c:27 | TGT:src/cmd/pjl_commands.c:25 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P014 | High |
| M005 | toner save logic (levels, density scaling + Clamp bugfix, menu/PJL handlers) | S005–S011 / H005 | REQ-A:src/features/toner_save/toner_save.c:1-40 | SRC:src/features/toner_save/toner_save.c:1-42 | TGT:src/features/toner_save/toner_save.c (new) | MISSING | COPY_NEW (row 7) | P009 | High |
| M006 | toner save API + level enum | S012–S013 / H006 | REQ-A:src/features/toner_save/toner_save.h:1-13 | SRC:src/features/toner_save/toner_save.h:1-13 | TGT:src/features/toner_save/toner_save.h (new) | MISSING | COPY_NEW (row 7) | P002 | High |
| M007 | menu file includes feature header (guarded) | S014 / H007 | REQ-A:src/panel/menu_table.c:4-6 | SRC:src/panel/menu_table.c:4-6 | TGT:src/panel/menu_table.c:3 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P015 | High |
| M008 | menu `TONER_SAVE` → TonerSave_MenuHandler (guarded) | S015 / H007 | REQ-A:src/panel/menu_table.c:11-13 | SRC:src/panel/menu_table.c:14-16 | TGT:src/panel/menu_table.c:7 | DIVERGED | TAKE_LATEST_PARTIAL (row 5) AUTO-DECIDED | P016 | High |
| M009 | render file includes feature header (guarded) | S016 / H008 | REQ-A:src/print/render.c:3-5 | SRC:src/print/render.c:3-5 | TGT:src/print/render.c:2 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P017 | High |
| M010 | Render_Page applies toner-save density (guarded) | S017 / H008 | REQ-A:src/print/render.c:11-13 | SRC:src/print/render.c:11-13 | TGT:src/print/render.c:7 | DIVERGED | ADAPT_MERGE (row 12) | P018 | High |
| M011 | string ID STR_TONER_SAVE | S018, S005.d2 (strings.h) / H009 | REQ-A:src/resources/strings.h:6 | SRC:src/resources/strings.h:6 | TGT:src/resources/strings.h:5 | DIVERGED | ADAPT_MERGE (row 12) | P007 | High |
| M012 | English text "Toner Save" | S019 / H010 | REQ-A:src/resources/strings_en.c:6 | SRC:src/resources/strings_en.c:6 | TGT:src/resources/strings_en.c:5 | DIVERGED | ADAPT_MERGE (row 12) | P010 | High |
| M013 | NV file includes feature header | S020 / H011 | REQ-A:src/settings/nv_settings.c:2 | SRC:src/settings/nv_settings.c:2 | TGT:src/settings/nv_settings.c:1 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P011 | High |
| M014 | NV default toner_save_level = OFF | S021 / H012 | REQ-A:src/settings/nv_settings.c:15 | SRC:src/settings/nv_settings.c:15 | TGT:src/settings/nv_settings.c:13 | DIVERGED | ADAPT_MERGE (row 12) | P012 | High |
| M015 | NV field toner_save_level | S022, S005.d2 (nv_settings.h) / H013 | REQ-A:src/settings/nv_settings.h:8 | SRC:src/settings/nv_settings.h:8 | TGT:src/settings/nv_settings.h:7 | DIVERGED | ADAPT_MERGE (row 12) + LAYOUT_RISK flag (row 15) AUTO-DECIDED | P006 | High |
| M016 | Clamp(v, lo, hi) used by bugfix + Density_Scale | S009.d1, S005.d1 / – | – | SRC:src/util/math_util.c:3-5, SRC:src/util/math_util.h:3 | TGT:src/util/math_util.c:3-5, TGT:src/util/math_util.h:3 | SIGNATURE_DIFF (no target callers) | REPLACE (row 14) | P004, P005 | High |
| M017 | Density_Scale + DENSITY_MAX + density.h | S009.d2–S009.d4 / – | – | SRC:src/print/density.c:1-7, SRC:src/print/density.h:1-5 | TGT:src/print/density.c, density.h (new) | MISSING | COPY_DEPENDENCY (row 8) | P003, P008 | High |
| M018 | build density.c | S009.d5 / – | – | SRC:Makefile:2 | TGT:Makefile:2 | MISSING | NON_CODE (row 18) | P019 | High |
| M019 | infrastructure already present | S008.d1, S010.d1, S010.d2, S021.d1, S015.d1, S004.d1, S015.d2, S017.d1, S005.d2 (log.h) / – | – | SRC (see C_trace) | TGT (see C_trace) | SAME_AS_SOURCE | SKIP_ALREADY_PRESENT (row 4) | – | High |
| M020 | consumers of the feature | S008.d2 (EcoReport_Print), S009.d6 (Menu_Quality → Density_Scale) / – | – | SRC:src/features/eco_report/eco_report.c:5-9, SRC:src/panel/menu.c:22 | – / TGT:src/panel/menu.c:19-23 | MISSING / DIVERGED | REPORT_ONLY (row 16) | – | High |

Coverage: C_trace rows 39 → M001–M020 (every row named once; S005.d2 split: strings.h→M011, nv_settings.h→M015, log.h→M019).

## Target Request-Label Convention
None found (searched: R10 `(REQ|CR|PR|ECR|ECO|TICKET|ISSUE|BUG|FIX|MOD|CHG)[-_#: ]?[0-9]{2,}` over TGT code → 0 hits). No labels added.

## Planned Changes (execution order: headers/types/macros before users)
Insertion convention: `insert-after` = new lines go right after the anchor line; `replace` = anchor line(s) replaced.

### P001 – config/model_b.h – add-define (M002)
Anchor TGT:config/model_b.h:3 `#define SUPPORT_FAX 1` (insert-after). Source SRC:config/model_a.h:3. Adaptation: file `config/model_a.h` → `config/model_b.h` (alias map); appended after the target's last feature define.
```
#define SUPPORT_TONER_SAVE 1
```
### P002 – src/features/toner_save/toner_save.h – add-file (M006)
Source SRC:src/features/toner_save/toner_save.h:1-13, verbatim copy (`cp`).
### P003 – src/print/density.h – add-file (M017)
Source SRC:src/print/density.h:1-5, verbatim copy.
### P004 – src/util/math_util.h – replace (M016)
Anchor TGT:src/util/math_util.h:3 `int Clamp(int v, int hi);` (replace). Source SRC:src/util/math_util.h:3.
```
int Clamp(int v, int lo, int hi);
```
### P005 – src/util/math_util.c – replace (M016)
Anchor TGT:src/util/math_util.c:3 `int Clamp(int v, int hi)` and TGT:src/util/math_util.c:5 `    if (v < 0) return 0;` (replace each). Source SRC:src/util/math_util.c:3,5.
```
int Clamp(int v, int lo, int hi)
```
```
    if (v < lo) return lo;
```
### P006 – src/settings/nv_settings.h – insert (M015)
Anchor TGT:src/settings/nv_settings.h:7 `    int duplex;` (insert-after). Source SRC:src/settings/nv_settings.h:8.
```
    int toner_save_level;
```
### P007 – src/resources/strings.h – insert (M011)
Anchor TGT:src/resources/strings.h:5 `    STR_DUPLEX,` (insert-after). Source SRC:src/resources/strings.h:6.
```
    STR_TONER_SAVE,
```
### P008 – src/print/density.c – add-file (M017)
Source SRC:src/print/density.c:1-7, verbatim copy.
### P009 – src/features/toner_save/toner_save.c – add-file (M005)
Source SRC:src/features/toner_save/toner_save.c:1-42, verbatim copy (request lines + BUGFIX L7, L24).
### P010 – src/resources/strings_en.c – insert (M012)
Anchor TGT:src/resources/strings_en.c:5 `    [STR_DUPLEX] = "2-Sided",` (insert-after). Source SRC:src/resources/strings_en.c:6.
```
    [STR_TONER_SAVE] = "Toner Save",
```
### P011 – src/settings/nv_settings.c – add-include (M013)
Anchor TGT:src/settings/nv_settings.c:1 `#include "nv_settings.h"` (insert-after). Source SRC:src/settings/nv_settings.c:2.
```
#include "../features/toner_save/toner_save.h"
```
### P012 – src/settings/nv_settings.c – insert (M014)
Anchor TGT:src/settings/nv_settings.c:13 `    g_settings.duplex = 0;` (insert-after). Source SRC:src/settings/nv_settings.c:15.
```
    g_settings.toner_save_level = TONER_SAVE_OFF;
```
### P013 – src/cmd/pjl_commands.c – add-include (M003)
Anchor TGT:src/cmd/pjl_commands.c:3 `#include "../core/log.h"` (insert-after). Source SRC:src/cmd/pjl_commands.c:4.
```
#include "../features/toner_save/toner_save.h"
```
### P014 – src/cmd/pjl_commands.c – add-registration (M004)
Anchor TGT:src/cmd/pjl_commands.c:25 `    { "DUPLEX", Pjl_SetDuplex },` (insert-after). Source SRC:src/cmd/pjl_commands.c:27.
```
    { "ECONOMODE", TonerSave_PjlSet },
```
### P015 – src/panel/menu_table.c – add-include (M007)
Anchor TGT:src/panel/menu_table.c:3 `#include "../../config/model_config.h"` (insert-after). Source SRC:src/panel/menu_table.c:4-6 (excluded UNRELATED SRC:src/panel/menu_table.c:7-9).
```
#ifdef SUPPORT_TONER_SAVE
#include "../features/toner_save/toner_save.h"
#endif
```
### P016 – src/panel/menu_table.c – add-registration (M008)
Anchor TGT:src/panel/menu_table.c:7 `    { "DUPLEX",   Menu_Duplex },` (insert-after). Source SRC:src/panel/menu_table.c:14-16. Adaptation: partial take – SRC:src/panel/menu_table.c:19-21 (ECO_REPORT) excluded; target-only FAX entry TGT:src/panel/menu_table.c:10 kept.
```
#ifdef SUPPORT_TONER_SAVE
    { "TONER_SAVE", TonerSave_MenuHandler },
#endif
```
### P017 – src/print/render.c – add-include (M009)
Anchor TGT:src/print/render.c:2 `#include "../../config/model_config.h"` (insert-after). Source SRC:src/print/render.c:3-5.
```
#ifdef SUPPORT_TONER_SAVE
#include "../features/toner_save/toner_save.h"
#endif
```
### P018 – src/print/render.c – insert (M010)
Anchor TGT:src/print/render.c:7 `    Log_Info("render start");` (insert-after). Source SRC:src/print/render.c:11-13. Target-only SUPPORT_FAX block TGT:src/print/render.c:9-11 kept.
```
#ifdef SUPPORT_TONER_SAVE
    density = TonerSave_ApplyDensity(density);
#endif
```
### P019 – Makefile – add-to-build (M018)
Anchor TGT:Makefile:2 `SRCS = src/main.c src/core/log.c src/util/math_util.c \` (replace). Source SRC:Makefile:2.
```
SRCS = src/main.c src/core/log.c src/util/math_util.c src/print/density.c \
```
### P020 – Makefile – add-to-build (M001)
Anchor TGT:Makefile:5 `       src/cmd/pjl_commands.c src/resources/strings_en.c` (insert-after). Source SRC:Makefile:6 (excluded UNRELATED SRC:Makefile:7).
```
SRCS += src/features/toner_save/toner_save.c
```

## Output snapshot plan (D4)
Scope: full copy of `TARGET_ROOT` (no `.git`, no build outputs present) → `OUTPUT_ROOT/Before` (unmodified) and `OUTPUT_ROOT/After` (+ P001–P020). Neither exists yet (nothing to replace).

## Validation plan (D5)
- Command `make -s MODEL=B` (BUILD_CMD) in `OUTPUT_ROOT/Before` (baseline) and `OUTPUT_ROOT/After`; expected: exit 0, no `-Wall` warnings in After.
- Smoke run `./printer_B` (driver TGT:src/main.c:9-14) in both: expected Before `toner_save=-1`, `pjl=-1`, `density=10`; After `toner_save=2`, `pjl=1`, `density=8` (level 1 after PJL → 80 % of 10).
- Build outputs (`printer_B`) removed after validation so `Before/`/`After/` stay source snapshots; `diffs/output.diff` = `git diff --no-index Before After`.
- Fallback if `make` fails for environment reasons: `cc -fsyntax-only -Wall -DMODEL_B <SRCS>` in After.
- Open questions: none (BUILD_CMD given).
