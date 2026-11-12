# T1-rename-multi – rename/move/split in A_latest (B2 tracing)

Built by `tests/tools/make_t1_rename_multi.py` from `T0-toner-save`. REQ and B_latest are identical to T0; only
A_latest evolved after the request, and golden = T0 golden with the same evolution (the manual porter copies A_latest).

## Traps (all in A_latest, none visible in the request)
| # | Change after the request | Request name/path | A_latest | Stable anchors left for tracing |
|---|---|---|---|---|
| 1 | File moved + renamed | `src/features/toner_save/toner_save.{c,h}` | `src/features/eco/eco_mode.{c,h}` | includes in render.c / menu_table.c / pjl_commands.c / nv_settings.c, Makefile `SRCS +=` |
| 2 | Function prefix rename (4 functions) | `TonerSave_*` | `EcoMode_*` | menu table key `"TONER_SAVE"`, PJL keyword `"ECONOMODE"`, call in `Render_Page` under `SUPPORT_TONER_SAVE` |
| 3 | Settings field rename | `toner_save_level` | `eco_level` | `NV_LoadDefaults` sets it to `TONER_SAVE_OFF`; same slot in `NvSettings_t` |
| 4 | Function split | `TonerSave_ApplyDensity` | `EcoMode_ApplyDensity` + `static eco_effective_level()` | comment `fix #1234`, `Clamp(...)`, `k_percent[level]`, `Density_Scale` |
| 5 | Header guard rename | `TONER_SAVE_H` | `ECO_MODE_H` | file content |

Kept on purpose: `STR_TONER_SAVE`, `"Toner Save"`, `SUPPORT_TONER_SAVE`, enum `TONER_SAVE_*`, `k_percent`, `is_valid`.

## Expected tracing (Checkpoint B)
Grep by request name finds none of the 4 functions, the field or the two files. Expected path through the link graph:
1. `stable` nodes anchor by name: `STR_TONER_SAVE`, `SUPPORT_TONER_SAVE`, enum values, `"TONER_SAVE"`, `"ECONOMODE"`, Makefile.
2. EDGE `registers`: `g_menu_table` entry `"TONER_SAVE"` → `EcoMode_MenuHandler`; `g_pjl_table` entry `"ECONOMODE"` → `EcoMode_PjlSet`.
3. PATTERN `TonerSave_` → `EcoMode_` (2 High renames) → predicts `EcoMode_GetLevel`, `EcoMode_ApplyDensity`; confirmed by SIM/SIG/EDGE.
4. EDGE `calls` from `Render_Page` (under the guard) → `EcoMode_ApplyDensity`; R17 on the request body → `possible SPLIT` with `eco_effective_level`.
5. EDGE `defaults` in `NV_LoadDefaults` → `eco_level`; EDGE `includes`/`builds` → `src/features/eco/eco_mode.{c,h}`.
6. Cross-check: every `calls`/`registers` edge consistent under latest names. No blocker of type NOT_FOUND / REMOVED / GONE.
Machine-checked expectations: `golden/expected_anchor.json`.

## Golden insertion positions
Same as T0 (manual port), with latest names and paths:
- new files copied whole from A_latest at the A_latest path (`src/features/eco/eco_mode.{c,h}`, `src/print/density.{c,h}`);
- Makefile: B's existing `SRCS = …` lines untouched, two appended lines `SRCS += src/features/eco/eco_mode.c`, `SRCS += src/print/density.c`
  (manual style: append, never edit B's existing line – the open T0 failure);
- includes / table entries / NV field / defaults at the same relative place as in A_latest, as in T0.
