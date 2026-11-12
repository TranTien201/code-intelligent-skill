# Search recipes (C/C++ and similar)

Copy-paste commands. `$ROOT` = the root searched, `$S` = symbol name, `$F` = file, `$W` = `$OUTPUT_ROOT/_work`,
`$SK` = this skill's directory (scripts in `$SK/scripts/`, run with `python3 -I`).
Common grep options (define once per shell):
```bash
GOPT=(-rn --include='*.c' --include='*.h' --include='*.cc' --include='*.cpp' --include='*.cxx' \
      --include='*.hpp' --include='*.hh' --include='*.inc' --exclude-dir=.git --exclude-dir=build --exclude-dir=out)
```
macOS grep: `-w` is reliable; if `\b` misbehaves inside `-E`, use `-w` or `[[:<:]]` / `[[:>:]]`.
Always read results narrowly: `sed -n '<a>,<b>p' "$F"`.

## R0 – Diff of the request
```bash
cd "$SOURCE_REQUEST"
diff -rq Before After                                   # file list (Only in / differ)
git diff --no-index --no-color -U3 --function-context -- "Before/$P" "After/$P" > "$OUTPUT_ROOT/diffs/source/$P.diff"
git diff --no-index --no-color -U0 -- "Before/$P" "After/$P"     # exact changed line numbers
git diff --no-index --stat Before After                  # sanity count
```
For an added file use `/dev/null` as the Before side; for a deleted file `/dev/null` as After.
`git diff --no-index` works on plain folders (no repository needed) and exits 1 when files differ: not an error.
Binary: `git diff --no-index --numstat` shows `-  -` → `file_status` stays as computed, function `N/A (non-code file)`.

Fallback without `git` (same information, standard `diff`):
```bash
diff -u -p "Before/$P" "After/$P" > "$OUTPUT_ROOT/diffs/source/$P.diff"    # -N for added/deleted: diff -u -p -N
diff -U0 "Before/$P" "After/$P"                                            # exact changed line numbers
diff -ruN Before After | grep -E '^\+' | grep -vc '^+++ '                 # added lines total
diff -ruN Before After | grep -E '^-'  | grep -vc '^--- '                  # deleted lines total
```

## R1 – Top-level symbol ranges of a file (function / struct / enum / table bodies)
```bash
awk '
function trim(s){gsub(/^[ \t]+|[ \t]+$/,"",s);return s}
{ raw=$0; code=raw; sub(/\/\/.*/,"",code)
  o=gsub(/\{/,"{",code); c=gsub(/\}/,"}",code)
  if (depth==0 && o>0) { if (trim(code)!="{") {hdr=raw; hs=NR} else {hdr=prev; hs=prevNR} }
  depth+=o-c
  if (depth==0 && o+c>0 && hs) { printf "%d-%d\t%s\n", hs, NR, trim(hdr); hs=0 }
  if (depth==0 && trim(code)!="") { prev=raw; prevNR=NR } }' "$F"
```
Output `start-end<TAB>header`. A changed line inside a range belongs to that symbol.
Limitations – verify by reading the header lines when: the signature spans several lines (header
shows only the last line), braces appear in strings/`/* */` comments, or code sits in `#if 0`.
Lines outside every range: classify with R2 (`#define`, prototype, global, `#include` → file scope).

## R2 – Definitions
```bash
grep "${GOPT[@]}" -E "^[A-Za-z_][^;]*[^A-Za-z0-9_]$S[[:space:]]*\(" "$ROOT" | grep -v ';[[:space:]]*$'   # function definition
grep "${GOPT[@]}" -E "[^A-Za-z0-9_]$S[[:space:]]*\([^)]*\)?[[:space:]]*;" "$ROOT" | grep -v '=' # prototype
grep "${GOPT[@]}" -E "^[[:space:]]*#[[:space:]]*define[[:space:]]+$S([^A-Za-z0-9_]|$)" "$ROOT"     # macro
grep "${GOPT[@]}" -E "(struct|union|enum)[[:space:]]+$S([^A-Za-z0-9_]|$)" "$ROOT"                  # tag
grep "${GOPT[@]}" -E "^\}[[:space:]]*$S[[:space:]]*;|typedef[^;]*[^A-Za-z0-9_]$S[[:space:]]*;" "$ROOT"  # typedef
grep "${GOPT[@]}" -wE "$S[[:space:]]*(=[^=]|,|$)" "$ROOT"                                          # enum constant (check it is inside an enum)
grep "${GOPT[@]}" -E "^[A-Za-z_][^(]*[^A-Za-z0-9_]$S[[:space:]]*(\[[^]]*\])?[[:space:]]*(=|;)" "$ROOT"   # global / table
```
Static symbols may be defined in several files: always record the file and use `name@path`.

