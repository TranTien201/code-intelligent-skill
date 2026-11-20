# Report Phase <1|2|3|4> — <RT> — run `<run-id>`

<!-- Một mẫu cho mọi phase. Mục không có nội dung thì ghi "Không có", không xoá mục.
     Phần thêm riêng của từng phase: xem bước "Report" trong file phase đó.
     Phase 3/4: mọi trạng thái chunk lấy từ kết quả render_review.py, không tự viết. -->

## Tổng kết

- File: <n> | Đơn vị: <n> | Đã xử lý: <n> | Bỏ qua: <n> | Cần xác nhận: <n>
- Phase 3/4: APPLIED <n> | KEPT <n> | NEED_CONFIRM <n> | BLOCKED <n> | FOLLOW <n> | câu hỏi <n> | skipped <n>
- File kết quả: <đường dẫn diff / diff (new) / merge-plan.json / review.html / target_out>

## Đã xử lý

| File | Đơn vị / Chunk | Nhãn / Trạng thái | Vị trí (bản code: dòng) | Ghi chú |
|---|---|---|---|---|

## Bỏ qua

| File | Đơn vị / Đoạn | Lý do (nhãn hoặc mã) | Chi tiết |
|---|---|---|---|

## Cần xác nhận

### <Q-id hoặc số>. <file> — <đơn vị>

- Chunk liên quan (Phase 3): <K…>; chunk đang chờ nó: <K…>
- Vì sao chưa chắc: <khác biệt cụ thể, tiêu chí nào không đạt>
- Code liên quan: <trích ngắn, kèm file và số dòng>
- Phương án và hệ quả:
  - Áp: <chunk kéo theo, logic Target bị thay, phụ thuộc còn thiếu>
  - Giữ Target: <logic Target giữ lại, phần feature chưa port>
- Trả lời của người dùng: <điền sau>

## Cảnh báo

- <UNEXPLAINED / UNRESOLVED / chưa compile / tool-gaps.md …>

## Độ phủ

| Chặng | Tổng | Đã khớp | Có lý do | Đã sửa | CHƯA XÉT |
|---|---|---|---|---|---|
| P1: dòng `+`/`-` → đơn vị | | | | | 0 |
| P2: dòng RT → Feature / `ledger.md` | | | | | 0 |
| P3: hunk diff (new) → chunk / `skipped` / Bỏ qua | | | | | 0 |
| P3/4: hunk diff output ↔ chunk APPLIED | | | | | 0 |

<!-- Chỉ điền các chặng đã chạy tới phase hiện tại. -->

## Kết quả cổng kiểm tra

| # | Kiểm tra | Kết quả (có số) | Đạt? |
|---|---|---|---|

<!-- Copy đúng bảng cổng của phase. "Đã kiểm tra" không có số = không đạt.
     Có dòng không đạt thì không sang phase sau. -->
