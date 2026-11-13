# Checkpoint A – Source Request Snapshot Comparison

**Goal:** an exact, complete inventory of what the request changed: files → hunks → modification
points → symbols, with line-level before/after content.
**Reads:** `SOURCE_REQUEST/Before/`, `SOURCE_REQUEST/After/` (and nothing else).
**Writes:** `diffs/source/**`, `_work/A_files.txt`, `_work/A_ranges/**`, `_work/A_hunks.md`, `_work/A_links.md`, report section A.
**Load:** `references/c-cpp-search-recipes.md` (R0, R1, R2, R15), `references/report-template.md`.

## Steps

### A1 – Prepare
Set Workflow Status row A: `In progress`, approval `Not required`. Clear the Checkpoint A body
(keep its sub-headings), delete old `diffs/source/` and `_work/A_*`.

### A2 – File list
```bash
cd "$SOURCE_REQUEST" && diff -rq Before After
```
Normalise into `_work/A_files.txt` as `<file_status>\t<relative path>`:
`Only in After…` → `added`; `Only in Before…` → `deleted`; `Files … differ` → `modified`.
For `Only in` lines that name a **directory**, expand to every file below it (`find`).
Exclude nothing silently: if you skip a file (e.g. `.DS_Store`), list it under Gate Result with the reason.
Record per file: code/non-code (glossary), encoding (`file -I`), line endings (`file` shows CRLF).
Whitespace/line-ending-only differences are still `modified`; note them as `cosmetic`.

### A3 – Per-file diff
For each file run R0 and save to `diffs/source/<relative path>.diff` (mirror the folder structure).
Also keep the `-U0` output in mind for exact line numbers. Non-UTF-8 code files: diff the bytes as
is, but read through `iconv` copies placed in `_work/` when you need to understand content.

### A4 – Symbol ranges
For each code file run R1 on the Before side and the After side (when they exist); save to
`_work/A_ranges/<path>.before.txt` / `.after.txt`. Fix multi-line signatures by reading the lines above
the reported header.

### A5 – Hunks, modification points, symbols
For each hunk (in file order) assign `H001…`. Inside the hunk, split runs of changed lines into
modification points; split again wherever the owning symbol changes. For each point:
- `-` lines → owner from the **Before** ranges; `+` lines → owner from the **After** ranges.
  **Never take the owner from the text after `@@ … @@`**: git prints the nearest preceding
  function-like line, which is often wrong for tables/structs (e.g. it shows `Pjl_SetDuplex` for a change
  inside `g_pjl_table`).
- Outside every range → classify with R2 patterns (`macro`, `prototype`, `global`, `enum-const`,
  `preprocessor`, `file scope`). If still unclear → `Not identified`.
- `function_status`: owner exists on both sides → `modified`; only After → `added`; only Before → `deleted`;
  `Not identified` or non-code → `unknown`.
- Static name present in several files → `name@path`.
Write every point into `_work/A_hunks.md` (schema in `work-artifacts.md`).

### A6 – Line pairing (for `Line-Level Changes` and manifest cells)
Within each modification point, take the `-` lines in order and the `+` lines in order, and pair them
by position: the 1st `-` with the 1st `+`, the 2nd with the 2nd, and so on. If one side has more lines,
put the extra lines on their own rows with the other cell blank. Never pair lines across points or hunks.
Context (unchanged) lines are never shown. Prefix each cell with its line number: `L42: <text>`.

### A7 – Request link graph (how the changed pieces connect)
The hunks of one request are almost never independent. Record how they connect, **from the request alone**
(REQ-A for added/modified items, REQ-B for deleted ones), so Checkpoint B can trace the easy, stable pieces
first and then *walk the links* to the pieces that were renamed or moved (anchor propagation).
Use recipe R15. Write `_work/A_links.md` (schema in `work-artifacts.md`).
1. **Nodes** – one per symbol owning a modification point (`A_hunks.md`), plus every data item the request
   adds or edits (string/resource ID, enum entry, settings/NVRAM field, config/guard macro, table entry) and every
   changed non-code file. Node id = `N###`; give its S-name, kind, `def at` (`REQ-A:path:line`) and H-ids.
2. **Stability** of each node (how likely its *name* survived later renames; B uses it as trace order):
   `stable` = string literals, string/resource IDs, NVRAM/settings keys, PJL/command keywords, enum values used
   as IDs, file names in build files, guard macros; `medium` = types, struct fields, macros, tables, globals,
   headers; `volatile` = functions and file-static helpers. When unsure choose the less stable class.
3. **Edges** `from –type→ to`, each with `REQ-A:path:line` of the line that proves it. Types: `calls`,
   `declares` (prototype/extern ↔ definition), `registers` (table entry ↔ handler/ID), `indexes` (enum ↔ array or
   switch over it), `localizes` (string ID ↔ language table entry), `defaults` (settings field ↔ default/reset),
   `reads`/`writes` (function ↔ field/global), `includes`, `builds` (build file ↔ source file), `guards`
   (macro ↔ guarded block), `uses-external` (request symbol → unchanged symbol outside the request, e.g. a system
   API: such targets rarely change and become anchors in B).
   Endpoints outside the request are allowed (node kind `external`, def `outside request`).
4. Nodes with no edge at all → `isolated` (list them; B traces them only by content).
5. Components: group connected nodes (`C1`, `C2`…). Several components = the request touches several
   loosely related places; note it for the reviewer.

### A8 – Fill the report
1. `### Changed File Manifest`: one row per modification point, in `_work/A_hunks.md` order, `No`
   sequential. Repeat `file` and `function` for several points in the same symbol. Non-code files:
   one row per file with `N/A (non-code file)` | `unknown` | `N/A` | `N/A`. Column formats are in
   `report-template.md`. Write the `manifest No` back into `_work/A_hunks.md`.
2. `### Line-Level Changes`: per code file, the A6 pairs.
3. `### Request Links`: summary counts, then the graph and the edge table generated from `_work/A_links.md`
   (format in `report-template.md`):
   ```bash
   python3 -I "$SK/scripts/links_view.py" --links "$W/A_links.md" --out "$W/A_links.mmd"   # paste its output
   ```
   No `python3` → the summary and the edge table only (copy the edge rows of `A_links.md`).
4. Run `gates/A.md`, write `### Gate Result`, update Workflow Status (SKILL.md §4).

## Stop message
```
Checkpoint A <Complete|Blocked>.
Files: <n> (added a / modified m / deleted d, non-code k) · Hunks: <h> · Manifest rows: <r>
Links: <n> nodes (stable s / medium m / volatile v) · <e> edges · components <c> · isolated: <list or none>
Not identified: <list or none> · Gate: <p>/<t> PASS
Report: <REPORT_PATH>
Reply "approve B" to start Checkpoint B (source change analysis).
```
