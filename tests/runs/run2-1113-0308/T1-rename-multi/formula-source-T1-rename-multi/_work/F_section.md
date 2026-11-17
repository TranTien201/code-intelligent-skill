### Validation Commands and Results
| Where | Command | Exit | Result |
|---|---|---|---|
| `OUTPUT_ROOT/Before` | `make -s MODEL=B` (BUILD_CMD) | 0 | baseline builds, 0 warnings (`-Wall`) |
| `OUTPUT_ROOT/Before` | `./printer_B` | 0 | `copies=2`, `toner_save=-1`, `pjl=-1`, `density=10` |
| `OUTPUT_ROOT/After` | `make -s MODEL=B` (BUILD_CMD) | 0 | builds, 0 warnings (`-Wall`) |
| `OUTPUT_ROOT/After` | `./printer_B` | 0 | `copies=2`, `[INFO] Toner Save`, `toner_save=2`, `[INFO] Toner Save`, `pjl=1`, `density=8`; `[INFO] fax header` still printed |

After matches the D expectations exactly (menu level 2 accepted, PJL ECONOMODE=1 → LOW → 80 % → density 10→8). Built binaries were removed from both snapshots afterwards. Raw output: `_work/F_validation.md`.

### Before/After Comparison
`diffs/output.diff` regenerated after validation and byte-identical to the E version (`cmp` → DIFF_STABLE). 15 files, +98/-3, 17 hunks; every hunk → E-id → approved P-id (see Traceability). No `E-F#` fixes were needed. `Before/` still identical to `TARGET_ROOT`.

### Traceability Matrix
| H-id | S-id | M-id | P-id | E-id | Output hunk | Result |
|---|---|---|---|---|---|---|
| H001 | S001 | M007 | P020 | E020 | `Makefile` @@ -3,6 +3,8 @@ (OUT-A:Makefile:6) | ported (partial take, eco_report line excluded) |
| H002 | S002 | M006 | P001 | E001 | `config/model_b.h` @@ -1,3 +1,4 @@ (OUT-A:config/model_b.h:4) | ported (ENABLE_GUARD into model_b.h, AUTO-DECIDED) |
| H003 | S003 | M009 | P014 | E014 | `src/cmd/pjl_commands.c` @@ -1,6 +1,7 @@ | ported |
| H004 | S004 | M010 | P015 | E015 | `src/cmd/pjl_commands.c` @@ -23,6 +24,7 @@ | ported |
| H005 | S005–S011 | M001 | P007 | E007 | `src/features/eco/eco_mode.c` @@ -0,0 +1,48 @@ (L1-20, 28-48) | ported (latest names, BUGFIX logic) |
| H006 | S012–S017 | M003 | P006 | E006 | `src/features/eco/eco_mode.h` @@ -0,0 +1,13 @@ | ported |
| H007 | S018 | M011 | P016 | E016 | `src/panel/menu_table.c` @@ -1,10 +1,16 @@ (L4-6) | ported (partial take) |
| H007 | S019 | M012 | P017 | E017 | `src/panel/menu_table.c` @@ -1,10 +1,16 @@ (L11-13) | ported (partial take, FAX kept) |
| H008 | S020 | M013 | P018 | E018 | `src/print/render.c` @@ -1,10 +1,16 @@ (L3-5) | ported |
| H008 | S021 | M014 | P019 | E019 | `src/print/render.c` @@ -1,10 +1,16 @@ (L11-13) | ported (3-way merge, FAX kept) |
| H009 | S022 | M015 | P010 | E010 | `src/resources/strings.h` @@ -3,6 +3,7 @@ | ported (layout risk) |
| H010 | S023 | M016 | P011 | E011 | `src/resources/strings_en.c` @@ -3,6 +3,7 @@ | ported |
| H011 | S024 | M017 | P012 | E012 | `src/settings/nv_settings.c` @@ -1,4 +1,5 @@ | ported |
| H012 | S025 | M018 | P013 | E013 | `src/settings/nv_settings.c` @@ -11,6 +12,7 @@ | ported |
| H013 | S026 | M019 | P009 | E009 | `src/settings/nv_settings.h` @@ -5,6 +5,7 @@ | ported (NVRAM layout risk) |
| ext | S027 | M002 | P008 | E008 | `src/features/eco/eco_mode.c` @@ -0,0 +1,48 @@ (L21-27) | ported (ext) |
| dep | S008.d1 | M020 | – (no change needed) | – | – (TGT:src/settings/nv_settings.c:5 equal) | already present |
| dep | S009.d1–d3 | M004 | P004, P005 | E004, E005 | `src/print/density.h` @@ -0,0 +1,5 @@; `src/print/density.c` @@ -0,0 +1,7 @@ | ported (dependency) |
| dep | S009.d4 | M008 | P021 | E021 | `Makefile` @@ -3,6 +3,8 @@ (OUT-A:Makefile:7) | ported (build entry, AUTO-DECIDED style) |
| dep | S027.d1 | M005 | P002, P003 | E002, E003 | `src/util/math_util.h` @@ -1,4 +1,4 @@; `src/util/math_util.c` @@ -1,8 +1,8 @@ | ported (REPLACE, AUTO-DECIDED) |
| dep | S010.d1 | M020 | – (no change needed) | – | – (TGT:src/core/log.c:4 equal) | already present |
| dep | S010.d2 | M020 | – (no change needed) | – | – (TGT:src/resources/strings_en.c:10 equal) | already present |
| consumer | eco_report, main (B4) | M021 | – (REPORT_ONLY) | – | – | report only |

