# Phase 4 — Người duyệt quyết định trên trang

Mục tiêu: người duyệt trả lời câu hỏi và chỉnh từng chunk trên `review.html`; agent ghép output cuối từ các quyết định đó. Agent không tự trả lời thay người duyệt.

## Bước 1 — Người duyệt dùng trang

Đọc: `phase3/review.html`, `phase3/REPORT.md`.

- Đưa người dùng đường dẫn `WORK/<run-id>/phase3/review.html`. Trên trang (xem `schema/README.md` §4b):
  - Trả lời câu hỏi (chọn phương án).
  - **→** áp một chunk: kéo theo mọi chunk trong `requires` của nó. Nếu trong đó có chunk thuộc câu hỏi chưa trả lời, trang chỉ tới câu hỏi đó.
  - **←** giữ Target: các chunk phụ thuộc tự lùi theo.
  - **RT**: chỉ hiện khi chunk có `rt`.
- Người duyệt xuất file quyết định, lưu vào `WORK/<run-id>/phase4/decisions.json`.
- Trang có banner đỏ (lỗi dữ liệu): quay lại Phase 3 sửa plan, không dùng file quyết định.

## Bước 2 — Kiểm file quyết định

Đọc: `phase4/decisions.json`, `phase3/merge-plan.json`.

- `rt` trùng plan. Mọi khoá `answers` là câu hỏi có thật, giá trị là phương án có thật. Mọi khoá `choices` là chunk có thật, giá trị ∈ `target`, `rt`, `apply`.
- Người duyệt ghi thêm yêu cầu bằng lời (ví dụ "sửa khác RT", câu hỏi mới) → quay lại Phase 3, Bước 7; sửa plan, tạo lại `review.html`, lặp lại Phase 4.

## Bước 3 — Ghép output

- Chạy lệnh ghép (`SKILL.md`) với `--decisions WORK/<run-id>/phase4/decisions.json`. Chỉ thêm `--allow-pending` khi người duyệt cố ý để lại câu hỏi chưa trả lời.
- Cập nhật chunk changelog theo trạng thái mới (Phase 3, Bước 9), ghép lại nếu chunk đó đổi.

## Bước 4 — Kiểm tra lại

- Chạy lại kiểm tra 10b của Phase 3, ghi diff vào `phase4/diff/<file>.diff`.
- Plan có sửa trong Phase 4 → chạy lại cả 10a và 10c.

## Bước 5 — Report, cổng

- Ghi `phase4/REPORT.md` theo `templates/report.md`: bảng trạng thái chunk **lấy từ kết quả tool**, câu trả lời từng câu hỏi, các chunk người duyệt chọn tay, đường dẫn `target_out/` và `phase4/diff/`.

**Cổng Phase 4:**

| # | Kiểm tra | Đạt khi |
|---|---|---|
| 1 | Khoá trong `decisions.json` hợp lệ | `n/n` |
| 2 | 10b: hunk không có chunk / chunk APPLIED không có trong diff | `0` / `0` |
| 3 | Chunk changelog chỉ liệt kê đơn vị có chunk APPLIED | `n/n` file |
| 4 | Chunk còn NEED_CONFIRM | `0`, hoặc liệt kê ở "Cần xác nhận" kèm lý do người duyệt để lại |
| 5 | Encoding/xuống dòng `target_out` giống Target | `n/n` file |

- Còn câu hỏi chưa trả lời: không báo "hoàn tất". Báo số chunk theo trạng thái và đường dẫn output.