## R3 – Uses
```bash
grep "${GOPT[@]}" -w "$S" "$ROOT"                                  # every use
grep "${GOPT[@]}" -E "(^|[^A-Za-z0-9_])$S[[:space:]]*\(" "$ROOT"   # calls
grep "${GOPT[@]}" -w "$S" "$ROOT" | grep -vE "$S[[:space:]]*\("    # non-call uses: function pointers, registration tables, callbacks
```
Registration tables (menus, command tables, handler arrays, init lists) are the most common hidden
incoming dependency: for every non-call use, read the enclosing table (R1) and note the entry.

## R4 – New tokens introduced by the request (outgoing dependencies)
```bash
grep -h '^+' "$OUTPUT_ROOT"/diffs/source/*.diff | grep -v '^+++' \
 | sed -e 's://.*$::' -e 's:"[^"]*"::g' | grep -oE '[A-Za-z_][A-Za-z0-9_]*' | sort -u > "$OUTPUT_ROOT/_work/B_new_tokens.txt"
```
Remove C/C++ keywords and standard types/library names (`if for while return sizeof static const
unsigned int char void struct enum union typedef extern inline bool true false NULL uint8_t … memcpy printf …`).
**Follow only these tokens** (tokens the request adds). Do not walk whole shared tables or files that
the request merely touches – only the hunks are ported.

## R5 – Enclosing preprocessor conditions of line N
```bash
awk -v N="$N" '
/^[ \t]*#[ \t]*(if|ifdef|ifndef)/ { st[++d]=$0 }
/^[ \t]*#[ \t]*(elif|else)/        { st[d]=st[d]" / "$0 }
/^[ \t]*#[ \t]*endif/              { d-- }
NR==N { for(i=1;i<=d;i++) print st[i]; exit }' "$F"
```
For each macro `M` in the condition, check where it is enabled:
```bash
grep "${GOPT[@]}" --include='Makefile' --include='*.mk' --include='CMakeLists.txt' --include='*.cmake' \
     -E "#[[:space:]]*define[[:space:]]+$M([^A-Za-z0-9_]|$)|-D$M([^A-Za-z0-9_]|$)|$M[[:space:]]*[:+]?=" "$ROOT"
```

## R6 – Headers / includes
```bash
grep "${GOPT[@]}" -E '#[[:space:]]*include' "$F"                    # what a file includes
grep "${GOPT[@]}" -E "#[[:space:]]*include[[:space:]]*[<\"]([^>\"]*/)?$(basename "$H")[>\"]" "$ROOT"   # who includes header H
```

## R7 – Compare one symbol across trees
```bash
sed -n '<a>,<b>p' "$FILE_1" > "$OUTPUT_ROOT/_work/cmp_1.txt"
sed -n '<c>,<d>p' "$FILE_2" > "$OUTPUT_ROOT/_work/cmp_2.txt"
diff -w "$OUTPUT_ROOT/_work/cmp_1.txt" "$OUTPUT_ROOT/_work/cmp_2.txt" && echo SAME
```
Get the ranges with R1 on each file. Compare target vs `REQ-B` and target vs `REQ-A` to decide the
target state; compare `SRC` vs `REQ-A` for drift.

## R8 – Rename candidates (only when the name is MISSING in target)
Take 1–2 distinctive lines of the source body (string literals, unusual constants, unique call
sequences) and search for them in the target:
```bash
grep "${GOPT[@]}" -F '<distinctive literal>' "$TARGET_ROOT"
```
A hit is a `RENAMED_CANDIDATE` with confidence `Low` until the user confirms.

