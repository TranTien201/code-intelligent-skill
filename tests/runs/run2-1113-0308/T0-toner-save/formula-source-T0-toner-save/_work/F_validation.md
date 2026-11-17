# F_validation

## Commands
| Where | Command | Exit | Output (trimmed) |
|---|---|---|---|
| OUT-B (`Before/`) | `make -s MODEL=B` | 0 | no output (no warnings) |
| OUT-B | `./printer_B` | 0 | `copies=2` · `toner_save=-1` · `pjl=-1` · `[INFO] render start` · `[INFO] render done` · `[INFO] fax header` · `density=10` |
| OUT-A (`After/`) | `make -s MODEL=B` | 0 | no output (no warnings with `-Wall`) |
| OUT-A | `./printer_B` | 0 | `copies=2` · `[INFO] Toner Save` · `toner_save=2` · `[INFO] Toner Save` · `pjl=1` · `[INFO] render start` · `[INFO] render done` · `[INFO] fax header` · `density=8` |

Build outputs `printer_B` removed from both snapshots after the runs.

## Diff / integrity
- `diffs/output.diff` regenerated after cleanup: byte-identical to the E version (DIFF_STABLE); Before still identical to TARGET_ROOT.
- `shasum` of SOURCE_REQUEST Before/After == `_work/input_baseline.txt` → REQUEST_UNCHANGED.
- `find SOURCE_ROOT TARGET_ROOT -newer .start_marker -type f` → nothing.

## Traceability
See report `### Traceability Matrix` (13 H rows + 8 dependency rows).
