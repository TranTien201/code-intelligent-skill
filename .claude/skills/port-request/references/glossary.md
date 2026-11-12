# Glossary (authoritative definitions)

| Term | Definition |
|---|---|
| **Request** | The change described by `SOURCE_REQUEST/Before/` → `SOURCE_REQUEST/After/`. |
| **Formula** | A unit of source *behavior* changed by the request: a computation, condition, constant/threshold, table entry, setting default, or call sequence. The output folder name `formula-source-*` and the *Formula Mapping Matrix* refer to mapping these units from source to target. One formula usually corresponds to one or more changed symbols. |
| **Hunk (`H###`)** | One `@@ ... @@` block of the source request diff. IDs are global across files, numbered in file order then hunk order. |
| **Modification point** | One contiguous run of `-` and/or `+` lines inside a hunk, belonging to one symbol. A hunk that spans two symbols yields two points. Manifest = one row per (symbol, modification point). |
| **Symbol** | Named code entity touched by a modification point. Kinds: `function`, `prototype`, `struct`, `union`, `enum`, `enum-const`, `typedef`, `macro`, `global`, `table` (initialized array/struct of entries, e.g. function-pointer registries), `preprocessor` (`#if/#ifdef` block), `file scope` (includes, pragmas, file-level comments). |
| **Function column value** | `<name> (<kind>)`, e.g. `Density_Scale (function)`, `NvData (struct)`, `DENSITY_MAX (macro)`, `g_menu_table (table)`. Static duplicates: `is_valid@src/panel/menu.c (function)`. Non-code file: `N/A (non-code file)`. Unknown: `Not identified`. |
| **Code file** | Extensions `.c .h .cc .cpp .cxx .hpp .hh .hxx .inc .ipp .s .S`. Everything else (Makefile, .mk, .txt, .xml, .json, .csv, binaries...) is a non-code file. |
| **file_status** | `added` = only in After; `deleted` = only in Before; `modified` = in both and different; `unknown` = cannot be compared (binary, unreadable). |
| **function_status** | `added` = symbol exists only on the After side of the file; `deleted` = only on the Before side; `modified` = on both sides; `unknown` = not identified or non-code. |
| **Outside-diff dependency** | A symbol used by request code (added lines) that is not itself changed by the request (e.g. a callee, macro, type, header, config define). The target may lack it. |
| **Incoming dependency** | Code outside the diff that uses a changed symbol: callers, registration tables, init sequences, NVRAM defaults. |
| **Latest source** | `SOURCE_ROOT`: the current source. The request diff is the *seed*; the code actually ported comes from latest source. |
| **Anchor result** (B) | Where a request file/symbol lives in latest source: `SAME_PATH` / `MOVED_FILE` / `SPLIT_FILE` (files); `SAME_NAME` / `MOVED_SYMBOL` / `RENAMED_SYMBOL` / `SPLIT_SYMBOL` / `MERGED_SYMBOL` (symbols); `MACRO_GENERATED` (name built by a macro); `REWRITTEN` (stable anchors still present, structure gone); `NOT_FOUND (removed|unknown)`. |
| **Request link graph** (A7) | `_work/A_links.md`: nodes (request symbols and data items) and typed edges between them (`calls`, `declares`, `registers`, `indexes`, `localizes`, `defaults`, `reads`, `writes`, `includes`, `builds`, `guards`, `uses-external`), each proven by a `REQ-A:path:line`. |
| **Node stability** | How likely a node's name survived later renames: `stable` (string literals/IDs, NVRAM keys, command keywords, build file names, guard macros), `medium` (types, fields, macros, tables, globals), `volatile` (functions, static helpers). B anchors stable nodes first. |
| **Anchor propagation** | Using an already anchored node to find a linked one: read the anchored end in latest source at the spot that plays the edge's role (call site, table slot, prototype order…) – recipe R12 L1. |
| **Link cross-check** | After both ends of an edge are anchored, the latest code must still show the relation under the latest names: `consistent` / `changed` / `broken`. |
| **Search method / signal** | How an anchor was found and what supports it: `NAME`, `ALIAS`, `EDGE`, `NEIGHBOR`, `FUZZY` (R16), `ANCHOR` (stable literals/IDs), `SIM` + `SIG` (R17), `PATTERN` (rename rule), `LLM` (hypothesis, never evidence alone). |
| **Fuzzy line match** (R16) | A request line searched as a regex where only feature identifiers are wildcards; finds lines whose callee/field names changed. |
| **Rename-invariant similarity** (R17) | Token-shingle containment of a reference body in a candidate after replacing every non-keyword identifier by a placeholder; literals and structure kept. Deterministic, no embeddings. |
| **Aliased request text** | REQ-A text with request names replaced by their latest names (`_work/B_aliased/`); used for latest state, hunk presence and evolution diffs so pure renames are not seen as changes. |
| **Latest state** (B) | `UNCHANGED_IN_LATEST` (= REQ-A), `EVOLVED` (changed after the request), `REMOVED_IN_LATEST` (request lines gone). Per hunk: `PRESENT` / `PARTIAL` / `GONE`. |
| **Evolution block** (B) | One change block between REQ-A body and latest body: `EXTENSION`, `BUGFIX`, `REFACTOR`, `UNRELATED`, `UNCLEAR` (rules: recipe R14). Drift = any `EVOLVED` item. |
| **Feature extension** | Code added to latest source after the request that belongs to the feature: `EXTENSION` blocks inside request symbols, and `EXTENSION_NEW` symbols elsewhere (new S-ids marked `ext`). Ported together with the request. |
| **Consumer** | Another feature in source that uses this feature. Never ported (`REPORT_ONLY`). |
| **Port version** | What is merged to the target for a symbol: latest body limited to request lines + `EXTENSION`/`BUGFIX`/`REFACTOR` blocks (without `UNRELATED` blocks). |
| **Data dependency** | Non-function item the feature needs: string/resource IDs and their per-language entries, enum entries and tables sized by them, settings fields + defaults + version/checksum, registry entries, config defines, data/resource files. |
| **Alias map** | `_work/alias_map.md`: request name/path → latest source name/path → target name/path, with evidence. Used to compare bodies "modulo aliases" and to adapt ported identifiers. |
| **Closure fixpoint** (C) | Dependencies are expanded repeatedly until no new item appears; a branch stops when the target already has it equal (modulo aliases). |
| **Target state** (Checkpoint C) | `SAME_AS_SOURCE` (equals the port version, possibly modulo aliases → already ported), `SAME_AS_BEFORE` (equals REQ-B → clean base), `DIVERGED` (exists, differs from both), `SIGNATURE_DIFF` (different params/return/fields), `MISSING`, `RENAMED` (other name/file, ≥ Medium evidence), `RENAMED_CANDIDATE` (weak evidence). Comparison ignores whitespace only. |
| **Confidence** | `High` = located by exact name and the bodies were compared; `Medium` = located but by partial match (different file, diverged body, anchor lines only); `Low` = inferred without direct evidence (rename candidates, naming similarity). For renames/moves the signal rules in recipe R12 apply (relation + content signal → High; 2 signals of different families → Medium; single or naming-only signal → Low). Every `Low` must appear in Blockers with a question. |
| **Port class** (Checkpoint D) | See `decision-table.md`. |
| **Target request-label convention** | An existing, consistent way the target marks request changes in code (e.g. `/* REQ-1234 */`, `// [CR#0123] start/end`). Applied only if found with evidence (≥3 consistent occurrences); otherwise `None found` and no labels are added. |
| **Approval** | See SKILL.md §5. |