## R9 – Tests and build entry points
```bash
find "$ROOT" -type d \( -iname 'test*' -o -iname 'unittest*' -o -iname 'ut' \) -not -path '*/.git/*'
grep "${GOPT[@]}" -lw "$S" "$ROOT" | grep -iE 'test|_ut|spec'
ls "$ROOT" | grep -iE '^(Makefile|GNUmakefile|CMakeLists.txt|build.*\.(sh|bat|py)|.*\.sln|.*\.vcxproj|README.*)$'
```

## R10 – Request-label convention in target
```bash
grep "${GOPT[@]}" -E '(REQ|CR|PR|ECR|ECO|TICKET|ISSUE|BUG|FIX|MOD|CHG)[-_#: ]?[0-9]{2,}' "$TARGET_ROOT" | head -50
```
Accept a convention only if ≥3 occurrences share one format (prefix, comment style, start/end
markers). Record 3 examples as evidence.

## R11 – Relocate a file (moved / renamed / split)
`$P` = request-relative path, `$REF` = the reference file (REQ-A version for source anchoring, the source
version for target lookup), `$W` = `$OUTPUT_ROOT/_work`.
```bash
# a. same basename elsewhere
find "$ROOT" -type f -name "$(basename "$P")" -not -path '*/.git/*'
# b. includes: who includes the old header name / a header with the same symbols (R6) – a moved header is
#    usually still included by the same .c files under a new path
# c. content similarity: rank candidate files by shared normalized lines
norm(){ sed -e 's://.*$::' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' "$1" | grep -vE '^([{}();]*|/\*.*|\*.*)$' | sort -u; }
norm "$REF" > "$W/ref.lines"; total=$(wc -l < "$W/ref.lines")
grep -oE '[A-Za-z_][A-Za-z0-9_]{6,}' "$REF" | sort | uniq -c | sort -n | head -15 | awk '{print $2}' > "$W/ref.ids"
grep "${GOPT[@]}" -lwF -f "$W/ref.ids" "$ROOT" | sed 's/:.*//' | sort -u | while read -r c; do
  n=$(norm "$c" | comm -12 - "$W/ref.lines" | wc -l); echo "$((100*n/total))% $c"; done | sort -rn | head -5
```
Relation signals for files (from `_work/A_links.md`): an anchored `.c` still `includes` a header at the same
place, or an anchored build file `builds` the candidate. File confidence follows the R12 rules with these as
relation signals and the similarity score as content signal.
Score ≥ 60 % → strong candidate; 30–60 % → candidate (maybe `SPLIT_FILE`: check whether 2 candidates together
cover the file); < 30 % → not the same file. The `ref.ids` are the *rarest* long identifiers of the file.
d. When the file's identifiers were renamed too (a–c find nothing): run R17 for the 2–3 largest blocks of `$REF`;
   the file that holds their top candidates is the file candidate (blocks landing in 2+ files → maybe `SPLIT_FILE`).

## R12 – Locate a symbol whose name is not found (search ladder)
`$OLD` = request name, body from REQ-A (from latest source when used for the target lookup in C).
`$W` = `$OUTPUT_ROOT/_work`, `$SK` = this skill's directory. Run the rungs **in order**; stop climbing as soon as
the confidence rules below give `High`, otherwise collect every candidate and its signals.
A missing name alone proves nothing: it may be a rename, a macro-generated name, a split/merge, a rewrite,
a removal or an encoding mismatch (L7 tells them apart).

