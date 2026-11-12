# Checkpoint A – Source Request Snapshot Comparison

**Goal:** an exact, complete inventory of what the request changed: files → hunks → modification
points → symbols, with line-level before/after content.
**Reads:** `SOURCE_REQUEST/Before/`, `SOURCE_REQUEST/After/` (and nothing else).
**Writes:** `diffs/source/**`, `_work/A_files.txt`, `_work/A_ranges/**`, `_work/A_hunks.md`, report section A.
**Load:** `references/c-cpp-search-recipes.md` (R0, R1, R2), `references/report-template.md`.

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

### A7 – Fill the report
1. `### Changed File Manifest`: one row per modification point, in `_work/A_hunks.md` order, `No`
   sequential. Repeat `file` and `function` for several points in the same symbol. Non-code files:
   one row per file with `N/A (non-code file)` | `unknown` | `N/A` | `N/A`. Column formats are in
   `report-template.md`. Write the `manifest No` back into `_work/A_hunks.md`.
2. `### Line-Level Changes`: per code file, the A6 pairs.
3. Run `gates/A.md`, write `### Gate Result`, update Workflow Status (SKILL.md §4).

## Stop message
```
Checkpoint A <Complete|Blocked>.
Files: <n> (added a / modified m / deleted d, non-code k) · Hunks: <h> · Manifest rows: <r>
Not identified: <list or none> · Gate: <p>/<t> PASS
Report: <REPORT_PATH>
Reply "approve B" to start Checkpoint B (source change analysis).
```
