# Checkpoint B – Source Change Analysis (anchor in latest source + feature closure)

**Goal:** starting from the request diff, trace back into `SOURCE_ROOT` (latest source), find where
every piece of the request lives *now* (even if files or functions were moved or renamed), find how the
feature was **extended** after the request, and collect the full closure of code **and data** the feature
needs. The result is the *port version* of the feature: what will be merged to the target.
**Reads:** `_work/A_hunks.md`, `diffs/source/**`, `SOURCE_REQUEST/Before|After`, `SOURCE_ROOT` (search and
narrow reads; plain folder, no history – everything is inferred from content).
**Writes:** `_work/B_anchor.md`, `_work/alias_map.md`, `_work/B_new_tokens.txt`, `_work/B_symbols.md`, report section B.
**Load:** `references/c-cpp-search-recipes.md` (R1–R7, R9, R11–R14), `references/glossary.md`.

## Steps

### B1 – Changed symbols (request view)
From `_work/A_hunks.md` create one `S###` per distinct symbol (several H-ids may share one S). For each,
read its REQ-B and REQ-A bodies and record `change type` and behavior `before → after` (concrete values,
conditions, parameters). For `layout` changes list members/enum values whose offset or value shifts.

### B2 – Anchor every request item in latest source
Do this for every changed **file** first, then every **S-id**, then every **hunk**.
1. **File** – same path exists in `SOURCE_ROOT`? If not → R11 (same basename, include sites,
   content similarity). Result: `SAME_PATH` / `MOVED_FILE <new path>` / `SPLIT_FILE <paths>` / `NOT_FOUND`.
2. **Symbol** – look for the same name in the anchored file(s), then repo-wide (R2). Not found → R12
   (compat alias/wrapper, caller anchor, neighbor anchor, signature shape, body similarity, distinctive literals). Result:
   `SAME_NAME` / `MOVED_SYMBOL` (same name, other file) / `RENAMED_SYMBOL <new name>` / `SPLIT_SYMBOL` /
   `MERGED_SYMBOL` / `NOT_FOUND`, with evidence and confidence (glossary).
3. **Latest state** – compare REQ-A body vs latest body (R7):
   `UNCHANGED_IN_LATEST` / `EVOLVED` / `REMOVED_IN_LATEST` (the request's `+` lines are no longer there:
   check each distinctive `+` line with `grep -F` in the anchored body).
4. **Hunk** – for each H-id: `PRESENT` (all its `+` lines exist in latest), `PARTIAL`, `GONE`.
5. Write `_work/B_anchor.md` and add every renamed/moved symbol or file to `_work/alias_map.md`
   (`request name/path → latest name/path`).
Any `NOT_FOUND`, `REMOVED_IN_LATEST`, `GONE` or `Low` confidence anchor → blocker with a question.

### B3 – Classify later evolution (only `EVOLVED` items)
Diff the REQ-A body against the latest body. For each later change block apply R14:
`EXTENSION` (feature grew: related to feature tokens/lines/guard), `REFACTOR` (rename/format/move of
feature lines), `BUGFIX` (fix to feature lines), `UNRELATED` (another feature or unrelated refactor in the
same function), `UNCLEAR`. Record per block with `SRC:path:line`. `UNCLEAR` → blocker.

### B4 – Discover feature extensions outside the request's symbols
The feature may have grown into new places after the request. Search latest source for:
- every use of the feature's symbols/macros/strings outside the anchored symbols (R3),
- code under the feature's guard macro(s) (R5 inverse: `grep -n "<GUARD>"` then read the blocks),
- symbols with the feature's naming prefix (`grep -rnw -E "<Prefix>[A-Za-z0-9_]*"`), new files referencing them.
Classify each hit: `EXTENSION_NEW` (belongs to the feature itself: inside its guard, in its files, named with its
prefix, or only reachable from the feature) / `CONSUMER` (another feature uses this one → `REPORT_ONLY` later) /
`UNCLEAR` (blocker). `EXTENSION_NEW` items get new S-ids marked `ext`.

### B5 – Port version and outgoing closure (code + data)
*Port version* of each S = latest body restricted to: request lines + `EXTENSION`/`REFACTOR`/`BUGFIX`
blocks (exclude `UNRELATED`). Note when the latest body mixes in `UNRELATED` blocks: partial take.
1. R4 on the port version text (request `+` lines **and** extension lines from latest) → `_work/B_new_tokens.txt`.
2. For each project token: is it an S-id? Otherwise find its definition in `SOURCE_ROOT` latest (R2) → dependency
   `S###.d#` with kind and `SRC:path:line`.
3. **Data dependencies** (R13): string IDs + every language table entry, enum entries + all arrays indexed or
   sized by that enum, settings/NVRAM fields + default tables + reset/init + version/migration/checksum,
   registry/menu/command/event table entries, resource/data/config files (search **all** file types), build entries.
4. Recurse into each dependency's body (R1 + R4 on its range). Stop rule here: generic infrastructure
   (used by > ~10 unrelated files, record it) or nothing new. Final stop against the target is done in C (fixpoint).
5. Headers (R6) and guards (R5) for every ported line; where each guard macro is enabled in source.

### B6 – Incoming dependencies needed for behavior
For each S (request + `ext`): callers and non-call uses (R3) → `needed-for-behavior` (registration entry,
init call, default value, dispatcher case) or `CONSUMER`.

### B7 – Tests
R9: tests touching each S, or `none found (patterns)`.

### B8 – Write the report
- `### Files Analyzed`: every manifest file → `analyzed` / `skipped (reason)`.
- `### Latest Source Anchoring`: `| H/S-id | request location | latest location | anchor result | latest state | evidence | confidence |` + alias map entries.
- `### Changed Symbols and Behavior`: `| S-id | symbol (kind) | H-ids / ext | change type | behavior before → after | later evolution |`.
- `### Dependencies and Test Coverage`: outgoing code deps, data deps, incoming deps, guards, headers, tests.
- `### Blockers and Context Risk`: unresolved anchors, UNCLEAR evolution/extension, partial takes, macro-generated
  code, runtime-assigned function pointers, complex `#if`, layout changes.
Run `gates/B.md`, write `### Gate Result`, update Workflow Status.

## Stop message
```
Checkpoint B <Complete|Blocked>.
Anchoring: same a · moved m · renamed r · not found n · evolved e · removed x
Extensions found: <k> (new symbols <list>) · Consumers (report only): <list>
Closure: code deps <d>, data deps <t> · Guards: <list> · Tests: <found/none>
Questions for you: <numbered list or none>
Reply "approve C" (with answers if any) to start Checkpoint C (target trace).
```
