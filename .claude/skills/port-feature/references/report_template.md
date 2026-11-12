# Mẫu báo cáo cuối

## Kết quả port `<tên feature>`: A → B
**Build:** OK / LỖI · **Rủi ro:** HIGH / MEDIUM / LOW · **Output:** `<thư mục B_ported>`

### Đã làm
| Loại | File / symbol | Lý do |
|---|---|---|
| Copy mới | ... | feature / phụ thuộc (chuỗi: X ← Y) |
| Merge | ... | hunk của feature, giữ phần riêng của B |
| Thêm define | ... | guard `#ifdef` |
| Thay thế | ... | xung đột SAFE_REPLACE |

### Quyết định đã đưa ra
- ... (vd dùng bản A_latest của `X` vì có bug-fix sau feature)

### Cần người xác nhận / làm tiếp
- ... (xung đột NEEDS_REVIEW, NVRAM, feature khác của A đang dùng feature này nhưng không copy...)

### Chi phí
- Context đã đọc: ~N token so với ~M token nếu đọc cả repo A
