# Decision table (Checkpoint D port classes)

Inputs: B (anchoring, evolution, extensions, closure) and C (target state). Apply top to bottom; the first
matching row wins. `Interactive` = what to do in `interactive` mode; `Auto default` = `APPROVAL_MODE=auto`
behaviour (mark `AUTO-DECIDED`). **Content source by default = the port version from latest source (B5).**

| # | Condition | Port class | Action | Interactive | Auto default |
|---|---|---|---|---|---|
| 1 | Anchor `NOT_FOUND` / `REMOVED_IN_LATEST` / hunk `GONE` in latest source | `SOURCE_GONE` | Do not port blindly; maybe the feature was reverted or rewritten | **ask, stop** | port REQ-A version, HIGH risk flag |
| 2 | Any `Low` confidence or `RENAMED_CANDIDATE` (source or target) | `NEEDS_CONFIRMATION` | No code planned until confirmed | **ask, stop** | `Blocked` for that M |
| 3 | Change type `cosmetic` only | `SKIP_COSMETIC` | Port only if the symbol is ported anyway | plan | plan |
| 4 | Target state `SAME_AS_SOURCE` (incl. equal modulo aliases) | `SKIP_ALREADY_PRESENT` | No change; cite evidence | plan | plan |
| 5 | Evolution has `UNRELATED` blocks in a ported symbol | `TAKE_LATEST_PARTIAL` | Port request + extension/bugfix/refactor lines only; list excluded lines | **ask** | partial take, flag |
| 6 | Target state `SAME_AS_BEFORE` | `APPLY_PORT_VERSION` | Replace the symbol body with the port version (or 3-way merge, see E) | plan | plan |
| 7 | Target `MISSING`, item is a request symbol or `ext` | `COPY_NEW` | Copy the port version; add declaration/header entries as in source | plan (list `ext` items as *scope beyond request*) | plan, flag `ext` |
| 8 | Target `MISSING`, item is a code dependency | `COPY_DEPENDENCY` | Copy latest definition from `SOURCE_ROOT` | plan | plan |
| 9 | Target `MISSING`, item is a data dependency (string, table entry, default, resource, enum entry) | `ADD_DATA` | Add the entry in **every** required place (all languages, all tables sized by the enum, defaults, version/checksum) in target style | plan | plan |
| 10 | Ported code references a symbol the target has under another confirmed name (`RENAMED`/`MOVED`) | `ALIAS_ADAPT` | Rewrite only those identifiers/includes in the ported text per alias map; list each substitution | plan | plan, flag |
| 11 | Guard macro of a ported line not enabled in target | `ENABLE_GUARD` | Add the define where the target enables sibling features (cite it) | **ask**: enable in target? | add, flag |
| 12 | Target `DIVERGED` | `ADAPT_MERGE` | 3-way merge: base REQ-B, ours target, theirs port version; keep target-only lines | ask on any conflict | merge; conflict → `Blocked` for that P |
| 13 | `SIGNATURE_DIFF` and target symbol has target callers | `CONFLICT` | Options: (a) keep target symbol, adapt ported call sites; (b) change target symbol + all target callers; (c) add new symbol | **ask, stop** | (a), flag |
| 14 | `SIGNATURE_DIFF`, no target callers | `REPLACE` | Replace with port version | plan | plan |
| 15 | Change type `layout` on persistent/shared data (NVRAM, protocol, file format, enum values used as IDs) | `LAYOUT_RISK` | Port as in source; record offset/value shift as HIGH risk | **ask** | port + HIGH risk |
| 16 | Item is a `CONSUMER` (another source feature uses this one) | `REPORT_ONLY` | Never copy; list | plan | plan |
| 17 | Incoming registration needed for behavior and missing in target | `ADD_REGISTRATION` | Add the single entry/call the feature needs, in target table style | plan | plan |
| 18 | Non-code file (build, resource) needed for build/behavior | `NON_CODE` | Port the needed entry (e.g. add new .c to Makefile); otherwise report | plan | plan |
| 19 | Nothing above matches | `UNCLASSIFIED` | Do not guess | **ask** | `Blocked` |

Rules:
- Every P-id states its content source: `SRC:<path>:<lines>` (port version) or `REQ-A:<path>:<lines>` (only when row 1 chose it).
- An item may need several classes (e.g. `COPY_NEW` + `ALIAS_ADAPT`): create one M per class, all naming the same item.
- New source files must be added to the target build (R9) as their own P-id.
- "Adaptation" column: `none` for verbatim copy; otherwise the exact difference from the source text and why (alias, partial take, conflict option).
