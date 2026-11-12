# Gate F

1. **Commands recorded** – every validation command with directory, exit code and result; Before baseline included.
2. **Honest status** – `Validated` only if After build (and runnable tests) succeeded with a confirmed command; otherwise `Partially validated` / `Not validated` with reasons.
3. **Diff stable** – `diffs/output.diff` matches the E version, except approved `E-F#` fixes, which are listed.
4. **Traceability complete** – every H-id and dependency has a full row; no blank cell without a reason; counts per result type shown.
5. **Only approved changes** – every output hunk → E-id → approved P-id (or approved `P-F#`).
6. **Input integrity** – `REQUEST_UNCHANGED` printed and the `-newer` check printed nothing (or the files are reported).
7. **Handoff** – paths, validation status, human-review list (CONFLICT, AUTO-DECIDED, ENABLE_GUARD, LAYOUT_RISK, drift, REPORT_ONLY), limitations, tests not run.
8. **Single report** – only one `PORT_REPORT.md` under `OUTPUT_ROOT` (`find "$OUTPUT_ROOT" -name '*REPORT*'`); Run Metadata `REPORT_PATH` / `Created at` unchanged.
9. **Status row** – F = `Complete`, Next approval gate = `None`.
