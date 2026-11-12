# Checklist "chỗ đăng ký ngầm" của firmware máy in

Đây là các liên kết mà graph tĩnh dễ sót. Danh sách này là MẪU, cần dev firmware của dự án
bổ sung và chỉnh theo codebase thật. Mỗi dòng: *khi feature làm X → phải kiểm tra Y ở B*.

| Feature thêm... | Kiểm tra ở B |
|---|---|
| Setting mới | Field trong struct NVRAM, giá trị mặc định (LoadDefaults/factory reset), version/migration của NVRAM, menu panel, Web UI, SNMP MIB, biến PJL |
| Lệnh PJL/PCL/ESC | Bảng dispatch lệnh, parser, tài liệu lệnh |
| Chuỗi hiển thị | Enum ID chuỗi + bảng chuỗi của **tất cả** ngôn ngữ (không chỉ `strings_en`) |
| Mục menu | Bảng menu, quyền truy cập (admin/user), icon/resource |
| Trạng thái/lỗi mới | Bảng mã lỗi, LED/panel message, log/SNMP trap |
| Task/thread | Bảng task, priority, stack size, init order |
| Hàm bật theo model | Macro `SUPPORT_*` trong file cấu hình model của B, Makefile/Kconfig |
| Tài nguyên phần cứng | Bảng GPIO/sensor của model B (có thể khác A, **không copy 1-1**, phải hỏi người) |

Luật chung:
- Enum chèn vào **giữa** danh sách → các giá trị phía sau bị dịch. Kiểm tra giá trị đó có được lưu
  (NVRAM, file, giao thức) không.
- Struct lưu NVRAM thêm field → kiểm tra cơ chế version/migration, kẻo đọc sai dữ liệu cũ sau khi update firmware.
