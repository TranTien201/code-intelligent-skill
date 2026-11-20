### Gate Result
PASS – 1 Files – 11/11 manifest files listed `analyzed`
PASS – 2 Symbol coverage – H001–H013 each in ≥1 S-id (S001–S026); S027 = ext
PASS – 3 Behavior – 27/27 S-ids have concrete before → after (values/conditions named)
PASS – 4 Anchoring complete – files 11/11, nodes 34/34, S-ids 27/27, H-ids 13/13 in `_work/B_anchor.md`
PASS – 5 Method and signals – every row names its method + signals with SRC:path:line; R17 scores in `_work/B_sim_raw.txt`; NAME anchors verified (kind + body; static `is_valid@src/panel/menu.c` rejected, blind 0.12); no anchor relies on LLM/PATTERN only
PASS – 6 Relocation evidence – 2 MOVED_FILE, 8 RENAMED (TONER_SAVE_H, 4 functions, 4 prototypes share rows, field), 3 MOVED_SYMBOL in `_work/alias_map.md`; 3 pattern rows
PASS – 7 Links cross-checked – 40/40 edges: consistent 38 / changed 2 / broken 0
PASS – 8 Loop finished – Iteration 2 anchored 0; Anchored Link Graph generated from final `B_anchor.md`
PASS – 9 No silent loss – H005 PARTIAL listed as blocker 1 with question; no NOT_FOUND/REWRITTEN/MACRO_GENERATED/REMOVED/GONE/Low
PASS – 10 Modulo aliases – `_work/B_aliased/` built after alias map; diff log `_work/B_aliased_vs_latest.txt`; hunk rows marked `(modulo aliases)`
PASS – 11 Evolution – 7 blocks classified (REFACTOR 1, BUGFIX 2, UNRELATED 1, UNCLEAR→AUTO-DECIDED UNRELATED 3, listed as blocker 2); partial takes S001, S018, S019 listed
PASS – 12 Extensions searched – patterns recorded in `_work/B_anchor.md` §Extension hits; 7 hits: 1 EXTENSION_NEW (S027), 6 CONSUMER
PASS – 13 Tokens – `_work/B_new_tokens.txt` from request + extension lines: 46 ids, 26 keyword/path/local/library, 20 project tokens = 14 S-id names + 6 deps/existing statics
PASS – 14 Code dependency evidence – 6 deps with SRC:path:line; depth 2, stop reasons stated
PASS – 15 Data dependencies – R13 checklist per kind (string ID, enum layout, NV field + defaults + version/CRC none, 2 registry entries, config macro, build entry, data files none)
PASS – 16 Incoming / guards / headers / tests – recorded; tests `none found` with commands
PASS – 17 Read-only – `find SOURCE_ROOT SOURCE_REQUEST -newer .start_marker` → 0 files
PASS – 18 Status row – B = Complete, Next approval gate = Awaiting Checkpoint C approval
