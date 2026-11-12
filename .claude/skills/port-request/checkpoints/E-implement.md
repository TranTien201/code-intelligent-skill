# Checkpoint E – Before/After Implementation

**Goal:** create the output snapshots and apply exactly the approved plan to `After/` – nothing more.
**Reads:** `_work/D_plan.md`, `TARGET_ROOT` (copy source), `SOURCE_REQUEST/After`, `SOURCE_ROOT` (content sources).
**Writes:** `OUTPUT_ROOT/Before/`, `OUTPUT_ROOT/After/`, `diffs/output.diff`, `_work/E_changes.md`, report section E.
**Does not build or run tests** (that is F). Structural self-checks below are allowed.

## Steps

### E1 – Snapshots
If D said existing snapshots will be replaced, delete only `OUTPUT_ROOT/Before` and `OUTPUT_ROOT/After`
(verify the paths start with `OUTPUT_ROOT` before deleting). Then:
```bash
rsync -a --exclude='.git' "$TARGET_ROOT"/ "$OUTPUT_ROOT/Before"/
rsync -a --exclude='.git' "$TARGET_ROOT"/ "$OUTPUT_ROOT/After"/
diff -rq "$TARGET_ROOT" "$OUTPUT_ROOT/Before" -x .git && echo BEFORE_IDENTICAL
```
Never edit `Before/` after this point.

### E2 – Apply planned changes, in P-id order
For each P-id, edit only the file under `OUTPUT_ROOT/After/`:
- Locate the anchor text exactly. If it is not found exactly once → do not improvise: mark the P `skipped
  (anchor not found)` and add a blocker.
- Insert/replace with the full new text from `_work/D_plan.md`, verbatim (plus the D2 label if any).
- `ADAPT_MERGE` (and optionally `APPLY_PORT_VERSION`): symbol-level 3-way merge –
  ```bash
  # base = REQ-B body, ours = target body (from After/), theirs = port version (from D_plan), each extracted to _work/merge/
  git merge-file -p _work/merge/ours.txt _work/merge/base.txt _work/merge/theirs.txt > _work/merge/result.txt; echo "conflicts=$?"
  ```
  `git merge-file` needs no repository. Do **not** substitute `diff3 -m` (wrong merges on macOS). Without `git`:
  apply the planned anchor-based edit; if any anchor of the request lines is missing in the target body → treat
  as conflict.
  `conflicts=0` → put `result.txt` in place of the target body. `>0` → do not hand-resolve silently: mark the P
  `skipped (merge conflict)` + blocker (interactive: show the conflict and ask).
- `add-file`: copy the file from the content source byte-for-byte (`cp -p`), then apply other P-ids to it if planned.
- Preserve encoding and line endings: check `file -I` before/after the edit; for non-UTF-8 files edit via
  `iconv` into `_work/`, edit, convert back, and confirm with `file -I` and a diff that only planned lines changed.
- Record `E###` in `_work/E_changes.md` with resulting `OUT-A:path:lines`.

### E3 – Output diff and self-check
```bash
cd "$OUTPUT_ROOT" && git diff --no-index --no-color -U3 Before After > diffs/output.diff; git diff --no-index --stat Before After
# without git: diff -ruN Before After > diffs/output.diff; diff -rq Before After
```
Map every hunk of `diffs/output.diff` to an E-id. A hunk with no E-id = unplanned change → revert it.
A P-id with no hunk (and not `skipped`) = not applied → fix.

### E4 – Write the report
- D's section is frozen (never edit it). First line of `### Exact Changes`:
  `Executing plan approved by: <E approval text>`.
- `### Output File Manifest`, `### Exact Changes` (formats in `report-template.md`).
- `### Diff Summary`: `--stat` totals + one line per file.
- `### Blockers`: skipped P-ids, encoding issues, anything that deviated.
Run `gates/E.md`, write `### Gate Result`, update Workflow Status.

## Stop message
```
Checkpoint E <Complete|Blocked>.
Snapshots: Before (identical to target: yes) · After: <f> files changed, +<a>/-<d> lines
Applied: <n>/<p> P-ids · Skipped: <list or none> · Unplanned hunks: 0
Output diff: <OUTPUT_ROOT>/diffs/output.diff
Reply "approve F" to validate and hand off.
```
