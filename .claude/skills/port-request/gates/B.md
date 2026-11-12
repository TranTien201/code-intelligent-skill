# Gate B

1. **Files** – every manifest file appears in `### Files Analyzed` as `analyzed` or `skipped (reason)`.
2. **Symbol coverage** – every H-id of `_work/A_hunks.md` belongs to ≥1 S-id; every S-id lists its H-ids (or `ext`).
3. **Behavior** – every S-id with change type ≠ `cosmetic` has a concrete before → after sentence (values/conditions named).
4. **Anchoring complete** – every changed file, every S-id and every H-id has an anchor result + latest state in `_work/B_anchor.md` (show counts A vs B).
5. **Relocation evidence** – every `MOVED_*`/`RENAMED_*`/`SPLIT_*`/`MERGED_*` lists the content signals used (R11/R12; no history exists) and a confidence matching R12's rules; all are in `_work/alias_map.md`.
6. **No silent loss** – every `NOT_FOUND`, `REMOVED_IN_LATEST`, hunk `GONE`/`PARTIAL`, and `Low` anchor is a blocker with a question.
7. **Evolution** – every `EVOLVED` item has each change block classified (R14); `UNCLEAR` blocks are blockers; partial takes listed.
8. **Extensions searched** – B4 searches (feature symbols, guard macros, naming prefix) were run and recorded with the patterns, even if nothing was found; each hit classified `EXTENSION_NEW` / `CONSUMER` / `UNCLEAR`.
9. **Tokens** – `_work/B_new_tokens.txt` built from request `+` lines **and** extension lines; every project token is an S-id, a dependency, or listed as standard/library (counts).
10. **Code dependency evidence** – every outgoing dependency has `SRC:path:line` or a blocker `definition not found`; recursion depth/stop reason stated.
11. **Data dependencies** – R13 checklist run for every string ID, enum entry, settings field, registry entry and config macro in the port version; findings or `none` per kind.
12. **Incoming / guards / headers / tests** – recorded per S (or `none found` with the command).
13. **Read-only** – `find "$SOURCE_ROOT" "$SOURCE_REQUEST" -newer "$OUTPUT_ROOT/_work/.start_marker" -type f -not -path '*/.git/*'` prints nothing.
14. **Status row** updated.
