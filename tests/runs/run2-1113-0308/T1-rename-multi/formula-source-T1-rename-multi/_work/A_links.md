# A_links – request link graph (from REQ-A only)

## Nodes
| N-id | name | kind | stability (stable/medium/volatile) | def at (REQ-A:path:line) | H-ids / S-id | component |
|---|---|---|---|---|---|---|
| N001 | SUPPORT_TONER_SAVE | config-macro | stable | REQ-A:config/model_a.h:3 | H002 | C1 |
| N002 | Makefile | build-file | stable | REQ-A:Makefile:6 | H001 | C1 |
| N003 | TONER_SAVE_H | preprocessor | stable | REQ-A:src/features/toner_save/toner_save.h:1 | H006 | C1 |
| N004 | TONER_SAVE_OFF/LOW/HIGH | enum | medium | REQ-A:src/features/toner_save/toner_save.h:3 | H006 | C1 |
| N005 | k_percent | global | medium | REQ-A:src/features/toner_save/toner_save.c:8 | H005 | C1 |
| N006 | is_valid | function | volatile | REQ-A:src/features/toner_save/toner_save.c:10 | H005 | C1 |
| N007 | TonerSave_GetLevel | function | volatile | REQ-A:src/features/toner_save/toner_save.c:15 | H005 | C1 |
| N008 | TonerSave_ApplyDensity | function | volatile | REQ-A:src/features/toner_save/toner_save.c:20 | H005 | C1 |
| N009 | TonerSave_MenuHandler | function | volatile | REQ-A:src/features/toner_save/toner_save.c:28 | H005 | C1 |
| N010 | TonerSave_PjlSet | function | volatile | REQ-A:src/features/toner_save/toner_save.c:37 | H005 | C1 |
| N011 | g_pjl_table | table | medium | REQ-A:src/cmd/pjl_commands.c:24 | H004 | C1 |
| N012 | "ECONOMODE" | table-entry | stable | REQ-A:src/cmd/pjl_commands.c:27 | H004 | C1 |
| N013 | g_menu_table | table | medium | REQ-A:src/panel/menu_table.c:8 | H007 | C1 |
| N014 | "TONER_SAVE" | table-entry | stable | REQ-A:src/panel/menu_table.c:12 | H007 | C1 |
| N015 | Render_Page | function | volatile | REQ-A:src/print/render.c:8 | H008 | C1 |
| N016 | StrId_t | enum | medium | REQ-A:src/resources/strings.h:3 | H009 | C1 |
| N017 | STR_TONER_SAVE | string-id | stable | REQ-A:src/resources/strings.h:6 | H009 | C1 |
| N018 | g_strings_en | table | medium | REQ-A:src/resources/strings_en.c:3 | H010 | C1 |
| N019 | NvSettings_t | struct | medium | REQ-A:src/settings/nv_settings.h:5 | H013 | C1 |
| N020 | toner_save_level | nv-field | stable | REQ-A:src/settings/nv_settings.h:8 | H013 | C1 |
| N021 | NV_LoadDefaults | function | volatile | REQ-A:src/settings/nv_settings.c:11 | H012 | C1 |
| N022 | file scope@src/cmd/pjl_commands.c | file scope | medium | REQ-A:src/cmd/pjl_commands.c:4 | H003 | C1 |
| N023 | file scope@src/features/toner_save/toner_save.c | file scope | medium | REQ-A:src/features/toner_save/toner_save.c:1 | H005 | C1 |
| N024 | file scope@src/panel/menu_table.c | file scope | medium | REQ-A:src/panel/menu_table.c:4 | H007 | C1 |
| N025 | file scope@src/print/render.c | file scope | medium | REQ-A:src/print/render.c:3 | H008 | C1 |
| N026 | file scope@src/settings/nv_settings.c | file scope | medium | REQ-A:src/settings/nv_settings.c:2 | H011 | C1 |
| N027 | TonerSave_GetLevel (prototype) | prototype | volatile | REQ-A:src/features/toner_save/toner_save.h:9 | H006 | C1 |
| N028 | TonerSave_ApplyDensity (prototype) | prototype | volatile | REQ-A:src/features/toner_save/toner_save.h:10 | H006 | C1 |
| N029 | TonerSave_MenuHandler (prototype) | prototype | volatile | REQ-A:src/features/toner_save/toner_save.h:11 | H006 | C1 |
| N030 | TonerSave_PjlSet (prototype) | prototype | volatile | REQ-A:src/features/toner_save/toner_save.h:12 | H006 | C1 |
| N031 | NV_GetSettings | external | medium | outside request | - | C1 |
| N032 | Density_Scale | external | medium | outside request | - | C1 |
| N033 | Log_Info | external | medium | outside request | - | C1 |
| N034 | Str_Get | external | medium | outside request | - | C1 |

