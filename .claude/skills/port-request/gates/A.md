# Gate A (all must PASS before status `Complete`)

Write each result to `### Gate Result` as `PASS|FAIL – <item> – <evidence>`.

1. **File count** – number of files in `_work/A_files.txt` (after directory expansion, minus listed exclusions)
   == number of distinct `file` values in the manifest. Show both numbers.
2. **Diff files** – every changed file has `diffs/source/<path>.diff` (non-empty).
3. **Hunk count** – `grep -c '^@@' diffs/source/**/*.diff` total == number of distinct H-ids in `_work/A_hunks.md`.
4. **Hunk coverage** – every H-id has ≥1 manifest row (`manifest No` filled); every manifest row of a code file traces to an H-id.
5. **Point coverage** – sum of `-` and `+` lines over all points == added/deleted line totals from `git diff --no-index --numstat Before After` (or the `diff -ruN` fallback in R0) for text files.
6. **Vocabulary** – `file_status` and `function_status` only `added|modified|deleted|unknown`; function values follow `<name> (<kind>)`, `N/A (non-code file)` or `Not identified`.
7. **Consistency** – `file_status=added` rows have `Modified_line_before = N/A`; `deleted` rows have `Modified_line_after = N/A`; non-code rows use `N/A (non-code file) | unknown | N/A | N/A`.
8. **Not identified** – each `Not identified` row has a reason in Gate Result (no silent unknowns).
9. **Template** – manifest header line equals the one in `references/report-template.md` exactly; rows numbered 1..n without gaps.
10. **Line-Level Changes** – one subsection per changed code file; no unchanged (context) lines; unmatched lines have a blank opposite cell.
11. **Inputs untouched** – no file was written outside `OUTPUT_ROOT` (`find "$SOURCE_REQUEST" -newer "$OUTPUT_ROOT/_work/.start_marker" -type f` prints nothing).
12. **Status row** – A = `Complete`, Next approval gate = `Awaiting Checkpoint B approval` (or `Blocked: …`).
