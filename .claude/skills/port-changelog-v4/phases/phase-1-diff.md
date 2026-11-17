# Phase 1 — Lấy diff và khoanh vùng hàm/biến của RT

Mục tiêu:
- Có file diff Before→After cho từng file.
- Biết chính xác RT đã thêm/sửa/xoá những hàm, macro, biến nào. Đây là danh sách đầu vào của Phase 2.

## Bước 1 — Lập danh sách file

- So sánh hai cây `request/Before/` và `request/After/` theo đường dẫn tương đối.
- Ghi trạng thái từng file:
  - `modified`: có ở cả hai, nội dung khác.
  - `added`: chỉ có ở After.
  - `deleted`: chỉ có ở Before.
- Bỏ qua file giống hệt nhau.
- File nhị phân hoặc không đọc được: vẫn ghi vào danh sách với trạng thái `blocked`.

## Bước 2 — Lấy diff Before→After

- Với mỗi file `modified`: gọi `get-diff(After/<file>, Before/<file>)`.
- Lưu kết quả vào `WORK/phase1/diff/<đường dẫn file>.diff`.
- File `added`: không cần gọi tool. Toàn bộ file là code mới của RT.
- File `deleted`: không cần gọi tool. Ghi trạng thái.

## Bước 3 — Đọc entry của RT trong changelog

- Ở đầu diff thường có các dòng `+` nằm trong khối `Modification:`. Đó là entry của RT.
- Nếu diff không có, đọc khối `Modification:` trong file After và tìm entry có mã RT.
  - Mã RT có thể có hậu tố, ví dụ `RT2486:V806-0001`. Vẫn tính là cùng RT.
- Từ entry, ghi lại:
  - Ngày, người làm, mã RT.
  - Danh sách `Add.` và `Mod.`. Lưu ý một mục có thể kéo dài nhiều dòng (các dòng sau chỉ có tên, không có chữ `Add.`/`Mod.`).
- Khách chỉ dùng hai từ khoá `Add.` và `Mod.`. Xoá một hàm/symbol cũng ghi là `Mod.`.
  - Vì vậy loại `Add` / `Mod` / `Del` của từng đơn vị phải xác định bằng diff (Bước 4), không lấy theo từ khoá trong changelog.
- Tên trong changelog có thể là hàm (`xxx()`), mảng (`xxx[][]`), hoặc macro/biến (`WAVMACH_ONLY_VER`). Chưa biết là loại gì thì để Bước 4 xác định.

## Bước 4 — Lập danh sách đơn vị của RT

- Với mỗi block `+`/`-` trong diff (bỏ qua phần khối `Modification:`):
  - Mở file After (cho dòng `+`) hoặc Before (cho dòng `-`) tại đúng số dòng.
  - Xác định dòng đó nằm trong đơn vị nào: hàm, macro, biến global/static, kiểu, prototype.
  - **Không dùng tên hàm ở dòng `@@` làm căn cứ.** Phải mở file và xem dòng đó thực sự nằm trong hàm nào (từ dòng chữ ký tới dấu `}` đóng hàm).
- Phân loại từng đơn vị:
  - `Add`: không có ở Before, có ở After.
  - `Mod`: có ở cả hai, nội dung khác.
  - `Del`: có ở Before, không có ở After. Trong changelog đơn vị này được ghi là `Mod.`, đối chiếu vẫn tính là khớp.
- Ghi khoảng dòng của đơn vị ở Before và After.
- Đối chiếu với changelog ở Bước 3:
  - Diff có thay đổi nhưng changelog không nhắc tới: ghi cảnh báo `UNEXPLAINED`, vẫn đưa vào danh sách.
  - Changelog có nhắc nhưng diff không có thay đổi: ghi cảnh báo, không tự mở rộng phạm vi.
  - Không xác định được dòng thay đổi thuộc đơn vị nào: ghi vào "Cần xác nhận", đưa các ứng viên.
- Lưu danh sách vào `WORK/phase1/units.md`:

```markdown
| # | File | Đơn vị | Loại | Add/Mod/Del | Dòng Before | Dòng After | Có trong changelog? |
|---|---|---|---|---|---|---|---|
| 1 | src/artlib.c | ArtLibGetRecipeData | hàm | Mod | 3790-3900 | 3812-3930 | Có |
| 2 | src/artlib.c | artLibSetVarDate | hàm | Add | - | 4100-4160 | Có |
```

## Bước 5 — Report, thông báo và dừng

- Ghi `WORK/phase1/REPORT.md` gồm:
  - Danh sách file và trạng thái (`modified` / `added` / `deleted` / `blocked`).
  - **Đường dẫn đầy đủ của từng file diff** để người dùng mở xem.
  - Entry RT đọc được từ changelog.
  - Bảng đơn vị của RT (copy từ `units.md`).
  - Cảnh báo (`UNEXPLAINED`...) và mục "Cần xác nhận" nếu có.
- Báo cho người dùng đường dẫn report và các file diff.
- Dừng, chờ người dùng xác nhận rồi mới sang Phase 2.
