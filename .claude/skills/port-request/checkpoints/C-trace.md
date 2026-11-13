# Checkpoint C – Source/Target Flow Trace (+ closure fixpoint)

**Goal:** for every item of the port version (request symbols, extensions, code and data dependencies),
establish with evidence what exists in the target – including items the target has under another name
or in another file – and keep expanding dependencies until the target already has everything else.
**Reads:** `_work/B_*.md`, `_work/alias_map.md`, `SOURCE_ROOT`, `SOURCE_REQUEST/Before|After`, `TARGET_ROOT`
(plain folders, no history).
**Writes:** `_work/C_trace.md`, `_work/alias_map.md` (target column), report section C. Never assumes equivalence.
**Load:** `references/c-cpp-search-recipes.md` (R1–R3, R5–R8, R11–R13, R16, R17), `references/glossary.md`; uses `_work/A_links.md`.

## Steps

### C1 – Source flows (latest)
Group items into formulas (behaviors). For each, the chain in latest source, entry → effect:
`FLOW-n source: SRC:<entry registration/caller> → SRC:<symbol> → SRC:<deps/data>`. No entry found → blocker.

### C2 – Locate each item in the target
For every S-id, `ext` S-id and dependency `S###.d#` (code and data):
1. Same path in target → R1 range by the latest name.
2. Same name elsewhere (R2) → `MOVED` in target.
3. Not found by name → R11 (file) / R12 ladder (symbol) in the target, with the **latest source** text as reference:
   L0 alias/wrapper → L1 walk the `A_links.md` edges (via the alias map) whose other end is already located in the
   target → L2 fuzzy lines (R16, `--abstract-file` = latest names of the port items) → L3 stable anchors → L4 R17
   (`--ref-file` = the `SOURCE_ROOT` file, `--root "$TARGET_ROOT"`) → L5 rename pattern (target naming rule) →
   L6 hypotheses. Signals and confidence per R12 → `RENAMED` (≥ Medium) or `RENAMED_CANDIDATE` (`Low`).
   Locate stable items first (string IDs, NVRAM keys, build entries) so their links can be walked.
4. Nothing → `MISSING`.
Fill the target column of `_work/alias_map.md` (`latest source name → target name`).

### C3 – Compare and classify
Extract the target body, the REQ-B body and the **port version** (from B5); compare with R7:
target = port version → `SAME_AS_SOURCE`; target = REQ-B → `SAME_AS_BEFORE`; params/return/fields differ →
`SIGNATURE_DIFF`; otherwise `DIVERGED` (list differing lines `TGT:path:line`). Compare after applying the alias
map (a body that differs only by renamed identifiers counts as equal, note `equal modulo aliases`).
For `SIGNATURE_DIFF`/`DIVERGED` list target callers (R3). Guards: enabled in target config/build? Headers included?
Data deps: does each table/language file/default/enum entry exist in the target? (R13 on target).

### C4 – Closure fixpoint
For every item that is `MISSING`, `DIVERGED` or `SIGNATURE_DIFF` whose own dependencies were not expanded in B
(B5 stopped earlier), expand them now with the B5 procedure and classify them with C2–C3. Repeat until an
iteration adds no new item. Stop following a branch as soon as the target has it `SAME_AS_SOURCE` (or equal
modulo aliases). Record each iteration in `_work/C_trace.md` (`Iteration k: +n items`).

### C5 – Target flows
For each `FLOW-n`: `FLOW-n target: TGT:<entry> → TGT:<symbol> → MISSING at <dep>`. Note target-only behavior
the port must not break (target-specific branches, other callers, target-only table entries).

### C6 – Write the report
- `### Source Behavior`: FLOW chains (latest source).
- `### Target Behavior`: FLOW chains (target) + `| id | item | target location | target state | confidence |`.
- `### Gaps, Evidence, and Confidence`: every non-`SAME_AS_SOURCE` item with evidence; alias map; data gaps;
  guard/header gaps; closure iterations.
- `### Blockers`: every `Low`, `RENAMED_CANDIDATE`, missing entry, with a yes/no question
  (e.g. "Is `TGT:src/x.c:88 DensAdj()` the target equivalent of `Density_Scale`?").
Run `gates/C.md`, write `### Gate Result`, update Workflow Status.
Interactive: answers are recorded in C's Blockers as `Answer: … (user, <date>)` before D starts.

## Stop message
```
Checkpoint C <Complete|Blocked>.
Items: <n> · SAME_AS_SOURCE a · SAME_AS_BEFORE b · DIVERGED c · SIGNATURE_DIFF s · MISSING m · RENAMED r · RENAMED_CANDIDATE q
Closure iterations: <k> (+<x> items) · Data gaps: <list> · Guards not enabled: <list>
Questions for you: <numbered list or none>
Reply "approve D" (with answers if any) to start Checkpoint D (mapping and plan).
```