**L0 – alias / wrapper** (signal `ALIAS`)
```bash
grep "${GOPT[@]}" -E "#[[:space:]]*define[[:space:]]+$OLD[[:space:](]" "$ROOT"
grep "${GOPT[@]}" -B2 -A6 -E "^[A-Za-z_].*[^A-Za-z0-9_]$OLD[[:space:]]*\(" "$ROOT" | grep -E 'return .*\('   # thin wrapper
grep "${GOPT[@]}" -w "$OLD" "$ROOT"     # also catches the old name left in comments ("renamed from …")
```
**L1 – walk the links** (signals `EDGE`, `NEIGHBOR`). For every edge of `$OLD` in `_work/A_links.md` whose other
end is already anchored in `$ROOT`, read that end's latest body and find the spot that played the edge's role:
| edge | where to look in the anchored end | the candidate is |
|---|---|---|
| `calls` (anchored caller → `$OLD`) | the caller's latest body; find the request call line with R16 | the function called at that position |
| `calls` (`$OLD` → anchored callee) | callers of the callee (R3) whose body matches `$OLD` (R16/R17) | that caller |
| `declares` | the header next to the anchored prototypes (same order) | the prototype in that slot |
| `registers` | the anchored table; entry with the same ID/key/slot | the handler/ID in that entry |
| `indexes` / `localizes` / `defaults` | the anchored enum, language table or default table; same position/value | the entry there |
| `reads` / `writes` | functions using the anchored field/global (R3) | the one whose body matches (R16/R17) |
| `includes` / `builds` | the anchored `.c` / build file | the included header / listed file |
`NEIGHBOR`: symbols defined just before/after `$OLD` in REQ-A (R1 ranges) found by name in `$ROOT`; the unknown
symbol between them is a candidate.

**L2 – fuzzy line grep** (signal `FUZZY`): R16 on the distinctive `+`/body lines of `$OLD` (skip `WEAK` patterns);
group the hits by enclosing block (R1 on each hit file). A block holding ≥2 non-WEAK hits is a candidate.

**L3 – stable anchors** (signal `ANCHOR`): from `$OLD`'s body take string literals, numeric constants other than
0/1/-1, data IDs (`STR_*`, NVRAM keys, command keywords) and `uses-external` callees; `grep -rnF` each (R13 for
data, all file types); count hits per enclosing block. A block holding ≥2 of them, and more than any other block,
is a candidate. Encoding: see L7.

**L4 – rename-invariant similarity** (signals `SIM`, `SIG`): R17. `SIM` when `blind` ≥ 0.6 and the result is not
`TOO-SHORT`; `SIG` when `sig` is `=`. `possible SPLIT` / `size` ≥ 2 → check `SPLIT_SYMBOL` / `MERGED_SYMBOL`.

**L5 – rename pattern** (signal `PATTERN`): when ≥2 symbols of this request are already anchored as renames with
the same textual rule (prefix/suffix/word change, e.g. `TonerSave_` → `Eco_`, `toner_save` → `eco_mode`), apply the
rule to `$OLD` and grep the predicted name (R2). Record the rule in `_work/alias_map.md` (`kind = pattern`).

**L6 – hypotheses** (signal `LLM`): synonyms, abbreviations, other naming conventions, the request's comments
(also non-English) → grep each guess (R2), then read the candidates and compare behavior with B1's
before → after sentence. A guess is only a lead: it never counts as evidence without a signal from L0–L4.

**L7 – nothing found: eliminate before concluding** (record which checks were done)
- macro-generated: `grep "${GOPT[@]}" -E '##|DEFINE_[A-Z_]*\(' "$ROOT"` near the anchored neighbors; parts of `$OLD` as macro args.
- encoding: for non-UTF-8 trees grep literals as bytes:
  `LC_ALL=C grep -a -rnF "$(printf '%s' "$LIT" | iconv -f UTF-8 -t SHIFT_JIS)" "$ROOT"` (use the encoding from `file -I`).
  `-a` is required: without it grep (and the `grep` wrapper of some agent shells) treats non-UTF-8 files as binary
  and silently skips them. Same for any grep of non-ASCII literals in non-UTF-8 trees (L3, R13).
- split / merged: R17 `possible SPLIT`, `size`.
- rewritten: stable anchors / data IDs of `$OLD` still present (L3) but no FUZZY/SIM match → `REWRITTEN`.
- removed: no anchor, no content match, and the linked ends no longer reference anything at that spot → `NOT_FOUND`
  with reason `removed` (B then sets latest state `REMOVED_IN_LATEST`).

