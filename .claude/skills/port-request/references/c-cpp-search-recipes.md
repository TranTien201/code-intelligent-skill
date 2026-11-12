# Search recipes (C/C++ and similar)

Copy-paste commands. `$ROOT` = the root searched, `$S` = symbol name, `$F` = file.
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
Score ≥ 60 % → strong candidate; 30–60 % → candidate (maybe `SPLIT_FILE`: check whether 2 candidates together
cover the file); < 30 % → not the same file. The `ref.ids` are the *rarest* long identifiers of the file.

## R12 – Find a renamed / moved / split symbol
`$OLD` = old name, body from REQ-A (or from source for target lookup).
```bash
# a. compatibility alias or wrapper
grep "${GOPT[@]}" -E "#[[:space:]]*define[[:space:]]+$OLD[[:space:](]" "$ROOT"
grep "${GOPT[@]}" -B2 -A6 -E "^[A-Za-z_].*[^A-Za-z0-9_]$OLD[[:space:]]*\(" "$ROOT" | grep -E 'return .*\('   # thin wrapper calling the new name
# b. neighbor anchor: in the reference file, note the symbols defined just before and after $OLD (R1 ranges);
#    find those neighbors in $ROOT (by name); the unknown symbol between them is a candidate.
#    Same for the prototype in the header and for entries in registration tables (same slot/position).
# c0. signature shape: same return type, same parameter count/types, same static/extern → supports a candidate
# c. caller anchor: take a caller of $OLD in REQ-A that still exists in $ROOT (by name or via R11/R12),
#    read the same call site in $ROOT; the function called at that position is the candidate.
# d. body similarity: extract candidate bodies (R1) and compare normalized lines with $OLD's body
norm_body(){ sed -n "$2,$3p" "$1" | sed -e 's://.*$::' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' | grep -vE '^[{}]*$' | sort -u; }
#    similarity = shared lines / lines of $OLD body (use comm -12 as in R11)
# e. distinctive literals (R8)
```
Evidence → confidence (no history available, so combine independent signals):
- `High`: identical normalized body under another name; or compat alias/wrapper (a); or ≥3 signals agree
  (caller anchor, neighbor anchor, signature shape, similarity ≥ 60 %).
- `Medium`: 2 agreeing signals, one of them similarity ≥ 60 % or caller anchor.
- `Low`: 1 signal only (literal only, similarity < 60 %, name resemblance) → ask the user.
Always list the signals used in the evidence cell.
If the old body is found spread over 2+ functions → `SPLIT_SYMBOL`; 2+ old bodies inside one → `MERGED_SYMBOL`.

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
