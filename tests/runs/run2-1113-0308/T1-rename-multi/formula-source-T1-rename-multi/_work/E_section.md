### Output File Manifest
| File | Action (added/modified/deleted) | E-ids |
|---|---|---|
| `Makefile` | modified | E020, E021 |
| `config/model_b.h` | modified | E001 |
| `src/cmd/pjl_commands.c` | modified | E014, E015 |
| `src/features/eco/eco_mode.c` | added | E007, E008 |
| `src/features/eco/eco_mode.h` | added | E006 |
| `src/panel/menu_table.c` | modified | E016, E017 |
| `src/print/density.c` | added | E005 |
| `src/print/density.h` | added | E004 |
| `src/print/render.c` | modified | E018, E019 |
| `src/resources/strings.h` | modified | E010 |
| `src/resources/strings_en.c` | modified | E011 |
| `src/settings/nv_settings.c` | modified | E012, E013 |
| `src/settings/nv_settings.h` | modified | E009 |
| `src/util/math_util.c` | modified | E003 |
| `src/util/math_util.h` | modified | E002 |

### Exact Changes
Executing plan approved by: AUTO (APPROVAL_MODE=auto)

| E-id | P-id | File:lines (OUT-A) | Change | Status (applied/skipped + reason) |
|---|---|---|---|---|
| E001 | P001 | `config/model_b.h`:4 | add `#define SUPPORT_TONER_SAVE 1` after SUPPORT_FAX | applied |
| E002 | P002 | `src/util/math_util.h`:3 | prototype → `int Clamp(int v, int lo, int hi);` | applied |
| E003 | P003 | `src/util/math_util.c`:3-5 | Clamp signature + lower bound `lo` (2 lines replaced) | applied |
| E004 | P004 | `src/print/density.h`:1-5 | new file density.h (cp -p) | applied |
| E005 | P005 | `src/print/density.c`:1-7 | new file density.c (cp -p) | applied |
| E006 | P006 | `src/features/eco/eco_mode.h`:1-13 | new file eco_mode.h (cp -p) | applied |
| E007 | P007 | `src/features/eco/eco_mode.c`:1-48 | new file eco_mode.c (cp -p, request symbols) | applied |
| E008 | P008 | `src/features/eco/eco_mode.c`:21-27 | ext eco_effective_level L21-27 (in same copy) | applied |
| E009 | P009 | `src/settings/nv_settings.h`:8 | + `int eco_level;` after duplex | applied |
| E010 | P010 | `src/resources/strings.h`:6 | + `STR_TONER_SAVE,` after STR_DUPLEX | applied |
| E011 | P011 | `src/resources/strings_en.c`:6 | + `[STR_TONER_SAVE] = "Toner Save",` | applied |
| E012 | P012 | `src/settings/nv_settings.c`:2 | + include eco_mode.h | applied |
| E013 | P013 | `src/settings/nv_settings.c`:15 | + `g_settings.eco_level = TONER_SAVE_OFF;` | applied |
| E014 | P014 | `src/cmd/pjl_commands.c`:4 | + include eco_mode.h | applied |
| E015 | P015 | `src/cmd/pjl_commands.c`:27 | + `{ "ECONOMODE", EcoMode_PjlSet },` | applied |
| E016 | P016 | `src/panel/menu_table.c`:4-6 | + guarded include (3 lines) | applied |
| E017 | P017 | `src/panel/menu_table.c`:11-13 | + guarded menu entry TONER_SAVE (3 lines) | applied |
| E018 | P018 | `src/print/render.c`:3-5 | + guarded include (3 lines) | applied |
| E019 | P019 | `src/print/render.c`:11-13 | + guarded `density = EcoMode_ApplyDensity(density);` (3 lines) | applied |
| E020 | P020 | `Makefile`:6 | + `SRCS += src/features/eco/eco_mode.c` | applied |
| E021 | P021 | `Makefile`:7 | + `SRCS += src/print/density.c` | applied |

ADAPT_MERGE verification (E2): `git merge-file -p` with base REQ-B, ours target, theirs port version for render.c, strings.h, strings_en.c, nv_settings.c, nv_settings.h, menu_table.c (theirs without SRC lines 7-9, 19-21), pjl_commands.c → 7/7 `conflicts=0`, merge result byte-identical to `After/` (`_work/merge/merge_log.txt`). Target-only FAX lines preserved.

### Diff Summary
`git diff --no-index --stat Before After`: 15 files changed, 98 insertions(+), 3 deletions(-); 17 hunks in `diffs/output.diff`.
- `Makefile` +2 · `config/model_b.h` +1 · `src/cmd/pjl_commands.c` +2 · `src/features/eco/eco_mode.c` +48 (new) · `src/features/eco/eco_mode.h` +13 (new) · `src/panel/menu_table.c` +6 · `src/print/density.c` +7 (new) · `src/print/density.h` +5 (new) · `src/print/render.c` +6 · `src/resources/strings.h` +1 · `src/resources/strings_en.c` +1 · `src/settings/nv_settings.c` +2 · `src/settings/nv_settings.h` +1 · `src/util/math_util.c` +2/-2 · `src/util/math_util.h` +1/-1

### Blockers
None. No P-id skipped; no encoding/EOL deviation (all us-ascii, LF, before and after).

### Gate Result
PASS – 1 Before identical – `diff -rq -x .git TARGET_ROOT OUTPUT_ROOT/Before` → BEFORE_IDENTICAL (no output)
PASS – 2 Every P applied – 21/21 P-ids → E001–E021 `applied`
PASS – 3 No unplanned change – 17/17 hunks of `diffs/output.diff` mapped (Makefile→E020/E021, model_b.h→E001, pjl ×2→E014/E015, eco_mode.c→E007/E008, eco_mode.h→E006, menu_table→E016/E017, density.c→E005, density.h→E004, render→E018/E019, strings.h→E010, strings_en.c→E011, nv_settings.c ×2→E012/E013, nv_settings.h→E009, math_util.c→E003, math_util.h→E002)
PASS – 4 Files – 15 files in `git diff --name-only` == 15 in Output File Manifest
PASS – 5 Verbatim – 21/21 inserted/replaced texts equal D text (exact line compare, stricter than `diff -w`)
PASS – 6 Encoding / EOL – `file -I` unchanged for all modified files (us-ascii), CRLF count 0 before and after
PASS – 7 Labels – none applied (D: None found)
PASS – 8 No validation run – no build/test executed in E
PASS – 9 Read-only inputs – marker check on SOURCE_ROOT, TARGET_ROOT, SOURCE_REQUEST → 0 files
PASS – 10 Status row – E = Complete, Next approval gate = Awaiting Checkpoint F approval
