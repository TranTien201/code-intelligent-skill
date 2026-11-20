# A_links – request link graph (from REQ-A only; no deletions in this request)

## Nodes
| N-id | name | kind | stability (stable/medium/volatile) | def at (REQ-A:path:line) | H-ids / S-id | component |
|---|---|---|---|---|---|---|
| N001 | SUPPORT_TONER_SAVE | config-macro | stable | REQ-A:config/model_a.h:3 | H002, H007, H008 | C1 |
| N002 | Makefile SRCS += toner_save.c | build-file | stable | REQ-A:Makefile:6 | H001 | C1 |
| N003 | "ECONOMODE" | table-entry | stable | REQ-A:src/cmd/pjl_commands.c:27 | H004 | C1 |
| N004 | "TONER_SAVE" | table-entry | stable | REQ-A:src/panel/menu_table.c:12 | H007 | C1 |
| N005 | STR_TONER_SAVE | string-id | stable | REQ-A:src/resources/strings.h:6 | H009 | C1 |
| N006 | "Toner Save" | table-entry | stable | REQ-A:src/resources/strings_en.c:6 | H010 | C1 |
| N007 | toner_save_level | nv-field | stable | REQ-A:src/settings/nv_settings.h:8 | H013 | C1 |
| N008 | TONER_SAVE_H | preprocessor | stable | REQ-A:src/features/toner_save/toner_save.h:1 | H006 | C1 |
| N009 | toner_save.h | file scope | medium | REQ-A:src/features/toner_save/toner_save.h:1 | H006 | C1 |
| N010 | TONER_SAVE_OFF/LOW/HIGH | enum | medium | REQ-A:src/features/toner_save/toner_save.h:3 | H006 | C1 |
| N011 | g_pjl_table | table | medium | REQ-A:src/cmd/pjl_commands.c:24 | H004 | C1 |
| N012 | g_menu_table | table | medium | REQ-A:src/panel/menu_table.c:8 | H007 | C1 |
| N013 | StrId_t | enum | medium | REQ-A:src/resources/strings.h:3 | H009 | C1 |
| N014 | g_strings_en | table | medium | REQ-A:src/resources/strings_en.c:3 | H010 | C1 |
| N015 | NvSettings_t | struct | medium | REQ-A:src/settings/nv_settings.h:5 | H013 | C1 |
| N016 | k_percent | global | medium | REQ-A:src/features/toner_save/toner_save.c:8 | H005 | C1 |
| N017 | is_valid | function | volatile | REQ-A:src/features/toner_save/toner_save.c:10 | H005 | C1 |
| N018 | TonerSave_GetLevel | function | volatile | REQ-A:src/features/toner_save/toner_save.c:15 | H005, H006 | C1 |
| N019 | TonerSave_ApplyDensity | function | volatile | REQ-A:src/features/toner_save/toner_save.c:20 | H005, H006 | C1 |
| N020 | TonerSave_MenuHandler | function | volatile | REQ-A:src/features/toner_save/toner_save.c:28 | H005, H006 | C1 |
| N021 | TonerSave_PjlSet | function | volatile | REQ-A:src/features/toner_save/toner_save.c:37 | H005, H006 | C1 |
| N022 | Render_Page | function | volatile | REQ-A:src/print/render.c:8 | H008 | C1 |
| N023 | NV_LoadDefaults | function | volatile | REQ-A:src/settings/nv_settings.c:11 | H012 | C1 |
| N024 | toner_save.c | file scope | medium | REQ-A:src/features/toner_save/toner_save.c:1 | H005 | C1 |
| N025 | includes@pjl_commands.c | file scope | medium | REQ-A:src/cmd/pjl_commands.c:4 | H003 | C1 |
| N026 | includes@nv_settings.c | file scope | medium | REQ-A:src/settings/nv_settings.c:2 | H011 | C1 |
| N027 | SUPPORT_TONER_SAVE@menu_table.c | preprocessor | medium | REQ-A:src/panel/menu_table.c:4 | H007 | C1 |
| N028 | SUPPORT_TONER_SAVE@render.c | preprocessor | medium | REQ-A:src/print/render.c:3 | H008 | C1 |
| N029 | NV_GetSettings | external | medium | outside request | - | C1 |
| N030 | Density_Scale | external | medium | outside request | - | C1 |
| N031 | Log_Info | external | medium | outside request | - | C1 |
| N032 | Str_Get | external | medium | outside request | - | C1 |

