# Checkpoint B – Source Change Analysis (anchor in latest source + feature closure)

**Goal:** starting from the request diff, trace back into `SOURCE_ROOT` (latest source), find where
every piece of the request lives *now* (even if files or functions were moved or renamed), find how the
feature was **extended** after the request, and collect the full closure of code **and data** the feature
needs. The result is the *port version* of the feature: what will be merged to the target.
**Reads:** `_work/A_hunks.md`, `_work/A_links.md`, `diffs/source/**`, `SOURCE_REQUEST/Before|After`, `SOURCE_ROOT` (search and
narrow reads; plain folder, no history – everything is inferred from content).
**Writes:** `_work/B_feature_ids.txt`, `_work/B_aliased/**`, `_work/B_anchor.md`, `_work/alias_map.md`, `_work/B_new_tokens.txt`,
`_work/B_symbols.md`, report section B.
**Load:** `references/c-cpp-search-recipes.md` (R1–R7, R9, R11–R17), `references/glossary.md`; uses `_work/A_links.md`.

## Steps

### B1 – Changed symbols (request view)
From `_work/A_hunks.md` create one `S###` per distinct symbol (several H-ids may share one S). For each,
read its REQ-B and REQ-A bodies and record `change type` and behavior `before → after` (concrete values,
conditions, parameters). For `layout` changes list members/enum values whose offset or value shifts.

### B2 – Anchor every request item in latest source (graph-driven loop)
Goal: for every node of `_work/A_links.md` (and so every S-id and file), find where it lives **now** in
`SOURCE_ROOT`, even when files or names changed. Names are searched first, then content, then relations;
every anchor records the method and the signals (R12 confidence rules).

**B2.0 – Prepare.** Write `_work/B_feature_ids.txt` = names of the `medium`/`volatile` nodes (one per line; used by
R16/R17). Order the nodes: `stable` → `medium` → `volatile`; inside a class, nodes with more edges first.

**B2.1 – Files.** Same path exists in `SOURCE_ROOT`? If not → R11 (basename, includes/builds links, content,
R17 fallback). Result: `SAME_PATH` / `MOVED_FILE <new path>` / `SPLIT_FILE <paths>` / `NOT_FOUND`.

**B2.2 – Nodes, one pass in B2.0 order.** For each not-yet-anchored node:
1. Exact name (R2) in the anchored file(s), then repo-wide. Found → **verify it is the same thing**: same kind,
   body comparable (R7 or R17 `blind` ≥ 0.6 against REQ-A), and not a different `static` symbol with the same name.
   Verified → `SAME_NAME` / `MOVED_SYMBOL` (method `NAME`, confidence `High`). Name found but body unrelated →
   treat as not found (name reused) and note it.
2. Not found by name → climb the R12 ladder: L0 alias → L1 walk the links (only edges whose other end is anchored)
   → L2 fuzzy lines (R16) → L3 stable anchors → L4 similarity (R17) → L5 rename pattern → L6 hypotheses.
   Result: `RENAMED_SYMBOL <new name>` / `SPLIT_SYMBOL` / `MERGED_SYMBOL` with method(s), signals, confidence.
3. Still nothing → leave it for the next iteration (a neighbor anchored later may unlock it).
Every new rename/move goes into `_work/alias_map.md` immediately (`request → latest`, method, signals); every
consistent rename rule found goes in as `kind = pattern` (R12 L5).

