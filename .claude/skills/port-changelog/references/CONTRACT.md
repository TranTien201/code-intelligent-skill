# port-changelog — internal contract (scripts, files, JSON)

Design source of truth: `../OVERVIEW.md`. This file fixes the interfaces so scripts can be built
independently. Standard library only, Python 3.9+, run with `python3 -I`. Scripts import each other
by adding their own directory to `sys.path` (`sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`).
All file IO goes through `common.read_src` / `common.write_src` (latin-1 byte-exact, EOL preserved).

## 1. Work directory

```
WORK/
  feature.diff            # THE single living file (stage: original -> latest -> merged)
  feature.orig.diff       # untouched copy of the customer diff (created by `run.py init`)
  target_out/             # full copy of target with the merge applied (step 2)
  .port_changelog/        # internal state, NOT a report
    config.json           # {"latest": abs, "target": abs, "rt": "RT2486"|null, "k": 3, "hi": 0.9, "lo": 0.6}
    scope.json            # step 0 output (changelog.py)
    questions.json        # open questions of the CURRENT step: {"step": n, "questions": [Question]}
    answers.json          # {"<question id>": {"answer": "Y"|"N"|<free text>, "by": "user"|"llm", "note": ""}}
```

Exit codes of every step script: `0` done, `2` questions pending (written to questions.json — rerun the
same step after answers.json is filled), `1` error.

A step NEVER asks the same question twice: if `answers.json` already has the id, use the answer.

### Question
```json
{"id": "s1:src/artlib.c:ArtLibCopyRecipeName:newsym:artLibLinkOnVarSet",
 "step": 1,
 "kind": "new_symbol",
 "who": "user",
 "file": "src/artlib.c", "unit": "ArtLibCopyRecipeName",
 "message": "<Vietnamese, short, one question>",
 "options": ["Y", "N"],
 "context": {"snippet": "...", "candidates": [...], "rt_hint": "RT2707 (V8.14) Add. artLibLinkOnVarSet()"}}
```
`who`: `"llm"` = Claude must judge it itself first (gray-zone similarity); it may write the answer with
`by: "llm"` or escalate by re-asking the user. `"user"` = must be asked to the human.

Kinds — step 1: `new_symbol`, `missing_unit`, `llm_judge`; step 2: `target_mismatch` (neither `-` nor `+`
found), `target_ambiguous` (several matches), `insert_point`, `target_file_missing`, `llm_judge`.
IDs are deterministic: `s<step>:<file>:<unit>:<kind>[:<detail>]`.

## 2. Notes inside feature.diff

- Global (before the first `---`): `# port-changelog <key>=<value>` — keys `rt`, `stage`
  (`original`|`latest`|`merged`), `latest`, `target`.
