| No | file | file_status | function | function_status | Modified_line_before | Modified_line_after |
|---:|---|---|---|---|---|---|
| 1 | `Makefile` | modified | N/A (non-code file) | unknown | N/A | N/A |
| 2 | `config/model_a.h` | modified | SUPPORT_TONER_SAVE (macro) | added | N/A | L3: `#define SUPPORT_TONER_SAVE 1` |
| 3 | `src/cmd/pjl_commands.c` | modified | file scope (file scope) | modified | N/A | L4: `#include "../features/toner_save/toner_save.h"` |
| 4 | `src/cmd/pjl_commands.c` | modified | g_pjl_table (table) | modified | N/A | L27: `    { "ECONOMODE", TonerSave_PjlSet },` |
| 5 | `src/features/toner_save/toner_save.c` | added | file scope (file scope) | added | N/A | L1: `#include <stdlib.h>`<br>L2: `#include "toner_save.h"`<br>… (+5 lines, H005) |
| 6 | `src/features/toner_save/toner_save.c` | added | k_percent (global) | added | N/A | L8: `static const int k_percent[] = { 100, 80, 60 };`<br>L9: (blank) |
| 7 | `src/features/toner_save/toner_save.c` | added | is_valid (function) | added | N/A | L10: `static int is_valid(int level)`<br>L11: `{`<br>… (+3 lines, H005) |
| 8 | `src/features/toner_save/toner_save.c` | added | TonerSave_GetLevel (function) | added | N/A | L15: `int TonerSave_GetLevel(void)`<br>L16: `{`<br>… (+3 lines, H005) |
| 9 | `src/features/toner_save/toner_save.c` | added | TonerSave_ApplyDensity (function) | added | N/A | L20: `int TonerSave_ApplyDensity(int density)`<br>L21: `{`<br>… (+6 lines, H005) |
| 10 | `src/features/toner_save/toner_save.c` | added | TonerSave_MenuHandler (function) | added | N/A | L28: `int TonerSave_MenuHandler(int key)`<br>L29: `{`<br>… (+7 lines, H005) |
| 11 | `src/features/toner_save/toner_save.c` | added | TonerSave_PjlSet (function) | added | N/A | L37: `int TonerSave_PjlSet(const char *arg)`<br>L38: `{`<br>… (+2 lines, H005) |
| 12 | `src/features/toner_save/toner_save.h` | added | TONER_SAVE_H (preprocessor) | added | N/A | L1: `#ifndef TONER_SAVE_H`<br>L2: `#define TONER_SAVE_H` |
| 13 | `src/features/toner_save/toner_save.h` | added | TONER_SAVE_OFF/LOW/HIGH (enum) | added | N/A | L3: `enum {`<br>L4: `    TONER_SAVE_OFF = 0,`<br>… (+4 lines, H006) |
| 14 | `src/features/toner_save/toner_save.h` | added | TonerSave_GetLevel (prototype) | added | N/A | L9: `int TonerSave_GetLevel(void);` |
| 15 | `src/features/toner_save/toner_save.h` | added | TonerSave_ApplyDensity (prototype) | added | N/A | L10: `int TonerSave_ApplyDensity(int density);` |
| 16 | `src/features/toner_save/toner_save.h` | added | TonerSave_MenuHandler (prototype) | added | N/A | L11: `int TonerSave_MenuHandler(int key);` |
| 17 | `src/features/toner_save/toner_save.h` | added | TonerSave_PjlSet (prototype) | added | N/A | L12: `int TonerSave_PjlSet(const char *arg);` |
| 18 | `src/features/toner_save/toner_save.h` | added | TONER_SAVE_H (preprocessor) | added | N/A | L13: `#endif` |
| 19 | `src/panel/menu_table.c` | modified | file scope (file scope) | modified | N/A | L4: `#ifdef SUPPORT_TONER_SAVE`<br>L5: `#include "../features/toner_save/toner_save.h"`<br>L6: `#endif` |
| 20 | `src/panel/menu_table.c` | modified | g_menu_table (table) | modified | N/A | L11: `#ifdef SUPPORT_TONER_SAVE`<br>L12: `    { "TONER_SAVE", TonerSave_MenuHandler },`<br>L13: `#endif` |
| 21 | `src/print/render.c` | modified | file scope (file scope) | modified | N/A | L3: `#ifdef SUPPORT_TONER_SAVE`<br>L4: `#include "../features/toner_save/toner_save.h"`<br>L5: `#endif` |
| 22 | `src/print/render.c` | modified | Render_Page (function) | modified | N/A | L11: `#ifdef SUPPORT_TONER_SAVE`<br>L12: `    density = TonerSave_ApplyDensity(density);`<br>L13: `#endif` |
| 23 | `src/resources/strings.h` | modified | StrId_t (enum) | modified | N/A | L6: `    STR_TONER_SAVE,` |
| 24 | `src/resources/strings_en.c` | modified | g_strings_en (table) | modified | N/A | L6: `    [STR_TONER_SAVE] = "Toner Save",` |
| 25 | `src/settings/nv_settings.c` | modified | file scope (file scope) | modified | N/A | L2: `#include "../features/toner_save/toner_save.h"` |
| 26 | `src/settings/nv_settings.c` | modified | NV_LoadDefaults (function) | modified | N/A | L15: `    g_settings.toner_save_level = TONER_SAVE_OFF;` |
| 27 | `src/settings/nv_settings.h` | modified | NvSettings_t (struct) | modified | N/A | L8: `    int toner_save_level;` |