## Edges
| from (N-id) | type | to (N-id) | evidence (REQ-A:path:line) |
|---|---|---|---|
| N002 | builds | N024 | REQ-A:Makefile:6 |
| N024 | includes | N009 | REQ-A:src/features/toner_save/toner_save.c:2 |
| N025 | includes | N009 | REQ-A:src/cmd/pjl_commands.c:4 |
| N026 | includes | N009 | REQ-A:src/settings/nv_settings.c:2 |
| N027 | includes | N009 | REQ-A:src/panel/menu_table.c:5 |
| N028 | includes | N009 | REQ-A:src/print/render.c:4 |
| N001 | guards | N027 | REQ-A:src/panel/menu_table.c:4 |
| N001 | guards | N004 | REQ-A:src/panel/menu_table.c:11 |
| N001 | guards | N028 | REQ-A:src/print/render.c:3 |
| N001 | guards | N022 | REQ-A:src/print/render.c:11 |
| N008 | guards | N009 | REQ-A:src/features/toner_save/toner_save.h:1 |
| N009 | declares | N018 | REQ-A:src/features/toner_save/toner_save.h:9 |
| N009 | declares | N019 | REQ-A:src/features/toner_save/toner_save.h:10 |
| N009 | declares | N020 | REQ-A:src/features/toner_save/toner_save.h:11 |
| N009 | declares | N021 | REQ-A:src/features/toner_save/toner_save.h:12 |
| N009 | declares | N010 | REQ-A:src/features/toner_save/toner_save.h:3 |
| N011 | registers | N003 | REQ-A:src/cmd/pjl_commands.c:27 |
| N003 | registers | N021 | REQ-A:src/cmd/pjl_commands.c:27 |
| N012 | registers | N004 | REQ-A:src/panel/menu_table.c:12 |
| N004 | registers | N020 | REQ-A:src/panel/menu_table.c:12 |
| N013 | indexes | N014 | REQ-A:src/resources/strings_en.c:3 |
| N005 | indexes | N014 | REQ-A:src/resources/strings_en.c:6 |
| N005 | localizes | N006 | REQ-A:src/resources/strings_en.c:6 |
| N015 | declares | N007 | REQ-A:src/settings/nv_settings.h:8 |
| N023 | defaults | N007 | REQ-A:src/settings/nv_settings.c:15 |
| N023 | reads | N010 | REQ-A:src/settings/nv_settings.c:15 |
| N017 | reads | N010 | REQ-A:src/features/toner_save/toner_save.c:12 |
| N018 | reads | N007 | REQ-A:src/features/toner_save/toner_save.c:17 |
| N018 | uses-external | N029 | REQ-A:src/features/toner_save/toner_save.c:17 |
| N019 | calls | N018 | REQ-A:src/features/toner_save/toner_save.c:22 |
| N019 | calls | N017 | REQ-A:src/features/toner_save/toner_save.c:23 |
| N019 | reads | N016 | REQ-A:src/features/toner_save/toner_save.c:25 |
| N019 | uses-external | N030 | REQ-A:src/features/toner_save/toner_save.c:25 |
| N020 | calls | N017 | REQ-A:src/features/toner_save/toner_save.c:30 |
| N020 | writes | N007 | REQ-A:src/features/toner_save/toner_save.c:32 |
| N020 | uses-external | N029 | REQ-A:src/features/toner_save/toner_save.c:32 |
| N020 | reads | N005 | REQ-A:src/features/toner_save/toner_save.c:33 |
| N020 | uses-external | N031 | REQ-A:src/features/toner_save/toner_save.c:33 |
| N020 | uses-external | N032 | REQ-A:src/features/toner_save/toner_save.c:33 |
| N021 | calls | N020 | REQ-A:src/features/toner_save/toner_save.c:39 |
| N022 | calls | N019 | REQ-A:src/print/render.c:12 |

Notes: `declares` is also used for header→enum and struct→field membership (closest A7 type). `atoi` (stdlib) not modelled.
Isolated: none
Components: C1 = {N001–N032} (single component: every changed place is linked to the toner_save module)