## Edges
| from (N-id) | type | to (N-id) | evidence (REQ-A:path:line) |
|---|---|---|---|
| N002 | builds | N023 | REQ-A:Makefile:6 |
| N023 | includes | N003 | REQ-A:src/features/toner_save/toner_save.c:2 |
| N022 | includes | N003 | REQ-A:src/cmd/pjl_commands.c:4 |
| N024 | includes | N003 | REQ-A:src/panel/menu_table.c:5 |
| N025 | includes | N003 | REQ-A:src/print/render.c:4 |
| N026 | includes | N003 | REQ-A:src/settings/nv_settings.c:2 |
| N001 | guards | N024 | REQ-A:src/panel/menu_table.c:4 |
| N001 | guards | N014 | REQ-A:src/panel/menu_table.c:11 |
| N001 | guards | N025 | REQ-A:src/print/render.c:3 |
| N001 | guards | N015 | REQ-A:src/print/render.c:11 |
| N003 | guards | N004 | REQ-A:src/features/toner_save/toner_save.h:1 |
| N011 | registers | N012 | REQ-A:src/cmd/pjl_commands.c:27 |
| N012 | registers | N010 | REQ-A:src/cmd/pjl_commands.c:27 |
| N013 | registers | N014 | REQ-A:src/panel/menu_table.c:12 |
| N014 | registers | N009 | REQ-A:src/panel/menu_table.c:12 |
| N015 | calls | N008 | REQ-A:src/print/render.c:12 |
| N008 | calls | N007 | REQ-A:src/features/toner_save/toner_save.c:22 |
| N008 | calls | N006 | REQ-A:src/features/toner_save/toner_save.c:23 |
| N008 | reads | N005 | REQ-A:src/features/toner_save/toner_save.c:25 |
| N008 | uses-external | N032 | REQ-A:src/features/toner_save/toner_save.c:25 |
| N009 | calls | N006 | REQ-A:src/features/toner_save/toner_save.c:30 |
| N009 | writes | N020 | REQ-A:src/features/toner_save/toner_save.c:32 |
| N009 | uses-external | N031 | REQ-A:src/features/toner_save/toner_save.c:32 |
| N009 | uses-external | N033 | REQ-A:src/features/toner_save/toner_save.c:33 |
| N009 | uses-external | N034 | REQ-A:src/features/toner_save/toner_save.c:33 |
| N009 | reads | N017 | REQ-A:src/features/toner_save/toner_save.c:33 |
| N010 | calls | N009 | REQ-A:src/features/toner_save/toner_save.c:39 |
| N007 | reads | N020 | REQ-A:src/features/toner_save/toner_save.c:17 |
| N007 | uses-external | N031 | REQ-A:src/features/toner_save/toner_save.c:17 |
| N006 | reads | N004 | REQ-A:src/features/toner_save/toner_save.c:12 |
| N021 | defaults | N020 | REQ-A:src/settings/nv_settings.c:15 |
| N021 | reads | N004 | REQ-A:src/settings/nv_settings.c:15 |
| N019 | declares | N020 | REQ-A:src/settings/nv_settings.h:8 |
| N016 | declares | N017 | REQ-A:src/resources/strings.h:6 |
| N018 | localizes | N017 | REQ-A:src/resources/strings_en.c:6 |
| N018 | indexes | N016 | REQ-A:src/resources/strings_en.c:3 |
| N027 | declares | N007 | REQ-A:src/features/toner_save/toner_save.h:9 |
| N028 | declares | N008 | REQ-A:src/features/toner_save/toner_save.h:10 |
| N029 | declares | N009 | REQ-A:src/features/toner_save/toner_save.h:11 |
| N030 | declares | N010 | REQ-A:src/features/toner_save/toner_save.h:12 |

Isolated: none
Components: C1 = {N001–N034} (single connected component: every request piece is linked through the toner_save.h include edges, the SUPPORT_TONER_SAVE guard and the toner_save_level / STR_TONER_SAVE data items)
