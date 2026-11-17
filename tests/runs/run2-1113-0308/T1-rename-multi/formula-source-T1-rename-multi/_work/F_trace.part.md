| H-id | S-id | M-id | P-id | E-id | Output hunk | Result |
|---|---|---|---|---|---|---|
| H001 | S001 | M007 | P020 | E020 | `Makefile` @@ -3,6 +3,8 @@ (OUT-A:Makefile:6) | ported (partial take, eco_report line excluded) |
| H002 | S002 | M006 | P001 | E001 | `config/model_b.h` @@ -1,3 +1,4 @@ (OUT-A:config/model_b.h:4) | ported (ENABLE_GUARD into model_b.h, AUTO-DECIDED) |
| H003 | S003 | M009 | P014 | E014 | `src/cmd/pjl_commands.c` @@ -1,6 +1,7 @@ | ported |
| H004 | S004 | M010 | P015 | E015 | `src/cmd/pjl_commands.c` @@ -23,6 +24,7 @@ | ported |
| H005 | S005–S011 | M001 | P007 | E007 | `src/features/eco/eco_mode.c` @@ -0,0 +1,48 @@ (L1-20, 28-48) | ported (latest names, BUGFIX logic) |
| H006 | S012–S017 | M003 | P006 | E006 | `src/features/eco/eco_mode.h` @@ -0,0 +1,13 @@ | ported |
| H007 | S018 | M011 | P016 | E016 | `src/panel/menu_table.c` @@ -1,10 +1,16 @@ (L4-6) | ported (partial take) |
| H007 | S019 | M012 | P017 | E017 | `src/panel/menu_table.c` @@ -1,10 +1,16 @@ (L11-13) | ported (partial take, FAX kept) |
| H008 | S020 | M013 | P018 | E018 | `src/print/render.c` @@ -1,10 +1,16 @@ (L3-5) | ported |
| H008 | S021 | M014 | P019 | E019 | `src/print/render.c` @@ -1,10 +1,16 @@ (L11-13) | ported (3-way merge, FAX kept) |
| H009 | S022 | M015 | P010 | E010 | `src/resources/strings.h` @@ -3,6 +3,7 @@ | ported (layout risk) |
| H010 | S023 | M016 | P011 | E011 | `src/resources/strings_en.c` @@ -3,6 +3,7 @@ | ported |
| H011 | S024 | M017 | P012 | E012 | `src/settings/nv_settings.c` @@ -1,4 +1,5 @@ | ported |
| H012 | S025 | M018 | P013 | E013 | `src/settings/nv_settings.c` @@ -11,6 +12,7 @@ | ported |
| H013 | S026 | M019 | P009 | E009 | `src/settings/nv_settings.h` @@ -5,6 +5,7 @@ | ported (NVRAM layout risk) |
| ext | S027 | M002 | P008 | E008 | `src/features/eco/eco_mode.c` @@ -0,0 +1,48 @@ (L21-27) | ported (ext) |
| dep | S008.d1 | M020 | – (no change needed) | – | – (TGT:src/settings/nv_settings.c:5 equal) | already present |
| dep | S009.d1–d3 | M004 | P004, P005 | E004, E005 | `src/print/density.h` @@ -0,0 +1,5 @@; `src/print/density.c` @@ -0,0 +1,7 @@ | ported (dependency) |
| dep | S009.d4 | M008 | P021 | E021 | `Makefile` @@ -3,6 +3,8 @@ (OUT-A:Makefile:7) | ported (build entry, AUTO-DECIDED style) |
| dep | S027.d1 | M005 | P002, P003 | E002, E003 | `src/util/math_util.h` @@ -1,4 +1,4 @@; `src/util/math_util.c` @@ -1,8 +1,8 @@ | ported (REPLACE, AUTO-DECIDED) |
| dep | S010.d1 | M020 | – (no change needed) | – | – (TGT:src/core/log.c:4 equal) | already present |
| dep | S010.d2 | M020 | – (no change needed) | – | – (TGT:src/resources/strings_en.c:10 equal) | already present |
| consumer | eco_report, main (B4) | M021 | – (REPORT_ONLY) | – | – | report only |

Counts: 13 H-ids in 15 rows → ported 15; ext ported 1; dependencies: ported 3, already present 3; report only 1; blocked 0. 17/17 output hunks covered.
