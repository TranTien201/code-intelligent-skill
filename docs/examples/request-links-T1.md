# Ví dụ: Request Links (T1-rename-multi, dữ liệu mẫu viết tay)

## Sau Checkpoint A – màu theo độ ổn định

```mermaid
flowchart LR
    subgraph C1["C1"]
        N001["STR_TONER_SAVE<br/>string-id · stable"]:::stable
        N002["SUPPORT_TONER_SAVE<br/>config-macro · stable"]:::stable
        N003["Makefile<br/>build-file · stable"]:::stable
        N004["NvSettings_t.toner_save_level<br/>nv-field · medium"]:::medium
        N005["TonerSave_GetLevel<br/>function · volatile"]:::volatile
        N006["TonerSave_ApplyDensity<br/>function · volatile"]:::volatile
        N007["TonerSave_MenuHandler<br/>function · volatile"]:::volatile
        N008["TonerSave_PjlSet<br/>function · volatile"]:::volatile
        N009["g_menu_table<br/>table · medium"]:::medium
        N010["g_pjl_table<br/>table · medium"]:::medium
        N011["Render_Page<br/>function · volatile"]:::volatile
        N012["NV_LoadDefaults<br/>function · volatile"]:::volatile
        N013["toner_save.c<br/>file · medium"]:::medium
    end
    N009 -->|registers| N007
    N010 -->|registers| N008
    N011 -->|calls| N006
    N006 -->|calls| N005
    N008 -->|calls| N007
    N005 -->|reads| N004
    N007 -->|writes| N004
    N007 -->|reads| N001
    N012 -->|defaults| N004
    N002 -->|guards| N011
    N002 -->|guards| N009
    N003 -->|builds| N013
    classDef stable fill:#d8f0dc,stroke:#2e7d32,color:#000
    classDef medium fill:#fff4cc,stroke:#b8860b,color:#000
    classDef volatile fill:#ffe0cc,stroke:#c85a00,color:#000
    classDef external fill:#eeeeee,stroke:#888888,color:#000,stroke-dasharray:4 3
    classDef same fill:#d8f0dc,stroke:#2e7d32,color:#000
    classDef renamed fill:#d6e6ff,stroke:#1f5fbf,color:#000
    classDef splitmerge fill:#ead9ff,stroke:#6a3fb5,color:#000
    classDef lowconf fill:#ffe0cc,stroke:#c85a00,color:#000,stroke-width:3px
    classDef missing fill:#ffd6d6,stroke:#c62828,color:#000,stroke-width:3px
    classDef open fill:#ffffff,stroke:#888888,color:#000
```

Legend: green = stable · yellow = medium · orange = volatile (trace order in B) · grey dashed = outside the request

| from | type | to | evidence |
|---|---|---|---|
| N009 `g_menu_table` | registers | N007 `TonerSave_MenuHandler` | REQ-A:src/panel/menu_table.c:12 |
| N010 `g_pjl_table` | registers | N008 `TonerSave_PjlSet` | REQ-A:src/cmd/pjl_commands.c:27 |
| N011 `Render_Page` | calls | N006 `TonerSave_ApplyDensity` | REQ-A:src/print/render.c:12 |
| N006 `TonerSave_ApplyDensity` | calls | N005 `TonerSave_GetLevel` | REQ-A:src/features/toner_save/toner_save.c:22 |
| N008 `TonerSave_PjlSet` | calls | N007 `TonerSave_MenuHandler` | REQ-A:src/features/toner_save/toner_save.c:39 |
| N005 `TonerSave_GetLevel` | reads | N004 `NvSettings_t.toner_save_level` | REQ-A:src/features/toner_save/toner_save.c:17 |
| N007 `TonerSave_MenuHandler` | writes | N004 `NvSettings_t.toner_save_level` | REQ-A:src/features/toner_save/toner_save.c:32 |
| N007 `TonerSave_MenuHandler` | reads | N001 `STR_TONER_SAVE` | REQ-A:src/features/toner_save/toner_save.c:33 |
| N012 `NV_LoadDefaults` | defaults | N004 `NvSettings_t.toner_save_level` | REQ-A:src/settings/nv_settings.c:15 |
| N002 `SUPPORT_TONER_SAVE` | guards | N011 `Render_Page` | REQ-A:src/print/render.c:11 |
| N002 `SUPPORT_TONER_SAVE` | guards | N009 `g_menu_table` | REQ-A:src/panel/menu_table.c:11 |
| N003 `Makefile` | builds | N013 `toner_save.c` | REQ-A:Makefile:6 |

