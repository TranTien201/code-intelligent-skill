# A_hunks – hunk + modification point inventory

Owner rule: `+` lines → After ranges (`A_ranges/*.after.txt`), lines outside ranges → R2. Blank separator lines inside an added file belong to the point before them. No `-` lines exist in this request (pure additions).

| H-id | file | hunk header | before range | after range | point | symbol (kind) | function_status | -lines | +lines | manifest No |
|---|---|---|---|---|---|---|---|---|---|---|
| H001 | `Makefile` | `@@ -2,7 +2,8 @@ MODEL ?= A` | - | L6 | p1 | N/A (non-code file) | unknown | 0 | 1 | 1 |
| H002 | `config/model_a.h` | `@@ -1,2 +1,3 @@` | - | L3 | p1 | SUPPORT_TONER_SAVE (macro) | added | 0 | 1 | 2 |
| H003 | `src/cmd/pjl_commands.c` | `@@ -1,6 +1,7 @@` | - | L4 | p1 | includes@src/cmd/pjl_commands.c (file scope) | modified | 0 | 1 | 3 |
| H004 | `src/cmd/pjl_commands.c` | `@@ -23,6 +24,7 @@` | - | L27 | p1 | g_pjl_table (table) | modified | 0 | 1 | 4 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | - | L1-L7 | p1 | includes@src/features/toner_save/toner_save.c (file scope) | added | 0 | 7 | 5 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | - | L8-L9 | p2 | k_percent (global) | added | 0 | 2 | 6 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | - | L10-L14 | p3 | is_valid (function) | added | 0 | 5 | 7 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | - | L15-L19 | p4 | TonerSave_GetLevel (function) | added | 0 | 5 | 8 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | - | L20-L27 | p5 | TonerSave_ApplyDensity (function) | added | 0 | 8 | 9 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | - | L28-L36 | p6 | TonerSave_MenuHandler (function) | added | 0 | 9 | 10 |
| H005 | `src/features/toner_save/toner_save.c` | `@@ -0,0 +1,40 @@` | - | L37-L40 | p7 | TonerSave_PjlSet (function) | added | 0 | 4 | 11 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | - | L1-L2 | p1 | TONER_SAVE_H (preprocessor) | added | 0 | 2 | 12 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | - | L3-L8 | p2 | TONER_SAVE_OFF/LOW/HIGH (enum) | added | 0 | 6 | 13 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | - | L9 | p3 | TonerSave_GetLevel (prototype) | added | 0 | 1 | 14 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | - | L10 | p4 | TonerSave_ApplyDensity (prototype) | added | 0 | 1 | 15 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | - | L11 | p5 | TonerSave_MenuHandler (prototype) | added | 0 | 1 | 16 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | - | L12 | p6 | TonerSave_PjlSet (prototype) | added | 0 | 1 | 17 |
| H006 | `src/features/toner_save/toner_save.h` | `@@ -0,0 +1,13 @@` | - | L13 | p7 | TONER_SAVE_H (preprocessor) | added | 0 | 1 | 18 |
| H007 | `src/panel/menu_table.c` | `@@ -1,10 +1,16 @@` | - | L4-L6 | p1 | SUPPORT_TONER_SAVE@src/panel/menu_table.c (preprocessor) | added | 0 | 3 | 19 |
| H007 | `src/panel/menu_table.c` | `@@ -1,10 +1,16 @@` | - | L11-L13 | p2 | g_menu_table (table) | modified | 0 | 3 | 20 |
| H008 | `src/print/render.c` | `@@ -1,10 +1,16 @@` | - | L3-L5 | p1 | SUPPORT_TONER_SAVE@src/print/render.c (preprocessor) | added | 0 | 3 | 21 |
| H008 | `src/print/render.c` | `@@ -1,10 +1,16 @@` | - | L11-L13 | p2 | Render_Page (function) | modified | 0 | 3 | 22 |
| H009 | `src/resources/strings.h` | `@@ -1,8 +1,9 @@` | - | L6 | p1 | StrId_t (enum) | modified | 0 | 1 | 23 |
| H010 | `src/resources/strings_en.c` | `@@ -3,6 +3,7 @@` | - | L6 | p1 | g_strings_en (table) | modified | 0 | 1 | 24 |
| H011 | `src/settings/nv_settings.c` | `@@ -1,4 +1,5 @@` | - | L2 | p1 | includes@src/settings/nv_settings.c (file scope) | modified | 0 | 1 | 25 |
| H012 | `src/settings/nv_settings.c` | `@@ -10,7 +11,8 @@ NvSettings_t *NV_GetSettings(void)` | - | L15 | p1 | NV_LoadDefaults (function) | modified | 0 | 1 | 26 |
| H013 | `src/settings/nv_settings.h` | `@@ -4,7 +4,8 @@` | - | L8 | p1 | NvSettings_t (struct) | modified | 0 | 1 | 27 |

Notes:
- H012 header text names `NV_GetSettings`, but the `+` line L15 lies in After range 11-18 `NV_LoadDefaults` (owner from ranges, not from the header).
- H006 p2: anonymous enum (no tag/typedef name) holding `TONER_SAVE_OFF`, `TONER_SAVE_LOW`, `TONER_SAVE_HIGH`; L8 is a blank separator.
- Preprocessor/file-scope owners in a single file are qualified with `@path` because the same owner name appears in several files.
- Totals: -0 / +74 (matches `git diff --no-index --numstat`).
