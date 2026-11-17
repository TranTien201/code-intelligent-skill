# F_validation

## Build (BUILD_CMD given → confirmed command)
| Where | Command | Exit | Output (trimmed) |
|---|---|---|---|
| OUTPUT_ROOT/Before | `make -s MODEL=B` | 0 | no output (no warnings with -Wall) |
| OUTPUT_ROOT/After | `make -s MODEL=B` | 0 | no output (no warnings with -Wall) |
| OUTPUT_ROOT/Before | `./printer_B` | 0 | copies=2 / toner_save=-1 / pjl=-1 / [INFO] render start / [INFO] render done / [INFO] fax header / density=10 |
| OUTPUT_ROOT/After | `./printer_B` | 0 | copies=2 / [INFO] Toner Save / toner_save=2 / [INFO] Toner Save / pjl=1 / [INFO] render start / [INFO] render done / [INFO] fax header / density=8 |
Interpretation: After – menu TONER_SAVE accepted level 2, PJL ECONOMODE=1 set level 1 (LOW, 80 %) → Render_Page(10) = Density_Scale(10, 80) = 8; FAX behavior preserved.

## Diff stability
`git diff --no-index Before After` regenerated; after removing build artifact `printer_B` (binary in both trees) it is byte-identical to the E version (`cmp` → DIFF_STABLE). `diffs/output.diff` unchanged.

## Integrity
REQUEST_UNCHANGED (sorted shasum vs `_work/input_baseline.txt`; unsorted compare differed only by `find` ordering). `find SOURCE_ROOT TARGET_ROOT -newer .start_marker` → nothing.
