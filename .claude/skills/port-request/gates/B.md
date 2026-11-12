# Gate B

1. **Files** – every manifest file appears in `### Files Analyzed` as `analyzed` or `skipped (reason)`.
2. **Symbol coverage** – every H-id of `_work/A_hunks.md` belongs to ≥1 S-id; every S-id lists its H-ids (or `ext`).
3. **Behavior** – every S-id with change type ≠ `cosmetic` has a concrete before → after sentence (values/conditions named).
4. **Anchoring complete** – every changed file, every node of `_work/A_links.md`, every S-id and every H-id has an anchor result + latest state in `_work/B_anchor.md` (show counts A vs B).
5. **Method and signals** – every anchor names its method (`NAME / ALIAS / EDGE / NEIGHBOR / FUZZY / ANCHOR / SIM / PATTERN / LLM`) and lists its signals with `SRC:path:line` (and R17 scores where used); the confidence follows R12's signal rules (no history exists). `NAME` anchors were verified as the same thing (kind + body), not just a name hit. An anchor supported only by `LLM`/`PATTERN` is `Low`.
6. **Relocation evidence** – every `MOVED_*`/`RENAMED_*`/`SPLIT_*`/`MERGED_*` is in `_work/alias_map.md`; every rename rule used by L5 is recorded as `kind = pattern`.
7. **Links cross-checked** – every `A_links.md` edge whose two ends are anchored has `consistent` / `changed` / `broken` (counts shown); every `broken` edge downgraded an anchor and is listed as a risk.
8. **Loop finished** – the iteration log is written and the last iteration anchored 0 new nodes; `#### Anchored Link Graph` is in the report (generated from the final `B_anchor.md`).
9. **No silent loss** – every `NOT_FOUND`, `REWRITTEN`, `MACRO_GENERATED`, `REMOVED_IN_LATEST`, hunk `GONE`/`PARTIAL`, and `Low` anchor is a blocker with a question; every `NOT_FOUND` lists the R12 L7 checks run (macro, encoding, split/merge, rewrite, removal).
10. **Modulo aliases** – latest state and hunk presence were computed on the aliased request text (`_work/B_aliased/`, B2.6) after the alias map was complete; lines matched only after aliasing or by R16 are marked.
11. **Evolution** – every `EVOLVED` item has each change block classified (R14) on the aliased diff; `UNCLEAR` blocks are blockers; partial takes listed.
12. **Extensions searched** – B4 searches (feature symbols by **latest** names, guard macros, request and latest naming prefixes, stable anchors) were run and recorded with the patterns, even if nothing was found; each hit classified `EXTENSION_NEW` / `CONSUMER` / `UNCLEAR`.
13. **Tokens** – `_work/B_new_tokens.txt` built from request `+` lines **and** extension lines; every project token is an S-id, a dependency, or listed as standard/library (counts).
14. **Code dependency evidence** – every outgoing dependency has `SRC:path:line` or a blocker `definition not found`; recursion depth/stop reason stated.
15. **Data dependencies** – R13 checklist run for every string ID, enum entry, settings field, registry entry and config macro in the port version; findings or `none` per kind.
16. **Incoming / guards / headers / tests** – recorded per S (or `none found` with the command).
17. **Read-only** – `find "$SOURCE_ROOT" "$SOURCE_REQUEST" -newer "$OUTPUT_ROOT/_work/.start_marker" -type f -not -path '*/.git/*'` prints nothing.
18. **Status row** updated.
