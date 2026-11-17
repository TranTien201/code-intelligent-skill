# E_changes

| E-id | P-id | file | OUT-A lines | applied/skipped | note |
|---|---|---|---|---|---|
| E001 | P001 | config/model_b.h | 4 | applied | insert-after |
| E002 | P002 | src/util/math_util.h | 3 | applied | replace |
| E003 | P003 | src/util/math_util.c | 3-5 | applied | replace3 |
| E004 | P004 | src/print/density.h | 1-5 | applied | add-file cp -p from SRC:src/print/density.h:1-5 |
| E005 | P005 | src/print/density.c | 1-7 | applied | add-file cp -p from SRC:src/print/density.c:1-7 |
| E006 | P006 | src/features/eco/eco_mode.h | 1-13 | applied | add-file cp -p from SRC:src/features/eco/eco_mode.h:1-13 |
| E007 | P007 | src/features/eco/eco_mode.c | 1-48 | applied | add-file cp -p from SRC:src/features/eco/eco_mode.c:1-20,28-48 |
| E008 | P008 | src/features/eco/eco_mode.c | 21-27 | applied | ext lines contained in cp -p copy (P007) |
| E009 | P009 | src/settings/nv_settings.h | 8 | applied | insert-after |
| E010 | P010 | src/resources/strings.h | 6 | applied | insert-after |
| E011 | P011 | src/resources/strings_en.c | 6 | applied | insert-after |
| E012 | P012 | src/settings/nv_settings.c | 2 | applied | insert-after |
| E013 | P013 | src/settings/nv_settings.c | 15 | applied | insert-after |
| E014 | P014 | src/cmd/pjl_commands.c | 4 | applied | insert-after |
| E015 | P015 | src/cmd/pjl_commands.c | 27 | applied | insert-after |
| E016 | P016 | src/panel/menu_table.c | 4-6 | applied | insert-after |
| E017 | P017 | src/panel/menu_table.c | 11-13 | applied | insert-after |
| E018 | P018 | src/print/render.c | 3-5 | applied | insert-after |
| E019 | P019 | src/print/render.c | 11-13 | applied | insert-after |
| E020 | P020 | Makefile | 6 | applied | insert-after |
| E021 | P021 | Makefile | 7 | applied | insert-after-P020 |

ADAPT_MERGE / APPLY check: `git merge-file -p ours base theirs` per file (`_work/merge/merge_log.txt`): 7/7 conflicts=0, result identical to After.
Verbatim check: 21/21 inserted texts equal D text.
