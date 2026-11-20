### Formula Mapping Matrix
| M-id | Formula (source behavior) | S-ids / H-ids | Request location | Latest source location | Target location | Target state | Port class | P-ids | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| M001 | F1 eco module: level get/validate, density scaling, menu/PJL handlers | S005–S011 / H005 | REQ-A:src/features/toner_save/toner_save.c:1-40 | SRC:src/features/eco/eco_mode.c:1-20,28-48 | `src/features/eco/eco_mode.c` (new) | MISSING | COPY_NEW (row 7) | P007 | High |
| M002 | F1 level clamp before scaling (fix #1234) | S027 (ext) | – | SRC:src/features/eco/eco_mode.c:21-27 | `src/features/eco/eco_mode.c` (new) | MISSING | COPY_NEW (row 7), flag `ext` – scope beyond request | P008 | High |
| M003 | F1 module interface: guard, level enum OFF/LOW/HIGH, 4 prototypes | S012–S017 / H006 | REQ-A:src/features/toner_save/toner_save.h:1-13 | SRC:src/features/eco/eco_mode.h:1-13 | `src/features/eco/eco_mode.h` (new) | MISSING | COPY_NEW (row 7) | P006 | High |
| M004 | F3 density scaling helper | S009.d1–d3 | – | SRC:src/print/density.c:1-7, SRC:src/print/density.h:1-5 | `src/print/density.{c,h}` (new) | MISSING | COPY_DEPENDENCY (row 8) | P004, P005 | High |
| M005 | F3 Clamp(v, lo, hi) used by fix #1234 and Density_Scale | S027.d1 | – | SRC:src/util/math_util.c:3-8, SRC:src/util/math_util.h:3 | TGT:src/util/math_util.c:3-8, TGT:src/util/math_util.h:3 | SIGNATURE_DIFF (no target callers) | REPLACE (row 14) | P002, P003 | High |
| M006 | F7 feature enabled for the model | S002 / H002 | REQ-A:config/model_a.h:3 | SRC:config/model_a.h:3 | TGT:config/model_b.h:1-3 | MISSING | ENABLE_GUARD (row 11) – AUTO-DECIDED (row 7 not usable: model_a.h is MODEL_A-only, absent in target) | P001 | High |
| M007 | F8 build eco module | S001 / H001 | REQ-A:Makefile:6 | SRC:Makefile:6 | TGT:Makefile:1-8 | DIVERGED | TAKE_LATEST_PARTIAL (row 5) – AUTO-DECIDED (exclude SRC:Makefile:7) | P020 | High |
| M008 | F8 build density helper | S009.d4 | – | SRC:Makefile:2 | TGT:Makefile:2-5 | MISSING | NON_CODE (row 18) | P021 | High |
| M009 | F2 PJL module sees feature header | S003 / H003 | REQ-A:src/cmd/pjl_commands.c:4 | SRC:src/cmd/pjl_commands.c:4 | TGT:src/cmd/pjl_commands.c:1-3 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P014 | High |
| M010 | F2 PJL "ECONOMODE" → EcoMode_PjlSet | S004 / H004 | REQ-A:src/cmd/pjl_commands.c:27 | SRC:src/cmd/pjl_commands.c:27 | TGT:src/cmd/pjl_commands.c:23-26 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P015 | High |
| M011 | F1 menu module sees feature header (guarded) | S018 / H007 | REQ-A:src/panel/menu_table.c:4-6 | SRC:src/panel/menu_table.c:4-6 | TGT:src/panel/menu_table.c:1-3 | SAME_AS_BEFORE | TAKE_LATEST_PARTIAL (row 5) – AUTO-DECIDED (exclude SRC:src/panel/menu_table.c:7-9) | P016 | High |
| M012 | F1 menu "TONER_SAVE" → EcoMode_MenuHandler (guarded) | S019 / H007 | REQ-A:src/panel/menu_table.c:11-13 | SRC:src/panel/menu_table.c:14-16 | TGT:src/panel/menu_table.c:5-11 | DIVERGED | TAKE_LATEST_PARTIAL (row 5) – AUTO-DECIDED (exclude SRC:src/panel/menu_table.c:19-21; merge keeps FAX) | P017 | High |
| M013 | F3 render module sees feature header (guarded) | S020 / H008 | REQ-A:src/print/render.c:3-5 | SRC:src/print/render.c:3-5 | TGT:src/print/render.c:1-3 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P018 | High |
| M014 | F3 Render_Page applies eco density | S021 / H008 | REQ-A:src/print/render.c:11-13 | SRC:src/print/render.c:11-13 | TGT:src/print/render.c:5-13 | DIVERGED | ADAPT_MERGE (row 12) | P019 | High |
| M015 | F5 string ID STR_TONER_SAVE | S022 / H009 | REQ-A:src/resources/strings.h:6 | SRC:src/resources/strings.h:6 | TGT:src/resources/strings.h:3-9 | DIVERGED | ADAPT_MERGE (row 12); layout shift → HIGH risk (row 15 noted) | P010 | High |
| M016 | F5 English text "Toner Save" | S023 / H010 | REQ-A:src/resources/strings_en.c:6 | SRC:src/resources/strings_en.c:6 | TGT:src/resources/strings_en.c:3-8 | DIVERGED | ADAPT_MERGE (row 12) | P011 | High |
| M017 | F6 NV module sees feature header | S024 / H011 | REQ-A:src/settings/nv_settings.c:2 | SRC:src/settings/nv_settings.c:2 | TGT:src/settings/nv_settings.c:1 | SAME_AS_BEFORE | APPLY_PORT_VERSION (row 6) | P012 | High |
| M018 | F6 default eco_level = TONER_SAVE_OFF | S025 / H012 | REQ-A:src/settings/nv_settings.c:15 | SRC:src/settings/nv_settings.c:15 | TGT:src/settings/nv_settings.c:10-17 | DIVERGED | ADAPT_MERGE (row 12) | P013 | High |
| M019 | F6 NV field eco_level | S026 / H013 | REQ-A:src/settings/nv_settings.h:8 | SRC:src/settings/nv_settings.h:8 | TGT:src/settings/nv_settings.h:5-11 | DIVERGED | ADAPT_MERGE (row 12); NVRAM layout shift → HIGH risk (row 15 noted) | P009 | High |
| M020 | infrastructure already present | S008.d1, S010.d1, S010.d2 | – | SRC:src/settings/nv_settings.c:6, SRC:src/core/log.c:4, SRC:src/resources/strings_en.c:10 | TGT:src/settings/nv_settings.c:5, TGT:src/core/log.c:4, TGT:src/resources/strings_en.c:10 | SAME_AS_SOURCE | SKIP_ALREADY_PRESENT (row 4) | – | High |
| M021 | consumers: eco_report feature, main driver | B4 CONSUMER hits | – | SRC:src/features/eco_report/eco_report.c:5-15, SRC:src/main.c:11-13 | (eco_report absent; TGT:src/main.c:11-13 identical) | – | REPORT_ONLY (row 16) | – | High |

### Target Request-Label Convention
None found (searched R10: `(REQ|CR|PR|ECR|ECO|TICKET|ISSUE|BUG|FIX|MOD|CHG)[-_#: ]?[0-9]{2,}` over TGT `*.c *.h` → 0 hits). No labels will be added.

### Planned Changes
| P-id | Target file | Action | Anchor (exact target text or line) | Content source | Adaptation | Label |
|---|---|---|---|---|---|---|
| P001 | `config/model_b.h` | add-define | TGT:config/model_b.h:3 `#define SUPPORT_FAX 1` | SRC:config/model_a.h:3 | position AUTO-DECIDED: appended after last feature define (TGT:config/model_b.h:3); request also appended at end of model_a.h | none |
| P002 | `src/util/math_util.h` | replace | TGT:src/util/math_util.h:3 `int Clamp(int v, int hi);` | SRC:src/util/math_util.h:3 | none (REPLACE row 14: target prototype `int Clamp(int v, int hi);` replaced) | none |
| P003 | `src/util/math_util.c` | replace | TGT:src/util/math_util.c:3 `int Clamp(int v, int hi)` | SRC:src/util/math_util.c:3-5 | none (REPLACE row 14: target L3-5 replaced; L4 `{` identical) | none |
| P004 | `src/print/density.h` | add-file | (new file) | SRC:src/print/density.h:1-5 | none | none |
| P005 | `src/print/density.c` | add-file | (new file) | SRC:src/print/density.c:1-7 | none | none |
| P006 | `src/features/eco/eco_mode.h` | add-file | (new file) | SRC:src/features/eco/eco_mode.h:1-13 | none | none |
| P007 | `src/features/eco/eco_mode.c` | add-file | (new file) | SRC:src/features/eco/eco_mode.c:1-20,28-48 | none (file written together with P008 as SRC:src/features/eco/eco_mode.c:1-48) | none |
| P008 | `src/features/eco/eco_mode.c` | insert | (new file) | SRC:src/features/eco/eco_mode.c:21-27 | none; ext (scope beyond request), inserted between EcoMode_GetLevel and EcoMode_ApplyDensity as in source | none |
| P009 | `src/settings/nv_settings.h` | insert | TGT:src/settings/nv_settings.h:7 `    int duplex;` | SRC:src/settings/nv_settings.h:8 | none; target-only `fax_resolution` kept | none |
| P010 | `src/resources/strings.h` | insert | TGT:src/resources/strings.h:5 `    STR_DUPLEX,` | SRC:src/resources/strings.h:6 | none; target-only `STR_FAX` kept | none |
| P011 | `src/resources/strings_en.c` | insert | TGT:src/resources/strings_en.c:5 `    [STR_DUPLEX] = "2-Sided",` | SRC:src/resources/strings_en.c:6 | none; target-only `[STR_FAX]` kept | none |
| P012 | `src/settings/nv_settings.c` | add-include | TGT:src/settings/nv_settings.c:1 `#include "nv_settings.h"` | SRC:src/settings/nv_settings.c:2 | none | none |
| P013 | `src/settings/nv_settings.c` | insert | TGT:src/settings/nv_settings.c:13 `    g_settings.duplex = 0;` | SRC:src/settings/nv_settings.c:15 | none; target-only fax default kept | none |
| P014 | `src/cmd/pjl_commands.c` | add-include | TGT:src/cmd/pjl_commands.c:3 `#include "../core/log.h"` | SRC:src/cmd/pjl_commands.c:4 | none | none |
| P015 | `src/cmd/pjl_commands.c` | add-registration | TGT:src/cmd/pjl_commands.c:25 `    { "DUPLEX", Pjl_SetDuplex },` | SRC:src/cmd/pjl_commands.c:27 | none | none |
| P016 | `src/panel/menu_table.c` | add-include | TGT:src/panel/menu_table.c:3 `#include "../../config/model_config.h"` | SRC:src/panel/menu_table.c:4-6 | partial take: SRC:src/panel/menu_table.c:7-9 (eco_report include) excluded | none |
| P017 | `src/panel/menu_table.c` | add-registration | TGT:src/panel/menu_table.c:7 `    { "DUPLEX",   Menu_Duplex },` | SRC:src/panel/menu_table.c:14-16 | partial take: SRC:src/panel/menu_table.c:19-21 (ECO_REPORT entry) excluded; target-only FAX entry kept | none |
| P018 | `src/print/render.c` | add-include | TGT:src/print/render.c:2 `#include "../../config/model_config.h"` | SRC:src/print/render.c:3-5 | none | none |
| P019 | `src/print/render.c` | insert | TGT:src/print/render.c:7 `    Log_Info("render start");` | SRC:src/print/render.c:11-13 | none; target-only SUPPORT_FAX block kept after "render done" | none |
| P020 | `Makefile` | add-to-build | TGT:Makefile:5 `       src/cmd/pjl_commands.c src/resources/strings_en.c` | SRC:Makefile:6 | partial take: SRC:Makefile:7 (eco_report.c) excluded | none |
| P021 | `Makefile` | add-to-build | TGT:Makefile:5 `       src/cmd/pjl_commands.c src/resources/strings_en.c` | SRC:Makefile:2 (density.c entry) | AUTO-DECIDED: source lists density.c inside `SRCS =` (SRC:Makefile:2); added as own `SRCS +=` line after P020 so existing target lines stay untouched | none |

Full new text per P-id: `_work/D_plan.md` (fenced) and `_work/D_plan.json`. Order: macro → Clamp → density → eco_mode.h → eco_mode.c → data (struct, enum, strings) → users (nv, pjl, menu, render) → build. Every anchor verified unique (`grep -c -F -x` = 1). New files `eco_mode.c`, `density.c` → P020, P021 (add-to-build); headers need no build entry.
Output snapshots (D4): `OUTPUT_ROOT/Before` and `After` = full copy of `TARGET_ROOT` (no `.git`/build outputs present); neither exists yet (no replacement needed).

### Validation Plan
- Command: `BUILD_CMD` = `make -s MODEL=B` (TGT:Makefile:1,7-8 confirm `MODEL ?= B`, `$(CC) -Wall -DMODEL_$(MODEL)`), run in `OUTPUT_ROOT/Before` (baseline) and `OUTPUT_ROOT/After`; capture warnings (`-Wall`).
- Run `./printer_B` in both (behavior driver TGT:src/main.c:9-13). Expected Before: `toner_save=-1`, `pjl=-1`, `density=10`. Expected After: `toner_save=2`, `pjl=1`, `density=8` (level LOW → 80 %, Clamp(8,0,15)), plus `[INFO] Toner Save` log lines; FAX output unchanged (`[INFO] fax header`).
- Diff `Before` vs `After` (`diff -ruN`) → `diffs/output.diff`; every hunk must map to an E-id.
- Fallback if `make` fails for environment reasons: `cc -fsyntax-only -DMODEL_B` on each `.c` of the SRCS list.
- Build outputs (`printer_B`) are removed from the snapshots after validation so `After` holds sources only (recorded in F).
- Open questions: none (command given).

### Risks
1. HIGH – NVRAM layout (row 15): `int eco_level` inserted after `duplex` in `NvSettings_t` (TGT:src/settings/nv_settings.h:4 says it is stored in NVRAM) shifts `language`, `quality`, `fax_resolution` by 4 bytes; no version/CRC exists to detect old data.
2. HIGH – enum IDs (row 15): `STR_TONER_SAVE` inserted after `STR_DUPLEX` shifts `STR_QUALITY` 2→3, `STR_FAX` 3→4, `STR_COUNT` 3→4.
3. AUTO-DECIDED – `Clamp` REPLACE (row 14): target `Clamp(v, hi)` becomes `Clamp(v, lo, hi)`; no current target callers, but any future model-B code written for the 2-arg form will not compile.
4. AUTO-DECIDED – ENABLE_GUARD: `SUPPORT_TONER_SAVE` enabled for model B (P001), position after `SUPPORT_FAX` (merge of REQ-B/target would conflict at end of file).
5. AUTO-DECIDED – partial takes: eco_report lines excluded (SRC:Makefile:7, SRC:src/panel/menu_table.c:7-9,19-21); `eco_report` feature (CONSUMER) not ported.
6. AUTO-DECIDED – Makefile style: `SRCS += src/print/density.c` as own line (source has it inside `SRCS =`, SRC:Makefile:2).
7. Scope beyond request: ext S027 `eco_effective_level` + `math_util.h` include (BUGFIX fix #1234), and dependencies density.c/.h.
8. Drift: request names were renamed in latest (TonerSave_→EcoMode_, toner_save/→eco/, toner_save_level→eco_level); target receives latest names.
9. Target behavior change: Render_Page now scales density when a level is set (density 10 → 8 with level LOW); FAX behavior untouched.

### Blockers
None. All decisions taken by the auto default rules are marked AUTO-DECIDED above and repeated in Final Handoff.

### Gate Result
PASS – 1 Mapping coverage – 35/35 `C_trace.md` rows → M001–M020 (+ M021 REPORT_ONLY for B4 consumers)
PASS – 2 Classes – decision-table classes with row numbers on every M-id
PASS – 3 Decisions – TAKE_LATEST_PARTIAL (M007, M011, M012), ENABLE_GUARD (M006), layout risk (M015, M019) marked AUTO-DECIDED / HIGH; no CONFLICT/NEEDS_CONFIRMATION/UNCLASSIFIED/SOURCE_GONE
PASS – 4 Plan coverage – 19 change M-ids have ≥1 P-id (21 P-ids, each names one M); M020/M021 have none
PASS – 5 Anchors – 16 non-add-file P-ids anchored on TGT:path:line, each anchor `grep -c -F -x` = 1 (P008 is inside new file P007)
PASS – 6 Data – STR_TONER_SAVE: enum P010 + only language table P011; eco_level: struct P009 + default P013; version/CRC: none exists; registries P015, P017; config P001; build P020, P021
PASS – 7 Aliases – target has no renamed equivalents (C: RENAMED 0); planned text uses latest names; no substitutions needed
PASS – 8 Extensions – ext S027 planned (M002/P008)
PASS – 9 Content – 21/21 P-ids have content source + full text in `_work/D_plan.md`; adaptations listed in Risks 4–6
PASS – 10 Build inclusion – eco_mode.c → P020, density.c → P021
PASS – 11 Order – macro/types/headers (P001–P006, P009–P010) before users (P007+, P012–P019)
PASS – 12 Label convention – None found + pattern
PASS – 13 Validation plan – command, dirs, baseline, expected values, fallback, no open questions
PASS – 14 No snapshots – `OUTPUT_ROOT/Before`, `After` do not exist
PASS – 15 Status row – D = Complete, Next approval gate = Awaiting Checkpoint E approval
