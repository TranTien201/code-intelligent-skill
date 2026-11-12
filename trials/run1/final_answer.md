## Port Toner Save từ A sang B
**Build:** OK (`make -s MODEL=B`), `./printer_B` chạy được · **Rủi ro:** HIGH (vì layout NVRAM, xem bên dưới) · **Output:** `output/B_ported`

`input/B_latest` không bị sửa. Kết quả phân tích nằm ở `output/work/` (`report.md`, `llm_review.md`).

### Đã làm
| Loại | File / symbol | Lý do |
|---|---|---|
| Copy mới | `src/features/toner_save/toner_save.c/.h` | Code chính của feature |
| Copy mới | `src/print/density.c/.h` (`Density_Scale`, `DENSITY_MAX`) | Feature cần mấy hàm này (`TonerSave_ApplyDensity` gọi `Density_Scale`), B chưa có. Đã thêm `density.c` vào Makefile |
| Merge 3 chiều | `Makefile`, `pjl_commands.c`, `menu_table.c`, `render.c`, `strings.h`, `strings_en.c`, `nv_settings.c/.h` | Chỉ đưa phần thay đổi của feature sang, giữ nguyên code riêng của B (ví dụ `fax_resolution`). Không còn conflict marker nào |
| Thêm define | `config/model_b.h`: `#define SUPPORT_TONER_SAVE 1` | Phần render và menu của feature nằm trong `#ifdef` này |
| Thay thế | `Clamp` trong `src/util/math_util.c/.h` | B có `Clamp(v, hi)` với 2 tham số, A có `Clamp(v, lo, hi)` với 3 tham số. Đã grep, B không gọi `Clamp` ở đâu cả, nên thay bằng bản của A |

### Quyết định đã đưa ra
- **`TonerSave_ApplyDensity` lấy bản mới nhất của A**, không lấy bản trong commit feature, vì bản mới có bug-fix #1234 (chặn giá trị đọc từ NVRAM bị hỏng).
- **Không copy `EcoReport_Print`.** Đây là một feature khác của A có dùng Toner Save, không thuộc phạm vi port.

### Cần người xác nhận
1. **Layout NVRAM bị dịch.** `toner_save_level` được chèn vào giữa `NvSettings_t`, ngay sau `duplex`. Vì vậy `language`, `quality`, `fax_resolution` đều bị lệch offset. Code B không có cơ chế version hay migration NVRAM. Máy B cập nhật firmware sẽ đọc sai setting cũ, trừ khi có factory reset hoặc chuyển field mới xuống cuối struct. Chuyển xuống cuối thì không còn là "copy 1-1" nữa, nên cần khách hàng quyết.
2. **Enum `StrId_t` bị dịch.** `STR_TONER_SAVE` được chèn trước `STR_QUALITY`, nên giá trị của `STR_QUALITY` tăng thêm 1. Cần xác nhận ID chuỗi này không được lưu hay gửi ra ngoài. B hiện chỉ có `strings_en.c` (đã merge). Nếu có bảng ngôn ngữ khác nằm ngoài repo này thì phải bổ sung chuỗi.
3. **Xác nhận B có muốn bật feature không**, tức là giữ `SUPPORT_TONER_SAVE 1` trong `config/model_b.h`.
4. Theo checklist nghiệp vụ, nếu B có Web UI hoặc SNMP cho setting thì cần thêm mục Toner Save. Repo này không có các phần đó nên tôi không kiểm tra được.
5. Tôi mới chạy thử một lần. Output có in `[INFO] Toner Save`, `toner_save=2`, `pjl=1`, `density=8`. Tôi chưa có output mong đợi để so, nên nên đối chiếu với máy A.

### Chi phí
- Context đã đọc: khoảng 278 token snippet cần review và vài lần query, so với khoảng 1.836 token nếu đọc cả repo A.