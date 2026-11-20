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
