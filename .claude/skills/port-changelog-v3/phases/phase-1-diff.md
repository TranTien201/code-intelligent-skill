# Phase 1 — Lấy diff Before-After và Latest-After

## 1.1 Lập danh sách file

- So sánh hai cây `Before/` và `After/` theo đường dẫn tương đối.
- Ghi trạng thái từng file: `modified`, `added` (chỉ có ở After), `deleted` (chỉ có ở Before).
- Bỏ qua file giống hệt nhau.
- File nhị phân hoặc không đọc được vẫn đưa vào danh sách với trạng thái `blocked`.

## 1.2 Lấy diff Before-After

- Với mỗi file `modified`: gọi `get-diff(After/<file>, Before/<file>)`.
- Lưu vào `WORK/phase1/before-after/<file>.diff`.
- File `added` / `deleted`: không cần gọi tool, chỉ ghi trạng thái.

## 1.3 Lấy diff Latest-After

- Tìm file cùng đường dẫn tương đối trong `latest/`.
- Có file: gọi `get-diff(latest/<file>, After/<file>)`, lưu vào `WORK/phase1/latest-after/<file>.diff`.
- Hai file giống hệt: ghi "Latest không đổi", không tạo diff.
- Không có file trong `latest/`: ghi "không còn trong Latest".

## 1.4 Đọc changelog của RT

- Trong khối `Modification:` của từng file, tìm entry có mã RT (kể cả dạng có hậu tố như `RT2486:V806-0001`).
- Lấy ngày, người làm, danh sách `Add.` / `Mod.`.
- Đọc thêm khối `Modification:` ở Latest: ghi các entry **nằm trên** entry RT (mới hơn) có nhắc tới hàm của RT.

## 1.5 Thông báo và dừng

- Báo cho người dùng:
  - Số file và trạng thái từng file.
  - **Đường dẫn đầy đủ của từng file diff** ở `before-after/` và `latest-after/` để người dùng mở xem.
  - Thông tin RT đọc được từ changelog.
- Dừng, chờ người dùng xác nhận rồi mới sang Phase 2.
