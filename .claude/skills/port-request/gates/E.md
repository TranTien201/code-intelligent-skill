# Gate E

1. **Before identical** – `diff -rq -x .git "$TARGET_ROOT" "$OUTPUT_ROOT/Before"` prints nothing.
2. **Every P applied** – every P-id has exactly one E-id with status `applied`, or `skipped` + reason + blocker.
3. **No unplanned change** – every hunk in `diffs/output.diff` maps to an E-id (show hunk count vs mapped count).
4. **Files** – set of files in `git diff --no-index --name-only Before After` (or `diff -rq Before After`) == files in `### Output File Manifest`.
5. **Verbatim** – for E-ids with adaptation `none`, the inserted text equals the D text (`diff -w` on the extracted lines).
6. **Encoding / EOL** – `file -I` and CRLF status of every modified file are unchanged versus `Before/`.
7. **Labels** – applied only if D found a convention, in exactly that format.
8. **No validation run** – no build/test commands were executed in E.
9. **Read-only inputs** – marker check on `SOURCE_ROOT`, `TARGET_ROOT`, `SOURCE_REQUEST` prints nothing.
10. **Status row** updated.
