# Phase 1 — Diff Before→After và danh sách đơn vị

Mục tiêu: có diff Before→After từng file và biết chính xác RT đã thêm / sửa / xoá đơn vị nào, đơn vị mới được chèn ở đâu. Đây là đầu vào của Phase 2.

## Bước 1 — Lập danh sách file

Đọc: `request/Before/`, `request/After/`.

- Kiểm tra `run-id` và `WORK/<run-id>/` theo `SKILL.md`. Tạo `WORK/<run-id>/phase1/`.
- Ghi SHA-256 mọi file trong hai cây request vào `phase1/REPORT.md` (dùng khi resume).
- So hai cây theo đường dẫn tương đối. Trạng thái: `modified` (có ở cả hai, khác nhau), `added` (chỉ After), `deleted` (chỉ Before), `blocked` (nhị phân / không đọc được). Bỏ qua file giống hệt.

## Bước 2 — Lấy diff

- File `modified`: `get_diff(After/<file>, Before/<file>)` → `WORK/<run-id>/phase1/diff/<file>.diff`.
- File `added`: cả file là code RT. File `deleted`: chỉ ghi trạng thái.

## Bước 3 — Đọc entry RT

Đọc: `phase1/diff/<file>.diff`; không có thì khối `Modification:` của file After.

- Tìm entry có mã RT (hậu tố như `RT1200:V806-0001` vẫn là cùng RT). Ghi ngày, người làm, danh sách `Add.` / `Mod.` (một mục có thể kéo dài nhiều dòng chỉ có tên).
- Khách chỉ dùng `Add.` và `Mod.`; xoá cũng ghi `Mod.`. Loại `Add`/`Mod`/`Del` lấy ở Bước 4.

## Bước 4 — Lập danh sách đơn vị và neo

Đọc: `phase1/diff/<file>.diff`, file After (dòng `+`), file Before (dòng `-`).

- Với mỗi dòng `+`/`-` ngoài khối `Modification:`: mở file thật tại đúng số dòng, xác định nó thuộc đơn vị nào theo phạm vi ở `SKILL.md` (hàm tính cả comment đầu hàm). **Không dùng tên hàm ở dòng `@@`.**
- Loại: `Add` (chỉ After), `Mod` (cả hai, khác), `Del` (chỉ Before).
- **Neo cho mọi đơn vị `Add`**: lấy từ dòng context của diff Phase 1, hoặc dòng không trống liền trước / liền sau đơn vị trong After.
  - Ghi dạng `trước "<dòng nguyên văn>"` hoặc `sau "<dòng nguyên văn>"`. Chọn dòng là duy nhất trong file.
  - Dòng liền kề không duy nhất (ví dụ `}`) thì ghi `sau đơn vị <tên>` (sau dòng cuối của đơn vị đó).
  - Ví dụ: helper `libLinkVarSet` là đơn vị cuối file, ngay trên dòng `/** EOF **/` → neo `trước "/** EOF **/"`.
- Đối chiếu với changelog:
  - Diff có thay đổi mà changelog không nhắc: cảnh báo `UNEXPLAINED`, vẫn đưa vào danh sách.
  - Changelog nhắc mà diff không đổi: cảnh báo, không tự mở rộng phạm vi.
  - Không xác định được dòng thuộc đơn vị nào: "Cần xác nhận", đưa ứng viên.
- Ghi `WORK/<run-id>/phase1/units.md`:

```markdown
| # | File | Đơn vị | Loại | Add/Mod/Del | Dòng Before | Dòng After | Neo (Add) | Trong changelog? |
|---|---|---|---|---|---|---|---|---|
| 1 | src/item.c | LibCopyItem | hàm | Mod | 400-655 | 410-710 | - | Có |
| 2 | src/item.c | libLinkVarSet | hàm | Add | - | 1100-1155 | trước "/** EOF **/" | Có |
```

## Bước 5 — Report, cổng, dừng

- Ghi `phase1/REPORT.md` theo `templates/report.md`: fingerprint, trạng thái từng file, **đường dẫn từng file diff**, entry RT, bảng đơn vị, cảnh báo, "Cần xác nhận".
- **Cổng Phase 1** (ghi số vào mục "Kết quả cổng kiểm tra"):

| # | Kiểm tra | Đạt khi |
|---|---|---|
| 1 | File khác nhau = modified + added + deleted + blocked | Bằng nhau |
| 2 | Dòng `+`/`-` ngoài `Modification:` đã gán đơn vị | `N/N`, chưa gán = 0 |
| 3 | Khoảng dòng đơn vị lấy từ file thật (không từ `@@`), hàm tính từ dòng đầu comment đầu hàm | `n/n` đơn vị |
| 4 | Đơn vị `Add` có neo | `n/n` |
| 5 | Mục `Add.`/`Mod.` trong changelog khớp đơn vị hoặc có cảnh báo | `n/n` |

- Báo người dùng đường dẫn report và các diff. Dừng chờ xác nhận.
