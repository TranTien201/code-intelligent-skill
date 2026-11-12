# Báo cáo port feature  (builder: treesitter)

**Mức rủi ro: HIGH**

- HIGH: kiểu dữ liệu dùng chung 'NvSettings_t' bị sửa (B đang dùng ở 3 chỗ; kiểm tra NVRAM/layout)
- HIGH: kiểu dữ liệu dùng chung 'StrId_t' bị sửa (B đang dùng ở 1 chỗ; kiểm tra NVRAM/layout)
- HIGH: 'Clamp' có ở B nhưng KHÁC A -> xung đột, cần người/LLM quyết
- MEDIUM: B chưa define 'SUPPORT_TONER_SAVE' -> copy xong code KHÔNG được build
- MEDIUM: 1 symbol đã thay đổi sau commit feature (drift)

## File
- Copy mới: ['src/features/toner_save/toner_save.c', 'src/features/toner_save/toner_save.h', 'src/print/density.c', 'src/print/density.h']
- Merge (3-way): ['Makefile', 'src/cmd/pjl_commands.c', 'src/panel/menu_table.c', 'src/print/render.c', 'src/resources/strings.h', 'src/resources/strings_en.c', 'src/settings/nv_settings.c', 'src/settings/nv_settings.h']
- Chèn symbol vào file có sẵn ở B: []
- File cấu hình A (map sang B): ['config/model_a.h']

## Symbol cần thêm vào B
- `STR_TONER_SAVE` (feature)
- `TONER_SAVE_HIGH` (feature)
- `TONER_SAVE_LOW` (feature)
- `TONER_SAVE_OFF` (feature)
- `TonerSave_ApplyDensity` (feature)
- `TonerSave_GetLevel` (feature)
- `TonerSave_MenuHandler` (feature)
- `TonerSave_PjlSet` (feature)
- `is_valid@src/features/toner_save/toner_save.c` (feature)
- `k_percent@src/features/toner_save/toner_save.c` (feature)
- `Density_Scale` (dependency, Density_Scale <- TonerSave_ApplyDensity)
- `DENSITY_MAX` (dependency, DENSITY_MAX <- Density_Scale <- TonerSave_ApplyDensity)

## Symbol có sẵn ở B cần merge hunk của feature
- `NV_LoadDefaults`
- `NvSettings_t`
- `Render_Page`
- `StrId_t`
- `g_menu_table@src/panel/menu_table.c`
- `g_pjl_table@src/cmd/pjl_commands.c`
- `g_strings_en@src/resources/strings_en.c`

## Xung đột
- `Clamp`: Clamp <- TonerSave_ApplyDensity

## Guard (#ifdef) B chưa define
- `SUPPORT_TONER_SAVE` dùng bởi ['Render_Page', 'g_menu_table@src/panel/menu_table.c']

## Drift (lấy bản A_latest)
- `TonerSave_ApplyDensity`

## Symbol dùng chung đã đổi sau feature (do commit khác, chỉ merge hunk feature)
- `g_menu_table@src/panel/menu_table.c`

## Chỉ báo cáo - feature khác của A đang dùng feature này (KHÔNG copy)
- `EcoReport_Print` -> `TONER_SAVE_OFF`
- `EcoReport_Print` -> `TonerSave_GetLevel`

## Điểm nối nghi vấn cần review

## Dừng vì B đã có y hệt (không cần đọc)
- `Log_Info`
- `NV_GetSettings`
- `Str_Get`

## Chi phí context
- Toàn bộ source A_latest: 7,347 ký tự (~1,836 token)
- Snippet cần người/LLM đọc (llm_review.md): 1,115 ký tự (~278 token)
- Số symbol đã duyệt trên graph: 19
