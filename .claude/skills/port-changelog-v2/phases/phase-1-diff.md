# Phase 1 — Lấy diff Before→After và After→Latest

Mục tiêu: có đủ diff để biết RT đã sửa gì (Before→After) và các RT về sau đã sửa tiếp gì (After→Latest).

## 1. Liệt kê file thay đổi

- So sánh đệ quy `Before/` và `After/` theo đường dẫn tương đối.
- Bỏ qua file giống hệt nhau.
- Ghi trạng thái từng file: `added` (chỉ có ở After), `deleted` (chỉ có ở Before), `modified`.
- File nhị phân / không đọc được vẫn phải liệt kê, ghi trạng thái `blocked` + lý do.

## 2. Lấy diff Before→After

- Với mỗi file trong danh sách: `get-diff(After/<file>, Before/<file>)`.
  - File `added`: so với file rỗng. File `deleted`: so file rỗng với Before.
- Lưu vào `WORK/phase1/before-after/<file>.diff` (giữ cấu trúc thư mục).

## 3. Lấy diff After→Latest

- Với mỗi file trong danh sách, tìm file cùng đường dẫn tương đối trong `latest/`.
- Có file → `get-diff(latest/<file>, After/<file>)`, lưu vào `WORK/phase1/after-latest/<file>.diff`.
- Không có file trong Latest → ghi `missing in Latest` (không tự đi tìm file đổi tên).
- Diff rỗng → ghi `không đổi sau RT`.

## 4. Đọc changelog `Modification:`

- Trong diff Before→After, tìm entry của RT trong khối `Modification:` (dòng `+` hoặc `-`).
  - Lấy: mã RT, ngày, người làm, danh sách `Add.` / `Mod.`.
- Trong `latest/`, grep mã RT **chỉ trong khối `Modification:`** của mọi file.
  - Tính cả entry con có hậu tố, ví dụ `RT2486:V806-0001` (bản sửa tiếp của chính chức năng).
  - Xác nhận thêm bằng ngày + người làm để tránh trùng mã.
- Liệt kê các entry **nằm phía trên** entry RT (mới hơn) trong Latest.
  - Lưu ý: changelog mới ở trên, cũ ở dưới. Entry nằm dưới RT là cũ hơn, không tính.
- Bỏ khối `Modification:` ra khỏi phần so sánh code (tránh nhiễu), chỉ dùng để đọc.

## 5. Báo người dùng

- In danh sách **đầy đủ** đường dẫn file diff (dạng đường dẫn tuyệt đối để mở được):

  | File | Trạng thái | Diff Before→After | Diff After→Latest |
  |---|---|---|---|

- Kèm tóm tắt: số file, entry RT tìm thấy, số entry mới hơn, file `blocked` / `missing in Latest`.
- Chờ người dùng xem xong (hoặc đồng ý đi tiếp) rồi sang Phase 2.
