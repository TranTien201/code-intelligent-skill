# A_hunks

| H-id | file | hunk header | before range | after range | point | symbol (kind) | function_status | -lines | +lines | manifest No |
|---|---|---|---|---|---|---|---|---|---|---|
| H001 | `Makefile` | `@@ -2,7 +2,8 @@ MODEL ?= A` | 2,7 | 2,8 | p1 | N/A (non-code file) | unknown | 0 | 1 (L6-L6) | 1 |
| H002 | `config/model_a.h` | `@@ -1,2 +1,3 @@` | 1,2 | 1,3 | p1 | SUPPORT_TONER_SAVE (macro) | added | 0 | 1 (L3-L3) | 2 |
| H003 | `src/cmd/pjl_commands.c` | `@@ -1,6 +1,7 @@` | 1,6 | 1,7 | p1 | file scope (file scope) | modified | 0 | 1 (L4-L4) | 3 |
| H004 | `src/cmd/pjl_commands.c` | `@@ -23,6 +24,7 @@` | 23,6 | 24,7 | p1 | g_pjl_table (table) | modified | 0 | 1 (L27-L27) | 4 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | 0,0 | 1,40 | p1 | file scope (file scope) | added | 0 | 7 (L1-L7) | 5 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | 0,0 | 1,40 | p2 | k_percent (global) | added | 0 | 2 (L8-L9) | 6 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | 0,0 | 1,40 | p3 | is_valid (function) | added | 0 | 5 (L10-L14) | 7 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | 0,0 | 1,40 | p4 | TonerSave_GetLevel (function) | added | 0 | 5 (L15-L19) | 8 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | 0,0 | 1,40 | p5 | TonerSave_ApplyDensity (function) | added | 0 | 8 (L20-L27) | 9 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | 0,0 | 1,40 | p6 | TonerSave_MenuHandler (function) | added | 0 | 9 (L28-L36) | 10 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | 0,0 | 1,40 | p7 | TonerSave_PjlSet (function) | added | 0 | 4 (L37-L40) | 11 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | 0,0 | 1,13 | p1 | TONER_SAVE_H (preprocessor) | added | 0 | 2 (L1-L2) | 12 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | 0,0 | 1,13 | p2 | TONER_SAVE_OFF/LOW/HIGH (enum) | added | 0 | 6 (L3-L8) | 13 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | 0,0 | 1,13 | p3 | TonerSave_GetLevel (prototype) | added | 0 | 1 (L9-L9) | 14 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | 0,0 | 1,13 | p4 | TonerSave_ApplyDensity (prototype) | added | 0 | 1 (L10-L10) | 15 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | 0,0 | 1,13 | p5 | TonerSave_MenuHandler (prototype) | added | 0 | 1 (L11-L11) | 16 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | 0,0 | 1,13 | p6 | TonerSave_PjlSet (prototype) | added | 0 | 1 (L12-L12) | 17 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | 0,0 | 1,13 | p7 | TONER_SAVE_H (preprocessor) | added | 0 | 1 (L13-L13) | 18 |
| H007 | `src/panel/menu_table.c` | `@@ -1,10 +1,16 @@` | 1,10 | 1,16 | p1 | file scope (file scope) | modified | 0 | 3 (L4-L6) | 19 |
| H007 | `src/panel/menu_table.c` | `@@ -1,10 +1,16 @@` | 1,10 | 1,16 | p2 | g_menu_table (table) | modified | 0 | 3 (L11-L13) | 20 |
| H008 | `src/print/render.c` | `@@ -1,10 +1,16 @@` | 1,10 | 1,16 | p1 | file scope (file scope) | modified | 0 | 3 (L3-L5) | 21 |
| H008 | `src/print/render.c` | `@@ -1,10 +1,16 @@` | 1,10 | 1,16 | p2 | Render_Page (function) | modified | 0 | 3 (L11-L13) | 22 |
| H009 | `src/resources/strings.h` | `@@ -3,6 +3,7 @@` | 3,6 | 3,7 | p1 | StrId_t (enum) | modified | 0 | 1 (L6-L6) | 23 |
| H010 | `src/resources/strings_en.c` | `@@ -1,8 +1,9 @@` | 1,8 | 1,9 | p1 | g_strings_en (table) | modified | 0 | 1 (L6-L6) | 24 |
| H011 | `src/settings/nv_settings.c` | `@@ -1,4 +1,5 @@` | 1,4 | 1,5 | p1 | file scope (file scope) | modified | 0 | 1 (L2-L2) | 25 |
| H012 | `src/settings/nv_settings.c` | `@@ -10,7 +11,8 @@` | 10,7 | 11,8 | p1 | NV_LoadDefaults (function) | modified | 0 | 1 (L15-L15) | 26 |
| H013 | `src/settings/nv_settings.h` | `@@ -4,7 +4,8 @@` | 4,7 | 4,8 | p1 | NvSettings_t (struct) | modified | 0 | 1 (L8-L8) | 27 |

All points are pure additions (0 `-` lines). Blank `+` lines are attached to the preceding point (H005, H006).