Counts: 13 H-ids in 15 rows → ported 15; ext ported 1; dependencies: ported 3, already present 3; report only 1; blocked 0. 17/17 output hunks covered.

### Limitations and Tests Not Run
- No unit tests exist in source or target (B7: `none found`); validation = build with `-Wall` + run of the target's own driver `src/main.c`.
- Only MODEL=B was built (target scope); behaviour with `SUPPORT_TONER_SAVE` undefined was not built.
- NVRAM compatibility with devices holding the old `NvSettings_t` layout cannot be tested here (no persistence code in the tree).

### Final Handoff
- Status: **Validated** (BUILD_CMD given; Before and After build, After runs with expected behaviour).
- Output: `OUTPUT_ROOT` = /Users/trantien/Documents/my-project/port-request-skill/tests/runs/run2-1113-0308/T1-rename-multi/formula-source-T1-rename-multi · ported tree `After/` · baseline `Before/` · diff `diffs/output.diff` · report `PORT_REPORT.md` · evidence `_work/`.
- Needs human review (AUTO-DECIDED in auto mode):
  1. ENABLE_GUARD: `#define SUPPORT_TONER_SAVE 1` added to `config/model_b.h:4` (after `SUPPORT_FAX`) – is toner save wanted on model B, and at this position?
  2. REPLACE: target `Clamp(int v, int hi)` changed to source `Clamp(int v, int lo, int hi)` (`src/util/math_util.{c,h}`); no target callers today.
  3. Partial takes / REPORT_ONLY: the `eco_report` feature (SRC:src/features/eco_report/*, SRC:Makefile:7, SRC:config/model_a.h:4, SRC:src/panel/menu_table.c:7-9,19-21) was classified CONSUMER and **not** ported (R14 proximity signal vs. its own guard → UNCLEAR, auto-decided UNRELATED).
  4. Makefile style: `SRCS += src/features/eco/eco_mode.c` and `SRCS += src/print/density.c` appended (source keeps density.c inside `SRCS =`).
  5. LAYOUT_RISK (HIGH): `eco_level` inserted after `duplex` in NVRAM struct `NvSettings_t`; `STR_TONER_SAVE` shifts `STR_QUALITY`/`STR_FAX` values.
  6. Scope beyond request: ext `eco_effective_level` + `math_util.h` include (fix #1234), dependencies `density.c/.h`.
  7. Drift: request names renamed in latest – target receives `EcoMode_*`, `src/features/eco/eco_mode.*`, `eco_level`, `ECO_MODE_H` (not `TonerSave_*`/`toner_save_level`).
- Next steps: review the 7 items, then copy `After/` changes (or apply `diffs/output.diff`) to the real target tree.

### Gate Result
PASS – 1 Commands recorded – Before + After build and run with cwd, exit codes, results
PASS – 2 Honest status – Validated: confirmed BUILD_CMD succeeded in After; no runnable tests exist (stated)
PASS – 3 Diff stable – regenerated `diffs/output.diff` byte-identical to E version; no E-F# fixes
PASS – 4 Traceability complete – 13/13 H-ids (15 rows), 1 ext, 8 dependencies (6 rows), 1 report-only row; counts shown; no blank cell without reason
PASS – 5 Only approved changes – 17/17 hunks → E001–E021 → P001–P021
PASS – 6 Input integrity – REQUEST_UNCHANGED; `-newer` check on SOURCE_ROOT/TARGET_ROOT printed nothing
PASS – 7 Handoff – paths, status, 7 review items (AUTO-DECIDED, ENABLE_GUARD, LAYOUT_RISK, drift, REPORT_ONLY), limitations
PASS – 8 Single report – one `PORT_REPORT.md`; REPORT_PATH / Created at unchanged
PASS – 9 Status row – F = Complete, Next approval gate = None
