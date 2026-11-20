# alias_map (request → latest source → target)
Target column is filled in Checkpoint C.

| kind (file/symbol/pattern) | request | latest source | target | method | evidence (R11/R12 signals) | confidence |
|---|---|---|---|---|---|---|
| file | src/features/toner_save/toner_save.c | src/features/eco/eco_mode.c | MISSING (new file, copy) | R11 + EDGE | R11c content 58% (next 8%); EDGE builds SRC:Makefile:6; includes eco_mode.h at SRC:src/features/eco/eco_mode.c:2; all 6 functions + k_percent found inside by SIM/NAME | High |
| file | src/features/toner_save/toner_save.h | src/features/eco/eco_mode.h | MISSING (new file, copy) | R11 + EDGE | R11c 45% (next 9%); EDGE includes from anchored files SRC:src/cmd/pjl_commands.c:4, SRC:src/panel/menu_table.c:5, SRC:src/print/render.c:4, SRC:src/settings/nv_settings.c:2 (same slot as REQ-A include) | High |
| symbol | TONER_SAVE_H | ECO_MODE_H | MISSING | EDGE | guard of moved header SRC:src/features/eco/eco_mode.h:1-2,13; same position as REQ-A:src/features/toner_save/toner_save.h:1-2,13 | High |
| symbol | TonerSave_GetLevel | EcoMode_GetLevel | MISSING | EDGE + FUZZY | EDGE declares slot 1 SRC:src/features/eco/eco_mode.h:9; FUZZY `return NV_GetSettings()->…;` SRC:src/features/eco/eco_mode.c:18; SIM 1.00 (TOO-SHORT) + SIG = | High |
| symbol | TonerSave_ApplyDensity | EcoMode_ApplyDensity | MISSING | EDGE + SIM | EDGE calls from Render_Page SRC:src/print/render.c:12; declares slot 2 SRC:src/features/eco/eco_mode.h:10; SIM 0.71 + SIG = SRC:src/features/eco/eco_mode.c:28-34 | High |
| symbol | TonerSave_MenuHandler | EcoMode_MenuHandler | MISSING | EDGE + SIM | EDGE registers "TONER_SAVE" SRC:src/panel/menu_table.c:15; SIM 1.00 + SIG = SRC:src/features/eco/eco_mode.c:36-43; FUZZY SRC:src/features/eco/eco_mode.c:40 | High |
| symbol | TonerSave_PjlSet | EcoMode_PjlSet | MISSING | EDGE + SIG + PATTERN | EDGE registers "ECONOMODE" SRC:src/cmd/pjl_commands.c:27; SIG =; SIM 1.00 (TOO-SHORT); PATTERN TonerSave_→EcoMode_; calls EcoMode_MenuHandler SRC:src/features/eco/eco_mode.c:47 | High |
| symbol | toner_save_level (NvSettings_t field) | eco_level | MISSING | EDGE + FUZZY | EDGE declares: same slot between duplex/language SRC:src/settings/nv_settings.h:8; defaults SRC:src/settings/nv_settings.c:15; FUZZY (non-WEAK) SRC:src/features/eco/eco_mode.c:18, :40 | High |
| symbol | is_valid@src/features/toner_save/toner_save.c | is_valid@src/features/eco/eco_mode.c | MISSING (TGT:src/panel/menu.c:4 is an unrelated static) | NAME | moved with file SRC:src/features/eco/eco_mode.c:11-14, SIM 1.00 SIG =; NOT is_valid@src/panel/menu.c:5 (blind 0.12, unrelated) | High |
| symbol | k_percent | k_percent | MISSING | NAME | moved with file SRC:src/features/eco/eco_mode.c:9 (lits 3/3) | High |
| pattern | TonerSave_* | EcoMode_* | no target naming rule (feature absent) | PATTERN | 4 pairs: GetLevel/ApplyDensity/MenuHandler/PjlSet (rows above) | High |
| pattern | features/toner_save/toner_save.{c,h} | features/eco/eco_mode.{c,h} | same path in target (new) | PATTERN | 2 files (rows above); include lines SRC:src/cmd/pjl_commands.c:4, SRC:src/panel/menu_table.c:5, SRC:src/print/render.c:4, SRC:src/settings/nv_settings.c:2 | High |
| pattern | toner_save (identifier word) → eco / eco_mode | toner_save_level→eco_level, TONER_SAVE_H→ECO_MODE_H | n/a | PATTERN | NOT applied to TONER_SAVE_OFF/LOW/HIGH, STR_TONER_SAVE, SUPPORT_TONER_SAVE, "TONER_SAVE" (unchanged by name, SRC:src/features/eco/eco_mode.h:4-6, SRC:src/resources/strings.h:6, SRC:config/model_a.h:3, SRC:src/panel/menu_table.c:15) | High |


C additions (latest → target):

| kind (file/symbol/pattern) | request | latest source | target | method | evidence (R11/R12 signals) | confidence |
|---|---|---|---|---|---|---|
| symbol | – | Clamp(int v, int lo, int hi) SRC:src/util/math_util.c:3 | Clamp(int v, int hi) TGT:src/util/math_util.c:3 | NAME | same name, SIGNATURE_DIFF (2 vs 3 params) | High |
| file | – | src/print/density.{c,h} | MISSING | R11 | basename 0 hits, R17 ≤ 0.15 | High |