**Signals → confidence** (no history exists; combine independent signals). Families: *relation* = `ALIAS`,
`EDGE`, `NEIGHBOR`; *content* = `FUZZY`, `ANCHOR`, `SIM`; *shape* = `SIG`; *naming* = `PATTERN`, `LLM`.
- `High`: `ALIAS`; or ≥1 relation + ≥1 content signal; or ≥3 agreeing signals from ≥2 families.
- `Medium`: 2 agreeing signals from 2 different families, not both naming (e.g. `SIM` + `SIG`, `FUZZY` + `PATTERN`).
- `Low`: a single signal, naming signals only, `SIM` below 0.6, or `TOO-SHORT` bodies with content signals only → ask.
- Downgrade one level when a link contradicts the candidate (cross-check fails, B2.3) or when two candidates are
  within 0.1 `blind` of each other with no other signal separating them.
Always list the signals in the evidence cell, e.g. `EDGE(N004 calls, SRC:src/print/render.c:88) + SIM 0.96 + SIG =`.
Old body spread over 2+ blocks → `SPLIT_SYMBOL`; 2+ old bodies inside one block → `MERGED_SYMBOL`.

## R13 – Data dependencies (search ALL file types, not only code)
```bash
grep -rnI -w --exclude-dir=.git "$TOKEN" "$ROOT"          # every text file: .c/.h, .csv, .xml, .json, .txt, .rc, .mk, linker scripts…
```
Checklist per kind:
- **String/message ID** (`STR_*`, `MSG_*`, resource IDs): the ID definition + the entry in **every** language/resource table.
- **Enum entry**: every array sized/indexed by the enum (`[X_COUNT]`, `[X_MAX]`), switch statements over it, tables in enum order.
- **Settings / NVRAM field**: struct field, default-value table, init/reset/factory-default function, version or
  layout number, checksum/CRC range, migration code, any range/limit table.
- **Registry entry**: menu/command/event/handler tables, dispatcher `case`, init sequence lists.
- **Config**: feature macros in config headers, Makefile/CMake defines, source lists, linker sections.
- **Data files**: tables, calibration/curve data, resource files referenced by name or by ID.

## R14 – Is a later change block related to the feature? (EXTENSION vs UNRELATED)
For a block of lines changed in latest source after the request (from `diff REQ-A-body latest-body`):
related signals –
1. the block's lines contain feature tokens (S names, feature macros, string IDs, `B_new_tokens.txt` project tokens);
2. the block is inside the feature's guard (R5);
3. the block edits or is within ±3 lines of the request's `+` lines;
4. comments in or next to the block naming the feature, the request or a request/ticket ID (R10 pattern).
≥1 of signals 1–3 (and none contradicting) → `EXTENSION` (new behavior) / `BUGFIX` (fixes feature lines) /
`REFACTOR` (renames/moves feature lines). None of them, and the block carries another feature's tokens/guard →
`UNRELATED`. Mixed or no signal → `UNCLEAR` (ask).