## Sau Checkpoint B – màu theo kết quả neo

```mermaid
flowchart LR
    subgraph C1["C1"]
        N001["STR_TONER_SAVE<br/>string-id · stable<br/>SAME_NAME NAME High"]:::same
        N002["SUPPORT_TONER_SAVE<br/>config-macro · stable<br/>SAME_NAME NAME High"]:::same
        N003["Makefile<br/>build-file · stable<br/>SAME_PATH NAME High"]:::same
        N004["NvSettings_t.toner_save_level<br/>nv-field · medium<br/>→ NvSettings_t.eco_level<br/>RENAMED_SYMBOL EDGE High"]:::renamed
        N005["TonerSave_GetLevel<br/>function · volatile<br/>→ EcoMode_GetLevel<br/>RENAMED_SYMBOL PATTERN Medium"]:::renamed
        N006["TonerSave_ApplyDensity<br/>function · volatile<br/>→ EcoMode_ApplyDensity<br/>SPLIT_SYMBOL EDGE High"]:::splitmerge
        N007["TonerSave_MenuHandler<br/>function · volatile<br/>→ EcoMode_MenuHandler<br/>RENAMED_SYMBOL EDGE High"]:::renamed
        N008["TonerSave_PjlSet<br/>function · volatile<br/>→ EcoMode_PjlSet<br/>RENAMED_SYMBOL EDGE High"]:::renamed
        N009["g_menu_table<br/>table · medium<br/>SAME_NAME NAME High"]:::same
        N010["g_pjl_table<br/>table · medium<br/>SAME_NAME NAME High"]:::same
        N011["Render_Page<br/>function · volatile<br/>SAME_NAME NAME High"]:::same
        N012["NV_LoadDefaults<br/>function · volatile<br/>SAME_NAME NAME High"]:::same
        N013["toner_save.c<br/>file · medium<br/>→ SRC:src/features/eco/eco_mode.c<br/>MOVED_FILE EDGE High"]:::renamed
    end
    N009 -->|registers| N007
    N010 -->|registers| N008
    N011 -->|calls| N006
    N006 -->|calls| N005
    N008 -->|calls| N007
    N005 -->|reads| N004
    N007 -->|writes| N004
    N007 -->|reads| N001
    N012 -->|defaults| N004
    N002 -->|guards| N011
    N002 -->|guards| N009
    N003 -->|builds| N013
    classDef stable fill:#d8f0dc,stroke:#2e7d32,color:#000
    classDef medium fill:#fff4cc,stroke:#b8860b,color:#000
    classDef volatile fill:#ffe0cc,stroke:#c85a00,color:#000
    classDef external fill:#eeeeee,stroke:#888888,color:#000,stroke-dasharray:4 3
    classDef same fill:#d8f0dc,stroke:#2e7d32,color:#000
    classDef renamed fill:#d6e6ff,stroke:#1f5fbf,color:#000
    classDef splitmerge fill:#ead9ff,stroke:#6a3fb5,color:#000
    classDef lowconf fill:#ffe0cc,stroke:#c85a00,color:#000,stroke-width:3px
    classDef missing fill:#ffd6d6,stroke:#c62828,color:#000,stroke-width:3px
    classDef open fill:#ffffff,stroke:#888888,color:#000
```

Legend: green = name kept · blue = renamed/moved · purple = split/merged · orange = Low confidence · red = not found/rewritten/removed · white = not anchored · grey dashed = outside the request
