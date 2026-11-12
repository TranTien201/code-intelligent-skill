# Checkpoint D – Formula Mapping and Plan

**Goal:** a complete, executable plan: every source behavior mapped to a target action, with the
exact text to write, so that Checkpoint E only executes.
**Reads:** `_work/B_symbols.md`, `_work/C_trace.md`, C's user answers, narrow reads of inputs.
**Writes:** `_work/D_plan.md`, report section D. **Does not create `Before/` or `After/`.**
**Load:** `references/decision-table.md`, `references/c-cpp-search-recipes.md` (R9, R10).

## Steps

### D1 – Mapping
For every S-id (incl. `ext`), code dependency and data dependency from C, apply `decision-table.md` (first matching
row) → `M###` with port class. Data dependencies need one P-id per place (each language table, each enum-sized table,
default table, version/checksum). Group by formula (behavior). Unresolved `NEEDS_CONFIRMATION`/`CONFLICT`/`UNCLASSIFIED`
→ interactive: ask and stop (record answers); auto: default rule + `AUTO-DECIDED`.

### D2 – Label convention
Run R10 on the target. Found (≥3 consistent occurrences) → describe the format with 3 evidence lines
and how `TARGET_REQUEST_ID` will be applied. Not found → `None found (searched: <pattern>)`; no labels will be added.

### D3 – Planned changes
For each M that needs a change, one or more `P###`:
- target file (repository-relative), action (`add-file`, `insert`, `replace`, `delete`, `apply-hunk`,
  `add-define`, `add-include`, `add-registration`, `add-to-build`),
- anchor: the exact existing target text (2–3 lines, copied from `TGT:path:line`) around which the change goes,
- content source (the port version `SRC:path:lines`, or `REQ-A:path:lines` only if decision row 1 chose it), and the **full new
  text** in `_work/D_plan.md` – already with alias substitutions (`ALIAS_ADAPT`) and partial-take exclusions applied,
- adaptation (`none` or exact description), label (per D2).
Order P-ids so headers/types/macros come before their users. Check: new source files have an `add-to-build` P-id.

### D4 – Output snapshot plan
State: target snapshot scope = full `TARGET_ROOT` copy excluding `.git` and build outputs (needed so F can build);
whether `OUTPUT_ROOT/Before|After` already exist and will be **replaced** by E.

### D5 – Validation plan
From R9: the build/test command(s) for the target (or `BUILD_CMD`), where to run them (`OUTPUT_ROOT/After`,
and `OUTPUT_ROOT/Before` as baseline), expected evidence, fallback if no build is possible
(`<cc> -fsyntax-only` with the include paths from the build files; header/symbol resolution checks). If the
command is unclear → question for the user.

### D6 – Write the report
- `### Formula Mapping Matrix`, `### Target Request-Label Convention`, `### Planned Changes` (formats in
  `report-template.md`), `### Validation Plan`, `### Risks` (layout, drift, adaptations, AUTO-DECIDED items,
  target behavior that might change), `### Blockers`.
Run `gates/D.md`, write `### Gate Result`, update Workflow Status.

## Stop message
```
Checkpoint D <Complete|Blocked>.
Mappings: <n> (APPLY_PORT_VERSION a, COPY_NEW c (ext: <k>), COPY_DEPENDENCY d, ADD_DATA t, ALIAS_ADAPT l, ADAPT_MERGE h, ENABLE_GUARD g, SKIP s, REPORT_ONLY r, …)
Scope beyond request (extensions from latest source): <list or none>
Planned changes: <p> in <f> files · Adaptations: <list or none> · Labels: <convention or none>
Validation: <command> · Existing output snapshots will be replaced: <yes/no>
Decisions needed: <list or none>
Reply "approve E" to create the snapshots and implement exactly this plan.
```
