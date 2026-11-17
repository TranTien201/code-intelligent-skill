# alias_map
| kind (file/symbol) | request | latest source | target | evidence (R11/R12) | confidence |
|---|---|---|---|---|---|
| file | config/model_a.h | config/model_a.h | config/model_b.h | R11b include anchor: TGT:config/model_config.h:5-6 includes model_b.h for MODEL_B (same slot as model_a.h for MODEL_A, SRC:config/model_config.h:3-4); TGT:Makefile:1 `MODEL ?= B`; R11c similarity 1/3 lines (`SUPPORT_DUPLEX`) + same `MODEL_NAME` key; R11a basename: no model_a.h in TGT | Medium |
| (symbols) | all request symbols | same names (B: no renames) | same names where present (no target renames found) | C_trace.md | High |
