# Phase 2 — Gộp thành diff mới nhất

Mục tiêu: từ diff Before→After và diff After→Latest, tạo một diff mới nhất cho từng file:
phần chức năng của RT ở trạng thái Latest, kèm đủ phụ thuộc.

Làm lần lượt **từng file** trong danh sách Phase 1. Không dừng sau một file.

## 1. Lập danh sách đơn vị thay đổi (từ diff Before→After)

- Đọc từng hunk, ánh xạ dòng thay đổi vào hàm/symbol bằng cách đọc source After.
  - Không dựa vào tên hàm ở header `@@` (có tool chỉ ghi số dòng).
- Mỗi đơn vị là một trong: hàm thêm, hàm sửa, hàm xóa, prototype, macro, biến global, type/struct, field.
- Đối chiếu với `Add.` / `Mod.` trong changelog:
  - Diff có nhưng changelog không nhắc → ghi `UNEXPLAINED`, vẫn xử lý.
  - Changelog nhắc nhưng diff không có → ghi cảnh báo, không mở rộng phạm vi.

## 2. So với diff After→Latest

- Với mỗi đơn vị, xem diff After→Latest có đụng tới nó không.
  - Không đụng → giữ nguyên thay đổi của Before→After.
  - Có đụng → lấy **toàn bộ** hàm/symbol theo bản Latest (mọi sửa đổi về sau trong chính hàm đó đều giữ).
  - Hàm không còn trong Latest → ghi `DELETE` (chưa xử lý đổi tên).
  - Macro/global/type không còn được định nghĩa/dùng trong Latest → bỏ khỏi trạng thái mong muốn.
  - Latest vẫn dùng symbol nhưng không tìm thấy định nghĩa → ghi `UNRESOLVED`.
- Ghi chú các entry changelog mới hơn có nhắc tới hàm đó (chỉ để giải thích, không dùng để loại code).

## 3. Closure (đủ phụ thuộc)

- Quét thân các hàm Latest đã chọn: tìm hàm, macro, global, type, prototype được dùng.
- Symbol định nghĩa trong Latest nhưng Target chưa có → tự thêm vào diff, rồi quét tiếp phụ thuộc của nó.
- Không hỏi chỉ vì có dependency mới. Chỉ hỏi khi không tìm được định nghĩa ở đâu cả.

## 4. Ghi diff mới nhất

- Ghi `WORK/phase2/<file>.diff`: dòng `-` = code After (hoặc Before nếu thêm mới), dòng `+` = code Latest.
  - Có thể dùng `get-diff` trên bản dựng tạm của hàm để sinh diff, không viết script riêng.
- Mỗi hunk có một dòng ghi chú ở đầu: tên hàm/symbol, nguồn (`RT`, `LATEST`, `CLOSURE`, `DELETE`), cảnh báo nếu có.
- Không sửa các file diff của Phase 1 (giữ làm bản gốc).

## 5. Report và báo người dùng

Ghi `WORK/phase2/REPORT.md` gồm 3 phần:

- **Bảng tất cả file** (không bỏ file nào):

  | File | Trạng thái | Số đơn vị | Đã gộp | Cần xác nhận | Đường dẫn diff mới |
  |---|---|---|---|---|---|

- **Đã gộp:** mỗi dòng một hàm/symbol, ghi nguồn (`RT` / `LATEST` / `CLOSURE` / `DELETE`) và entry RT mới hơn liên quan.
- **Cần người xác nhận:** mỗi mục ghi file, hàm/symbol, lý do không chắc, đoạn code liên quan, đề xuất.
- **Cảnh báo:** `UNEXPLAINED`, `UNRESOLVED`, changelog thiếu/thừa.

Sau đó:

- Báo người dùng đường dẫn report + số đã gộp / cần xác nhận.
- Hỏi các mục cần xác nhận (AskUserQuestion), cập nhật lại diff và report theo câu trả lời.
- Chỉ sang Phase 3 khi không còn mục chờ, hoặc người dùng đồng ý để lại.
