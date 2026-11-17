| E001 | P001 | `config/model_b.h`:4 | add `#define SUPPORT_TONER_SAVE 1` after SUPPORT_FAX | applied |
| E002 | P002 | `src/util/math_util.h`:3 | prototype → `int Clamp(int v, int lo, int hi);` | applied |
| E003 | P003 | `src/util/math_util.c`:3-5 | Clamp signature + lower bound `lo` (2 lines replaced) | applied |
| E004 | P004 | `src/print/density.h`:1-5 | new file density.h (cp -p) | applied |
| E005 | P005 | `src/print/density.c`:1-7 | new file density.c (cp -p) | applied |
| E006 | P006 | `src/features/eco/eco_mode.h`:1-13 | new file eco_mode.h (cp -p) | applied |
| E007 | P007 | `src/features/eco/eco_mode.c`:1-48 | new file eco_mode.c (cp -p, request symbols) | applied |
| E008 | P008 | `src/features/eco/eco_mode.c`:21-27 | ext eco_effective_level L21-27 (in same copy) | applied |
| E009 | P009 | `src/settings/nv_settings.h`:8 | + `int eco_level;` after duplex | applied |
| E010 | P010 | `src/resources/strings.h`:6 | + `STR_TONER_SAVE,` after STR_DUPLEX | applied |
| E011 | P011 | `src/resources/strings_en.c`:6 | + `[STR_TONER_SAVE] = "Toner Save",` | applied |
| E012 | P012 | `src/settings/nv_settings.c`:2 | + include eco_mode.h | applied |
| E013 | P013 | `src/settings/nv_settings.c`:15 | + `g_settings.eco_level = TONER_SAVE_OFF;` | applied |
| E014 | P014 | `src/cmd/pjl_commands.c`:4 | + include eco_mode.h | applied |
| E015 | P015 | `src/cmd/pjl_commands.c`:27 | + `{ "ECONOMODE", EcoMode_PjlSet },` | applied |
| E016 | P016 | `src/panel/menu_table.c`:4-6 | + guarded include (3 lines) | applied |
| E017 | P017 | `src/panel/menu_table.c`:11-13 | + guarded menu entry TONER_SAVE (3 lines) | applied |
| E018 | P018 | `src/print/render.c`:3-5 | + guarded include (3 lines) | applied |
| E019 | P019 | `src/print/render.c`:11-13 | + guarded `density = EcoMode_ApplyDensity(density);` (3 lines) | applied |
| E020 | P020 | `Makefile`:6 | + `SRCS += src/features/eco/eco_mode.c` | applied |
| E021 | P021 | `Makefile`:7 | + `SRCS += src/print/density.c` | applied |
