# alias_map
| kind (file/symbol/pattern) | request | latest source | target | method | evidence (R11/R12 signals) | confidence |
|---|---|---|---|---|---|---|
| (none) | – | – | – | – | B: every request file/symbol found by exact name at the same path in SRC (B_anchor.md); no renames, no moves, no rename pattern | – |
| file | config/model_a.h | config/model_a.h | config/model_b.h | EDGE + ANCHOR | EDGE: TGT:config/model_config.h:5-6 includes model_b.h in the slot where SRC:config/model_config.h:3-4 includes model_a.h (file identical); target model = B (TGT:Makefile:1); ANCHOR: shared lines `MODEL_NAME`, `SUPPORT_DUPLEX 1` (TGT:config/model_b.h:1-2) | High |
| symbol | (all other names) | same | same (or MISSING) | NAME | C_trace.md | High |