- Per file (before that file's `---`), one line per unit, machine-readable `key=value` tokens then free text:
  ```
  # unit=ArtLibCopyRecipeName kind=func change=mod status=CHANGED rt=RT2707 after=ArtLibEntryRecipeName | <free text>
  # step2 unit=ArtLibCopyRecipeName result=AUTO | <free text>
  ```
  `change`: `add` | `mod` | `del` | `closure` (pulled in by a new symbol) | `toplevel` (lines outside units).
  `status` (step 1): `UNCHANGED` | `CHANGED` | `UNEXPLAINED` | `MISSING` | `PARTIAL_REMOVED`.
  `after=<name>`: unit that precedes this one in Latest (insert anchor for whole new units).
  `result` (step 2): `AUTO` | `SKIP` | `USER_Y` | `USER_N` | `ASK`.
- Hunk header section (`@@ ... @@ <name>`) = unit name the hunk belongs to (empty for toplevel).
- Changelog (`Modification:`) block lines are NEVER part of hunks after step 1; the RT entry lives in
  `scope.json` and is inserted into target by step 2.

## 3. scope.json (changelog.py)

```json
{
 "rt": "RT2486",
 "fingerprint": {"rt": "RT2486", "rt_full": "RT2486", "date": "2018/08/31", "author": "Y.Kaneko (TTS-X)",
                 "version": "V8.06R0", "items": {"Add": ["artLibSetVarDate"], "Mod": ["ArtLibGetRecipeData"]},
                 "raw": ["/*#         2018/08/31  Y.Kaneko (TTS-X)     RT2486    ... #*/", "..."]},
 "files": [{"path": "src/artlib.c", "in_diff": true, "has_entry": true, "latest_exists": true, "warning": null}],
 "later_entries": [{"file": "src/artlib.c", "rt": "RT2707", "rt_full": "RT2707", "date": "2021/08/02",
                    "author": "S.Kinoshita", "version": "V8.14R000",
                    "items": {"Add": ["artLibLinkOnVarSet"], "Mod": ["ArtLibCopyRecipeName"]},
                    "relation": "suspect", "touches": ["ArtLibCopyRecipeName"]}],
 "followups": [ /* entries of the SAME RT with a suffix (RT2486:V806-0001), same shape */ ],
 "suspects": {"ArtLibCopyRecipeName": ["RT2707"]},
 "symbol_sources": {"artLibLinkOnVarSet": {"rt": "RT2707", "version": "V8.14R000", "date": "2021/08/02", "file": "src/artlib.c", "action": "Add"}},
 "rt_items": {"Add": [...], "Mod": [...]},
 "diff_units": ["ArtLibCopyRecipeName", "..."],
 "coverage": {"missing_in_diff": [], "extra_in_diff": []}
}
```
`relation`: `suspect` (Mod/Add/Del of a name in rt_items), `symbol_source` (only adds/mods names not in
rt_items), `unrelated`. The fingerprint comes from the `+` lines of the `Modification:` block in
feature.diff (if several files carry it, the first; all files are listed in `files`).

## 4. Module APIs

### changelog.py
```python
find_mod_block(lines) -> (start, end) | None   # 0-based [start, end) of the /*# ... #*/ Modification block
blank_mod_block(lines) -> list                 # same length, block lines replaced by ''
parse_entries(block_lines) -> [entry]          # newest first; entry keys as in later_entries + "raw", "offset"
norm_name(s) -> str                            # 'artLibSetVarDate()' -> 'artLibSetVarDate', 'X[][]' -> 'X'
fingerprint_from_diff(files: [FileDiff]) -> [{"file": path, "entry": entry}]
build_scope(diff_path, latest_dir, rt=None) -> dict   # scope.json content
insert_entry(lines, raw_entry_lines) -> list   # insert entry as newest (right after 'Modification:' line);
                                               # if no block: return lines unchanged
# CLI: changelog.py scope --diff D --latest L [--rt RT] --out scope.json ; changelog.py show FILE
```
Entry line formats to support (columns vary, spaces vary):
- header: `/*#   YYYY/MM/DD  <author ...>  [Vx.yyRzzz]  RTnnnn[:suffix]   #*/`
- item:   `/*#   Add. name()  #*/` ; continuation `/*#        name()  #*/` (inherits last action word);
  action word = any `Word.` (`Add.`, `Mod.`, `Del.`, `Chg.` ...)
- version separator: `/*# ---- From here TELINDY V8.14R000 #*/` -> applies to the entries ABOVE it
  (up to the previous separator). If the header itself has `Vx.yyRzzz`, that wins.

### locate.py
```python
class DefIndex:                       # lazy symbol-definition index over a tree
    def __init__(self, root): ...
    def defs(self, name) -> [(relpath, Unit)]   # grep -rlw then find_units; cached
    def units(self, relpath) -> [Unit]          # cached
    def has(self, name) -> bool

similarity(a_lines, b_lines) -> float           # 0..1, rename-tolerant containment of a in b
find_unit(name, kind, ref_lines, root, hint_files=None, index=None, hi=0.9, lo=0.6) -> {
    "status": "found" | "renamed" | "llm" | "missing",
    "path": relpath|None, "unit": Unit|None, "score": float, "method": "name"|"similarity",
    "candidates": [{"path", "name", "start", "end", "score"}]}   # top 3
locate_block(block_lines, lines, lo_line=1, hi_line=None) -> [Candidate]
    # Candidate = {"start": int, "end": int, "score": float, "method": "exact"|"normalized"|"anchor"|"fuzzy"}
    # 1-based inclusive in `lines`; sorted by score desc; blank/comment-only lines of block ignored for matching
decide(cands, hi=0.9, lo=0.6) -> "auto" | "llm" | "ask"
    # auto: best >= hi and (single candidate or best - second >= 0.1)
    # llm : lo <= best < hi, or several candidates close to each other (all >= lo)
    # ask : best < lo or no candidate (exception: best is an 'anchor' hit with score >= 0.25 -> llm)
line_in(line, lines) -> bool                    # normalized (norm_line) membership
# CLI: locate.py unit --name N --root R [--ref-file F --ref-name N] ; locate.py block --block-file B --file F
```

### carry.py (step 1)  `carry.py --work W` → rewrites feature.diff (stage=latest), exit 0/2/1
### merge_target.py (step 2) `merge_target.py --work W` → target_out/, feature.diff notes + stage=merged
### verify.py (step 3) `verify.py --work W [--build-cmd CMD]` → prints Vietnamese checklist, exit 0/1
### run.py
```
run.py init  --work W --latest L --target T (--diff D | --before B --after A) [--rt RT]
run.py step0|step1|step2|step3 --work W
run.py all   --work W            # runs from the first unfinished step; stops at exit 2
run.py answer --work W --id ID --answer A [--by user|llm] [--note TEXT]
run.py questions --work W        # prints open questions (Vietnamese)
```

## 5. Step 2 decision table (merge_target.py)

Per hunk, inside the target unit with the same name (found with `locate.find_unit` on target):

| `-` side (context + removed) found in target | `+`-only lines already in target | result |
|---|---|---|
| yes, `decide` = auto | no | AUTO (apply, keep target's own version of context lines) |
| any | yes (all non-blank `+` lines present, `line_in`) | SKIP |
| `decide` = llm | — | question `llm_judge` (who=llm) |
| no (`ask`) | no | question `target_mismatch` (never silently skipped) |
| several close candidates | — | question `target_ambiguous` |

Pure-add hunk (no `-` lines): anchor on context lines; whole new unit (`change=add|closure`) absent in
target → insert after the target unit named by `after=`, else after the last unit of the file;
if the target file itself is missing → question `target_file_missing` (Y = create file from Latest content).
After all hunks of a file: insert the RT changelog entry (`scope.json` fingerprint raw lines) with
`changelog.insert_entry` if the target file has a Modification block.
Answer handling: `Y` on a mismatch/ambiguous question = apply at the best candidate; `N` = skip;
a number `1..3` = apply at that candidate.
