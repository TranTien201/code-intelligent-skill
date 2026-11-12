# Bối cảnh bài toán Port Request (Trace + Copy + Merge)

> Tài liệu nền, dùng lại khi phát triển / test skill `.claude/skills/port-request/`.
> Không phải bài toán của HyperDev.

## 1. Khách hàng cung cấp gì

3 bộ source, đều là **thư mục thường, không có lịch sử git**:

| Input | Tên trong skill | Ý nghĩa |
|---|---|---|
| Source mới nhất của máy A | `SOURCE_ROOT` | Trạng thái hiện tại của máy đã có tính năng |
| Source mới nhất của máy B | `TARGET_ROOT` | Máy cần nhận tính năng |
| Source của chức năng ở máy A (trong quá khứ) | `SOURCE_REQUEST` | Gồm `Before/` (trước khi code) và `After/` (sau khi code thêm feature). Có thể là cả cây hoặc chỉ các file thay đổi |

## 2. Yêu cầu đầu ra

- Copy tính năng của máy A sang máy B.
- Port theo **code mới nhất của A**, không phải bản `After/` cũ: tính năng ở A_latest thường đã thay đổi sau thời điểm request.
- Output phải **giống kết quả người làm tay (không dùng AI)**. Đây là tiêu chí nghiệm thu.

## 3. Điểm khó cốt lõi: `After/` (quá khứ) ≠ A_latest

Code chức năng trong request là ảnh chụp tại thời điểm làm feature. Sau đó, ở A_latest:

- **Mở rộng:** cùng hàm đó nhưng được thêm logic, hoặc feature mọc thêm hàm/file mới.
- **Sửa lỗi:** bugfix trên chính các dòng của feature.
- **Thay thế / đổi tên:** đổi tên hàm, đổi tên file, chuyển thư mục, tách hoặc gộp hàm/file. Vì vậy **tìm theo tên không còn tin cậy**.
- **Lẫn code khác:** trong cùng hàm có thêm code của feature khác (không được port).
- **Bị xoá / viết lại:** feature không còn ở dạng cũ, phải dừng và hỏi.

Không có git, nên mọi đổi tên/di chuyển đều phải suy ra **từ nội dung**: độ giống thân hàm, caller anchor,
neighbor anchor, chữ ký, literal đặc trưng, alias/wrapper (recipe R11/R12).

Phía máy B cũng có thể khác: B đã có hàm tương đương dưới tên khác, đã port một phần, đã tự sửa file chung, hoặc khác chữ ký hàm.

## 4. Hai câu hỏi chính

1. Từ code feature (request) → truy vào **A_latest** thế nào khi tên/vị trí đã đổi? → Checkpoint B (anchor, evolution, extension, closure).
2. Từ A_latest → xác định **file nào, dòng nào** bị ảnh hưởng (phụ thuộc code + dữ liệu: string đa ngôn ngữ, enum + mảng theo enum, NVRAM + default + version, bảng đăng ký, Makefile, guard `#ifdef`) để đánh giá và copy sang B → Checkpoint B5/C (closure tới fixpoint), D (plan), E (merge).

## 5. Quyết định đã chốt với bên yêu cầu

| Câu hỏi | Trả lời | Ngày |
|---|---|---|
| Người làm tay có port phần **mở rộng sau request** (`ext`: EXTENSION/BUGFIX ở A_latest) không? | **Có port.** Golden output phải bao gồm phần mở rộng. | 2026-11-12 |
| Ca mơ hồ (rename bằng chứng yếu, CONFLICT): golden là "dừng/hỏi" hay code người chọn? | _Chưa chốt_ | |
| Người làm tay có thêm nhãn request (`/* REQ-xxxx */`) không? | _Chưa chốt_ | |
| Mức "giống": byte-by-byte hay bỏ qua khoảng trắng / thứ tự include? | **Khớp 1-1.** Số file và số dòng phải đúng như bản làm tay; từng dòng phải khớp (xem §7). | 2026-11-12 |

## 6. Kế hoạch test (tóm tắt)

Khoảng 30 case, mỗi case có `input/` (A_latest, B_latest, REQ/Before, REQ/After), `golden/After/` (kết quả port tay),
`golden/expected.yaml` (đáp án theo từng checkpoint) và `TRAP.md`.

- **T1 – 22 case đơn bẫy:** 9 case truy vết đổi tên/di chuyển (B2), 4 case evolution (B3/B4), 4 case phụ thuộc code + dữ liệu (B5/C4), 5 case phía máy B (C).
- **T2 – 5 case kết hợp:** đổi tên ở cả A_latest và B; tách file + code không liên quan lẫn vào + NVRAM; định dạng (CRLF, Shift-JIS, chữ ký nhiều dòng...); C++; case đối chứng (không được thay đổi gì).
- **T3 – 2–3 ca thật** khách đã port tay, dùng làm thước đo chính.
- **Chấm điểm:** khớp 1-1 theo §7, và so `_work/*` với `expected.yaml` để tìm checkpoint lỗi đầu tiên.
- **Log:** `claude -p --output-format stream-json` → `transcript.jsonl`, giữ `OUTPUT_ROOT`, sinh `score.json` cho từng case và `summary.md` cho cả lần chạy.

Bộ `data/` hiện có (Toner Save, 11 bẫy) **không có ca đổi tên nào** và làm cho skill cũ `port-feature`. Có thể chuyển sang định dạng input của `port-request` để dùng làm case hồi quy.

## 7. Tiêu chí khớp 1-1 với bản làm tay (đã chốt 2026-11-12)

Một case chỉ **PASS** khi `OUTPUT/After` khớp `golden/After` (bản làm tay) ở **cả 4 mức**:

| Mức | Kiểm tra | Lệnh gợi ý |
|---|---|---|
| 1. Tập file | Đúng các file được thêm/sửa/xoá, không thiếu, không thừa | `diff -rq golden/After OUTPUT/After` |
| 2. Số dòng | Mỗi file: số dòng thêm / số dòng xoá so với B_latest bằng bản làm tay | `git diff --no-index --numstat B_latest X/After` cho cả golden và output, rồi so 2 kết quả |
| 3. Từng dòng | Nội dung và vị trí từng dòng giống hệt (kể cả thụt lề, dòng trống, vị trí chèn) | `diff -r golden/After OUTPUT/After` phải rỗng |
| 4. Byte | Encoding và kiểu xuống dòng (LF/CRLF) giữ đúng như file gốc của B | `cmp`, `file -I` |

Nếu fail, score ghi rõ: file thiếu/thừa, dòng thiếu/thừa/sai (kèm `path:line`) và checkpoint lỗi đầu tiên.

Hệ quả cho skill và golden:
- Gate E đang so verbatim bằng `diff -w` (bỏ qua khoảng trắng) → cần siết lại thành so khớp tuyệt đối.
- **Vị trí chèn** (hàm mới đặt ở đâu trong file, entry thêm vào chỗ nào trong bảng/enum/Makefile, include đặt dòng nào) sẽ quyết định PASS/FAIL. Cần ghi lại quy tắc người làm tay đang dùng (ví dụ: cùng vị trí tương đối như ở A_latest, cạnh symbol lân cận) để skill làm theo đúng quy tắc đó. Mỗi case trong `TRAP.md` ghi lý do của vị trí chèn trong golden.
