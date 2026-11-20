# E_changes

| E-id | P-id | file | OUT-A lines | applied/skipped | note |
|---|---|---|---|---|---|
| E001 | P001 | src/print/density.h | 1-5 | applied | add-file `cp -p` SRC:src/print/density.h |
| E002 | P002 | src/print/density.c | 1-7 | applied | add-file `cp -p` SRC:src/print/density.c |
| E003 | P003 | src/util/math_util.h | 3 | applied | Clamp prototype → `int Clamp(int v, int lo, int hi);` |
| E004 | P004 | src/util/math_util.c | 3-8 | applied | Clamp body replaced with SRC:src/util/math_util.c:3-8 |
| E005 | P005 | src/features/toner_save/toner_save.h | 1-13 | applied | add-file `cp -p` SRC |
| E006 | P006 | src/features/toner_save/toner_save.c | 1-42 | applied | add-file `cp -p` SRC (incl. BUGFIX L7, L24) |
| E007 | P007 | config/model_b.h | 4 | applied | +`#define SUPPORT_TONER_SAVE 1` |
| E008 | P008 | src/resources/strings.h | 6 | applied | +`STR_TONER_SAVE,` (git merge-file, conflicts=0) |
| E009 | P009 | src/resources/strings_en.c | 6 | applied | +`[STR_TONER_SAVE] = "Toner Save",` (merge, conflicts=0) |
| E010 | P010 | src/settings/nv_settings.h | 8 | applied | +`int toner_save_level;` (merge, conflicts=0) |
| E011 | P011 | src/settings/nv_settings.c | 2 | applied | +include toner_save.h |
| E012 | P012 | src/settings/nv_settings.c | 15 | applied | +`g_settings.toner_save_level = TONER_SAVE_OFF;` (merge, conflicts=0) |
| E013 | P013 | src/print/render.c | 3-5 | applied | +guarded include |
| E014 | P014 | src/print/render.c | 11-13 | applied | +guarded `TonerSave_ApplyDensity` call (merge, conflicts=0) |
| E015 | P015 | src/panel/menu_table.c | 4-6 | applied | +guarded include (ECO block excluded) |
| E016 | P016 | src/panel/menu_table.c | 11-13 | applied | +guarded TONER_SAVE entry (ECO entry excluded) |
| E017 | P017 | src/cmd/pjl_commands.c | 4 | applied | +include toner_save.h |
| E018 | P018 | src/cmd/pjl_commands.c | 27 | applied | +`{ "ECONOMODE", TonerSave_PjlSet },` |
| E019 | P019 | Makefile | 2 | applied | +`src/print/density.c` in SRCS |
| E020 | P020 | Makefile | 6 | applied | +`SRCS += src/features/toner_save/toner_save.c` |

Merge inputs/outputs: `_work/merge/P0{08,09,10,12,14}.{base,ours,theirs,result}.txt`.
Hunk map (17 hunks in diffs/output.diff): Makefile@1→E019,E020; model_b.h@1→E007; pjl_commands.c@1→E017, @23→E018; toner_save.c→E006; toner_save.h→E005; menu_table.c@1→E015,E016; density.c→E002; density.h→E001; render.c@1→E013,E014; strings.h→E008; strings_en.c→E009; nv_settings.c@1→E011, @11→E012; nv_settings.h→E010; math_util.c→E004; math_util.h→E003.