**B2.3 – Cross-check through the links.** For each edge whose both ends are now anchored, check that the latest
code still shows the relation with the latest names (e.g. request `A calls B`, alias `B → B'` ⇒ latest body of
`A'` calls `B'`; table entry of ID still points to the handler's latest name). Result per edge:
`consistent` / `changed (<what>)` / `broken`. A `broken` edge downgrades the less certain end one level (R12) and
is listed as a risk; `changed` is normal evolution (B3 will classify it).

**B2.4 – Iterate.** Repeat B2.2–B2.3 for the nodes still open. Stop when an iteration anchors no new node.
Log each iteration in `_work/B_anchor.md`: `Iteration k: +n anchored (NAME a, EDGE e, FUZZY f, ANCHOR c, SIM s, PATTERN p)`.

**B2.5 – Still not found → eliminate (R12 L7).** For each remaining node record which checks were run and conclude
`MACRO_GENERATED <macro, SRC:path:line>` / `REWRITTEN` (anchors present, structure gone) / `NOT_FOUND (removed)` /
`NOT_FOUND (unknown)`. Encoding mismatches must be ruled out before `NOT_FOUND`.

**B2.6 – Latest state and hunks (modulo aliases).** Only now, with the alias map complete:
- Apply the alias map to the request text first: in REQ-A bodies and `+` lines, replace every request name by its
  latest name (`_work/B_aliased/<path>`; never edit the inputs). Whole words only, longest names first, e.g.
  `LC_ALL=C sed -E 's/(^|[^A-Za-z0-9_])OLD([^A-Za-z0-9_]|$)/\1NEW\2/g'` (portable BSD/GNU; run twice for adjacent hits).
- Compare the aliased REQ-A body with the latest body (R7): `UNCHANGED_IN_LATEST` / `EVOLVED` / `REMOVED_IN_LATEST`.
- Per hunk: each distinctive aliased `+` line found in the anchored latest body (`grep -F`, then R16 for lines that
  still miss) → `PRESENT` (all found), `PARTIAL`, `GONE`. Lines found only after aliasing or only by R16 are marked
  `(modulo aliases)` / `(fuzzy)` with the matching `SRC:path:line`.
- Write `_work/B_anchor.md`.
Any `NOT_FOUND`, `REWRITTEN`, `MACRO_GENERATED`, `REMOVED_IN_LATEST`, `GONE`, `broken` edge or `Low` anchor →
blocker with a question.

### B3 – Classify later evolution (only `EVOLVED` items)
Diff the **aliased** REQ-A body (`_work/B_aliased/`, B2.6) against the latest body, so pure renames do not show up
as change blocks (a rename-only difference is `REFACTOR`). For each later change block apply R14:
`EXTENSION` (feature grew: related to feature tokens/lines/guard), `REFACTOR` (rename/format/move of
feature lines), `BUGFIX` (fix to feature lines), `UNRELATED` (another feature or unrelated refactor in the
same function), `UNCLEAR`. Record per block with `SRC:path:line`. `UNCLEAR` → blocker.

### B4 – Discover feature extensions outside the request's symbols
The feature may have grown into new places after the request. Search latest source **with the latest names**
(alias map), never only with the request names – after a rename the old names find nothing:
- every use of the feature's symbols/macros/strings (latest names) outside the anchored symbols (R3),
- code under the feature's guard macro(s) (R5 inverse: `grep -n "<GUARD>"` then read the blocks),
- symbols with the feature's naming prefix – the request prefix **and** every latest prefix from `alias_map.md`
  `kind = pattern` rows (`grep -rnw -E "<Prefix>[A-Za-z0-9_]*"`), new files referencing them,
- the stable anchors of the feature (string IDs, NVRAM keys, command keywords from `A_links.md`) in places not yet anchored.
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
- `### Latest Source Anchoring`: `| H/S-id | request location | latest location | anchor result | latest state | method | evidence (signals) | confidence |`
  + alias map entries (incl. rename patterns) + iteration log + link cross-check counts (`consistent / changed / broken`)
  + `#### Anchored Link Graph`: the A7 graph coloured by anchor result, with the latest name of every node, so the
  reviewer sees how anchors propagated (paste the output, without the edge table already shown in A):
  `python3 -I "$SK/scripts/links_view.py" --links "$W/A_links.md" --anchor "$W/B_anchor.md" --no-table --out "$W/B_links.mmd"`.
- `### Changed Symbols and Behavior`: `| S-id | symbol (kind) | H-ids / ext | change type | behavior before → after | later evolution |`.
- `### Dependencies and Test Coverage`: outgoing code deps, data deps, incoming deps, guards, headers, tests.
- `### Blockers and Context Risk`: unresolved anchors, UNCLEAR evolution/extension, partial takes, macro-generated
  code, runtime-assigned function pointers, complex `#if`, layout changes.
Run `gates/B.md`, write `### Gate Result`, update Workflow Status.

## Stop message
```
Checkpoint B <Complete|Blocked>.
Anchoring: same a · moved m · renamed r · split/merged s · not found n · evolved e · removed x
Methods: NAME a · EDGE e · FUZZY f · ANCHOR c · SIM s · PATTERN p · LLM-led l · iterations k · broken links: <list or none>
Rename patterns: <request → latest rules or none>
Extensions found: <k> (new symbols <list>) · Consumers (report only): <list>
Closure: code deps <d>, data deps <t> · Guards: <list> · Tests: <found/none>
Questions for you: <numbered list or none>
Reply "approve C" (with answers if any) to start Checkpoint C (target trace).
```
