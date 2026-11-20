# Phase 3 — Merge diff mới nhất vào FOMULAR

Mục tiêu: áp các diff `WORK/phase2/*.diff` vào bản copy của Target.

## 1. Chuẩn bị

- Copy `target/` sang `WORK/target_out/` (nếu đã có thì dùng tiếp, không copy đè).
- Ghi lại encoding và kiểu xuống dòng của từng file Target để giữ nguyên khi ghi.
- Làm lần lượt **mọi file** trong `WORK/phase2/`. Không dừng sau một file.

## 2. Tìm vị trí trong Target

Với mỗi hunk, tìm chỗ tương ứng trong file Target, từ rẻ đến đắt:

- **Bậc 1 — Tên hàm/symbol:** tìm định nghĩa đúng tên trong file tương ứng.
- **Bậc 2 — Khớp sau chuẩn hóa:** bỏ khoảng trắng, comment rồi so dòng.
- **Bậc 3 — Mỏ neo hiếm:** grep token đặc trưng (tên hàm được gọi, macro, chuỗi, field).
- **Bậc 4 — Điểm giống nhau:** so đoạn code với các vùng ứng viên, tính % bằng cách đếm dòng/token giống.
- **Bậc 5 — Tự đánh giá:** đọc đoạn gốc + 2–3 ứng viên tốt nhất, trả lời "có cùng logic không, vì sao".

Ngưỡng:

| Kết quả tìm | Xử lý |
|---|---|
| Giống ≥ 90% và chỉ 1 ứng viên | Tự merge |
| 60–90%, hoặc nhiều ứng viên | Bậc 5: chắc chắn + có lý do → merge, ghi chú; không chắc → **hỏi** |
| < 60% và không còn mỏ neo | **Hỏi** |

## 3. Luật merge từng block

- **Block chỉ có dòng `+`** (thêm mới) → merge qua.
  - Nếu Target đã có đúng code đó → ghi `SKIP (đã có)`.
- **Block có dòng `-` rồi dòng `+`** (sửa code) → kiểm tra Target có hàm/đoạn code `-` đó không:
  - Có → thay bằng code `+`, giữ code riêng của FOMULAR xung quanh nếu không xung đột.
  - Không có → **không merge**, ghi `SKIP (Target không có code cũ)`.
- **Block `DELETE`** (hàm bị xóa ở Latest):
  - Target còn hàm đó và không có code/caller riêng → xóa, ghi `DELETE`.
  - Target đã không có → ghi `SKIP`.
  - Target có code riêng hoặc caller ngoài phạm vi → **hỏi**.
- **Symbol closure:** thêm định nghĩa còn thiếu vào đúng file.
  - Target có symbol nhưng khác chữ ký/kiểu → conflict, **hỏi**.
- **File added/deleted:** tạo/xóa file trong `target_out/` theo trạng thái Phase 1, kiểm tra chỗ tham chiếu liên quan.
- Thêm entry changelog của RT vào khối `Modification:` của file Target, theo đúng định dạng của file đó.

## 4. Kiểm tra cuối

- Mọi file trong danh sách đã có trạng thái cuối; không còn đoạn chờ.
- Mọi symbol dùng trong code đã merge đều có định nghĩa tương thích trong `target_out/`.
- Không còn caller gọi tới hàm đã xóa; prototype và định nghĩa khớp nhau.
- Encoding / xuống dòng của file trong `target_out/` giống Target gốc.
- Nếu người dùng cung cấp lệnh build → chạy thử và ghi kết quả.
- Xem tổng thay đổi: `get-diff(target_out/<file>, target/<file>)` cho từng file đã sửa.

## 5. Report và báo người dùng

Ghi `WORK/phase3/REPORT.md` gồm:

- **Bảng tất cả file:**

  | File | Đã merge | SKIP | DELETE | Cần xác nhận | Kết quả kiểm tra |
  |---|---|---|---|---|---|

- **Đã merge:** mỗi dòng một hàm/symbol, cách tìm được vị trí (bậc mấy, % giống), ghi chú.
- **Bỏ qua (SKIP):** hàm/đoạn và lý do (đã có / Target không có code cũ).
- **Cần người xác nhận:** file, hàm/symbol, đoạn Latest và các ứng viên trong Target, lý do không chắc, đề xuất.
- **Kết quả kiểm tra cuối** (mục 4).

Sau đó:

- Báo người dùng đường dẫn report, `target_out/`, và số đã merge / bỏ qua / cần xác nhận.
- Hỏi các mục cần xác nhận, áp theo câu trả lời, cập nhật report.
- Không báo "hoàn tất" khi còn mục chờ.