## R15 – Request link graph (Checkpoint A7)
Inputs: `_work/A_hunks.md` (owners), `_work/A_ranges/**` (R1 ranges), REQ-A (REQ-B for deleted items).
`$RA` = `$SOURCE_REQUEST/After`. Work only inside the request; endpoints outside it become `external` nodes.
```bash
# node names: owners of modification points + data items added on + lines
awk -F'|' 'NR>2{print $8}' "$W/A_hunks.md" | sed 's/ (.*//;s/^ *//;s/@.*//' | grep -v '^Not identified$' | sort -u > "$W/A_node_names.txt"  # 'symbol (kind)' column
#   then append the data items added on + lines (string IDs, enum entries, fields, macros) found while reading the hunks
# calls / reads / writes / registers / localizes / defaults / indexes: every use of a node name inside another node's range
while read -r n; do grep "${GOPT[@]}" -nw -- "$n" "$RA"; done < "$W/A_node_names.txt" > "$W/A_uses.txt"
#   for each hit: the enclosing range (A_ranges, R1) is the 'from' node; decide the type from the line:
#   'n(' → calls · inside an initializer table → registers · inside an enum-sized array / switch(case n) → indexes ·
#   in a language/resource table → localizes · in a default/init/reset function → defaults · 'x->n =' / 'n =' → writes · else reads
# declares: prototypes / externs of node names in headers
grep -rn --include='*.h' -E "^[^#].*[^A-Za-z0-9_](NAME)[[:space:]]*\(" "$RA"      # NAME = node name; one per node
# includes: request headers included by request files
grep -rn -E '^[[:space:]]*#[[:space:]]*include' "$RA" | grep -F -f <(find "$RA" -name '*.h' -exec basename {} \;)
# builds: request source files listed in build files
find "$RA" -type f \( -name Makefile -o -name '*.mk' -o -name CMakeLists.txt -o -name '*.cmake' \) -exec \
  grep -nF -f <(find "$RA" -name '*.c' -o -name '*.cpp' | xargs -n1 basename) {} +
# guards: R5 on each + line; nodes inside the same #if/#ifdef share a 'guards' edge with the macro node
# uses-external: R4 tokens of the node's + lines that are not node names and not standard/library
```
Each edge row: `from | type | to | REQ-A:path:line`. Stability classes are in `checkpoints/A-diff.md` A7.

## R16 – Fuzzy line grep (rename-tolerant)
Turns one source line into a POSIX ERE where only the identifiers that may have been renamed become wildcards;
literals, keywords, operators and unchanged names stay literal. Works with BSD and GNU grep.
```bash
P=$(python3 -I "$SK/scripts/fuzzy_line.py" --abstract-file "$W/B_feature_ids.txt" "$LINE")   # stderr: kept=… wild=… [WEAK]
grep "${GOPT[@]}" -nE -e "$P" "$ROOT"
```
- `B_feature_ids.txt` = names defined by the request (nodes of `A_links.md` with stability `medium`/`volatile`),
  one per line. Without `--abstract-file` every non-keyword identifier becomes a wildcard (weaker).
- Use only distinctive lines; a `WEAK` pattern (fewer than 3 literal tokens, e.g. `i = 0;`) is never a signal alone.
- One-line patterns miss statements split over several lines and reformatted logic: R17 covers those.
- No `python3`: build the pattern by hand – replace each feature identifier by `[A-Za-z_][A-Za-z0-9_]*`, escape
  `. [ ] ( ) * + ? { } | ^ $ \` as `[.]`…, and put `[[:space:]]*` between tokens.

## R17 – Rename-invariant similarity (whole body)
Compares one REQ-A block (function, table, struct/enum) with **every** top-level block of `$ROOT`. Deterministic,
standard-library Python, no embeddings. Comments and whitespace are ignored; every non-keyword identifier becomes
`$I` (so renames do not matter) while literals, keywords and operators are kept; 4-token shingles are compared by
containment (= share of the reference that is still present, so a function that grew after the request is not penalised).
```bash
python3 -I "$SK/scripts/similarity.py" --ref-file "$SOURCE_REQUEST/After/$P" --ref-name "$OLD" \
        --root "$ROOT" --feature-ids "$W/B_feature_ids.txt" --top 5          # or --ref-lines a-b ; --json
```
Columns: `blind` (containment, rename-proof), `named` (only feature ids abstracted; stricter), `size` (candidate /
reference tokens), `lits` (shared literals), `calls` (shared callee names), `sig` (`=` same parameter count and
return/storage tokens, `~` same count, `!` different). `TOO-SHORT` (< 15 tokens) → scores unreliable, not a `SIM` signal.
`possible SPLIT` → two blocks together cover ≥ 60 % of the reference.
Reading: `blind` ≥ 0.8 strong, 0.6–0.8 candidate, < 0.6 not the same block. `size` ≥ 2 with high `blind` → the block
grew a lot (EXTENSION) or absorbed other code (MERGED): read it. Limits: complete rewrites (no shared structure) and
heavy macro code are not detected; preprocessor lines are ignored.
No `python3` → skip R16/R17 and record `SIM/FUZZY not available (python3 missing)` in the evidence.
