# Checkpoint F – Validation and Handoff

**Goal:** prove the port builds/works as far as the project allows, prove that only approved changes
exist, prove inputs were not modified, and hand off clearly.
**Reads:** `OUTPUT_ROOT/Before|After`, all `_work` files, the report.
**Writes:** `_work/F_validation.md`, build artifacts only inside `OUTPUT_ROOT/Before|After`, report section F.

## Steps

### F1 – Determine the command
Use `BUILD_CMD` or the command from D's Validation Plan. If it is still unclear (several candidates, needs
toolchain/env you cannot confirm): interactive → ask before running and before claiming success;
auto → run the best candidate and label the result `UNCONFIRMED COMMAND`.

### F2 – Baseline and validation runs
Run the same command in `OUTPUT_ROOT/Before` (baseline) and `OUTPUT_ROOT/After`. Save trimmed output
(command, exit code, last ~40 lines, every error/warning line mentioning a ported file) to `_work/F_validation.md`.
- After fails but Before passes → port problem: analyse the errors, map missing symbols with R2/R3. Fixes are
  **not** made silently: interactive → propose and ask (approved fixes get new ids `P-F#`/`E-F#`, are
  applied to `After/` only, and are listed in F's Validation section; D/E sections stay frozen); auto → at most 2 fix rounds restricted to plan-consistent fixes
  (missing include/declaration/dependency copy), each flagged `AUTO-DECIDED`.
- Both fail the same way → environment/pre-existing issue; do not claim validation, record it.
- No build possible → fallback from D (`-fsyntax-only` per changed file with include paths, symbol resolution
  greps). Label clearly as `partial validation`.
Run related tests found in B7 if runnable.

### F3 – Before/After comparison
Regenerate `diffs/output.diff`; confirm it equals E's version (no change since E). Confirm every hunk maps
to an E-id and every E-id to an approved P-id.

### F4 – Traceability
Build `### Traceability Matrix`: one row per H-id, per `ext` S-id and per dependency S###.d# (code and data): H → S → M → P → E → output hunk →
result (`ported`, `ported (ext)`, `already present`, `skipped: <class/reason>`, `report only`, `blocked`). No empty cell without a reason.

### F5 – Input integrity
```bash
(cd "$SOURCE_REQUEST" && find Before After -type f -exec shasum {} +) | diff - "$OUTPUT_ROOT/_work/input_baseline.txt" && echo REQUEST_UNCHANGED
find "$SOURCE_ROOT" "$TARGET_ROOT" -newer "$OUTPUT_ROOT/_work/.start_marker" -type f -not -path '*/.git/*' | head
```
The second command must print nothing (if it prints files, report them – they may be changes by someone else; do not claim integrity).

### F6 – Write the report
- `### Validation Commands and Results`: `| Where | Command | Exit | Result |` + key error lines.
- `### Before/After Comparison`: F3 result.
- `### Traceability Matrix`.
- `### Limitations and Tests Not Run`: everything not validated and why, `partial validation`, `UNCONFIRMED COMMAND`.
- `### Final Handoff`: output paths (`OUTPUT_ROOT`, `After/`, `diffs/output.diff`, report), validation status
  (`Validated` / `Partially validated` / `Not validated`), decisions for human review (CONFLICT choices,
  AUTO-DECIDED items, ENABLE_GUARD, LAYOUT_RISK, drift, REPORT_ONLY list), next steps.
Run `gates/F.md`, write `### Gate Result`, update Workflow Status (F → `Complete`, next gate `None`).

## Final message
```
Port <TARGET_REQUEST_ID>: <Validated|Partially validated|Not validated|Blocked>
After: <path> · Diff: <path> · Report: <path>
Build: Before <exit> / After <exit> · Tests: <run/not run>
Traceability: <n> hunks → ported p, already present a, skipped s, report-only r, blocked b
Needs human review: <list>
```
